'''
Created on Apr 18, 2012

@author: danieles
'''

from sympy import sympify

from src.irbase import RValue, VecAccess, Pointer, AddressOf, Comment, sa
    
from src.isas.isabase import ISA, Loader, Storer, LoadReplacer
from src.isas.sse import mmLoaduPs, mmCvtssf32, mmShufflePs
from src.isas.sse2 import SSE2, mmLoaduPd, mmLoadSd, mmShufflePd, mmStoreuPd, mmAddPd, mmMulPd, mmSetzeroPd, mmUnpackhiPd, \
                            mmUnpackloPd, mmStoreSd, mmCvtsdf64
# from src.irbase import *
# from src.isas.isabase import *
# from src.isas.x86 import *
# from src.isas.sse import *
# from src.isas.sse2 import *

class mmHaddPd(RValue):
    def __init__(self, src0, src1):
        super(mmHaddPd, self).__init__()
        self.srcs += [ src0, src1 ]

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[0]+src0[1], src1[0]+src1[1] ]
        
    def unparse(self, indent):
        return indent + "_mm_hadd_pd(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mmHaddPd( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class mmLoaddupPd(RValue, VecAccess):
    def __init__(self, pointer, zeromask=None):
        super(mmLoaddupPd, self).__init__()
        self.reglen = 2
        self.mrmap = [(0,1)]
        self.zeromask = [0]*self.reglen
        if zeromask is not None: # In this case all the positions have to be zero
            self.zeromask = [1]*self.reglen
        self.pointer = pointer

    def computeSym(self, nameList):
        p = self.pointer.computeSym(nameList)
        return [ sympify(p+'_0'), sympify(p+'_0') ] 

    def getZMask(self):
        return self.zeromask
        
    def unparse(self, indent):
        return indent + "_mm_loaddup_pd(" + self.pointer.unparse("") + ")"
    
    def printInst(self, indent):
        return indent + "mmLoaddupPd( " + self.pointer.printInst("") + " )"

    def __eq__(self, other):
        return isinstance(other, mmLoaddupPd) and self.pointer == other.pointer
    
    def __hash__(self):
        return hash((hash("mmLoaddupPd"), self.pointer.mat, self.pointer.at))

class mmMovedupPd(RValue):
    def __init__(self, src):
        super(mmMovedupPd, self).__init__()
        self.srcs += [ src ]

    def computeSym(self, nameList):
        src = self.srcs[0].computeSym(nameList)
        return [ src[0], src[0] ]
    
    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        return [ s0ZMask[0], s0ZMask[0] ]

    def unparse(self, indent):
        return indent + "_mm_movedup_pd(" + self.srcs[0].unparse("") + ")" 

    def printInst(self, indent):
        return indent + "mmMovedupPd( " + self.srcs[0].printInst("") + " )"

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


class _Dbl2Loader(Loader):
    
    def __init__(self):
        super(_Dbl2Loader, self).__init__()

    def loadMatrix(self, mParams):
        src, dst = mParams['m'], mParams['nuM']
        sL, sR = mParams['mL'], mParams['mR']
        dL, dR = mParams['nuML'], mParams['nuMR']
        M, N = mParams['M'], mParams['N']
#         nuMM = mParams['nuMM']
        isCompact = mParams['compact']
        instructions = []

        if M == 1 and N == 1:
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            instr = mmStoreuPd(mmLoadSd(AddressOf(sa(src[sL.of(0),sR.of(0)]))), pc)
            instructions += [ Comment("1x1 -> 1x2"), instr ]
        elif M == 2 and N == 1:
            if not isCompact:
                es = [ mmLoadSd(Pointer(src[sL.of(i),sR.of(0)])) for i in range(2) ]
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = mmStoreuPd(mmShufflePd(es[0], es[1], (0,0)), pc)
                instructions += [ Comment("2x1 -> 2x1 - incompact"), instr ]
        
        return instructions

class _Dbl2BLAC(object):
    def __init__(self):
        super(_Dbl2BLAC, self).__init__()
    
    def Add(self, s0Params, s1Params, dParams, opts):
        
        nu = 2
        src0, src1, dst = s0Params['nuM'], s1Params['nuM'], dParams['nuM']
        s0L, s0R = s0Params['nuML'], s0Params['nuMR']
        s1L, s1R = s1Params['nuML'], s1Params['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        M, N     = dParams['nuMM'], dParams['nuMN']
        instructions = []

        instructions += [ Comment(str(nu) + "-BLAC: " + str(M) + "x" + str(N) + " + " + str(M) + "x" + str(N)) ]
        if M*N == nu:
            va = mmLoaduPd(Pointer(src0[s0L.of(0),s0R.of(0)]))
            vb = mmLoaduPd(Pointer(src1[s1L.of(0),s1R.of(0)]))
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            instr = mmStoreuPd(mmAddPd(va, vb), pc)
            instructions += [ instr ]
        elif M == nu and N == nu:
            for i in range(M):
                va = mmLoaduPd(Pointer(src0[s0L.of(i),s0R.of(0)]))
                vb = mmLoaduPd(Pointer(src1[s1L.of(i),s1R.of(0)]))
                pc = Pointer(dst[dL.of(i),dR.of(0)])
                instr = mmStoreuPd(mmAddPd(va, vb), pc)
                instructions += [ instr ]
        
        return instructions

    def Kro(self, s0Params, s1Params, dParams, opts):

        nu = 2
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
            va = mmLoaduPd(Pointer(src0[s0L.of(0),s0R.of(0)]))
            vb = mmLoaduPd(Pointer(src1[s1L.of(0),s1R.of(0)]))
            instr = mmStoreuPd(mmMulPd(va, vb), pc)
            instructions += [ instr ]
        elif oM*oK == 1:
            if N*P == nu:
                va = mmLoaduPd(Pointer(src0[s0L.of(0),s0R.of(0)]))
                dup = mmShufflePd(va, va, (0,0))
                vb = mmLoaduPd(Pointer(src1[s1L.of(0),s1R.of(0)]))
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = mmStoreuPd(mmMulPd(dup, vb), pc)
                instructions += [ instr ]
            else:
                va = mmLoaduPd(Pointer(src0[s0L.of(0),s0R.of(0)]))
                dup = mmShufflePd(va, va, (0,0))
                for i in range(nu):
                    vb = mmLoaduPd(Pointer(src1[s1L.of(i),s1R.of(0)]))
                    pc = Pointer(dst[dL.of(i),dR.of(0)])
                    instr = mmStoreuPd(mmMulPd(dup, vb), pc)
                    instructions += [ instr ]
        else:
            if M*K == nu:
                vb = mmLoaduPd(Pointer(src1[s1L.of(0),s1R.of(0)]))
                dup = mmShufflePd(vb, vb, (0,0))
                va = mmLoaduPd(Pointer(src0[s0L.of(0),s0R.of(0)]))
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = mmStoreuPd(mmMulPd(va, dup), pc)
                instructions += [ instr ]
            else:
                vb = mmLoaduPd(Pointer(src1[s1L.of(0),s1R.of(0)]))
                dup = mmShufflePd(vb, vb, (0,0))
                for i in range(nu):
                    va = mmLoaduPd(Pointer(src0[s0L.of(i),s0R.of(0)]))
                    pc = Pointer(dst[dL.of(i),dR.of(0)])
                    instr = mmStoreuPd(mmMulPd(va, dup), pc)
                    instructions += [ instr ]
        
        return instructions

    def Mul(self, s0Params, s1Params, dParams, opts):

        nu = 2
        src0, src1, dst = s0Params['nuM'], s1Params['nuM'], dParams['nuM']
        s0L, s0R = s0Params['nuML'], s0Params['nuMR']
        s1L, s1R = s1Params['nuML'], s1Params['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        M, K, N = s0Params['nuMM'], s0Params['nuMN'], s1Params['nuMN']
        instructions = []

        instructions += [ Comment(str(nu) + "-BLAC: " + str(M) + "x" + str(K) + " * " + str(K) + "x" + str(N)) ]
        if M == 1:
            if N == 1:
                va = mmLoaduPd(Pointer(src0[s0L.of(0),s0R.of(0)]))
                vb = mmLoaduPd(Pointer(src1[s1L.of(0),s1R.of(0)]))
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = mmStoreuPd(mmHaddPd(mmMulPd(va, vb), mmSetzeroPd()), pc)
#                     instr = mmStoreSd(mmHaddPd(mmMulPd(va, vb), mmSetzeroPd()), pc)
                instructions += [ instr ]
            else:
                va = mmLoaduPd(Pointer(src0[s0L.of(0),s0R.of(0)]))
                vb0 = mmLoaduPd(Pointer(src1[s1L.of(0),s1R.of(0)]))
                vb1 = mmLoaduPd(Pointer(src1[s1L.of(1),s1R.of(0)]))
                vbt0 = mmUnpackloPd(vb0, vb1)
                vbt1 = mmUnpackhiPd(vb0, vb1)
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = mmStoreuPd(mmHaddPd(mmMulPd(va, vbt0), mmMulPd(va, vbt1)), pc)
                instructions += [ instr ]
        else:
            if K == 1:
                va0 = mmLoaddupPd(Pointer(src0[s0L.of(0),s0R.of(0)]))
                va1 = mmLoaddupPd(Pointer(src0[s0L.of(1),s0R.of(0)]))
                vb = mmLoaduPd(Pointer(src1[s1L.of(0),s1R.of(0)]))
                pc0 = Pointer(dst[dL.of(0),dR.of(0)])
                pc1 = Pointer(dst[dL.of(1),dR.of(0)])
                instr0 = mmStoreuPd(mmMulPd(va0, vb), pc0)
                instr1 = mmStoreuPd(mmMulPd(va1, vb), pc1)
                instructions += [ instr0, instr1 ]
            else:
                if N == 1:
                    va0 = mmLoaduPd(Pointer(src0[s0L.of(0),s0R.of(0)]))
                    va1 = mmLoaduPd(Pointer(src0[s0L.of(1),s0R.of(0)]))
                    vb = mmLoaduPd(Pointer(src1[s1L.of(0),s1R.of(0)]))
                    pc = Pointer(dst[dL.of(0),dR.of(0)])
                    instr = mmStoreuPd(mmHaddPd(mmMulPd(va0, vb), mmMulPd(va1, vb)), pc)
                    instructions += [ instr ]
                else:
                    va0 = mmLoaduPd(Pointer(src0[s0L.of(0),s0R.of(0)]))
                    va1 = mmLoaduPd(Pointer(src0[s0L.of(1),s0R.of(0)]))
                    vb0 = mmLoaduPd(Pointer(src1[s1L.of(0),s1R.of(0)]))
                    vb1 = mmLoaduPd(Pointer(src1[s1L.of(1),s1R.of(0)]))
                    vbt0 = mmUnpackloPd(vb0, vb1)
                    vbt1 = mmUnpackhiPd(vb0, vb1)
                    pc0 = Pointer(dst[dL.of(0),dR.of(0)])
                    pc1 = Pointer(dst[dL.of(1),dR.of(0)])
                    instr0 = mmStoreuPd(mmHaddPd(mmMulPd(va0, vbt0), mmMulPd(va0, vbt1)), pc0)
                    instr1 = mmStoreuPd(mmHaddPd(mmMulPd(va1, vbt0), mmMulPd(va1, vbt1)), pc1)
                    instructions += [ instr0, instr1 ]

        return instructions

    def T(self, sParams, dParams, opts):

        nu = 2
        src, dst = sParams['nuM'], dParams['nuM']
        sL, sR = sParams['nuML'], sParams['nuMR']
        dL, dR = dParams['nuML'], dParams['nuMR']
        M, N = dParams['nuMM'], dParams['nuMN']
        instructions = []

        instructions += [ Comment(str(nu) + "-BLAC: (" + str(N) + "x" + str(M) + ")^T") ]
        if M*N == nu:
            va = mmLoaduPd(Pointer(src[sL.of(0),sR.of(0)]))
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            instr = mmStoreuPd(va, pc)
            instructions += [ instr ]
        else:
            va0 = mmLoaduPd(Pointer(src[sL.of(0),sR.of(0)]))
            va1 = mmLoaduPd(Pointer(src[sL.of(1),sR.of(0)]))
            pc0 = Pointer(dst[dL.of(0),dR.of(0)])
            pc1 = Pointer(dst[dL.of(1),dR.of(0)])
            vt0 = mmUnpackloPd(va0, va1)
            vt1 = mmUnpackhiPd(va0, va1)
            instr0 = mmStoreuPd(vt0, pc0)
            instr1 = mmStoreuPd(vt1, pc1)
            instructions += [ instr0, instr1 ]
        
        return instructions

class _Dbl2Storer(Storer):
    def __init__(self):
        super(_Dbl2Storer, self).__init__()

    def storeMatrix(self, mParams):
        src, dst = mParams['nuM'], mParams['m']
        sL, sR = mParams['nuML'], mParams['nuMR']
        dL, dR = mParams['mL'], mParams['mR']
        M, N = mParams['M'], mParams['N']
        isCompact = mParams['compact']
        instructions = []

        if M == 1 and N == 1:
            nuv = mmLoaduPd(Pointer(src[sL.of(0),sR.of(0)]))
            pc = AddressOf(sa(dst[dL.of(0),dR.of(0)]))
            instr = mmStoreSd(nuv, pc)
            instructions += [ Comment("1x2 -> 1x1"), instr ]
        elif M == 2 and N == 1:
            if not isCompact:
                nuv = mmLoaduPd(Pointer(src[sL.of(0),sR.of(0)]))
                e = mmShufflePd(nuv, nuv, (1,1))
                pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(2) ]
                instr0 = mmStoreSd(nuv, pcs[0])
                instr1 = mmStoreSd(e, pcs[1])
                instructions += [ Comment("2x1 -> 2x1 - (Store) Incompact"), instr0, instr1 ]
            
        return instructions

class SSE3LoadReplacer(LoadReplacer):
    def __init__(self, opts):
        super(SSE3LoadReplacer, self).__init__(opts)

    def ScaLoad(self, src, repList): #repList is a list of tuples (line, dst)
        isFlt = (self.opts['precision'] == 'float')
        if src.pointer.at[1] == 0:
            return mmCvtssf32(mmLoaduPs(repList[0][1].pointer)) if isFlt else mmCvtsdf64(mmLoaduPd(repList[0][1].pointer))
        if isFlt: 
            return mmCvtssf32(mmShufflePs(mmLoaduPs(repList[0][1].pointer), mmLoaduPs(repList[0][1].pointer), (0, 0, 0, src.pointer.at[1])))
        return mmCvtsdf64(mmShufflePd(mmLoaduPd(repList[0][1].pointer), mmLoaduPd(repList[0][1].pointer), (0, src.pointer.at[1])))

    def mmLoaddupPd(self, src, repList):
        sList = sorted(repList, key=lambda t: t[0], reverse=True)
        dst = sList[0][1]
        if dst.reglen == 2 and dst.mrmap == [0,1]:
            at = src.pointer.getAt()
            return mmShufflePd(mmLoaduPd(dst.pointer), mmLoaduPd(dst.pointer), (at[0],at[0]))

    def mmLoaduPd(self, src, repList):
        if len(repList) == 2 and all(map(lambda d: d[1].reglen == 2 and d[1].mrmap == [0], repList)):
            dstList = [ t[1] for t in repList]
            sList = sorted(dstList, key = lambda dst: dst.pointer, reverse=True) #higher pointer to lower
            return mmUnpackloPd(mmLoadSd(sList[1].pointer),mmLoadSd(sList[0].pointer))
        
class SSE3(ISA):
    def __init__(self, opts):
        super(SSE3, self).__init__()

        self.name = "SSE3"

        sse2 = SSE2(opts)

        fp_m128d = { 'type': '__m128d' }
        fp_m128d['arith'] = [ mmHaddPd ]
        fp_m128d['load']  = [ mmLoaddupPd ]
        fp_m128d['misc']  = [ ]
        fp_m128d['cvt']  = [ ]
        fp_m128d['set']   = [ ]
        fp_m128d['move']  = [ mmMovedupPd ]
        fp_m128d['store'] = [ ]
        fp_m128d['loader'] = _Dbl2Loader()
        fp_m128d['nublac'] = _Dbl2BLAC()
        fp_m128d['storer'] = _Dbl2Storer()
        fp_m128d['loadreplacer'] = SSE3LoadReplacer(opts)
        
        fp_m128 = { 'type': '__m128' }
        fp_m128['arith'] = [ mmHaddPs ]
        fp_m128['load']  = [ ]
        fp_m128['misc']  = [ ]
        fp_m128['cvt']  = [ ]
        fp_m128['set']   = [ ]
        fp_m128['move']  = [ ]
        fp_m128['store'] = [ ]

        self.updateType(fp_m128, sse2.types['fp'][('float',4)], ['arith', 'load', 'misc', 'cvt', 'set', 'move', 'store'])
        self.updateType(fp_m128d, sse2.types['fp'][('double',2)], ['arith', 'load', 'misc', 'cvt', 'set', 'move', 'store'])

        self.types = { 'fp': { ('double', 2): fp_m128d, ('float', 4): fp_m128} }

    