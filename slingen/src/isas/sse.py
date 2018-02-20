'''
Created on Apr 18, 2012

@author: danieles
'''

from sympy import sympify

from src.binding import getReference
from src.irbase import RValue, VecAccess, VecDest, Pointer, PointerCast, MovStatement, Mov, icode, DebugPrint
from src.abstractint import AbstractElement, IntervalCongruenceReductionAnalysis
from src.isas.isabase import ISA

# from src.isas.x86 import x86

# from src.irbase import *
# from src.isas.isabase import *
# from src.isas.x86 import *

class mmLoadGs(RValue, VecAccess):
    ''' Wrapper of a vector load instruction.
        
        Useful when we want to represent a composite load instruction as a single logical instruction and then have it
        easily replaced by a scalar during scalar replacement.
        '''
    def __init__(self, pointer, mrmap, isCompact=False, isCorner=True, horizontal=True, zeromask=[]):
        super(mmLoadGs, self).__init__()
        self.pointer = pointer
        self.mrmap = mrmap
        self.isCompact = isCompact
        self.isCorner = isCorner
        self.horizontal = horizontal
        self.orientation = 'horizontal' if horizontal else 'vertical'
        self.zeromask = zeromask
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
            if mrmap == [(0, 1, 2, 3)]:
                content = mmLoad1Ps(pointer, zeromask)
            elif mrmap[0] == 0:
                content = mmLoadSs(pointer, zeromask)
            else:
                zm_i = [0] if mrmap[0] in zeromask else []
                ei = mmLoadSs(pointer, zm_i)
                pos = 4*[1]
                pos[mrmap[0]] = 0
                pos.reverse()
                content = mmShufflePs(ei, ei, tuple(pos))
        elif mrmap == [0, 1]:
            if horizontal or isCompact:
                content = mmLoadlPi(mmSetzeroPs(), PointerCast("__m64", pointer), zeromask)
            else:
                zm0 = [0] if 0 in zeromask else [] # Used to build the zmask in mmUnpackloPs
                zm1 = [0] if 1 in zeromask else [] #
                pointer1 = Pointer((pointer.mat, (pointer.at[0] + 1, pointer.at[1])))
                e0 = mmLoadSs(pointer, zm0)
                e1 = mmLoadSs(pointer1, zm1)
                content = mmUnpackloPs(e0, e1)
        elif mrmap == [0, 1, 2]:
            if horizontal or isCompact:
                zm0_1 = []
                zm2 = []
                for el in zeromask:
                    if el < 2:
                        zm0_1.append(el)
                    else:
                        zm2.append(el - 2)
                pointer2 = Pointer((pointer.mat, (pointer.at[0], pointer.at[1] + 2)))
                v0_1 = mmLoadlPi(mmSetzeroPs(), PointerCast("__m64", pointer), zm0_1)
                e2 = mmLoadSs(pointer2, zm2)
                content = mmShufflePs(v0_1, e2, (1,0,1,0))
            else:
                ps = [pointer] + [Pointer((pointer.mat, (pointer.at[0] + i, pointer.at[1]))) for i in range(1, 3)]
                zms = [[0] if i in zeromask else [] for i in range(3)]
                es = [mmLoadSs(p, zm) for p, zm in zip(ps, zms)]
                content = mmShufflePs(mmUnpackloPs(es[0], es[1]), es[2], (1,0,1,0))
        elif mrmap == [0, 1, 2, 3]:
            if horizontal or isCompact:
                content = mmLoaduPs(pointer, zeromask)
            else:
                ps = [pointer] + [Pointer((pointer.mat, (pointer.at[0] + i, pointer.at[1]))) for i in range(1, 4)]
                zms = [[0] if i in zeromask else [] for i in range(4)]
                es = [mmLoadSs(p, zm) for p, zm in zip(ps, zms)]
                content = mmShufflePs(mmUnpackloPs(es[0], es[1]), mmUnpackloPs(es[2], es[3]), (1,0,1,0))
        elif mrmap == [1, 2]:
            if horizontal or isCompact:
                v1_2 = mmLoadlPi(mmSetzeroPs(), PointerCast("__m64", pointer), zeromask)
                content = mmShufflePs(v1_2, v1_2, (2,1,0,2))
        elif mrmap == [2, 3]:
            if horizontal or isCompact:
                content = mmLoadhPi(mmSetzeroPs(), PointerCast("__m64", pointer), zeromask)
        elif mrmap == [1, 2, 3]:
            if horizontal or isCompact:
                zm1 = []
                zm2_3 = []
                for el in zeromask:
                    if el == 1:
                        zm1.append(0)
                    elif el > 1:
                        zm2.append(el)
                pointer2 = Pointer((pointer.mat, (pointer.at[0], pointer.at[1] + 1)))
                e1 = mmLoadSs(pointer, zm1)
                v2_3 = mmLoadhPi(mmSetzeroPs(), PointerCast("__m64", pointer2), zm2_3)
                content = mmShufflePs(e1, v2_3, (3,2,0,1))

        if content is None:
            raise ValueError('mmLoadGs does not support mrmap %s with %s layout yet' % (str(mrmap), 'horizontal' if horizontal else 'vertical'))
        return content
    
    def computeSym(self, nameList):
        return self.content.computeSym(self, nameList)
    
    def getZMask(self):
        return self.content.getZMask()
    
    def unparse(self, indent):
        content = self.content
        if self.analysis is not None and isinstance(self.analysis, IntervalCongruenceReductionAnalysis):
            content.env = self.env
            self.analysis.propagateEnvToSrcs(content)
            content = content.align(self.analysis)
        return content.unparse(indent)

    def setIterSet(self, indices, iterSet):
        super(mmLoadGs, self).setIterSet(indices, iterSet)
        self.setSpaceReadMap(indices, iterSet)
        
    def printInst(self, indent):
#         return 'mmLoadGs(%s, %s, %s)' % (str(self.mrmap), self.orientation, self.content.printInst(indent))
        return 'mmLoadGs(%r, %r, %s)' % (self.pointer, self.mrmap, self.orientation)
    
    def align(self, analysis):
        self.analysis = analysis
        return self
    
    def __eq__(self, other):
        return isinstance(other, VecAccess) and self.reglen == other.reglen and self.pointer == other.pointer and self.mrmap == other.mrmap and self.horizontal == other.horizontal
    
    def __hash__(self):
        return hash((hash('mmLoadGs'), self.pointer.mat, self.pointer.at, str(self.mrmap), self.orientation))

class mmStoreGs(MovStatement):
    '''Wrapper of a vector store instruction.
        
        Useful when we want to represent a composite store instruction as a single logical instruction and then have it
        easily replaced by a scalar during scalar replacement.
        '''
    def __init__(self, src, dst, mrmap, isCompact=False, isCorner=True, horizontal=True):
        super(mmStoreGs, self).__init__()
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
                content = [mmStoreSsNoZeromask(src, dst)]
            else:
                ei = mmShufflePs(src, src, tuple(4*[mrmap[0]]))
                content = [mmStoreSsNoZeromask(ei, dst)]
        elif mrmap == [0, 1]:
            if horizontal or isCompact:
                content = [mmStorelPi(src, PointerCast("__m64", dst))]
            else:
                p0 = dst
                p1 = Pointer((dst.mat, (dst.at[0] + 1, dst.at[1])))
                e1 = mmShufflePs(src, src, (2,2,2,1))
                content = [mmStoreSsNoZeromask(src, p0), mmStoreSsNoZeromask(e1, p1)]
        elif mrmap == [0, 1, 2]:
            if horizontal or isCompact:
                p0 = dst
                p2 = Pointer((dst.mat, (dst.at[0], dst.at[1] + 2)))
                e2 = mmShufflePs(src, src, (3,3,3,2))
                content = [mmStorelPi(src, PointerCast("__m64", p0)), mmStoreSsNoZeromask(e2, p2)]
            else:
                ps = [dst, Pointer((dst.mat, (dst.at[0] + 1, dst.at[1]))), Pointer((dst.mat, (dst.at[0] + 2, dst.at[1])))]
                e1 = mmShufflePs(src, src, (3,3,3,1))
                e2 = mmShufflePs(src, src, (3,3,3,2))
                content = [mmStoreSsNoZeromask(src, ps[0]), mmStoreSsNoZeromask(e1, ps[1]), mmStoreSsNoZeromask(e2, ps[2])]
        elif mrmap == [0, 1, 2, 3]:
            if horizontal or isCompact:
                content = [mmStoreuPs(src, dst)]
            else:
                ps = [dst] + [Pointer((dst.mat, (dst.at[0] + i, dst.at[1]))) for i in range(1, 4)]
                es = [mmShufflePs(src, src, (3,3,3,i)) for i in range(1,4)]
                content = [mmStoreSsNoZeromask(src, ps[0])] + [mmStoreSsNoZeromask(es[i-1], ps[i]) for i in range(1,4)]
        elif mrmap == [1, 2]:
            if horizontal or isCompact:
                v1_2 = mmShufflePs(src, src, (3,3,2,1))
                content = [mmStorelPi(v1_2, PointerCast("__m64", dst))]
        elif mrmap == [2, 3]:
            if horizontal or isCompact:
                content = [mmStorehPi(src, PointerCast("__m64", dst))]
        elif mrmap == [1, 2, 3]:
            if horizontal or isCompact:
                pointer2 = Pointer((dst.mat, (dst.at[0], dst.at[1] + 1)))
                e1 = mmShufflePs(src, src, (1,1,1,1))
                content = [mmStoreSsNoZeromask(e1, dst), mmStorehPi(src, PointerCast("__m64", pointer2))]
        
        if content is None:
            raise ValueError('mmStoreGs does not support mrmap %s with %s layout yet' % (str(mrmap), 'horizontal' if horizontal else 'vertical'))

#         content.append(DebugPrint(["\"Storing "+getReference(icode, dst.mat).physLayout.name+"\"", "\" [ \"", str(dst.at[0]), "\" , \"", str(dst.at[1]), "\" ] at line \"", "__LINE__"]));
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
        return mmStoreGs(src, dst, mrmap, dst.isCompact, dst.isCorner, dst.horizontal)
    
    def computeSym(self, nameList):
        return self.srcs[0].computeSym(nameList)[:len(self.mrmap)]
    
    def unparse(self, indent):
        content = self.content
        if self.analysis is not None and isinstance(self.analysis, IntervalCongruenceReductionAnalysis):
            for instr in content:
                instr.env = self.env
                self.analysis.propagateEnvToSrcs(instr)
            content = [instr.align(self.analysis) for instr in content]
        return '\n'.join(instr.unparse(indent) for instr in content)
    
    def printInst(self, indent):
#         return 'mmStoreGs(%s, %s, %s)' % (str(self.mrmap), self.orientation, ','.join([instr.printInst(indent) for instr in self._content]))
        return 'mmStoreGs(%r, %r, %r, %s)' % (self.dst, self.srcs[0], self.mrmap, self.orientation)
    
    def align(self, analysis):
        self.analysis = analysis
        return self

class mmLoaduPs(RValue, VecAccess):
    def __init__(self, pointer, zeromask=None):
        super(mmLoaduPs, self).__init__()
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
        return indent + "_mm_loadu_ps(" + self.pointer.unparse("") + ")"
    
    def printInst(self, indent):
        return indent + "mmLoaduPs( " + self.pointer.printInst("") + " )"
    
    def align(self, analysis):
        analysis.env = self.env # restore the analysis env that corresponds to this instruction
        if analysis.congruenceAnalysis.lessEqual(analysis.evaluateExpr(sympify(self.pointer.ref.physLayout.name) + getReference(icode, self.pointer.mat).getLinIdx(self.pointer.at))[1], AbstractElement((0, self.reglen))):
            return mmLoadPs(self.pointer, [pos for pos, zm in enumerate(self.zeromask) if zm == 1])
        else:
            return self

    def __eq__(self, other):
        return isinstance(other, mmLoaduPs) and self.pointer == other.pointer
    
    def __hash__(self):
        return hash((hash("mmLoaduPs"), self.pointer.mat, self.pointer.at))

class mmLoadPs(RValue, VecAccess):
    ''' Aligned load of a 128bit vector. '''
    def __init__(self, pointer, zeromask=None):
        super(mmLoadPs, self).__init__()
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
        return indent + "_mm_load_ps(" + self.pointer.unparse("") + ")"
    
    def printInst(self, indent):
        return indent + "mmLoadPs( " + self.pointer.printInst("") + " )"

    def __eq__(self, other):
        return isinstance(other, mmLoadPs) and self.pointer == other.pointer
    
    def __hash__(self):
        return hash((hash("mmLoadPs"), self.pointer.mat, self.pointer.at))
    
class mmLoad1Ps(RValue, VecAccess):
    def __init__(self, pointer, zeromask=None):
        super(mmLoad1Ps, self).__init__()
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
        return indent + "_mm_load1_ps(" + self.pointer.unparse("") + ")"
    
    def printInst(self, indent):
        return indent + "mmLoad1Ps( " + self.pointer.printInst("") + " )"

    def __eq__(self, other):
        return isinstance(other, mmLoad1Ps) and self.pointer == other.pointer
    
    def __hash__(self):
        return hash((hash("mmLoad1Ps"), self.pointer.mat, self.pointer.at))

class mmLoadSs(RValue, VecAccess):
    def __init__(self, pointer, zeromask=None):
        super(mmLoadSs, self).__init__()
        self.reglen = 4
        self.mrmap = [0]
        self.zeromask = [0] + [1]*3
        if zeromask is not None:
            for pos in zeromask: # there should at most be 1 pos == 0 here
                self.zeromask[pos] = 1
        self.pointer = pointer

    def computeSym(self, nameList):
        p = self.pointer.computeSym(nameList)
        return [ sympify(p+'_0'), sympify(0), sympify(0), sympify(0) ] 

    def getZMask(self):
        return self.zeromask
        
    def unparse(self, indent):
        return indent + "_mm_load_ss(" + self.pointer.unparse("") + ")"
    
    def printInst(self, indent):
        return indent + "mmLoadSs( " + self.pointer.printInst("") + " )"

    def __eq__(self, other):
        return isinstance(other, mmLoadSs) and self.pointer == other.pointer
    
    def __hash__(self):
        return hash((hash("mmLoadSs"), self.pointer.mat, self.pointer.at))

class mmLoadlPi(RValue, VecAccess):
    '''Load 2 single-precision (32-bit) floating-point elements from memory into the lower 2 elements of dst 
    and copy the upper 2 elements from a to dst.
    '''
    def __init__(self, src, pointer, zeromask=None):
        super(mmLoadlPi, self).__init__()
        self.reglen = 4
        self.mrmap = [0,1]
        self.zeromask = [0]*self.reglen
        if zeromask is not None:
            for pos in zeromask: 
                self.zeromask[pos] = 1
        self.srcs += [ src ]
        self.pointer = pointer

    def computeSym(self, nameList):
        p = self.pointer.computeSym(nameList)
        src = self.srcs[0].computeSym(nameList)
        return [ sympify(p+'_0'), sympify(p+'_1'), src[2], src[3] ] 

    def getZMask(self):
        return self.zeromask
        
    def unparse(self, indent):
        return indent + "_mm_loadl_pi(" + self.srcs[0].unparse("") + ", " + self.pointer.unparse("") + ")"
    
    def printInst(self, indent):
        return indent + "mmLoadlPi( " + self.srcs[0].printInst("") + ", " + self.pointer.printInst("") + " )"

    def __eq__(self, other):
        return isinstance(other, mmLoadlPi) and self.pointer == other.pointer
    
    def __hash__(self):
        return hash((hash("mmLoadlPi"), self.pointer.mat, self.pointer.at))

class mmLoadhPi(RValue, VecAccess):
    def __init__(self, src, pointer, zeromask=None):
        super(mmLoadhPi, self).__init__()
        self.reglen = 4
        self.mrmap = [2,3]
        self.zeromask = [0]*self.reglen
        if zeromask is not None:
            for pos in zeromask: 
                self.zeromask[pos] = 1
        self.srcs += [ src ]
        self.pointer = pointer

    def computeSym(self, nameList):
        p = self.pointer.computeSym(nameList)
        src = self.srcs[0].computeSym(nameList)
        return [ src[0], src[1], sympify(p+'_2'), sympify(p+'_3') ] 

    def getZMask(self):
        return self.zeromask
        
    def unparse(self, indent):
        return indent + "_mm_loadh_pi(" + self.srcs[0].unparse("") + ", " + self.pointer.unparse("") + ")"
    
    def printInst(self, indent):
        return indent + "mmLoadhPi( " + self.srcs[0].printInst("") + ", " + self.pointer.printInst("") + " )"

    def __eq__(self, other):
        return isinstance(other, mmLoadhPi) and self.pointer == other.pointer
    
    def __hash__(self):
        return hash((hash("mmLoadhPi"), self.pointer.mat, self.pointer.at))

class mmAddPs(RValue):
    def __init__(self, src0, src1):
        super(mmAddPs, self).__init__()
        self.srcs += [ src0, src1 ] 

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[0] + src1[0], src0[1] + src1[1], src0[2] + src1[2], src0[3] + src1[3] ]

    def unparse(self, indent):
        return indent + "_mm_add_ps(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mmAddPs( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mmMulPs(RValue):
    def __init__(self, src0, src1):
        super(mmMulPs, self).__init__()
        self.srcs += [ src0, src1 ] 

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[0] * src1[0], src0[1] * src1[1], src0[2] * src1[2], src0[3] * src1[3] ]

    def unparse(self, indent):
        return indent + "_mm_mul_ps(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mmMulPs( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mmHaddPs(RValue):
    def __init__(self, src0, src1):
        super(mmHaddPs, self).__init__()
        self.srcs += [ src0, src1 ]

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[0]+src0[1], src0[2]+src0[3], src1[0]+src1[1], src1[2]+src1[3] ]
        
    def unparse(self, indent):
        return indent + "_mm_hadd_ps(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mmHaddPs( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mmUnpackloPs(RValue):
    def __init__(self, src0, src1):
        super(mmUnpackloPs, self).__init__()
        self.srcs += [ src0, src1 ]

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[0], src1[0], src0[1], src1[1] ]

    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [ s0ZMask[0], s1ZMask[0], s0ZMask[1], s1ZMask[1] ]

    def unparse(self, indent):
        return indent + "_mm_unpacklo_ps(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mmUnpackloPs( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mmUnpackhiPs(RValue):
    def __init__(self, src0, src1):
        super(mmUnpackhiPs, self).__init__()
        self.srcs += [ src0, src1 ]

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[2], src1[2], src0[3], src1[3] ]

    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [ s0ZMask[2], s1ZMask[2], s0ZMask[3], s1ZMask[3] ]
        
    def unparse(self, indent):
        return indent + "_mm_unpackhi_ps(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mmUnpackhiPs( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mmShufflePs(RValue):
    def __init__(self, src0, src1, immTuple):
        super(mmShufflePs, self).__init__()
        self.srcs += [ src0, src1 ]
        self.immTuple = immTuple

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[self.immTuple[3]], src0[self.immTuple[2]], src1[self.immTuple[1]], src1[self.immTuple[0]] ]
    
    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [ s0ZMask[self.immTuple[3]], s0ZMask[self.immTuple[2]], s1ZMask[self.immTuple[1]], s1ZMask[self.immTuple[0]] ]
        
    def unparse(self, indent):
        return indent + "_mm_shuffle_ps(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ", _MM_SHUFFLE" + str(self.immTuple) + ")" 

    def printInst(self, indent):
        return indent + "mmShufflePs( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + ", " + str(self.immTuple) + " )"

class mmMovelhPs(RValue):
    def __init__(self, src0, src1):
        super(mmMovelhPs, self).__init__()
        self.srcs += [ src0, src1 ]

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src1[0], src1[1], src0[0], src0[1] ]

    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [ s1ZMask[0], s1ZMask[1], s0ZMask[0], s0ZMask[1] ]
        
    def unparse(self, indent):
        return indent + "_mm_movelh_ps(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mmMovelhPs( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mmMovehlPs(RValue):
    def __init__(self, src0, src1):
        super(mmMovehlPs, self).__init__()
        self.srcs += [ src0, src1 ]

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src1[2], src1[3], src0[2], src0[3] ]

    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [ s1ZMask[2], s1ZMask[3], s0ZMask[2], s0ZMask[3] ]
        
    def unparse(self, indent):
        return indent + "_mm_movehl_ps(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mmMovehlPs( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mmMoveSs(RValue):
    def __init__(self, src0, src1):
        super(mmMoveSs, self).__init__()
        self.srcs += [ src0, src1 ]

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src1[0], src0[1], src0[2], src0[3] ]

    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [ s1ZMask[0], s0ZMask[1], s0ZMask[2], s0ZMask[3] ]
        
    def unparse(self, indent):
        return indent + "_mm_move_ss(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mmMoveSs( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mmSetPs(RValue):
    def __init__(self, src0, src1, src2, src3):
        super(mmSetPs, self).__init__()
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
        return indent + "_mm_set_ps(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ", " + self.srcs[2].unparse("") + ", " + self.srcs[3].unparse("") + ")"
    
    def printInst(self, indent):
        return indent + "mmSetPs( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + self.srcs[2].printInst("") + ", " + self.srcs[3].printInst("") + " )"

class mmSet1Ps(RValue):
    def __init__(self, src):
        super(mmSet1Ps, self).__init__()
        self.srcs += [ src ]

    def computeSym(self, nameList):
        sym = self.srcs[0].computeSym(nameList)[0]
        return [ sym, sym, sym, sym ] 

    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        return [ s0ZMask[0], s0ZMask[0], s0ZMask[0], s0ZMask[0] ]
    
    def unparse(self, indent):
        return indent + "_mm_set1_ps(" + self.srcs[0].unparse("") + ")"
    
    def printInst(self, indent):
        return indent + "mmSet1Ps( " + self.srcs[0].printInst("") + " )"

class mmSetzeroPs(RValue):
    def __init__(self):
        super(mmSetzeroPs, self).__init__()

    def computeSym(self, nameList):
        return [ sympify(0), sympify(0), sympify(0), sympify(0) ]
        
    def unparse(self, indent):
        return indent + "_mm_setzero_ps()" 

    def printInst(self, indent):
        return indent + "mmSetzeroPs()"

class mmCvtssf32(RValue):
    def __init__(self, src):
        super(mmCvtssf32, self).__init__()
        self.srcs += [ src ]

    def computeSym(self, nameList):
        return [ self.srcs[0].computeSym(nameList)[0] ] 
    
    def unparse(self, indent):
        return indent + "_mm_cvtss_f32(" + self.srcs[0].unparse("") + ")"
    
    def printInst(self, indent):
        return indent + "mmCvtssf32( " + self.srcs[0].printInst("") + " )"

class mmStoreuPs(MovStatement):
    mrmap = [0,1,2,3] # static definition of the mem-reg mapping imposed by the store
    def __init__(self, src, dst):
        super(mmStoreuPs, self).__init__()
        dstpointer = dst if isinstance(dst, Pointer) else dst.pointer
        # silent introduction of VecDest operator
        self.dst = VecDest(dstpointer, 4, self.mrmap)
        self.srcs += [ src ]
        self.pointer = dstpointer

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
        return reglen == 4 and mrmap == mmStoreuPs.mrmap

    @staticmethod
    def getStore(src, dst):
        return mmStoreuPs(src, dst)

    def computeSym(self, nameList):
        return self.srcs[0].computeSym(nameList) 
     
    def unparse(self, indent):
        return indent + "_mm_storeu_ps(" + self.dst.unparse("") + ", " + self.srcs[0].unparse("") + ");"
    
    def printInst(self, indent):
        return indent + "mmStoreuPs( " + self.srcs[0].printInst("") + ", " + self.dst.printInst("") + " )"
    
    def align(self, analysis):
        for i, source in enumerate(self.srcs):
            self.srcs[i] = source.align(analysis)
        analysis.env = self.env # restore the analysis env that corresponds to this instruction
        if analysis.congruenceAnalysis.lessEqual(analysis.evaluateExpr(sympify(self.dst.pointer.ref.physLayout.name) + getReference(icode, self.dst.pointer.mat).getLinIdx(self.dst.pointer.at))[1], AbstractElement((0, self.dst.reglen))):
            return mmStorePs(self.srcs[0], self.dst.pointer)
        else:
            return self

class mmStorePs(MovStatement):
    mrmap = [0,1,2,3] # static definition of the mem-reg mapping imposed by the store
    def __init__(self, src, dst):
        super(mmStorePs, self).__init__()
        # silent introduction of VecDest operator
        self.dst = VecDest(dst, 4, self.mrmap, isAligned=True) if isinstance(dst, Pointer) else VecDest(dst.pointer, 4, self.mrmap, isAligned=True)
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
        return reglen == 4 and mrmap == mmStoreuPs.mrmap and isAligned

    @staticmethod
    def getStore(src, dst):
        return mmStorePs(src, dst)

    def computeSym(self, nameList):
        return self.srcs[0].computeSym(nameList) 
     
    def unparse(self, indent):
        return indent + "_mm_store_ps(" + self.dst.unparse("") + ", " + self.srcs[0].unparse("") + ");"
    
    def printInst(self, indent):
        return indent + "mmStorePs( " + self.srcs[0].printInst("") + ", " + self.dst.printInst("") + " )"
    
class mmStoreSs(MovStatement):
    mrmap = [0]
    def __init__(self, src, dst):
        super(mmStoreSs, self).__init__()
        self.dst = VecDest(dst, 4, self.mrmap) if isinstance(dst, Pointer) else VecDest(dst.pointer, 4, self.mrmap) # When passing VecAccess in ScaRep
        self.srcs += [ src ]
        self.srcZMask = src.getZMask()

    @staticmethod
    def canStore(reglen, mrmap, horizontal=True, isAligned=False):
        if not horizontal: return False
        return reglen == 4 and mrmap == mmStoreSs.mrmap

    @staticmethod
    def getStore(src, dst):
        return mmStoreSs(src, dst)
     
    def replaceRefs(self, refMap):
        dst = self.dst.replaceRefs(refMap)
        src = self.srcs[0].replaceRefs(refMap)
        if isinstance(dst, VecDest):
            self.dst = dst
            self.srcs[0] = src
            return self
        if self.srcZMask != [0,1,1,1]:
            return Mov(mmMoveSs(mmSetzeroPs(), src), dst)
        return Mov(src, dst)
     
    def computeSym(self, nameList):
        return [ self.srcs[0].computeSym(nameList)[0] ] 

    def unparse(self, indent):
        return indent + "_mm_store_ss(" + self.dst.unparse("") + ", " + self.srcs[0].unparse("") + ");"
    
    def printInst(self, indent):
        return indent + "mmStoreSs( " + self.srcs[0].printInst("") + ", " + self.dst.printInst("") + " )"

class mmStoreSsNoZeromask(MovStatement):
    ''' This class can and must be used instead of mmStoreSs by generic store instructions. '''
    mrmap = [0]
    def __init__(self, src, dst):
        super(mmStoreSsNoZeromask, self).__init__()
        self.dst = VecDest(dst, 4, self.mrmap) if isinstance(dst, Pointer) else VecDest(dst.pointer, 4, self.mrmap) # When passing VecAccess in ScaRep
        self.srcs += [ src ]
#         self.srcZMask = src.getZMask()

    @staticmethod
    def canStore(reglen, mrmap, horizontal=True, isAligned=False):
        if not horizontal: return False
        return reglen == 4 and mrmap == mmStoreSs.mrmap

    @staticmethod
    def getStore(src, dst):
        return mmStoreSsNoZeromask(src, dst)
     
    def replaceRefs(self, refMap):
        dst = self.dst.replaceRefs(refMap)
        src = self.srcs[0].replaceRefs(refMap)
        if isinstance(dst, VecDest):
            self.dst = dst
            self.srcs[0] = src
            return self
#         if self.srcZMask != [0,1,1,1]:
#             return Mov(mmMoveSs(mmSetzeroPs(), src), dst)
        return Mov(src, dst)
     
    def computeSym(self, nameList):
        return [ self.srcs[0].computeSym(nameList)[0] ] 

    def unparse(self, indent):
        return indent + "_mm_store_ss(" + self.dst.unparse("") + ", " + self.srcs[0].unparse("") + ");"
    
    def printInst(self, indent):
        return indent + "mmStoreSsNoZeromask( " + self.srcs[0].printInst("") + ", " + self.dst.printInst("") + " )"

class mmStorelPi(MovStatement):
    mrmap = [0,1]
    def __init__(self, src, dst):
        super(mmStorelPi, self).__init__()
        self.dst = VecDest(dst, 4, self.mrmap) if isinstance(dst, Pointer) else VecDest(dst.pointer, 4, self.mrmap) 
        self.srcs += [ src ]
 
    @staticmethod
    def canStore(reglen, mrmap, horizontal=True, isAligned=False):
        if not horizontal: return False
        return reglen == 4 and mrmap == mmStorelPi.mrmap

    @staticmethod
    def getStore(src, dst):
        return mmStorelPi(src, dst)
     
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
        return [ src[0], src[1] ] 
 
    def unparse(self, indent):
        return indent + "_mm_storel_pi(" + self.dst.unparse("") + ", " + self.srcs[0].unparse("") + ");"
     
    def printInst(self, indent):
        return indent + "mmStorelPi( " + self.srcs[0].printInst("") + ", " + self.dst.printInst("") + " )"

class mmStorehPi(MovStatement):
    mrmap = [2,3]
    def __init__(self, src, dst):
        super(mmStorehPi, self).__init__()
        self.dst = VecDest(dst, 4, self.mrmap) if isinstance(dst, Pointer) else VecDest(dst.pointer, 4, self.mrmap) 
        self.srcs += [ src ]
 
    @staticmethod
    def canStore(reglen, mrmap, horizontal=True, isAligned=False):
        if not horizontal: return False
        return reglen == 4 and mrmap == mmStorehPi.mrmap

    @staticmethod
    def getStore(src, dst):
        return mmStorehPi(src, dst)
     
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
        return [ src[2], src[3] ] 
 
    def unparse(self, indent):
        return indent + "_mm_storeh_pi(" + self.dst.unparse("") + ", " + self.srcs[0].unparse("") + ");"
     
    def printInst(self, indent):
        return indent + "mmStorehPi( " + self.srcs[0].printInst("") + ", " + self.dst.printInst("") + " )"
    
class SSE(ISA):
    def __init__(self, opts):
        super(SSE, self).__init__()

        self.name = "SSE"
        
        fp_m128 = { 'type': '__m128' }
        fp_m128['arith']  = [ mmAddPs, mmMulPs ]
        fp_m128['load']   = [ mmLoadPs, mmLoaduPs, mmLoad1Ps, mmLoadSs, mmLoadlPi, mmLoadhPi, mmLoadGs ]
        fp_m128['misc']   = [ mmUnpackloPs, mmUnpackhiPs, mmShufflePs ]
        fp_m128['cvt']    = [ mmCvtssf32 ]
        fp_m128['set']    = [ mmSetPs, mmSet1Ps, mmSetzeroPs ]
        fp_m128['move']   = [ mmMovelhPs, mmMovehlPs, mmMoveSs ]
        fp_m128['store']  = [ mmStoreGs ]

        self.types = { 'fp': { ('float', 4): fp_m128 } }