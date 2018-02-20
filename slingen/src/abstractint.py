'''
Created on Jan 26, 2014

@author: nkyrt
'''

from sympy import oo, Integer, sympify
from copy import deepcopy

from src.irbase import Inst, Statement, CIRContext, MultiContext, ForLoop
from src.physical import Array

#--------------------------------- Declaration of abstract domain lattices ---------------------------------#
 
class AbstractElement(object):
    def __init__(self, v):
        super(AbstractElement, self).__init__()
        self.v = v
    
    def __eq__(self, other):
        return self.v == other.v
    
    def __repr__(self):
        return '%s(%r)' % (str(type(self)), self.v)

#--------------------------------- Declaration of abstract domain semantics ---------------------------------#
        
class AbstractAnalysis(object):
    def __init__(self):
        super(AbstractAnalysis, self).__init__()
        self.env = {}
        self.BOTTOM = AbstractElement('BOTTOM_ABSTRACT')
        self.TOP = AbstractElement('TOP_ABSTRACT')
    
    def isBottom(self, element):
        return element == self.BOTTOM
    
    def isTop(self, element):
        return element == self.TOP
        
    def applySemantics(self, target):
        ''' Advance the analysis by applying the semantics of the given instructions (target). 
        
        Update the AbstractAnalysis environment according to the semantics of the given instructions.
        Moreover store the current analysis environment as a field of the instructions.
        '''
        if isinstance(target, Inst):
            try:
                getattr(self, target.__class__.__name__)(target)
            except AttributeError:
                # this means that the analysis has not implemented anything for the specific instruction
                # because this instruction does not affect the analysis environment
                target.env = deepcopy(self.env)
        elif isinstance(target, CIRContext):
            preLoopVars = self.env.keys()
            self.applyContextSemantics(target)
            newenv = {var: self.env[var] for var in preLoopVars}
            self.env = newenv
        elif isinstance(target, MultiContext):
            for context in target.contexts:
                self.applySemantics(context)
    
    def applyContextSemantics(self, target):
        ''' Advance the analysis by applying the semantics of the instructions within the given context. '''
        # We assume that all local arrays are aligned
        for var in target.declare:
            if isinstance(var, Array):
                self.env[sympify(var.name)] = self.TOP
        for ib in target.flatList:
            for instr in ib.instructions:
                self.applySemantics(instr)
    
    def clearInstEnv(self, target):
        ''' Reset the analysis status for all instructions in target. '''
        if isinstance(target, Inst):
            target.env = {}
            if isinstance(target, ForLoop):
                target.timesTaken = 0
            elif isinstance(target, Statement):
                for source in target.srcs:
                    self.clearInstEnv(source)
        if isinstance(target, CIRContext):
            for ib in target.flatList:
                for instr in ib.instructions:
                    self.clearInstEnv(instr)
        elif isinstance(target, MultiContext):
            for context in target.contexts:
                self.clearInstEnv(context)
    
    def reset(self):
        ''' Reset the analysis status. '''
        self.env = {}
        
    def propagateEnvToSrcs(self, target):
        ''' Propagate the analysis environment of each of the given instructions to its sources. '''
        if isinstance(target, Statement):
            for source in target.srcs:
                source.env = target.env
                self.propagateEnvToSrcs(source)
        elif isinstance(target, CIRContext):
            for ib in target.flatList:
                for instr in ib.instructions:
                    self.propagateEnvToSrcs(instr)
        elif isinstance(target, MultiContext):
            for context in target.contexts:
                self.propagateEnvToSrcs(context)
                        
    def evaluateExpr(self, expr):
        ''' Evaluate the given (symbolic) expression in the current environment. '''
        if isinstance(expr, int):
            expr = Integer(expr)
        if expr.is_Add:
            return self.abstractAdd([self.evaluateExpr(arg) for arg in expr._args])
        elif expr.is_Mul:
            return self.abstractMul([self.evaluateExpr(arg) for arg in expr._args])
        elif expr.is_Symbol:
            return self.env[expr]
        elif expr.is_Number:
            return self.evaluateConstant(expr)
        else:
            raise Exception('Cannot evaluate expression %s of type %s' % (str(expr), str(type(expr))))
    
    def evaluateConstant(self, constant):
        raise NotImplementedError('Should have implemented this')
    
    def abstractAdd(self, args):
        raise NotImplementedError('Should have implemented this')
    
    def abstractMul(self, args):
        raise NotImplementedError('Should have implemented this')

class IntervalAnalysis(AbstractAnalysis):
    def __init__(self):
        super(IntervalAnalysis, self).__init__()
        self.BOTTOM = AbstractElement('BOTTOM_INTERVAL')
        self.TOP = AbstractElement((-oo, oo))
    
    def lessEqual(self, first, second):
        ''' Return true if first is under second in the Intervals lattice, else return False. '''
        return self.isBottom(first) or self.isTop(second) or \
            first.v[0] >= second.v[0] and first.v[1] <= second.v[1]
        
    def glb(self, first, second):
        ''' Return the greatest lower bound of first and second. '''
        if self.isBottom(first) or self.isBottom(second) or first.v[1] < second.v[0] or second.v[1] < first.v[0]:
            res = self.BOTTOM
        else:
            res = AbstractElement((max(first.v[0], second.v[0]), min(first.v[1], second.v[1])))
        return res
    
    def lub(self, first, second):
        ''' Return the least upper bound of first and second. '''
        if self.isBottom(first):
            res = second
        elif self.isBottom(second):
            res = first
        else:
            res = AbstractElement((min(first.v[0], second.v[0]), max(first.v[1], second.v[1])))
        return res
    
    def widen(self, first, second):
        ''' Return the result of applying widening between first and second (in this order). '''
        if self.isBottom(first):
            return deepcopy(second)
        elif self.isBottom(second):
            return deepcopy(first)
        else:
            low = -oo if second.v[0] < first.v[0] else first.v[0]
            high = oo if second.v[1] > first.v[1] else first.v[1]
            return AbstractElement((low, high))
    
    def evaluateConstant(self, constant):
        ''' Evaluation of a constant value in the abstract domain. '''
        constant = int(constant)
        return AbstractElement((constant, constant))
    
    def abstractAdd(self, args):
        ''' Implementation of the addition operator in the abstract domain. '''
        first = args[0]
        if self.isBottom(first):
            return self.BOTTOM
        lowVal, highVal = first.v
        for arg in args[1:]:
            if self.isBottom(arg):
                return self.BOTTOM
            lowVal += arg.v[0]
            highVal += arg.v[1]
        return AbstractElement((lowVal, highVal))
    
    def abstractMul(self, args):
        ''' Implementation of the multiplication operator in the abstract domain. '''
        first = args[0]
        if self.isBottom(first):
            return self.BOTTOM
        lowVal, highVal = first.v
        for arg in args[1:]:
            if self.isBottom(arg):
                return self.BOTTOM
            l, h = arg.v
            extremeCandidates = [0 if (v[0] == 0 and v[1] * v[1] == oo or v[1] == 0 and v[0] * v[0] == oo) else v[0] * v[1] for v in zip([lowVal, lowVal, highVal, highVal], [l, h, l, h])]
            lowVal = min(extremeCandidates)
            highVal = max(extremeCandidates)
        return AbstractElement((lowVal, highVal))

class ParityAnalysis(AbstractAnalysis):
    def __init__(self, N):
        super(ParityAnalysis, self).__init__()
        self.N = N
        self.BOTTOM = AbstractElement('BOTTOM_PARITY')
        self.TOP = AbstractElement('TOP_PARITY')
     
    def lessEqual(self, first, second):
        ''' Return true if first is under second in the Intervals lattice, else return False. '''
        return self.isBottom(first) or self.isTop(second) or first.v == second.v
        
    def glb(self, first, second):
        ''' Return the greatest lower bound of first and second. '''
        v = self.BOTTOM
        if self.isTop(first):
            v = second
        elif self.isTop(second):
            v = first
        elif first == second:
            v = first
        return v
    
    def lub(self, first, second):
        ''' Return the least upper bound of first and second. '''
        v = self.TOP
        if self.isBottom(first):
            v = second
        elif self.isBottom(second):
            v = first
        elif first == second:
            v = first
        return v
    
    def evaluateConstant(self, constant):
        ''' Evaluation of a constant value in the abstract domain. '''
        constant = int(constant)
        return AbstractElement(constant % self.N)
    
    def abstractAdd(self, args):
        ''' Implementation of the addition operator in the abstract domain. '''
        topValue = self.TOP.v
        first = args[0]
        parity = first.v
        for arg in args[1:]:
            if self.isBottom(arg):
                return self.BOTTOM
            if parity != topValue:
                if self.isTop(arg):
                    parity = topValue
                else:
                    parity += arg.v
        if parity != topValue:
            parity = parity % self.N
        return AbstractElement(parity)
    
    def abstractMul(self, args):
        ''' Implementation of the multiplication operator in the abstract domain. '''
        topValue = self.TOP.v
        first = args[0]
        if self.isBottom(first):
            return self.BOTTOM 
        parity = first.v
        for arg in args[1:]:
            if self.isBottom(arg):
                return self.BOTTOM
            p = arg.v
            if p == 0 or parity == 0:
                parity = 0
            elif p == topValue:
                parity = topValue
            elif parity != topValue: 
                parity *= p
        if parity != topValue:
            parity = parity % self.N
        return AbstractElement(parity)
    
class CongruenceAnalysis(AbstractAnalysis):
    def __init__(self):
        super(CongruenceAnalysis, self).__init__()
        self.BOTTOM = AbstractElement('BOTTOM_CONGRUENCE')
        self.TOP = AbstractElement((1,0))
     
    def lessEqual(self, first, second):
        ''' Return true if first is under second in the Intervals lattice, else return False. '''
        c1, m1 = first.v
        c2, m2 = second.v
        if m2 == 0: 
            return m1 == 0 and c1 == c2
        else:
            return m1 % m2 == 0 and c1 % m2 == c2
        
    def glb(self, first, second):
        ''' Return the greatest lower bound of first and second. '''
        raise NotImplementedError('glb of Congruence domain not implemented yet!')
    
    def lub(self, first, second):
        ''' Return the least upper bound of first and second. '''
        c1, m1 = first.v
        c2, m2 = second.v
        m = gcdm(m1, m2, abs(c1 - c2))
        c = c1
        if m > 0: c = c % m
        return AbstractElement((c, m))
    
    def evaluateConstant(self, constant):
        ''' Evaluation of a constant value in the abstract domain. '''
        constant = int(constant)
        return AbstractElement((constant, 0))
    
    def abstractAdd(self, args):
        ''' Implementation of the addition operator in the abstract domain. '''
        c, m = args[0].v
        for arg in args[1:]:
            c += arg.v[0]
            m = gcd(m, arg.v[1])
        if m > 0: c = c % m
        return AbstractElement((c, m))
    
    def abstractMul(self, args):
        ''' Implementation of the multiplication operator in the abstract domain. '''
        c, m = args[0].v
        for arg in args[1:]:
            argc, argm = arg.v
            m = gcdm(c*argm, m*argc, m*argm)
            c *= argc
        if m > 0: c = c % m
        return AbstractElement((c, m))

class CongruenceModNAnalysis(AbstractAnalysis):
    def __init__(self, N):
        super(CongruenceModNAnalysis, self).__init__()
        self.N = N
        self.BOTTOM = AbstractElement(set())
        self.TOP = AbstractElement(set(range(N)))
     
    def lessEqual(self, first, second):
        ''' Return true if first is under second in the Intervals lattice, else return False. '''
        return first.v <= second.v
        
    def glb(self, first, second):
        ''' Return the greatest lower bound of first and second. '''
        return AbstractElement(first.v & second.v)
    
    def lub(self, first, second):
        ''' Return the least upper bound of first and second. '''
        return AbstractElement(first.v | second.v)
    
    def evaluateConstant(self, constant):
        ''' Evaluation of a constant value in the abstract domain. '''
        constant = int(constant)
        return AbstractElement(set([constant % self.N]))
    
    def abstractAdd(self, args):
        ''' Implementation of the addition operator in the abstract domain. '''
        res = set(args[0].v)
        for arg in args[1:]:
            res = set([(v1 + v2) % self.N for v1 in res for v2 in arg.v])
        return AbstractElement(res)
    
    def abstractMul(self, args):
        ''' Implementation of the multiplication operator in the abstract domain. '''
        res = set(args[0].v)
        for arg in args[1:]:
            res = set([(v1 * v2) % self.N for v1 in res for v2 in arg.v])
        return AbstractElement(res)
    
class IntervalParityReductionAnalysis(AbstractAnalysis):
    WIDENING_THRESHOLD = 5 # should be > 0
    def __init__(self, N):
        super(IntervalParityReductionAnalysis, self).__init__()
        self.N = N
        self.intervalAnalysis = IntervalAnalysis()
        self.parityAnalysis = ParityAnalysis(N)
    
    def applySemantics(self, target):
        ''' Advance the analysis by applying the semantics of the given instructions (target). 
         
        We override the base class applySemantics method in order to speed up the analysis.
        '''
        if isinstance(target, ForLoop):
            self.ForLoop(target)
        elif isinstance(target, MultiContext):
            for context in target.contexts:
                self.applySemantics(context)
        elif isinstance(target, Inst):
            target.env = self.env
        elif isinstance(target, CIRContext):
            self.applyContextSemantics(target)
        else:
            raise Exception('Unknown target for applySemantics: %s' % target.__class__.__name__)    
    
    def applyContextSemantics(self, target):
        ''' Advance the analysis by applying the semantics of the instructions within the given context. '''
        # We assume that all local arrays are aligned
        for var in target.declare:
            if isinstance(var, Array):
                self.env[sympify(var.name)] = (self.intervalAnalysis.TOP, AbstractElement(0))
        for ib in target.flatList:
            for instr in ib.instructions:
                self.applySemantics(instr)
                            
    def ForLoop(self, loop):
        ''' Update env according to the content of the given for-loop. '''
        return self._ForLoop_fast(loop)
    
    def _ForLoop_fast(self, loop):
        ''' Fast(er) implementation of ForLoop, according to which we first calculate the fixpoint for the loop index 
        and then we move the analysis to the contents of the loop (possibly another nested loop). '''
        intervalAnalysis = self.intervalAnalysis
        parityAnalysis = self.parityAnalysis
        
        start = loop.B
        end = loop.E
        step = loop.S
        index = loop.idx
        timesTaken = loop.timesTaken
        
        abstractStart = self.evaluateExpr(start)
        abstractEnd = self.evaluateExpr(end)
        abstractStep = self.evaluateExpr(step)
        minVal = abstractStart[0].v[0]
        valUpperBound = abstractEnd[0].v[1] - 1
        loopInterval = AbstractElement((minVal, valUpperBound))
        
        preLoopVars = self.env.keys()
        wideningApplied = False
        
        while True: # loop until the fixpoint is reached
            timesTaken += 1
            
            # calculate the new abstract value of the loop index
            if timesTaken == 1: # we enter the loop coming from the previous instruction
                indexVal = self.evaluateExpr(start)
            else: # we enter the loop coming from the last instruction of another iteration of the loop
                indexVal = self.abstractAdd([self.env[index], abstractStep])
                if not wideningApplied and timesTaken >= self.WIDENING_THRESHOLD: # apply widening to the interval if we reached the threshold
                    indexVal = (intervalAnalysis.widen(loop.env[index][0], indexVal[0]), indexVal[1])
                    wideningApplied = True
                    
            # apply semantics of implicit assume of for-loop
            indexVal = (intervalAnalysis.glb(indexVal[0], loopInterval), indexVal[1])
            
            # reduce
            indexVal = self.reduce(*indexVal)
            
            # update the environment of the analysis
            if loop.env: # we have gone through the loop before
                self.env[index] = self.reduce(intervalAnalysis.lub(loop.env[index][0], indexVal[0]), parityAnalysis.lub(loop.env[index][1], indexVal[1]))
            else: # this is the first time we go through the loop
                self.env[index] = indexVal
            # check if we have reached a fixpoint
            fixpointReached = equalEnvs(loop.env, self.env)
            if fixpointReached:
                timesTaken = 0
                break
            else:
                loop.env = deepcopy(self.env)
            
        # analyze the instructions within the body of the loop
        self.applyContextSemantics(loop)
        
        # remove the contents of env that were not there before entering the for-loop (i.e. local variables of the loop body)
        newenv = {var: self.env[var] for var in preLoopVars}
        self.env = newenv
            
#     def _ForLoop_slow(self, loop):
#         ''' Rigorous implementation of ForLoop, according to which we move the analysis following the control flow graph. 
#         
#         This implementation is slow because for each iteration of a loop we have to calculate the fixpoint for all its nested loops.
#         Since we don't modify the loop index from within the body of the loop, it is safe to calculate the fixpoint of the outer loop
#         before entering the inner (nested) loop - see ForLoop_fast above.
#         '''
#         intervalAnalysis = self.intervalAnalysis
#         parityAnalysis = self.parityAnalysis
#         
#         start = loop.B
#         end = loop.E
#         step = loop.S
#         index = loop.idx
#         timesTaken = loop.timesTaken
#         
#         abstractStart = self.evaluateExpr(start)
#         abstractEnd = self.evaluateExpr(end)
#         abstractStep = self.evaluateExpr(step)
#         minVal = abstractStart[0].v[0]
#         valUpperBound = abstractEnd[0].v[1] - 1
#         loopInterval = AbstractElement((minVal, valUpperBound))
#         
#         preLoopVars = self.env.keys()
#         wideningApplied = False
#         
#         while True: # loop until the fixpoint is reached
#             timesTaken += 1
#             
#             # calculate the new abstract value of the loop index
#             if timesTaken == 1: # we enter the loop coming from the previous instruction
#                 indexVal = self.evaluateExpr(start)
#             else: # we enter the loop coming from the last instruction of another iteration of the loop
#                 indexVal = self.abstractAdd([self.env[index], abstractStep])
#                 if not wideningApplied and timesTaken >= self.WIDENING_THRESHOLD: # apply widening to the interval if we reached the threshold
#                     indexVal = (intervalAnalysis.widen(loop.env[index][0], indexVal[0]), indexVal[1])
#                     wideningApplied = True
#                     
#             # apply semantics of implicit assume of for-loop
#             indexVal = (intervalAnalysis.glb(indexVal[0], loopInterval), indexVal[1])
#             
#             # reduce
#             indexVal = self.reduce(*indexVal)
#             
#             # update the environment of the analysis
#             if loop.env: # we have gone through the loop before
#                 self.env[index] = self.reduce(intervalAnalysis.lub(loop.env[index][0], indexVal[0]), parityAnalysis.lub(loop.env[index][1], indexVal[1]))
#             else: # this is the first time we go through the loop
#                 self.env[index] = indexVal
#             
#             # check if we have reached a fixpoint
#             fixpointReached = equalEnvs(loop.env, self.env)
#             if fixpointReached:
#                 timesTaken = 0
#                 break
#             else:
#                 loop.env = deepcopy(self.env)
#             
#             # analyze the instructions within the body of the loop
#             self.applyContextSemantics(loop)
#         
#         # remove the contents of env that were not there before entering the for-loop (i.e. local variables of the loop body)
#         newenv = {var: self.env[var] for var in preLoopVars}
#         self.env = newenv
    
#     def _ForLoop_old(self, loop):
#         ''' Update env according to the content of the given for-loop. '''
#         start = loop.B
#         end = loop.E
#         step = loop.S
#         
#         abstractStart = self.evaluateExpr(start)
#         abstractEnd = self.evaluateExpr(end)
#         abstractStep = self.evaluateExpr(step)
#         if any(val.isBottom() for val in [abstractStart[0], abstractStart[1], abstractEnd[0], abstractEnd[1], abstractStep[0], abstractStep[1]]) \
#                 or abstractEnd[0].v[1] - 1 < abstractStart[0].v[0]:
#             # this practically means unreachable code
#             intervalVal = IntervalElement.getBottom()
#             parityVal = ParityElement.getBottom()
#         else:
#             minVal = abstractStart[0].v[0]
#             valUpperBound = abstractEnd[0].v[1] - 1
#             
#             intervalVal1 = IntervalElement('dummy')
#             intervalVal2 = IntervalElement.getBottom() # so that it won't affect the first lub computation inside the loop
#             parityVal1 = ParityElement('dummy')
#             parityVal2 = ParityElement.getBottom()
#             i = 0
#             loopInterval = IntervalElement((minVal, valUpperBound))
#             wideningApplied = False
#             # calculate the fixpoint
#             while not (intervalVal2 == intervalVal1 and parityVal1 == parityVal2) and self.evaluateExpr(end - (start + i * step))[0].v != IntervalElement.BOTTOM:
#                 if i > self.WIDENING_THRESHOLD and not wideningApplied:
# #                     print 'Applying widening for loop %s' % loop.unparse()
#                     newVal = (intervalVal1.widen(intervalVal2), self.evaluateExpr(start + i * step)[1])
#                     wideningApplied = True
#                 else:
#                     newVal = self.evaluateExpr(start + i * step)
#                 # semantics of implicit assume statement that corresponds to the for-loop
#                 newVal = self.reduce(newVal[0].glb(loopInterval), newVal[1])
#                 if intervalVal1 != intervalVal2:
#                     intervalVal1 = intervalVal2
#                     intervalVal2 = newVal[0].lub(intervalVal2)
#                 if parityVal1 != parityVal2:
#                     parityVal1 = parityVal2 
#                     parityVal2 = newVal[1].lub(parityVal2)
#                 intervalVal2, parityVal2 = self.reduce(intervalVal2, parityVal2)
#                 i += 1
#             intervalVal = intervalVal2
#             parityVal= parityVal2
#             
#         self.env[loop.idx] = (intervalVal, parityVal)    
    
    def evaluateExpr(self, expr):
        return self.reduce(*AbstractAnalysis.evaluateExpr(self, expr))
    
    def abstractAdd(self, args):
        ''' Implementation of the addition operator in the abstract domain. '''
        return self.reduce(self.intervalAnalysis.abstractAdd([arg[0] for arg in args]), self.parityAnalysis.abstractAdd([arg[1] for arg in args]))
    
    def abstractMul(self, args):
        ''' Implementation of the multiplication operator in the abstract domain. '''
        return self.reduce(self.intervalAnalysis.abstractMul([arg[0] for arg in args]), self.parityAnalysis.abstractMul([arg[1] for arg in args]))
    
    def evaluateConstant(self, constant):
        ''' Evaluation of a constant value in the abstract domain. '''
        return self.intervalAnalysis.evaluateConstant(constant), self.parityAnalysis.evaluateConstant(constant)
    
    def reduce(self, intervalVal, parityVal):
        ''' If possible, return a more precise (Interval, Parity) element 
        by combining information from the two abstract domains. 
        ''' 
        intervalAnalysis = self.intervalAnalysis
        parityAnalysis = self.parityAnalysis
        if intervalAnalysis.isBottom(intervalVal) or intervalVal.v[0] == oo or intervalVal.v[1] == -oo \
        or parityAnalysis.isBottom(parityVal):
            return intervalAnalysis.BOTTOM, parityAnalysis.BOTTOM
        intervalLow = intervalVal.v[0]
        intervalHigh = intervalVal.v[1]
        intervalLength = intervalHigh - intervalLow + 1
        if intervalLength <= 0:
            return intervalAnalysis.BOTTOM, parityAnalysis.BOTTOM
        if not parityAnalysis.isTop(parityVal):
            parity = parityVal.v
            if intervalLow != -oo and intervalLow % self.N != parity:
                intervalLowParity = intervalLow % self.N
                if parity < intervalLowParity: parity += self.N
                intervalLowNew = intervalLow + parity - intervalLowParity
                return self.reduce(AbstractElement((intervalLowNew, intervalHigh)), parityVal)
            elif intervalHigh != oo and intervalHigh % self.N != parity:
                intervalHighParity = intervalHigh % self.N
                if parity > intervalHighParity: 
                    delta = self.N - parity + intervalHighParity 
                else:
                    delta = intervalHighParity - parity
                intervalHighNew = intervalHigh - delta
                return self.reduce(AbstractElement((intervalLow, intervalHighNew)), parityVal)
        if not intervalAnalysis.isTop(intervalVal) and not parityAnalysis.isTop(parityVal) and intervalLength < self.N:
            # the interval can be reduced to only one value
            intervalLowParity = intervalLow % self.N
            intervalHighParity = intervalHigh % self.N
            parity = parityVal.v
            if intervalHighParity < intervalLowParity: intervalHighParity += self.N
            if parity < intervalLowParity: parity += self.N
            if parity < intervalLowParity or parity > intervalHighParity:
                return intervalAnalysis.getBottom(), parityAnalysis.getBottom()
            else:
                v = intervalLow + parity - intervalLowParity
                return AbstractElement((v, v)), parityVal
        if intervalLength == 1 and parityAnalysis.isTop(parityVal):
            newParity = intervalLow % self.N
            return intervalVal, AbstractElement(newParity)
        return intervalVal, parityVal

class IntervalCongruenceReductionAnalysis(AbstractAnalysis):
    WIDENING_THRESHOLD = 5 # should be > 0
    def __init__(self):
        super(IntervalCongruenceReductionAnalysis, self).__init__()
        self.intervalAnalysis = IntervalAnalysis()
        self.congruenceAnalysis = CongruenceAnalysis()
    
    def applySemantics(self, target):
        ''' Advance the analysis by applying the semantics of the given instructions (target). 
         
        We override the base class applySemantics method in order to speed up the analysis.
        '''
        if isinstance(target, ForLoop):
            self.ForLoop(target)
        elif isinstance(target, MultiContext):
            for context in target.contexts:
                self.applySemantics(context)
        elif isinstance(target, Inst):
            target.env = self.env
        elif isinstance(target, CIRContext):
            self.applyContextSemantics(target)
        else:
            raise Exception('Unknown target for applySemantics: %s' % target.__class__.__name__)    
    
    def applyContextSemantics(self, target):
        ''' Advance the analysis by applying the semantics of the instructions within the given context. '''
        # We assume that all local arrays are aligned
        for var in target.declare:
            if isinstance(var, Array):
                self.env[sympify(var.name)] = (self.intervalAnalysis.TOP, AbstractElement((0,1)))
        for ib in target.flatList:
            for instr in ib.instructions:
                self.applySemantics(instr)
                            
    def ForLoop(self, loop):
        ''' Update env according to the content of the given for-loop. '''
        return self._ForLoop_fast(loop)
    
    def _ForLoop_fast(self, loop):
        ''' Fast(er) implementation of ForLoop, according to which we first calculate the fixpoint for the loop index 
        and then we move the analysis to the contents of the loop (possibly another nested loop). '''
        intervalAnalysis = self.intervalAnalysis
        congruenceAnalysis = self.congruenceAnalysis
        
        start = loop.B
        end = loop.E
        step = loop.S
        index = loop.idx
        timesTaken = loop.timesTaken
        
        abstractStart = self.evaluateExpr(start)
        abstractEnd = self.evaluateExpr(end)
        abstractStep = self.evaluateExpr(step)
        minVal = abstractStart[0].v[0]
        valUpperBound = abstractEnd[0].v[1] - 1
        loopInterval = AbstractElement((minVal, valUpperBound))
        
        preLoopVars = self.env.keys()
        wideningApplied = False
        
        while True: # loop until the fixpoint is reached
            timesTaken += 1
            
            # calculate the new abstract value of the loop index
            if timesTaken == 1: # we enter the loop coming from the previous instruction
                indexVal = self.evaluateExpr(start)
            else: # we enter the loop coming from the last instruction of another iteration of the loop
                indexVal = self.abstractAdd([self.env[index], abstractStep])
                if not wideningApplied and timesTaken >= self.WIDENING_THRESHOLD: # apply widening to the interval if we reached the threshold
                    indexVal = (intervalAnalysis.widen(loop.env[index][0], indexVal[0]), indexVal[1])
                    wideningApplied = True
                    
            # apply semantics of implicit assume of for-loop
            indexVal = (intervalAnalysis.glb(indexVal[0], loopInterval), indexVal[1])
            
            # reduce
            indexVal = self.reduce(*indexVal)
            
            # update the environment of the analysis
            if loop.env: # we have gone through the loop before
                self.env[index] = self.reduce(intervalAnalysis.lub(loop.env[index][0], indexVal[0]), congruenceAnalysis.lub(loop.env[index][1], indexVal[1]))
            else: # this is the first time we go through the loop
                self.env[index] = indexVal
            # check if we have reached a fixpoint
            fixpointReached = equalEnvs(loop.env, self.env)
            if fixpointReached:
                timesTaken = 0
                break
            else:
                loop.env = deepcopy(self.env)
            
        # analyze the instructions within the body of the loop
        self.applyContextSemantics(loop)
        
        # remove the contents of env that were not there before entering the for-loop (i.e. local variables of the loop body)
        newenv = {var: self.env[var] for var in preLoopVars}
        self.env = newenv
            
    def evaluateExpr(self, expr):
        return self.reduce(*AbstractAnalysis.evaluateExpr(self, expr))
    
    def abstractAdd(self, args):
        ''' Implementation of the addition operator in the abstract domain. '''
        return self.reduce(self.intervalAnalysis.abstractAdd([arg[0] for arg in args]), self.congruenceAnalysis.abstractAdd([arg[1] for arg in args]))
    
    def abstractMul(self, args):
        ''' Implementation of the multiplication operator in the abstract domain. '''
        return self.reduce(self.intervalAnalysis.abstractMul([arg[0] for arg in args]), self.congruenceAnalysis.abstractMul([arg[1] for arg in args]))
    
    def evaluateConstant(self, constant):
        ''' Evaluation of a constant value in the abstract domain. '''
        return self.intervalAnalysis.evaluateConstant(constant), self.congruenceAnalysis.evaluateConstant(constant)
    
    def reduce(self, intervalVal, congruenceVal):
        ''' If possible, return a more precise (Interval, Congruence) element 
        by combining information from the two abstract domains. 
        ''' 
        intervalAnalysis = self.intervalAnalysis
        congruenceAnalysis = self.congruenceAnalysis
        if intervalAnalysis.isBottom(intervalVal) or intervalVal.v[0] == oo or intervalVal.v[1] == -oo \
        or congruenceAnalysis.isBottom(congruenceVal):
            return intervalAnalysis.BOTTOM, congruenceAnalysis.BOTTOM
        intervalLow = intervalVal.v[0]
        intervalHigh = intervalVal.v[1]
        c, m = congruenceVal.v
        if m == 0:
            if c >= intervalLow and c <= intervalHigh:
                return AbstractElement((c,c)), congruenceVal
            else:
                return intervalAnalysis.BOTTOM, congruenceAnalysis.BOTTOM
        
        if intervalLow != -oo and intervalHigh != oo:
            r = self.R(congruenceVal, intervalLow)
            l = self.L(congruenceVal, intervalHigh)
            if r > l:
                return intervalAnalysis.BOTTOM, congruenceAnalysis.BOTTOM
            if r == l:
                return AbstractElement((r, r)), AbstractElement((r, 0))
            return AbstractElement((r, l)), congruenceVal
        else:
            if intervalLow != -oo:
                r = self.R(congruenceVal, intervalLow)
                return AbstractElement((r, intervalHigh)), congruenceVal
            elif intervalHigh != oo:
                l = self.L(congruenceVal, intervalHigh)
                return AbstractElement((intervalLow, l)), congruenceVal
            else:
                return intervalVal, congruenceVal

    def R(self, congruenceVal, a):
        p, m = congruenceVal.v
        return a + (p-a) % m
        
    def L(self, congruenceVal, a):
        p, m = congruenceVal.v
        return a - (a-p) % m
        
class IntervalCongruenceModNReductionAnalysis(AbstractAnalysis):
    WIDENING_THRESHOLD = 5 # should be > 0
    def __init__(self, N):
        super(IntervalCongruenceModNReductionAnalysis, self).__init__()
        self.N = N
        self.intervalAnalysis = IntervalAnalysis()
        self.congruenceAnalysis = CongruenceModNAnalysis(N)
    
    def applySemantics(self, target):
        ''' Advance the analysis by applying the semantics of the given instructions (target). 
         
        We override the base class applySemantics method in order to speed up the analysis.
        '''
        if isinstance(target, ForLoop):
            self.ForLoop(target)
        elif isinstance(target, MultiContext):
            for context in target.contexts:
                self.applySemantics(context)
        elif isinstance(target, Inst):
            target.env = self.env
        elif isinstance(target, CIRContext):
            self.applyContextSemantics(target)
        else:
            raise Exception('Unknown target for applySemantics: %s' % target.__class__.__name__)    
    
    def applyContextSemantics(self, target):
        ''' Advance the analysis by applying the semantics of the instructions within the given context. '''
        # We assume that all local arrays are aligned
        for var in target.declare:
            if isinstance(var, Array):
                self.env[sympify(var.name)] = (self.intervalAnalysis.TOP, AbstractElement(set([0])))
        for ib in target.flatList:
            for instr in ib.instructions:
                self.applySemantics(instr)
                            
    def ForLoop(self, loop):
        ''' Update env according to the content of the given for-loop. '''
        return self._ForLoop_fast(loop)
    
    def _ForLoop_fast(self, loop):
        ''' Fast(er) implementation of ForLoop, according to which we first calculate the fixpoint for the loop index 
        and then we move the analysis to the contents of the loop (possibly another nested loop). '''
        intervalAnalysis = self.intervalAnalysis
        congruenceAnalysis = self.congruenceAnalysis
        
        start = loop.B
        end = loop.E
        step = loop.S
        index = loop.idx
        timesTaken = loop.timesTaken
        
        abstractStart = self.evaluateExpr(start)
        abstractEnd = self.evaluateExpr(end)
        abstractStep = self.evaluateExpr(step)
        minVal = abstractStart[0].v[0]
        valUpperBound = abstractEnd[0].v[1] - 1
        loopInterval = AbstractElement((minVal, valUpperBound))
        
        preLoopVars = self.env.keys()
        wideningApplied = False
        
        while True: # loop until the fixpoint is reached
            timesTaken += 1
            
            # calculate the new abstract value of the loop index
            if timesTaken == 1: # we enter the loop coming from the previous instruction
                indexVal = self.evaluateExpr(start)
            else: # we enter the loop coming from the last instruction of another iteration of the loop
                indexVal = self.abstractAdd([self.env[index], abstractStep])
                if not wideningApplied and timesTaken >= self.WIDENING_THRESHOLD: # apply widening to the interval if we reached the threshold
                    indexVal = (intervalAnalysis.widen(loop.env[index][0], indexVal[0]), indexVal[1])
                    wideningApplied = True
                    
            # apply semantics of implicit assume of for-loop
            indexVal = (intervalAnalysis.glb(indexVal[0], loopInterval), indexVal[1])
            
            # reduce
            indexVal = self.reduce(*indexVal)
            
            # update the environment of the analysis
            if loop.env: # we have gone through the loop before
                self.env[index] = self.reduce(intervalAnalysis.lub(loop.env[index][0], indexVal[0]), congruenceAnalysis.lub(loop.env[index][1], indexVal[1]))
            else: # this is the first time we go through the loop
                self.env[index] = indexVal
            # check if we have reached a fixpoint
            fixpointReached = equalEnvs(loop.env, self.env)
            if fixpointReached:
                timesTaken = 0
                break
            else:
                loop.env = deepcopy(self.env)
            
        # analyze the instructions within the body of the loop
        self.applyContextSemantics(loop)
        
        # remove the contents of env that were not there before entering the for-loop (i.e. local variables of the loop body)
        newenv = {var: self.env[var] for var in preLoopVars}
        self.env = newenv
            
    def evaluateExpr(self, expr):
        return self.reduce(*AbstractAnalysis.evaluateExpr(self, expr))
    
    def abstractAdd(self, args):
        ''' Implementation of the addition operator in the abstract domain. '''
        return self.reduce(self.intervalAnalysis.abstractAdd([arg[0] for arg in args]), self.congruenceAnalysis.abstractAdd([arg[1] for arg in args]))
    
    def abstractMul(self, args):
        ''' Implementation of the multiplication operator in the abstract domain. '''
        return self.reduce(self.intervalAnalysis.abstractMul([arg[0] for arg in args]), self.congruenceAnalysis.abstractMul([arg[1] for arg in args]))
    
    def evaluateConstant(self, constant):
        ''' Evaluation of a constant value in the abstract domain. '''
        return self.intervalAnalysis.evaluateConstant(constant), self.congruenceAnalysis.evaluateConstant(constant)
    
    def reduce(self, intervalVal, congruenceVal):
        ''' If possible, return a more precise (Interval, Congruence) element 
        by combining information from the two abstract domains. 
        ''' 
        intervalAnalysis = self.intervalAnalysis
        congruenceAnalysis = self.congruenceAnalysis
        if intervalAnalysis.isBottom(intervalVal) or intervalVal.v[0] == oo or intervalVal.v[1] == -oo \
        or congruenceAnalysis.isBottom(congruenceVal):
            return intervalAnalysis.BOTTOM, congruenceAnalysis.BOTTOM
        intervalLow = intervalVal.v[0]
        intervalHigh = intervalVal.v[1]
        intervalLength = intervalHigh - intervalLow + 1
        if intervalLength <= 0:
            return intervalAnalysis.BOTTOM, congruenceAnalysis.BOTTOM
        congruence = congruenceVal.v
        if intervalLow != -oo and intervalLow % self.N not in congruence:
            intervalLowNew = intervalLow + 1
            return self.reduce(AbstractElement((intervalLowNew, intervalHigh)), congruenceVal)
        elif intervalHigh != oo and intervalHigh % self.N not in congruence:
            intervalHighNew = intervalHigh - 1
            return self.reduce(AbstractElement((intervalLow, intervalHighNew)), congruenceVal)
        if intervalLength == 1:
            parity = intervalLow % self.N
            if parity not in congruence:
                return intervalAnalysis.BOTTOM, congruenceAnalysis.BOTTOM
            if len(congruence) > 1:
                return intervalVal, AbstractElement(set([parity])) 
        return intervalVal, congruenceVal
    
def equalEnvs(env1, env2):
    ''' Check if the two environments are the same (useful when we want to check if we have reached a fixpoint). '''
#     return cmp(env1, env2) == 0
    return (env1 == env2)

def gcd(a, b):
    """Return greatest common divisor using Euclid's Algorithm."""
    while b:      
        a, b = b, a % b
    return a

def gcdm(*args):
    """Return gcd of args."""
    return reduce(gcd, args)
    
def lcm(a, b):
    """Return lowest common multiple."""
    return a * b // gcd(a, b)

def lcmm(*args):
    """Return lcm of args."""   
    return reduce(lcm, args)

def abs(n):
    ''' Return the absolute value of n. '''
    if n < 0: n = -n
    return n
