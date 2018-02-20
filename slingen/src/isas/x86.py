'''
Created on Apr 18, 2012

@author: danieles
'''

# from src.irbase import *
# from src.isas.isabase import *
from sympy import sqrt
from src.dsls.ll import IdentityMatrix, AllEntriesConstantMatrix
from src.irbase import RValue, ScaLoad, Deref, Mov, Comment, V
from src.isas.isabase import ISA, Loader, Storer
    
class ScaAdd(RValue):
    def __init__(self, src0, src1):
        super(ScaAdd, self).__init__()
        self.srcs += [src0, src1]

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[0] + src1[0] ]
    
    def unparse(self, indent):
        return indent + self.srcs[0].unparse("") + " + " + self.srcs[1].unparse("")

    def printInst(self, indent):
        return indent + "ScaAdd( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class ScaSub(RValue):
    def __init__(self, src0, src1):
        super(ScaSub, self).__init__()
        self.srcs += [src0, src1]

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[0] - src1[0] ]
    
    def unparse(self, indent):
        return indent + self.srcs[0].unparse("") + " - " + self.srcs[1].unparse("")

    def printInst(self, indent):
        return indent + "ScaSub( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class ScaMul(RValue):
    def __init__(self, src0, src1):
        super(ScaMul, self).__init__()
        self.srcs += [src0, src1]

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[0] * src1[0] ]
        
    def unparse(self, indent):
        return indent + self.srcs[0].unparse("") + " * " + self.srcs[1].unparse("")

    def printInst(self, indent):
        return indent + "ScaMul( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class ScaSqrt(RValue):
    def __init__(self, src):
        super(ScaSqrt, self).__init__()
        self.srcs += [src]

    def computeSym(self, nameList):
        src = self.srcs[0].computeSym(nameList)
        return [ sqrt(src) ]
        
    def unparse(self, indent):
        return indent + "sqrt(" + self.srcs[0].unparse("") + ")"

    def printInst(self, indent):
        return indent + "ScaSqrt( " + self.srcs[0].printInst("") + " )"

class ScaDiv(RValue):
    def __init__(self, src0, src1):
        super(ScaDiv, self).__init__()
        self.srcs += [src0, src1]

    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [ src0[0] / src1[0] ]
        
    def unparse(self, indent):
        return indent + self.srcs[0].unparse("") + " / " + self.srcs[1].unparse("")

    def printInst(self, indent):
        return indent + "ScaDiv( " + self.srcs[0].printInst("") + ", " + self.srcs[1].printInst("") + " )"

class _ScaLoader(Loader):
    def __init__(self):
        super(_ScaLoader, self).__init__()
    
    def loadMatrix(self, mParams):
        src, dst = mParams['m'], mParams['nuM']
        sL, sR = mParams['mL'], mParams['mR']
        dL, dR = mParams['nuML'], mParams['nuMR']
        M, N = mParams['M'], mParams['N']
        nuMM, nuMN = mParams['nuMM'], mParams['nuMN']
        mStruct, mAccess = mParams['struct'], mParams['access']
        instructions = []

        if IdentityMatrix.test(mStruct, mAccess, M, N):
            comm = Comment('%dx%d - %s' % (M, N, 'Identity'))
            instrs = [Mov(V(1), ScaLoad(dst[dL.of(i),dR.of(i)])) for i in range(M) ]
            instructions.extend([comm] + instrs)

        if AllEntriesConstantMatrix.test(mStruct, mAccess, M, N):
            mat_type = mStruct.keys()[0]
            comm = Comment('%dx%d - %s' % ( M, N, str(mat_type) ) )
            instrs = []
            for i in range(M):
                for j in range(N):
                    instrs.append( Mov(V(mat_type._const_value), ScaLoad(dst[dL.of(i),dR.of(j)])) )
            instructions.extend([comm] + instrs)

        return instructions

class _ScaBLAC(object):
    def __init__(self):
        super(_ScaBLAC, self).__init__()

    def Zero(self, dParams, opts):
        
        dst = dParams['nuM']
        dL, dR = dParams['nuML'], dParams['nuMR']
        M, N = dParams['nuMM'], dParams['nuMN']
        instructions = []

        instructions += [ Comment("1-BLAC: Zero " + str(M) + "x" + str(N)) ]
        for i in range(M):
            for j in range(N):
                instr = Mov( V(0), ScaLoad(dst[dL.of(i),dR.of(j)]) )
                instructions.append( instr )
        
        return instructions
    
    def Copy(self, sParams, dParams, opts):
        sub, dst = sParams['nuM'], dParams['nuM']
        subL, subR = sParams['nuML'], sParams['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        M, N = sParams['nuMM'], sParams['nuMN']
        instructions = []

        instructions += [ Comment("1-BLAC: Copy " + str(M) + "x" + str(N)) ]
        for i in range(M):
            for j in range(N):
                instr = Mov(ScaLoad(sub[subL.of(i),subR.of(j)]), ScaLoad(dst[dL.of(i),dR.of(j)]))
                instructions += [ instr ]

        return instructions
        
    def Add(self, s0Params, s1Params, dParams, opts):
        
        src0, src1, dst = s0Params['nuM'], s1Params['nuM'], dParams['nuM']
        s0L, s0R = s0Params['nuML'], s0Params['nuMR']
        s1L, s1R = s1Params['nuML'], s1Params['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        M, N     = dParams['nuMM'], dParams['nuMN']
        instructions = []

        instructions += [ Comment("1-BLAC: " + str(M) + "x" + str(N) + " + " + str(M) + "x" + str(N)) ]
        for i in range(M):
            for j in range(N):
                instr = Mov(ScaAdd(ScaLoad(src0[s0L.of(i),s0R.of(j)]), ScaLoad(src1[s1L.of(i),s1R.of(j)])), ScaLoad(dst[dL.of(i),dR.of(j)]))
                instructions += [ instr ]
        
        return instructions

    def Sub(self, s0Params, s1Params, dParams, opts):
        
        src0, src1, dst = s0Params['nuM'], s1Params['nuM'], dParams['nuM']
        s0L, s0R = s0Params['nuML'], s0Params['nuMR']
        s1L, s1R = s1Params['nuML'], s1Params['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        M, N     = dParams['nuMM'], dParams['nuMN']
        instructions = []

        instructions += [ Comment("1-BLAC: " + str(M) + "x" + str(N) + " - " + str(M) + "x" + str(N)) ]
        for i in range(M):
            for j in range(N):
                instr = Mov(ScaSub(ScaLoad(src0[s0L.of(i),s0R.of(j)]), ScaLoad(src1[s1L.of(i),s1R.of(j)])), ScaLoad(dst[dL.of(i),dR.of(j)]))
                instructions += [ instr ]
        
        return instructions

#     def LDiv(self, s0Params, s1Params, dParams, opts):
#         src0, src1, dst = s0Params['nuM'], s1Params['nuM'], dParams['nuM']
#         s0L, s0R = s0Params['nuML'], s0Params['nuMR']
#         s1L, s1R = s1Params['nuML'], s1Params['nuMR']
#         dL, dR   = dParams['nuML'], dParams['nuMR']
#         M, N = s0Params['nuMM'], s1Params['nuMN']
#         instructions = []
# 
#         instructions += [ Comment("1-BLAC: " + str(M) + "x" + str(M) + " \ " + str(M) + "x" + str(N)) ]
# 
#         for j in range(N):
#             instr = Mov(ScaDiv(ScaLoad(src1[s1L.of(0),s1R.of(j)]), ScaLoad(src0[s0L.of(0),s0R.of(0)])), ScaLoad(dst[dL.of(0),dR.of(j)]))
#             instructions += [ instr ]
# #             for i in range(1, M):
# #                 t0 = ScaMul(ScaLoad(src0[s0L.of(i),s0R.of(0)]), ScaLoad(dst[dL.of(0),dR.of(j)]))
# #                 for k in range(1, i):
# #                     t1 = ScaMul(ScaLoad(src0[s0L.of(i),s0R.of(k)]), ScaLoad(dst[dL.of(k),dR.of(j)]))
# #                     t0 = ScaAdd(t0, t1)
# #                 s = ScaSub(ScaLoad(src1[s1L.of(i),s1R.of(j)]), t0)
# #                 instr = Mov(ScaDiv(s, ScaLoad(src0[s0L.of(i),s0R.of(i)])), ScaLoad(dst[dL.of(i),dR.of(j)]))
# #                 instructions += [ instr ]

        return instructions

#     def RDiv(self, s0Params, s1Params, dParams, opts):
    def Div(self, s0Params, s1Params, dParams, opts):
        src0, src1, dst = s0Params['nuM'], s1Params['nuM'], dParams['nuM']
        s0L, s0R = s0Params['nuML'], s0Params['nuMR']
        s1L, s1R = s1Params['nuML'], s1Params['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        M, N = s0Params['nuMM'], s1Params['nuMN']
        instructions = []

        instructions += [ Comment("1-BLAC: " + str(M) + "x" + str(N) + " / " + str(N) + "x" + str(N)) ]

        for i in range(M):
            instr = Mov(ScaDiv(ScaLoad(src0[s0L.of(i),s0R.of(0)]), ScaLoad(src1[s1L.of(0),s1R.of(0)])), ScaLoad(dst[dL.of(i),dR.of(0)]))
            instructions += [ instr ]

        return instructions
        
    def Mul(self, s0Params, s1Params, dParams, opts):

        src0, src1, dst = s0Params['nuM'], s1Params['nuM'], dParams['nuM']
        s0L, s0R = s0Params['nuML'], s0Params['nuMR']
        s1L, s1R = s1Params['nuML'], s1Params['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        M, K, N = s0Params['nuMM'], s0Params['nuMN'], s1Params['nuMN']
        instructions = []

        instructions += [ Comment("1-BLAC: " + str(M) + "x" + str(K) + " * " + str(K) + "x" + str(N)) ]
        for i in range(M):
            for j in range(N):
                instr = Mov(ScaMul(ScaLoad(src0[s0L.of(i),s0R.of(0)]), ScaLoad(src1[s1L.of(0),s1R.of(j)])), ScaLoad(dst[dL.of(i),dR.of(j)]))
                instructions += [ instr ]

        for k in range(1,K):
            for i in range(M):
                for j in range(N):
                    t = ScaMul(ScaLoad(src0[s0L.of(i),s0R.of(k)]), ScaLoad(src1[s1L.of(k),s1R.of(j)]))
                    instr = Mov(ScaAdd(ScaLoad(dst[dL.of(i),dR.of(j)]), t), ScaLoad(dst[dL.of(i),dR.of(j)]))
                    instructions += [ instr ]

        return instructions

    def Kro(self, s0Params, s1Params, dParams, opts):
        src0, src1, dst = s0Params['nuM'], s1Params['nuM'], dParams['nuM']
        s0L, s0R = s0Params['nuML'], s0Params['nuMR']
        s1L, s1R = s1Params['nuML'], s1Params['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        M, K, N, P = s0Params['nuMM'], s0Params['nuMN'], s1Params['nuMM'], s1Params['nuMN']
        instructions = []
        
        instructions += [ Comment("1-BLAC: " + str(M) + "x" + str(K) + " Kro " + str(N) + "x" + str(P)) ]
        for i in range(M):
            for k in range(K):
                for j in range(N):
                    for p in range(P):
                        instr = Mov(ScaMul(ScaLoad(src0[s0L.of(i),s0R.of(k)]), ScaLoad(src1[s1L.of(j),s1R.of(p)])), ScaLoad(dst[dL.of(i+j),dR.of(k+p)]))
                        instructions += [ instr ]
        
        return instructions

    def Sqrt(self, sParams, dParams, opts):
        src, dst = sParams['nuM'], dParams['nuM']
        sL, sR = sParams['nuML'], sParams['nuMR']
        dL, dR = dParams['nuML'], dParams['nuMR']
        M, N = dParams['nuMM'], dParams['nuMN']
        instructions = []

        instructions += [ Comment("1-BLAC: sqrt(" + str(N) + "x" + str(M) + ")") ]
        instr = Mov(ScaSqrt(ScaLoad(src[sL.of(0),sR.of(0)])), ScaLoad(dst[dL.of(0),dR.of(0)]))
        instructions += [ instr ]
        
        return instructions

    def Neg(self, sParams, dParams, opts):
        src, dst = sParams['nuM'], dParams['nuM']
        sL, sR = sParams['nuML'], sParams['nuMR']
        dL, dR = dParams['nuML'], dParams['nuMR']
        M, N = dParams['nuMM'], dParams['nuMN']
        instructions = []

        instructions += [ Comment("1-BLAC: -(" + str(N) + "x" + str(M) + ")") ]
        instr = Mov(ScaMul(V(-1), ScaLoad(src[sL.of(0),sR.of(0)])), ScaLoad(dst[dL.of(0),dR.of(0)]))
        instructions += [ instr ]
        
        return instructions

    def T(self, sParams, dParams, opts):
        src, dst = sParams['nuM'], dParams['nuM']
        sL, sR = sParams['nuML'], sParams['nuMR']
        dL, dR = dParams['nuML'], dParams['nuMR']
        M, N = dParams['nuMM'], dParams['nuMN']
        instructions = []

        instructions += [ Comment("1-BLAC: (" + str(N) + "x" + str(M) + ")^T") ]
        for i in range(M):
            for j in range(N):
                instr = Mov(ScaLoad(src[sL.of(j),sR.of(i)]), ScaLoad(dst[dL.of(i),dR.of(j)]))
                instructions += [ instr ]
        
        return instructions

class _ScaStorer(Storer):
    def __init__(self):
        super(_ScaStorer, self).__init__()

    def storeMatrix(self, mParams):
        src, dst = mParams['nuM'], mParams['m']
        sL, sR = mParams['nuML'], mParams['nuMR']
        dL, dR = mParams['mL'], mParams['mR']
        M, N = mParams['M'], mParams['N']
        isCompact = mParams['compact']
        mStruct, mAccess = mParams['struct'], mParams['access']
        instructions = []

        for i in instructions:
            i.bounds.update(mParams['bounds'])

        return instructions

class x86(ISA):
    def __init__(self, opts):
        super(x86, self).__init__()
#         self.nu = [ 1 ]
        self.precision = opts['precision']
        self.name = "x86"
#         self.vectorize = False
        fp_s = { 'type': self.precision } # input/output types allowed by the ISA for a given nu
        fp_s['arith'] = [ ScaAdd, ScaSub, ScaMul, ScaDiv, ScaSqrt ]
        fp_s['load']  = [ ScaLoad, Deref ]
        fp_s['misc']  = [ ]
        fp_s['set']   = [ ]
        fp_s['move']  = [ ]
        fp_s['store'] = [ Mov ]

        fp_s['loader'] = _ScaLoader()
        fp_s['nublac'] = _ScaBLAC()
        fp_s['storer'] = _ScaStorer()

        self.types = { 'fp': { (self.precision, 1): fp_s } }

        self.add_func_defs = [ ]    