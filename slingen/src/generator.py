'''
Created on Apr 18, 2012

@author: danieles
'''

import math
import sympy

from itertools import count
from copy import deepcopy
from sympy import sympify
from islpy import dim_type, Constraint, Set, Map

from src.dsls.ll import Matrix, ZeroMatrix, G, Iv, MappingException
from src.dsls.sigmall import NewSum
from src.dsls.processing import computeIndependentSubexprWithBounds

from src.irbase import ForLoop, If, Comment, IBlock, SingleContext, Mov, icode, sa
from src.nublac import NeonAllocator, NuAllocator
from src.isas.x86 import ScaAdd, ScaMul
from src.isas.armv7 import ARMv7

#from src.binding import *

# import ir
# from ir import *

# from src import irbase
# from src.irbase import *
# from src.isas.isabase import *
# from src.isas.x86 import *
# from src.isas.sse import *
# from src.isas.sse2 import *
# from src.isas.sse3 import *
# from src.isas.ssse3 import *
# from src.isas.sse4_1 import *
# from src.isas.avx import *
# from src.isas.neon import *

#import src.nublac
# import nublac

class Generator(object):
    pass


class CodeGenerator(Generator):
    def __init__(self, expr, opts):
        self.counter = count()
        self.nublac = opts['isaman'].getNuBLAC(opts['precision'], opts['nu'])
#         self.allocator = src.nublac.NuAllocator()
        self.allocator = NeonAllocator() if ARMv7 in opts['isaman'].isaList else NuAllocator()
        self.gen(expr, opts)

    def Load(self, mParamsList, opts):
        instructions = []
        for mParams in mParamsList:
            if mParams['nu'] > 1:
                loader = opts['isaman'].getLoader(opts['precision'], mParams['nu'])
                instructions += loader.loadMatrix(mParams)
        return instructions

    def Store(self, mParamsList, opts):
        instructions = []
        for mParams in mParamsList:
            if mParams['nu'] > 1:
                storer = opts['isaman'].getStorer(opts['precision'], mParams['nu'])
                instructions += storer.storeMatrix(mParams)
        return instructions
        
    def gen(self, expr, opts, bounds=None,context=None):
        if bounds is None:
            bounds = {}
        getattr(self, expr.__class__.__name__)(expr, opts, bounds, context)

    def Assign(self, expr, opts, bounds, context=None, setComp=True):
        if expr.isComputed(): return
            
        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts, bounds)
        getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], opts, bounds)

#         mLhs = expr.inexpr[0].getOut()
#         mRhs = expr.inexpr[1].getOut()
        
#         if mLhs.attr['o']:
#             src = mRhs
#             dst = mLhs
#             sexpr = expr.inexpr[1]
#         else:
#             src = mLhs
#             dst = mRhs
#             sexpr = expr.inexpr[0]

#         if sexpr.reqAss or dst.attr['i']:
#             
#             sL,sR = src.fL.subs(bounds), src.fR.subs(bounds)
#             dL,dR   = dst.fL.subs(bounds), dst.fR.subs(bounds)
#             
#             block = IBlock()
#     
#             for i in range(src.size[0]):
#                 for j in range(src.size[1]):
#                     try:
#                         instr = Mov(sa(src[sL.of(i),sR.of(j)]), sa(dst[dL.of(i),dR.of(j)]))
#                     except MappingException:
#                         print "Add> MappingException"
#                     else:
#                         block.instructions += [ instr ]
#     
#             if context is not None:
#                 context.blocks += [ block ]
#             else:
#                 icode.blocks += [ block ]
            
        expr.setComputed(setComp)
    
    def resetInit(self, expr, idx, isInOutDep, dsIsInOutDep, opts):
        if (not expr.isBoundToParam or expr.isBoundToParam and opts['init']) and \
            ((idx.i in expr.forceInitIdx and expr.forceInitCounter > 0) or (isInOutDep and expr.initCounter > 0)):
            expr.init = True
            for s in expr.depSums:
                s.init = True

        for b, e in zip(dsIsInOutDep, expr.depSums):
            if b and e.initCounter > 0:
                e.init = True
                for s in e.depSums:
                    s.init = True

        #When moving to a different heterogeneous area of the matrix the init. counter should be reset 
        if idx.i in expr.forceInitIdx and expr.forceInitCounter > 0:
            expr.forceInitCounter -= 1
            del expr.initCounterIdx[:]
            expr.initCounter = 1
            
    def generateBody(self, expr, opts, bounds, context, acc):
        expr.addPartialComp(bounds)
        if not acc or expr.init:
            src = expr.inexpr[0]
            getattr(self, src.__class__.__name__)(src, opts, bounds, context, setComp=False)
            expr.initCounter -= 1
            expr.init = False
        else:
            src = expr.inexpr[1]
            getattr(self, src.__class__.__name__)(src, opts, bounds, context, setComp=False)
            
    def buildLoop(self, toBuild, uFactors, expr, opts, bounds, context, acc=False):
        # Every Index is associated with a loop. When there are no longer available indices
        # the code due to the operator should be added to the context of the innermost loop 
        if len(toBuild) > 0:
#            #Determine list of nodes under expr that don't depend upon expr's indices and generate before creating
#            #the context for the next loop body (Could be moved within Sum's method)
            # Reduces the list of indices and unrolling factors
            nextToBuild = [ deepcopy(i) for i in toBuild[1:]]
            nextUFactors = [ deepcopy(u) for u in uFactors[1:]]
            idx = deepcopy(toBuild[0])
            idx.subs(bounds)
            uf = deepcopy(uFactors[0]).subs(bounds)
            isInOutDep = any(map(lambda setCounterExpr: idx.i in setCounterExpr, expr.outDep)) # Due to merge one should check if the idx is in outDep of eventual depSums
            dsIsInOutDep = [ any(map(lambda setCounterExpr: idx.i in setCounterExpr, s.outDep)) for s in expr.depSums ]
            # In case of accumulation, if the index doesn't belong to outDep, 
            # initialize the output without creating a new context.
            if acc and expr.init:
#               if not idx.i in expr.outerIdx + expr.outDep
                if all(map(lambda avoidInitExpr: idx.i not in avoidInitExpr, expr.outerIdx + expr.outDep)):
                    newBounds = dict(bounds.items() + [(idx.i, sympify(idx.b))])
                    self.buildLoop(nextToBuild, nextUFactors, expr, opts, newBounds, context, acc)
                    idx.reinit(idx.b+idx.s)
            # q > 0 means a loop body is required
            # r > 0 means the body should be executed outside the loop, binding the idx to r values
            L = idx.e-idx.b
            q = L//(uf*idx.s)
            r = int(math.ceil((L%(uf*idx.s))/float(idx.s)))
            
            rep_factor = r+uf if q>0 else r
            if not idx.i in expr.initCounterIdx:
                # How many times the index's value will be increased
                if isInOutDep:
                    expr.initCounterIdx.append(idx.i)
                    expr.initCounter *= rep_factor
                    for s in expr.depSums:
                        s.init = True
                        s.initCounter = 1 if s.initCounter == 0 else s.initCounter 
                
            for b, e in zip(dsIsInOutDep, expr.depSums):
                if b:
                    e.initCounter = rep_factor #if e.initCounter == 0 else e.initCounter*rep_factor
                    e.init = True
                    for s in e.depSums:
                        s.init = True
                
                
            for k in range(r):
                # Compute the body within the parent context binding the value of idx (if idx is declared)
                newBounds = dict(bounds.items() + [(idx.i, sympify(idx.b))])# if idx.needsLoop() else bounds
                self.buildLoop(nextToBuild, nextUFactors, expr, opts, newBounds, context, acc)
                self.resetInit(expr, idx, isInOutDep, dsIsInOutDep, opts)
                 
                idx.reinit(idx.b+idx.s)
            # Depending on the unrolling factor the loop body could be repeated
            if q > 0:
                # Create a temporary unrolled index and decide whether it requires a new loop
                uIdx = deepcopy(idx)
                uIdx.set(idx.b, idx.e, uf*idx.s)
                loccontext = ForLoop(uIdx.i, uIdx.b, uIdx.e, uIdx.s) if uIdx.needsLoop() else context

                for k in range(uf):
                    # Get ranges that will be used to address the proper tile in the matrix
                    # Compute the body within the parent context binding the value of idx (if idx is declared)
                    base = uIdx.i if uIdx.needsLoop() else sympify(uIdx.b)
                    newBounds = dict(bounds.items() + [(idx.i, base+k*idx.s)])# if idx.needsLoop() else bounds
                    self.buildLoop(nextToBuild, nextUFactors, expr, opts, newBounds, loccontext, acc)
                    self.resetInit(expr, idx, isInOutDep, dsIsInOutDep, opts)
            
                if(uIdx.needsLoop()):
                    temp = IBlock()
                    temp.instructions += [ loccontext ]
                    context.blocks += [ temp ]
        else:
            # Generation of the innermost loop body
            self.generateBody(expr, opts, bounds, context, acc)

    def Sum(self, expr, opts, bounds, context=None, setComp=True):
        if expr.isComputed() or expr.isBuilding or expr.partiallyComputed(bounds): return

        expr.isBuilding = True
        
        if context is None:
            context = icode
        
        #Determine list of nodes under expr that don't depend upon expr's indices and generate before creating
        #the context for the next loop body (Could be moved within Sum's method)
#         indepList = computeIndependentSubexpr(expr.inexpr[0], expr.iList, [], opts)
        indepList = computeIndependentSubexprWithBounds(expr.inexpr[0], expr.iList, bounds, [], opts)
        for e in indepList:
            if not e.isComputed():
#                 getattr(self, e.__class__.__name__)(e, opts, bounds, context)
                getattr(self, e.__class__.__name__)(e, opts, {}, context)
        
        expr.computeDepSums(opts)
                
#        self.buildLoop(expr.iList, [], expr.uFactors, expr, opts, bounds, context)
        # Top indices in forceInit can have at most 2 values if they appear at this point
        # Everyone of them requires the expr to be reinit everytime we move from an heterogeneous area to the next one,
        # once for every new dimension, eg in 2D: Init/I=0 -> (J=0/Reinit, J=1/Reinit), I=1/Reinit-> (J=0/Reinit, J=1)   
        expr.forceInitCounter = 0
        for i in range(1,len(expr.forceInitIdx)+1):
            expr.forceInitCounter += 2**i-1
#         self.buildLoop(expr.iList, expr.uFactors, expr, opts, bounds, context, depSums, expr.acc)
        self.buildLoop(expr.iList, expr.uFactors, expr, opts, bounds, context, expr.acc)
        expr.setComputed(setComp)
        expr.isBuilding = False

    def Add(self, expr, opts, bounds, context=None, setComp=True):
        if expr.isComputed(): return
        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, bounds, context, setComp)
        
        src0 = expr.getInexprMat(0)
        src1 = expr.getInexprMat(1)
        dst = expr.out
        
        s0Params, s1Params = self.allocator.extractParams(src0, bounds, opts), self.allocator.extractParams(src1, bounds, opts)
        dParams = self.allocator.extractParams(dst, bounds, opts)
        
        block = IBlock()

        block.instructions += [ Comment(str(expr) + " -- " + str(bounds)) ]
        
        if s0Params['nuable'] and s1Params['nuable'] and dParams['nuable']:
            block.instructions += self.Load([s0Params, s1Params], opts)
            block.instructions += self.nublac.Add(s0Params, s1Params, dParams, opts)
            block.instructions += self.Store([dParams], opts)
        else:
            s0L, s0R = s0Params['mL'], s0Params['mR']
            s1L, s1R = s1Params['mL'], s1Params['mR']
            dL, dR   = dParams['mL'], dParams['mR']
            M, N = dParams['M'], dParams['N']

            block.instructions += [ Comment(str(M) + "x" + str(N) + " + " + str(M) + "x" + str(N)) ]
            for i in range(M):
                for j in range(N):
                    instr = Mov(ScaAdd(sa(src0[s0L.of(i),s0R.of(j)]), sa(src1[s1L.of(i),s1R.of(j)])), sa(dst[dL.of(i),dR.of(j)]))
                    block.instructions += [ instr ]


        if context is not None:
            context.blocks += [ block ]
        else:
            icode.blocks += [ block ]
        expr.setComputed(setComp)

    def Kro(self, expr, opts, bounds, context=None, setComp=True):
        if expr.isComputed(): return
        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, bounds, context, setComp)
        
        src0 = expr.getInexprMat(0)
        src1 = expr.getInexprMat(1)
        dst = expr.out
        
        s0Params, s1Params = self.allocator.extractParams(src0, bounds, opts), self.allocator.extractParams(src1, bounds, opts)
        dParams = self.allocator.extractParams(dst, bounds, opts)
        
        block = IBlock()


        block.instructions += [ Comment(str(expr) + " -- " + str(bounds)) ]

        if s0Params['nuable'] and s1Params['nuable'] and dParams['nuable']:
            block.instructions += self.Load([s0Params, s1Params], opts)
            block.instructions += self.nublac.Kro(s0Params, s1Params, dParams, opts)
            block.instructions += self.Store([dParams], opts)
        else:
            s0L, s0R = s0Params['mL'], s0Params['mR']
            s1L, s1R = s1Params['mL'], s1Params['mR']
            dL, dR   = dParams['mL'], dParams['mR']
            M, K, N, P = s0Params['M'], s0Params['N'], s1Params['M'], s1Params['N']

            block.instructions += [ Comment("Clean-up: " + str(M) + "x" + str(K) + " Kro " + str(N) + "x" + str(P)) ]
            for i in range(M):
                for k in range(K):
                    for j in range(N):
                        for p in range(P):
                            instr = Mov(ScaMul(sa(src0[s0L.of(i),s0R.of(k)]), sa(src1[s1L.of(j),s1R.of(p)])), sa(dst[dL.of(i+j),dR.of(k+p)]))
                            block.instructions += [ instr ]
            
        
        if context is not None:
            context.blocks += [ block ]
        else:
            icode.blocks += [ block ]
        expr.setComputed(setComp)

    def Mul(self, expr, opts, bounds, context=None, setComp=True):
        if expr.isComputed(): return
        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, bounds, context, setComp)

        src0 = expr.getInexprMat(0)
        src1 = expr.getInexprMat(1)
        dst = expr.out
        
        s0Params, s1Params = self.allocator.extractParams(src0, bounds, opts), self.allocator.extractParams(src1, bounds, opts)
        dParams = self.allocator.extractParams(dst, bounds, opts)

        block = IBlock()

        block.instructions += [ Comment(str(expr) + " -- " + str(bounds)) ]

        M, s0K, s1K, N = s0Params['M'], s0Params['N'], s1Params['M'], s1Params['N']

        if s0Params['nuable'] and s1Params['nuable'] and dParams['nuable']:
            block.instructions += self.Load([s0Params, s1Params], opts)
            if (M*s0K == 1) or (s1K*N == 1):
                block.instructions += self.nublac.Kro(s0Params, s1Params, dParams, opts)
            else:
                block.instructions += self.nublac.Mul(s0Params, s1Params, dParams, opts)
            block.instructions += self.Store([dParams], opts)
        else:
            s0L, s0R = s0Params['mL'], s0Params['mR']
            s1L, s1R = s1Params['mL'], s1Params['mR']
            dL, dR   = dParams['mL'], dParams['mR']
            
            block.instructions += [ Comment("Clean-up: " + str(M) + "x" + str(s0K) + " * " + str(s1K) + "x" + str(N)) ]
            for i in range(M):
                for j in range(N):
                    instr = Mov(ScaMul(sa(src0[s0L.of(i),s0R.of(0)]), sa(src1[s1L.of(0),s1R.of(j)])), sa(dst[dL.of(i),dR.of(j)]))
                    block.instructions += [ instr ]

            for k in range(1,s0K):
                for i in range(M):
                    for j in range(N):
                        t = ScaMul(sa(src0[s0L.of(i),s0R.of(k)]), sa(src1[s1L.of(k),s1R.of(j)]))
                        instr = Mov(ScaAdd(sa(dst[dL.of(i),dR.of(j)]), t), sa(dst[dL.of(i),dR.of(j)]))
                        block.instructions += [ instr ]
                    
        
        if context is not None:
            context.blocks += [ block ]
        else:
            icode.blocks += [ block ]
        expr.setComputed(setComp)

    def PMul(self, expr, opts, bounds, context=None, setComp=True):
        if expr.isComputed(): return
        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, bounds, context, setComp)

        src0 = expr.getInexprMat(0)
        src1 = expr.getInexprMat(1)
        dst = expr.out
        
        s0Params, s1Params = self.allocator.extractParams(src0, bounds, opts), self.allocator.extractParams(src1, bounds, opts)
        dParams = self.allocator.extractParams(dst, bounds, opts)

        block = IBlock()

        block.instructions += [ Comment(str(expr) + " -- " + str(bounds)) ]

#         M, s0K, s1K, N = s0Params['M'], s0Params['N'], s1Params['M'], s1Params['N']

        if s0Params['nuable'] and s1Params['nuable'] and dParams['nuable']:
            block.instructions += self.Load([s0Params, s1Params], opts)
            block.instructions += self.nublac.PMul(s0Params, s1Params, dParams, opts)
            block.instructions += self.Store([dParams], opts)
        else:
            raise NotImplementedError('Scalar PMul not implemented yet')
#             s0L, s0R = s0Params['mL'], s0Params['mR']
#             s1L, s1R = s1Params['mL'], s1Params['mR']
#             dL, dR   = dParams['mL'], dParams['mR']
#             
#             block.instructions += [ Comment("Clean-up: " + str(M) + "x" + str(s0K) + " * " + str(s1K) + "x" + str(N)) ]
#             for i in range(M):
#                 for j in range(N):
#                     instr = Mov(ScaMul(sa(src0[s0L.of(i),s0R.of(0)]), sa(src1[s1L.of(0),s1R.of(j)])), sa(dst[dL.of(i),dR.of(j)]))
#                     block.instructions += [ instr ]
# 
#             for k in range(1,s0K):
#                 for i in range(M):
#                     for j in range(N):
#                         t = ScaMul(sa(src0[s0L.of(i),s0R.of(k)]), sa(src1[s1L.of(k),s1R.of(j)]))
#                         instr = Mov(ScaAdd(sa(dst[dL.of(i),dR.of(j)]), t), sa(dst[dL.of(i),dR.of(j)]))
#                         block.instructions += [ instr ]
#                     
        
        if context is not None:
            context.blocks += [ block ]
        else:
            icode.blocks += [ block ]
        expr.setComputed(setComp)
    
    def HRed(self, expr, opts, bounds, context=None, setComp=True):
        if expr.isComputed(): return
        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, bounds, context, setComp)
        
        src = expr.getInexprMat(0)
        dst = expr.out
        
        sParams = self.allocator.extractParams(src, bounds, opts) 
        dParams = self.allocator.extractParams(dst, bounds, opts)
        
        block = IBlock()

        block.instructions += [ Comment(str(expr) + " -- " + str(bounds)) ]

        if sParams['nuable'] and dParams['nuable']:
            block.instructions += self.Load([sParams], opts)
            block.instructions += self.nublac.HRed(sParams, dParams, opts)
            block.instructions += self.Store([dParams], opts)
        else:
            raise NotImplementedError('Scalar HRed not implemented yet')
#             sL, sR = sParams['mL'], sParams['mR']
#             dL, dR = dParams['mL'], dParams['mR']
#             M, N = dParams['M'], dParams['N']
# 
#             block.instructions += [ Comment("clean-up: (" + str(N) + "x" + str(M) + ")^T") ]
#             for i in range(M):
#                 for j in range(N):
#                     instr = Mov(sa(src[sL.of(j),sR.of(i)]), sa(dst[dL.of(i),dR.of(j)]))
#                     block.instructions += [ instr ]
        
        if context is not None:
            context.blocks += [ block ]
        else:
            icode.blocks += [ block ]
        expr.setComputed(setComp)
        
    def T(self, expr, opts, bounds, context=None, setComp=True):
        if expr.isComputed(): return
        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, bounds, context, setComp)
        
        src = expr.getInexprMat(0)
        dst = expr.out
        
        sParams = self.allocator.extractParams(src, bounds, opts) 
        dParams = self.allocator.extractParams(dst, bounds, opts)
        
        block = IBlock()

        block.instructions += [ Comment(str(expr) + " -- " + str(bounds)) ]

        if sParams['nuable'] and dParams['nuable']:
            block.instructions += self.Load([sParams], opts)
            block.instructions += self.nublac.T(sParams, dParams, opts)
            block.instructions += self.Store([dParams], opts)
        else:
            sL, sR = sParams['mL'], sParams['mR']
            dL, dR = dParams['mL'], dParams['mR']
            M, N = dParams['M'], dParams['N']

            block.instructions += [ Comment("clean-up: (" + str(N) + "x" + str(M) + ")^T") ]
            for i in range(M):
                for j in range(N):
                    instr = Mov(sa(src[sL.of(j),sR.of(i)]), sa(dst[dL.of(i),dR.of(j)]))
                    block.instructions += [ instr ]
        
        if context is not None:
            context.blocks += [ block ]
        else:
            icode.blocks += [ block ]
        expr.setComputed(setComp)
        
    def S(self, expr, opts, bounds, context=None, setComp=True):
        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, bounds, context, setComp)
        
        if isinstance(expr.inexpr[0], G):
            src = expr.getInexprMat(0)
            dst = expr.out
            
            sL,sR = expr.inexpr[0].fL.subs(bounds), expr.inexpr[0].fR.subs(bounds)
            dL,dR   = expr.fL.subs(bounds), expr.fR.subs(bounds)
            
            block = IBlock()
    
            for i in range(src.size[0]):
                for j in range(src.size[1]):
                    try:
                        instr = Mov(sa(src[sL.of(i),sR.of(j)]), sa(dst[dL.of(i),dR.of(j)]))
                    except MappingException:
                        print "S> MappingException"
                    else:
                        block.instructions += [ instr ]
    
            if context is not None:
                context.blocks += [ block ]
            else:
                icode.blocks += [ block ]

            expr.setComputed(setComp)
            

    def G(self, expr, opts, bounds, context=None, setComp=True):
        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, bounds, context, setComp)

#     def Access(self, expr, opts, context=None):
#         for sub in expr.inexpr:
#             getattr(self, sub.__class__.__name__)(sub, opts)

    def Scalar(self, expr, opts, bounds, context=None, setComp=True):
        self.Matrix(expr, opts, bounds, context, setComp)

    def SquaredMatrix(self, expr, opts, bounds, context=None, setComp=True):
        self.Matrix(expr, opts, bounds, context, setComp)

    def Matrix(self, expr, opts, bounds, context=None, setComp=True):
        expr.setComputed(setComp)

# def floord(n,d):
#     if n < 0:
#         return -((-(n)+(d)-1)/(d))
#     else:
#         return (n)/(d)
# 
# def ceild(n,d):
#     if n < 0:
#         return -((-(n))/(d))
#     else:
#         return ((n)+(d)-1)/(d)

class StructuresConstructor(object):
    def __init__(self):
        super(StructuresConstructor, self).__init__()

    def construct(self, sllprog, opts, minbounds=None, iterspace=None):
        if minbounds is None:
            minbounds = {}
        if iterspace is None:
            iterspace = Set("{[]}")
#         sllprog.computeSpaceIdxNames(i='i',j='j', ipfix=str(globalSSAIndex()), jpfix=str(globalSSAIndex()), opts=opts)
        ext_opts = {'idx_for_sca_dims': True}
        ext_opts.update(opts)
        sllprog.computeSpaceIdxNames(opts=ext_opts)
        self.llBlock(sllprog.stmtList, opts, minbounds, iterspace)

    def replaceConnectedPhysicalLayout(self, newPhys, expr, i):
        subPhys = icode.bindingTable.getPhysicalLayout(expr.getInexprMat(i))
        icode.bindingTable.replaceConnectedPhysicalLayout(subPhys, newPhys, expr.inexpr[i])
        if not icode.bindingTable.existPhysicalLayout(subPhys):
            icode.declare.remove(subPhys)
        
    def llBlock(self, expr, opts, minbounds, iterspace):
        for s in expr:
            getattr(self, s.__class__.__name__)(s, opts, minbounds, iterspace)
    
    def llFor(self, expr, opts, minbounds, iterspace):
        sidx, sLb, sUb, sInc = str(expr.idx), str(expr.lb), str(expr.ub), str(expr.s)
        idcs = iterspace.get_var_names(dim_type.set) + [sidx]
        setstr = str("{ [" + ",".join(idcs) + "] : exists s: " + sidx + "="+sInc+"s and " + sLb + " <= " + sidx + " <= " + sUb + " }") 
        newDimSet = Set(setstr)
        newIterspace = newDimSet.intersect(iterspace.add_dims(dim_type.set, 1))
        lexmin = newIterspace.lexmin()
        ps = []
        lexmin.foreach_point(ps.append)
        vs = [ ps[0].get_coordinate_val(dim_type.set, i).to_python() for i in range(len(idcs)) ]
        newMinbounds = { idcs[i] : vs[i] for i in range(len(idcs)) }
        getattr(self, expr.body.__class__.__name__)(expr.body, opts, newMinbounds, newIterspace)
        
    def llIf(self, expr, opts, minbounds, iterspace):
        for b in expr.bodys:
            getattr(self, b.__class__.__name__)(b, opts, minbounds, iterspace)
        
    def llStmt(self, expr, opts, minbounds, iterspace):
        getattr(self, expr.eq.__class__.__name__)(expr.eq, opts, minbounds, iterspace)
    
    def Assign(self, expr, opts, minbounds, iterspace):
        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts, minbounds, iterspace)
        getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], opts, minbounds, iterspace)

    def NewSum(self, expr, opts, minbounds, iterspace):
#         minlb = expr.lb.subs(minbounds)
#         
#         if 'max' in str(minlb) or 'min' in str(minlb) or 'floord' in str(minlb) or 'ceild' in str(minlb):
#             minlb = sympify(eval(str(minlb)))
#         newMinbounds = dict(minbounds.items() + [(expr.idx, minlb)])
        
        sidx, sLb, sUb, sInc = str(expr.idx), str(expr.lb), str(expr.ub), str(expr.s)
        idcs = iterspace.get_var_names(dim_type.set) + [sidx]
        setstr = str("{ [" + ",".join(idcs) + "] : exists s: " + sidx + "="+sInc+"s and " + sLb + " <= " + sidx + " <= " + sUb + " }") 
        newDimSet = Set(setstr)
        newIterspace = newDimSet.intersect(iterspace.add_dims(dim_type.set, 1))
        lexmin = newIterspace.lexmin()
        ps = []
        lexmin.foreach_point(ps.append)
        vs = [ ps[0].get_coordinate_val(dim_type.set, i).to_python() for i in range(len(idcs)) ]
        newMinbounds = { idcs[i] : vs[i] for i in range(len(idcs)) }
        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts, newMinbounds, newIterspace)

        if expr.out.genStruct is None:
            expr.out.genStruct = expr.getInexprMat(0).genStruct

    def S(self, expr, opts, minbounds, iterspace):

        dst = expr.out

        if dst.genStruct is None:
            dst.genStruct = {}
            fL = expr.fL.subs(minbounds)
            fR = expr.fR.subs(minbounds)
            o = [ fL.of(0), fR.of(0) ]
            gatSet = Set("{[i,j]: "+str(o[0])+"<=i<"+str(o[0]+fL.n)+" and "+str(o[1])+"<=j<"+str(o[1]+fR.n)+"}")
            aboveSet = expr.getStructFromAbove()
            for s in aboveSet:
                t = aboveSet[s].intersect(gatSet)
                if not t.is_empty():
                    sht = t-t
                    for bs in t.get_basic_sets():
                        cs = bs.get_constraints()
                        for i in range(2):
                            tcs = []
                            for c in cs:
                                f = Constraint.equality_from_aff if c.is_equality() else Constraint.inequality_from_aff 
                                c = f( c.get_aff().add_constant_val( int(o[i]*(c.get_coefficient_val(dim_type.set, i).to_python())) ) )
                                tcs.append(c)
                            cs = tcs
                        sht = sht.union(Set.universe(t.get_space()).add_constraints(cs))
                    if not sht.is_empty():
                        dst.genStruct[s] = sht
                        
#             matStruct = aboveSet[Matrix].intersect(gatSet)
#             aboveMap = expr.getAccessFromAbove()
#             matAccess = aboveMap.intersect_domain(matStruct)
#             aboveMap_basicMaps, matAccess_basicMaps = aboveMap.get_basic_maps(), matAccess.get_basic_maps()
#             genAccess_basicMaps = [ ibm for ibm in aboveMap_basicMaps if any(map(lambda mbm: not mbm.intersect(ibm).is_empty(), matAccess_basicMaps)) ]
#             genAccess = Map.from_basic_map(genAccess_basicMaps[0])
#             for bm in genAccess_basicMaps[1:]:
#                 genAccess = genAccess.union(bm)
#             dst.setGenAccess(genAccess)
            genAccess_maps = []
            for struct in dst.genStruct:
                matStruct = aboveSet[struct].intersect(gatSet)
                aboveMap = expr.getAccessFromAbove()
    
                inMap_basicMaps, matStruct_basicSets = aboveMap.get_basic_maps(), matStruct.get_basic_sets()
                intersecting_basicMaps = [ ibm for ibm in inMap_basicMaps if any(map(lambda mbs: not ibm.intersect_domain(mbs).domain().is_empty(), matStruct_basicSets)) ]
                
                shifted_basicMaps = []
                for bm in intersecting_basicMaps:
                    wrapped_univ = bm.universe_like().wrap()
                    wrapped_cs = bm.wrap().get_constraints()
                    for var in bm.wrap().get_var_dict().values():
                        tcs = []
                        for c in wrapped_cs:
                            if not c.is_equality():
                                f = Constraint.inequality_from_aff
                                coeff = c.get_coefficient_val(*var).to_python()
                                sign = coeff//abs(coeff) if coeff != 0 else coeff
                                c = f( c.get_aff().add_constant_val( int(sign*o[var[1]]) ) )
                            tcs.append(c)
                        wrapped_cs = tcs
                    shifted_basicMaps.append(wrapped_univ.add_constraints(wrapped_cs).unwrap())
                
                mat_set = dst.genStruct[struct]
                for sbm in shifted_basicMaps:
                    m = Map.from_basic_map(sbm.universe_like())
                    test_m = Map.from_basic_map(sbm.universe_like()).intersect_domain(mat_set)
                    for c in sbm.get_constraints():
                        tm = test_m.add_constraint(c)
                        if test_m != tm:
                            test_m = tm
                            m = m.add_constraint(c)
                    genAccess_maps.append(m)

            genAccess = genAccess_maps[0]
            for m in genAccess_maps[1:]:
                genAccess = genAccess.union(m)
            dst.setGenAccess(genAccess)

        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, minbounds, iterspace)
        if not isinstance(expr.inexpr[0], G):
            # If we directly scatter a gather we should keep the phys. layout separated
            # Otherwise we can bind the subexpr's phys. layout to a larger one where 
            # the op. S is supposed to scatter its input.
            if dst.genStruct == expr.inexpr[0].getOut().genStruct and dst.genAccess() == expr.inexpr[0].getOut().genAccess():
                sub = expr.getInexprMat(0)
                outPhys = icode.bindingTable.getPhysicalLayout(dst) 
                self.replaceConnectedPhysicalLayout(outPhys, expr, 0)
                sub.fL, sub.fR = expr.fL, expr.fR
        

    def Sacc(self, expr, opts, minbounds, iterspace):

        dst = expr.out
        
        if dst.genStruct is None:
            dst.genStruct = {}
            fL = expr.fL.subs(minbounds)
            fR = expr.fR.subs(minbounds)
            o = [ fL.of(0), fR.of(0) ]
            gatSet = Set("{[i,j]: "+str(o[0])+"<=i<"+str(o[0]+fL.n)+" and "+str(o[1])+"<=j<"+str(o[1]+fR.n)+"}")
            aboveSet = expr.getStructFromAbove()
            for s in aboveSet:
                t = aboveSet[s].intersect(gatSet)
                if not t.is_empty():
                    sht = t-t
                    for bs in t.get_basic_sets():
                        cs = bs.get_constraints()
                        for i in range(2):
                            tcs = []
                            for c in cs:
                                f = Constraint.equality_from_aff if c.is_equality() else Constraint.inequality_from_aff 
                                c = f( c.get_aff().add_constant_val( int(o[i]*(c.get_coefficient_val(dim_type.set, i).to_python())) ) )
                                tcs.append(c)
                            cs = tcs
                        sht = sht.union(Set.universe(t.get_space()).add_constraints(cs))
                    if not sht.is_empty():
                        dst.genStruct[s] = sht

            genAccess_maps = []
            for struct in dst.genStruct:
                matStruct = aboveSet[struct].intersect(gatSet)
                aboveMap = expr.getAccessFromAbove()
    
                inMap_basicMaps, matStruct_basicSets = aboveMap.get_basic_maps(), matStruct.get_basic_sets()
                intersecting_basicMaps = [ ibm for ibm in inMap_basicMaps if any(map(lambda mbs: not ibm.intersect_domain(mbs).domain().is_empty(), matStruct_basicSets)) ]
                
                shifted_basicMaps = []
                for bm in intersecting_basicMaps:
                    wrapped_univ = bm.universe_like().wrap()
                    wrapped_cs = bm.wrap().get_constraints()
                    for var in bm.wrap().get_var_dict().values():
                        tcs = []
                        for c in wrapped_cs:
                            if not c.is_equality():
                                f = Constraint.inequality_from_aff
                                coeff = c.get_coefficient_val(*var).to_python()
                                sign = coeff//abs(coeff) if coeff != 0 else coeff
                                c = f( c.get_aff().add_constant_val( int(sign*o[var[1]]) ) )
                            tcs.append(c)
                        wrapped_cs = tcs
                    shifted_basicMaps.append(wrapped_univ.add_constraints(wrapped_cs).unwrap())
                
                mat_set = dst.genStruct[struct]
                for sbm in shifted_basicMaps:
                    m = Map.from_basic_map(sbm.universe_like())
                    test_m = Map.from_basic_map(sbm.universe_like()).intersect_domain(mat_set)
                    for c in sbm.get_constraints():
                        tm = test_m.add_constraint(c)
                        if test_m != tm:
                            test_m = tm
                            m = m.add_constraint(c)
                    genAccess_maps.append(m)

            genAccess = genAccess_maps[0]
            for m in genAccess_maps[1:]:
                genAccess = genAccess.union(m)
            dst.setGenAccess(genAccess)

        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, minbounds, iterspace)


    def G(self, expr, opts, minbounds, iterspace):

        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, minbounds, iterspace)

        dst = expr.out
        sub = expr.getInexprMat(0)

        if dst.genStruct is None:
            dst.genStruct = {}
            fL = expr.fL.subs(minbounds)
            fR = expr.fR.subs(minbounds)
            o = [ fL.of(0), fR.of(0) ]
            gatSet = Set("{[i,j]: "+str(o[0])+"<=i<"+str(o[0]+fL.n)+" and "+str(o[1])+"<=j<"+str(o[1]+fR.n)+"}")
            inSet = sub.genStruct
            for s in inSet: #For every type of content create a structure for the gather subtructing the origin from the aff conditions
                t = inSet[s].intersect(gatSet)
                if not t.is_empty():
                    sht = t-t
                    for bs in t.get_basic_sets():
                        cs = bs.get_constraints()
                        for i in range(2):
                            tcs = []
                            for c in cs:
                                f = Constraint.equality_from_aff if c.is_equality() else Constraint.inequality_from_aff
                                coeff = c.get_coefficient_val(dim_type.set, i).to_python()
                                sign = coeff//abs(coeff) if coeff != 0 else coeff 
                                c = f( c.get_aff().add_constant_val( int(sign*o[i]) ) )
                                tcs.append(c)
                            cs = tcs
                        sht = sht.union(Set.universe(t.get_space()).add_constraints(cs))
                    if not sht.is_empty():
                        dst.genStruct[s] = sht
            

            genAccess_maps = []
            for struct in dst.genStruct:
                matStruct = inSet[struct].intersect(gatSet)
                inMap = sub.genAccess()
    
                inMap_basicMaps, matStruct_basicSets = inMap.get_basic_maps(), matStruct.get_basic_sets()
                intersecting_basicMaps = [ ibm for ibm in inMap_basicMaps if any(map(lambda mbs: not ibm.intersect_domain(mbs).domain().is_empty(), matStruct_basicSets)) ]
                
                shifted_basicMaps = []
                for bm in intersecting_basicMaps:
                    wrapped_univ = bm.universe_like().wrap()
                    wrapped_cs = bm.wrap().get_constraints()
                    for var in bm.wrap().get_var_dict().values():
                        tcs = []
                        for c in wrapped_cs:
                            if not c.is_equality():
                                f = Constraint.inequality_from_aff
                                coeff = c.get_coefficient_val(*var).to_python()
                                sign = coeff//abs(coeff) if coeff != 0 else coeff
                                c = f( c.get_aff().add_constant_val( int(sign*o[var[1]]) ) )
                            tcs.append(c)
                        wrapped_cs = tcs
                    shifted_basicMaps.append(wrapped_univ.add_constraints(wrapped_cs).unwrap())
                
                mat_set = dst.genStruct[struct]
                for sbm in shifted_basicMaps:
                    m = Map.from_basic_map(sbm.universe_like())
                    test_m = Map.from_basic_map(sbm.universe_like()).intersect_domain(mat_set)
                    for c in sbm.get_constraints():
                        tm = test_m.add_constraint(c)
                        if test_m != tm:
                            test_m = tm
                            m = m.add_constraint(c)
                    genAccess_maps.append(m)

            genAccess = genAccess_maps[0]
            for m in genAccess_maps[1:]:
                genAccess = genAccess.union(m)
            dst.setGenAccess(genAccess)
            
    def Scalar(self, expr, opts, minbounds, iterspace):
        self.Matrix(expr, opts, minbounds, iterspace)

    def SquaredMatrix(self, expr, opts, minbounds, iterspace):
        self.Matrix(expr, opts, minbounds, iterspace)

    def LowerTriangular(self, expr, opts, minbounds, iterspace):
        self.Matrix(expr, opts, minbounds, iterspace)

    def UpperTriangular(self, expr, opts, minbounds, iterspace):
        self.Matrix(expr, opts, minbounds, iterspace)

    def LowerUnitTriangular(self, expr, opts, minbounds, iterspace):
        self.Matrix(expr, opts, minbounds, iterspace)

    def UpperUnitTriangular(self, expr, opts, minbounds, iterspace):
        self.Matrix(expr, opts, minbounds, iterspace)

    def Symmetric(self, expr, opts, minbounds, iterspace):
        self.Matrix(expr, opts, minbounds, iterspace)

    def IdentityMatrix(self, expr, opts, minbounds, iterspace):
        self.Matrix(expr, opts, minbounds, iterspace)

    def AllEntriesConstantMatrixWithValue(self, expr, opts, minbounds, iterspace):
        self.Matrix(expr, opts, minbounds, iterspace)

    def Matrix(self, expr, opts, minbounds, iterspace):
        if expr.genStruct is None:
            s = expr.getFlatPolyStructureFromIndices(expr.spaceIdxNames[0]+expr.spaceIdxNames[1], expr.o, expr.getFlatSize())
            expr.genStruct = dict( (strct,sset) for strct, sset in s.items() if not sset.is_empty() ) 

    def Iv(self, expr, opts, minbounds, iterspace):
        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts, minbounds, iterspace)

        if expr.out.genStruct is None:
            expr.out.genStruct = expr.getInexprMat(0).genStruct

    def Add(self, expr, opts, minbounds, iterspace):
        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, minbounds, iterspace)

        dst = expr.out
        src0 = expr.getInexprMat(0)
        src1 = expr.getInexprMat(1)

        if dst.genStruct is None:
            dst.genStruct = {}
            s0, s1 = src0.genStruct, src1.genStruct
            pairs = [ (p0,p1) for p0 in s0 for p1 in s1 ]
            for p in pairs:
                if p[0] is ZeroMatrix and p[1] is ZeroMatrix:
                    dst.genStruct[ZeroMatrix] = s0[p[0]].intersect(s1[p[1]]) 
                else:
                    if Matrix in dst.genStruct:
                        dst.genStruct[Matrix] = dst.genStruct[Matrix].union(s0[p[0]].intersect(s1[p[1]]))
                    else:
                        dst.genStruct[Matrix] = s0[p[0]].intersect(s1[p[1]])
            dst.genStruct = dict( (strct, sset) for strct, sset in dst.genStruct.items() if not sset.is_empty() )

    def Sub(self, expr, opts, minbounds, iterspace):
        self.Add(expr, opts, minbounds, iterspace)
        
    def Kro(self, expr, opts, minbounds, iterspace):

        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, minbounds, iterspace)

        src0 = expr.getInexprMat(0)
        src1 = expr.getInexprMat(1)
        dst = expr.out

        if dst.genStruct is None:
            dst.genStruct = src0.genStruct if src1.isScalar() else src1.genStruct 

    def Div(self, expr, opts, minbounds, iterspace):

        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, minbounds, iterspace)

        src0 = expr.getInexprMat(0)
        dst = expr.out

        if dst.genStruct is None:
#             dst.genStruct = src0.genStruct 
            # This should come from a scalar computation
            dst.genStruct = { Matrix: src0.genStruct.values()[0] } 

    def Sqrt(self, expr, opts, minbounds, iterspace):

        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, minbounds, iterspace)

        src0 = expr.getInexprMat(0)
        dst = expr.out

        if dst.genStruct is None:
            dst.genStruct = src0.genStruct 

    def Neg(self, expr, opts, minbounds, iterspace):

        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, minbounds, iterspace)

        src0 = expr.getInexprMat(0)
        dst = expr.out

        if dst.genStruct is None:
            dst.genStruct = src0.genStruct 

    def LDiv(self, expr, opts, minbounds, iterspace):
        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, minbounds, iterspace)

        src0 = expr.getInexprMat(0)
        src1 = expr.getInexprMat(1)
        dst = expr.out
        
        if dst.genStruct is None:
            lgs, rgs = src0.genStruct[Matrix], src1.genStruct[Matrix]
            lzs, rzs = src0.genStruct.get(ZeroMatrix, lgs.empty(lgs.get_space())), src1.genStruct.get(ZeroMatrix, rgs.empty(rgs.get_space()))
            lids, rids = lgs.get_var_names(dim_type.set), rgs.get_var_names(dim_type.set)
            lzs = lzs.insert_dims(dim_type.set, 2, 1).set_dim_name(dim_type.set, 2, rids[1])
            rzs = rzs.insert_dims(dim_type.set, 1, 1).set_dim_name(dim_type.set, 1, lids[0])
            zeroStruct = (rzs - lzs.intersect(rzs)).project_out(dim_type.set, 0, 1)
            matStruct = dst.getFlatBoundingSet([lids[1],rids[1]])-zeroStruct
            dst.genStruct = {}
            if not matStruct.is_empty():
                dst.genStruct[Matrix] = matStruct
            if not zeroStruct.is_empty():
                dst.genStruct[ZeroMatrix] = zeroStruct
        
    def Mul(self, expr, opts, minbounds, iterspace):

        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, minbounds, iterspace)

        src0 = expr.getInexprMat(0)
        src1 = expr.getInexprMat(1)
        dst = expr.out
        
        if dst.genStruct is None:
            lgs, rgs = src0.genStruct[Matrix], src1.genStruct[Matrix]
            lids, rids = lgs.get_var_names(dim_type.set), rgs.get_var_names(dim_type.set)
            lgs = lgs.insert_dims(dim_type.set, 2, 1).set_dim_name(dim_type.set, 2, rids[1])
            rgs = rgs.insert_dims(dim_type.set, 0, 1).set_dim_name(dim_type.set, 0, lids[0])
            matStruct = lgs.intersect(rgs).project_out(dim_type.set, 1, 1)
            zeroStruct = dst.getFlatBoundingSet([lids[0],rids[1]])-matStruct
            dst.genStruct = {}
            if not matStruct.is_empty():
                dst.genStruct[Matrix] = matStruct
            if not zeroStruct.is_empty():
                dst.genStruct[ZeroMatrix] = zeroStruct

    def T(self, expr, opts, minbounds, iterspace):

        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, minbounds, iterspace)
        
        src = expr.getInexprMat(0)
        dst = expr.out

        if dst.genStruct is None:
            mTrans = Map("{[i,j]->[j,i]}")
            dst.genStruct = {}
            for s in src.genStruct:
                genStruct = mTrans.intersect_domain(src.genStruct[s]).range()
                for i in range(len(dst.spaceIdxNames)):
                    if dst.spaceIdxNames[i][0]:
                        genStruct = genStruct.set_dim_name(dim_type.set, i, dst.spaceIdxNames[i][0])
                dst.genStruct[s] = genStruct 

class BcastTableBuilder(object):
    '''
    Determines how to load a scalar element at a given point (i.e., as a single element or broadcasting).
    '''
    def __init__(self):
        self.bcTable = {}
    
    def build(self, expr):
        getattr(self, expr.__class__.__name__)(expr)
        return self.bcTable
        
    def Assign(self, expr):
        bc = self.bcTable.get(expr.inexpr[0].name, expr.getInexprMat(0).isScalar())
        l = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], bc)
        r = getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], l)
        if l == True and l != r:
            l = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], r)
        self.bcTable[expr.out.name] = l
        
    def Scalar(self, expr, bc):
        self.bcTable[expr.name] = bc
        return bc

    def Matrix(self, expr, bc):
        self.bcTable[expr.name] = bc
        return bc

    def SquaredMatrix(self, expr, bc):
        return self.Matrix(expr, bc)

    def LowerTriangular(self, expr, bc):
        return self.Matrix(expr, bc)

    def UpperTriangular(self, expr, bc):
        return self.Matrix(expr, bc)

    def LowerUnitTriangular(self, expr, bc):
        return self.Matrix(expr, bc)

    def UpperUnitTriangular(self, expr, bc):
        return self.Matrix(expr, bc)

    def Symmetric(self, expr, bc):
        return self.Matrix(expr, bc)

    def IdentityMatrix(self, expr, bc):
        return self.Matrix(expr, bc)

    def AllEntriesConstantMatrixWithValue(self, expr, bc):
        return self.Matrix(expr, bc)

    def NewSum(self, expr, bc):
        bc = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], bc)
        self.bcTable[expr.out.name] = bc
        return bc

    def S(self, expr, bc):
        bc = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], bc)
        self.bcTable[expr.out.name] = bc
        return bc

    def Sacc(self, expr, bc):
        bc = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], bc)
        self.bcTable[expr.out.name] = bc
        return bc
    
    def G(self, expr, bc):
        bc = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], bc)
        self.bcTable[expr.out.name] = bc
        return bc

    def Iv(self, expr, bc):
        bc = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], bc)
        self.bcTable[expr.out.name] = bc
        return bc

    def Add(self, expr, bc):
        l = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], bc)
        r = getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], l)
        if l == True and l != r:
            l = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], r)
        self.bcTable[expr.out.name] = l
        return l

    def Sub(self, expr, bc):
        # Assumed same case as for Add
        l = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], bc)
        r = getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], l)
        if l == True and l != r:
            l = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], r)
        self.bcTable[expr.out.name] = l
        return l

    def Kro(self, expr, bc):
        src0, src1 = expr.getInexprMat(0), expr.getInexprMat(1)
        bc = bc and src0.isScalar() and src1.isScalar() or src0.isScalar() and not src1.isScalar() or not src0.isScalar() and src1.isScalar() 
        l = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], bc)
        r = getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], bc)
        self.bcTable[expr.out.name] = l or r
        return l or r

    def LDiv(self, expr, bc):
        # Depending on the implementation of the v-BLAC this may change
        l = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], bc)
        r = getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], bc)
        self.bcTable[expr.out.name] = bc
        return bc

    def Div(self, expr, bc):
        # Depending on the implementation of the v-BLAC this may change
        l = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], bc)
        r = getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], bc)
        self.bcTable[expr.out.name] = bc
        return bc

    def Sqrt(self, expr, bc):
        # Depending on the implementation of the v-BLAC this may change
        l = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], bc)
        self.bcTable[expr.out.name] = bc
        return bc

    def Neg(self, expr, bc):
        # Depending on the implementation of the v-BLAC this may change
        l = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], bc)
        self.bcTable[expr.out.name] = bc
        return bc

    def Mul(self, expr, bc):
        src0, src1 = expr.getInexprMat(0), expr.getInexprMat(1)
        dst = expr.out
        bc = bc and not dst.isScalar() and (src0.isScalar() or src1.isScalar())
        l = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], bc if src0.isScalar() else False)
        r = getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], bc if src1.isScalar() else False)
        self.bcTable[expr.out.name] = l or r
        return l or r

    def T(self, expr, bc):
        bc = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], bc)
        self.bcTable[expr.out.name] = bc
        return bc
    
class StructuresGenerator(Generator):
    def __init__(self, sllprog, opts):
        self.nublac = opts['isaman'].getNuBLAC(opts['precision'], opts['nu'])
        self.scablac = opts['isaman'].getNuBLAC(opts['precision'], 1)
        self.allocator = NeonAllocator() if ARMv7 in opts['isaman'].isaList else NuAllocator()
#         self.genBlock(sllprog.stmtList, opts)
        self.genStructConstruct(sllprog, opts)
        for b in sllprog.stmtList:
            setstr = '{[ '+(','.join(b.ann['indices']))+' ]}'
            getattr(self, b.__class__.__name__)(b, opts, genopts={'setComp': True, 'indices': b.ann['indices'], 'iterset': Set(setstr)}, bounds={}, context=icode)
    
#     def genBlock(self, stmtList, opts):
#         for s in stmtList:
#             if isinstance(s, llLoop):
#                 self.genBlock(s.body, opts)
#             elif isinstance(s, llIf):
#                 for b in s.bodys:
#                     self.genBlock(b, opts)
#             else:
#                 self.genStructConstruct(s.eq, opts)
#                 bcastTable = self.createBcastTable(s.eq)
#                 setstr = '{[ '+(','.join(s.ann['indices']))+' ]}'
#                 self.gen(s.eq, opts, {'setComp': True, 'bcast': bcastTable, 'indices': s.ann['indices'], 'iterset': Set(setstr)})
        
    def createBcastTable(self, expr):
        return BcastTableBuilder().build(expr)
        
    def genStructConstruct(self, sllprog, opts):
        StructuresConstructor().construct(sllprog, opts)

#     def extractGenParams(self, expr, bounds, opts):
#         if expr.genParams is None:
#             out = expr.getOut()
#             expr.genParams = self.allocator.extractParams(out, bounds, opts)
#         return expr.genParams
        
    def Load(self, mParamsList, opts):
        instructions = []
        for mParams in mParamsList:
#             if mParams['nu'] > 1:
            loader = opts['isaman'].getLoader(opts['precision'], mParams['nu'])
            instructions += loader.loadMatrix(mParams)
        return instructions

    def Store(self, mParamsList, opts):
        instructions = []
        for mParams in mParamsList:
#             if mParams['nu'] > 1:
            storer = opts['isaman'].getStorer(opts['precision'], mParams['nu'])
            instructions += storer.storeMatrix(mParams)
        return instructions

    def Pack(self, mParamsList, opts):
        instructions = []
        packer = opts['isaman'].getPacker()
        instructions += packer.pack(mParamsList)
        return instructions

    def Unpack(self, mParamsList, opts):
        instructions = []
        packer = opts['isaman'].getPacker()
        instructions += packer.unpack(mParamsList)
        return instructions

#     def gen(self, stmtList, opts, genopts, bounds, context):
# #     def gen(self, expr, opts, genopts, bounds=None, context=None):
# #         if bounds is None:
# #             bounds = {}
# #         if context is None:
# #             context = icode
#         for s in stmtList:
#             getattr(self, s.__class__.__name__)(s, opts, genopts, bounds, context)

    def llBlock(self, expr, opts, genopts, bounds, context=None):
        for s in expr:
            getattr(self, s.__class__.__name__)(s, opts, genopts, bounds, context)
    
    def llFor(self, expr, opts, genopts, bounds, context=None):
#         self.gen(expr.body, opts, genopts, bounds, context)
        idx = expr.idx
        lb = expr.lb.subs(bounds)
        ub = expr.ub.subs(bounds)
        s = expr.s
        loccontext = context
        # q > 0 means a loop body is required
        # r > 0 means the body should be executed outside the loop, binding the idx to r values
        uf = expr.uFactor
        #These replaces could prob go since in sLL floord/ceild re no longer used 
        a,b = sympy.Wild('a'), sympy.Wild('b')
        L = ub-lb+1
        L = L.replace(sympy.Function('floord')(a,b), sympy.floor(a/b))
        L = L.replace(sympy.Function('ceild')(a,b), sympy.ceiling(a/b))
        L = L.subs({sympy.Function('min'): sympy.Min, sympy.Function('max'): sympy.Max})
        if L.is_Number and s.is_Number:
            if opts['unroll'][str(idx)] == 1:
                uf = L//s
            if L > 0:
                if uf*s > L:
                    uf = L//s
                q = L//(uf*s) if uf > 0 else 0
                r = int(math.ceil((L%(uf*s))/float(s))) if uf > 0 else 1 
    #             r = (L%(uf*s))//s if uf > 0 else 1 
       
                for k in range(r):
                    # Compute the body within the parent context binding the value of idx (if idx is declared)
                    newBounds = dict(bounds.items() + [(idx, lb)])# if idx.needsLoop() else bounds
                    genoptsCopy = deepcopy(genopts)
                    genoptsCopy['setComp'] = False
                    getattr(self, expr.body.__class__.__name__)(expr.body, opts, genoptsCopy, newBounds, context)
                    lb = lb + s
                # Depending on the unrolling factor the loop body could be repeated
    #             loccontext = context
                iterSet = genopts['iterset']
                if q > 1:
                    loccontext = ForLoop(idx, lb, ub, s*uf) #if uIdx.needsLoop() else context
                    base = idx
                    newSet = Set('{['+(','.join(genopts['indices']))+']: exists a: '+str(idx)+'='+str(s*uf)+'a and '+str(lb)+'<='+str(idx)+'<='+str(ub)+'}')
                    iterSet = iterSet.intersect(newSet)
                else:
                    base = lb
                       
                for k in range(uf):
                    # Get ranges that will be used to address the proper tile in the matrix
                    # Compute the body within the parent context binding the value of idx (if idx is declared)
                    newBounds = dict(bounds.items() + [(idx, base+k*s)])# if idx.needsLoop() else bounds
                    genoptsCopy = deepcopy(genopts)
                    genoptsCopy['setComp'] = False
                    genoptsCopy['iterset'] = iterSet
                    getattr(self, expr.body.__class__.__name__)(expr.body, opts, genoptsCopy, newBounds, context=loccontext)
       
        else:
#             if uf == sys.maxint:
#                 uf = 1
#             loccontext = ForLoop(idx, lb, ub, s*uf)
            loccontext = ForLoop(idx, lb, ub, s)
            genoptsCopy = deepcopy(genopts)
            newSet = Set('{['+(','.join(genopts['indices']))+']: exists a: '+str(idx)+'='+str(s*uf)+'a and '+str(lb)+'<='+str(idx)+'<='+str(ub)+'}')
            genoptsCopy['iterset'] = genopts['iterset'].intersect(newSet)
            getattr(self, expr.body.__class__.__name__)(expr.body, opts, genoptsCopy, bounds, context=loccontext)

#         loccontext = ForLoop(idx, lb, ub, s)
#         getattr(self, body.__class__.__name__)(body, opts, bounds, context=loccontext)        
        
        if loccontext != context:
            temp = IBlock()
            temp.instructions += [ loccontext ]
            context.blocks += [ temp ]
        
    def llIf(self, expr, opts, genopts, bounds, context=None):
        #Here considering the only branch that cloog can generate 
        needIf = expr.conds[0].isSymbolic(bounds)
        
        if needIf:
            ifcontext = SingleContext()
            simcond = expr.conds[0].simplify(bounds)
            genoptsCopy = deepcopy(genopts)
            newSet = Set(str('{['+(','.join(genopts['indices']))+']: ' + simcond.getIslStr()+ ' }'))
            genoptsCopy['iterset'] = genopts['iterset'].intersect(newSet)
            getattr(self, expr.bodys[0].__class__.__name__)(expr.bodys[0], opts, genopts, bounds, context=ifcontext)
            multicontext = If([ ifcontext ], [ simcond ] )
            temp = IBlock()
            temp.instructions += [ multicontext ]
            context.blocks += [ temp ]
        elif expr.conds[0].isTrue(bounds):
            getattr(self, expr.bodys[0].__class__.__name__)(expr.bodys[0], opts, genopts, bounds, context=context)
        
    def llStmt(self, expr, opts, genopts, bounds, context=None):
        bcastTable = self.createBcastTable(expr.eq)
        genoptsCopy = deepcopy(genopts)
        genoptsCopy['bcast'] = bcastTable
#         nublac, vec, nu = self.nublac, opts['vectorize'], opts['nu']
        nublac, vec, nu = self.nublac, opts['useintrinsics'], opts['nu']
        
        block = IBlock()
        block.instructions += [ Comment("Generating : " + str(expr.eq)) ]
        context.blocks.append(block)
        
        if vec and not expr.can_gen_with_nublac(self.nublac, exclude=[NewSum, Iv], at_least_has_op=True):
            self.nublac, opts['useintrinsics'], opts['nu'] = self.scablac, False, 1
        getattr(self, expr.eq.__class__.__name__)(expr.eq, opts, genoptsCopy, bounds, context)
        self.nublac, opts['useintrinsics'], opts['nu'] = nublac, vec, nu
        
    def Assign(self, expr, opts, genopts, bounds, context=None):
        if expr.isComputed(): return
            
        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts, genopts, bounds, context)
        getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], opts, genopts, bounds, context)

        expr.setComputed(genopts['setComp'])

    def buildLoop(self, idx, lb, ub, s, body, opts, genopts, bounds, context):
        lb = lb.subs(bounds)
        ub = ub.subs(bounds)
        loccontext = context
        # q > 0 means a loop body is required
        # r > 0 means the body should be executed outside the loop, binding the idx to r values
        uf = opts['ufs'][str(idx)]
        #These replaces could prob go since in sLL floord/ceild re no longer used 
        a,b = sympy.Wild('a'), sympy.Wild('b')
        L = ub-lb+1
        L = L.replace(sympy.Function('floord')(a,b), sympy.floor(a/b))
        L = L.replace(sympy.Function('ceild')(a,b), sympy.ceiling(a/b))
        L = L.subs({sympy.Function('min'): sympy.Min, sympy.Function('max'): sympy.Max})
        if L.is_Number and s.is_Number:
            if opts['unroll'][str(idx)] == 1:
                uf = L//s
            if L > 0:
                if uf*s > L:
                    uf = L//s
                q = L//(uf*s) if uf > 0 else 0
                r = int(math.ceil((L%(uf*s))/float(s))) if uf > 0 else 1 
    #             r = (L%(uf*s))//s if uf > 0 else 1 
       
                for k in range(r):
                    # Compute the body within the parent context binding the value of idx (if idx is declared)
                    newBounds = dict(bounds.items() + [(idx, lb)])# if idx.needsLoop() else bounds
                    genoptsCopy = deepcopy(genopts)
                    genoptsCopy['setComp'] = False
                    
                    getattr(self, body.__class__.__name__)(body, opts, genoptsCopy, newBounds, context)
                    lb = lb + s
                # Depending on the unrolling factor the loop body could be repeated
    #             loccontext = context
                iterSet = genopts['iterset']
                if q > 1:
                    loccontext = ForLoop(idx, lb, ub, s*uf) #if uIdx.needsLoop() else context
                    base = idx
                    newSet = Set('{['+(','.join(genopts['indices']))+']: exists a: '+str(idx)+'='+str(s*uf)+'a and '+str(lb)+'<='+str(idx)+'<='+str(ub)+'}')
                    iterSet = iterSet.intersect(newSet)
                else:
                    base = lb
                       
                for k in range(uf):
                    # Get ranges that will be used to address the proper tile in the matrix
                    # Compute the body within the parent context binding the value of idx (if idx is declared)
                    newBounds = dict(bounds.items() + [(idx, base+k*s)])# if idx.needsLoop() else bounds
                    genoptsCopy = deepcopy(genopts)
                    genoptsCopy['setComp'] = False
                    genoptsCopy['iterset'] = iterSet
                    getattr(self, body.__class__.__name__)(body, opts, genoptsCopy, newBounds, context=loccontext)
       
        else:
#             if uf == sys.maxint:
#                 uf = 1
#             loccontext = ForLoop(idx, lb, ub, s*uf)
            loccontext = ForLoop(idx, lb, ub, s)
            genoptsCopy = deepcopy(genopts)
            newSet = Set('{['+(','.join(genopts['indices']))+']: exists a: '+str(idx)+'='+str(s*uf)+'a and '+str(lb)+'<='+str(idx)+'<='+str(ub)+'}')
            genoptsCopy['iterset'] = genopts['iterset'].intersect(newSet)
            getattr(self, body.__class__.__name__)(body, opts, genoptsCopy, bounds, context=loccontext)

#         loccontext = ForLoop(idx, lb, ub, s)
#         getattr(self, body.__class__.__name__)(body, opts, bounds, context=loccontext)        
        
        if loccontext != context:
            temp = IBlock()
            temp.instructions += [ loccontext ]
            context.blocks += [ temp ]
    
    def NewSum(self, expr, opts, genopts, bounds, context=None):
        if expr.isComputed(): return
        
        idxList = list(expr.depSet-set(bounds.keys()))
        genoptsCopy = deepcopy(genopts)
        indepList = computeIndependentSubexprWithBounds(expr.inexpr[0], idxList, bounds, genoptsCopy, opts)
        for e in indepList:
            getattr(self, e[0].__class__.__name__)(e[0], opts, e[1], bounds, context)

        genoptsCopy = deepcopy(genopts)
        if expr.init:
            genoptsCopy['init'] = True
            dst, nuDst = expr.out, expr.nuout 
            dParams = self.allocator.extractParams(dst, bounds, opts, subNuM=nuDst)
            expr.nuout = dParams['nuM'] 
             
            block = IBlock()
     
#             if dParams['nuable']:
            block.instructions += self.nublac.Zero(dParams, opts)
#                 block.instructions += self.Store([dParams], opts)
#             else:
#                 dL, dR   = dParams['mL'], dParams['mR']
#                 M, N = dParams['M'], dParams['N']
#                 for i in range(M):
#                     for j in range(N):
#                         instr = Mov(V(0), sa(dst[dL.of(i),dR.of(j)]))
#                         block.instructions += [ instr ]
 
     
            for i in block.instructions:
                i.setIterSet(genopts['indices'], genopts['iterset'])  
     
            if context is not None:
                context.blocks += [ block ]
            else:
                icode.blocks += [ block ]
        else:
            genoptsCopy['init'] = False
            
        self.buildLoop(sympify(expr.idx), expr.lb, expr.ub, expr.s, expr.inexpr[0], opts, genoptsCopy, bounds, context)
        if expr.out.genStruct is None:
            expr.out.genStruct = expr.getInexprMat(0).genStruct
        expr.setComputed(genopts['setComp'])

    def S(self, expr, opts, genopts, bounds, context=None):
        if expr.isComputed(): return

        sub = expr.getInexprMat(0)
        dst = expr.out

        gatDst = G(expr.fL, dst, expr.fR, setAsPred=False)
        gdst = gatDst.getOut()
        dstPhys = icode.bindingTable.getPhysicalLayout(dst)
        icode.bindingTable.addBinding(gdst, dstPhys)
        gdst.fL, gdst.fR, gdst.genStruct = expr.fL, expr.fR, expr.out.genStruct
        gdst.setGenAccess(expr.out.genAccess())
        
        subParams = self.allocator.extractParams(sub, bounds, opts, bcast=genopts['bcast'][sub.name])
        expr.inexpr[0].nuout = subParams['nuM']
        dParams = self.allocator.extractParams(gdst, bounds, opts, subNuM=subParams['nuM'])

        if sub.size[0] > opts['nu'] or sub.size[1] > opts['nu']: 
            block = IBlock()
            # Required to avoid overwriting correct values when unpacking.
            # e.g., S2-S1-+ the result of + would cover a partial tile of S1.out.
            # If we don't pack previously then S2 would write spurious values back when unpacking.    
            block.instructions += self.Pack([dParams, subParams], opts)

            for i in block.instructions:
                i.setIterSet(genopts['indices'], genopts['iterset'])  

            if context is not None:
                context.blocks += [ block ]
            else:
                icode.blocks += [ block ]
                
        for s in expr.inexpr:
            getattr(self, s.__class__.__name__)(s, opts, genopts, bounds, context)
            
        block = IBlock()
        if sub.size[0] > opts['nu'] or sub.size[1] > opts['nu']: 
            block.instructions += self.Unpack([subParams, dParams], opts)
        else:
#             nusub = expr.getInexprNuMat(0)
#             subParams = self.allocator.extractParams(sub, bounds, opts, subNuM=nusub)
            
            if isinstance(expr.inexpr[0], G):
#                 if subParams['nuable'] and dParams['nuable']:
                sub, nusub = expr.getInexprMatNuMat(0)
                subParams = self.allocator.extractParams(sub, bounds, opts, bcast=genopts['bcast'][sub.name], subNuM=nusub )
                block.instructions += self.nublac.Copy(subParams, dParams, opts)
#                 else:
#                     subL, subR = subParams['mL'], subParams['mR']
#                     dL, dR   = dParams['mL'], dParams['mR']
#                     M, N = subParams['M'], subParams['N']
#                     for i in range(M):
#                         for j in range(N):
#                             instr = Mov(sa(sub[subL.of(i),subR.of(j)]), sa(dst[dL.of(i),dR.of(j)]))
#                             block.instructions += [ instr ]
#             if subParams['nuable']:
            block.instructions += self.Store([dParams], opts)
        
        for i in block.instructions:
            i.setIterSet(genopts['indices'], genopts['iterset'])  
            
        if context is not None:
            context.blocks += [ block ]
        else:
            icode.blocks += [ block ]
        expr.setComputed(genopts['setComp'])

    def Sacc(self, expr, opts, genopts, bounds, context=None):
        if expr.isComputed(): return

        sub = expr.getInexprMat(0)
        dst = expr.out
        
        gatDst = G(expr.fL, dst, expr.fR, setAsPred=False)
        gdst = gatDst.getOut()
        dstPhys = icode.bindingTable.getPhysicalLayout(dst)
        icode.bindingTable.addBinding(gdst, dstPhys)
        gdst.fL, gdst.fR, gdst.genStruct = expr.fL, expr.fR, expr.out.genStruct
        gdst.setGenAccess(expr.out.genAccess())

        subParams = self.allocator.extractParams(sub, bounds, opts, bcast=genopts['bcast'][sub.name])
        expr.inexpr[0].nuout = subParams['nuM']
        if genopts.get('init', False):
            dParams = self.allocator.extractParams(gdst, bounds, opts, subNuM=expr.pred[0][0].getNuOut())
        else:
            dParams = self.allocator.extractParams(gdst, bounds, opts) # In case of $ dParams can be associated to a different nuout
        
        if sub.size[0] > opts['nu'] or sub.size[1] > opts['nu']: 
            block = IBlock()
            block.instructions += self.Pack([dParams, subParams], opts)

            for i in block.instructions:
                i.setIterSet(genopts['indices'], genopts['iterset'])  

            if context is not None:
                context.blocks += [ block ]
            else:
                icode.blocks += [ block ]

        for s in expr.inexpr:
            getattr(self, s.__class__.__name__)(s, opts, genopts, bounds, context)

        block = IBlock()

        if sub.size[0] > opts['nu'] or sub.size[1] > opts['nu']: 
            block.instructions += self.Unpack([subParams, dParams], opts)
        else:
#             if subParams['nuable'] and dParams['nuable']:
            if genopts.get('init', False):
                block.instructions += self.nublac.Add(subParams, dParams, dParams, opts)
            else:
                block.instructions += self.Load([dParams], opts)
                if expr.neg:
                    block.instructions += self.nublac.Sub(dParams, subParams, dParams, opts)
                else:
                    block.instructions += self.nublac.Add(dParams, subParams, dParams, opts)
                block.instructions += self.Store([dParams], opts)
#             else:
#                 subL, subR = subParams['mL'], subParams['mR']
#                 dL, dR   = dParams['mL'], dParams['mR']
#                 M, N = subParams['M'], subParams['N']
#                 for i in range(M):
#                     for j in range(N):
#                         instr = Mov(ScaAdd(sa(dst[dL.of(i),dR.of(j)]), sa(sub[subL.of(i),subR.of(j)])), sa(dst[dL.of(i),dR.of(j)]))
#                         block.instructions += [ instr ]

        for i in block.instructions:
            i.setIterSet(genopts['indices'], genopts['iterset'])  
            
        if context is not None:
            context.blocks += [ block ]
        else:
            icode.blocks += [ block ]
         
#         block = IBlock()
#         instr = Mov(ScaAdd(sa(dst[expr.fL.of(0),expr.fR.of(0)]),sa(sub[sub.fL.of(0),sub.fR.of(0)])), sa(dst[expr.fL.of(0),expr.fR.of(0)]))
#         block.instructions += [ instr ]
#         
#         if context is not None:
#             context.blocks += [ block ]
#         else:
#             icode.blocks += [ block ]
        expr.setComputed(genopts['setComp'])

    def G(self, expr, opts, genopts, bounds, context=None):
        if expr.isComputed(): return

        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, genopts, bounds, context)

        sub, nusub = expr.getInexprMatNuMat(0)
        dst = expr.out

        block = IBlock()
        
        if dst.size[0] > opts['nu'] or dst.size[1] > opts['nu']:
            gatSub = G(expr.fL, sub, expr.fR, setAsPred=False)
            gsub = gatSub.getOut()
            dstPhys = icode.bindingTable.getPhysicalLayout(sub)
            icode.bindingTable.addBinding(gsub, dstPhys)
            gsub.fL, gsub.fR, gsub.genStruct = expr.fL, expr.fR, expr.out.genStruct
            gsub.setGenAccess(expr.out.genAccess())
            
            dParams = self.allocator.extractParams(dst, bounds, opts)
            subParams = self.allocator.extractParams(gsub, bounds, opts)
            
            block.instructions += self.Pack([subParams, dParams], opts)
        else:
            subParams = self.allocator.extractParams(dst, bounds, opts, bcast=genopts['bcast'][dst.name], subNuM=nusub)
            block.instructions += self.Load([subParams], opts)
            expr.nuout = subParams['nuM']

        for i in block.instructions:
            i.setIterSet(genopts['indices'], genopts['iterset'])  
            
        if context is not None:
            context.blocks += [ block ]
        else:
            icode.blocks += [ block ]
        expr.setComputed(genopts['setComp'])
            
    def Scalar(self, expr, opts, genopts, bounds, context=None):
        self.Matrix(expr, opts, genopts, bounds, context)

    def SquaredMatrix(self, expr, opts, genopts, bounds, context=None):
        self.Matrix(expr, opts, genopts, bounds, context)

    def LowerTriangular(self, expr, opts, genopts, bounds, context=None):
        self.Matrix(expr, opts, genopts, bounds, context)

    def UpperTriangular(self, expr, opts, genopts, bounds, context=None):
        self.Matrix(expr, opts, genopts, bounds, context)

    def LowerUnitTriangular(self, expr, opts, genopts, bounds, context=None):
        self.Matrix(expr, opts, genopts, bounds, context)

    def UpperUnitTriangular(self, expr, opts, genopts, bounds, context=None):
        self.Matrix(expr, opts, genopts, bounds, context)

    def Symmetric(self, expr, opts, genopts, bounds, context=None):
        self.Matrix(expr, opts, genopts, bounds, context)

    def IdentityMatrix(self, expr, opts, genopts, bounds, context=None):
        self.Matrix(expr, opts, genopts, bounds, context)

    def AllEntriesConstantMatrixWithValue(self, expr, opts, genopts, bounds, context=None):
        self.Matrix(expr, opts, genopts, bounds, context)

    def Matrix(self, expr, opts, genopts, bounds, context=None):
        if expr.isComputed(): return
        expr.setComputed(genopts['setComp'])

    def Iv(self, expr, opts, genopts, bounds, context=None):
        if expr.isComputed(): return
        
        needIf = expr.cond.isSymbolic(bounds)
        condIsTrue = False
        if not needIf:
            condIsTrue = expr.cond.isTrue(bounds)
            
        if expr.init:
            expr.inexpr[0].nuout = expr.nuout
            if needIf or not condIsTrue:
                dst, nuDst = expr.out, expr.nuout 
                dParams = self.allocator.extractParams(dst, bounds, opts, subNuM=nuDst)
                expr.nuout = dParams['nuM'] 
                expr.inexpr[0].nuout = dParams['nuM']
    
                block = IBlock()
         
#                 if dParams['nuable']:
                block.instructions += self.nublac.Zero(dParams, opts)
#                 else:
#                     dL, dR   = dParams['mL'], dParams['mR']
#                     M, N = dParams['M'], dParams['N']
#                     for i in range(M):
#                         for j in range(N):
#                             instr = Mov(V(0), sa(dst[dL.of(i),dR.of(j)]))
#                             block.instructions += [ instr ]
     
         
                for i in block.instructions:
                    i.setIterSet(genopts['indices'], genopts['iterset'])  
         
                if context is not None:
                    context.blocks += [ block ]
                else:
                    icode.blocks += [ block ]

        if needIf:
            ifcontext = SingleContext()
            simcond = expr.cond.simplify(bounds)
            genoptsCopy = deepcopy(genopts)
            newSet = Set(str('{['+(','.join(genopts['indices']))+']: ' + simcond.getIslStr()+ ' }'))
            genoptsCopy['iterset'] = genopts['iterset'].intersect(newSet)
            getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts, genopts, bounds, context=ifcontext)
            multicontext = If([ ifcontext ], [ simcond ] )
            temp = IBlock()
            temp.instructions += [ multicontext ]
            context.blocks += [ temp ]
        elif condIsTrue:
            getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts, genopts, bounds, context=context)
            
        if expr.out.genStruct is None:
            expr.out.genStruct = expr.getInexprMat(0).genStruct
        

    def Add(self, expr, opts, genopts, bounds, context=None):
        if expr.isComputed(): return
        for sub in expr.inexpr:
#             genoptsCopy = deepcopy(genopts)
#             genoptsCopy['bcast'] = False
            getattr(self, sub.__class__.__name__)(sub, opts, genopts, bounds, context)
        
        dst, nuDst = expr.out, expr.nuout 
        if icode.bindingTable.isBound(dst) and icode.bindingTable.getPhysicalLayout(dst) is not None:

            src0, nuSrc0 = expr.getInexprMatNuMat(0)
            src1, nuSrc1 = expr.getInexprMatNuMat(1)

            s0Params = self.allocator.extractParams(src0, bounds, opts, subNuM=nuSrc0)
            s1Params = self.allocator.extractParams(src1, bounds, opts, subNuM=nuSrc1)
            dParams = self.allocator.extractParams(dst, bounds, opts, subNuM=nuDst)
            expr.nuout = dParams['nuM'] 
            
            block = IBlock()
    
#             if s0Params['nuable'] and s1Params['nuable'] and dParams['nuable']:
            block.instructions += self.nublac.Add(s0Params, s1Params, dParams, opts)
#             else:
#                 s0L, s0R = s0Params['mL'], s0Params['mR']
#                 s1L, s1R = s1Params['mL'], s1Params['mR']
#                 dL, dR   = dParams['mL'], dParams['mR']
#                 M, N = dParams['M'], dParams['N']
#                 for i in range(M):
#                     for j in range(N):
#                         instr = Mov(ScaAdd(sa(src0[s0L.of(i),s0R.of(j)]), sa(src1[s1L.of(i),s1R.of(j)])), sa(dst[dL.of(i),dR.of(j)]))
#                         block.instructions += [ instr ]

    
            for i in block.instructions:
                i.setIterSet(genopts['indices'], genopts['iterset'])  
    
            if context is not None:
                context.blocks += [ block ]
            else:
                icode.blocks += [ block ]
            
#             block = IBlock()
#             instr = Mov(ScaAdd(sa(src0[src0.fL.of(0),src0.fR.of(0)]), sa(src1[src1.fL.of(0),src1.fR.of(0)])), sa(dst[dst.fL.of(0),dst.fR.of(0)]))
#             block.instructions += [ instr ]
#                 
#             
#             if context is not None:
#                 context.blocks += [ block ]
#             else:
#                 icode.blocks += [ block ]
        expr.setComputed(genopts['setComp'])

    def Sub(self, expr, opts, genopts, bounds, context=None):
        if expr.isComputed(): return
        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, genopts, bounds, context)
        
        dst, nuDst = expr.out, expr.nuout 
        src0, nuSrc0 = expr.getInexprMatNuMat(0)
        src1, nuSrc1 = expr.getInexprMatNuMat(1)

        s0Params = self.allocator.extractParams(src0, bounds, opts, subNuM=nuSrc0)
        s1Params = self.allocator.extractParams(src1, bounds, opts, subNuM=nuSrc1)
        dParams = self.allocator.extractParams(dst, bounds, opts, subNuM=nuDst)
        expr.nuout = dParams['nuM'] 
        
        block = IBlock()

#         if s0Params['nuable'] and s1Params['nuable'] and dParams['nuable']:
        block.instructions += self.nublac.Sub(s0Params, s1Params, dParams, opts)
#         else:
#             s0L, s0R = s0Params['mL'], s0Params['mR']
#             s1L, s1R = s1Params['mL'], s1Params['mR']
#             dL, dR   = dParams['mL'], dParams['mR']
#             M, N = dParams['M'], dParams['N']
#             for i in range(M):
#                 for j in range(N):
#                     instr = Mov(ScaSub(sa(src0[s0L.of(i),s0R.of(j)]), sa(src1[s1L.of(i),s1R.of(j)])), sa(dst[dL.of(i),dR.of(j)]))
#                     block.instructions += [ instr ]


        for i in block.instructions:
            i.setIterSet(genopts['indices'], genopts['iterset'])

        if context is not None:
            context.blocks += [ block ]
        else:
            icode.blocks += [ block ]
        
        expr.setComputed(genopts['setComp'])

    def Kro(self, expr, opts, genopts, bounds, context=None):
        if expr.isComputed(): return
        
#         bcast = False if src0.isScalar() and src1.isScalar() else True
        for sub in expr.inexpr:
#             genoptsCopy = deepcopy(genopts)
#             genoptsCopy['bcast'] = bcast
            getattr(self, sub.__class__.__name__)(sub, opts, genopts, bounds, context)
        
        src0, src1 = expr.getInexprMat(0), expr.getInexprMat(1)
        nuSrc0, nuSrc1 = expr.getInexprNuMat(0), expr.getInexprNuMat(1)
        dst, nuDst = expr.out, expr.nuout
            
        s0Params = self.allocator.extractParams(src0, bounds, opts, bcast=genopts['bcast'][src0.name], subNuM=nuSrc0)
        s1Params = self.allocator.extractParams(src1, bounds, opts, bcast=genopts['bcast'][src1.name], subNuM=nuSrc1)
        dParams = self.allocator.extractParams(dst, bounds, opts, subNuM=nuDst)
        expr.nuout = dParams['nuM'] 
        
        block = IBlock()

#         if s0Params['nuable'] and s1Params['nuable'] and dParams['nuable']:
        block.instructions += self.nublac.Kro(s0Params, s1Params, dParams, opts)
#         else:
#             s0L, s0R = s0Params['mL'], s0Params['mR']
#             s1L, s1R = s1Params['mL'], s1Params['mR']
#             dL, dR   = dParams['mL'], dParams['mR']
#             M, K, N, P = s0Params['M'], s0Params['N'], s1Params['M'], s1Params['N']
#             for i in range(M):
#                 for k in range(K):
#                     for j in range(N):
#                         for p in range(P):
#                             instr = Mov(ScaMul(sa(src0[s0L.of(i),s0R.of(k)]), sa(src1[s1L.of(j),s1R.of(p)])), sa(dst[dL.of(i+j),dR.of(k+p)]))
#                             block.instructions += [ instr ]
            
        for i in block.instructions:
            i.setIterSet(genopts['indices'], genopts['iterset'])  
            
        if context is not None:
            context.blocks += [ block ]
        else:
            icode.blocks += [ block ]
        expr.setComputed(genopts['setComp'])
        
#         block = IBlock()
#         instr = Mov(ScaMul(sa(src0[src0.fL.of(0),src0.fR.of(0)]), sa(src1[src1.fL.of(0),src1.fR.of(0)])), sa(dst[dst.fL.of(0),dst.fR.of(0)]))
#         block.instructions += [ instr ]
#             
#         
#         if context is not None:
#             context.blocks += [ block ]
#         else:
#             icode.blocks += [ block ]
#         expr.setComputed(setComp)        
    def Mul(self, expr, opts, genopts, bounds, context=None):
        if expr.isComputed(): return

#         bcast = True if not dst.isScalar() and (src0.isScalar() or src1.isScalar()) else False
        for sub in expr.inexpr:
#             genoptsCopy = deepcopy(genopts)
#             genoptsCopy['bcast'] = bcast
            getattr(self, sub.__class__.__name__)(sub, opts, genopts, bounds, context)

#         for sub in expr.inexpr:
#             getattr(self, sub.__class__.__name__)(sub, opts, genopts, bounds, context)

        src0, src1 = expr.getInexprMat(0), expr.getInexprMat(1)
        dst = expr.out
        nuSrc0, nuSrc1 = expr.getInexprNuMat(0), expr.getInexprNuMat(1)
        nuDst = expr.nuout
# 
#         src0 = expr.getInexprMat(0)
#         src1 = expr.getInexprMat(1)
#         dst = expr.out
#         
#         s0Params, s1Params = self.allocator.extractParams(src0, bounds, opts), self.allocator.extractParams(src1, bounds, opts)
#         dParams = self.allocator.extractParams(dst, bounds, opts)

        s0Params = self.allocator.extractParams(src0, bounds, opts, bcast=genopts['bcast'][src0.name], subNuM=nuSrc0)
        s1Params = self.allocator.extractParams(src1, bounds, opts, bcast=genopts['bcast'][src1.name], subNuM=nuSrc1)
        dParams = self.allocator.extractParams(dst, bounds, opts, bcast=genopts['bcast'][dst.name], subNuM=nuDst)
        expr.nuout = dParams['nuM'] 

        block = IBlock()

        M, s0K, s1K, N = s0Params['M'], s0Params['N'], s1Params['M'], s1Params['N']

#         if s0Params['nuable'] and s1Params['nuable'] and dParams['nuable']:
        if (M*s0K == 1) or (s1K*N == 1):
            block.instructions += self.nublac.Kro(s0Params, s1Params, dParams, opts)
        else:
            block.instructions += self.nublac.Mul(s0Params, s1Params, dParams, opts)
#         else:
#             s0L, s0R = s0Params['mL'], s0Params['mR']
#             s1L, s1R = s1Params['mL'], s1Params['mR']
#             dL, dR   = dParams['mL'], dParams['mR']
#             for i in range(M):
#                 for j in range(N):
#                     instr = Mov(ScaMul(sa(src0[s0L.of(i),s0R.of(0)]), sa(src1[s1L.of(0),s1R.of(j)])), sa(dst[dL.of(i),dR.of(j)]))
#                     block.instructions += [ instr ]
# 
#             for k in range(1,s0K):
#                 for i in range(M):
#                     for j in range(N):
#                         t = ScaMul(sa(src0[s0L.of(i),s0R.of(k)]), sa(src1[s1L.of(k),s1R.of(j)]))
#                         instr = Mov(ScaAdd(sa(dst[dL.of(i),dR.of(j)]), t), sa(dst[dL.of(i),dR.of(j)]))
#                         block.instructions += [ instr ]
                    
        for i in block.instructions:
            i.setIterSet(genopts['indices'], genopts['iterset'])  
            
        if context is not None:
            context.blocks += [ block ]
        else:
            icode.blocks += [ block ]
        expr.setComputed(genopts['setComp'])

    def LDiv(self, expr, opts, genopts, bounds, context=None):
        if expr.isComputed(): return

        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, genopts, bounds, context)

        src0, src1 = expr.getInexprMat(0), expr.getInexprMat(1)
        dst = expr.out
        nuSrc0, nuSrc1 = expr.getInexprNuMat(0), expr.getInexprNuMat(1)
        nuDst = expr.nuout

        s0Params = self.allocator.extractParams(src0, bounds, opts, bcast=genopts['bcast'][src0.name], subNuM=nuSrc0)
        s1Params = self.allocator.extractParams(src1, bounds, opts, bcast=genopts['bcast'][src1.name], subNuM=nuSrc1)
        dParams = self.allocator.extractParams(dst, bounds, opts, bcast=genopts['bcast'][dst.name], subNuM=nuDst)
        expr.nuout = dParams['nuM'] 

        block = IBlock()

#         M, N = s0Params['M'], s1Params['N']

#         if s0Params['nuable'] and s1Params['nuable'] and dParams['nuable']:
        block.instructions += self.nublac.LDiv(s0Params, s1Params, dParams, opts)
#         else:
#             s0L, s0R = s0Params['mL'], s0Params['mR']
#             s1L, s1R = s1Params['mL'], s1Params['mR']
#             dL, dR   = dParams['mL'], dParams['mR']
#             for j in range(N):
#                 instr = Mov(ScaDiv(sa(src1[s1L.of(0),s1R.of(j)]), sa(src0[s0L.of(0),s0R.of(0)])), sa(dst[dL.of(0),dR.of(j)]))
#                 block.instructions += [ instr ]
#                 for i in range(1, M):
#                     t0 = ScaMul(sa(src0[s0L.of(i),s0R.of(0)]), sa(dst[dL.of(0),dR.of(j)]))
#                     for k in range(1, i):
#                         t1 = ScaMul(sa(src0[s0L.of(i),s0R.of(k)]), sa(dst[dL.of(k),dR.of(j)]))
#                         t0 = ScaAdd(t0, t1)
#                     s = ScaSub(sa(src1[s1L.of(i),s1R.of(j)]), t0)
#                     instr = Mov(ScaDiv(s, sa(src0[s0L.of(i),s0R.of(i)])), sa(dst[dL.of(i),dR.of(j)]))
#                     block.instructions += [ instr ]
                    
        for i in block.instructions:
            i.setIterSet(genopts['indices'], genopts['iterset'])  
            
        if context is not None:
            context.blocks += [ block ]
        else:
            icode.blocks += [ block ]
        expr.setComputed(genopts['setComp'])

    def Div(self, expr, opts, genopts, bounds, context=None):
        if expr.isComputed(): return

        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, genopts, bounds, context)

        src0, src1 = expr.getInexprMat(0), expr.getInexprMat(1)
        dst = expr.out
        nuSrc0, nuSrc1 = expr.getInexprNuMat(0), expr.getInexprNuMat(1)
        nuDst = expr.nuout

        s0Params = self.allocator.extractParams(src0, bounds, opts, bcast=genopts['bcast'][src0.name], subNuM=nuSrc0)
        s1Params = self.allocator.extractParams(src1, bounds, opts, bcast=genopts['bcast'][src1.name], subNuM=nuSrc1)
        dParams = self.allocator.extractParams(dst, bounds, opts, bcast=genopts['bcast'][dst.name], subNuM=nuDst)
        expr.nuout = dParams['nuM'] 

        block = IBlock()
        
        f = self.nublac.Div if hasattr(self.nublac, 'Div') else self.nublac._Div 
        block.instructions += f(s0Params, s1Params, dParams, opts)
            
        for i in block.instructions:
            i.setIterSet(genopts['indices'], genopts['iterset'])  
            
        if context is not None:
            context.blocks += [ block ]
        else:
            icode.blocks += [ block ]
        expr.setComputed(genopts['setComp'])

    def Sqrt(self, expr, opts, genopts, bounds, context=None):
        if expr.isComputed(): return
        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, genopts, bounds, context)
        
        src, nuSrc = expr.getInexprMatNuMat(0)
        dst, nuDst = expr.out, expr.nuout

        sParams = self.allocator.extractParams(src, bounds, opts, subNuM=nuSrc)
        dParams = self.allocator.extractParams(dst, bounds, opts, subNuM=nuDst)
        expr.nuout = dParams['nuM'] 
        
        block = IBlock()

        f = self.nublac.Sqrt if hasattr(self.nublac, 'Sqrt') else self.nublac._Sqrt 
        block.instructions += f(sParams, dParams, opts)

        for i in block.instructions:
            i.setIterSet(genopts['indices'], genopts['iterset'])  
            
        if context is not None:
            context.blocks += [ block ]
        else:
            icode.blocks += [ block ]
        expr.setComputed(genopts['setComp'])

    def Neg(self, expr, opts, genopts, bounds, context=None):
        if expr.isComputed(): return
        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, genopts, bounds, context)
        
        src, nuSrc = expr.getInexprMatNuMat(0)
        dst, nuDst = expr.out, expr.nuout

        sParams = self.allocator.extractParams(src, bounds, opts, subNuM=nuSrc)
        dParams = self.allocator.extractParams(dst, bounds, opts, subNuM=nuDst)
        expr.nuout = dParams['nuM'] 
        
        block = IBlock()

        block.instructions += self.nublac.Neg(sParams, dParams, opts)

        for i in block.instructions:
            i.setIterSet(genopts['indices'], genopts['iterset'])  
            
        if context is not None:
            context.blocks += [ block ]
        else:
            icode.blocks += [ block ]
        expr.setComputed(genopts['setComp'])

    def T(self, expr, opts, genopts, bounds, context=None):
        if expr.isComputed(): return
        for sub in expr.inexpr:
            getattr(self, sub.__class__.__name__)(sub, opts, genopts, bounds, context)
        
        src, nuSrc = expr.getInexprMatNuMat(0)
        dst, nuDst = expr.out, expr.nuout

        sParams = self.allocator.extractParams(src, bounds, opts, subNuM=nuSrc)
        dParams = self.allocator.extractParams(dst, bounds, opts, subNuM=nuDst)
        expr.nuout = dParams['nuM'] 
        
        block = IBlock()

        block.instructions += self.nublac.T(sParams, dParams, opts)

        for i in block.instructions:
            i.setIterSet(genopts['indices'], genopts['iterset'])  
            
        if context is not None:
            context.blocks += [ block ]
        else:
            icode.blocks += [ block ]
        expr.setComputed(genopts['setComp'])

if __name__ == '__main__':
    pass