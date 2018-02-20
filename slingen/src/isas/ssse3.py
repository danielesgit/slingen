'''
Created on Apr 18, 2012

@author: danieles
'''

from itertools import count
from islpy import Set, Map
from sympy import sympify

from src.dsls.ll import Matrix, ZeroMatrix

from src.irbase import RValue, Pointer, AddressOf, PointerDest, ForLoop, Comment, IBlock, sa,\
    MovStatement
from src.isas.isabase import ISA, Loader, Storer, LoadReplacer
from src.isas.sse3 import SSE3 
from src.isas.sse import mmShufflePs, mmSetzeroPs, mmStoreuPs, mmMovehlPs, mmMovelhPs, mmAddPs, mmMulPs, \
                         mmUnpackloPs, mmLoadGs, mmUnpackhiPs, mmStoreGs, mmMoveSs, mmHaddPs 
from src.isas.sse2 import mmBsrliSi128
                            
# from src.irbase import *
# from src.isas.isabase import *
# from src.isas.x86 import *
# from src.isas.sse import *
# from src.isas.sse2 import *
# from src.isas.sse3 import *

class mmShiftPs(RValue): # Only until integer ISA is introduced
    def __init__(self, src0, src1, fCount):
        super(mmShiftPs, self).__init__()
        self.srcs += [ src0, src1 ]
        self.fCount = fCount # number of floats position the combination [src1 | src0 ] should be shifted to the left

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        conc = src1 + src0;
        if self.fCount >= 8:
            res = [ '0' ]*4
        else:
            res = conc[self.fCount:]
            if len(res) >= 4:
                res = res[:4]
            else:
                res = res + ['0']*(4-len(res))
        return res

    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        conc = s1ZMask + s0ZMask;
        if self.fCount >= 8:
            res = [ 1 ]*4
        else:
            res = conc[self.fCount:]
            if len(res) >= 4:
                res = res[:4]
            else:
                res = res + [ 1 ]*(4-len(res))
        return res

    def unparse(self, indent):
        s0 = "_mm_castps_si128(" + self.srcs[0].unparse("") + ")"
        s1 = "_mm_castps_si128(" + self.srcs[1].unparse("") + ")"
        return indent + "_mm_castsi128_ps(_mm_alignr_epi8(" + s0 + ", " + s1 + ", " + str(4*self.fCount) + "))" 

    def printInst(self, indent):
        return indent + "mmShiftPs( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + ", " + str(self.fCount) + " )"

def _mmBlendPs(v1, v2, mask):
    ''' Simulation of _mmBlendPs (SSE4.1) in SSSE3. '''
    if mask == (1,0,0,0): # MSB -> LSB (res should be: [ v1[0], v1[1], v1[2], v2[3] ])
        return mmShufflePs(v1, mmUnpackhiPs(v1, v2), (3, 0, 1, 0))
    else:
        raise Exception('Unsupported mask %r for mmBlendPs simulation in SSSE3' % mask)

def _mmInsertPs(v1, v2, mask):
    if mask == [0,0,1,1,0,0,0,0]: # MSB -> LSB (res should be: [ v1[0], v1[1], v1[2], v2[0] ])
        return mmShufflePs(v1, mmMoveSs(v1, v2), (0, 2, 1, 0))
    else:
        raise Exception('Unsupported mask %r for mmInsertPs simulation in SSSE31' % mask)

class SSSE3MemCpy(MovStatement):
    def __init__(self, src, dst, numbytes):
        super(SSSE3MemCpy, self).__init__()
        self.dst = PointerDest(dst) if isinstance(dst, Pointer) else dst
        self.srcs += [ src ]
        self.numbytes = numbytes
        
    def unparse(self, indent):
        return indent + "memcpy(" + self.dst.unparse("") + ", " + self.srcs[0].unparse("") + "," + str(self.numbytes) + ");"
    
    def printInst(self, indent):
        return indent + "SSSE3MemCpy( " + self.srcs[0].printInst("") + ", " + self.dst.printInst("") + ", " + str(self.numbytes) + " )"

#     @staticmethod
#     def canStore(reglen, mrmap, horizontal=True, isAligned=False):
#         return False  
#     
#     @staticmethod
#     def getStore(src, dst):
#         return Mov(src, dst)

class _Flt4Loader(Loader):
    def __init__(self):
        super(_Flt4Loader, self).__init__()
    
    def loadMatrix(self, mParams):
        src, dst = mParams['m'], mParams['nuM']
        sL, sR = mParams['mL'], mParams['mR']
        dL, dR = mParams['nuML'], mParams['nuMR']
        M, N = mParams['M'], mParams['N']
        isCompact, isCorner = mParams['compact'], mParams['corner']
        mStruct, mAccess = mParams['struct'], mParams['access']
        instructions = []
        
        if (len(mStruct) == 1 and Matrix in mStruct) or (M!=N):
            if M == 1:
                if N == 1:
#                     v0 = mmLoadGs(AddressOf(sa(src[sL.of(0),sR.of(0)])), [0], isCompact, isCorner)
                    pa = AddressOf(sa(src[sL.of(0),sR.of(0)]))
                    pc = Pointer(dst[dL.of(0),dR.of(0)])
                    if mParams['bcast']:
                        v0 = mmLoadGs(pa, [tuple(range(4))], isCompact, isCorner)
                    else:
                        v0 = mmLoadGs(pa, [0], isCompact, isCorner)
                    instr = mmStoreGs(v0, pc, [0, 1, 2, 3])
                    instructions.extend([Comment("1x1 -> 1x4"), instr])
                elif N in [2, 3]:
                    v = mmLoadGs(Pointer(src[sL.of(0),sR.of(0)]), range(N), isCompact, isCorner)
                    pc = Pointer(dst[dL.of(0),dR.of(0)])
                    instr = mmStoreGs(v, pc, [0, 1, 2, 3])
                    instructions.extend([Comment("1x%d -> 1x4 - Corner" % N), instr])
            elif (M in [2, 3] or M == 4 and not isCompact) and N == 1:
                v = mmLoadGs(Pointer(src[sL.of(0),sR.of(0)]), range(M), isCompact, isCorner, horizontal=False)
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                comm = Comment('%dx1 -> 4x1 - %s' % (M, 'Compact' if isCompact else 'Incompact'))
                instr = mmStoreGs(v, pc, range(4))
                instructions.extend([comm, instr])
            elif M > 1 and N > 1 and mAccess.intersect(Map("{[i,j]->[i,j]}")) == mAccess and not (M == 4 and N == 4):
#                 if M == N and mAccess != Map("{[i,j]->[i,j]: 0<=i,j<4}"):
#                 else:
                vs = [mmLoadGs(Pointer(src[sL.of(i),sR.of(0)]), range(N), isCompact, isCorner=False) for i in range(0, M-1)]
                vs.append(mmLoadGs(Pointer(src[sL.of(M-1),sR.of(0)]), range(N), isCompact, isCorner))
                vs.extend([mmSetzeroPs() for _ in range(M, 4)])
                pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
                comm = Comment('%dx%d -> 4x4 - %s' % (M, N, 'Compact' if isCompact else 'Incompact'))
                instrs = [mmStoreGs(v, pc, [0, 1, 2, 3]) for v, pc in zip(vs, pcs)]
                instructions.extend([comm] + instrs)
            elif M == N and mAccess.intersect(Map("{[i,j]->[i,j]}")) != mAccess: #mAccess != Map("{[i,j]->[i,j]}"):
                if mAccess == Map("{[i,j]->[i,j]: j<=i}").union(Map("{[i,j]->[j,i]: j>i}")):
                    #LSymm
                    vs = [mmLoadGs(Pointer(src[sL.of(i),sR.of(0)]), range(i+1), isCompact, isCorner=False) for i in range(0, M-1)]
                    vs.append(mmLoadGs(Pointer(src[sL.of(M-1),sR.of(0)]), range(M), isCompact, isCorner))
                    vs.extend([mmSetzeroPs() for _ in range(M, 4)])
                    rows = [ mmShufflePs(mmShufflePs(vs[0], vs[1], (0,0,0,0)), mmShufflePs(vs[2], vs[3], (0,0,0,0)), (2,0,2,0)) ]
                    rows.append(mmShufflePs(vs[1], mmShufflePs(vs[2], vs[3], (1,1,1,1)), (2,0,1,0)))
                    rows.append(mmShufflePs(vs[2], mmUnpackhiPs(vs[2], vs[3]), (1,0,1,0)))
                    rows.append(vs[3])
                    pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
                    comm = Comment('%dx%d -> 4x4 - %s' % (M, N, 'LowSymm'))
                    instrs = [mmStoreGs(v, pc, [0, 1, 2, 3]) for v, pc in zip(rows, pcs)]
                    instructions.extend([comm] + instrs)
                elif mAccess == Map("{[i,j]->[j,i]: j<i}").union(Map("{[i,j]->[i,j]: j>=i}")):
                    #USymm
                    vs = [mmLoadGs(Pointer(src[sL.of(i),sR.of(i)]), range(i,M), isCompact, isCorner=False) for i in range(M-1)]
                    vs.append(mmLoadGs(Pointer(src[sL.of(M-1),sR.of(M-1)]), [M-1], isCompact, isCorner))
                    vs.extend([mmSetzeroPs() for _ in range(M, 4)])
                    rows = [ vs[0] ]
                    rows.append(mmShufflePs(mmUnpackloPs(vs[0], vs[1]), vs[1], (3,2,3,2)))
                    rows.append(mmShufflePs(mmShufflePs(vs[0], vs[1], (2,2,2,2)), vs[2], (3,2,2,0)))
                    rows.append(mmShufflePs(mmShufflePs(vs[0], vs[1], (3,3,3,3)), mmShufflePs(vs[2], vs[3], (3,3,3,3)), (2,0,2,0)))
                    pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
                    comm = Comment('%dx%d -> 4x4 - %s' % (M, N, 'UpSymm'))
                    instrs = [mmStoreGs(v, pc, [0, 1, 2, 3]) for v, pc in zip(rows, pcs)]
                    instructions.extend([comm] + instrs)
        elif len(mStruct) == 2:
            if Matrix in mStruct and ZeroMatrix in mStruct and M==N:
                if mStruct[Matrix] == Set("{[i,j]: 0<=i<"+str(M)+" and 0<=j<=i}") and mStruct[ZeroMatrix] == Set("{[i,j]: 0<=i<"+str(M)+" and i<j<"+str(M)+"}"):
                    #LowerTriang 
                    vs = [mmLoadGs(Pointer(src[sL.of(i),sR.of(0)]), range(i+1), isCompact, isCorner=False) for i in range(M-1)]
                    vs.append(mmLoadGs(Pointer(src[sL.of(M-1),sR.of(0)]), range(M), isCompact, isCorner))
                    vs.extend([mmSetzeroPs() for _ in range(M, 4)])
                    pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
                    comm = Comment('%dx%d -> 4x4 - %s' % (M, N, 'LowTriang'))
                    instrs = [mmStoreGs(v, pc, [0, 1, 2, 3]) for v, pc in zip(vs, pcs)]
                    instructions.extend([comm] + instrs)
                elif mStruct[Matrix] == Set("{[i,j]: 0<=i<"+str(M)+" and i<=j<"+str(M)+"}") and mStruct[ZeroMatrix] == Set("{[i,j]: 0<=i<"+str(M)+" and 0<=j<i}"):
                    #UpperTriang 
                    vs = [mmLoadGs(Pointer(src[sL.of(i),sR.of(i)]), range(i,M), isCompact, isCorner=False) for i in range(M-1)]
                    vs.append(mmLoadGs(Pointer(src[sL.of(M-1),sR.of(M-1)]), [M-1], isCompact, isCorner))
                    vs.extend([mmSetzeroPs() for _ in range(M, 4)])
                    pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
                    comm = Comment('%dx%d -> 4x4 - %s' % (M, N, 'UpperTriang'))
                    instrs = [mmStoreGs(v, pc, [0, 1, 2, 3]) for v, pc in zip(vs, pcs)]
                    instructions.extend([comm] + instrs)

        for i in instructions:
            i.bounds.update(mParams['bounds'])
        return instructions

class _Flt4BLAC(object):
    def __init__(self):
        super(_Flt4BLAC, self).__init__()

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

        instructions += [ Comment(str(nu) + "Copy-BLAC: " + str(M) + "x" + str(N)) ]
        if M*N == nu:
            va = mmLoadGs(Pointer(src[sL.of(0),sR.of(0)]), [0, 1, 2, 3])
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            instr = mmStoreGs(va, pc, [0, 1, 2, 3])
            instructions.append(instr)
        elif M == nu and N == nu:
            vas = [mmLoadGs(Pointer(src[sL.of(i),sR.of(0)]), [0, 1, 2, 3]) for i in range(4)]
            pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
            instrs = [mmStoreGs(va, pc, [0, 1, 2, 3]) for va, pc in zip(vas, pcs)]
            instructions.extend(instrs)
        
        for i in instructions:
            i.bounds.update(dParams['bounds'])                
        return instructions
    
    def Add(self, s0Params, s1Params, dParams, opts):
        
        nu = 4
        # these are the 3 Matrix objects involved
        src0, src1, dst = s0Params['nuM'], s1Params['nuM'], dParams['nuM']
        # these are the index functions for the two dimensions of each of the three matrices
        s0L, s0R = s0Params['nuML'], s0Params['nuMR']
        s1L, s1R = s1Params['nuML'], s1Params['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        # these are the sizes of the matrices
        M, N     = dParams['nuMM'], dParams['nuMN']
        instructions = []

        instructions += [ Comment(str(nu) + "-BLAC: " + str(M) + "x" + str(N) + " + " + str(M) + "x" + str(N)) ]
        if M*N == nu:
            va = mmLoadGs(Pointer(src0[s0L.of(0),s0R.of(0)]), [0, 1, 2, 3])
            vb = mmLoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), [0, 1, 2, 3])
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            instr = mmStoreGs(mmAddPs(va, vb), pc, [0, 1, 2, 3])
            instructions.append(instr)
        elif M == nu and N == nu:
            vas = [mmLoadGs(Pointer(src0[s0L.of(i),s0R.of(0)]), [0, 1, 2, 3]) for i in range(4)]
            vbs = [mmLoadGs(Pointer(src1[s1L.of(i),s1R.of(0)]), [0, 1, 2, 3]) for i in range(4)]
            pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
            instrs = [mmStoreGs(mmAddPs(va, vb), pc, [0, 1, 2, 3]) for va, vb, pc in zip(vas, vbs, pcs)]
            instructions.extend(instrs)
        
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
        if oM*oK*oN*oP == 1: # case 1x1 Kron 1x1
            va = mmLoadGs(Pointer(src0[s0L.of(0),s0R.of(0)]), [0, 1, 2, 3])
            vb = mmLoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), [0, 1, 2, 3])
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            instr = mmStoreGs(mmMulPs(va, vb), pc, [0, 1, 2, 3])
            instructions.append(instr)
        elif oM*oK == 1:
            if s0Params['bcast']:
                dup = mmLoadGs(Pointer(src0[s0L.of(0),s0R.of(0)]), range(nu))
            else:
                va = mmLoadGs(Pointer(src0[s0L.of(0),s0R.of(0)]), [0, 1, 2, 3])
                dup = mmShufflePs(va, va, (0,0,0,0))

            if N*P == nu: # case 1x1 Kron NxP, where N*P=nu
#                 va = mmLoadGs(Pointer(src0[s0L.of(0),s0R.of(0)]), [0, 1, 2, 3])
#                 dup = mmShufflePs(va, va, (0,0,0,0)) # SSE instruction: move lowest doubleword of va to all doublewords of result
                vb = mmLoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), [0, 1, 2, 3])
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = mmStoreGs(mmMulPs(dup, vb), pc, [0, 1, 2, 3])
                instructions.append(instr)
            else: # case 1x1 Kron nuxnu
#                 va = mmLoadGs(Pointer(src0[s0L.of(0),s0R.of(0)]), [0, 1, 2, 3])
#                 dup = mmShufflePs(va, va, (0,0,0,0))
                for i in range(nu):
                    vb = mmLoadGs(Pointer(src1[s1L.of(i),s1R.of(0)]), [0, 1, 2, 3])
                    pc = Pointer(dst[dL.of(i),dR.of(0)])
                    instr = mmStoreGs(mmMulPs(dup, vb), pc, [0, 1, 2, 3])
                    instructions.append(instr)
        else:
            if s1Params['bcast']:
                dup = mmLoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu))
            else:
                vb = mmLoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), [0, 1, 2, 3])
                dup = mmShufflePs(vb, vb, (0,0,0,0))

            if M*K == nu: # case MxK Kron 1x1, where M*K=nu
#                 vb = mmLoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), [0, 1, 2, 3])
#                 dup = mmShufflePs(vb, vb, (0,0,0,0))
                va = mmLoadGs(Pointer(src0[s0L.of(0),s0R.of(0)]), [0, 1, 2, 3])
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = mmStoreGs(mmMulPs(va, dup), pc, [0, 1, 2, 3])
                instructions.append(instr)
            else: # case nuxnu Kron 1x1
#                 vb = mmLoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), [0, 1, 2, 3])
#                 dup = mmShufflePs(vb, vb, (0,0,0,0))
                for i in range(nu):
                    va = mmLoadGs(Pointer(src0[s0L.of(i),s0R.of(0)]), [0, 1, 2, 3])
                    pc = Pointer(dst[dL.of(i),dR.of(0)])
                    instr = mmStoreGs(mmMulPs(va, dup), pc, [0, 1, 2, 3])
                    instructions.append(instr)
        
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
            if N == 1: # 1xnu * nux1
                va = mmLoadGs(Pointer(src0[s0L.of(0),s0R.of(0)]), [0, 1, 2, 3])
                vb = mmLoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), [0, 1, 2, 3])
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                mul1 = mmMulPs(va, vb)
                mul2 = mmHaddPs(mul1, mul1)
                instr = mmStoreGs(mmHaddPs(mul2, mul2), pc, [0, 1, 2, 3])
                instructions.append(instr)
            else: # 1xnu * nuxnu
                vb0 = mmLoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), [0, 1, 2, 3])
                vb1 = mmLoadGs(Pointer(src1[s1L.of(1),s1R.of(0)]), [0, 1, 2, 3])
                vb2 = mmLoadGs(Pointer(src1[s1L.of(2),s1R.of(0)]), [0, 1, 2, 3])
                vb3 = mmLoadGs(Pointer(src1[s1L.of(3),s1R.of(0)]), [0, 1, 2, 3])

                va00 = mmLoadGs(Pointer(src0[s0L.of(0),s0R.of(0)]), [(0, 1, 2, 3)])
                va01 = mmLoadGs(Pointer(src0[s0L.of(0),s0R.of(1)]), [(0, 1, 2, 3)])
                va02 = mmLoadGs(Pointer(src0[s0L.of(0),s0R.of(2)]), [(0, 1, 2, 3)])
                va03 = mmLoadGs(Pointer(src0[s0L.of(0),s0R.of(3)]), [(0, 1, 2, 3)])
                mul0 = mmMulPs(va00, vb0)
                mul1 = mmMulPs(va01, vb1)
                add0 = mmAddPs(mul0, mul1)
                mul2 = mmMulPs(va02, vb2)
                mul3 = mmMulPs(va03, vb3)
                add1 = mmAddPs(mul2, mul3)
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = mmStoreGs(mmAddPs(add0, add1), pc, [0, 1, 2, 3])
                instructions.append(instr)
        else:
            if K == 1: # nux1 * 1xnu
                va0 = mmLoadGs(Pointer(src0[s0L.of(0),s0R.of(0)]), [(0, 1, 2, 3)])
                va1 = mmLoadGs(Pointer(src0[s0L.of(1),s0R.of(0)]), [(0, 1, 2, 3)])
                va2 = mmLoadGs(Pointer(src0[s0L.of(2),s0R.of(0)]), [(0, 1, 2, 3)])
                va3 = mmLoadGs(Pointer(src0[s0L.of(3),s0R.of(0)]), [(0, 1, 2, 3)])
                vb = mmLoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), [0, 1, 2, 3])
                pc0 = Pointer(dst[dL.of(0),dR.of(0)])
                pc1 = Pointer(dst[dL.of(1),dR.of(0)])
                pc2 = Pointer(dst[dL.of(2),dR.of(0)])
                pc3 = Pointer(dst[dL.of(3),dR.of(0)])
                instr0 = mmStoreGs(mmMulPs(va0, vb), pc0, [0, 1, 2, 3])
                instr1 = mmStoreGs(mmMulPs(va1, vb), pc1, [0, 1, 2, 3])
                instr2 = mmStoreGs(mmMulPs(va2, vb), pc2, [0, 1, 2, 3])
                instr3 = mmStoreGs(mmMulPs(va3, vb), pc3, [0, 1, 2, 3])
                instructions.extend([instr0, instr1, instr2, instr3])
            else:
                if N == 1: # nuxnu * nux1
                    va0 = mmLoadGs(Pointer(src0[s0L.of(0),s0R.of(0)]), [0, 1, 2, 3])
                    va1 = mmLoadGs(Pointer(src0[s0L.of(1),s0R.of(0)]), [0, 1, 2, 3])
                    va2 = mmLoadGs(Pointer(src0[s0L.of(2),s0R.of(0)]), [0, 1, 2, 3])
                    va3 = mmLoadGs(Pointer(src0[s0L.of(3),s0R.of(0)]), [0, 1, 2, 3])
                    vb = mmLoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), [0, 1, 2, 3])
                    mul0 = mmMulPs(va0, vb)
                    mul1 = mmMulPs(va1, vb)
                    mul2 = mmMulPs(va2, vb)
                    mul3 = mmMulPs(va3, vb)
                    hadd0 = mmHaddPs(mul0, mul1)
                    hadd1 = mmHaddPs(mul2, mul3)
                    pc = Pointer(dst[dL.of(0),dR.of(0)])
                    instr = mmStoreGs(mmHaddPs(hadd0, hadd1), pc, [0, 1, 2, 3])
                    instructions.append(instr)
                else: # nuxnu * nuxnu
                    vb0 = mmLoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), [0, 1, 2, 3])
                    vb1 = mmLoadGs(Pointer(src1[s1L.of(1),s1R.of(0)]), [0, 1, 2, 3])
                    vb2 = mmLoadGs(Pointer(src1[s1L.of(2),s1R.of(0)]), [0, 1, 2, 3])
                    vb3 = mmLoadGs(Pointer(src1[s1L.of(3),s1R.of(0)]), [0, 1, 2, 3])
                    for i in range(nu):
                        vai0 = mmLoadGs(Pointer(src0[s0L.of(i),s0R.of(0)]), [(0, 1, 2, 3)])
                        vai1 = mmLoadGs(Pointer(src0[s0L.of(i),s0R.of(1)]), [(0, 1, 2, 3)])
                        vai2 = mmLoadGs(Pointer(src0[s0L.of(i),s0R.of(2)]), [(0, 1, 2, 3)])
                        vai3 = mmLoadGs(Pointer(src0[s0L.of(i),s0R.of(3)]), [(0, 1, 2, 3)])
                        mul0 = mmMulPs(vai0, vb0)
                        mul1 = mmMulPs(vai1, vb1)
                        add0 = mmAddPs(mul0, mul1)
                        mul2 = mmMulPs(vai2, vb2)
                        mul3 = mmMulPs(vai3, vb3)
                        add1 = mmAddPs(mul2, mul3)
                        pc = Pointer(dst[dL.of(i),dR.of(0)])
                        instr = mmStoreGs(mmAddPs(add0, add1), pc, [0, 1, 2, 3])
                        instructions.append(instr)
        
        for i in instructions:
            i.bounds.update(dParams['bounds'])
        return instructions
    
    def PMul(self, s0Params, s1Params, dParams, opts):

        nu = 4
        src0, src1, dst = s0Params['nuM'], s1Params['nuM'], dParams['nuM']
        s0L, s0R = s0Params['nuML'], s0Params['nuMR']
        s1L, s1R = s1Params['nuML'], s1Params['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        M, K, N = s0Params['nuMM'], s0Params['nuMN'], s1Params['nuMN']
        instructions = []

        instructions += [ Comment(str(nu) + "-BLAC: " + str(M) + "x" + str(K) + " % " + str(K) + "x" + str(N)) ]
        if K > 1:
            vas = [mmLoadGs(Pointer(src0[s0L.of(i),s0R.of(0)]), [0, 1, 2, 3]) for i in range(M)]
            vb = mmLoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), [0, 1, 2, 3])
            pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(M)]
            muls = [mmMulPs(va, vb) for va in vas]
            instrs = [mmStoreGs(mul, pc, [0, 1, 2, 3]) for mul, pc in zip(muls, pcs)]
        else:
            va = mmLoadGs(Pointer(src0[s0L.of(0),s0R.of(0)]), [0, 1, 2, 3])
            vb = mmLoadGs(Pointer(src1[s1L.of(0),s1R.of(0)]), [(0, 1, 2, 3)])
            pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(nu)]
            mul = mmMulPs(va, vb)
            zeros = mmSetzeroPs()
            ress = [mmMoveSs(zeros, mul)]
            for i in range(1,4):
                mulnew = mmBsrliSi128(mul, i)
                ress.append(mmMoveSs(zeros, mulnew))
            instrs = [mmStoreGs(res, pc, [0, 1, 2, 3]) for res, pc in zip(ress, pcs)]
        instructions.extend(instrs)
        
        for i in instructions:
            i.bounds.update(dParams['bounds'])
        return instructions
    
    def HRed(self, sParams, dParams, opts):

        nu = 4
        src, dst = sParams['nuM'], dParams['nuM']
        sL, sR = sParams['nuML'], sParams['nuMR']
        dL, dR = dParams['nuML'], dParams['nuMR']
        M, N = dParams['nuMM'], dParams['nuMN']
        instructions = []

        instructions += [ Comment(str(nu) + "-BLAC: HRed(" + str(M) + "x" + str(N) + ")") ]
        if M == 1:
            va = mmLoadGs(Pointer(src[sL.of(0),sR.of(0)]), [0, 1, 2, 3])
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            tmp = mmHaddPs(va, va)
            instr = mmStoreGs(mmHaddPs(tmp, tmp), pc, [0, 1, 2, 3])
            instructions.append(instr)
        else: # M == nu
            vas = [mmLoadGs(Pointer(src[sL.of(i),sR.of(0)]), [0, 1, 2, 3]) for i in range(nu)]
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            tmp01 = mmHaddPs(vas[0], vas[1])
            tmp23 = mmHaddPs(vas[2], vas[3])
            res = mmHaddPs(tmp01, tmp23)
            instr = mmStoreGs(res, pc, [0, 1, 2, 3])
            instructions.append(instr)
        
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
            va = mmLoadGs(Pointer(src[sL.of(0),sR.of(0)]), [0, 1, 2, 3])
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            instr = mmStoreuPs(va, pc)
            instructions += [ instr ]
        else:
            va0 = mmLoadGs(Pointer(src[sL.of(0),sR.of(0)]), [0, 1, 2, 3])
            va1 = mmLoadGs(Pointer(src[sL.of(1),sR.of(0)]), [0, 1, 2, 3])
            va2 = mmLoadGs(Pointer(src[sL.of(2),sR.of(0)]), [0, 1, 2, 3])
            va3 = mmLoadGs(Pointer(src[sL.of(3),sR.of(0)]), [0, 1, 2, 3])
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
            instr0 = mmStoreGs(col0, pc0, [0, 1, 2, 3])
            instr1 = mmStoreGs(col1, pc1, [0, 1, 2, 3])
            instr2 = mmStoreGs(col2, pc2, [0, 1, 2, 3])
            instr3 = mmStoreGs(col3, pc3, [0, 1, 2, 3])
            instructions.extend([instr0, instr1, instr2, instr3])
        
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
        mStruct, mAccess = mParams['struct'], mParams['access']
        instructions = []
        
        if (len(mStruct) == 1 and Matrix in mStruct) or (M!=N):
            if M == 1:
                if N == 1:
                    nuv = mmLoadGs(Pointer(src[sL.of(0),sR.of(0)]), [0, 1, 2, 3], zeromask=[1,2,3])
                    pc = AddressOf(sa(dst[dL.of(0),dR.of(0)]))
                    instr = mmStoreGs(nuv, pc, [0])
                    instructions.extend([Comment("1x4 -> 1x1"), instr])
                elif N in [2, 3]:
                    nuv = mmLoadGs(Pointer(src[sL.of(0),sR.of(0)]), [0, 1, 2, 3], zeromask=range(N, 4))
    #                 pc = PointerCast("__m64", Pointer(dst[dL.of(0),dR.of(0)])) if N == 2 else Pointer(dst[dL.of(0),dR.of(0)])
                    pc = Pointer(dst[dL.of(0),dR.of(0)]) 
                    instr = mmStoreGs(nuv, pc, range(N), isCompact)
                    instructions.extend([Comment("1x4 -> 1x%d - Corner" % N), instr])
            elif (M in [2, 3] or M == 4 and not isCompact) and N == 1:
                nuv = mmLoadGs(Pointer(src[sL.of(0),sR.of(0)]), [0, 1, 2, 3], isCompact, zeromask=range(M, 4))
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                comm = Comment("4x1 -> %dx1 - %s" % (M, 'Compact' if isCompact else 'Incompact'))
                instr = mmStoreGs(nuv, pc, range(M), isCompact, horizontal=False)
                instructions.extend([comm, instr])
    #         elif M > 1 and N > 1:
            elif M > 1 and N > 1 and not (M == 4 and N == 4):
                nuvs = [mmLoadGs(Pointer(src[sL.of(i),sR.of(0)]), [0, 1, 2, 3], isCompact, zeromask=range(N, 4)) for i in range(M)]
                pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(M)]
                comm = Comment("4x4 -> %dx%d - %s" % (M, N, 'Compact' if isCompact else 'Incompact'))
                instrs = [mmStoreGs(nuv, pc, range(N), isCompact) for nuv, pc in zip(nuvs, pcs)]
                instructions.extend([comm] + instrs)
            elif M == N and mAccess.intersect(Map("{[i,j]->[i,j]}")) != mAccess:
                if mAccess == Map("{[i,j]->[i,j]: j<=i}").union(Map("{[i,j]->[j,i]: j>i}")):
                    #LSymm
                    nuvs = [mmLoadGs(Pointer(src[sL.of(i),sR.of(0)]), [0, 1, 2, 3], isCompact, zeromask=range(i+1, 4)) for i in range(M)]
                    pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(M)]
                    comm = Comment("4x4 -> %dx%d - %s" % (M, N, 'LowSymm'))
                    instrs = [mmStoreGs(nuvs[i], pcs[i], range(i+1), isCompact) for i in range(M)]
                    instructions.extend([comm] + instrs)
                elif mAccess == Map("{[i,j]->[j,i]: j<i}").union(Map("{[i,j]->[i,j]: j>=i}")):
                    #USymm
                    nuvs = [mmLoadGs(Pointer(src[sL.of(i),sR.of(0)]), [0, 1, 2, 3], isCompact, zeromask=range(0, i)) for i in range(M)]
                    pcs = [Pointer(dst[dL.of(i),dR.of(i)]) for i in range(M)]
                    comm = Comment("4x4 -> %dx%d - %s" % (M, N, 'UpSymm'))
                    instrs = [mmStoreGs(nuvs[i], pcs[i], range(i,M), isCompact) for i in range(M)]
                    instructions.extend([comm] + instrs)
        elif len(mStruct) == 2:
            if Matrix in mStruct and ZeroMatrix in mStruct and M==N:
                if mStruct[Matrix] == Set("{[i,j]: 0<=i<"+str(M)+" and 0<=j<=i}") and mStruct[ZeroMatrix] == Set("{[i,j]: 0<=i<"+str(M)+" and i<j<"+str(M)+"}"):
                    #LowerTriang 
                    nuvs = [mmLoadGs(Pointer(src[sL.of(i),sR.of(0)]), [0, 1, 2, 3], isCompact, zeromask=range(i+1, 4)) for i in range(M)]
                    pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(M)]
                    comm = Comment("4x4 -> %dx%d - %s" % (M, N, 'LowTriang'))
                    instrs = [mmStoreGs(nuvs[i], pcs[i], range(i+1), isCompact) for i in range(M)]
                    instructions.extend([comm] + instrs)
                elif mStruct[Matrix] == Set("{[i,j]: 0<=i<"+str(M)+" and i<=j<"+str(M)+"}") and mStruct[ZeroMatrix] == Set("{[i,j]: 0<=i<"+str(M)+" and 0<=j<i}"):
                    #UpperTriang 
                    nuvs = [mmLoadGs(Pointer(src[sL.of(i),sR.of(0)]), [0, 1, 2, 3], isCompact, zeromask=range(0, i)) for i in range(M)]
                    pcs = [Pointer(dst[dL.of(i),dR.of(i)]) for i in range(M)]
                    comm = Comment("4x4 -> %dx%d - %s" % (M, N, 'UpTriang'))
                    instrs = [mmStoreGs(nuvs[i], pcs[i], range(i,M), isCompact) for i in range(M)]
                    instructions.extend([comm] + instrs)
        for i in instructions:
            i.bounds.update(mParams['bounds'])
        return instructions

class _Packer(object):
    def __init__(self, opts):
        self.opts = opts
        self.counter = count()
        hdr = "<string.h>"
        if not hdr in self.opts['includefiles']:
            self.opts['includefiles'].append(hdr)
    
    def pack(self, mParams):
        src, dst = mParams[0]['m'], mParams[1]['m']
        sL, sR = mParams[0]['mL'], mParams[0]['mR']
        dL, dR = mParams[1]['mL'], mParams[1]['mR']
        M, N = mParams[1]['M'], mParams[1]['N']
        isCompact = mParams[0]['compact']
        mStruct, mAccess = mParams[1]['struct'], mParams[1]['access']
        instructions = []
        
        if (len(mStruct) == 1 and Matrix in mStruct) or (M!=N):
            if mAccess.intersect(Map("{[i,j]->[i,j]}")) == mAccess:
                if isCompact:
                    c = SSSE3MemCpy(Pointer(src[sL.of(0),sR.of(0)]), Pointer(dst[dL.of(0),dR.of(0)]), M*N*self.opts['sdata'])
                    instructions.append(c)
                else:
                    idx = "pck"+str(self.counter.next())
                    sidx = sympify(idx)
                    f = ForLoop(idx, sympify(0), M-1, sympify(1))
                    c = SSSE3MemCpy(Pointer(src[sL.of(sidx),sR.of(0)]), Pointer(dst[dL.of(sidx),dR.of(0)]), N*self.opts['sdata'])
                    temp = IBlock()
                    temp.instructions += [ c ]
                    f.blocks += [ temp ]
                    instructions.append(f)
            elif M == N and mAccess.intersect(Map("{[i,j]->[i,j]}")) != mAccess: #mAccess != Map("{[i,j]->[i,j]}"):
                if mAccess == Map("{[i,j]->[i,j]: j<=i}").union(Map("{[i,j]->[j,i]: j>i}")):
                    #LSymm
                    idx = "pck"+str(self.counter.next())
                    sidx = sympify(idx)
                    f = ForLoop(idx, sympify(0), M-1, sympify(1))
                    c = SSSE3MemCpy(Pointer(src[sL.of(sidx),sR.of(0)]), Pointer(dst[dL.of(sidx),dR.of(0)]), (sidx+1)*self.opts['sdata'])
                    temp = IBlock()
                    temp.instructions += [ c ]
                    f.blocks += [ temp ]
                    instructions.append(f)
                elif mAccess == Map("{[i,j]->[j,i]: j<i}").union(Map("{[i,j]->[i,j]: j>=i}")):
                    #USymm
                    idx = "pck"+str(self.counter.next())
                    sidx = sympify(idx)
                    f = ForLoop(idx, sympify(0), M-1, sympify(1))
                    c = SSSE3MemCpy(Pointer(src[sL.of(sidx),sR.of(sidx)]), Pointer(dst[dL.of(sidx),dR.of(sidx)]), (M-sidx)*self.opts['sdata'])
                    temp = IBlock()
                    temp.instructions += [ c ]
                    f.blocks += [ temp ]
                    instructions.append(f)
        elif len(mStruct) == 2:
            if Matrix in mStruct and ZeroMatrix in mStruct and M==N:
                if mStruct[Matrix] == Set("{[i,j]: 0<=i<"+str(M)+" and 0<=j<=i}") and mStruct[ZeroMatrix] == Set("{[i,j]: 0<=i<"+str(M)+" and i<j<"+str(M)+"}"):
                    #LowerTriang 
                    idx = "pck"+str(self.counter.next())
                    sidx = sympify(idx)
                    f = ForLoop(idx, sympify(0), M-1, sympify(1))
                    c = SSSE3MemCpy(Pointer(src[sL.of(sidx),sR.of(0)]), Pointer(dst[dL.of(sidx),dR.of(0)]), (sidx+1)*self.opts['sdata'])
                    temp = IBlock()
                    temp.instructions += [ c ]
                    f.blocks += [ temp ]
                    instructions.append(f)
                elif mStruct[Matrix] == Set("{[i,j]: 0<=i<"+str(M)+" and i<=j<"+str(M)+"}") and mStruct[ZeroMatrix] == Set("{[i,j]: 0<=i<"+str(M)+" and 0<=j<i}"):
                    #UpperTriang 
                    idx = "pck"+str(self.counter.next())
                    sidx = sympify(idx)
                    f = ForLoop(idx, sympify(0), M-1, sympify(1))
                    c = SSSE3MemCpy(Pointer(src[sL.of(sidx),sR.of(sidx)]), Pointer(dst[dL.of(sidx),dR.of(sidx)]), (M-sidx)*self.opts['sdata'])
                    temp = IBlock()
                    temp.instructions += [ c ]
                    f.blocks += [ temp ]
                    instructions.append(f)

        for i in instructions:
            i.bounds.update(mParams[0]['bounds'])
        return instructions

    def unpack(self, mParams):
        src, dst = mParams[0]['m'], mParams[1]['m']
        sL, sR = mParams[0]['mL'], mParams[0]['mR']
        dL, dR = mParams[1]['mL'], mParams[1]['mR']
        M, N = mParams[0]['M'], mParams[0]['N']
        isCompact = mParams[1]['compact']
        mStruct, mAccess = mParams[0]['struct'], mParams[0]['access']
        instructions = []
        
        if (len(mStruct) == 1 and Matrix in mStruct) or (M!=N):
            if mAccess.intersect(Map("{[i,j]->[i,j]}")) == mAccess:
                if isCompact:
                    c = SSSE3MemCpy(Pointer(src[sL.of(0),sR.of(0)]), Pointer(dst[dL.of(0),dR.of(0)]), M*N*self.opts['sdata'])
                    instructions.append(c)
                else:
                    idx = "upck"+str(self.counter.next())
                    sidx = sympify(idx)
                    f = ForLoop(idx, sympify(0), M-1, sympify(1))
                    c = SSSE3MemCpy(Pointer(src[sL.of(sidx),sR.of(0)]), Pointer(dst[dL.of(sidx),dR.of(0)]), N*self.opts['sdata'])
                    temp = IBlock()
                    temp.instructions += [ c ]
                    f.blocks += [ temp ]
                    instructions.append(f)
            elif M == N and mAccess.intersect(Map("{[i,j]->[i,j]}")) != mAccess: #mAccess != Map("{[i,j]->[i,j]}"):
                if mAccess == Map("{[i,j]->[i,j]: j<=i}").union(Map("{[i,j]->[j,i]: j>i}")):
                    #LSymm
                    idx = "upck"+str(self.counter.next())
                    sidx = sympify(idx)
                    f = ForLoop(idx, sympify(0), M-1, sympify(1))
                    c = SSSE3MemCpy(Pointer(src[sL.of(sidx),sR.of(0)]), Pointer(dst[dL.of(sidx),dR.of(0)]), (sidx+1)*self.opts['sdata'])
                    temp = IBlock()
                    temp.instructions += [ c ]
                    f.blocks += [ temp ]
                    instructions.append(f)
                elif mAccess == Map("{[i,j]->[j,i]: j<i}").union(Map("{[i,j]->[i,j]: j>=i}")):
                    #USymm
                    idx = "upck"+str(self.counter.next())
                    sidx = sympify(idx)
                    f = ForLoop(idx, sympify(0), M-1, sympify(1))
                    c = SSSE3MemCpy(Pointer(src[sL.of(sidx),sR.of(sidx)]), Pointer(dst[dL.of(sidx),dR.of(sidx)]), (M-sidx)*self.opts['sdata'])
                    temp = IBlock()
                    temp.instructions += [ c ]
                    f.blocks += [ temp ]
                    instructions.append(f)
        elif len(mStruct) == 2:
            if Matrix in mStruct and ZeroMatrix in mStruct and M==N:
                if mStruct[Matrix] == Set("{[i,j]: 0<=i<"+str(M)+" and 0<=j<=i}") and mStruct[ZeroMatrix] == Set("{[i,j]: 0<=i<"+str(M)+" and i<j<"+str(M)+"}"):
                    #LowerTriang 
                    idx = "upck"+str(self.counter.next())
                    sidx = sympify(idx)
                    f = ForLoop(idx, sympify(0), M-1, sympify(1))
                    c = SSSE3MemCpy(Pointer(src[sL.of(sidx),sR.of(0)]), Pointer(dst[dL.of(sidx),dR.of(0)]), (sidx+1)*self.opts['sdata'])
                    temp = IBlock()
                    temp.instructions += [ c ]
                    f.blocks += [ temp ]
                    instructions.append(f)
                elif mStruct[Matrix] == Set("{[i,j]: 0<=i<"+str(M)+" and i<=j<"+str(M)+"}") and mStruct[ZeroMatrix] == Set("{[i,j]: 0<=i<"+str(M)+" and 0<=j<i}"):
                    #UpperTriang 
                    idx = "upck"+str(self.counter.next())
                    sidx = sympify(idx)
                    f = ForLoop(idx, sympify(0), M-1, sympify(1))
                    c = SSSE3MemCpy(Pointer(src[sL.of(sidx),sR.of(sidx)]), Pointer(dst[dL.of(sidx),dR.of(sidx)]), (M-sidx)*self.opts['sdata'])
                    temp = IBlock()
                    temp.instructions += [ c ]
                    f.blocks += [ temp ]
                    instructions.append(f)

        for i in instructions:
            i.bounds.update(mParams[0]['bounds'])
        return instructions
        
        
class _LoadReplacer(LoadReplacer):
    def __init__(self, opts):
        super(_LoadReplacer, self).__init__(opts)

    def mmLoadGs(self, src, repList, bounds):
        sList = sorted(repList, key=lambda t: t[0], reverse=True)
        dst = sList[0][1]
        if src.reglen == 4 and len(src.mrmap) == 1 and src.mrmap[0] == (0, 1, 2, 3):
            # corresponds to mmLoad1Ps
            if dst.reglen == 4 and dst.mrmap == [0,1,2,3]:
                if dst.horizontal:
                    pos = src.pointer.linIdx - dst.pointer.linIdx
                else:
                    pos = None
                    for i in range(4):
                        if Pointer((src.pointer.mat, (src.pointer.at[0] + i, src.pointer.at[1]))).eqValueFirst(src.pointer):
                            pos = i
                            break
                return mmShufflePs(mmLoadGs(dst.pointer, [0, 1, 2, 3]), mmLoadGs(dst.pointer, [0, 1, 2, 3]), 
                                   (pos, pos, pos, pos))
            else:
                raise Exception('Cannot load-replace!')
        else:
            raise Exception('Cannot load-replace!')
        
class SSSE3(ISA):
    def __init__(self, opts):
        super(SSSE3, self).__init__()
#         self.nu = [ 2 ]
#         self.types = {2: '__m128d'}
#         self.vectorize = True
        self.name = "SSSE3"
        
        sse3 = SSE3(opts)
        
        fp_m128 = { 'type': '__m128' }
        fp_m128['arith'] = [ ]
        fp_m128['load']  = [ ]
        fp_m128['misc']  = [ mmShiftPs ]
        fp_m128['cvt']   = [ ]
        fp_m128['set']   = [ ]
        fp_m128['move']  = [ ]
        fp_m128['store'] = [ ]
        fp_m128['loader'] = _Flt4Loader()
        fp_m128['nublac'] = _Flt4BLAC()
        fp_m128['storer'] = _Flt4Storer()
        fp_m128['loadreplacer'] = _LoadReplacer(opts)

        self.updateType(fp_m128, sse3.types['fp'][('float',4)], ['arith', 'load', 'misc', 'cvt', 'set', 'move', 'store'])

        self.types = { 'fp': { ('float', 4): fp_m128} }
        
        self.packer = _Packer(opts)
        