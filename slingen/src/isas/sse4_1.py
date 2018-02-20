'''
Created on Apr 18, 2012

@author: danieles
'''

from src.irbase import RValue, Pointer, PointerCast, AddressOf, Comment, sa
    

from src.isas.isabase import ISA, Loader, Storer, LoadReplacer
# from src.isas.ssse3 import SSSE3, SSE3, SSE2, SSE, x86
from src.isas.sse import mmLoaduPs, mmCvtssf32, mmShufflePs, mmSetzeroPs, mmLoadlPi, mmLoadSs, \
                            mmStoreuPs, mmMovehlPs, mmMovelhPs, mmAddPs, mmMulPs, mmStoreSs, mmStorelPi, mmUnpackloPs, \
                            mmUnpackhiPs, mmHaddPs, mmLoad1Ps
from src.isas.sse2 import mmLoaduPd, mmShufflePd, mmCvtsdf64
from src.isas.ssse3 import SSSE3, mmShiftPs
                        
# from src.irbase import *
# from src.isas.isabase import *
# from src.isas.x86 import *
# from src.isas.sse import *
# from src.isas.sse2 import *
# from src.isas.sse3 import *


class mmDpPs(RValue):
    def __init__(self, src0, src1, immBitList):
        super(mmDpPs, self).__init__()
        self.srcs += [ src0, src1 ]
        self.immBitList = immBitList
        imm = 0
        for bit in immBitList:
            imm = (imm << 1) | int(bit)
        self.imm = imm 

    def computeSym(self, nameList): # To be fixed (more general)
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[0] * src1[0], src0[1] * src1[1], src0[2] * src1[2], src0[3] * src1[3] ]

    def unparse(self, indent):
        return indent + "_mm_dp_ps(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ", " + str(self.imm) + ")" 

    def printInst(self, indent):
        return indent + "mmDpPs( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + ", " + str(self.immBitList) + " )"

class mmInsertPs(RValue):
    def __init__(self, src0, src1, immBitList):
        super(mmInsertPs, self).__init__()
        self.srcs += [ src0, src1 ]
        self.immBitList = immBitList
        imm = 0
        for bit in immBitList: # bits 0-3: zeromask (if bit: copy tmp else 0) - 4-5: where to insert - 6-7: which elem of b to insert
            imm = (imm << 1) | int(bit)
        self.imm = imm 
 
    def computeSym(self, nameList): # to be made more general 
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        posb = int(self.immBitList[0]) << 1 | int(self.immBitList[1]) 
        posa = int(self.immBitList[2]) << 1 | int(self.immBitList[3])
        tmp = [ '0' if self.immBitList[4+i] else src0[i] for i in range(4) ]
        tmp[posa] = src1[posb]
        return tmp
     
    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1Zmask = self.srcs[1].getZMask()
        posb = int(self.immBitList[0]) << 1 | int(self.immBitList[1]) 
        posa = int(self.immBitList[2]) << 1 | int(self.immBitList[3])
        tmp = [ 1 if self.immBitList[4+i] else s0ZMask[i] for i in range(4) ]
        tmp[posa] = s1Zmask[posb]
        return tmp
         
    def unparse(self, indent):
        return indent + "_mm_insert_ps(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ", " + str(self.imm) + ")" 
 
    def printInst(self, indent):
        return indent + "mmInsertPs( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + ", " + str(self.immBitList) + " )"
 
class mmBlendPs(RValue):
    def __init__(self, src0, src1, immBitList):
        super(mmBlendPs, self).__init__()
        self.srcs += [ src0, src1 ]
        self.immBitList = immBitList
        imm = 0
        for bit in immBitList:
            imm = (imm << 1) | int(bit)
        self.imm = imm 
 
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src1[0] if self.immBitList[3] else src0[0], src1[1] if self.immBitList[2] else src0[1], src1[2] if self.immBitList[1] else src0[2], src1[3] if self.immBitList[0] else src0[3] ]
 
    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [ s1ZMask[0] if self.immBitList[3] else s0ZMask[0], s1ZMask[1] if self.immBitList[2] else s0ZMask[1], s1ZMask[2] if self.immBitList[1] else s0ZMask[2], s1ZMask[3] if self.immBitList[0] else s0ZMask[3] ]
 
    def unparse(self, indent):
        return indent + "_mm_blend_ps(" + self.srcs[0].unparse("") + ", " + self.srcs[1].unparse("") + ", " + str(self.imm) + ")" 
 
    def printInst(self, indent):
        return indent + "mmBlendPs( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + ", " + str(self.immBitList) + " )"

# def mmBlendPs(v1, v2, mask):
#     ''' Simulation of _mmBlendPs (SSE4.1) in SSSE3. '''
#     if mask == (1,0,0,0): # MSB -> LSB (res should be: [ v1[0], v1[1], v1[2], v2[3] ])
#         return mmShufflePs(v1, mmUnpackhiPs(v1, v2), (3, 0, 1, 0))
#     else:
#         raise Exception('Unsupported mask %r for mmBlendPs simulation in SSSE3' % mask)
#  
# def mmInsertPs(v1, v2, mask):
#     if mask == [0,0,1,1,0,0,0,0]: # MSB -> LSB (res should be: [ v1[0], v1[1], v1[2], v2[0] ])
#         return mmShufflePs(v1, mmMoveSs(v1, v2), (0, 2, 1, 0))
#     else:
#         raise Exception('Unsupported mask %r for mmInsertPs simulation in SSSE3' % mask)
# 
# def mmDpPs(v1, v2, mask):
#     if mask == [1,1,1,1,0,0,0,1]:
#         mul1 = mmMulPs(v1, v2)
#         mul2 = mmHaddPs(mul1, mul1)
#         return mmHaddPs(mul2, mul2)
#     else:
#         raise Exception('Unsupported mask %r for mmDpPs simulation in SSSE3' % mask)

class _Flt4Loader(Loader):
    def __init__(self):
        super(_Flt4Loader, self).__init__()
    
    def loadMatrix(self, mParams):
        src, dst = mParams['m'], mParams['nuM']
        sL, sR = mParams['mL'], mParams['mR']
        dL, dR = mParams['nuML'], mParams['nuMR']
        M, N = mParams['M'], mParams['N']
        isCompact, isCorner = mParams['compact'], mParams['corner']
        instructions = []

        if M == 1:
            if N == 1:
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = mmStoreuPs(mmLoadSs(AddressOf(sa(src[sL.of(0),sR.of(0)]))), pc)
                instructions += [ Comment("1x1 -> 1x4"), instr ]
            elif N == 2:
                v0_1 = mmLoadlPi(mmSetzeroPs(), PointerCast("__m64", Pointer(src[sL.of(0),sR.of(0)])))
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = mmStoreuPs(v0_1, pc)
                instructions += [ Comment("1x2 -> 1x4 - Corner") ]
                instructions += [ instr ]
            elif N == 3:
                v0_1 = mmLoadlPi(mmSetzeroPs(), PointerCast("__m64", Pointer(src[sL.of(0),sR.of(0)])))
                e2 = mmLoadSs(Pointer(src[sL.of(0),sR.of(2)]))
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = mmStoreuPs(mmShufflePs(v0_1, e2, (1,0,1,0)), pc)
                instructions += [ Comment("1x3 -> 1x4 - Corner") ]
                instructions += [ instr ]
        elif M == 2:
            if N == 1:
                if isCompact:
                    v0_1 = mmLoadlPi(mmSetzeroPs(), PointerCast("__m64", Pointer(src[sL.of(0),sR.of(0)])))
                    pc = Pointer(dst[dL.of(0),dR.of(0)])
                    instr = mmStoreuPs(v0_1, pc)
                    instructions += [ Comment("2x1 -> 4x1 - Compact") ]
                    instructions += [ instr ]
                else:
                    e0 = mmLoadSs(Pointer(src[sL.of(0),sR.of(0)]))
                    e1 = mmLoadSs(Pointer(src[sL.of(1),sR.of(0)]))
                    pc = Pointer(dst[dL.of(0),dR.of(0)])
                    instr = mmStoreuPs(mmUnpackloPs(e0, e1), pc)
                    instructions += [ Comment("2x1 -> 4x1 - incompact") ]
                    instructions += [ instr ]
            elif N == 2:
                    v0_1 = mmLoadlPi(mmSetzeroPs(), PointerCast("__m64", Pointer(src[sL.of(0),sR.of(0)])))
                    v2_3 = mmLoadlPi(mmSetzeroPs(), PointerCast("__m64", Pointer(src[sL.of(1),sR.of(0)])))
                    pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4) ]
                    instr0 = mmStoreuPs(v0_1, pcs[0])
                    instr1 = mmStoreuPs(v2_3, pcs[1])
                    instructions += [ Comment("2x2 -> 4x4") ]
                    instructions += [ instr0, instr1, mmStoreuPs(mmSetzeroPs(), pcs[2]), mmStoreuPs(mmSetzeroPs(), pcs[3]) ]
            elif N == 3:
                if isCompact:
                    v0_3 = mmLoaduPs(Pointer(src[sL.of(0),sR.of(0)]))
                    v4_5 = mmLoadlPi(mmSetzeroPs(), PointerCast("__m64", Pointer(src[sL.of(1),sR.of(1)])))
                    pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4) ]
                    instr0 = mmStoreuPs(mmBlendPs(v0_3, mmSetzeroPs(), (1,0,0,0)), pcs[0])
                    instr1 = mmStoreuPs(mmShiftPs(v4_5, v0_3, 3), pcs[1])
                    instructions += [ Comment("2x3 -> 4x4 - Compact") ]
                    instructions += [ instr0, instr1, mmStoreuPs(mmSetzeroPs(), pcs[2]), mmStoreuPs(mmSetzeroPs(), pcs[3]) ]
                else:
                    v0_2 = mmLoaduPs(Pointer(src[sL.of(0),sR.of(0)]))
                    v3_4 = mmLoadlPi(mmSetzeroPs(), PointerCast("__m64", Pointer(src[sL.of(1),sR.of(0)])))
                    e5   = mmLoadSs(Pointer(src[sL.of(1),sR.of(2)]))
                    pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4) ]
                    instr0 = mmStoreuPs(mmBlendPs(v0_2, mmSetzeroPs(), (1,0,0,0)), pcs[0])
                    instr1 = mmStoreuPs(mmShufflePs(v3_4, e5, (1,0,1,0)), pcs[1])
                    instructions += [ Comment("2x3 -> 4x4 - Incompact") ]
                    instructions += [ instr0, instr1, mmStoreuPs(mmSetzeroPs(), pcs[2]), mmStoreuPs(mmSetzeroPs(), pcs[3]) ]
            elif N == 4:
                v0_3 = mmLoaduPs(Pointer(src[sL.of(0),sR.of(0)]))
                v4_7 = mmLoaduPs(Pointer(src[sL.of(1),sR.of(0)]))
                pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4) ]
                instr0 = mmStoreuPs(v0_3, pcs[0])
                instr1 = mmStoreuPs(v4_7, pcs[1])
                instructions += [ Comment("2x4 -> 4x4") ]
                instructions += [ instr0, instr1, mmStoreuPs(mmSetzeroPs(), pcs[2]), mmStoreuPs(mmSetzeroPs(), pcs[3]) ]
        elif M == 3:
            if N == 1:
                if isCompact:
                    v0_1 = mmLoadlPi(mmSetzeroPs(), PointerCast("__m64", Pointer(src[sL.of(0),sR.of(0)])))
                    e2 = mmLoadSs(Pointer(src[sL.of(2),sR.of(0)]))
                    pc = Pointer(dst[dL.of(0),dR.of(0)])
                    instr = mmStoreuPs(mmShufflePs(v0_1, e2, (1,0,1,0)), pc)
                    instructions += [ Comment("3x1 -> 4x1 - Compact") ]
                    instructions += [ instr ]
                else:
                    e0 = mmLoadSs(Pointer(src[sL.of(0),sR.of(0)]))
                    e1 = mmLoadSs(Pointer(src[sL.of(1),sR.of(0)]))
                    e2 = mmLoadSs(Pointer(src[sL.of(2),sR.of(0)]))
                    pc = Pointer(dst[dL.of(0),dR.of(0)])
                    instr = mmStoreuPs(mmShufflePs(mmUnpackloPs(e0, e1), e2, (1,0,1,0)), pc)
                    instructions += [ Comment("3x1 -> 4x1 - incompact") ]
                    instructions += [ instr ]
            elif N == 2:
                    v0_1 = mmLoadlPi(mmSetzeroPs(), PointerCast("__m64", Pointer(src[sL.of(0),sR.of(0)])))
                    v2_3 = mmLoadlPi(mmSetzeroPs(), PointerCast("__m64", Pointer(src[sL.of(1),sR.of(0)])))
                    v4_5 = mmLoadlPi(mmSetzeroPs(), PointerCast("__m64", Pointer(src[sL.of(2),sR.of(0)])))
                    pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4) ]
                    instr0 = mmStoreuPs(v0_1, pcs[0])
                    instr1 = mmStoreuPs(v2_3, pcs[1])
                    instr2 = mmStoreuPs(v4_5, pcs[2])
                    instructions += [ Comment("3x2 -> 4x4") ]
                    instructions += [ instr0, instr1, instr2, mmStoreuPs(mmSetzeroPs(), pcs[3]) ]
            elif N == 3:
                if isCompact:
                    v0_3 = mmLoaduPs(Pointer(src[sL.of(0),sR.of(0)]))
                    v4_7 = mmLoaduPs(Pointer(src[sL.of(1),sR.of(1)]))
                    e8 = mmLoadSs(Pointer(src[sL.of(2),sR.of(2)]))
                    pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4) ]
                    instr0 = mmStoreuPs(mmBlendPs(v0_3, mmSetzeroPs(), (1,0,0,0)), pcs[0])
                    instr1 = mmStoreuPs(mmBlendPs(mmShiftPs(v4_7, v0_3, 3), mmSetzeroPs(), (1,0,0,0)), pcs[1])
                    instr2 = mmStoreuPs(mmShufflePs(v4_7, e8, (1,0,3,2)), pcs[2])
                    instructions += [ Comment("3x3 -> 4x4 - Compact") ]
                    instructions += [ instr0, instr1, instr2, mmStoreuPs(mmSetzeroPs(), pcs[3]) ]
                else:
                    v0_2 = mmLoaduPs(Pointer(src[sL.of(0),sR.of(0)]))
                    v3_5 = mmLoaduPs(Pointer(src[sL.of(1),sR.of(0)]))
                    v6_7 = mmLoadlPi(mmSetzeroPs(), PointerCast("__m64", Pointer(src[sL.of(2),sR.of(0)])))
                    e8   = mmLoadSs(Pointer(src[sL.of(2),sR.of(2)]))
                    pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4) ]
                    instr0 = mmStoreuPs(mmBlendPs(v0_2, mmSetzeroPs(), (1,0,0,0)), pcs[0])
                    instr1 = mmStoreuPs(mmBlendPs(v3_5, mmSetzeroPs(), (1,0,0,0)), pcs[1])
                    instr2 = mmStoreuPs(mmShufflePs(v6_7, e8, (1,0,1,0)), pcs[2])
                    instructions += [ Comment("3x3 -> 4x4 - Incompact") ]
                    instructions += [ instr0, instr1, instr2, mmStoreuPs(mmSetzeroPs(), pcs[3]) ]
            elif N == 4:
                rows = [ mmLoaduPs(Pointer(src[sL.of(i),sR.of(0)])) for i in range(3) ]
                pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4) ]
                instrs = [ mmStoreuPs(rows[i], pcs[i]) for i in range(3) ]
                instructions += [ Comment("3x4 -> 4x4") ] + instrs + [ mmStoreuPs(mmSetzeroPs(), pcs[3]) ]
        elif M == 4:
            if N == 1:
                if not isCompact:
                    es = [ mmLoadSs(Pointer(src[sL.of(i),sR.of(0)])) for i in range(4) ]
                    pc = Pointer(dst[dL.of(0),dR.of(0)])
                    instr = mmStoreuPs(mmShufflePs(mmUnpackloPs(es[0], es[1]), mmUnpackloPs(es[2], es[3]), (1,0,1,0)), pc)
                    instructions += [ Comment("4x1 -> 4x1 - incompact"), instr ]
            elif N == 2:
                    rows = [ mmLoadlPi(mmSetzeroPs(), PointerCast("__m64", Pointer(src[sL.of(i),sR.of(0)]))) for i in range(4) ]
                    pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4) ]
                    instrs = [ mmStoreuPs(rows[i], pcs[i]) for i in range(4) ]
                    instructions += [ Comment("4x2 -> 4x4") ] + instrs
            elif N == 3:
                if isCompact:
                    v0_3 = mmLoaduPs(Pointer(src[sL.of(0),sR.of(0)]))
                    v4_7 = mmLoaduPs(Pointer(src[sL.of(1),sR.of(1)]))
                    v8_11 = mmLoaduPs(Pointer(src[sL.of(2),sR.of(2)]))
                    pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4) ]
                    instr0 = mmStoreuPs(mmBlendPs(v0_3, mmSetzeroPs(), (1,0,0,0)), pcs[0])
                    instr1 = mmStoreuPs(mmBlendPs(mmShiftPs(v4_7, v0_3, 3), mmSetzeroPs(), (1,0,0,0)), pcs[1])
                    instr2 = mmStoreuPs(mmBlendPs(mmShiftPs(v8_11, v4_7, 2), mmSetzeroPs(), (1,0,0,0)), pcs[2])
                    instr3 = mmStoreuPs(mmShiftPs(mmSetzeroPs(), v8_11, 1), pcs[3])
                    instructions += [ Comment("4x3 -> 4x4 - Compact") ]
                    instructions += [ instr0, instr1, instr2, instr3 ]
                else:
                    v0_2 = mmLoaduPs(Pointer(src[sL.of(0),sR.of(0)]))
                    v3_5 = mmLoaduPs(Pointer(src[sL.of(1),sR.of(0)]))
                    v6_8 = mmLoaduPs(Pointer(src[sL.of(2),sR.of(0)]))
                    pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4) ]
                    instr0 = mmStoreuPs(mmBlendPs(v0_2, mmSetzeroPs(), (1,0,0,0)), pcs[0])
                    instr1 = mmStoreuPs(mmBlendPs(v3_5, mmSetzeroPs(), (1,0,0,0)), pcs[1])
                    instr2 = mmStoreuPs(mmBlendPs(v6_8, mmSetzeroPs(), (1,0,0,0)), pcs[2])
                    if isCorner:
                        v9_10 = mmLoadlPi(mmSetzeroPs(), PointerCast("__m64", Pointer(src[sL.of(3),sR.of(0)])))
                        e11   = mmLoadSs(Pointer(src[sL.of(3),sR.of(2)]))
                        instr3 = mmStoreuPs(mmShufflePs(v9_10, e11, (1,0,1,0)), pcs[3])
                        instructions += [ Comment("4x3 -> 4x4 - Incompact Corner") ]
                        instructions += [ instr0, instr1, instr2, instr3 ]
                    else:
                        v9_11 = mmLoaduPs(Pointer(src[sL.of(3),sR.of(0)]))
                        instr3 = mmStoreuPs(mmBlendPs(v9_11, mmSetzeroPs(), (1,0,0,0)), pcs[3])
                        instructions += [ Comment("4x3 -> 4x4 - Incompact") ]
                        instructions += [ instr0, instr1, instr2, instr3 ]
        
        for i in instructions:
            i.bounds.update(mParams['bounds'])                
        return instructions

class _Flt4BLAC(object):
    def __init__(self):
        super(_Flt4BLAC, self).__init__()
    
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
            va = mmLoaduPs(Pointer(src0[s0L.of(0),s0R.of(0)]))
            vb = mmLoaduPs(Pointer(src1[s1L.of(0),s1R.of(0)]))
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            instr = mmStoreuPs(mmAddPs(va, vb), pc)
            instructions += [ instr ]
        elif M == nu and N == nu:
            for i in range(M):
                va = mmLoaduPs(Pointer(src0[s0L.of(i),s0R.of(0)]))
                vb = mmLoaduPs(Pointer(src1[s1L.of(i),s1R.of(0)]))
                pc = Pointer(dst[dL.of(i),dR.of(0)])
                instr = mmStoreuPs(mmAddPs(va, vb), pc)
                instructions += [ instr ]
        
        for i in instructions:
            i.bounds.update(dParams['bounds'])                
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
            va = mmLoaduPs(Pointer(src0[s0L.of(0),s0R.of(0)]))
            vb = mmLoaduPs(Pointer(src1[s1L.of(0),s1R.of(0)]))
            instr = mmStoreuPs(mmMulPs(va, vb), pc)
            instructions += [ instr ]
        elif oM*oK == 1:
            if N*P == nu:
                va = mmLoaduPs(Pointer(src0[s0L.of(0),s0R.of(0)]))
                dup = mmShufflePs(va, va, (0,0,0,0))
                vb = mmLoaduPs(Pointer(src1[s1L.of(0),s1R.of(0)]))
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = mmStoreuPs(mmMulPs(dup, vb), pc)
                instructions += [ instr ]
            else:
                va = mmLoaduPs(Pointer(src0[s0L.of(0),s0R.of(0)]))
                dup = mmShufflePs(va, va, (0,0,0,0))
                for i in range(nu):
                    vb = mmLoaduPs(Pointer(src1[s1L.of(i),s1R.of(0)]))
                    pc = Pointer(dst[dL.of(i),dR.of(0)])
                    instr = mmStoreuPs(mmMulPs(dup, vb), pc)
                    instructions += [ instr ]
        else:
            if M*K == nu:
                vb = mmLoaduPs(Pointer(src1[s1L.of(0),s1R.of(0)]))
                dup = mmShufflePs(vb, vb, (0,0,0,0))
                va = mmLoaduPs(Pointer(src0[s0L.of(0),s0R.of(0)]))
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = mmStoreuPs(mmMulPs(va, dup), pc)
                instructions += [ instr ]
            else:
                vb = mmLoaduPs(Pointer(src1[s1L.of(0),s1R.of(0)]))
                dup = mmShufflePs(vb, vb, (0,0,0,0))
                for i in range(nu):
                    va = mmLoaduPs(Pointer(src0[s0L.of(i),s0R.of(0)]))
                    pc = Pointer(dst[dL.of(i),dR.of(0)])
                    instr = mmStoreuPs(mmMulPs(va, dup), pc)
                    instructions += [ instr ]
        
        for i in instructions:
            i.bounds.update(dParams['bounds'])                
        return instructions

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
                va = mmLoaduPs(Pointer(src0[s0L.of(0),s0R.of(0)]))
                vb = mmLoaduPs(Pointer(src1[s1L.of(0),s1R.of(0)]))
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = mmStoreuPs(mmDpPs(va, vb, [1,1,1,1,0,0,0,1]), pc)
                instructions += [ instr ]
            else:
                vb0 = mmLoaduPs(Pointer(src1[s1L.of(0),s1R.of(0)]))
                vb1 = mmLoaduPs(Pointer(src1[s1L.of(1),s1R.of(0)]))
                vb2 = mmLoaduPs(Pointer(src1[s1L.of(2),s1R.of(0)]))
                vb3 = mmLoaduPs(Pointer(src1[s1L.of(3),s1R.of(0)]))

                va00 = mmLoad1Ps(Pointer(src0[s0L.of(0),s0R.of(0)]))
                va01 = mmLoad1Ps(Pointer(src0[s0L.of(0),s0R.of(1)]))
                va02 = mmLoad1Ps(Pointer(src0[s0L.of(0),s0R.of(2)]))
                va03 = mmLoad1Ps(Pointer(src0[s0L.of(0),s0R.of(3)]))
                mul0 = mmMulPs(va00, vb0)
                mul1 = mmMulPs(va01, vb1)
                add0 = mmAddPs(mul0, mul1)
                mul2 = mmMulPs(va02, vb2)
                mul3 = mmMulPs(va03, vb3)
                add1 = mmAddPs(mul2, mul3)
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = mmStoreuPs(mmAddPs(add0, add1), pc)
                instructions += [ instr ]
        else:
            if K == 1:
                va0 = mmLoad1Ps(Pointer(src0[s0L.of(0),s0R.of(0)]))
                va1 = mmLoad1Ps(Pointer(src0[s0L.of(1),s0R.of(0)]))
                va2 = mmLoad1Ps(Pointer(src0[s0L.of(2),s0R.of(0)]))
                va3 = mmLoad1Ps(Pointer(src0[s0L.of(3),s0R.of(0)]))
                vb = mmLoaduPs(Pointer(src1[s1L.of(0),s1R.of(0)]))
                pc0 = Pointer(dst[dL.of(0),dR.of(0)])
                pc1 = Pointer(dst[dL.of(1),dR.of(0)])
                pc2 = Pointer(dst[dL.of(2),dR.of(0)])
                pc3 = Pointer(dst[dL.of(3),dR.of(0)])
                instr0 = mmStoreuPs(mmMulPs(va0, vb), pc0)
                instr1 = mmStoreuPs(mmMulPs(va1, vb), pc1)
                instr2 = mmStoreuPs(mmMulPs(va2, vb), pc2)
                instr3 = mmStoreuPs(mmMulPs(va3, vb), pc3)
                instructions += [ instr0, instr1, instr2, instr3 ]
            else:
                if N == 1:
                    va0 = mmLoaduPs(Pointer(src0[s0L.of(0),s0R.of(0)]))
                    va1 = mmLoaduPs(Pointer(src0[s0L.of(1),s0R.of(0)]))
                    va2 = mmLoaduPs(Pointer(src0[s0L.of(2),s0R.of(0)]))
                    va3 = mmLoaduPs(Pointer(src0[s0L.of(3),s0R.of(0)]))
                    vb = mmLoaduPs(Pointer(src1[s1L.of(0),s1R.of(0)]))
                    mul0 = mmMulPs(va0, vb)
                    mul1 = mmMulPs(va1, vb)
                    mul2 = mmMulPs(va2, vb)
                    mul3 = mmMulPs(va3, vb)
                    hadd0 = mmHaddPs(mul0, mul1)
                    hadd1 = mmHaddPs(mul2, mul3)
                    pc = Pointer(dst[dL.of(0),dR.of(0)])
                    instr = mmStoreuPs(mmHaddPs(hadd0, hadd1), pc)
                    instructions += [ instr ]
                else:
                    vb0 = mmLoaduPs(Pointer(src1[s1L.of(0),s1R.of(0)]))
                    vb1 = mmLoaduPs(Pointer(src1[s1L.of(1),s1R.of(0)]))
                    vb2 = mmLoaduPs(Pointer(src1[s1L.of(2),s1R.of(0)]))
                    vb3 = mmLoaduPs(Pointer(src1[s1L.of(3),s1R.of(0)]))
                    for i in range(nu):
                        vai0 = mmLoad1Ps(Pointer(src0[s0L.of(i),s0R.of(0)]))
                        vai1 = mmLoad1Ps(Pointer(src0[s0L.of(i),s0R.of(1)]))
                        vai2 = mmLoad1Ps(Pointer(src0[s0L.of(i),s0R.of(2)]))
                        vai3 = mmLoad1Ps(Pointer(src0[s0L.of(i),s0R.of(3)]))
                        mul0 = mmMulPs(vai0, vb0)
                        mul1 = mmMulPs(vai1, vb1)
                        add0 = mmAddPs(mul0, mul1)
                        mul2 = mmMulPs(vai2, vb2)
                        mul3 = mmMulPs(vai3, vb3)
                        add1 = mmAddPs(mul2, mul3)
                        pc = Pointer(dst[dL.of(i),dR.of(0)])
                        instr = mmStoreuPs(mmAddPs(add0, add1), pc)
                        instructions += [ instr ]

        for i in instructions:
            i.bounds.update(dParams['bounds'])                
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
            va = mmLoaduPs(Pointer(src[sL.of(0),sR.of(0)]))
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            instr = mmStoreuPs(va, pc)
            instructions += [ instr ]
        else:
            va0 = mmLoaduPs(Pointer(src[sL.of(0),sR.of(0)]))
            va1 = mmLoaduPs(Pointer(src[sL.of(1),sR.of(0)]))
            va2 = mmLoaduPs(Pointer(src[sL.of(2),sR.of(0)]))
            va3 = mmLoaduPs(Pointer(src[sL.of(3),sR.of(0)]))
            #Equivalent of _MM_TRANSPOSE4_PS
            tmp0 = mmUnpackloPs(va0, va1)
            tmp2 = mmUnpackloPs(va2, va3)
            tmp1 = mmUnpackhiPs(va0, va1)
            tmp3 = mmUnpackhiPs(va2, va3)
            col0 = mmMovelhPs(tmp0, tmp2)
            col1 = mmMovehlPs(tmp2, tmp0)
            col2 = mmMovelhPs(tmp1, tmp3)
            col3 = mmMovehlPs(tmp3, tmp1)
            #Equivalent of _MM_TRANSPOSE4_PS
            pc0 = Pointer(dst[dL.of(0),dR.of(0)])
            pc1 = Pointer(dst[dL.of(1),dR.of(0)])
            pc2 = Pointer(dst[dL.of(2),dR.of(0)])
            pc3 = Pointer(dst[dL.of(3),dR.of(0)])
            instr0 = mmStoreuPs(col0, pc0)
            instr1 = mmStoreuPs(col1, pc1)
            instr2 = mmStoreuPs(col2, pc2)
            instr3 = mmStoreuPs(col3, pc3)
            instructions += [ instr0, instr1, instr2, instr3 ]
        
        for i in instructions:
            i.bounds.update(dParams['bounds'])                
        return instructions

class _Flt4Storer(Storer):
    def __init__(self):
        super(_Flt4Storer, self).__init__()

    def storeMatrix(self, mParams):
        src, dst = mParams['nuM'], mParams['m']
        sL, sR = mParams['nuML'], mParams['nuMR']
        dL, dR = mParams['mL'], mParams['mR']
        M, N = mParams['M'], mParams['N']
        isCompact = mParams['compact']
        instructions = []

        if M == 1:
            if N == 1:
                nuv = mmLoaduPs(Pointer(src[sL.of(0),sR.of(0)]), [1,2,3])
                pc = AddressOf(sa(dst[dL.of(0),dR.of(0)]))
                instr = mmStoreSs(nuv, pc)
                instructions += [ Comment("1x4 -> 1x1"), instr ]
            elif N == 2:
                nuv = mmLoaduPs(Pointer(src[sL.of(0),sR.of(0)]), [2,3])
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = mmStorelPi(nuv, PointerCast("__m64", pc))
                instructions += [ Comment("1x4 -> 1x2 - Corner"), instr ]
            elif N == 3:
                nuv = mmLoaduPs(Pointer(src[sL.of(0),sR.of(0)]), [3])
                e2 = mmShufflePs(nuv, nuv, (3,3,3,2))
                pc0 = Pointer(dst[dL.of(0),dR.of(0)])
                pc2 = Pointer(dst[dL.of(0),dR.of(2)])
                instr0 = mmStorelPi(nuv, PointerCast("__m64", pc0))
                instr1 = mmStoreSs(e2, pc2)
                instructions += [ Comment("1x4 -> 1x3 - Corner") ]
                instructions += [ instr0, instr1 ]
        elif M == 2:
            if N == 1:
                nuv = mmLoaduPs(Pointer(src[sL.of(0),sR.of(0)]), [2,3])
                if isCompact:
                    pc = Pointer(dst[dL.of(0),dR.of(0)])
                    instr = mmStorelPi(nuv, PointerCast("__m64", pc))
                    instructions += [ Comment("4x1 -> 2x1 - Compact"), instr ]
                else:
                    e1 = mmShufflePs(nuv, nuv, (2,2,2,1))
                    pc0 = Pointer(dst[dL.of(0),dR.of(0)])
                    pc1 = Pointer(dst[dL.of(1),dR.of(0)])
                    instr0 = mmStoreSs(nuv, pc0)
                    instr1 = mmStoreSs(e1, pc1)
                    instructions += [ Comment("4x1 -> 2x1 - Incompact") ]
                    instructions += [ instr0, instr1 ]
            elif N == 2:
                nuvs = [ mmLoaduPs(Pointer(src[sL.of(i),sR.of(0)]), [2,3]) for i in range(2) ]
                pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(2) ]
                instrs = [ mmStorelPi(nuvs[i], PointerCast("__m64", pcs[i])) for i in range(2) ]
                instructions += [ Comment("4x4 -> 2x2") ] + instrs
            elif N == 3:
                nuvs = [ mmLoaduPs(Pointer(src[sL.of(i),sR.of(0)]), [3]) for i in range(2) ]
                if isCompact:
                    pc0 = Pointer(dst[dL.of(0),dR.of(0)])
                    pc1 = Pointer(dst[dL.of(1),dR.of(1)])
                    instr0 = mmStoreuPs(mmInsertPs(nuvs[0], nuvs[1], [0,0,1,1,0,0,0,0]), pc0)
                    instr1 = mmStorelPi(mmShufflePs(nuvs[1], nuvs[1], (3,3,2,1)), PointerCast("__m64", pc1))
                    instructions += [ Comment("4x4 -> 2x3 - Compact") ]
                    instructions += [ instr0, instr1 ]
                else:
                    instructions += [ Comment("4x4 -> 2x3 - Compact") ]
                    e2 = mmShufflePs(nuvs[0], nuvs[0], (3,3,3,2))
                    instrRow0 = [ mmStorelPi(nuvs[0], PointerCast("__m64", Pointer(dst[dL.of(0),dR.of(0)]))), mmStoreSs(e2, Pointer(dst[dL.of(0),dR.of(2)])) ]
                    e5 = mmShufflePs(nuvs[1], nuvs[1], (3,3,3,2))
                    instrRow1 = [ mmStorelPi(nuvs[1], PointerCast("__m64", Pointer(dst[dL.of(1),dR.of(0)]))), mmStoreSs(e5, Pointer(dst[dL.of(1),dR.of(2)])) ]
                    instructions += instrRow0 + instrRow1
            elif N == 4:
                v0_3 = mmLoaduPs(Pointer(src[sL.of(0),sR.of(0)]))
                v4_7 = mmLoaduPs(Pointer(src[sL.of(1),sR.of(0)]))
                pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(2) ]
                instr0 = mmStoreuPs(v0_3, pcs[0])
                instr1 = mmStoreuPs(v4_7, pcs[1])
                instructions += [ Comment("4x4 -> 2x4") ]
                instructions += [ instr0, instr1 ]
        elif M == 3:
            if N == 1:
                nuv = mmLoaduPs(Pointer(src[sL.of(0),sR.of(0)]), [3])
                if isCompact:
                    e2 = mmShufflePs(nuv, nuv, (3,3,3,2))
                    pc0 = Pointer(dst[dL.of(0),dR.of(0)])
                    pc2 = Pointer(dst[dL.of(2),dR.of(0)])
                    instr0 = mmStorelPi(nuv, PointerCast("__m64", pc0))
                    instr1 = mmStoreSs(e2, pc2)
                    instructions += [ Comment("4x1 -> 3x1 - Compact") ]
                    instructions += [ instr0, instr1 ]
                else:
                    e1 = mmShufflePs(nuv, nuv, (3,3,3,1))
                    e2 = mmShufflePs(nuv, nuv, (3,3,3,2))
                    pc0 = Pointer(dst[dL.of(0),dR.of(0)])
                    pc1 = Pointer(dst[dL.of(1),dR.of(0)])
                    pc2 = Pointer(dst[dL.of(2),dR.of(0)])
                    instr0 = mmStoreSs(nuv, pc0)
                    instr1 = mmStoreSs(e1, pc1)
                    instr2 = mmStoreSs(e2, pc2)
                    instructions += [ Comment("4x1 -> 3x1 - Incompact") ]
                    instructions += [ instr0, instr1, instr2 ]
            elif N == 2:
                nuvs = [ mmLoaduPs(Pointer(src[sL.of(i),sR.of(0)]), [2,3]) for i in range(3) ]
                pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(3) ]
                instrs = [ mmStorelPi(nuvs[i], PointerCast("__m64", pcs[i])) for i in range(3) ]
                instructions += [ Comment("4x4 -> 3x2") ] + instrs
            elif N == 3:
                nuvs = [ mmLoaduPs(Pointer(src[sL.of(i),sR.of(0)]), [3]) for i in range(3) ]
                if isCompact:
                    pc0 = Pointer(dst[dL.of(0),dR.of(0)])
                    pc1 = Pointer(dst[dL.of(1),dR.of(1)])
                    pc2 = Pointer(dst[dL.of(2),dR.of(2)])
                    instr0 = mmStoreuPs(mmInsertPs(nuvs[0], nuvs[1], [0,0,1,1,0,0,0,0]), pc0)
                    instr1 = mmStoreuPs(mmShufflePs(nuvs[1], nuvs[2], (1,0,2,1)), pc1)
                    instr2 = mmStoreSs(mmShufflePs(nuvs[2], nuvs[2], (3,3,3,2)), pc2)
                    instructions += [ Comment("4x4 -> 3x3 - Compact"), instr0, instr1, instr2 ]
                else:
                    instructions += [ Comment("4x4 -> 3x3 - Incompact") ]
                    for i in range(3):
                        e = mmShufflePs(nuvs[i], nuvs[i], (3,3,3,2))
                        instructions += [ mmStorelPi(nuvs[i], PointerCast("__m64", Pointer(dst[dL.of(i),dR.of(0)]))), mmStoreSs(e, Pointer(dst[dL.of(i),dR.of(2)])) ]
            elif N == 4:
                instrs = [ mmStoreuPs(mmLoaduPs(Pointer(src[sL.of(i),sR.of(0)])), Pointer(dst[dL.of(i),dR.of(0)])) for i in range(3) ]
                instructions += [ Comment("4x4 -> 2x4") ] + instrs
        elif M == 4:
            if N == 1:
                if not isCompact:
                    nuv = mmLoaduPs(Pointer(src[sL.of(0),sR.of(0)]))
                    es = [ mmShufflePs(nuv, nuv, (3,3,3,i)) for i in range(1,4) ]
                    pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4) ]
                    instr0 = mmStoreSs(nuv, pcs[0])
                    instrs = [ mmStoreSs(es[i-1], pcs[i]) for i in range(1,4) ]
                    instructions += [ Comment("4x1 -> 4x1 - (Store) Incompact"), instr0 ] + instrs
            elif N == 2:
                nuvs = [ mmLoaduPs(Pointer(src[sL.of(i),sR.of(0)]), [2,3]) for i in range(4) ]
                pcs = [ Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4) ]
                instrs = [ mmStorelPi(nuvs[i], PointerCast("__m64", pcs[i])) for i in range(4) ]
                instructions += [ Comment("4x4 -> 4x2") ] + instrs
            elif N == 3:
                nuvs = [ mmLoaduPs(Pointer(src[sL.of(i),sR.of(0)]), [3]) for i in range(4) ]
                if isCompact:
                    pc0 = Pointer(dst[dL.of(0),dR.of(0)])
                    pc1 = Pointer(dst[dL.of(1),dR.of(1)])
                    pc2 = Pointer(dst[dL.of(2),dR.of(2)])
                    instr0 = mmStoreuPs(mmInsertPs(nuvs[0], nuvs[1], [0,0,1,1,0,0,0,0]), pc0)
                    instr1 = mmStoreuPs(mmShufflePs(nuvs[1], nuvs[2], (1,0,2,1)), pc1)
                    instr2 = mmStoreuPs(mmShiftPs(nuvs[3], mmShufflePs(nuvs[2], nuvs[2], (2,3,3,3)), 3), pc2)
                    instructions += [ Comment("4x4 -> 4x3 - Compact"), instr0, instr1, instr2 ]
                else:
                    instructions += [ Comment("4x4 -> 4x3 - Incompact") ]
                    for i in range(4):
                        e = mmShufflePs(nuvs[i], nuvs[i], (3,3,3,2))
                        instructions += [ mmStorelPi(nuvs[i], PointerCast("__m64", Pointer(dst[dL.of(i),dR.of(0)]))), mmStoreSs(e, Pointer(dst[dL.of(i),dR.of(2)])) ]

        for i in instructions:
            i.bounds.update(mParams['bounds'])                
        return instructions

class SSE4_1LoadReplacer(LoadReplacer):
    def __init__(self, opts):
        super(SSE4_1LoadReplacer, self).__init__(opts)

    def ScaLoad(self, src, repList, bounds): 
        '''
        src is the ScaLoad object we want to replace. 
        repList is a list of tuples (line, dst). The dst elements of the tuples are store commands.
        '''
        sList = sorted(repList, key=lambda t: t[0], reverse=True)
        isFlt = (self.opts['precision'] == 'float')
        if src.pointer.at[1] == 0:
            return mmCvtssf32(mmLoaduPs(sList[0][1].pointer)) if isFlt else mmCvtsdf64(mmLoaduPd(sList[0][1].pointer))
        if isFlt: 
            return mmCvtssf32(mmShufflePs(mmLoaduPs(sList[0][1].pointer), mmLoaduPs(sList[0][1].pointer), (0, 0, 0, src.pointer.at[1])))
        return mmCvtsdf64(mmShufflePd(mmLoaduPd(sList[0][1].pointer), mmLoaduPd(sList[0][1].pointer), (0, src.pointer.at[1])))

    def mmLoad1Ps(self, src, repList, bounds):
        sList = sorted(repList, key=lambda t: t[0], reverse=True)
        dst = sList[0][1]
        if dst.reglen == 4 and dst.mrmap == [0,1,2,3]:
            at = src.pointer.getAt()
            direct = 1 if src.pointer.getMat().size[1].subs(bounds) > 1 else 0   # Temp solution
            sel = at[direct]%4
            return mmShufflePs(mmLoaduPs(dst.pointer), mmLoaduPs(dst.pointer), (sel,sel,sel,sel))
        else:
            raise Exception('Cannot load-replace!')

    def mmLoaduPs(self, src, repList, bounds):
        sList = sorted(repList, key=lambda t: t[0], reverse=True)
        if len(sList) >= 2: 
            dstList = [ t[1] for t in sList[0:2]]
            addSList = sorted(dstList, key = lambda dst: dst.pointer, reverse=True) #higher pointer to lower
            if addSList[1].reglen == 4 and addSList[0].reglen == 4 and addSList[1].mrmap == [0,1] and addSList[0].mrmap == [0]:
                return mmShufflePs(mmLoadlPi(mmSetzeroPs(), addSList[1].pointer), mmLoadSs(addSList[0].pointer), (1,0,1,0))
#             else:
#                 raise Exception('Cannot load-replace!')
        if len(sList) >= 3:
            dstList = [ t[1] for t in sList[0:3]]
            addSList = sorted(dstList, key = lambda dst: dst.pointer, reverse=True) #higher pointer to lower
            if all(s.reglen == 4 and s.mrmap == m for s, m in zip(addSList, [[0,1,2,3], [0], [0,1]])):
                return mmShufflePs(mmLoadlPi(mmSetzeroPs(), PointerCast("__m64", addSList[2].pointer)), 
                            mmUnpackloPs(mmLoadSs(addSList[1].pointer), mmLoaduPs(addSList[0].pointer)), 
                            (1,0,1,0))
#             else:
#                 raise Exception('Cannot load-replace!')
        if len(sList) >= 4:
            dstList = [ t[1] for t in sList[0:4]]
            addSList = sorted(dstList, key = lambda dst: dst.pointer, reverse=True) #higher pointer to lower
            if all(map(lambda d: d.reglen == 4 and d.mrmap == [0], addSList)):
                return mmShufflePs(mmShufflePs(mmLoadSs(addSList[3].pointer),mmLoadSs(addSList[2].pointer),(1,0,1,0)), mmShufflePs(mmLoadSs(addSList[1].pointer),mmLoadSs(addSList[0].pointer),(1,0,1,0)), (1,0,1,0))
        if len(sList) >= 1 and sList[0][1].mrmap == [0,1,2,3]:
            return src
#         else:
        raise Exception('Cannot load-replace!')

class SSE4_1(ISA):
    def __init__(self, opts):
        super(SSE4_1, self).__init__()
        self.name = "SSE4.1"
        
        ssse3 = SSSE3(opts)
        
        fp_m128 = { 'type': '__m128' }
        fp_m128['arith'] = [ mmDpPs ]
        fp_m128['load']  = [ ]
        fp_m128['misc']  = [ mmBlendPs, mmInsertPs ]
        fp_m128['cvt']   = [ ]
        fp_m128['set']   = [ ]
        fp_m128['move']  = [ ]
        fp_m128['store'] = [ ]
        fp_m128['loader'] = _Flt4Loader()
        fp_m128['nublac'] = _Flt4BLAC()
        fp_m128['storer'] = _Flt4Storer()
        fp_m128['loadreplacer'] = SSE4_1LoadReplacer(opts)

        self.updateType(fp_m128, ssse3.types['fp'][('float',4)], ['arith', 'load', 'misc', 'cvt', 'set', 'move', 'store'])
        
        self.types = { 'fp': { ('float', 4): fp_m128} }

    