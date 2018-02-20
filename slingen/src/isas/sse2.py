'''
Created on Apr 18, 2012

@author: danieles
'''

from sympy import sympify

from src.irbase import RValue, VecAccess, VecDest, Pointer, MovStatement, Mov

from src.isas.isabase import ISA
from src.isas.sse import SSE 
# from src.isas.sse import mmSetzeroPs, mmLoadlPi, mmLoadSs, mmStoreuPs, mmMovehlPs, mmMovelhPs, \
#                             mmAddPs, mmMulPs, mmStoreSs, mmStorelPi, mmUnpackloPs, mmLoadGs, mmUnpackhiPs, mmStoreGs, mmMoveSs,\
#                             mmLoad1Ps

# from src.irbase import *
# from src.isas.isabase import *
# from src.isas.x86 import *
# from src.isas.sse import *

class mmLoaduPd(RValue, VecAccess):
    def __init__(self, pointer, zeromask=None):
        super(mmLoaduPd, self).__init__()
        self.reglen = 2
        self.mrmap = [0,1]
        self.zeromask = [0]*self.reglen
        if zeromask is not None:
            for pos in zeromask:
                self.zeromask[pos] = 1
        self.pointer = pointer

    def computeSym(self, nameList):
        p = self.pointer.computeSym(nameList)
        return [ sympify(p+'_0'), sympify(p+'_1') ] 

    def getZMask(self):
        return self.zeromask

    def unparse(self, indent):
        return indent + "_mm_loadu_pd(" + self.pointer.unparse("") + ")"

    def printInst(self, indent):
        return indent + "mmLoaduPd( " + self.pointer.printInst("") + " )"

    def __eq__(self, other):
        return isinstance(other, mmLoaduPd) and self.pointer == other.pointer
    
    def __hash__(self):
        return hash((hash("mmLoaduPd"), self.pointer.mat, self.pointer.at))

class mmLoadSd(RValue, VecAccess):
    def __init__(self, pointer, zeromask=None):
        super(mmLoadSd, self).__init__()
        self.reglen = 2
        self.mrmap = [0]
        self.zeromask = [0, 1]
        if zeromask is not None:
            for pos in zeromask: # there should at most be 1 pos == 0 here
                self.zeromask[pos] = 1
        self.pointer = pointer

    def computeSym(self, nameList):
        p = self.pointer.computeSym(nameList)
        return [ sympify(p+'_0'), sympify(0) ] 

    def getZMask(self):
        return self.zeromask
        
    def unparse(self, indent):
        return indent + "_mm_load_sd(" + self.pointer.unparse("") + ")"
    
    def printInst(self, indent):
        return indent + "mmLoadSd( " + self.pointer.printInst("") + " )"

    def __eq__(self, other):
        return isinstance(other, mmLoadSd) and self.pointer == other.pointer
    
    def __hash__(self):
        return hash((hash("mmLoadSd"), self.pointer.mat, self.pointer.at))

class mmStoreuPd(MovStatement):
    mrmap = [0,1]
    def __init__(self, src, dst):
        super(mmStoreuPd, self).__init__()
        self.dst = VecDest(dst, 2, self.mrmap) if isinstance(dst, Pointer) else VecDest(dst.pointer, 2, self.mrmap)
        self.srcs += [ src ]
#         self.slen = 2
#         self.dlen = 2
        

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
        return reglen == 2 and mrmap == mmStoreuPd.mrmap

    @staticmethod
    def getStore(src, dst):
        return mmStoreuPd(src, dst)

    def computeSym(self, nameList):
        return self.srcs[0].computeSym(nameList) 
     
    def unparse(self, indent):
        return indent + "_mm_storeu_pd(" + self.dst.unparse("") + ", " + self.srcs[0].unparse("") + ");"
    
    def printInst(self, indent):
        return indent + "mmStoreuPd( " + self.srcs[0].printInst("") + ", " + self.dst.printInst("") + " )"

class mmStoreSd(MovStatement):
    mrmap = [ 0 ]
    def __init__(self, src, dst):
        super(mmStoreSd, self).__init__()
#         self.dst = ScaDest(dst) if isinstance(dst, Pointer) else ScaDest(dst.pointer)  # I don't anything else than a pointer can get here
        self.dst = VecDest(dst, 2, self.mrmap) if isinstance(dst, Pointer) else VecDest(dst.pointer, 2, self.mrmap) 
        self.srcs += [ src ]
#         self.srcZMask = src.getZMask()
#         self.slen = 2
#         self.dlen = 1

    @staticmethod
    def canStore(reglen, mrmap, horizontal=True, isAligned=False):
        if not horizontal: return False
        return reglen == 2 and mrmap == mmStoreSd.mrmap

    @staticmethod
    def getStore(src, dst):
        return mmStoreSd(src, dst)

    def replaceRefs(self, refMap):
#         pointer = AddressOf(self.dst.replaceRefs(refMap))
#         src = self.srcs[0].replaceRefs(refMap)
#         return mmStoreSd(src, pointer)
        dst = self.dst.replaceRefs(refMap)
        src = self.srcs[0].replaceRefs(refMap)
        if isinstance(dst, VecDest):
            self.dst = dst
            self.srcs[0] = src
            return self
        if self.srcZMask != [0,1]:
            return Mov(mmMoveSd(mmSetzeroPd(), src), dst)
        return Mov(src, dst)
     
#     def replaceInLHS(self, old, new):
#         if self.dst == old:
#             return mmStoreSd(self.srcs[0], AddressOf(new))

    def computeSym(self, nameList):
        return [ self.srcs[0].computeSym(nameList)[0] ] 

    def unparse(self, indent):
        return indent + "_mm_store_sd(" + self.dst.unparse("") + ", " + self.srcs[0].unparse("") + ");"
    
    def printInst(self, indent):
        return indent + "mmStoreSd( " + self.srcs[0].printInst("") + ", " + self.dst.printInst("") + " )"

class mmSetPd(RValue):
    def __init__(self, src0, src1):
        super(mmSetPd, self).__init__()
        self.srcs += [ src0, src1 ]

    def computeSym(self, nameList):
        return [ self.srcs[1].computeSym(nameList)[0], self.srcs[0].computeSym(nameList)[0] ] 

    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [ s1ZMask[0], s0ZMask[0] ]
    
    def unparse(self, indent):
        return indent + "_mm_set_pd(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")"
    
    def printInst(self, indent):
        return indent + "mmSetPd( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mmSet1Pd(RValue):
    def __init__(self, src):
        super(mmSet1Pd, self).__init__()
        self.srcs += [ src ]

    def computeSym(self, nameList):
        sym = self.srcs[0].computeSym(nameList)[0]
        return [ sym, sym ] 

    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        return [ s0ZMask[0], s0ZMask[0] ]
    
    def unparse(self, indent):
        return indent + "_mm_set1_pd(" + self.srcs[0].unparse("") + ")"
    
    def printInst(self, indent):
        return indent + "mmSet1Pd( " + self.srcs[0].printInst("") + " )"

class mmCvtsdf64(RValue):
    def __init__(self, src):
        super(mmCvtsdf64, self).__init__()
        self.srcs += [ src ]

    def computeSym(self, nameList):
        return [ self.srcs[0].computeSym(nameList)[0] ] 
    
    def unparse(self, indent):
        return indent + "_mm_cvtsd_f64(" + self.srcs[0].unparse("") + ")"
    
    def printInst(self, indent):
        return indent + "mmCvtsdf64( " + self.srcs[0].printInst("") + " )"

class mmAddPd(RValue):
    def __init__(self, src0, src1):
        super(mmAddPd, self).__init__()
        self.srcs += [ src0, src1 ] 

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[0] + src1[0], src0[1] + src1[1] ]

    def unparse(self, indent):
        return indent + "_mm_add_pd(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mmAddPd( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mmMulPd(RValue):
    def __init__(self, src0, src1):
        super(mmMulPd, self).__init__()
        self.srcs += [ src0, src1 ]

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[0] * src1[0], src0[1] * src1[1] ]
        
    def unparse(self, indent):
        return indent + "_mm_mul_pd(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mmMulPd( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mmDivPd(RValue):
    def __init__(self, src0, src1):
        super(mmDivPd, self).__init__()
        self.srcs += [ src0, src1 ] 

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[0] / src1[0], src0[1] / src1[1] ]

    def unparse(self, indent):
        return indent + "_mm_div_pd(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mmDivPd( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mmSqrtPd(RValue):
    def __init__(self, src):
        super(mmSqrtPd, self).__init__()
        self.srcs += [ src ] 

    def unparse(self, indent):
        return indent + "_mm_sqrt_pd(" + self.srcs[0].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mmSqrtPd( " + self.srcs[0].printInst("") + " )"

class mmUnpackloPd(RValue):
    def __init__(self, src0, src1):
        super(mmUnpackloPd, self).__init__()
        self.srcs += [ src0, src1 ]

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[0], src1[0] ]

    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [ s0ZMask[0], s1ZMask[0] ]

    def unparse(self, indent):
        return indent + "_mm_unpacklo_pd(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mmUnpackloPd( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mmUnpackhiPd(RValue):
    def __init__(self, src0, src1):
        super(mmUnpackhiPd, self).__init__()
        self.srcs += [ src0, src1 ]

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[1], src1[1] ]

    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [ s0ZMask[1], s1ZMask[1] ]
        
    def unparse(self, indent):
        return indent + "_mm_unpackhi_pd(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mmUnpackhiPd( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mmShufflePd(RValue):
    def __init__(self, src0, src1, immTuple):
        super(mmShufflePd, self).__init__()
        self.srcs += [ src0, src1 ]
        self.immTuple = immTuple
        self.imm = (int(immTuple[0]) << 1) | int(immTuple[1])

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[self.immTuple[1]], src1[self.immTuple[0]] ]
    
    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [ s0ZMask[self.immTuple[1]], s1ZMask[self.immTuple[0]] ]

    def unparse(self, indent):
        return indent + "_mm_shuffle_pd(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ", " + str(self.imm) + ")" 

    def printInst(self, indent):
        return indent + "mmShufflePd( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + ", " + str(self.immTuple) + " )"

class mmMoveSd(RValue):
    def __init__(self, src0, src1):
        super(mmMoveSd, self).__init__()
        self.srcs += [ src0, src1 ]

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src1[0], src0[1] ]
    
    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [ s1ZMask[0], s0ZMask[1] ]

    def unparse(self, indent):
        return indent + "_mm_move_sd(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mmMoveSd( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mmSetzeroPd(RValue):
    def __init__(self):
        super(mmSetzeroPd, self).__init__()

    def computeSym(self, nameList):
        return [ sympify(0), sympify(0) ]
        
    def unparse(self, indent):
        return indent + "_mm_setzero_pd()" 

    def printInst(self, indent):
        return indent + "mmSetzeroPd()"

class mmBslliSi128(RValue):
    ''' Shift vector left by imm elements. '''
    def __init__(self, src, imm):
        super(mmBslliSi128, self).__init__()
        self.srcs += [ src ]
        self.imm = imm

    def computeSym(self, nameList):
        src = self.srcs[0].computeSym(nameList)
        if self.imm >= 4:
            res = [ '0' ]*4
        else:
            res = src[self.imm:]
            res = res + ['0']*(4-len(res))
        return res

    def getZMask(self):
        sZMask = self.srcs[0].getZMask()
        if self.imm >= 4:
            res = [ 1 ]*4
        else:
            res = sZMask[self.imm:]
            res = res + [ 1 ]*(4-len(res))
        return res

    def unparse(self, indent):
        s = '_mm_castps_si128(%s)' % self.srcs[0].unparse('')
        return '%s_mm_castsi128_ps(_mm_bslli_si128(%s, %d))' % (indent, s, 4*self.imm) 

    def printInst(self, indent):
        return "%smmBslliSi128( %s, %d )" % (indent, self.srcs[0].printInst(''), self.imm)

class mmBsrliSi128(RValue):
    ''' Shift vector right by imm elements. '''
    def __init__(self, src, imm):
        super(mmBsrliSi128, self).__init__()
        self.srcs += [ src ]
        self.imm = imm

    def computeSym(self, nameList):
        src = self.srcs[0].computeSym(nameList)
        if self.imm >= 4:
            res = [ '0' ]*4
        else:
            res = src[:(4-self.imm)]
            res = ['0']*(4-len(res)) + res
        return res

    def getZMask(self):
        sZMask = self.srcs[0].getZMask()
        if self.imm >= 4:
            res = [ 1 ]*4
        else:
            res = sZMask[:(4-self.imm)]
            res = [ 1 ]*(4-len(res)) + res
        return res

    def unparse(self, indent):
        s = '_mm_castps_si128(%s)' % self.srcs[0].unparse('')
        return '%s_mm_castsi128_ps(_mm_bsrli_si128(%s, %d))' % (indent, s, 4*self.imm) 

    def printInst(self, indent):
        return "%smmBsrliSi128( %s, %d )" % (indent, self.srcs[0].printInst(''), self.imm)
          
class SSE2(ISA):
    def __init__(self, opts):
        super(SSE2, self).__init__()
#         self.nu = [ 2 ]
#         self.vectorize = True
        self.name = "SSE2"
        
        sse = SSE(opts)
        
        fp_m128 = { 'type': '__m128' }
        fp_m128['arith']  = []
        fp_m128['load']   = []
        fp_m128['misc']   = [mmBslliSi128, mmBsrliSi128]
        fp_m128['cvt']    = []
        fp_m128['set']    = []
        fp_m128['move']   = []
        fp_m128['store']  = []
        
        fp_m128d = { 'type': '__m128d' }
        fp_m128d['arith']  = [ mmAddPd, mmMulPd ]
        fp_m128d['load']   = [ mmLoaduPd, mmLoadSd ]
        fp_m128d['misc']   = [ mmUnpackhiPd, mmUnpackloPd, mmShufflePd ]
        fp_m128d['cvt']    = [ mmCvtsdf64 ]
        fp_m128d['set']    = [ mmSetPd, mmSet1Pd, mmSetzeroPd ]
        fp_m128d['move']   = [ mmMoveSd ]
        fp_m128d['store']  = [ mmStoreuPd, mmStoreSd ]
        
        self.updateType(fp_m128, sse.types['fp'][('float',4)], ['arith', 'load', 'misc', 'cvt', 'set', 'move', 'store'])
        self.types = { 'fp': { ('float', 4): fp_m128, ('double', 2): fp_m128d } }

        