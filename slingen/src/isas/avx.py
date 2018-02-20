'''
Created on Apr 18, 2012

@author: danieles
'''

import sys
from sympy import sympify

from islpy import Set, Map

from src.dsls.ll import Matrix, ZeroMatrix, Symmetric, LowerTriangular, UpperTriangular, LowerUnitTriangular, UpperUnitTriangular, IdentityMatrix, AllEntriesConstantMatrix

from src.binding import getReference, ScalarsReference
from src.irbase import RValue, Pointer, VecAccess, VecDest, MovStatement, Mov, Comment, AddressOf, sa, V, DebugPrint, icode
from src.isas.isabase import ISA, Loader, Storer, LoadReplacer
from src.isas.sse2 import mmLoadSd, mmStoreSd, mmDivPd, mmSqrtPd
# from src.isas.sse4_1 import SSE4_1, SSSE3, SSE3, SSE2, SSE, x86
# from src.isas.isabase import *
# from src.isas.x86 import *
# from src.isas.sse import *
# from src.isas.sse2 import *
# from src.isas.sse3 import *
# from src.isas.ssse3 import *
# from src.isas.sse4_1 import *

class mm256LoadGs(RValue, VecAccess):
    ''' Wrapper of a vector load instruction.
        
        Useful when we want to represent a composite load instruction as a single logical instruction and then have it
        easily replaced by a scalar during scalar replacement.
        '''
    def __init__(self, pointer, mrmap, isCompact=True, isCorner=False, horizontal=True, zeromask=[]):
        super(mm256LoadGs, self).__init__()
        self.pointer = pointer
        self.mrmap = mrmap
        self.isCompact = isCompact
        self.isCorner = isCorner
        self.horizontal = horizontal
        self.orientation = 'horizontal' if horizontal else 'vertical'
        self.zeromask = zeromask
        self.reglen = 8
        self.analysis = None
        self._content = None
    
    @property
    def content(self):
        if self._content == None:
            self._content = self.generateContent()
        return self._content
    
    def generateContent(self):
        mrmap = self.mrmap
        pointer = self.pointer
        zeromask = self.zeromask
        horizontal = self.horizontal
        isCompact = self.isCompact
        content = None
        if len(mrmap) == 1:
            if mrmap == [tuple(range(self.reglen))]:
                content = mm256BroadcastSs(pointer, zeromask)
#             if mrmap[0] == 0:
            else:
                vmask = self.reglen*[0]
                vmask[mrmap[0]] = 1
                maskPtr = pointer if isinstance(pointer.ref, ScalarsReference) else Pointer((pointer.mat, (pointer.at[0], pointer.at[1] - mrmap[0])))
                content = mm256MaskloadPs(maskPtr, vmask, zeromask)
#             else:
#                 zm_i = [0] if mrmap[0] in zeromask else []
#                 ei = mmLoadSs(pointer, zm_i)
#                 pos = 4*[1]
#                 pos[mrmap[0]] = 0
#                 pos.reverse()
#                 content = mmShufflePs(ei, ei, tuple(pos))
#         elif (N == 1 and ((M <= nu and not isCompact) or (M < nu and isCompact))) or (M == 1 and N < nu):
        elif mrmap == range(len(mrmap)):
            l = len(mrmap)
            if isCompact or horizontal:
                if l == self.reglen:
                    content = mm256LoaduPs(pointer, zeromask)
                else:
                    vmask = self.reglen*[0]
                    vmask[:l] = l*[1] 
                    content = mm256MaskloadPs(pointer, vmask, zeromask)
            else: # Incompact case should appear only if vertical
                vmask = [1] + 7*[0]
                es = [ mm256MaskloadPs(Pointer((pointer.mat, (pointer.at[0] + i, pointer.at[1]))), vmask) for i in range(l) ]
                if l == 2: 
                    content = mm256UnpackloPs(es[0], es[1])
                elif l==3:
                    t0 = mm256UnpackloPs(es[0], es[1])
                    content = mm256ShufflePs(t0, es[2], (1,0,1,0))
                elif l==4:
                    t0 = mm256UnpackloPs(es[0], es[1])
                    t1 = mm256UnpackloPs(es[2], es[3])
                    content = mm256ShufflePs(t0, t1, (1,0,1,0))
                elif l==5:
                    t0 = mm256UnpackloPs(es[0], es[1])
                    t1 = mm256UnpackloPs(es[2], es[3])
                    t2 = mm256ShufflePs(t0, t1, (1,0,1,0))
                    content = mm256Permute2f128Ps(t2, es[4], [0,0,1,0,0,0,0,0])
                elif l==6:
                    t0 = mm256UnpackloPs(es[0], es[1])
                    t1 = mm256UnpackloPs(es[2], es[3])
                    t2 = mm256ShufflePs(t0, t1, (1,0,1,0))
                    t3 = mm256UnpackloPs(es[4], es[5])
                    content = mm256Permute2f128Ps(t2, t3, [0,0,1,0,0,0,0,0])
                elif l==7:
                    t0 = mm256UnpackloPs(es[0], es[1])
                    t1 = mm256UnpackloPs(es[2], es[3])
                    t2 = mm256ShufflePs(t0, t1, (1,0,1,0))
                    t3 = mm256UnpackloPs(es[4], es[5])
                    t4 = mm256ShufflePs(t3, es[6], (1,0,1,0))
                    content = mm256Permute2f128Ps(t2, t4, [0,0,1,0,0,0,0,0])
                elif l==8:
                    t0 = mm256UnpackloPs(es[0], es[1])
                    t1 = mm256UnpackloPs(es[2], es[3])
                    t2 = mm256ShufflePs(t0, t1, (1,0,1,0))
                    t3 = mm256UnpackloPs(es[4], es[5])
                    t4 = mm256UnpackloPs(es[6], es[7])
                    t5 = mm256ShufflePs(t3, t4, (1,0,1,0))
                    content = mm256Permute2f128Ps(t2, t5, [0,0,1,0,0,0,0,0])
        elif any(map(lambda rng: mrmap == rng, [range(i,j+1) for i in range(self.reglen) for j in range(self.reglen) if i<j ])):
            vmask = self.reglen*[0]
            for i in mrmap:
                vmask[i] = 1
            content = mm256MaskloadPs(Pointer((pointer.mat, (pointer.at[0], pointer.at[1] - mrmap[0]))), vmask, zeromask)


        if content is None:
            raise ValueError('mm256LoadGs does not support mrmap %s with %s layout yet' % (str(mrmap), 'horizontal' if horizontal else 'vertical'))
        return content
    
    def computeSym(self, nameList):
        return self.content.computeSym(self, nameList)
    
    def getZMask(self):
        return self.content.getZMask()
    
    def unparse(self, indent):
        content = self.content
        res = content.unparse(indent)
#         res += "\n" + DebugPrint(["\""+getReference(icode, self.pointer.mat).physLayout.name+"\"", "\" [ \"", str(self.pointer.at[0]), "\" , \"", str(self.pointer.at[1]), "\" ] at line \"", "__LINE__"]).unparse(indent);
        
#         if self.analysis is not None and isinstance(self.analysis, IntervalCongruenceReductionAnalysis):
#             content.env = self.env
#             self.analysis.propagateEnvToSrcs(content)
#             content = content.align(self.analysis)
        return res

    def setIterSet(self, indices, iterSet):
        super(mm256LoadGs, self).setIterSet(indices, iterSet)
        self.setSpaceReadMap(indices, iterSet)
    
    def printInst(self, indent):
#         return 'mmLoadGs(%s, %s, %s)' % (str(self.mrmap), self.orientation, self.content.printInst(indent))
        return 'mm256LoadGs(%r, %r, %s)' % (self.pointer, self.mrmap, self.orientation)
    
    def align(self, analysis):
        self.analysis = analysis
        return self
    
    def __eq__(self, other):
        return isinstance(other, VecAccess) and self.reglen == other.reglen and self.pointer == other.pointer and self.mrmap == other.mrmap and (self.horizontal == other.horizontal or self.isCompact and other.isCompact)
    
    def __hash__(self):
        return hash((hash('mm256LoadGs'), self.pointer.mat, self.pointer.at, str(self.mrmap), self.orientation))

class mm256StoreGs(MovStatement):
    '''Wrapper of a vector store instruction.
        
        Useful when we want to represent a composite store instruction as a single logical instruction and then have it
        easily replaced by a scalar during scalar replacement.
        '''
    def __init__(self, src, dst, mrmap, isCompact=True, isCorner=False, horizontal=True):
        super(mm256StoreGs, self).__init__()
        self.srcs += [src]
        self.mrmap = mrmap
        dstptr = dst if isinstance(dst, Pointer) else dst.pointer
        self.dst = VecDest(dstptr, 8, mrmap, horizontal, isCompact, isCorner)
        self.horizontal = horizontal
        self.isCompact = isCompact
        self.isCorner = isCorner
        self.orientation = 'horizontal' if horizontal else 'vertical'
        self.reglen = 8
        self.analysis = None
        self._content = None
    
    @property
    def content(self):
        if self._content is None:
            self._content = self.generateContent()
        return self._content
    
    def generateContent(self):
        dst = self.dst.pointer
        src = self.srcs[0]
        mrmap = self.mrmap
        horizontal = self.horizontal
        isCompact = self.isCompact
        content = None
        if len(mrmap) == 1:
            vmask = 8*[0]
            vmask[mrmap[0]] = 1
            content = [mm256MaskstorePs(vmask, src, dst)]
        elif mrmap == range(len(mrmap)):
            l = len(mrmap)
            if isCompact or horizontal:
                if l == self.reglen:
                    content = [mm256StoreuPs(src, dst)]
                else:
                    vmask = self.reglen*[0]
                    vmask[:l] = l*[1] 
                    content = [mm256MaskstorePs(vmask, src, dst)]
            else: # Incompact case should appear only if vertical
                content = []
                vmask = [1] + 7*[0]
                pcs = [ Pointer((dst.mat, (dst.at[0] + i, dst.at[1]))) for i in range(l) ]
                if l == 2: 
                    content.append( mm256MaskstorePs(vmask, src, pcs[0]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(src, src, (2,2,2,1)), pcs[1]) )
                elif l==3:
                    content.append( mm256MaskstorePs(vmask, src, pcs[0]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(src, src, (3,3,3,1)), pcs[1]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(src, src, (3,3,3,2)), pcs[2]) )
                elif l==4:
                    content.append( mm256MaskstorePs(vmask, src, pcs[0]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(src, mm256SetzeroPs(), (0,0,0,1)), pcs[1]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(src, mm256SetzeroPs(), (0,0,0,2)), pcs[2]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(src, mm256SetzeroPs(), (0,0,0,3)), pcs[3]) )
                elif l==5:
                    content.append( mm256MaskstorePs(vmask, src, pcs[0]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(src, mm256SetzeroPs(), (0,0,0,1)), pcs[1]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(src, mm256SetzeroPs(), (0,0,0,2)), pcs[2]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(src, mm256SetzeroPs(), (0,0,0,3)), pcs[3]) )
                    lane1 = mm256Permute2f128Ps(src, src, [1,0,0,0,0,0,0,1])
                    content.append( mm256MaskstorePs(vmask, lane1, pcs[4]) )
                elif l==6:
                    content.append( mm256MaskstorePs(vmask, src, pcs[0]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(src, mm256SetzeroPs(), (0,0,0,1)), pcs[1]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(src, mm256SetzeroPs(), (0,0,0,2)), pcs[2]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(src, mm256SetzeroPs(), (0,0,0,3)), pcs[3]) )
                    lane1 = mm256Permute2f128Ps(src, src, [1,0,0,0,0,0,0,1])
                    content.append( mm256MaskstorePs(vmask, lane1, pcs[4]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(lane1, lane1, (2,2,2,1)), pcs[5]) )
                elif l==7:
                    content.append( mm256MaskstorePs(vmask, src, pcs[0]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(src, mm256SetzeroPs(), (0,0,0,1)), pcs[1]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(src, mm256SetzeroPs(), (0,0,0,2)), pcs[2]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(src, mm256SetzeroPs(), (0,0,0,3)), pcs[3]) )
                    lane1 = mm256Permute2f128Ps(src, src, [1,0,0,0,0,0,0,1])
                    content.append( mm256MaskstorePs(vmask, lane1, pcs[4]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(lane1, lane1, (3,3,3,1)), pcs[5]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(lane1, lane1, (3,3,3,2)), pcs[6]) )
                elif l==8:
                    content.append( mm256MaskstorePs(vmask, src, pcs[0]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(src, mm256SetzeroPs(), (0,0,0,1)), pcs[1]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(src, mm256SetzeroPs(), (0,0,0,2)), pcs[2]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(src, mm256SetzeroPs(), (0,0,0,3)), pcs[3]) )
                    lane1 = mm256Permute2f128Ps(src, src, [1,0,0,0,0,0,0,1])
                    content.append( mm256MaskstorePs(vmask, lane1, pcs[4]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(lane1, mm256SetzeroPs(), (0,0,0,1)), pcs[5]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(lane1, mm256SetzeroPs(), (0,0,0,2)), pcs[6]) )
                    content.append( mm256MaskstorePs(vmask, mm256ShufflePs(lane1, mm256SetzeroPs(), (0,0,0,3)), pcs[7]) )
        
        if content is None:
            raise ValueError('mm256StoreGs does not support mrmap %s with %s layout yet' % (str(mrmap), 'horizontal' if horizontal else 'vertical'))
        return content
    
    def replaceRefs(self, refMap):
        dst = self.dst.replaceRefs(refMap)
        src = self.srcs[0].replaceRefs(refMap)
        if isinstance(dst, VecDest):
            self.dst = dst
            self.srcs[0] = src
            return self
        return Mov(src, dst)
    
    @staticmethod
    def canStore(reglen, mrmap, horizontal, isAligned=False):
        return reglen == 8
    
    @staticmethod
    def getStore(src, dst):
        mrmap = dst.mrmap
        if isinstance(mrmap, int):
            mrmap = [mrmap]
        return mm256StoreGs(src, dst, mrmap, dst.isCompact, dst.isCorner, dst.horizontal)
    
    def computeSym(self, nameList):
        return self.srcs[0].computeSym(nameList)[:len(self.mrmap)]
    
    def unparse(self, indent):
        content = self.content
#         if self.analysis is not None and isinstance(self.analysis, IntervalCongruenceReductionAnalysis):
#             for instr in content:
#                 instr.env = self.env
#                 self.analysis.propagateEnvToSrcs(instr)
#             content = [instr.align(self.analysis) for instr in content]
        return '\n'.join(instr.unparse(indent) for instr in content)
    
    def printInst(self, indent):
#         return 'mmStoreGs(%s, %s, %s)' % (str(self.mrmap), self.orientation, ','.join([instr.printInst(indent) for instr in self._content]))
        return 'mm256StoreGs(%r, %r, %r, %s)' % (self.dst, self.srcs[0], self.mrmap, self.orientation)
    
    def align(self, analysis):
        self.analysis = analysis
        return self

class mm256LoadGd(RValue, VecAccess):
    ''' Wrapper of a vector load instruction.
        
        Useful when we want to represent a composite load instruction as a single logical instruction and then have it
        easily replaced by a scalar during scalar replacement.
        '''
    def __init__(self, pointer, mrmap, isCompact=True, isCorner=False, horizontal=True, zeromask=None, not_using_mask=None):
        super(mm256LoadGd, self).__init__()
        self.pointer = pointer
        self.mrmap = mrmap
        self.isCompact = isCompact
        self.isCorner = isCorner
        self.horizontal = horizontal
        self.orientation = 'horizontal' if horizontal else 'vertical'
        self.zeromask = [] if zeromask is None else zeromask
        self.not_using_mask = [False]*len(mrmap) if not_using_mask is None else not_using_mask
        self.reglen = 4
        self.analysis = None
        self._content = None
    
    @property
    def content(self):
        if self._content == None:
            self._content = self.generateContent()
        return self._content
    
    def generateContent(self):
        mrmap = self.mrmap
        pointer = self.pointer
        zeromask = self.zeromask
        horizontal = self.horizontal
        isCompact = self.isCompact
        content = None
        if len(mrmap) == 1:
            if mrmap == [tuple(range(self.reglen))]:
                content = mm256BroadcastSd(pointer, zeromask)
            elif mrmap[0] == 0:
                content = mm256CastPd128Pd256(mmLoadSd(pointer))
            else:
                vmask = self.reglen*[0]
                vmask[mrmap[0]] = 1
                maskPtr = pointer if isinstance(pointer.ref, ScalarsReference) else Pointer((pointer.mat, (pointer.at[0], pointer.at[1] - mrmap[0])))
                content = mm256MaskloadPd(maskPtr, vmask, zeromask)
        elif mrmap == range(len(mrmap)):
            l = len(mrmap)
            if isCompact or horizontal:
                if l == self.reglen:
                    content = mm256LoaduPd(pointer, zeromask)
#                     content = asm256LoaduPd(pointer, zeromask)
                else:
                    vmask = self.reglen*[0]
                    vmask[:l] = l*[1] 
                    content = mm256MaskloadPd(pointer, vmask, zeromask)
            else: # Incompact case should appear only if vertical
#                 vmask = [1] + 3*[0]
#                 es = [ mm256MaskloadPd(Pointer((pointer.mat, (pointer.at[0] + i, pointer.at[1]))), vmask) for i in range(l) ]
                es = [ mm256CastPd128Pd256(mmLoadSd(Pointer((pointer.mat, (pointer.at[0] + i, pointer.at[1]))))) for i in range(l) ]
                if l == 2: 
                    content = mm256ShufflePd(es[0], es[1], [0,0,0,0])
                elif l==3:
                    content = mm256Permute2f128Pd(mm256UnpackloPd(es[0], es[1]), es[2], [0,0,1,0,0,0,0,0])
                elif l==4:
                    content = mm256Permute2f128Pd(mm256UnpackloPd(es[0], es[1]), mm256UnpackloPd(es[2], es[3]), (0,0,1,0,0,0,0,0))
        elif any(map(lambda rng: mrmap == rng, [range(i,j+1) for i in range(self.reglen) for j in range(self.reglen) if i<j ])):
            vmask = self.reglen*[0]
            for i in mrmap:
                vmask[i] = 1
            content = mm256MaskloadPd(Pointer((pointer.mat, (pointer.at[0], pointer.at[1] - mrmap[0]))), vmask, zeromask)

        if content is None:
            raise ValueError('mm256LoadGd does not support mrmap %s with %s layout yet' % (str(mrmap), 'horizontal' if horizontal else 'vertical'))
        return content
    
    def computeSym(self, nameList):
        return self.content.computeSym(self, nameList)
    
    def getZMask(self):
        return self.content.getZMask()
    
    def unparse(self, indent):
        content = self.content
#         if self.analysis is not None and isinstance(self.analysis, IntervalCongruenceReductionAnalysis):
#             content.env = self.env
#             self.analysis.propagateEnvToSrcs(content)
#             content = content.align(self.analysis)
        return content.unparse(indent)

    def setIterSet(self, indices, iterSet):
        super(mm256LoadGd, self).setIterSet(indices, iterSet)
        self.setSpaceReadMap(indices, iterSet)
    
    def printInst(self, indent):
#         return 'mmLoadGs(%s, %s, %s)' % (str(self.mrmap), self.orientation, self.content.printInst(indent))
        return 'mm256LoadGd(%r, %r, %r, %s, isCompact=%s)' % (self.pointer, self.mrmap, self.not_using_mask, self.orientation, str(self.isCompact))
    
    def align(self, analysis):
        self.analysis = analysis
        return self
    
    def __eq__(self, other):
        return isinstance(other, VecAccess) and self.reglen == other.reglen and self.pointer == other.pointer and self.mrmap == other.mrmap and (self.horizontal == other.horizontal or self.isCompact and other.isCompact)
    
    def __hash__(self):
        return hash((hash('mm256LoadGd'), self.pointer.mat, self.pointer.at, str(self.mrmap), self.orientation, self.isCompact))

class mm256StoreGd(MovStatement):
    '''Wrapper of a vector store instruction.
        
        Useful when we want to represent a composite store instruction as a single logical instruction and then have it
        easily replaced by a scalar during scalar replacement.
        '''
    def __init__(self, src, dst, mrmap, isCompact=True, isCorner=False, horizontal=True):
        super(mm256StoreGd, self).__init__()
        self.srcs += [src]
        self.mrmap = mrmap
        dstptr = dst if isinstance(dst, Pointer) else dst.pointer
        self.dst = VecDest(dstptr, 4, mrmap, horizontal, isCompact, isCorner)
        self.horizontal = horizontal
        self.isCompact = isCompact
        self.isCorner = isCorner
        self.orientation = 'horizontal' if horizontal else 'vertical'
        self.reglen = 4
        self.analysis = None
        self._content = None
    
    @property
    def content(self):
        if self._content is None:
            self._content = self.generateContent()
        return self._content
    
    def generateContent(self):
        dst = self.dst.pointer
        src = self.srcs[0]
        mrmap = self.mrmap
        horizontal = self.horizontal
        isCompact = self.isCompact
        content = None
        
        if len(mrmap) == 1:
            if mrmap[0] == 0:
                content = [ mmStoreSd(mm256CastPd256Pd128(src), dst) ]
            else:
                vmask = self.reglen*[0]
                vmask[mrmap[0]] = 1
                content = [mm256MaskstorePd(vmask, src, Pointer((dst.mat, (dst.at[0], dst.at[1]-mrmap[0]))))]
        elif mrmap == range(len(mrmap)):
            l = len(mrmap)
            if isCompact or horizontal:
                if l == self.reglen:
                    content = [mm256StoreuPd(src, dst)]
#                     content = [asm256StoreuPd(src, dst)]
                else:
                    vmask = self.reglen*[0]
                    vmask[:l] = l*[1] 
                    content = [mm256MaskstorePd(vmask, src, dst)]
            else: # Incompact case should appear only if vertical
                content = []
                vmask = [1] + 3*[0]
                pcs = [ Pointer((dst.mat, (dst.at[0] + i, dst.at[1]))) for i in range(l) ]
                if l == 2: 
                    content.append( mm256MaskstorePd(vmask, src, pcs[0]) )
                    content.append( mm256MaskstorePd(vmask, mm256ShufflePd(src, src, [0,0,0,1]), pcs[1]) )
                elif l==3:
                    content.append( mm256MaskstorePd(vmask, src, pcs[0]) )
                    content.append( mm256MaskstorePd(vmask, mm256ShufflePd(src, src, [0,0,0,1]), pcs[1]) )
                    content.append( mm256MaskstorePd(vmask, mm256Permute2f128Pd(src, src, [1,0,0,0,0,0,0,1]), pcs[2]) )
                elif l==4:
                    content.append( mm256MaskstorePd(vmask, src, pcs[0]) )
                    content.append( mm256MaskstorePd(vmask, mm256ShufflePd(src, src, [0,0,0,1]), pcs[1]) )
                    invlane = mm256Permute2f128Pd(src, src, [1,0,0,0,0,0,0,1])
                    content.append( mm256MaskstorePd(vmask, invlane, pcs[2]) )
                    content.append( mm256MaskstorePd(vmask, mm256ShufflePd(invlane, invlane, [0,0,0,1]), pcs[3]) )
        elif any(map(lambda rng: mrmap == rng, [range(i,j+1) for i in range(self.reglen) for j in range(self.reglen) if i<j ])):
            vmask = self.reglen*[0]
            for i in mrmap:
                vmask[i] = 1
            content = [mm256MaskstorePd(vmask, src, Pointer((dst.mat, (dst.at[0], dst.at[1]-mrmap[0]))))]
#         elif mrmap == [1, 2]:
#             if horizontal or isCompact:
#                 v1_2 = mmShufflePs(src, src, (3,3,2,1))
#                 content = [mmStorelPi(v1_2, PointerCast("__m64", dst))]
#         elif mrmap == [2, 3]:
#             if horizontal or isCompact:
#                 content = [mmStorehPi(src, PointerCast("__m64", dst))]
#         elif mrmap == [1, 2, 3]:
#             if horizontal or isCompact:
#                 pointer2 = Pointer((dst.mat, (dst.at[0], dst.at[1] + 1)))
#                 e1 = mmShufflePs(src, src, (1,1,1,1))
#                 content = [mmStoreSsNoZeromask(e1, dst), mmStorehPi(src, PointerCast("__m64", pointer2))]
        
        if content is None:
            raise ValueError('mm256StoreGd does not support mrmap %s with %s layout yet' % (str(mrmap), 'horizontal' if horizontal else 'vertical'))
#         #DEBUG
#         pi,pj=0,0
#         for _ in range(len(mrmap)):
#             content.append(DebugPrint(["\"Storing "+getReference(icode, dst.mat).physLayout.name+"\"", "\" [ \"", str(dst.at[0]+pi), "\" , \"", str(dst.at[1]+pj), "\" ] at line \"", "__LINE__"]));
#             if horizontal:
#                 pj += 1
#             else:
#                 pi += 1
#         #DEBUG
        return content
    
    def replaceRefs(self, refMap):
        dst = self.dst.replaceRefs(refMap)
        src = self.srcs[0].replaceRefs(refMap)
        if isinstance(dst, VecDest):
            self.dst = dst
            self.srcs[0] = src
            return self
        return Mov(src, dst)
    
    @staticmethod
    def canStore(reglen, mrmap, horizontal, isAligned=False):
        return reglen == 4
    
    @staticmethod
    def getStore(src, dst):
        mrmap = dst.mrmap
        if isinstance(mrmap, int):
            mrmap = [mrmap]
        return mm256StoreGd(src, dst, mrmap, dst.isCompact, dst.isCorner, dst.horizontal)
    
    def computeSym(self, nameList):
        return self.srcs[0].computeSym(nameList)[:len(self.mrmap)]
    
    def unparse(self, indent):
        content = self.content
#         if self.analysis is not None and isinstance(self.analysis, IntervalCongruenceReductionAnalysis):
#             for instr in content:
#                 instr.env = self.env
#                 self.analysis.propagateEnvToSrcs(instr)
#             content = [instr.align(self.analysis) for instr in content]
        return '\n'.join(instr.unparse(indent) for instr in content)
    
    def printInst(self, indent):
#         return 'mmStoreGs(%s, %s, %s)' % (str(self.mrmap), self.orientation, ','.join([instr.printInst(indent) for instr in self._content]))
        return 'mm256StoreGd(%r, %r, %r, %s, isCompact=%s)' % (self.dst, self.srcs[0], self.mrmap, self.orientation, str(self.isCompact))
    
    def align(self, analysis):
        self.analysis = analysis
        return self

class mm256LoaduPd(RValue, VecAccess):
    def __init__(self, pointer, zeromask=None):
        super(mm256LoaduPd, self).__init__()
        self.reglen = 4
        self.mrmap = [0,1,2,3]
        self.zeromask = [0]*self.reglen
        if zeromask is not None:
            for pos in zeromask:
                self.zeromask[pos] = 1
        self.pointer = pointer

    def computeSym(self, nameList):
        p = self.pointer.computeSym(nameList)
        return [ sympify(p+'_0'), sympify(p+'_1'), sympify(p+'_2'), sympify(p+'_3') ] 

    def getZMask(self):
        return self.zeromask
    
    def unparse(self, indent):
        return indent + "_mm256_loadu_pd(" + self.pointer.unparse("") + ")"

    def printInst(self, indent):
        return indent + "mm256LoaduPd( " + self.pointer.printInst("") + " )"

    def __eq__(self, other):
        return isinstance(other, mm256LoaduPd) and self.pointer == other.pointer
    
    def __hash__(self):
        return hash((hash("mm256LoaduPd"), self.pointer.mat, self.pointer.at))

class asm256LoaduPd(mm256LoaduPd):
    def __init__(self, pointer, zeromask=None):
        super(asm256LoaduPd, self).__init__(pointer, zeromask)

    def unparse(self, indent):
        return indent + "_asm256_loadu_pd(" + self.pointer.unparse("") + ")"

    def printInst(self, indent):
        return indent + "asm256LoaduPd( " + self.pointer.printInst("") + " )"
    
    @staticmethod
    def add_func_defs():
        f =  "static __inline__ __m256d _asm256_loadu_pd(const double* p) {\n"
        f += "  __m256d v;\n"
        f += "  __asm__(\"vmovupd %1, %0\" : \"=x\" (v) : \"m\" (*p));\n"
        f += "  return v;\n}\n"
        return [f]
    
class mm256MaskloadPd(RValue, VecAccess):
    def __init__(self, pointer, vecmask, zeromask=None):
        super(mm256MaskloadPd, self).__init__()
        self.reglen = 4
        self.mrmap = []
        self.zeromask = []
        for m,i in zip(vecmask,range(4)):
            self.mrmap += [i] if m else [-1]
            self.zeromask += [0] if m else [1]
        if zeromask is not None:
            for pos in zeromask: # there should at most be 1 pos == 0 here
                self.zeromask[pos] = 1
        self.pointer = pointer
        self.vecmask = vecmask

    def computeSym(self, nameList):
        p = self.pointer.computeSym(nameList)
        res = []
        for m,i in zip(self.vecmask,range(4)):
            res += [sympify(p+'_'+str(i))] if m else [sympify(0)]
        return res 

    def getZMask(self):
        return self.zeromask
        
    def unparse(self, indent):
        vm = "_mm256_setr_epi64x("
        for m,i in zip(self.vecmask,range(4)):
            vm += "(__int64)1 << 63" if m else "0"
            vm += ", " if i<3 else ")"
        return indent + "_mm256_maskload_pd(" + self.pointer.unparse("") + ", " + vm + ")"
    
    def printInst(self, indent):
        return indent + "mm256MaskloadPd( " + self.pointer.printInst("") + ", " + str(self.vecmask) + ")"

    def __eq__(self, other):
        return isinstance(other, mm256MaskloadPd) and self.vecmask == other.vecmask and self.pointer == other.pointer
    
    def __hash__(self):
        return hash((hash("mm256MaskloadPd"), hash(tuple(self.vecmask)), self.pointer.mat, self.pointer.at))

class mm256BroadcastSd(RValue, VecAccess):
    def __init__(self, pointer, zeromask=None):
        super(mm256BroadcastSd, self).__init__()
        self.reglen = 4
        self.mrmap = [(0,1,2,3)]
        self.zeromask = [0]*self.reglen
        if zeromask is not None: # In this case all the positions have to be zero
            self.zeromask = [1]*self.reglen
        self.pointer = pointer

    def computeSym(self, nameList):
        p = self.pointer.computeSym(nameList)
        return [ sympify(p+'_0'), sympify(p+'_0'), sympify(p+'_0'), sympify(p+'_0') ] 

    def getZMask(self):
        return self.zeromask
        
    def unparse(self, indent):
        return indent + "_mm256_broadcast_sd(" + self.pointer.unparse("") + ")"
    
    def printInst(self, indent):
        return indent + "mm256BroadcastSd( " + self.pointer.printInst("") + " )"

    def __eq__(self, other):
        return isinstance(other, mm256BroadcastSd) and self.pointer == other.pointer
    
    def __hash__(self):
        return hash((hash("mm256BroadcastSd"), self.pointer.mat, self.pointer.at))

class mm256StoreuPd(MovStatement):
    mrmap = [0,1,2,3] # static definition of the mem-reg mapping imposed by the store
    def __init__(self, src, dst):
        super(mm256StoreuPd, self).__init__()
        self.dst = VecDest(dst, 4, self.mrmap) if isinstance(dst, Pointer) else VecDest(dst.pointer, 4, self.mrmap)
        self.srcs += [ src ]
#         self.slen = 4
#         self.dlen = 4
        

    def replaceRefs(self, refMap):
        dst = self.dst.replaceRefs(refMap)
        src = self.srcs[0].replaceRefs(refMap)
        if isinstance(dst, VecDest):
            self.dst = dst
            self.srcs[0] = src
            return self
        return Mov(src, dst)

    @staticmethod
    def canStore(reglen, mrmap, horizontal=True, isAligned=False):
        if not horizontal: return False
        return reglen == 4 and mrmap == mm256StoreuPd.mrmap

    @staticmethod
    def getStore(src, dst):
        return mm256StoreuPd(src, dst)

    def computeSym(self, nameList):
        return self.srcs[0].computeSym(nameList) 
     
    def unparse(self, indent):
        return indent + "_mm256_storeu_pd(" + self.dst.unparse("") + ", " + self.srcs[0].unparse("") + ");"
    
    def printInst(self, indent):
        return indent + "mm256StoreuPd( " + self.srcs[0].printInst("") + ", " + self.dst.printInst("") + " )"

class asm256StoreuPd(mm256StoreuPd):
    def __init__(self, src, dst):
        super(asm256StoreuPd, self).__init__(src, dst)

    def unparse(self, indent):
        return indent + "_asm256_storeu_pd(" + self.dst.unparse("") + ", " + self.srcs[0].unparse("") + ");"

    def printInst(self, indent):
        return indent + "asm256StoreuPd( " + self.srcs[0].printInst("") + ", " + self.dst.printInst("") + " )"
    
    @staticmethod
    def add_func_defs():
        f =  "static __inline__ void _asm256_storeu_pd(double* p, const __m256d& v) {\n"
        f += "  __asm__(\"vmovupd %1, %0\" : \"=rm\" (*p) : \"x\" (v));\n}\n"
        return [f]

class mm256MaskstorePd(MovStatement):
    def __init__(self, vecmask, src, dst):
        super(mm256MaskstorePd, self).__init__()
        self.mrmap = []
        for m,i in zip(vecmask,range(4)):
            self.mrmap += [i] if m else [-1]
        self.dst = VecDest(dst, 4, self.mrmap) if isinstance(dst, Pointer) else VecDest(dst.pointer, 4, self.mrmap) 
        self.srcs += [ src ]
        self.vecmask = vecmask
 
    @staticmethod
    def canStore(reglen, mrmap, horizontal=True, isAligned=False):
        if not horizontal: return False
        itcan = True
        for m,i in zip(mrmap,range(4)):
            itcan = itcan and (m == i or m == -1)
        return reglen == 4 and itcan

    @staticmethod
    def getStore(src, dst):
        vecmask = [ (0 if r == -1 else 1) for r in dst.mrmap ]
        vecmask.extend([0 for _ in range(len(dst.mrmap), 4)])
        return mm256MaskstorePd(vecmask, src, dst)
     
    def replaceRefs(self, refMap):
        dst = self.dst.replaceRefs(refMap)
        src = self.srcs[0].replaceRefs(refMap)
        if isinstance(dst, VecDest):
            self.dst = dst
            self.srcs[0] = src
            return self
        return Mov(src, dst)
      
    def computeSym(self, nameList):
        src = self.srcs[0].computeSym(nameList)
        res = []
        for m,i in zip(self.vecmask,range(4)):
            res += [src[i]] if m else ["-"]
        return res 
 
    def unparse(self, indent):
        vm = "_mm256_setr_epi64x("
        for m,i in zip(self.vecmask,range(4)):
            vm += "(__int64)1 << 63" if m else "0"
            vm += ", " if i<3 else ")"
        return indent + "_mm256_maskstore_pd(" + self.dst.unparse("") + ", " + vm + ", " + self.srcs[0].unparse("") + ");"
     
    def printInst(self, indent):
        return indent + "mm256MaskstorePd( " + str(self.vecmask) + ", " + self.srcs[0].printInst("") + ", " + self.dst.printInst("") + " )"

class mm256Set1Pd(RValue):
    def __init__(self, src):
        super(mm256Set1Pd, self).__init__()
        self.srcs += [ src ]

    def computeSym(self, nameList):
        sym = self.srcs[0].computeSym(nameList)[0]
        return [ sym, sym, sym, sym ] 

    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        return [ s0ZMask[0], s0ZMask[0], s0ZMask[0], s0ZMask[0] ]
    
    def unparse(self, indent):
        return indent + "_mm256_set1_pd(" + self.srcs[0].unparse("") + ")"
    
    def printInst(self, indent):
        return indent + "mm256Set1Pd( " + self.srcs[0].printInst("") + " )"

class mm256SetPd(RValue):
    def __init__(self, src0, src1, src2, src3):
        super(mm256SetPd, self).__init__()
        self.srcs += [ src0, src1, src2, src3 ]

    def computeSym(self, nameList):
        return [ self.srcs[3].computeSym(nameList)[0], self.srcs[2].computeSym(nameList)[0], self.srcs[1].computeSym(nameList)[0], self.srcs[0].computeSym(nameList)[0] ] 

    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        s2ZMask = self.srcs[2].getZMask()
        s3ZMask = self.srcs[3].getZMask()
        return [ s3ZMask[0], s2ZMask[0], s1ZMask[0], s0ZMask[0] ]
    
    def unparse(self, indent):
        return indent + "_mm256_set_pd(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ", " + self.srcs[2].unparse("") + ", " + self.srcs[3].unparse("") + ")"
    
    def printInst(self, indent):
        return indent + "mm256SetPd( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + self.srcs[2].printInst("") + ", " + self.srcs[3].printInst("") + " )"

class mm256CastPd128Pd256(RValue):
    def __init__(self, src):
        super(mm256CastPd128Pd256, self).__init__()
        self.srcs += [ src ] 

    def computeSym(self, nameList):
        src = self.srcs[0].computeSym(nameList)
        x = sympify('x') # Unknown
        return [ src[0], src[1], x, x ]

    def unparse(self, indent):
        return indent + "_mm256_castpd128_pd256(" + self.srcs[0].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mm256CastPd128Pd256( " + self.srcs[0].printInst("") + " )"

class mm256CastPd256Pd128(RValue):
    def __init__(self, src):
        super(mm256CastPd256Pd128, self).__init__()
        self.srcs += [ src ] 

    def computeSym(self, nameList):
        src = self.srcs[0].computeSym(nameList)
        return [ src[0], src[1] ]

    def unparse(self, indent):
        return indent + "_mm256_castpd256_pd128(" + self.srcs[0].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mm256CastPd256Pd128( " + self.srcs[0].printInst("") + " )"

class mm256AddPd(RValue):
    def __init__(self, src0, src1):
        super(mm256AddPd, self).__init__()
        self.srcs += [ src0, src1 ] 

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[0] + src1[0], src0[1] + src1[1], src0[2] + src1[2], src0[3] + src1[3] ]

    def unparse(self, indent):
        return indent + "_mm256_add_pd(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mm256AddPd( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mm256SubPd(RValue):
    def __init__(self, src0, src1):
        super(mm256SubPd, self).__init__()
        self.srcs += [ src0, src1 ] 

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[0] - src1[0], src0[1] - src1[1], src0[2] - src1[2], src0[3] - src1[3] ]

    def unparse(self, indent):
        return indent + "_mm256_sub_pd(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mm256SubPd( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mm256MulPd(RValue):
    def __init__(self, src0, src1):
        super(mm256MulPd, self).__init__()
        self.srcs += [ src0, src1 ] 

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[0] * src1[0], src0[1] * src1[1], src0[2] * src1[2], src0[3] * src1[3] ]

    def unparse(self, indent):
        return indent + "_mm256_mul_pd(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mm256MulPd( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mm256DivPd(RValue):
    def __init__(self, src0, src1):
        super(mm256DivPd, self).__init__()
        self.srcs += [ src0, src1 ] 

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[0] / src1[0], src0[1] / src1[1], src0[2] / src1[2], src0[3] / src1[3] ]

    def unparse(self, indent):
        return indent + "_mm256_div_pd(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mm256DivPd( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mm256SqrtPd(RValue):
    def __init__(self, src):
        super(mm256SqrtPd, self).__init__()
        self.srcs += [ src ] 

    def unparse(self, indent):
        return indent + "_mm256_sqrt_pd(" + self.srcs[0].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mm256SqrtPd( " + self.srcs[0].printInst("") + " )"

class mm256HaddPd(RValue):
    def __init__(self, src0, src1):
        super(mm256HaddPd, self).__init__()
        self.srcs += [ src0, src1 ]

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[0]+src0[1], src1[0]+src1[1], src0[2]+src0[3], src1[2]+src1[3] ]
        
    def unparse(self, indent):
        return indent + "_mm256_hadd_pd(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mm256HaddPd( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mm256SetzeroPd(RValue):
    def __init__(self):
        super(mm256SetzeroPd, self).__init__()

    def computeSym(self, nameList):
        return [ sympify(0), sympify(0), sympify(0), sympify(0) ]
        
    def unparse(self, indent):
        return indent + "_mm256_setzero_pd()" 

    def printInst(self, indent):
        return indent + "mm256SetzeroPd()"
 
class mm256Permute2f128Pd(RValue):
    def __init__(self, src0, src1, immBitList):
        super(mm256Permute2f128Pd, self).__init__()
        self.srcs += [ src0, src1 ]
        self.immBitList = immBitList
        imm = 0
        for bit in immBitList:
            imm = (imm << 1) | int(bit)
        self.imm = imm 

    def select4(self, src0, src1, control, ifzero):
        imm = 0
        if control[0]:
            return [ifzero]*2
        for bit in control[2:]:
            imm = (imm << 1) | int(bit)
        if imm == 0:
            return [src0[i] for i in range(2)]
        if imm == 1:
            return [src0[i] for i in range(2,4)]
        if imm == 2:
            return [src1[i] for i in range(2)]
        if imm == 3:
            return [src1[i] for i in range(2,4)]
        
        
    def computeSym(self, nameList): # To be fixed (more general)
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return self.select4(src0, src1, self.immBitList[4:], sympify(0)) + self.select4(src1, src1, self.immBitList[:4], sympify(0)) # Is the def in Intrinsics guide buggy?? 
    
    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return self.select4(s0ZMask, s1ZMask, self.immBitList[4:], 1) + self.select4(s1ZMask, s1ZMask, self.immBitList[:4], 1) # Is the def in Intrinsics guide buggy?? 
        
    def unparse(self, indent):
        return indent + "_mm256_permute2f128_pd(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ", " + str(self.imm) + ")" 

    def printInst(self, indent):
        return indent + "mm256Permute2f128Pd( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + ", " + str(self.immBitList) + " )"

class mm256PermutePd(RValue):
    def __init__(self, src, immBitList):
        super(mm256PermutePd, self).__init__()
        self.srcs += [ src ]
        self.immBitList = immBitList
        imm = 0
        for bit in immBitList:
            imm = (imm << 1) | int(bit)
        self.imm = imm 

    def computeSym(self, nameList):
        src = self.srcs[0].computeSym(nameList)
        return [ src[1] if self.immBitList[3] else src[0], src[1] if self.immBitList[2] else src[0], src[3] if self.immBitList[1] else src[2], src[3] if self.immBitList[0] else src[2] ] 
    
    def getZMask(self):
        sZMask = self.srcs[0].getZMask()
        return [ sZMask[1] if self.immBitList[3] else sZMask[0], sZMask[1] if self.immBitList[2] else sZMask[0], sZMask[3] if self.immBitList[1] else sZMask[2], sZMask[3] if self.immBitList[0] else sZMask[2] ] 
        
    def unparse(self, indent):
        return indent + "_mm256_permute_pd(" + self.srcs[0].unparse("") + ", " + str(self.imm) + ")" 

    def printInst(self, indent):
        return indent + "mm256PermutePd( " + self.srcs[0].printInst("") + ", " + str(self.immBitList) + " )"

class mm256ShufflePd(RValue):
    def __init__(self, src0, src1, immBitList):
        super(mm256ShufflePd, self).__init__()
        self.srcs += [ src0, src1 ]
        self.immBitList = immBitList
        imm = 0
        for bit in immBitList:
            imm = (imm << 1) | int(bit)
        self.imm = imm 

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[self.immBitList[3]], src1[self.immBitList[2]], src0[2 + self.immBitList[1]], src1[2 + self.immBitList[0]] ]
    
    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [ s0ZMask[self.immBitList[3]], s1ZMask[self.immBitList[2]], s0ZMask[2 + self.immBitList[1]], s1ZMask[2 + self.immBitList[0]] ]

    def unparse(self, indent):
        return indent + "_mm256_shuffle_pd(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ", " + str(self.imm) + ")" 

    def printInst(self, indent):
        return indent + "mm256ShufflePd( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + ", " + str(self.immBitList) + " )"

class mm256UnpackloPd(RValue):
    def __init__(self, src0, src1):
        super(mm256UnpackloPd, self).__init__()
        self.srcs += [ src0, src1 ]

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[0], src1[0], src0[2], src1[2] ]

    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [ s0ZMask[0], s1ZMask[0], s0ZMask[2], s1ZMask[2] ]

    def unparse(self, indent):
        return indent + "_mm256_unpacklo_pd(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mm256UnpackloPd( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mm256UnpackhiPd(RValue):
    def __init__(self, src0, src1):
        super(mm256UnpackhiPd, self).__init__()
        self.srcs += [ src0, src1 ]

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[1], src1[1], src0[3], src1[3] ]

    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [ s0ZMask[1], s1ZMask[1], s0ZMask[3], s1ZMask[3] ]

    def unparse(self, indent):
        return indent + "_mm256_unpackhi_pd(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mm256UnpackhiPd( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mm256BlendPd(RValue):
    def __init__(self, src0, src1, immBitList):
        super(mm256BlendPd, self).__init__()
        self.srcs += [ src0, src1 ]
        self.immBitList = immBitList
        imm = 0
        for bit in immBitList:
            imm = (imm << 1) | int(bit)
        self.imm = imm 

    def computeSym(self, nameList):
        e = 3
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src1[i] if self.immBitList[e-i] else src0[i] for i in range(e) ]

    def getZMask(self):
        e = 3
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [ s1ZMask[i] if self.immBitList[e-i] else s0ZMask[i] for i in range(e) ]

    def unparse(self, indent):
        return indent + "_mm256_blend_pd(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ", " + str(self.imm) + ")" 

    def printInst(self, indent):
        return indent + "mm256BlendPd( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + ", " + str(self.immBitList) + " )"

class mm256LoaduPs(RValue, VecAccess):
    def __init__(self, pointer, zeromask=None):
        super(mm256LoaduPs, self).__init__()
        self.reglen = 8
        self.mrmap = range(self.reglen)
        self.zeromask = [0]*self.reglen
        if zeromask is not None:
            for pos in zeromask:
                self.zeromask[pos] = 1
        self.pointer = pointer

    def computeSym(self, nameList):
        p = self.pointer.computeSym(nameList)
        return [ sympify(p+'_'+str(i)) for i in range(self.reglen) ] 

    def getZMask(self):
        return self.zeromask
    
    def unparse(self, indent):
        return indent + "_mm256_loadu_ps(" + self.pointer.unparse("") + ")"
    
    def printInst(self, indent):
        return indent + "mm256LoaduPs( " + self.pointer.printInst("") + " )"

    def __eq__(self, other):
        return isinstance(other, mm256LoaduPs) and self.pointer == other.pointer
    
    def __hash__(self):
        return hash((hash("mm256LoaduPs"), self.pointer.mat, self.pointer.at))

class mm256MaskloadPs(RValue, VecAccess):
    def __init__(self, pointer, vecmask, zeromask=None):
        super(mm256MaskloadPs, self).__init__()
        self.reglen = 8
        self.mrmap = []
        self.zeromask = []
        for m,i in zip(vecmask,range(8)):
            self.mrmap += [i] if m else [-1]
            self.zeromask += [0] if m else [1]
        if zeromask is not None:
            for pos in zeromask: # there should at most be 1 pos == 0 here
                self.zeromask[pos] = 1
        self.pointer = pointer
        self.vecmask = vecmask

    def computeSym(self, nameList):
        p = self.pointer.computeSym(nameList)
        res = []
        for m,i in zip(self.vecmask,range(self.reglen)):
            res += [sympify(p+'_'+str(i))] if m else [sympify(0)]
        return res 

    def getZMask(self):
        return self.zeromask
        
    def unparse(self, indent):
        vm = "_mm256_setr_epi32("
        for m,i in zip(self.vecmask,range(self.reglen)):
            vm += "(int)1 << 31" if m else "0"
            vm += ", " if i<7 else ")"
        return indent + "_mm256_maskload_ps(" + self.pointer.unparse("") + ", " + vm + ")"
    
    def printInst(self, indent):
        return indent + "mm256MaskloadPs( " + self.pointer.printInst("") + ", " + str(self.vecmask) + ")"

    def __eq__(self, other):
        return isinstance(other, mm256MaskloadPs) and self.vecmask == other.vecmask and self.pointer == other.pointer
    
    def __hash__(self):
        return hash((hash("mm256MaskloadPs"), hash(tuple(self.vecmask)), self.pointer.mat, self.pointer.at))

class mm256BroadcastSs(RValue, VecAccess):
    def __init__(self, pointer, zeromask=None):
        super(mm256BroadcastSs, self).__init__()
        self.reglen = 8
        self.mrmap = [tuple(range(self.reglen))]
        self.zeromask = [0]*self.reglen
        if zeromask is not None: # In this case all the positions have to be zero
            self.zeromask = [1]*self.reglen
        self.pointer = pointer

    def computeSym(self, nameList):
        p = self.pointer.computeSym(nameList)
        return [ sympify(p+'_0') ]*self.reglen 

    def getZMask(self):
        return self.zeromask
        
    def unparse(self, indent):
        return indent + "_mm256_broadcast_ss(" + self.pointer.unparse("") + ")"
    
    def printInst(self, indent):
        return indent + "mm256BroadcastSs( " + self.pointer.printInst("") + " )"

    def __eq__(self, other):
        return isinstance(other, mm256BroadcastSs) and self.pointer == other.pointer
    
    def __hash__(self):
        return hash((hash("mm256BroadcastSs"), self.pointer.mat, self.pointer.at))

class mm256StoreuPs(MovStatement):
    mrmap = range(8) # static definition of the mem-reg mapping imposed by the store
    def __init__(self, src, dst):
        super(mm256StoreuPs, self).__init__()
        self.dst = VecDest(dst, 8, self.mrmap) if isinstance(dst, Pointer) else VecDest(dst.pointer, 8, self.mrmap)
        self.srcs += [ src ]
        

    def replaceRefs(self, refMap):
        dst = self.dst.replaceRefs(refMap)
        src = self.srcs[0].replaceRefs(refMap)
        if isinstance(dst, VecDest):
            self.dst = dst
            self.srcs[0] = src
            return self
        return Mov(src, dst)

    @staticmethod
    def canStore(reglen, mrmap, horizontal=True, isAligned=False):
        if not horizontal: return False
        return reglen == 8 and mrmap == mm256StoreuPs.mrmap

    @staticmethod
    def getStore(src, dst):
        return mm256StoreuPs(src, dst)

    def computeSym(self, nameList):
        return self.srcs[0].computeSym(nameList) 
     
    def unparse(self, indent):
        return indent + "_mm256_storeu_ps(" + self.dst.unparse("") + ", " + self.srcs[0].unparse("") + ");"
    
    def printInst(self, indent):
        return indent + "mm256StoreuPs( " + self.srcs[0].printInst("") + ", " + self.dst.printInst("") + " )"

class mm256MaskstorePs(MovStatement):
    def __init__(self, vecmask, src, dst):
        super(mm256MaskstorePs, self).__init__()
        self.mrmap = []
        for m,i in zip(vecmask,range(8)):
            self.mrmap += [i] if m else [-1]
        self.dst = VecDest(dst, 8, self.mrmap) if isinstance(dst, Pointer) else VecDest(dst.pointer, 8, self.mrmap) 
        self.srcs += [ src ]
        self.vecmask = vecmask
 
    @staticmethod
    def canStore(reglen, mrmap, horizontal=True, isAligned=False):
        if not horizontal: return False
        itcan = True
        for m,i in zip(mrmap,range(8)):
            itcan = itcan and (m == i or m == -1)
        return reglen == 8 and itcan

    @staticmethod
    def getStore(src, dst):
        vecmask = [ (0 if r == -1 else 1) for r in dst.mrmap ]
        vecmask.extend([0 for _ in range(len(dst.mrmap), 8)])
        return mm256MaskstorePs(vecmask, src, dst)
     
    def replaceRefs(self, refMap):
        dst = self.dst.replaceRefs(refMap)
        src = self.srcs[0].replaceRefs(refMap)
        if isinstance(dst, VecDest):
            self.dst = dst
            self.srcs[0] = src
            return self
        return Mov(src, dst)
      
    def computeSym(self, nameList):
        src = self.srcs[0].computeSym(nameList)
        res = []
        for m,i in zip(self.vecmask,range(4)):
            res += [src[i]] if m else ["-"]
        return res 
 
    def unparse(self, indent):
        vm = "_mm256_setr_epi32("
        for m,i in zip(self.vecmask,range(8)):
            vm += "(int)1 << 31" if m else "0"
            vm += ", " if i<7 else ")"
        return indent + "_mm256_maskstore_ps(" + self.dst.unparse("") + ", " + vm + ", " + self.srcs[0].unparse("") + ");"
     
    def printInst(self, indent):
        return indent + "mm256MaskstorePs( " + str(self.vecmask) + ", " + self.srcs[0].printInst("") + ", " + self.dst.printInst("") + " )"

class mm256AddPs(RValue):
    def __init__(self, src0, src1):
        super(mm256AddPs, self).__init__()
        self.srcs += [ src0, src1 ] 

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[i] + src1[i] for i in range(8) ]

    def unparse(self, indent):
        return indent + "_mm256_add_ps(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mm256AddPs( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mm256SubPs(RValue):
    def __init__(self, src0, src1):
        super(mm256SubPs, self).__init__()
        self.srcs += [ src0, src1 ] 

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[i] - src1[i] for i in range(8) ]

    def unparse(self, indent):
        return indent + "_mm256_sub_ps(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mm256SubPs( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mm256MulPs(RValue):
    def __init__(self, src0, src1):
        super(mm256MulPs, self).__init__()
        self.srcs += [ src0, src1 ] 

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[i] * src1[i] for i in range(8) ]

    def unparse(self, indent):
        return indent + "_mm256_mul_ps(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mm256MulPs( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mm256HaddPs(RValue):
    def __init__(self, src0, src1):
        super(mm256HaddPs, self).__init__()
        self.srcs += [ src0, src1 ]

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        lane0 = [ src0[0]+src0[1], src0[2]+src0[3], src1[0]+src1[1], src1[2]+src1[3] ]
        lane1 = [ src0[4]+src0[5], src0[6]+src0[7], src1[4]+src1[5], src1[6]+src1[7] ]
        return lane0 + lane1
        
    def unparse(self, indent):
        return indent + "_mm256_hadd_ps(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mm256HaddPs( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mm256Permute2f128Ps(RValue):
    def __init__(self, src0, src1, immBitList):
        super(mm256Permute2f128Ps, self).__init__()
        self.srcs += [ src0, src1 ]
        self.immBitList = immBitList
        imm = 0
        for bit in immBitList:
            imm = (imm << 1) | int(bit)
        self.imm = imm 

    def select4(self, src0, src1, control, ifzero):
        imm = 0
        if control[0]:
            return [ifzero]*4
        for bit in control[2:]:
            imm = (imm << 1) | int(bit)
        if imm == 0:
            return [src0[i] for i in range(4)]
        if imm == 1:
            return [src0[i] for i in range(4,8)]
        if imm == 2:
            return [src1[i] for i in range(4)]
        if imm == 3:
            return [src1[i] for i in range(4,8)]
        
        
    def computeSym(self, nameList): # To be fixed (more general)
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return self.select4(src0, src1, self.immBitList[4:], sympify(0)) + self.select4(src1, src1, self.immBitList[:4], sympify(0)) # Is the def in Intrinsics guide buggy?? 
    
    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return self.select4(s0ZMask, s1ZMask, self.immBitList[4:], 1) + self.select4(s1ZMask, s1ZMask, self.immBitList[:4], 1) # Is the def in Intrinsics guide buggy?? 
        
    def unparse(self, indent):
        return indent + "_mm256_permute2f128_ps(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ", " + str(self.imm) + ")" 

    def printInst(self, indent):
        return indent + "mm256Permute2f128Ps( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + ", " + str(self.immBitList) + " )"

class mm256UnpackloPs(RValue):
    def __init__(self, src0, src1):
        super(mm256UnpackloPs, self).__init__()
        self.srcs += [ src0, src1 ]

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        lane0 = [ src0[0], src1[0], src0[1], src1[1] ]
        lane1 = [ src0[4], src1[4], src0[5], src1[5] ]
        return lane0 + lane1

    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        lane0 = [ s0ZMask[0], s1ZMask[0], s0ZMask[1], s1ZMask[1] ]
        lane1 = [ s0ZMask[4], s1ZMask[4], s0ZMask[5], s1ZMask[5] ]
        return lane0 + lane1

    def unparse(self, indent):
        return indent + "_mm256_unpacklo_ps(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mm256UnpackloPs( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mm256UnpackhiPs(RValue):
    def __init__(self, src0, src1):
        super(mm256UnpackhiPs, self).__init__()
        self.srcs += [ src0, src1 ]

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        lane0 = [ src0[2], src1[2], src0[3], src1[3] ]
        lane1 = [ src0[6], src1[6], src0[7], src1[7] ]
        return lane0 + lane1

    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        lane0 = [ s0ZMask[2], s1ZMask[2], s0ZMask[3], s1ZMask[3] ]
        lane1 = [ s0ZMask[6], s1ZMask[6], s0ZMask[7], s1ZMask[7] ]
        return lane0 + lane1

    def unparse(self, indent):
        return indent + "_mm256_unpackhi_ps(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mm256UnpackhiPs( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mm256BlendPs(RValue):
    def __init__(self, src0, src1, immBitList):
        super(mm256BlendPs, self).__init__()
        self.srcs += [ src0, src1 ]
        self.immBitList = immBitList
        imm = 0
        for bit in immBitList:
            imm = (imm << 1) | int(bit)
        self.imm = imm 

    def computeSym(self, nameList):
        e = 7
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src1[i] if self.immBitList[e-i] else src0[i] for i in range(e) ]

    def getZMask(self):
        e = 7
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [ s1ZMask[i] if self.immBitList[e-i] else s0ZMask[i] for i in range(e) ]

    def unparse(self, indent):
        return indent + "_mm256_blend_ps(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ", " + str(self.imm) + ")" 

    def printInst(self, indent):
        return indent + "mm256BlendPs( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + ", " + str(self.immBitList) + " )"

class mm256ShufflePs(RValue):
    def __init__(self, src0, src1, immTuple):
        super(mm256ShufflePs, self).__init__()
        self.srcs += [ src0, src1 ]
        self.immTuple = tuple(immTuple)

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        lane0 = [ src0[self.immTuple[3]], src0[self.immTuple[2]], src1[self.immTuple[1]], src1[self.immTuple[0]] ]
        lane1 = [ src0[4 + self.immTuple[3]], src0[4 + self.immTuple[2]], src1[4 + self.immTuple[1]], src1[4 + self.immTuple[0]] ]
        return lane0 + lane1
    
    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        lane0 = [ s0ZMask[self.immTuple[3]], s0ZMask[self.immTuple[2]], s1ZMask[self.immTuple[1]], s1ZMask[self.immTuple[0]] ]
        lane1 = [ s0ZMask[4 + self.immTuple[3]], s0ZMask[4 + self.immTuple[2]], s1ZMask[4 + self.immTuple[1]], s1ZMask[4 + self.immTuple[0]] ]
        return lane0 + lane1
        
    def unparse(self, indent):
        return indent + "_mm256_shuffle_ps(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ", _MM_SHUFFLE" + str(self.immTuple) + ")" 

    def printInst(self, indent):
        return indent + "mm256ShufflePs( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + ", " + str(self.immTuple) + " )"

class mm256SetzeroPs(RValue):
    def __init__(self):
        super(mm256SetzeroPs, self).__init__()

    def computeSym(self, nameList):
        return [ sympify(0) ]*8
        
    def unparse(self, indent):
        return indent + "_mm256_setzero_ps()" 

    def printInst(self, indent):
        return indent + "mm256SetzeroPs()"

class _Dbl4Loader(Loader):
    def __init__(self):
        super(_Dbl4Loader, self).__init__()
    
    def loadMatrix(self, mParams):
        src, dst = mParams['m'], mParams['nuM']
        sL, sR = mParams['mL'], mParams['mR']
        dL, dR = mParams['nuML'], mParams['nuMR']
        M, N = mParams['M'], mParams['N']
        nuMM, nuMN = mParams['nuMM'], mParams['nuMN']
        isCompact = mParams['compact']
        mStruct, mAccess = mParams['struct'], mParams['access']
        instructions = []
        nu = 4
        
        instructions.append(Comment('AVX Loader:'))
        if Matrix.testGeneral(mStruct, mAccess, M, N):
#         if (len(mStruct) == 1 and Matrix in mStruct) or (M!=N):
            if M == 1 and N == 1:
                pc = Pointer(dst[dL.of(0),dR.of(0)])
    #             vmask = [1] + 7*[0]
                pa = AddressOf(sa(src[sL.of(0),sR.of(0)]))
                if mParams['bcast']:
                    va = mm256LoadGd(pa, [tuple(range(nu))])
                else:
                    va = mm256LoadGd(pa, [0])
                instr = mm256StoreGd(va, pc, range(nu))
                instructions += [ Comment(str(M) + "x" + str(N) + " -> " + str(nuMM) + "x" + str(nuMN)) ]
                instructions += [ instr ]
            elif (N == 1 and ((M <= nu and not isCompact) or (M < nu and isCompact))) or (M == 1 and N < nu):
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                horizontal = M==1
                pa = Pointer(src[sL.of(0),sR.of(0)])
                va = mm256LoadGd(pa, range(max(M,N)), isCompact=isCompact, horizontal=horizontal)
                instr = mm256StoreGd(va, pc, range(nu))
                instructions += [ Comment(str(M) + "x" + str(N) + " -> " + str(nuMM) + "x" + str(nuMN)) ]
                instructions += [ instr ]
            elif ((M < nu and N < nu) or (M == nu and N > 1 and N < nu) or (M > 1 and M < nu and N == nu)):
                pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(nu) ]
                pas = [ Pointer(src[sL.of(i),sR.of(0)]) for i in range(M) ]
                vas = [ mm256LoadGd(pas[i], range(N)) for i in range(M) ]
                instructions += [ Comment(str(M) + "x" + str(N) + " -> " + str(nuMM) + "x" + str(nuMN)) ]
                instructions += [ mm256StoreGd(vas[i], pcs[i], range(nu)) for i in range(M) ]
                instructions += [ mm256StoreGd(mm256SetzeroPd(), pcs[i], range(nu)) for i in range(M,nu) ]
        elif Symmetric.testLower(mStruct, mAccess, M, N):
#             elif M == N and mAccess.intersect(Map("{[i,j]->[i,j]}")) != mAccess: #mAccess != Map("{[i,j]->[i,j]}"):
#                 if mAccess == Map("{[i,j]->[i,j]: j<=i}").union(Map("{[i,j]->[j,i]: j>i}")):
                #LSymm
                vs = [mm256LoadGd(Pointer(src[sL.of(i),sR.of(0)]), range(i+1), isCompact) for i in range(0, M-1)]
                vs.append(mm256LoadGd(Pointer(src[sL.of(M-1),sR.of(0)]), range(M), isCompact))
                vs.extend([mm256SetzeroPd() for _ in range(M, 4)])
                if M == 1:
                    rows = vs
                elif M == 2:
                    rows = [ mm256ShufflePd(vs[0], vs[1], (0,0,0,0)) ]
                    rows.extend(vs[1:])
                elif M == 3:
                    r2to1 = mm256ShufflePd(vs[0], vs[1], (0,0,0,0))
                    r3to1 = mm256Permute2f128Pd(r2to1, vs[2], (0,0,1,0,0,0,0,0))
                    rows = [ mm256BlendPd(r3to1, vs[0], (1,0,0,0)) ]
                    r3to2 = mm256Permute2f128Pd(vs[1], vs[2], (0,0,1,0,0,0,0,0))
                    rows.append( mm256BlendPd(mm256PermutePd(r3to2, (0,1,1,0)), vs[0], (1,0,0,0)) )
                    rows.extend(vs[2:])
                else:
                    r2to1 = mm256ShufflePd(vs[0], vs[1], (0,0,0,0))
                    r3p4i = mm256ShufflePd(vs[2], vs[3], (0,0,0,0))
                    rows = [ mm256Permute2f128Pd(r2to1, r3p4i, (0,0,1,0,0,0,0,0)) ]
                    r3p4ii = mm256ShufflePd(vs[2], vs[3], (0,0,1,1))
                    rows.append( mm256Permute2f128Pd(vs[1], r3p4ii, (0,0,1,0,0,0,0,0)) )
                    rows.append( mm256BlendPd(vs[2], r3p4ii, (1,1,0,0)) )
                    rows.append( vs[3] )
                pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
                comm = Comment('%dx%d -> 4x4 - %s' % (M, N, 'LowSymm'))
                instrs = [mm256StoreGd(v, pc, [0, 1, 2, 3]) for v, pc in zip(rows, pcs)]
                instructions.extend([comm] + instrs)
        elif Symmetric.testUpper(mStruct, mAccess, M, N):
#                 elif mAccess == Map("{[i,j]->[j,i]: j<i}").union(Map("{[i,j]->[i,j]: j>=i}")):
                #USymm
                vs = [mm256LoadGd(Pointer(src[sL.of(i),sR.of(i)]), range(i,M), isCompact) for i in range(0, M-1)]
                vs.append(mm256LoadGd(Pointer(src[sL.of(M-1),sR.of(M-1)]), [M-1], isCompact))
                vs.extend([mm256SetzeroPd() for _ in range(M, 4)])
                if M == 1:
                    rows = vs
                elif M == 2:
                    rows = [ vs[0] ]
                    rows.append( mm256ShufflePd(vs[0], vs[1], (0,0,1,1)) )
                    rows.extend(vs[2:])
                elif M == 3:
                    rows = [ vs[0] ]
                    r1to2 = mm256ShufflePd(vs[0], vs[1], (0,0,1,1))
                    rows.append( mm256BlendPd(r1to2, vs[1], (1,1,0,0)) )
                    r1p2 = mm256ShufflePd(vs[0], vs[1], (0,0,0,0))
                    rows.append( mm256Permute2f128Pd(r1p2, vs[2], (0,0,1,1,0,0,0,1)) )
                    rows.append(vs[3])
                else:
                    rows = [ vs[0] ]
                    r1to2 = mm256ShufflePd(vs[0], vs[1], (0,0,1,1))
                    rows.append( mm256BlendPd(r1to2, vs[1], (1,1,0,0)) )
                    r1p2 = mm256ShufflePd(vs[0], vs[1], (0,0,0,0))
                    rows.append( mm256Permute2f128Pd(r1p2, vs[2], (0,0,1,1,0,0,0,1)) )
                    r1p2 = mm256ShufflePd(vs[0], vs[1], (1,1,0,0))
                    r3p4 = mm256ShufflePd(vs[2], vs[3], (1,1,0,0))
                    rows.append( mm256Permute2f128Pd(r1p2, r3p4, (0,0,1,1,0,0,0,1)) )
                pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
                comm = Comment('%dx%d -> 4x4 - %s' % (M, N, 'UpSymm'))
                instrs = [mm256StoreGd(v, pc, [0, 1, 2, 3]) for v, pc in zip(rows, pcs)]
                instructions.extend([comm] + instrs)
        elif LowerUnitTriangular.test(mStruct, mAccess, M, N):
            ones = mm256Set1Pd(V(1))
            lds = [ mm256SetzeroPd() ]
            lds.extend( [mm256LoadGd(Pointer(src[sL.of(i+1),sR.of(0)]), range(i+1), isCompact) for i in range(M-1)] )
            vs = []
            for i,v in enumerate(lds):
                imm = 4*[0]
                imm[3-i] = 1
                vs.append( mm256BlendPd(v, ones, imm) )
            vs.extend([mm256SetzeroPd() for _ in range(M, 4)])
            pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
            comm = Comment('%dx%d -> 4x4 - %s' % (M, N, 'LowUnitTriang'))
            instrs = [mm256StoreGd(v, pc, [0, 1, 2, 3]) for v, pc in zip(vs, pcs)]
            instructions.extend([comm] + instrs)
        elif LowerTriangular.test(mStruct, mAccess, M, N):
            vs = [mm256LoadGd(Pointer(src[sL.of(i),sR.of(0)]), range(i+1), isCompact) for i in range(M-1)]
            vs.append(mm256LoadGd(Pointer(src[sL.of(M-1),sR.of(0)]), range(M), isCompact))
            vs.extend([mm256SetzeroPd() for _ in range(M, 4)])
            pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
            comm = Comment('%dx%d -> 4x4 - %s' % (M, N, 'LowTriang'))
            instrs = [mm256StoreGd(v, pc, [0, 1, 2, 3]) for v, pc in zip(vs, pcs)]
            instructions.extend([comm] + instrs)
        elif UpperUnitTriangular.test(mStruct, mAccess, M, N):
            ones = mm256Set1Pd(V(1))
            lds = [mm256LoadGd(Pointer(src[sL.of(i),sR.of(i+1)]), range(i+1,M), isCompact) for i in range(M-1)]
            lds.append( mm256SetzeroPd() )
            vs = []
            for i,v in enumerate(lds):
                imm = 4*[0]
                imm[3-i] = 1
                vs.append( mm256BlendPd(v, ones, imm) )
            vs.extend([mm256SetzeroPd() for _ in range(M, 4)])
            pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
            comm = Comment('%dx%d -> 4x4 - %s' % (M, N, 'UpperUnitTriang'))
            instrs = [mm256StoreGd(v, pc, [0, 1, 2, 3]) for v, pc in zip(vs, pcs)]
            instructions.extend([comm] + instrs)
        elif UpperTriangular.test(mStruct, mAccess, M, N):
            vs = [mm256LoadGd(Pointer(src[sL.of(i),sR.of(i)]), range(i,M), isCompact) for i in range(M-1)]
            vs.append(mm256LoadGd(Pointer(src[sL.of(M-1),sR.of(M-1)]), [M-1], isCompact))
#                     vs = [mm256LoadGd(Pointer(src[sL.of(i),sR.of(0)]), range(i,M), isCompact) for i in range(M-1)]
#                     vs.append(mm256LoadGd(Pointer(src[sL.of(M-1),sR.of(0)]), [M-1], isCompact))
            vs.extend([mm256SetzeroPd() for _ in range(M, 4)])
            pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
            comm = Comment('%dx%d -> 4x4 - %s' % (M, N, 'UpperTriang'))
            instrs = [mm256StoreGd(v, pc, [0, 1, 2, 3]) for v, pc in zip(vs, pcs)]
            instructions.extend([comm] + instrs)
        elif AllEntriesConstantMatrix.test(mStruct, mAccess, M, N):
            const_value  = mStruct.keys()[0]._const_value
            if M == 1 and N == 1:
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                if mParams['bcast']:
                    va = mm256Set1Pd(V(const_value))
                else:
                    va = mm256SetPd(V(0), V(0), V(0), V(const_value))
                instr = mm256StoreGd(va, pc, range(nu))
                instructions += [ Comment("Constant " + str(M) + "x" + str(N) + " -> " + str(nuMM) + "x" + str(nuMN)) ]
                instructions += [ instr ]
            elif N == 1 or M == 1:
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                consts = [ V(0) for _ in range(nu-max(M,N)) ] + [V(const_value) for _ in range(max(M,N))]
                va = mm256SetPd(*consts)
                instr = mm256StoreGd(va, pc, range(nu))
                instructions += [ Comment("Constant " + str(M) + "x" + str(N) + " -> " + str(nuMM) + "x" + str(nuMN)) ]
                instructions += [ instr ]
            else:
                pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(nu) ]
                consts = [ V(0) for _ in range(nu-N) ] + [V(const_value) for _ in range(N)]
                va = mm256SetPd(*consts)
                vas = [ va for i in range(M) ]
                instructions += [ Comment("Constant " + str(M) + "x" + str(N) + " -> " + str(nuMM) + "x" + str(nuMN)) ]
                instructions += [ mm256StoreGd(vas[i], pcs[i], range(nu)) for i in range(M) ]
                instructions += [ mm256StoreGd(mm256SetzeroPd(), pcs[i], range(nu)) for i in range(M,nu) ]
        elif IdentityMatrix.test(mStruct, mAccess, M, N):
            ones = mm256Set1Pd(V(1))
            zeros = mm256SetzeroPd()
            vs = []
            for i in range(M):
                imm = 4*[0]
                imm[3-i] = 1
                vs.append( mm256BlendPd(zeros, ones, imm) )
            for i in range(M,4):
                vs.append( zeros )
            pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
            comm = Comment('%dx%d -> 4x4 - %s' % (M, N, 'Identity'))
            instrs = [mm256StoreGd(v, pc, [0, 1, 2, 3]) for v, pc in zip(vs, pcs)]
            instructions.extend([comm] + instrs)
                        
        return instructions

class _Dbl4BLAC(object):
    def __init__(self):
        super(_Dbl4BLAC, self).__init__()
    
    def Zero(self, dParams, opts):
        
        nu = 4
        dst = dParams['nuM']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        M, N     = dParams['nuMM'], dParams['nuMN']
        instructions = []

        instructions += [ Comment(str(nu) + "-BLAC: Zero " + str(M) + "x" + str(N)) ]
        if M*N == nu:
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            instr = mm256StoreGd(mm256SetzeroPd(), pc, range(nu))
            instructions += [ instr ]
        elif M == nu and N == nu:
            for i in range(M):
                pc = Pointer(dst[dL.of(i),dR.of(0)])
                instr = mm256StoreGd(mm256SetzeroPd(), pc, range(nu))
                instructions += [ instr ]
        
        return instructions

    def Copy(self, sParams, dParams, opts):
        
        nu = 4
        # these are the 3 Matrix objects involved
        src, dst = sParams['nuM'], dParams['nuM']
        # these are the index functions for the two dimensions of each of the matrices
        sL, sR = sParams['nuML'], sParams['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        # these are the sizes of the matrices
        M, N     = dParams['nuMM'], dParams['nuMN']
        instructions = []

        instructions += [ Comment(str(nu) + "-BLAC: Copy " + str(M) + "x" + str(N)) ]
        if M*N == nu:
            va = mm256LoadGd(Pointer(src[sL.of(0),sR.of(0)]), [0, 1, 2, 3])
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            instr = mm256StoreGd(va, pc, [0, 1, 2, 3])
            instructions.append(instr)
        elif M == nu and N == nu:
            vas = [mm256LoadGd(Pointer(src[sL.of(i),sR.of(0)]), [0, 1, 2, 3]) for i in range(4)]
            pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
            instrs = [mm256StoreGd(va, pc, [0, 1, 2, 3]) for va, pc in zip(vas, pcs)]
            instructions.extend(instrs)
        
        for i in instructions:
            i.bounds.update(dParams['bounds'])                
        return instructions
    
    def Add(self, s0Params, s1Params, dParams, opts):
        
        nu = 4
        src0, src1, dst = s0Params['nuM'], s1Params['nuM'], dParams['nuM']
        s0L, s0R = s0Params['nuML'], s0Params['nuMR']
        s1L, s1R = s1Params['nuML'], s1Params['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        M, N     = dParams['nuMM'], dParams['nuMN']
        instructions = []

        instructions += [ Comment(str(nu) + "-BLAC: " + str(M) + "x" + str(N) + " + " + str(M) + "x" + str(N)) ]
        if M*N == nu:
            va = mm256LoadGd(Pointer(src0[s0L.of(0),s0R.of(0)]), range(nu))
            vb = mm256LoadGd(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            instr = mm256StoreGd(mm256AddPd(va, vb), pc, range(nu))
            instructions += [ instr ]
        elif M == nu and N == nu:
            for i in range(M):
                va = mm256LoadGd(Pointer(src0[s0L.of(i),s0R.of(0)]), range(nu))
                vb = mm256LoadGd(Pointer(src1[s1L.of(i),s1R.of(0)]), range(nu))
                pc = Pointer(dst[dL.of(i),dR.of(0)])
                instr = mm256StoreGd(mm256AddPd(va, vb), pc, range(nu))
                instructions += [ instr ]
        
        return instructions

    def Neg(self, sParams, dParams, opts):
        
        nu = 4
        src, dst = sParams['nuM'], dParams['nuM']
        sL, sR = sParams['nuML'], sParams['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        M, N     = dParams['nuMM'], dParams['nuMN']
        instructions = []

        instructions += [ Comment(str(nu) + "-BLAC: -( " + str(M) + "x" + str(N) + " )") ]
        if M*N == nu:
            va = mm256LoadGd(Pointer(src[sL.of(0),sR.of(0)]), range(nu))
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            instr = mm256StoreGd(mm256SubPd(mm256SetzeroPd(), va), pc, range(nu))
            instructions += [ instr ]
        elif M == nu and N == nu:
            for i in range(M):
                va = mm256LoadGd(Pointer(src[sL.of(i),sR.of(0)]), range(nu))
                pc = Pointer(dst[dL.of(i),dR.of(0)])
                instr = mm256StoreGd(mm256SubPd(mm256SetzeroPd(), va), pc, range(nu))
                instructions += [ instr ]

        return instructions

    def Sub(self, s0Params, s1Params, dParams, opts):
        
        nu = 4
        src0, src1, dst = s0Params['nuM'], s1Params['nuM'], dParams['nuM']
        s0L, s0R = s0Params['nuML'], s0Params['nuMR']
        s1L, s1R = s1Params['nuML'], s1Params['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        M, N     = dParams['nuMM'], dParams['nuMN']
        instructions = []

        instructions += [ Comment(str(nu) + "-BLAC: " + str(M) + "x" + str(N) + " - " + str(M) + "x" + str(N)) ]
        if M*N == nu:
            va = mm256LoadGd(Pointer(src0[s0L.of(0),s0R.of(0)]), range(nu))
            vb = mm256LoadGd(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            instr = mm256StoreGd(mm256SubPd(va, vb), pc, range(nu))
            instructions += [ instr ]
        elif M == nu and N == nu:
            for i in range(M):
                va = mm256LoadGd(Pointer(src0[s0L.of(i),s0R.of(0)]), range(nu))
                vb = mm256LoadGd(Pointer(src1[s1L.of(i),s1R.of(0)]), range(nu))
                pc = Pointer(dst[dL.of(i),dR.of(0)])
                instr = mm256StoreGd(mm256SubPd(va, vb), pc, range(nu))
                instructions += [ instr ]
        
        return instructions

    def _Div(self, s0Params, s1Params, dParams, opts):
        
        nu = 4
        src0, src1, dst = s0Params['nuM'], s1Params['nuM'], dParams['nuM']
        s0L, s0R = s0Params['nuML'], s0Params['nuMR']
        s1L, s1R = s1Params['nuML'], s1Params['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        M, N     = dParams['nuMM'], dParams['nuMN']
        instructions = []

        instructions += [ Comment(str(nu) + "-BLAC: " + str(M) + "x" + str(N) + " / " + str(M) + "x" + str(N)) ]
        va = mm256LoadGd(Pointer(src0[s0L.of(0),s0R.of(0)]), range(nu))
        vb = mm256LoadGd(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
        pc = Pointer(dst[dL.of(0),dR.of(0)])
#         instr = mm256StoreGd(mm256DivPd(va, vb), pc, range(nu))
        instr = mm256StoreGd(mm256CastPd128Pd256(mmDivPd(mm256CastPd256Pd128(va), mm256CastPd256Pd128(vb))), pc, range(nu))
        instructions += [ instr ]
        
        return instructions

    def _Sqrt(self, sParams, dParams, opts):
        
        nu = 4
        src, dst = sParams['nuM'], dParams['nuM']
        sL, sR = sParams['nuML'], sParams['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        M, N     = dParams['nuMM'], dParams['nuMN']
        instructions = []

        instructions += [ Comment(str(nu) + "-BLAC: sqrt(" + str(M) + "x" + str(N) + ")") ]
        va = mm256LoadGd(Pointer(src[sL.of(0),sR.of(0)]), range(nu))
        pc = Pointer(dst[dL.of(0),dR.of(0)])
#         instr = mm256StoreGd(mm256SqrtPd(va), pc, range(nu))
        instr = mm256StoreGd(mm256CastPd128Pd256(mmSqrtPd(mm256CastPd256Pd128(va))), pc, range(nu))
        instructions += [ instr ]
        
        return instructions

#     def LDiv(self, s0Params, s1Params, dParams, opts):
#         nu = 4
#         src0, src1, dst = s0Params['nuM'], s1Params['nuM'], dParams['nuM']
#         s0L, s0R = s0Params['nuML'], s0Params['nuMR']
#         s1L, s1R = s1Params['nuML'], s1Params['nuMR']
#         dL, dR   = dParams['nuML'], dParams['nuMR']
#         oN, M, N = s1Params['N'], s0Params['nuMM'], s1Params['nuMN']
#         s0Struct = s0Params['struct']
#         instructions = []
# 
#         instructions += [ Comment(str(nu) + "-BLAC: " + str(M) + "x" + str(M) + " \ " + str(M) + "x" + str(N)) ]
#         if M == 1:
#             va0 = mm256LoadGd(Pointer(src0[s0L.of(0),s0R.of(0)]), range(nu))
#             if oN > 1:
#                 dupa00 = mm256UnpackloPd(va0, va0)
#                 va0 = mm256Permute2f128Pd(dupa00, dupa00, [0,0,1,0,0,0,0,0])
#             vb = mm256LoadGd(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
#             pc = Pointer(dst[dL.of(0),dR.of(0)])
#             instructions += [ mm256StoreGd(mm256DivPd(vb, va0), pc, range(nu)) ]
#         else:
#             if s0Struct[Matrix] == Set("{[i,j]: 0<=i<"+str(M)+" and 0<=j<=i}") and s0Struct[ZeroMatrix] == Set("{[i,j]: 0<=i<"+str(M)+" and i<j<"+str(M)+"}"):
#                 if N == 1: #trsv forward-sub
#                     va0 = mm256LoadGd(Pointer(src0[s0L.of(0),s0R.of(0)]), range(nu))
#                     va1 = mm256LoadGd(Pointer(src0[s0L.of(1),s0R.of(0)]), range(nu))
#                     va2 = mm256LoadGd(Pointer(src0[s0L.of(2),s0R.of(0)]), range(nu))
#                     va3 = mm256LoadGd(Pointer(src0[s0L.of(3),s0R.of(0)]), range(nu))
#                     pc = Pointer(dst[dL.of(0),dR.of(0)])
#                     tmp0 = mm256UnpackloPd(va0, va1)
#                     tmp1 = mm256UnpackloPd(va2, va3)
#                     tmp2 = mm256UnpackhiPd(va0, va1)
#                     tmp3 = mm256UnpackhiPd(va2, va3)
#                     col0 = mm256BlendPd(mm256Permute2f128Pd(tmp0, tmp1, [0,0,1,0,0,0,0,0]), mm256SetzeroPd(), [0,0,0,1])
#                     col1 = mm256BlendPd(mm256Permute2f128Pd(tmp2, tmp3, [0,0,1,0,0,0,0,0]), mm256SetzeroPd(), [0,0,1,0])
#                     col2 = mm256BlendPd(mm256Permute2f128Pd(tmp0, tmp1, [0,0,1,1,0,0,0,1]), mm256SetzeroPd(), [0,1,0,0])
#                     vb = mm256LoadGd(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
#                     d01 = mm256BlendPd(va0, va1, [0,0,1,0])
#                     d23 = mm256BlendPd(va2, va3, [1,0,0,0])
#                     diag = mm256BlendPd(d01, d23, [1,1,0,0])
#                     ones = mm256Set1Pd(sa(1.))
#                     rdiag = mm256DivPd(ones, diag)
#                     sol = mm256MulPd(rdiag, vb)
#                     instructions += [ mm256StoreGd(sol, pc, range(nu)) ]
#                     dupx0 = mm256UnpackloPd(mm256LoadGd(pc, range(4)), mm256LoadGd(pc, range(4)))
#                     dupLane = mm256Permute2f128Pd(dupx0, dupx0, [0,0,1,0,0,0,0,0]) # Dup first lane
#                     cx0 = mm256MulPd(rdiag, mm256MulPd(col0, dupLane))
#                     sol = mm256SubPd(mm256LoadGd(pc, range(nu)), cx0)
#                     instructions += [ mm256StoreGd(sol, pc, range(nu)) ]
#                     dupx1 = mm256UnpackhiPd(mm256LoadGd(pc, range(4)), mm256LoadGd(pc, range(4)))
#                     dupLane = mm256Permute2f128Pd(dupx1, dupx1, [0,0,1,0,0,0,0,0]) # Dup first lane
#                     cx1 = mm256MulPd(rdiag, mm256MulPd(col1, dupLane))
#                     sol = mm256SubPd(mm256LoadGd(pc, range(nu)), cx1)
#                     instructions += [ mm256StoreGd(sol, pc, range(nu)) ]
#                     dupx2 = mm256UnpackloPd(mm256LoadGd(pc, range(4)), mm256LoadGd(pc, range(4)))
#                     dupLane = mm256Permute2f128Pd(dupx2, dupx2, [0,0,1,1,0,0,0,1]) # Dup second lane
#                     cx2 = mm256MulPd(rdiag, mm256MulPd(col2, dupLane))
#                     sol = mm256SubPd(mm256LoadGd(pc, range(nu)), cx2)
#                     instructions += [ mm256StoreGd(sol, pc, range(nu)) ]
#                 else: #trsm
#                     vas = [ mm256LoadGd(Pointer(src0[s0L.of(i),s0R.of(0)]), range(nu)) for i in range(nu)]
#                     ones = mm256Set1Pd(sa(1.))
#                     ums = [ (mm256UnpackloPd,[0,0,1,0,0,0,0,0]), (mm256UnpackhiPd,[0,0,1,0,0,0,0,0]), (mm256UnpackloPd,[0,0,1,1,0,0,0,1]), (mm256UnpackhiPd,[0,0,1,1,0,0,0,1]) ]
#                     rdiags = [ ]
#                     for i in range(nu):
#                         upack, mask = ums[i]
#                         dupaii = upack(vas[i], vas[i])
#                         bcaii = mm256Permute2f128Pd(dupaii, dupaii, mask)
#                         rdiags.append(mm256DivPd(ones, bcaii))
#                     vbs = [ mm256LoadGd(Pointer(src1[s1L.of(i),s1R.of(0)]), range(nu)) for i in range(nu)]
#                     pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(nu)]
#                     #Solve X00, X01, X02, X03
#         #             dupa00 = mm256UnpackloPd(vas[0], vas[0])
#         #             sol = mm256DivPd(vbs[0], mm256Permute2f128Pd(dupa00, dupa00, [0,0,1,0,0,0,0,0]))
#                     sol = mm256MulPd(rdiags[0], vbs[0])
#                     instructions += [ mm256StoreGd(sol, pcs[0], range(nu)) ]
#                     #Solve X10, X11, X12, X13
#                     #bcast L10
#                     dupa10 = mm256UnpackloPd(vas[1], vas[1])
#                     bca10 = mm256Permute2f128Pd(dupa10, dupa10, [0,0,1,0,0,0,0,0])
#                     x0 = mm256LoadGd(pcs[0], range(nu))
#                     sol = mm256MulPd(rdiags[1], mm256SubPd(vbs[1], mm256MulPd(bca10, x0)))
#                     instructions += [ mm256StoreGd(sol, pcs[1], range(nu)) ]
#                     #Solve X2..
#                     #bcast L20, L21
#                     dupa20 = mm256UnpackloPd(vas[2], vas[2])
#                     bca20 = mm256Permute2f128Pd(dupa20, dupa20, [0,0,1,0,0,0,0,0])
#                     dupa21 = mm256UnpackhiPd(vas[2], vas[2])
#                     bca21 = mm256Permute2f128Pd(dupa21, dupa21, [0,0,1,0,0,0,0,0])
#                     x1 = mm256LoadGd(pcs[1], range(nu))
#                     sol = mm256MulPd(rdiags[2], mm256SubPd(mm256SubPd(vbs[2], mm256MulPd(bca20, x0)), mm256MulPd(bca21, x1)))
#                     instructions += [ mm256StoreGd(sol, pcs[2], range(nu)) ]
#                     #Solve X3..
#                     #bcast L30, L31, L32
#                     dupa30 = mm256UnpackloPd(vas[3], vas[3])
#                     bca30 = mm256Permute2f128Pd(dupa30, dupa30, [0,0,1,0,0,0,0,0])
#                     dupa31 = mm256UnpackhiPd(vas[3], vas[3])
#                     bca31 = mm256Permute2f128Pd(dupa31, dupa31, [0,0,1,0,0,0,0,0])
#                     dupa32 = dupa30
#                     bca32 = mm256Permute2f128Pd(dupa32, dupa32, [0,0,1,1,0,0,0,1])
#                     x2 = mm256LoadGd(pcs[2], range(nu))
#                     sol = mm256MulPd(rdiags[3], mm256SubPd(mm256SubPd(mm256SubPd(vbs[3], mm256MulPd(bca30, x0)), mm256MulPd(bca31, x1)), mm256MulPd(bca32, x2)))
#                     instructions += [ mm256StoreGd(sol, pcs[3], range(nu)) ]
#             else: 
#                 if N == 1: #trsv backward-sub
#                     va0 = mm256LoadGd(Pointer(src0[s0L.of(0),s0R.of(0)]), range(nu))
#                     va1 = mm256LoadGd(Pointer(src0[s0L.of(1),s0R.of(0)]), range(nu))
#                     va2 = mm256LoadGd(Pointer(src0[s0L.of(2),s0R.of(0)]), range(nu))
#                     va3 = mm256LoadGd(Pointer(src0[s0L.of(3),s0R.of(0)]), range(nu))
#                     pc = Pointer(dst[dL.of(0),dR.of(0)])
#                     tmp0 = mm256UnpackloPd(va0, va1)
#                     tmp1 = mm256UnpackloPd(va2, va3)
#                     tmp2 = mm256UnpackhiPd(va0, va1)
#                     tmp3 = mm256UnpackhiPd(va2, va3)
#                     col1 = mm256BlendPd(mm256Permute2f128Pd(tmp2, tmp3, [0,0,1,0,0,0,0,0]), mm256SetzeroPd(), [0,0,1,0])
#                     col2 = mm256BlendPd(mm256Permute2f128Pd(tmp0, tmp1, [0,0,1,1,0,0,0,1]), mm256SetzeroPd(), [0,1,0,0])
#                     col3 = mm256BlendPd(mm256Permute2f128Pd(tmp2, tmp3, [0,0,1,1,0,0,0,1]), mm256SetzeroPd(), [1,0,0,0])
#                     vb = mm256LoadGd(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
#                     d01 = mm256BlendPd(va0, va1, [0,0,1,0])
#                     d23 = mm256BlendPd(va2, va3, [1,0,0,0])
#                     diag = mm256BlendPd(d01, d23, [1,1,0,0])
#                     ones = mm256Set1Pd(sa(1.))
#                     rdiag = mm256DivPd(ones, diag)
#                     sol = mm256MulPd(rdiag, vb)
#                     instructions += [ mm256StoreGd(sol, pc, range(nu)) ]
#                     dupx3 = mm256UnpackhiPd(mm256LoadGd(pc, range(4)), mm256LoadGd(pc, range(4)))
#                     dupLane = mm256Permute2f128Pd(dupx3, dupx3, [0,0,1,1,0,0,0,1]) # Dup second lane: x3 x3 x3 x3
#                     cx3 = mm256MulPd(rdiag, mm256MulPd(col3, dupLane))
#                     sol = mm256SubPd(mm256LoadGd(pc, range(nu)), cx3)
#                     instructions += [ mm256StoreGd(sol, pc, range(nu)) ]
#                     dupx2 = mm256UnpackloPd(mm256LoadGd(pc, range(4)), mm256LoadGd(pc, range(4)))
#                     dupLane = mm256Permute2f128Pd(dupx2, dupx2, [0,0,1,1,0,0,0,1]) # Dup second lane
#                     cx2 = mm256MulPd(rdiag, mm256MulPd(col2, dupLane))
#                     sol = mm256SubPd(mm256LoadGd(pc, range(nu)), cx2)
#                     instructions += [ mm256StoreGd(sol, pc, range(nu)) ]
#                     dupx1 = mm256UnpackhiPd(mm256LoadGd(pc, range(4)), mm256LoadGd(pc, range(4)))
#                     dupLane = mm256Permute2f128Pd(dupx1, dupx1, [0,0,1,0,0,0,0,0]) # Dup first lane
#                     cx1 = mm256MulPd(rdiag, mm256MulPd(col1, dupLane))
#                     sol = mm256SubPd(mm256LoadGd(pc, range(nu)), cx1)
#                     instructions += [ mm256StoreGd(sol, pc, range(nu)) ]
#                 else: #trsm
#                     vas = [ mm256LoadGd(Pointer(src0[s0L.of(i),s0R.of(0)]), range(nu)) for i in range(nu)]
#                     ones = mm256Set1Pd(sa(1.))
#                     ums = [ (mm256UnpackloPd,[0,0,1,0,0,0,0,0]), (mm256UnpackhiPd,[0,0,1,0,0,0,0,0]), (mm256UnpackloPd,[0,0,1,1,0,0,0,1]), (mm256UnpackhiPd,[0,0,1,1,0,0,0,1]) ]
#                     rdiags = [ ]
#                     for i in range(nu):
#                         upack, mask = ums[i]
#                         dupaii = upack(vas[i], vas[i])
#                         bcaii = mm256Permute2f128Pd(dupaii, dupaii, mask)
#                         rdiags.append(mm256DivPd(ones, bcaii))
#                     vbs = [ mm256LoadGd(Pointer(src1[s1L.of(i),s1R.of(0)]), range(nu)) for i in range(nu)]
#                     pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(nu)]
#                     #Solve X30, X31, X32, X33
#                     sol = mm256MulPd(rdiags[3], vbs[3])
#                     instructions += [ mm256StoreGd(sol, pcs[3], range(nu)) ]
#                     #Solve X20, X21, X22, X23
#                     #bcast U23
#                     dupa23 = mm256UnpackhiPd(vas[2], vas[2])
#                     bca23 = mm256Permute2f128Pd(dupa23, dupa23, [0,0,1,1,0,0,0,1])
#                     x3 = mm256LoadGd(pcs[3], range(nu))
#                     sol = mm256MulPd(rdiags[2], mm256SubPd(vbs[2], mm256MulPd(bca23, x3)))
#                     instructions += [ mm256StoreGd(sol, pcs[2], range(nu)) ]
#                     #Solve X1..
#                     #bcast U12, U13
#                     dupa12 = mm256UnpackloPd(vas[1], vas[1])
#                     bca12 = mm256Permute2f128Pd(dupa12, dupa12, [0,0,1,1,0,0,0,1])
#                     dupa13 = mm256UnpackhiPd(vas[1], vas[1])
#                     bca13 = mm256Permute2f128Pd(dupa13, dupa13, [0,0,1,1,0,0,0,1])
#                     x2 = mm256LoadGd(pcs[2], range(nu))
#                     sol = mm256MulPd(rdiags[1], mm256SubPd(mm256SubPd(vbs[1], mm256MulPd(bca12, x2)), mm256MulPd(bca13, x3)))
#                     instructions += [ mm256StoreGd(sol, pcs[1], range(nu)) ]
#                     #Solve X0..
#                     #bcast U01, U02, U03
#                     dupa01 = mm256UnpackhiPd(vas[0], vas[0])
#                     bca01 = mm256Permute2f128Pd(dupa01, dupa01, [0,0,1,0,0,0,0,0])
#                     dupa02 = mm256UnpackloPd(vas[0], vas[0])
#                     bca02 = mm256Permute2f128Pd(dupa02, dupa02, [0,0,1,1,0,0,0,1])
#                     dupa03 = dupa01
#                     bca03 = mm256Permute2f128Pd(dupa03, dupa03, [0,0,1,1,0,0,0,1])
#                     x1 = mm256LoadGd(pcs[1], range(nu))
#                     sol = mm256MulPd(rdiags[0], mm256SubPd(mm256SubPd(mm256SubPd(vbs[0], mm256MulPd(bca01, x1)), mm256MulPd(bca02, x2)), mm256MulPd(bca03, x3)))
#                     instructions += [ mm256StoreGd(sol, pcs[0], range(nu)) ]
# 
#         return instructions
        
    def Mul(self, s0Params, s1Params, dParams, opts):

        nu = 4
        src0, src1, dst = s0Params['nuM'], s1Params['nuM'], dParams['nuM']
        s0L, s0R = s0Params['nuML'], s0Params['nuMR']
        s1L, s1R = s1Params['nuML'], s1Params['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        M, K, N = s0Params['nuMM'], s0Params['nuMN'], s1Params['nuMN']
        instructions = []

        instructions += [ Comment(str(nu) + "-BLAC: " + str(M) + "x" + str(K) + " * " + str(K) + "x" + str(N)) ]
        if M == 1:
            if N == 1:
                va = mm256LoadGd(Pointer(src0[s0L.of(0),s0R.of(0)]), range(nu))
                vb = mm256LoadGd(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                vmul = mm256MulPd(va, vb)
                vper = mm256Permute2f128Pd(vmul, vmul, [1,0,0,0,0,0,0,1])
                vadd0 = mm256AddPd(vmul, vper)
                vble = mm256BlendPd(vadd0, mm256SetzeroPd(), [1,1,1,0])
                vshu = mm256ShufflePd(vadd0, vadd0, [0,0,0,1])
                vadd1 = mm256AddPd(vble, vshu)
                instr = mm256StoreGd(vadd1, pc, range(nu))
                instructions += [ instr ]
            else:
                vb0 = mm256LoadGd(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
                vb1 = mm256LoadGd(Pointer(src1[s1L.of(1),s1R.of(0)]), range(nu))
                vb2 = mm256LoadGd(Pointer(src1[s1L.of(2),s1R.of(0)]), range(nu))
                vb3 = mm256LoadGd(Pointer(src1[s1L.of(3),s1R.of(0)]), range(nu))

                va00 = mm256LoadGd(Pointer(src0[s0L.of(0),s0R.of(0)]), [tuple(range(nu))])
                va01 = mm256LoadGd(Pointer(src0[s0L.of(0),s0R.of(1)]), [tuple(range(nu))])
                va02 = mm256LoadGd(Pointer(src0[s0L.of(0),s0R.of(2)]), [tuple(range(nu))])
                va03 = mm256LoadGd(Pointer(src0[s0L.of(0),s0R.of(3)]), [tuple(range(nu))])
                mul0 = mm256MulPd(va00, vb0)
                mul1 = mm256MulPd(va01, vb1)
                add0 = mm256AddPd(mul0, mul1)
                mul2 = mm256MulPd(va02, vb2)
                mul3 = mm256MulPd(va03, vb3)
                add1 = mm256AddPd(mul2, mul3)
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = mm256StoreGd(mm256AddPd(add0, add1), pc, range(nu))
                instructions += [ instr ]
        else:
            if K == 1:
                va0 = mm256LoadGd(Pointer(src0[s0L.of(0),s0R.of(0)]), [tuple(range(nu))])
                va1 = mm256LoadGd(Pointer(src0[s0L.of(1),s0R.of(0)]), [tuple(range(nu))])
                va2 = mm256LoadGd(Pointer(src0[s0L.of(2),s0R.of(0)]), [tuple(range(nu))])
                va3 = mm256LoadGd(Pointer(src0[s0L.of(3),s0R.of(0)]), [tuple(range(nu))])
                vb = mm256LoadGd(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
                pc0 = Pointer(dst[dL.of(0),dR.of(0)])
                pc1 = Pointer(dst[dL.of(1),dR.of(0)])
                pc2 = Pointer(dst[dL.of(2),dR.of(0)])
                pc3 = Pointer(dst[dL.of(3),dR.of(0)])
                instr0 = mm256StoreGd(mm256MulPd(va0, vb), pc0, range(nu))
                instr1 = mm256StoreGd(mm256MulPd(va1, vb), pc1, range(nu))
                instr2 = mm256StoreGd(mm256MulPd(va2, vb), pc2, range(nu))
                instr3 = mm256StoreGd(mm256MulPd(va3, vb), pc3, range(nu))
                instructions += [ instr0, instr1, instr2, instr3 ]
            else:
                if N == 1:
                    va0 = mm256LoadGd(Pointer(src0[s0L.of(0),s0R.of(0)]), range(nu))
                    va1 = mm256LoadGd(Pointer(src0[s0L.of(1),s0R.of(0)]), range(nu))
                    va2 = mm256LoadGd(Pointer(src0[s0L.of(2),s0R.of(0)]), range(nu))
                    va3 = mm256LoadGd(Pointer(src0[s0L.of(3),s0R.of(0)]), range(nu))
                    vb = mm256LoadGd(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
                    mul0 = mm256MulPd(va0, vb)
                    mul1 = mm256MulPd(va1, vb)
                    mul2 = mm256MulPd(va2, vb)
                    mul3 = mm256MulPd(va3, vb)
                    hadd0 = mm256HaddPd(mul0, mul1)
                    hadd1 = mm256HaddPd(mul2, mul3)
                    vper = mm256Permute2f128Pd(hadd0, hadd1, [0,0,1,0,0,0,0,1])
                    vble = mm256BlendPd(hadd0, hadd1, [1,1,0,0])
                    pc = Pointer(dst[dL.of(0),dR.of(0)])
                    instr = mm256StoreGd(mm256AddPd(vper, vble), pc, range(nu))
                    instructions += [ instr ]
                else:
                    vb0 = mm256LoadGd(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
                    vb1 = mm256LoadGd(Pointer(src1[s1L.of(1),s1R.of(0)]), range(nu))
                    vb2 = mm256LoadGd(Pointer(src1[s1L.of(2),s1R.of(0)]), range(nu))
                    vb3 = mm256LoadGd(Pointer(src1[s1L.of(3),s1R.of(0)]), range(nu))
                    for i in range(nu):
                        vai0 = mm256LoadGd(Pointer(src0[s0L.of(i),s0R.of(0)]), [tuple(range(nu))])
                        vai1 = mm256LoadGd(Pointer(src0[s0L.of(i),s0R.of(1)]), [tuple(range(nu))])
                        vai2 = mm256LoadGd(Pointer(src0[s0L.of(i),s0R.of(2)]), [tuple(range(nu))])
                        vai3 = mm256LoadGd(Pointer(src0[s0L.of(i),s0R.of(3)]), [tuple(range(nu))])
                        mul0 = mm256MulPd(vai0, vb0)
                        mul1 = mm256MulPd(vai1, vb1)
                        add0 = mm256AddPd(mul0, mul1)
                        mul2 = mm256MulPd(vai2, vb2)
                        mul3 = mm256MulPd(vai3, vb3)
                        add1 = mm256AddPd(mul2, mul3)
                        pc = Pointer(dst[dL.of(i),dR.of(0)])
                        instr = mm256StoreGd(mm256AddPd(add0, add1), pc, range(nu))
                        instructions += [ instr ]

        return instructions

    def Kro(self, s0Params, s1Params, dParams, opts):

        nu = 4
        src0, src1, dst = s0Params['nuM'], s1Params['nuM'], dParams['nuM']
        s0L, s0R = s0Params['nuML'], s0Params['nuMR']
        s1L, s1R = s1Params['nuML'], s1Params['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        oM, oK, oN, oP = s0Params['M'], s0Params['N'], s1Params['M'], s1Params['N']
        M, K, N, P = s0Params['nuMM'], s0Params['nuMN'], s1Params['nuMM'], s1Params['nuMN']
        instructions = []
        
        instructions += [ Comment(str(nu) + "-BLAC: " + str(M) + "x" + str(K) + " Kro " + str(N) + "x" + str(P)) ]
        if oM*oK*oN*oP == 1:
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            va = mm256LoadGd(Pointer(src0[s0L.of(0),s0R.of(0)]), range(nu))
            vb = mm256LoadGd(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
            instr = mm256StoreGd(mm256MulPd(va, vb), pc, range(nu))
            instructions += [ instr ]
        elif oM*oK == 1:
            if s0Params['bcast']:
                dup = mm256LoadGd(Pointer(src0[s0L.of(0),s0R.of(0)]), range(nu))
            else:
                va = mm256LoadGd(Pointer(src0[s0L.of(0),s0R.of(0)]), range(nu))
                repva = mm256Permute2f128Pd(va, va, [0,0,0,0,0,0,0,0]) #Need to replicate on the 2nd lane
                dup = mm256ShufflePd(repva, repva, (0,0,0,0))
                
            if N*P == nu:
                vb = mm256LoadGd(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = mm256StoreGd(mm256MulPd(dup, vb), pc, range(nu))
                instructions += [ instr ]
            else:
#                 va = mm256LoadGd(Pointer(src0[s0L.of(0),s0R.of(0)]), range(nu))
#                 repva = mm256Permute2f128Pd(va, va, [0,0,0,0,0,0,0,0]) #Need to replicate on the 2nd lane
#                 dup = mm256ShufflePd(repva, repva, (0,0,0,0))
                for i in range(nu):
                    vb = mm256LoadGd(Pointer(src1[s1L.of(i),s1R.of(0)]), range(nu))
                    pc = Pointer(dst[dL.of(i),dR.of(0)])
                    instr = mm256StoreGd(mm256MulPd(dup, vb), pc, range(nu))
                    instructions += [ instr ]
        else:
            if s1Params['bcast']:
                dup = mm256LoadGd(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
            else:
                vb = mm256LoadGd(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
                repvb = mm256Permute2f128Pd(vb, vb, [0,0,0,0,0,0,0,0]) #Need to replicate on the 2nd lane
                dup = mm256ShufflePd(repvb, repvb, (0,0,0,0))
            
            if M*K == nu:
                va = mm256LoadGd(Pointer(src0[s0L.of(0),s0R.of(0)]), range(nu))
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = mm256StoreGd(mm256MulPd(va, dup), pc, range(nu))
                instructions += [ instr ]
            else:
#                 vb = mm256LoadGd(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
#                 repvb = mm256Permute2f128Pd(vb, vb, [0,0,0,0,0,0,0,0]) #Need to replicate on the 2nd lane
#                 dup = mm256ShufflePd(repvb, repvb, (0,0,0,0))
                for i in range(nu):
                    va = mm256LoadGd(Pointer(src0[s0L.of(i),s0R.of(0)]), range(nu))
                    pc = Pointer(dst[dL.of(i),dR.of(0)])
                    instr = mm256StoreGd(mm256MulPd(va, dup), pc, range(nu))
                    instructions += [ instr ]
        
        return instructions

    def T(self, sParams, dParams, opts):

        nu = 4
        src, dst = sParams['nuM'], dParams['nuM']
        sL, sR = sParams['nuML'], sParams['nuMR']
        dL, dR = dParams['nuML'], dParams['nuMR']
        M, N = dParams['nuMM'], dParams['nuMN']
        instructions = []

        instructions += [ Comment(str(nu) + "-BLAC: (" + str(N) + "x" + str(M) + ")^T") ]
        if M*N == nu:
            va = mm256LoadGd(Pointer(src[sL.of(0),sR.of(0)]), range(nu))
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            instr = mm256StoreGd(va, pc, range(nu))
            instructions += [ instr ]
        else:
            va0 = mm256LoadGd(Pointer(src[sL.of(0),sR.of(0)]), range(nu))
            va1 = mm256LoadGd(Pointer(src[sL.of(1),sR.of(0)]), range(nu))
            va2 = mm256LoadGd(Pointer(src[sL.of(2),sR.of(0)]), range(nu))
            va3 = mm256LoadGd(Pointer(src[sL.of(3),sR.of(0)]), range(nu))

            tmp0 = mm256UnpackloPd(va0, va1)
            tmp1 = mm256UnpackloPd(va2, va3)
            tmp2 = mm256UnpackhiPd(va0, va1)
            tmp3 = mm256UnpackhiPd(va2, va3)
            col0 = mm256Permute2f128Pd(tmp0, tmp1, [0,0,1,0,0,0,0,0])
            col1 = mm256Permute2f128Pd(tmp2, tmp3, [0,0,1,0,0,0,0,0])
            col2 = mm256Permute2f128Pd(tmp0, tmp1, [0,0,1,1,0,0,0,1])
            col3 = mm256Permute2f128Pd(tmp2, tmp3, [0,0,1,1,0,0,0,1])

            pc0 = Pointer(dst[dL.of(0),dR.of(0)])
            pc1 = Pointer(dst[dL.of(1),dR.of(0)])
            pc2 = Pointer(dst[dL.of(2),dR.of(0)])
            pc3 = Pointer(dst[dL.of(3),dR.of(0)])
            instr0 = mm256StoreGd(col0, pc0, range(nu))
            instr1 = mm256StoreGd(col1, pc1, range(nu))
            instr2 = mm256StoreGd(col2, pc2, range(nu))
            instr3 = mm256StoreGd(col3, pc3, range(nu))
            instructions += [ instr0, instr1, instr2, instr3 ]
        
        return instructions

class _Dbl4Storer(Storer):
    def __init__(self):
        super(_Dbl4Storer, self).__init__()

    def storeMatrix(self, mParams):
        src, dst = mParams['nuM'], mParams['m']
        sL, sR = mParams['nuML'], mParams['nuMR']
        dL, dR = mParams['mL'], mParams['mR']
        M, N = mParams['M'], mParams['N']
        isCompact = mParams['compact']
        mStruct, mAccess = mParams['struct'], mParams['access']
        instructions = []
        nu = 4

        instructions.append(Comment('AVX Storer:'))
        if Matrix.testGeneral(mStruct, mAccess, M, N):        
            if M == 1 and N == 1:
                pc = AddressOf(sa(dst[dL.of(0),dR.of(0)]))
                va = mm256LoadGd(Pointer(src[sL.of(0),sR.of(0)]), range(nu))
                instr = mm256StoreGd(va, pc,[0])
                instructions += [ instr ]
            elif (N == 1 and ((M <= nu and not isCompact) or (M < nu and isCompact))) or (M == 1 and N < nu):
                va = mm256LoadGd(Pointer(src[sL.of(0),sR.of(0)]), range(nu))
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                horizontal = M==1
                instr = mm256StoreGd(va, pc, range(max(M,N)), isCompact=isCompact, horizontal=horizontal)            
                instructions += [ instr ]
            elif mAccess.intersect(Map("{[i,j]->[i,j]}")) == mAccess and ((M < nu and N < nu) or (M == nu and N > 1 and N < nu) or (M > 1 and M < nu and N == nu)):
                pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(M) ]
                vas = [ mm256LoadGd(Pointer(src[sL.of(i),sR.of(0)]), range(nu)) for i in range(M) ]
                instrs = [ mm256StoreGd(vas[i], pcs[i], range(N)) for i in range(M) ]
                instructions += instrs
        elif Symmetric.testLower(mStruct, mAccess, M, N):
#             elif M == N and mAccess.intersect(Map("{[i,j]->[i,j]}")) != mAccess:
#                 if mAccess == Map("{[i,j]->[i,j]: j<=i}").union(Map("{[i,j]->[j,i]: j>i}")):
                #LSymm
            nuvs = [mm256LoadGd(Pointer(src[sL.of(i),sR.of(0)]), [0, 1, 2, 3], isCompact, zeromask=range(i+1, 4)) for i in range(M)]
            pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(M)]
            comm = Comment("4x4 -> %dx%d - %s" % (M, N, 'LowSymm'))
            instrs = [mm256StoreGd(nuvs[i], pcs[i], range(i+1), isCompact) for i in range(M)]
            instructions.extend([comm] + instrs)
        elif Symmetric.testUpper(mStruct, mAccess, M, N):
#                 elif mAccess == Map("{[i,j]->[j,i]: j<i}").union(Map("{[i,j]->[i,j]: j>=i}")):
                #USymm
            nuvs = [mm256LoadGd(Pointer(src[sL.of(i),sR.of(0)]), [0, 1, 2, 3], isCompact, zeromask=range(0, i)) for i in range(M)]
            pcs = [Pointer(dst[dL.of(i),dR.of(i)]) for i in range(M)]
            comm = Comment("4x4 -> %dx%d - %s" % (M, N, 'UpSymm'))
            instrs = [mm256StoreGd(nuvs[i], pcs[i], range(i,M), isCompact) for i in range(M)]
            instructions.extend([comm] + instrs)
#        elif len(mStruct) == 2:
#             if Matrix in mStruct and ZeroMatrix in mStruct and M==N:
#                 if mStruct[Matrix] == Set("{[i,j]: 0<=i<"+str(M)+" and 0<=j<=i}") and mStruct[ZeroMatrix] == Set("{[i,j]: 0<=i<"+str(M)+" and i<j<"+str(M)+"}"):
        elif LowerTriangular.test(mStruct, mAccess, M, N):
            #LowerTriang 
            nuvs = [mm256LoadGd(Pointer(src[sL.of(i),sR.of(0)]), [0, 1, 2, 3], isCompact, zeromask=range(i+1, 4)) for i in range(M)]
            pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(M)]
            comm = Comment("4x4 -> %dx%d - %s" % (M, N, 'LowTriang'))
            instrs = [mm256StoreGd(nuvs[i], pcs[i], range(i+1), isCompact) for i in range(M)]
            instructions.extend([comm] + instrs)
        elif UpperTriangular.test(mStruct, mAccess, M, N):
#                 elif mStruct[Matrix] == Set("{[i,j]: 0<=i<"+str(M)+" and i<=j<"+str(M)+"}") and mStruct[ZeroMatrix] == Set("{[i,j]: 0<=i<"+str(M)+" and 0<=j<i}"):
            #UpperTriang 
            nuvs = [mm256LoadGd(Pointer(src[sL.of(i),sR.of(0)]), [0, 1, 2, 3], isCompact, zeromask=range(0, i)) for i in range(M)]
            pcs = [Pointer(dst[dL.of(i),dR.of(i)]) for i in range(M)]
#                     pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(M)]
            comm = Comment("4x4 -> %dx%d - %s" % (M, N, 'UpTriang'))
            instrs = [mm256StoreGd(nuvs[i], pcs[i], range(i,M), isCompact) for i in range(M)]
            instructions.extend([comm] + instrs)
#        elif (len(mStruct) == 1 and Matrix in mStruct) or (M!=N):
        
        for i in instructions:
            i.bounds.update(mParams['bounds'])
        
#         if M == 1:
#             if N < 4:
#                 pc = AddressOf(sa(dst[dL.of(0),dR.of(0)])) if N == 1 else Pointer(dst[dL.of(0),dR.of(0)])
#                 vmask = N*[1] + (4-N)*[0]
#                 va = mm256LoaduPd(Pointer(src[sL.of(0),sR.of(0)]),range(N,4))
#                 instr = mm256MaskstorePd(vmask, va, pc)
#                 instructions += [ Comment("1x4 -> 1x" + str(N) + " - Corner") ]
#                 instructions += [ instr ]
#         elif M == 2:
#             if N == 1:
#                 nuv = mm256LoaduPd(Pointer(src[sL.of(0),sR.of(0)]), [2,3])
#                 if isCompact:
#                     pc = Pointer(dst[dL.of(0),dR.of(0)])
#                     vmask = 2*[1] + 2*[0]
#                     instr = mm256MaskstorePd(vmask, nuv, pc)
#                     instructions += [ Comment("4x1 -> 2x1 - Compact") ]
#                     instructions += [ instr ]
#                 else:
#                     vmask = [1] + 3*[0]
#                     pc0 = Pointer(dst[dL.of(0),dR.of(0)])
#                     pc1 = Pointer(dst[dL.of(1),dR.of(0)])
#                     instr0 = mm256MaskstorePd(vmask, nuv, pc0)
#                     instr1 = mm256MaskstorePd(vmask, mm256ShufflePd(nuv, nuv, [0,0,0,1]), pc1)
#                     instructions += [ Comment("4x1 -> 2x1 - incompact") ]
#                     instructions += [ instr0, instr1 ]
#             elif N == 2:
#                 nuv0 = mm256LoaduPd(Pointer(src[sL.of(0),sR.of(0)]), [2,3])
#                 nuv1 = mm256LoaduPd(Pointer(src[sL.of(1),sR.of(0)]), [2,3])
#                 if isCompact:
#                     pc = Pointer(dst[dL.of(0),dR.of(0)])
#                     v = mm256Permute2f128Pd(nuv0, nuv1, [0,0,1,0,0,0,0,0])
#                     instructions += [ Comment("4x4 -> 2x2 - Compact"), mm256StoreuPd(v, pc) ]
#                 else:
#                     vmask = 2*[1] + 2*[0]
#                     pc0 = Pointer(dst[dL.of(0),dR.of(0)])
#                     pc1 = Pointer(dst[dL.of(1),dR.of(0)])
#                     instr0 = mm256MaskstorePd(vmask, nuv0, pc0)
#                     instr1 = mm256MaskstorePd(vmask, nuv1, pc1)
#                     instructions += [ Comment("4x4 -> 2x2 - incompact") ]
#                     instructions += [ instr0, instr1 ]
#             elif N == 3:
#                 nuv0 = mm256LoaduPd(Pointer(src[sL.of(0),sR.of(0)]), [3])
#                 nuv1 = mm256LoaduPd(Pointer(src[sL.of(1),sR.of(0)]), [3])
#                 if isCompact:
#                     pc0 = Pointer(dst[dL.of(0),dR.of(0)])
#                     pc1 = Pointer(dst[dL.of(1),dR.of(1)])
#                     t0 = mm256Permute2f128Pd(nuv1, nuv1, [0,0,0,0,0,0,0,1]) # 2nd lane <-> 1st
#                     t1 = mm256ShufflePd(nuv1, t0, [0,1,0,1])
#                     vmask = 2*[1] + 2*[0]
#                     instr0 = mm256StoreuPd(mm256BlendPd(nuv0, t1, [1,0,0,0]), pc0)
#                     instr1 = mm256MaskstorePd(vmask, t1, pc1)
#                     instructions += [ Comment("4x4 -> 2x3 - Compact") ]
#                     instructions += [ instr0, instr1 ]
#                 else:
#                     pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(2) ]
#                     vmask = 3*[1] + [0]
#                     instr0 = mm256MaskstorePd(vmask, nuv0, pcs[0])
#                     instr1 = mm256MaskstorePd(vmask, nuv1, pcs[1])
#                     instructions += [ Comment("4x4 -> 2x3 - incompact") ]
#                     instructions += [ instr0, instr1 ]
#             elif N == 4:
#                 v0_3 = mm256LoaduPd(Pointer(src[sL.of(0),sR.of(0)]))
#                 v4_7 = mm256LoaduPd(Pointer(src[sL.of(1),sR.of(0)]))
#                 pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(2) ]
#                 instr0 = mm256StoreuPd(v0_3, pcs[0])
#                 instr1 = mm256StoreuPd(v4_7, pcs[1])
#                 instructions += [ Comment("4x4 -> 2x4") ]
#                 instructions += [ instr0, instr1 ]
#         elif M == 3:
#             if N == 1:
#                 nuv = mm256LoaduPd(Pointer(src[sL.of(0),sR.of(0)]), [3])
#                 if isCompact:
#                     vmask = 3*[1] + [0]
#                     pc = Pointer(dst[dL.of(0),dR.of(0)])
#                     instr = mm256MaskstorePd(vmask, nuv, pc)
#                     instructions += [ Comment("4x1 -> 3x1 - Compact") ]
#                     instructions += [ instr ]
#                 else:
#                     pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(3) ]
#                     vmask = [1] + 3*[0]
#                     instr0 = mm256MaskstorePd(vmask, nuv, pcs[0])
#                     instr1 = mm256MaskstorePd(vmask, mm256ShufflePd(nuv, nuv, [0,0,0,1]), pcs[1])
#                     instr2 = mm256MaskstorePd(vmask, mm256Permute2f128Pd(nuv, nuv, [1,0,0,0,0,0,0,1]), pcs[2])
#                     instructions += [ Comment("4x1 -> 3x1 - incompact") ]
#                     instructions += [ instr0, instr1, instr2 ]
#             elif N == 2:
#                 nuvs = [ mm256LoaduPd(Pointer(src[sL.of(i),sR.of(0)]), [2,3]) for i in range(3) ]
#                 if isCompact:
#                     pc0 = Pointer(dst[dL.of(0),dR.of(0)])
#                     pc1 = Pointer(dst[dL.of(2),dR.of(0)])
#                     v = mm256Permute2f128Pd(nuvs[0], nuvs[1], [0,0,1,0,0,0,0,0])
#                     vmask = 2*[1] + 2*[0]
#                     instructions += [ Comment("4x4 -> 3x2 - Compact"), mm256StoreuPd(v, pc0), mm256MaskstorePd(vmask, nuvs[2], pc1) ]
#                 else:
#                     pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(3) ]
#                     vmask = 2*[1] + 2*[0]
#                     instructions += [ Comment("4x4 -> 3x2 - incompact") ]
#                     instructions += [ mm256MaskstorePd(vmask, nuvs[i], pcs[i]) for i in range(3) ]
#             elif N == 3:
#                 nuvs = [ mm256LoaduPd(Pointer(src[sL.of(i),sR.of(0)]), [3]) for i in range(3) ]
#                 vmask = 3*[1] + [0]
#                 pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(3) ]
#                 instructions += [ Comment("4x4 -> 3x3 - (In)compact") ]
#                 instructions += [ mm256MaskstorePd(vmask, nuvs[i], pcs[i]) for i in range(3) ]
#             elif N == 4:
#                 nuvs = [ mm256LoaduPd(Pointer(src[sL.of(i),sR.of(0)])) for i in range(3) ]
#                 pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(3) ]
#                 instructions += [ Comment("4x4 -> 3x4") ]
#                 instructions += [ mm256StoreuPd(nuvs[i], pcs[i]) for i in range(3) ]
#         elif M == 4:
#             if N == 1:
#                 if not isCompact:
#                     nuv = mm256LoaduPd(Pointer(src[sL.of(0),sR.of(0)]))
#                     pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4) ]
#                     vmask = [1] + 3*[0]
#                     instr0 = mm256MaskstorePd(vmask, nuv, pcs[0])
#                     instr1 = mm256MaskstorePd(vmask, mm256ShufflePd(nuv, nuv, [0,0,0,1]), pcs[1])
#                     invlane = mm256Permute2f128Pd(nuv, nuv, [1,0,0,0,0,0,0,1])
#                     instr2 = mm256MaskstorePd(vmask, invlane, pcs[2])
#                     instr3 = mm256MaskstorePd(vmask, mm256ShufflePd(invlane, invlane, [0,0,0,1]), pcs[3])
#                     instructions += [ Comment("4x1 -> 4x1 - incompact"), instr0, instr1, instr2, instr3 ]
#             elif N < 4:
#                 nuvs = [ mm256LoaduPd(Pointer(src[sL.of(i),sR.of(0)]), range(N,4)) for i in range(4) ]
#                 vmask = N*[1] + (4-N)*[0]
#                 pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4) ]
#                 instrs = [ mm256MaskstorePd(vmask, nuvs[i], pcs[i]) for i in range(4) ]
#                 instructions += [ Comment("4x" + str(N) + " -> 4x4") ] + instrs

        return instructions

class _Flt8Loader(Loader):
    def __init__(self):
        super(_Flt8Loader, self).__init__()
    
    def loadMatrix(self, mParams):
        
        nu=8
        src, dst = mParams['m'], mParams['nuM']
        sL, sR = mParams['mL'], mParams['mR']
        dL, dR = mParams['nuML'], mParams['nuMR']
        M, N = mParams['M'], mParams['N']
        nuMM, nuMN = mParams['nuMM'], mParams['nuMN']
        isCompact = mParams['compact']
        instructions = [ ]
        
        if M == 1 and N == 1:
            pc = Pointer(dst[dL.of(0),dR.of(0)])
#             vmask = [1] + 7*[0]
            pa = AddressOf(sa(src[sL.of(0),sR.of(0)]))
            if mParams['bcast']:
                va = mm256LoadGs(pa, [tuple(range(nu))])
            else:
                va = mm256LoadGs(pa, [0])
            instr = mm256StoreGs(va, pc, range(nu))
            instructions += [ Comment(str(M) + "x" + str(N) + " -> " + str(nuMM) + "x" + str(nuMN)) ]
            instructions += [ instr ]
        elif (N == 1 and ((M <= nu and not isCompact) or (M < nu and isCompact))) or (M == 1 and N < nu):
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            horizontal = M==1
            pa = Pointer(src[sL.of(0),sR.of(0)])
            va = mm256LoadGs(pa, range(max(M,N)), isCompact=isCompact, horizontal=horizontal)
            instr = mm256StoreGs(va, pc, range(nu))
#             else: # Incompact case should appear only for M>1 and N==1
#                 vmask = [1] + 7*[0]
#                 es = [ mm256MaskloadPs(Pointer(src[sL.of(i),sR.of(0)]), vmask) for i in range(M) ]
#                 if M == 2: 
#                     instr = mm256StoreuPs(mm256UnpackloPs(es[0], es[1]), pc)
#                 elif M==3:
#                     t0 = mm256UnpackloPs(es[0], es[1])
#                     instr = mm256StoreuPs(mm256ShufflePs(t0, es[2], (1,0,1,0)), pc)
#                 elif M==4:
#                     t0 = mm256UnpackloPs(es[0], es[1])
#                     t1 = mm256UnpackloPs(es[2], es[3])
#                     instr = mm256StoreuPs(mm256ShufflePs(t0, t1, (1,0,1,0)), pc)
#                 elif M==5:
#                     t0 = mm256UnpackloPs(es[0], es[1])
#                     t1 = mm256UnpackloPs(es[2], es[3])
#                     t2 = mm256ShufflePs(t0, t1, (1,0,1,0))
#                     instr = mm256StoreuPs(mm256Permute2f128Ps(t2, es[4], [0,0,1,0,0,0,0,0]), pc)
#                 elif M==6:
#                     t0 = mm256UnpackloPs(es[0], es[1])
#                     t1 = mm256UnpackloPs(es[2], es[3])
#                     t2 = mm256ShufflePs(t0, t1, (1,0,1,0))
#                     t3 = mm256UnpackloPs(es[4], es[5])
#                     instr = mm256StoreuPs(mm256Permute2f128Ps(t2, t3, [0,0,1,0,0,0,0,0]), pc)
#                 elif M==7:
#                     t0 = mm256UnpackloPs(es[0], es[1])
#                     t1 = mm256UnpackloPs(es[2], es[3])
#                     t2 = mm256ShufflePs(t0, t1, (1,0,1,0))
#                     t3 = mm256UnpackloPs(es[4], es[5])
#                     t4 = mm256ShufflePs(t3, es[6], (1,0,1,0))
#                     instr = mm256StoreuPs(mm256Permute2f128Ps(t2, t4, [0,0,1,0,0,0,0,0]), pc)
#                 elif M==8:
#                     t0 = mm256UnpackloPs(es[0], es[1])
#                     t1 = mm256UnpackloPs(es[2], es[3])
#                     t2 = mm256ShufflePs(t0, t1, (1,0,1,0))
#                     t3 = mm256UnpackloPs(es[4], es[5])
#                     t4 = mm256UnpackloPs(es[6], es[7])
#                     t5 = mm256ShufflePs(t3, t4, (1,0,1,0))
#                     instr = mm256StoreuPs(mm256Permute2f128Ps(t2, t5, [0,0,1,0,0,0,0,0]), pc)
            instructions += [ Comment(str(M) + "x" + str(N) + " -> " + str(nuMM) + "x" + str(nuMN)) ]
            instructions += [ instr ]
        elif (M < nu and N < nu) or (M == nu and N > 1 and N < nu) or (M > 1 and M < nu and N == nu):
            pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(nu) ]
            pas = [ Pointer(src[sL.of(i),sR.of(0)]) for i in range(M) ]
            vas = [ mm256LoadGs(pas[i], range(N)) for i in range(M) ]
            instructions += [ Comment(str(M) + "x" + str(N) + " -> " + str(nuMM) + "x" + str(nuMN)) ]
            instructions += [ mm256StoreGs(vas[i], pcs[i], range(nu)) for i in range(M) ]
            instructions += [ mm256StoreGs(mm256SetzeroPs(), pcs[i], range(nu)) for i in range(M,nu) ]
                
        return instructions

class _Flt8BLAC(object):
    def __init__(self):
        super(_Flt8BLAC, self).__init__()

    def Add(self, s0Params, s1Params, dParams, opts):
        
        nu = 8
        src0, src1, dst = s0Params['nuM'], s1Params['nuM'], dParams['nuM']
        s0L, s0R = s0Params['nuML'], s0Params['nuMR']
        s1L, s1R = s1Params['nuML'], s1Params['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        M, N     = dParams['nuMM'], dParams['nuMN']
        instructions = []

        instructions += [ Comment(str(nu) + "-BLAC: " + str(M) + "x" + str(N) + " + " + str(M) + "x" + str(N)) ]
        if M*N == nu:
            va = mm256LoadGs(Pointer(src0[s0L.of(0),s0R.of(0)]), range(nu))
            vb = mm256LoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            instr = mm256StoreGs(mm256AddPs(va, vb), pc, range(nu))
            instructions += [ instr ]
        elif M == nu and N == nu:
            for i in range(M):
                va = mm256LoadGs(Pointer(src0[s0L.of(i),s0R.of(0)]), range(nu))
                vb = mm256LoadGs(Pointer(src1[s1L.of(i),s1R.of(0)]), range(nu))
                pc = Pointer(dst[dL.of(i),dR.of(0)])
                instr = mm256StoreGs(mm256AddPs(va, vb), pc, range(nu))
                instructions += [ instr ]
        
        return instructions

    def Mul(self, s0Params, s1Params, dParams, opts):

        nu = 8
        src0, src1, dst = s0Params['nuM'], s1Params['nuM'], dParams['nuM']
        s0L, s0R = s0Params['nuML'], s0Params['nuMR']
        s1L, s1R = s1Params['nuML'], s1Params['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        M, K, N = s0Params['nuMM'], s0Params['nuMN'], s1Params['nuMN']
        instructions = []

        instructions += [ Comment(str(nu) + "-BLAC: " + str(M) + "x" + str(K) + " * " + str(K) + "x" + str(N)) ]
        if M == 1:
            if N == 1:
                va = mm256LoadGs(Pointer(src0[s0L.of(0),s0R.of(0)]), range(nu))
                vb = mm256LoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                vmul = mm256MulPs(va, vb)
                vper = mm256Permute2f128Ps(vmul, vmul, [1,0,0,0,0,0,0,1])
                vadd0 = mm256AddPs(vmul, vper)
                vshu0 = mm256ShufflePs(vadd0, mm256SetzeroPs(), [0,0,3,2])
                vadd1 = mm256AddPs(vadd0, vshu0)
                vble1 = mm256BlendPs(vadd1, mm256SetzeroPs(), [1]*7 + [0])
                vshu1 = mm256ShufflePs(vadd1, mm256SetzeroPs(), [0,0,2,1])
                vadd2 = mm256AddPs(vble1, vshu1)
                instr = mm256StoreGs(vadd2, pc, range(nu))
                instructions += [ instr ]
            else:
                vbs = [ mm256LoadGs(Pointer(src1[s1L.of(i),s1R.of(0)]), range(nu)) for i in range(nu) ]
                va0s = [ mm256LoadGs(Pointer(src0[s0L.of(0),s0R.of(i)]), [tuple(range(nu))]) for i in range(nu) ]
                
                adds = []
                for i in range(0,nu,2):
                    mul0 = mm256MulPs(va0s[i], vbs[i])
                    mul1 = mm256MulPs(va0s[i+1], vbs[i+1])
                    adds.append( mm256AddPs(mul0, mul1) )
                t0 = mm256AddPs(adds[0], adds[1])
                t1 = mm256AddPs(adds[2], adds[3])
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = mm256StoreGs(mm256AddPs(t0, t1), pc, range(nu))
                instructions += [ instr ]
        else:
            if K == 1:
                vas = [ mm256LoadGs(Pointer(src0[s0L.of(i),s0R.of(0)]), [tuple(range(nu))]) for i in range(nu) ]
                vb = mm256LoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
                pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(nu) ]
                instrs = [ mm256StoreGs(mm256MulPs(vas[i], vb), pcs[i], range(nu)) for i in range(nu) ]
                instructions += instrs
            else:
                if N == 1:
                    vas = [ mm256LoadGs(Pointer(src0[s0L.of(i),s0R.of(0)]), range(nu)) for i in range(nu) ]
                    vb = mm256LoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
                    muls = [ mm256MulPs(vas[i], vb) for i in range(nu) ]
                    lane0s = [ mm256Permute2f128Ps(muls[i], muls[4+i], [0,0,1,0,0,0,0,0]) for i in range(nu//2) ]
                    lane1s = [ mm256Permute2f128Ps(muls[i], muls[4+i], [0,0,1,1,0,0,0,1]) for i in range(nu//2) ]
                    t0s = [ mm256HaddPs(lane0s[i], lane1s[i]) for i in range(nu//2) ]
                    t1s = [ mm256HaddPs(t0s[i], t0s[i+1]) for i in range(0,nu//2,2) ]
                    pc = Pointer(dst[dL.of(0),dR.of(0)])
                    instr = mm256StoreGs(mm256HaddPs(t1s[0], t1s[1]), pc, range(nu))
                    instructions += [ instr ]
                else:
                    vbs = [ mm256LoadGs(Pointer(src1[s1L.of(i),s1R.of(0)]), range(nu)) for i in range(nu) ]
                    for i in range(nu):
                        vais = [ mm256LoadGs(Pointer(src0[s0L.of(i),s0R.of(j)]), [tuple(range(nu))]) for j in range(nu) ]
                        adds = []
                        for j in range(0,nu,2):
                            mul0 = mm256MulPs(vais[j], vbs[j])
                            mul1 = mm256MulPs(vais[j+1], vbs[j+1])
                            adds.append( mm256AddPs(mul0, mul1) )
                        t0 = mm256AddPs(adds[0], adds[1])
                        t1 = mm256AddPs(adds[2], adds[3])
                        pc = Pointer(dst[dL.of(i),dR.of(0)])
                        instr = mm256StoreGs(mm256AddPs(t0, t1), pc, range(nu))
                        instructions += [ instr ]

        return instructions

    def Kro(self, s0Params, s1Params, dParams, opts):

        nu = 8
        src0, src1, dst = s0Params['nuM'], s1Params['nuM'], dParams['nuM']
        s0L, s0R = s0Params['nuML'], s0Params['nuMR']
        s1L, s1R = s1Params['nuML'], s1Params['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        oM, oK, oN, oP = s0Params['M'], s0Params['N'], s1Params['M'], s1Params['N']
        M, K, N, P = s0Params['nuMM'], s0Params['nuMN'], s1Params['nuMM'], s1Params['nuMN']
        instructions = []
        
        instructions += [ Comment(str(nu) + "-BLAC: " + str(M) + "x" + str(K) + " Kro " + str(N) + "x" + str(P)) ]
        if oM*oK*oN*oP == 1:
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            va = mm256LoadGs(Pointer(src0[s0L.of(0),s0R.of(0)]), range(nu))
            vb = mm256LoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
            instr = mm256StoreGs(mm256MulPs(va, vb), pc, range(nu))
            instructions += [ instr ]
        elif oM*oK == 1:
            if s0Params['bcast']:
                dup = mm256LoadGs(Pointer(src0[s0L.of(0),s0R.of(0)]), range(nu))
            else:
                va = mm256LoadGs(Pointer(src0[s0L.of(0),s0R.of(0)]), range(nu))
                repva = mm256Permute2f128Ps(va, va, [0,0,0,0,0,0,0,0]) #Need to replicate on the 2nd lane
                dup = mm256ShufflePs(repva, repva, (0,0,0,0))

            if N*P == nu:
                vb = mm256LoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = mm256StoreGs(mm256MulPs(dup, vb), pc, range(nu))
                instructions += [ instr ]
            else:
#                 va = mm256LoadGs(Pointer(src0[s0L.of(0),s0R.of(0)]), range(nu))
#                 repva = mm256Permute2f128Ps(va, va, [0,0,0,0,0,0,0,0]) #Need to replicate on the 2nd lane
#                 dup = mm256ShufflePs(repva, repva, (0,0,0,0))
                for i in range(nu):
                    vb = mm256LoadGs(Pointer(src1[s1L.of(i),s1R.of(0)]), range(nu))
                    pc = Pointer(dst[dL.of(i),dR.of(0)])
                    instr = mm256StoreGs(mm256MulPs(dup, vb), pc, range(nu))
                    instructions += [ instr ]
        else:
            if s1Params['bcast']:
                dup = mm256LoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
            else:
                vb = mm256LoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
                repvb = mm256Permute2f128Ps(vb, vb, [0,0,0,0,0,0,0,0]) #Need to replicate on the 2nd lane
                dup = mm256ShufflePs(repvb, repvb, (0,0,0,0))

            if M*K == nu:
                va = mm256LoadGs(Pointer(src0[s0L.of(0),s0R.of(0)]), range(nu))
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = mm256StoreGs(mm256MulPs(va, dup), pc, range(nu))
                instructions += [ instr ]
            else:
#                 vb = mm256LoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
#                 repvb = mm256Permute2f128Ps(vb, vb, [0,0,0,0,0,0,0,0]) #Need to replicate on the 2nd lane
#                 dup = mm256ShufflePs(repvb, repvb, (0,0,0,0))
                for i in range(nu):
                    va = mm256LoadGs(Pointer(src0[s0L.of(i),s0R.of(0)]), range(nu))
                    pc = Pointer(dst[dL.of(i),dR.of(0)])
                    instr = mm256StoreGs(mm256MulPs(va, dup), pc, range(nu))
                    instructions += [ instr ]
        
        return instructions

    def T(self, sParams, dParams, opts):

        nu = 8
        src, dst = sParams['nuM'], dParams['nuM']
        sL, sR = sParams['nuML'], sParams['nuMR']
        dL, dR = dParams['nuML'], dParams['nuMR']
        M, N = dParams['nuMM'], dParams['nuMN']
        instructions = []

        instructions += [ Comment(str(nu) + "-BLAC: (" + str(N) + "x" + str(M) + ")^T") ]
        if M*N == nu:
            va = mm256LoadGs(Pointer(src[sL.of(0),sR.of(0)]), range(nu))
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            instr = mm256StoreGs(va, pc, range(nu))
            instructions += [ instr ]
        else:
            vas = [ mm256LoadGs(Pointer(src[sL.of(i),sR.of(0)]), range(nu)) for i in range(nu) ]

            unplos = [ mm256UnpackloPs(vas[i], vas[i+1]) for i in range(0,nu,2) ]
            unphis = [ mm256UnpackhiPs(vas[i], vas[i+1]) for i in range(0,nu,2) ]
            
            trow0 = mm256ShufflePs(unplos[0], unplos[1], (1,0,1,0))
            trow1 = mm256ShufflePs(unplos[0], unplos[1], (3,2,3,2))
            trow2 = mm256ShufflePs(unphis[0], unphis[1], (1,0,1,0))
            trow3 = mm256ShufflePs(unphis[0], unphis[1], (3,2,3,2))
            trow4 = mm256ShufflePs(unplos[2], unplos[3], (1,0,1,0))
            trow5 = mm256ShufflePs(unplos[2], unplos[3], (3,2,3,2))
            trow6 = mm256ShufflePs(unphis[2], unphis[3], (1,0,1,0))
            trow7 = mm256ShufflePs(unphis[2], unphis[3], (3,2,3,2))

            newrows = [ mm256Permute2f128Ps(trow0, trow4, [0,0,1,0,0,0,0,0]) ]
            newrows.append( mm256Permute2f128Ps(trow1, trow5, [0,0,1,0,0,0,0,0]) )
            newrows.append( mm256Permute2f128Ps(trow2, trow6, [0,0,1,0,0,0,0,0]) )
            newrows.append( mm256Permute2f128Ps(trow3, trow7, [0,0,1,0,0,0,0,0]) )
            newrows.append( mm256Permute2f128Ps(trow0, trow4, [0,0,1,1,0,0,0,1]) )
            newrows.append( mm256Permute2f128Ps(trow1, trow5, [0,0,1,1,0,0,0,1]) )
            newrows.append( mm256Permute2f128Ps(trow2, trow6, [0,0,1,1,0,0,0,1]) )
            newrows.append( mm256Permute2f128Ps(trow3, trow7, [0,0,1,1,0,0,0,1]) )

            pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(nu) ]
            instructions += [ mm256StoreGs(newrows[i], pcs[i], range(nu)) for i in range(nu) ]
        
        return instructions

class _Flt8Storer(Storer):
    def __init__(self):
        super(_Flt8Storer, self).__init__()

    def storeMatrix(self, mParams):
        nu=8
        src, dst = mParams['nuM'], mParams['m']
        sL, sR = mParams['nuML'], mParams['nuMR']
        dL, dR = mParams['mL'], mParams['mR']
        M, N = mParams['M'], mParams['N']
        nuMM, nuMN = mParams['nuMM'], mParams['nuMN']
        isCompact = mParams['compact']
        instructions = [ Comment(str(nuMM) + "x" + str(nuMN) + " -> " + str(M) + "x" + str(N)) ]

        if M == 1 and N == 1:
            pc = AddressOf(sa(dst[dL.of(0),dR.of(0)]))
            va = mm256LoadGs(Pointer(src[sL.of(0),sR.of(0)]), range(nu))
            instr = mm256StoreGs(va, pc,[0])
            instructions += [ instr ]
        elif (N == 1 and ((M <= nu and not isCompact) or (M < nu and isCompact))) or (M == 1 and N < nu):
            va = mm256LoadGs(Pointer(src[sL.of(0),sR.of(0)]), range(nu))
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            horizontal = M==1
            instr = mm256StoreGs(va, pc, range(max(M,N)), isCompact=isCompact, horizontal=horizontal)            
#             if isCompact:
#                 pc = Pointer(dst[dL.of(0),dR.of(0)])
#                 if max(M,N) < nu:
#                     vmask = max(M,N)*[1] + (nu-max(M,N))*[0]
#                     instrs = [ mm256MaskstorePs(vmask, va, pc) ]
#                 else:
#                     instrs = [ mm256StoreuPs(va, pc) ]
#             else:
#                 vmask = [1] + 7*[0]
#                 pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(M) ]
#                 instrs = []
#                 if M == 2: 
#                     instrs.append( mm256MaskstorePs(vmask, va, pcs[0]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(va, va, (2,2,2,1)), pcs[1]) )
#                 elif M==3:
#                     instrs.append( mm256MaskstorePs(vmask, va, pcs[0]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(va, va, (3,3,3,1)), pcs[1]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(va, va, (3,3,3,2)), pcs[2]) )
#                 elif M==4:
#                     instrs.append( mm256MaskstorePs(vmask, va, pcs[0]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(va, mm256SetzeroPs(), (0,0,0,1)), pcs[1]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(va, mm256SetzeroPs(), (0,0,0,2)), pcs[2]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(va, mm256SetzeroPs(), (0,0,0,3)), pcs[3]) )
#                 elif M==5:
#                     instrs.append( mm256MaskstorePs(vmask, va, pcs[0]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(va, mm256SetzeroPs(), (0,0,0,1)), pcs[1]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(va, mm256SetzeroPs(), (0,0,0,2)), pcs[2]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(va, mm256SetzeroPs(), (0,0,0,3)), pcs[3]) )
#                     lane1 = mm256Permute2f128Ps(va, va, [1,0,0,0,0,0,0,1])
#                     instrs.append( mm256MaskstorePs(vmask, lane1, pcs[4]) )
#                 elif M==6:
#                     instrs.append( mm256MaskstorePs(vmask, va, pcs[0]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(va, mm256SetzeroPs(), (0,0,0,1)), pcs[1]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(va, mm256SetzeroPs(), (0,0,0,2)), pcs[2]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(va, mm256SetzeroPs(), (0,0,0,3)), pcs[3]) )
#                     lane1 = mm256Permute2f128Ps(va, va, [1,0,0,0,0,0,0,1])
#                     instrs.append( mm256MaskstorePs(vmask, lane1, pcs[4]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(lane1, lane1, (2,2,2,1)), pcs[5]) )
#                 elif M==7:
#                     instrs.append( mm256MaskstorePs(vmask, va, pcs[0]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(va, mm256SetzeroPs(), (0,0,0,1)), pcs[1]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(va, mm256SetzeroPs(), (0,0,0,2)), pcs[2]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(va, mm256SetzeroPs(), (0,0,0,3)), pcs[3]) )
#                     lane1 = mm256Permute2f128Ps(va, va, [1,0,0,0,0,0,0,1])
#                     instrs.append( mm256MaskstorePs(vmask, lane1, pcs[4]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(lane1, lane1, (3,3,3,1)), pcs[5]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(lane1, lane1, (3,3,3,2)), pcs[6]) )
#                 elif M==8:
#                     instrs.append( mm256MaskstorePs(vmask, va, pcs[0]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(va, mm256SetzeroPs(), (0,0,0,1)), pcs[1]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(va, mm256SetzeroPs(), (0,0,0,2)), pcs[2]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(va, mm256SetzeroPs(), (0,0,0,3)), pcs[3]) )
#                     lane1 = mm256Permute2f128Ps(va, va, [1,0,0,0,0,0,0,1])
#                     instrs.append( mm256MaskstorePs(vmask, lane1, pcs[4]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(lane1, mm256SetzeroPs(), (0,0,0,1)), pcs[5]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(lane1, mm256SetzeroPs(), (0,0,0,2)), pcs[6]) )
#                     instrs.append( mm256MaskstorePs(vmask, mm256ShufflePs(lane1, mm256SetzeroPs(), (0,0,0,3)), pcs[7]) )
            instructions += [ instr ]
        elif (M < nu and N < nu) or (M == nu and N > 1 and N < nu) or (M > 1 and M < nu and N == nu):
            pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(M) ]
            vas = [ mm256LoadGs(Pointer(src[sL.of(i),sR.of(0)]), range(nu)) for i in range(M) ]
#             if N < nu:
#                 vmask = N*[1] + (nu-N)*[0]
#                 instrs = [ mm256MaskstorePs(vmask, vas[i], pcs[i]) for i in range(M) ]
#             else:
            instrs = [ mm256StoreGs(vas[i], pcs[i], range(N)) for i in range(M) ]
            instructions += instrs
                
        return instructions

class AVXLoadReplacer(LoadReplacer):
    def __init__(self, opts):
        super(AVXLoadReplacer, self).__init__(opts)

    def mm256BroadcastSd(self, src, repList):
        sList = sorted(repList, key=lambda t: t[0], reverse=True)
        dst = sList[0][1]
        if dst.reglen == 4 and dst.mrmap == [0,1,2,3]:
#             at = src.pointer.getAt()
#             direct = 1 if src.pointer.getMat().size[1] > 1 else 0   # Temp solution
#             lane1, posInLane = at[direct] > 1, at[direct] % 2  
#             immBitList = [0,0,1,1,0,0,0,1] if lane1 else [0,0,1,0,0,0,0,0]
#             dupLane = mm256Permute2f128Pd(mm256LoaduPd(dst.pointer), mm256LoaduPd(dst.pointer), immBitList) # Dup the lane where we can find the value
#             return mm256ShufflePd(dupLane, dupLane, [posInLane]*4)
            dupx2 = mm256UnpackloPd(mm256LoaduPd(dst.pointer), mm256LoaduPd(dst.pointer))
            return mm256Permute2f128Pd(dupx2, dupx2, [0,0,1,0,0,0,0,0]) # Dup first lane

    def mm256LoadGd(self, src, repList, bounds):
        #src is the mm256LoadGd we want to replace with combinations of elements from previous stores in repList 
#         if src.pointer._ref.physLayout.name == 'C' and src.pointer.at == (0,8) and src.mrmap == [0]:
#             pass
        list_by_line = sorted(repList, key=lambda t: t[0], reverse=True)
        dsts_by_line = [ t[1] for t in list_by_line ]
        src_dsts_map = self.src_dsts_map(src, dsts_by_line)
        if len(src_dsts_map) > 1:
            dsts = [ t[2] for t in src_dsts_map ] 
            if len(src_dsts_map) == 4 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([0],[0]),([1],[0]),([2],[0]),([3],[0])]) ]):
                notums = [ [True]*len(dst.mrmap) for dst in dsts ]
                for i in range(4):
                    notums[i][dsts[i].mrmap.index(0)] = False
                ld_dsts = [ mm256LoadGd(dsts[i].pointer, dsts[i].mrmap, isCompact=dsts[i].isCompact, horizontal=dsts[i].horizontal, not_using_mask=notums[i]) for i in range(4) ]
                shuf_1st = mm256UnpackloPd(ld_dsts[0], ld_dsts[1])
                shuf_2nd = mm256UnpackloPd(ld_dsts[2], ld_dsts[3])
#                 blend_1st_2nd = mm256BlendPd(shuf_1st, shuf_2nd, [1,1,0,0])
#                 return blend_1st_2nd
                return mm256Permute2f128Pd(shuf_1st, shuf_2nd, [0,0,1,0,0,0,0,0])
            elif len(src_dsts_map) == 4 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([0],[2]),([1],[1]),([2],[0]),([3],[0])]) ]):
                notums = [ [True]*len(dst.mrmap) for dst in dsts ]
                for i,p in enumerate([2,1,0,0]):
                    notums[i][dsts[i].mrmap.index(p)] = False
                ld_dsts = [ mm256LoadGd(dsts[i].pointer, dsts[i].mrmap, isCompact=dsts[i].isCompact, horizontal=dsts[i].horizontal, not_using_mask=notums[i]) for i in range(4) ]
                shuf_2nd = mm256UnpackloPd(ld_dsts[2], ld_dsts[3])
                perm = mm256Permute2f128Pd(ld_dsts[0], shuf_2nd, [0,0,1,0,0,0,0,1])
                return mm256BlendPd(perm, ld_dsts[1], [0,0,1,0])
            elif len(src_dsts_map) == 3 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([0],[0]),([1],[0]),([2],[0])]) ]):
                notums = [ [True]*len(dst.mrmap) for dst in dsts ]
                for i in range(3):
                    notums[i][dsts[i].mrmap.index(0)] = False
                ld_dsts = [ mm256LoadGd(dsts[i].pointer, dsts[i].mrmap, isCompact=dsts[i].isCompact, horizontal=dsts[i].horizontal, not_using_mask=notums[i]) for i in range(3) ]
                shuf_1st = mm256UnpackloPd(ld_dsts[0], ld_dsts[1])
                shuf_2nd = mm256UnpackloPd(ld_dsts[2], mm256SetzeroPd())
#                 blend_1st_2nd = mm256BlendPd(shuf_1st, shuf_2nd, [1,1,0,0])
#                 return blend_1st_2nd
                return mm256Permute2f128Pd(shuf_1st, shuf_2nd, [0,0,1,0,0,0,0,0])
            elif len(src_dsts_map) == 3 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([0],[1]),([1],[0]),([2],[0])]) ]):
                notums = [ [True]*len(dst.mrmap) for dst in dsts ]
                for i,p in enumerate([1,0,0]):
                    notums[i][dsts[i].mrmap.index(p)] = False
                ld_dsts = [ mm256LoadGd(dsts[i].pointer, dsts[i].mrmap, isCompact=dsts[i].isCompact, horizontal=dsts[i].horizontal, not_using_mask=notums[i]) for i in range(3) ]
                shuf_1st = mm256ShufflePd(ld_dsts[0], ld_dsts[1], [0,0,0,1])
                shuf_2nd = mm256UnpackloPd(ld_dsts[2], mm256SetzeroPd())
                return mm256Permute2f128Pd(shuf_1st, shuf_2nd, [0,0,1,0,0,0,0,0])
            elif len(src_dsts_map) == 3 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([0],[0]),([1],[0]),([2,3],[1,2])]) ]):
                notums = [ [True]*len(dst.mrmap) for dst in dsts ]
                notums[0][dsts[0].mrmap.index(0)] = False
                notums[1][dsts[1].mrmap.index(0)] = False
                for p in [1,2]:
                    notums[2][dsts[2].mrmap.index(p)] = False
                ld_dst2 = mm256LoadGd(dsts[2].pointer, dsts[2].mrmap, isCompact=dsts[2].isCompact, horizontal=dsts[2].horizontal, not_using_mask=notums[2])
                immBitList = [0,0,0,0,1,0,0,0] # Move 1st lane to 2nd. 1st lane is zeroed 
                inter_lane = mm256Permute2f128Pd(ld_dst2, ld_dst2, immBitList)
                shuf_1st = mm256ShufflePd(mm256LoadGd(dsts[0].pointer, dsts[0].mrmap, isCompact=dsts[0].isCompact, horizontal=dsts[0].horizontal, not_using_mask=notums[0]), \
                                          mm256LoadGd(dsts[1].pointer, dsts[1].mrmap, isCompact=dsts[1].isCompact, horizontal=dsts[1].horizontal, not_using_mask=notums[1]), [0,0,0,0])
                shuf_2nd = mm256ShufflePd(inter_lane, ld_dst2, [0,1,0,0])
                blend_1st_2nd = mm256BlendPd(shuf_1st, shuf_2nd, [1,1,0,0])
                return blend_1st_2nd
            elif len(src_dsts_map) == 3 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([0],[0]),([1],[0]),([2],[1])]) ]):
                notums = [ [True]*len(dst.mrmap) for dst in dsts ]
                notums[0][dsts[0].mrmap.index(0)] = False
                notums[1][dsts[1].mrmap.index(0)] = False
                notums[2][dsts[2].mrmap.index(1)] = False
                ld_dst2 = mm256LoadGd(dsts[2].pointer, dsts[2].mrmap, isCompact=dsts[2].isCompact, horizontal=dsts[2].horizontal, not_using_mask=notums[2]) 
                immBitList = [0,0,0,0,1,0,0,0] # Move 1st lane to 2nd. 1st lane is zeroed
                inter_lane = mm256Permute2f128Pd(ld_dst2, ld_dst2, immBitList)
                shuf_1st = mm256UnpackloPd(mm256LoadGd(dsts[0].pointer, dsts[0].mrmap, isCompact=dsts[0].isCompact, horizontal=dsts[0].horizontal, not_using_mask=notums[0]), \
                                           mm256LoadGd(dsts[1].pointer, dsts[1].mrmap, isCompact=dsts[1].isCompact, horizontal=dsts[1].horizontal, not_using_mask=notums[1]))
                shuf_2nd = mm256UnpackhiPd(inter_lane, mm256SetzeroPd())
                blend_1st_2nd = mm256BlendPd(shuf_1st, shuf_2nd, [1,1,0,0])
                return blend_1st_2nd
            elif len(src_dsts_map) == 3 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([0],[3]),([1],[3]),([2],[3])]) ]):
                notums = [ [True]*len(dst.mrmap) for dst in dsts ]
                for dst,notum in zip(dsts,notums):
                    notum[dst.mrmap.index(3)] = False
                lds = [ mm256LoadGd(dst.pointer, dst.mrmap, isCompact=dst.isCompact, horizontal=dst.horizontal, not_using_mask=notum) for dst,notum in zip(dsts,notums) ]
                immBitList = [1,0,0,0,0,0,0,1] 
                perms_lane = [ mm256Permute2f128Pd(ld, ld, immBitList) for ld in lds[:2] ] 
                shuf1 = mm256UnpackhiPd(perms_lane[0], perms_lane[1])
                shuf2 = mm256UnpackhiPd(lds[2], mm256SetzeroPd())
                blend = mm256BlendPd(shuf1, shuf2, [1,1,0,0])
                return blend
            elif len(src_dsts_map) ==3 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([0],[2]),([1],[1]),([2],[0])]) ]):
                notums = [ [True]*len(dst.mrmap) for dst in dsts ]
                for dst,notum,p in zip(dsts,notums,[2,1,0]):
                    notum[dst.mrmap.index(p)] = False
                lds = [ mm256LoadGd(dst.pointer, dst.mrmap, isCompact=dst.isCompact, horizontal=dst.horizontal, not_using_mask=notum) for dst,notum in zip(dsts,notums) ]
                perm_lane02 = mm256Permute2f128Pd(lds[0], lds[2], [0,0,1,0,0,0,0,1])
                blend1 = mm256BlendPd(mm256SetzeroPd(), lds[1], [0,0,1,0]) 
                load_rep = mm256BlendPd(perm_lane02, blend1, [1,0,1,0])
                return load_rep
            elif len(src_dsts_map) == 3 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([0,1],[0,1]),([2],[2]), ([3],[0])]) ]):
                notums = [ [True]*len(dst.mrmap) for dst in dsts ]
                for p in [0,1]:
                    notums[0][dsts[0].mrmap.index(p)] = False
                notums[1][dsts[1].mrmap.index(2)] = False
                notums[2][dsts[2].mrmap.index(0)] = False
                lds = [ mm256LoadGd(dst.pointer, dst.mrmap, isCompact=dst.isCompact, horizontal=dst.horizontal, not_using_mask=notum) for dst,notum in zip(dsts,notums) ]
                perm = mm256Permute2f128Pd(lds[0], lds[2], [0,0,1,0,0,0,0,0])
                shuf = mm256ShufflePd(perm, perm, [0,0,1,0])
                return mm256BlendPd(lds[1], shuf, [1,0,1,1])
            elif len(src_dsts_map) == 3 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([0],[0]),([1],[1]),([2],[0])]) ]):
                notums = [ [True]*len(dst.mrmap) for dst in dsts ]
                for d,p in [(0,0),(1,1),(2,0)]:
                    notums[d][dsts[d].mrmap.index(p)] = False
                lds = [ mm256LoadGd(dst.pointer, dst.mrmap, isCompact=dst.isCompact, horizontal=dst.horizontal, not_using_mask=notum) for dst,notum in zip(dsts,notums) ]
                blend01 = mm256BlendPd(lds[0], lds[1], [0,0,1,0])
                perm = mm256Permute2f128Pd(blend01, lds[2], [0,0,1,0,0,0,0,0])
                return mm256BlendPd(perm, mm256SetzeroPd(), [1,0,0,0])
            elif len(src_dsts_map) == 2 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([0],[1]),([1],[0])]) ]):
                notums = [ [True]*len(dst.mrmap) for dst in dsts ]
                for dst,notum,p in zip(dsts,notums,[1,0]):
                    notum[dst.mrmap.index(p)] = False
                lds = [ mm256LoadGd(dst.pointer, dst.mrmap, isCompact=dst.isCompact, horizontal=dst.horizontal, not_using_mask=notum) for dst,notum in zip(dsts,notums) ]
                blend_lds = [ mm256BlendPd(ld, mm256SetzeroPd(), [1,1,0,0]) for ld in lds ]
                shuf = mm256ShufflePd(blend_lds[0], blend_lds[1], [0,0,0,1])
                return shuf
            elif len(src_dsts_map) == 2 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([0],[1]),([1],[1])]) ]):
                notums = [ [True]*len(dst.mrmap) for dst in dsts ]
                for dst,notum in zip(dsts,notums):
                    notum[dst.mrmap.index(1)] = False
                lds = [ mm256LoadGd(dst.pointer, dst.mrmap, isCompact=dst.isCompact, horizontal=dst.horizontal, not_using_mask=notum) for dst,notum in zip(dsts,notums) ]
                blend_lds = [ mm256BlendPd(ld, mm256SetzeroPd(), [1,1,0,0]) for ld in lds ]
                shuf = mm256UnpackhiPd(blend_lds[0], blend_lds[1])
                return shuf
            elif len(src_dsts_map) == 2 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([0],[3]),([1],[3])]) ]):
                notums = [ [True]*len(dst.mrmap) for dst in dsts ]
                for dst,notum in zip(dsts,notums):
                    notum[dst.mrmap.index(3)] = False
                lds = [ mm256LoadGd(dst.pointer, dst.mrmap, isCompact=dst.isCompact, horizontal=dst.horizontal, not_using_mask=notum) for dst,notum in zip(dsts,notums) ]
                immBitList = [1,0,0,0,0,0,0,1] 
                perms_lane = [ mm256Permute2f128Pd(ld, ld, immBitList) for ld in lds ] 
                shuf = mm256UnpackhiPd(perms_lane[0], perms_lane[1])
                return shuf
            elif len(src_dsts_map) == 2 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([0],[0]),([1,2],[0,1])]) ]):
                notums = [ [True]*len(dst.mrmap) for dst in dsts ]
                notums[0][dsts[0].mrmap.index(0)] = False
                for p in [0,1]:
                    notums[1][dsts[1].mrmap.index(p)] = False
                ld_dst1 = mm256LoadGd(dsts[1].pointer, dsts[1].mrmap, isCompact=dsts[1].isCompact, horizontal=dsts[1].horizontal, not_using_mask=notums[1]) 
                immBitList = [0,0,0,0,1,0,0,0] # Move 1st lane to 2nd. 1st lane is zeroed 
                inter_lane = mm256Permute2f128Pd(ld_dst1, ld_dst1, immBitList)
                shuf_1st = mm256UnpackloPd(mm256LoadGd(dsts[0].pointer, dsts[0].mrmap, isCompact=dsts[0].isCompact, horizontal=dsts[0].horizontal, not_using_mask=notums[0]), ld_dst1)
#                 shuf_1st = mm256ShufflePd(mm256LoadGd(dsts[0].pointer, dsts[0].mrmap), mm256LoadGd(dsts[1].pointer, dsts[1].mrmap), [0,0,0,0])
                shuf_2nd = mm256UnpackhiPd(inter_lane, mm256SetzeroPd())
                blend_1st_2nd = mm256BlendPd(shuf_1st, shuf_2nd, [1,1,0,0])
                return blend_1st_2nd
            elif len(src_dsts_map) == 2 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([0,1],[0,1]),([2],[0])]) ]):
                notums = [ [True]*len(dst.mrmap) for dst in dsts ]
                for p in [0,1]:
                    notums[0][dsts[0].mrmap.index(p)] = False
                notums[1][dsts[1].mrmap.index(0)] = False
                lds = [ mm256LoadGd(dst.pointer, dst.mrmap, isCompact=dst.isCompact, horizontal=dst.horizontal, not_using_mask=notum) for dst,notum in zip(dsts,notums) ]
                blend1 = mm256BlendPd(mm256SetzeroPd(), lds[1], [0,0,0,1])
                inter_lane = mm256Permute2f128Pd(blend1, blend1, [0,0,0,0,1,0,0,0])
                return mm256BlendPd(lds[0], inter_lane, [1,1,0,0])
            elif len(src_dsts_map) == 2 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([0,1,2],[0,1,2]),([3],[0])]) ]):
                notums = [ [True]*len(dst.mrmap) for dst in dsts ]
                for p in [0,1,2]:
                    notums[0][dsts[0].mrmap.index(p)] = False
                notums[1][dsts[1].mrmap.index(0)] = False
                lds = [ mm256LoadGd(dst.pointer, dst.mrmap, isCompact=dst.isCompact, horizontal=dst.horizontal, not_using_mask=notum) for dst,notum in zip(dsts,notums) ]
                perm = mm256Permute2f128Pd(lds[1], lds[1], [0,0,0,0,1,0,0,0])
                shuf = mm256ShufflePd(perm, perm, [0,0,0,0])
                return mm256BlendPd(lds[0], shuf, [1,0,0,0])
            elif len(src_dsts_map) == 2 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([0],[2]),([1],[0])]) ]):
                sys.exit("replacement under construction")
                notums = [ [True]*len(dst.mrmap) for dst in dsts ]
                for dst,notum,p in zip(dsts,notums,[2,0]):
                    notum[dst.mrmap.index(p)] = False
                lds = [ mm256LoadGd(dst.pointer, dst.mrmap, isCompact=dst.isCompact, horizontal=dst.horizontal, not_using_mask=notum) for dst,notum in zip(dsts,notums) ]
                immBitList = [1,0,0,0,0,0,0,1] 
                perm_lane = mm256Permute2f128Pd(lds[0], lds[0], immBitList) 
                load_rep = mm256BlendPd(perm_lane, lds[1], [0,0,1,0])
                return load_rep
            elif len(src_dsts_map) == 2 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([0],[2]),([1],[1])]) ]):
                notums = [ [True]*len(dst.mrmap) for dst in dsts ]
                for dst,notum,p in zip(dsts,notums,[2,1]):
                    notum[dst.mrmap.index(p)] = False
                lds = [ mm256LoadGd(dst.pointer, dst.mrmap, isCompact=dst.isCompact, horizontal=dst.horizontal, not_using_mask=notum) for dst,notum in zip(dsts,notums) ]
                immBitList = [1,0,0,0,0,0,0,1] 
                perm_lane = mm256Permute2f128Pd(lds[0], lds[0], immBitList) 
                load_rep = mm256BlendPd(perm_lane, lds[1], [0,0,1,0])
                return load_rep
            elif len(src_dsts_map) == 2 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([0],[2]),([1],[2])]) ]):
                notums = [ [True]*len(dst.mrmap) for dst in dsts ]
                for dst,notum in zip(dsts,notums):
                    notum[dst.mrmap.index(2)] = False
                lds = [ mm256LoadGd(dst.pointer, dst.mrmap, isCompact=dst.isCompact, horizontal=dst.horizontal, not_using_mask=notum) for dst,notum in zip(dsts,notums) ]
                immBitList = [1,0,0,0,0,0,0,1] 
                perms_lane = [ mm256Permute2f128Pd(ld, ld, immBitList) for ld in lds ] 
                shuf = mm256UnpackloPd(perms_lane[0], perms_lane[1])
                return shuf
            elif len(src_dsts_map) == 2 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([0],[0]),([1],[0])]) ]):
                notums = [ [True]*len(dst.mrmap) for dst in dsts ]
                for i in range(2):
                    notums[i][dsts[i].mrmap.index(0)] = False
                ld_dsts = [ mm256LoadGd(dsts[i].pointer, dsts[i].mrmap, isCompact=dsts[i].isCompact, horizontal=dsts[i].horizontal, not_using_mask=notums[i]) for i in range(2) ]
                shuf_1st = mm256UnpackloPd(ld_dsts[0], ld_dsts[1])
                blend_1st_zeros = mm256BlendPd(shuf_1st, mm256SetzeroPd(), [1,1,0,0])
                return blend_1st_zeros
            elif len(src_dsts_map) == 2 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([0],[1]),([1],[2])]) ]): #Like single map, dist==-1
                notums = [ [True]*len(dst.mrmap) for dst in dsts ]
                notums[0][1], notums[1][2] = False, False
                ld_dsts = [ mm256LoadGd(dsts[i].pointer, dsts[i].mrmap, isCompact=dsts[i].isCompact, horizontal=dsts[i].horizontal, not_using_mask=notums[i]) for i in range(2) ]
                lane_perm = mm256Permute2f128Pd(ld_dsts[1], ld_dsts[1], [1,0,0,0,0,0,0,1])
                blend_dst = mm256BlendPd(mm256SetzeroPd(), ld_dsts[0], [0,0,1,0])
                load_rep = mm256ShufflePd(blend_dst, lane_perm, [0,1,0,1])
                return load_rep
            elif dsts[-1] is None:
                if len(src_dsts_map) == 2 and all([ t[:2] == p for t,p in zip(src_dsts_map,[ ([0],[0]) ]) ]): #Blending
                    dst = dsts[0]
                    dnotum = [True]*len(dst.mrmap)
                    dnotum[0] = False  
                    ld_dst = mm256LoadGd(dst.pointer, dst.mrmap, isCompact=dst.isCompact, horizontal=dst.horizontal, not_using_mask=dnotum)
                    src.not_using_mask[0] = True
                    imm_list = [0]*dst.reglen
                    imm_list[dst.reglen-1] = 1
                    return mm256BlendPd(src, ld_dst, imm_list)
                elif len(src_dsts_map) == 2 and all([ t[:2] == p for t,p in zip(src_dsts_map,[ ([0],[1]) ]) ]): 
                    dst = dsts[0]
                    dnotum = [True]*len(dst.mrmap)
                    dnotum[1] = False  
                    ld_dst = mm256LoadGd(dst.pointer, dst.mrmap, isCompact=dst.isCompact, horizontal=dst.horizontal, not_using_mask=dnotum)
                    blend_dst = mm256BlendPd(src, ld_dst, [0,0,1,0])
                    src.not_using_mask[0] = True
                    return mm256ShufflePd(blend_dst, src, [1,0,1,1])
                elif len(src_dsts_map) == 2 and all([ t[:2] == p for t,p in zip(src_dsts_map,[ ([1],[0]) ]) ]): 
                    dst = dsts[0]
                    dnotum = [True]*len(dst.mrmap)
                    dnotum[0] = False  
                    ld_dst = mm256LoadGd(dst.pointer, dst.mrmap, isCompact=dst.isCompact, horizontal=dst.horizontal, not_using_mask=dnotum)
                    blend_dst = mm256BlendPd(src, ld_dst, [0,0,0,1])
                    src.not_using_mask[1] = True
                    return mm256ShufflePd(src, blend_dst, [1,0,0,0])
                elif len(src_dsts_map) == 2 and all([ t[:2] == p for t,p in zip(src_dsts_map,[ ([1],[1]) ]) ]): 
                    dst = dsts[0]
                    dnotum = [True]*len(dst.mrmap)
                    dnotum[1] = False  
                    ld_dst = mm256LoadGd(dst.pointer, dst.mrmap, isCompact=dst.isCompact, horizontal=dst.horizontal, not_using_mask=dnotum)
                    src.not_using_mask[1] = True
                    imm_list = [0]*dst.reglen
                    imm_list[-2] = 1
                    return mm256BlendPd(src, ld_dst, imm_list)
                elif len(src_dsts_map) == 3 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([0,1],[0,1]),([2],[2])]) ]):
                    notums = [ [True]*len(dst.mrmap) for dst in dsts[:2] ]
                    for p in [0,1]:
                        notums[0][dsts[0].mrmap.index(p)] = False
                    notums[1][dsts[1].mrmap.index(2)] = False
                    lds = [ mm256LoadGd(dst.pointer, dst.mrmap, isCompact=dst.isCompact, horizontal=dst.horizontal, not_using_mask=notum) for dst,notum in zip(dsts,notums) ]
                    src.not_using_mask[:3] = [True]*3
                    blend_dsts = mm256BlendPd(lds[0], lds[1], [0,1,0,0])
                    return mm256BlendPd(blend_dsts, src, [1,0,0,0])
                elif len(src_dsts_map) == 3 and all([ t[:2] == p for t,p in zip(src_dsts_map,[([1],[1]),([2],[0])]) ]):
                    notums = [ [True]*len(dst.mrmap) for dst in dsts[:-1] ]
                    notums[0][dsts[0].mrmap.index(1)] = False
                    notums[1][dsts[1].mrmap.index(0)] = False
                    src.not_using_mask[1:3] = [True]*2
                    lds = [ mm256LoadGd(dst.pointer, dst.mrmap, isCompact=dst.isCompact, horizontal=dst.horizontal, not_using_mask=notum) for dst,notum in zip(dsts[:-1],notums) ]
                    imm_list = [0]*dsts[0].reglen
                    imm_list[-2] = 1
                    blend0 = mm256BlendPd(src, lds[0], imm_list)
                    blend1 = mm256BlendPd(mm256SetzeroPd(), lds[1], [0,0,0,1])
                    inter_lane = mm256Permute2f128Pd(blend1, blend1, [0,0,0,0,1,0,0,0])
                    return mm256BlendPd(blend0, inter_lane, [0,1,0,0])
                else:
                    src_dsts_map = self.src_dsts_map(src, dsts_by_line)
                    raise Exception('Cannot load-replace when dst is None!')
            else:
                src_dsts_map = self.src_dsts_map(src, dsts_by_line)
                raise Exception('len(src_dsts_map) > 1: Cannot load-replace!')
        else:
            src_reg_pos, dst_reg_pos, dst = src_dsts_map[0]
            notum = [True]*len(dst.mrmap)
            for p in dst_reg_pos:
                notum[dst.mrmap.index(p)] = False  

            ld_dst = mm256LoadGd(dst.pointer, dst.mrmap, isCompact=dst.isCompact, horizontal=dst.horizontal, not_using_mask=notum)

            imm_list = [0]*dst.reglen
            for pos in dst_reg_pos:
                imm_list[dst.reglen-1-pos] = 1
            blend_dst = mm256BlendPd(mm256SetzeroPd(), ld_dst, imm_list)
            
            if src.reglen == 4 and len(src_reg_pos) == 1 and src_reg_pos[0] == tuple(range(4)): #Analogous of bcast with genLoad
                lane1, posInLane = dst_reg_pos[0] > 1, dst_reg_pos[0] % 2
                immBitList = [0,0,1,1,0,0,0,1] if lane1 else [0,0,1,0,0,0,0,0]
                dupLane = mm256Permute2f128Pd(ld_dst, ld_dst, immBitList) # Dup the lane where we can find the value
                return mm256ShufflePd(dupLane, dupLane, [posInLane]*4)
            elif src_reg_pos == dst_reg_pos:
                return blend_dst
            elif len(set([s-d for s,d in zip(src_reg_pos, dst_reg_pos)])) == 1: # shifting
                dist = src_reg_pos[0] - dst_reg_pos[0]
                if len(src.mrmap) == 1 and (all([p>1 for p in src_reg_pos+dst_reg_pos]) or all([p<2 for p in src_reg_pos+dst_reg_pos])):
                    # No cross-lane shift
                    if dist == 1:
                        load_rep = mm256UnpackloPd(mm256SetzeroPd(), blend_dst)
                    elif dist == -1:
                        load_rep = mm256UnpackhiPd(blend_dst, mm256SetzeroPd())
                    return load_rep
                if dist > 0:
                    lane_perm = mm256Permute2f128Pd(ld_dst, ld_dst, [0,0,0,0,1,0,0,0])
                    if dist == 1:
                        load_rep = mm256ShufflePd(lane_perm, blend_dst, [0,1,0,1])
                    elif dist == 2:
                        if len(dst_reg_pos) > 1:
                            load_rep = lane_perm
                        else:
                            load_rep = mm256Permute2f128Pd(blend_dst, blend_dst, [0,0,0,0,1,0,0,0])
                    elif dist == 3:
                        load_rep = mm256UnpackloPd(mm256SetzeroPd(), lane_perm)
                    return load_rep
                else:
                    lane_perm = mm256Permute2f128Pd(ld_dst, ld_dst, [1,0,0,0,0,0,0,1])
                    if dist == -1:
                        load_rep = mm256ShufflePd(blend_dst, lane_perm, [0,1,0,1])
                    elif dist == -2:
                        if len(dst_reg_pos) > 1:
                            load_rep = lane_perm
                        else:
                            load_rep = mm256Permute2f128Pd(blend_dst, blend_dst, [1,0,0,0,0,0,0,1])
                    elif dist == -3:
                        load_rep = mm256UnpackhiPd(lane_perm, mm256SetzeroPd())
                    return load_rep
            else:
                src_dsts_map = self.src_dsts_map(src, dsts_by_line)
                raise Exception('len(src_dsts_map) == 1: Cannot load-replace!')
        
    def mm256BroadcastSs(self, src, repList):
        sList = sorted(repList, key=lambda t: t[0], reverse=True)
        dst = sList[0][1]
        if dst.reglen == 8 and dst.mrmap == range(8):
            at = src.pointer.getAt()
            direct = 1 if src.pointer.getMat().size[1] > 1 else 0   # Temp solution
            lane1, posInLane = at[direct] > 3, at[direct] % 4  
            immBitList = [0,0,1,1,0,0,0,1] if lane1 else [0,0,1,0,0,0,0,0]
            dupLane = mm256Permute2f128Ps(mm256LoaduPs(dst.pointer), mm256LoaduPs(dst.pointer), immBitList) # Dup the lane where we can find the value
            return mm256ShufflePs(dupLane, dupLane, [posInLane]*4)

    def mm256LoadGs(self, src, repList, bounds):
        sList = sorted(repList, key=lambda t: t[0], reverse=True)
        dst = sList[0][1]
        if src.reglen == 8 and len(src.mrmap) == 1 and src.mrmap[0] == tuple(range(8)):
            if dst.reglen == 8: # and dst.mrmap == range(8):
                at = src.pointer.getAt()
                direct = 1 if src.pointer.getMat().size[1] > 1 else 0   # Temp solution
                lane1, posInLane = at[direct] > 3, at[direct] % 4  
                immBitList = [0,0,1,1,0,0,0,1] if lane1 else [0,0,1,0,0,0,0,0]
                dupLane = mm256Permute2f128Ps(mm256LoadGs(dst.pointer, dst.mrmap), mm256LoadGs(dst.pointer, dst.mrmap), immBitList) # Dup the lane where we can find the value
                return mm256ShufflePs(dupLane, dupLane, [posInLane]*4)
            else:
                raise Exception('Cannot load-replace!')
        else:
            raise Exception('Cannot load-replace!')
            

class AVX(ISA):
    def __init__(self, opts):
        super(AVX, self).__init__()
        self.name = "AVX"

        fp_m256d = { 'type': '__m256d' }
        fp_m256d['arith'] = [ mm256AddPd, mm256SubPd, mm256MulPd, mm256DivPd, mm256HaddPd ]
        fp_m256d['load']  = [ mm256LoaduPd, mm256MaskloadPd, mm256BroadcastSd, mm256LoadGd, asm256LoaduPd ]
        fp_m256d['misc']  = [ mm256Permute2f128Pd, mm256PermutePd, mm256ShufflePd, mm256UnpackloPd, mm256UnpackhiPd, mm256BlendPd ]
        fp_m256d['set']   = [ mm256SetzeroPd, mm256Set1Pd ]
        fp_m256d['move']  = [ ]
#         fp_m256d['store'] = [ mm256StoreuPd, mm256MaskstorePd ]
        fp_m256d['store'] = [ mm256StoreGd ]
        fp_m256d['loader'] = _Dbl4Loader()
        fp_m256d['nublac'] = _Dbl4BLAC()
        fp_m256d['storer'] = _Dbl4Storer()
        fp_m256d['loadreplacer'] = AVXLoadReplacer(opts)

        fp_m256 = { 'type': '__m256' }
        fp_m256['arith'] = [ mm256AddPs, mm256MulPs, mm256HaddPs ]
        fp_m256['load']  = [ mm256LoaduPs, mm256MaskloadPs, mm256BroadcastSs, mm256LoadGs ]
        fp_m256['misc']  = [ mm256Permute2f128Ps, mm256BlendPs, mm256ShufflePs, mm256UnpackloPs, mm256UnpackhiPs ]
        fp_m256['set']   = [ mm256SetzeroPs ]
        fp_m256['move']  = [ ]
#         fp_m256['store'] = [ mm256StoreuPs, mm256MaskstorePs ]
        fp_m256['store'] = [ mm256StoreGs ]
        fp_m256['loader'] = _Flt8Loader()
        fp_m256['nublac'] = _Flt8BLAC()
        fp_m256['storer'] = _Flt8Storer()
        fp_m256['loadreplacer'] = fp_m256d['loadreplacer']
        
        self.types = { 'fp': { ('double', 4): fp_m256d, ('float', 8): fp_m256} }
        
        self.add_func_defs = [ asm256LoaduPd, asm256StoreuPd ]