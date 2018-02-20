'''
Created on Jan 23, 2015

@author: danieles
'''

from src.dsls.ll import Operator, ParamMat, Add, G, S, Sacc, T, Iv, Kro, fI, Assign, Neg
from src.dsls.sigmall import Sum, NewSum
from src.dsls.processing import resetDependencies, computeDependencies, computeIndependentSubexpr, computeDependentSubexprOfType, createSubsDict

from src.rules.base import Rule, RuleSet
from src.rules.llrules import HFuseGathers

#-------------- Rules ----------------

class HRemoveTransChain(Rule):
    def __init__(self):
        super(HRemoveTransChain, self).__init__()

    def applicable(self, holo):
        return isinstance(holo.succ[0].node, T)
 
    def genChoices(self, holo):
        return [ [] ]
     
    def apply(self, holo, choice):
        retHolo = holo.succ[0].succ[0]
        if len(holo.pred) > 0:
            del retHolo.pred[:] 
            for predTuple in holo.pred:
                predTuple[0].succ[predTuple[1]] = retHolo
                retHolo.pred.append((predTuple[0], predTuple[1]))

        del holo.pred[:]
        del holo.succ[0].succ[:]
         
        return retHolo

class HRemoveNegChain(Rule):
    def __init__(self):
        super(HRemoveNegChain, self).__init__()

    def applicable(self, holo):
        return isinstance(holo.succ[0].node, Neg)
 
    def genChoices(self, holo):
        return [ [] ]
     
    def apply(self, holo, choice):
        retHolo = holo.succ[0].succ[0]
        if len(holo.pred) > 0:
            del retHolo.pred[:] 
            for predTuple in holo.pred:
                predTuple[0].succ[predTuple[1]] = retHolo
                retHolo.pred.append((predTuple[0], predTuple[1]))

        del holo.pred[:]
        del holo.succ[0].succ[:]
         
        return retHolo

class HPushTransDown(Rule):
    def __init__(self):
        super(HPushTransDown, self).__init__()

    def applicable(self, holo):
        return len(holo.pred) == 1 and isinstance(holo.pred[0][0].node, T)
 
    def genChoices(self, holo):
        return [ [] ]
 
    def mask(self, node):
        return [True, False]
     
    def apply(self, holo, choice):

        h0 = holo.succ[0]
        h1 = holo.succ[1]
        
        t0, t1 = T(h0), T(h1)
        newExpr = holo.node.__class__(t0, t1)
        newHolo = newExpr.getHolograph()
        
        newHolo.succ[0].succ.append(h0)
        newHolo.succ[1].succ.append(h1)
        h0.pred.remove((holo,0))
        h1.pred.remove((holo,1))
        h0.pred.append((newHolo.succ[0],0))
        h1.pred.append((newHolo.succ[1],0))
        
        newHolo.pred = holo.pred[0][0].pred
        
        for predTuple in holo.pred[0][0].pred:
            pred = predTuple[0]
            pos  = predTuple[1]
            pred.succ[pos] = newHolo 
        
        return newHolo

class HFuseScatters(Rule):
    def __init__(self):
        super(HFuseScatters, self).__init__()

    def applicable(self, holo):
        return isinstance(holo.succ[0].node, S) and holo.node.__class__ == holo.succ[0].node.__class__ 
 
    def genChoices(self, holo):
        return [ [] ]
     
    def apply(self, holo, choice):
        
        hsuccS = holo.succ[0]
        succS = hsuccS.node
        
        fL = holo.node.fL.compose(succS.fL)
        fR = holo.node.fR.compose(succS.fR)
        newHolo = holo.node.__class__(fL, hsuccS.succ[0], fR).getHolograph()
        
        newHolo.succ.append(hsuccS.succ[0])
        hsuccS.succ[0].pred.remove((hsuccS,0))
        hsuccS.succ[0].pred.append((newHolo,0))
        
        if len(holo.pred) > 0:
            del newHolo.pred[:] 
            for predTuple in holo.pred:
                predTuple[0].succ[predTuple[1]] = newHolo
                newHolo.pred.append((predTuple[0], predTuple[1]))

        del holo.pred[:]
        del hsuccS.succ[:]
         
        return newHolo

class HNegScatterAcc(Rule):
    def __init__(self):
        super(HNegScatterAcc, self).__init__()

    def applicable(self, holo):
        return isinstance(holo.succ[0].node, Neg) and isinstance(holo.node, Sacc) 
 
    def genChoices(self, holo):
        return [ [] ]
     
    def apply(self, holo, choice):
        
        hsuccS = holo.succ[0]
        
        newHolo = holo.node.__class__(holo.node.fL, hsuccS.succ[0], holo.node.fR).getHolograph()
        newHolo.node.neg = True
        
        newHolo.succ.append(hsuccS.succ[0])
        hsuccS.succ[0].pred.remove((hsuccS,0))
        hsuccS.succ[0].pred.append((newHolo,0))
        
        if len(holo.pred) > 0:
            del newHolo.pred[:] 
            for predTuple in holo.pred:
                predTuple[0].succ[predTuple[1]] = newHolo
                newHolo.pred.append((predTuple[0], predTuple[1]))

        del holo.pred[:]
        del hsuccS.succ[:]
         
        return newHolo

class HUnrollSum(Rule):
    def __init__(self, opts):
        super(HUnrollSum, self).__init__()
        self.opts = opts

    def applicable(self, holo):
        L = holo.node.ub-holo.node.lb+1
        if L.is_Number and holo.node.s.is_Number:
            if self.opts['unroll'][str(holo.node.idx)] == 1:
                return True
        return False 
 
    def genChoices(self, holo):
        return [ [] ]
     
    def apply(self, holo, choice):
        L = holo.node.ub-holo.node.lb+1
        unrolledExpr = [ ]
        for i in range(0, L, holo.node.s):
            e = holo.node.inexpr[0].duplicate(changeOut=True)
            e.subs({holo.node.idx: holo.node.lb+i})
            unrolledExpr.append(e)
        
        while(len(unrolledExpr) > 1):
            r = unrolledExpr.pop()
            l = unrolledExpr.pop()
            unrolledExpr.append(l+r)

        newExpr = unrolledExpr[0]
        newHolo = newExpr.getHolograph()
        
        if len(holo.pred) > 0:
            del newHolo.pred[:] 
            for predTuple in holo.pred:
                predTuple[0].succ[predTuple[1]] = newHolo
                newHolo.pred.append((predTuple[0], predTuple[1]))

        del holo.pred[:]
         
        return newHolo

class HDistributeSum(Rule):
    def __init__(self, opts):
        super(HDistributeSum, self).__init__()
        self.opts = opts

    def applicable(self, holo):
        return 'dist' in self.opts['idxProperties'][str(holo.node.idx)] and isinstance(holo.succ[0].node, Add)
 
    def genChoices(self, holo):
        return [ [] ]
     
    def apply(self, holo, choice):
        
        oldsum = holo.node
        h0, h1 = holo.succ[0].succ[0], holo.succ[0].succ[1]
        s0 = NewSum(h0, oldsum.idx, oldsum.lb, oldsum.ub, oldsum.s, oldsum.uFactor)
        s1 = NewSum(h1, oldsum.idx, oldsum.lb, oldsum.ub, oldsum.s, oldsum.uFactor)
        newHolo = (s0+s1).getHolograph()

        newHolo.succ[0].succ.append(h0)
        newHolo.succ[1].succ.append(h1)
        h0.pred.remove((holo.succ[0],0))
        h1.pred.remove((holo.succ[0],1))
        h0.pred.append((newHolo.succ[0],0))
        h1.pred.append((newHolo.succ[1],0))
        
        if len(holo.pred) > 0:
            del newHolo.pred[:] 
            for predTuple in holo.pred:
                predTuple[0].succ[predTuple[1]] = newHolo
                newHolo.pred.append((predTuple[0], predTuple[1]))

        del holo.pred[:]
         
        return newHolo

class HDistributeIv(Rule):
    def __init__(self):
        super(HDistributeIv, self).__init__()

    def applicable(self, holo):
        return isinstance(holo.succ[0].node, Add)
 
    def genChoices(self, holo):
        return [ [] ]
     
    def apply(self, holo, choice):
        
        oldIv = holo.node
        h0, h1 = holo.succ[0].succ[0], holo.succ[0].succ[1]
        iv0 = Iv(h0, oldIv.cond)
        iv1 = Iv(h1, oldIv.cond)
        newHolo = (iv0+iv1).getHolograph()

        newHolo.succ[0].succ.append(h0)
        newHolo.succ[1].succ.append(h1)
        h0.pred.remove((holo.succ[0],0))
        h1.pred.remove((holo.succ[0],1))
        h0.pred.append((newHolo.succ[0],0))
        h1.pred.append((newHolo.succ[1],0))
        
        if len(holo.pred) > 0:
            del newHolo.pred[:] 
            for predTuple in holo.pred:
                predTuple[0].succ[predTuple[1]] = newHolo
                newHolo.pred.append((predTuple[0], predTuple[1]))

        del holo.pred[:]
         
        return newHolo

class HFactorSalphaOutOfSum(Rule):
    def __init__(self):
        super(HFactorSalphaOutOfSum, self).__init__()

    def applicable(self, holo):
        return len(holo.pred) == 1 and isinstance(holo.pred[0][0].node, NewSum) \
            and not holo.node.dependsOn(holo.pred[0][0].node.idx) and isinstance(holo.succ[0].node, Kro)   
 
    def genChoices(self, holo):
        return [ [] ]
     
    def apply(self, holo, choice):
        
        oldSum = holo.pred[0][0].node
        alpha = holo.succ[0].succ[0].node 
        h0 = holo.succ[0].succ[1]
        if isinstance(holo.node, Sacc):
            fL, fR = fI(holo.succ[0].node.getOut().size[0]), fI(holo.succ[0].node.getOut().size[1])
            inSacc = Sacc(fL, h0, fR)
            newSum = NewSum(inSacc, oldSum.idx, oldSum.lb, oldSum.ub, oldSum.s, oldSum.uFactor)
            newSum.init = True
        else:
            newSum = NewSum(h0, oldSum.idx, oldSum.lb, oldSum.ub, oldSum.s, oldSum.uFactor)
        kro = alpha*newSum
        newHolo = holo.node.__class__(holo.node.fL, kro, holo.node.fR).getHolograph()

        h0.pred.remove((holo.succ[0],1))
        if isinstance(holo.node, Sacc):
            newHolo.succ[0].succ[1].succ[0].succ.append(h0)
            h0.pred.append((newHolo.succ[0].succ[1].succ[0],0))
        else:
            newHolo.succ[0].succ[1].succ.append(h0)
            h0.pred.append((newHolo.succ[0].succ[1],0))
            
        if len(holo.pred[0][0].pred) > 0:
            del newHolo.pred[:] 
            for predTuple in holo.pred[0][0].pred:
                predTuple[0].succ[predTuple[1]] = newHolo
                newHolo.pred.append((predTuple[0], predTuple[1]))

        del holo.pred[0][0].pred[:]
        del holo.pred[:]
         
        return newHolo

class HFactorSOutOfIv(Rule):
    def __init__(self):
        super(HFactorSOutOfIv, self).__init__()

    def applicable(self, holo):
        return len(holo.pred) == 1 and isinstance(holo.pred[0][0].node, Iv) \
            and not any( map(lambda s: holo.node.dependsOn(s), holo.pred[0][0].node.cond.getSymAtoms()) )   
 
    def genChoices(self, holo):
        return [ [] ]
     
    def apply(self, holo, choice):
        
        oldIv = holo.pred[0][0].node
        h0 = holo.succ[0]
        newIv = Iv(h0, oldIv.cond)
        newIv.init = True
        newHolo = holo.node.__class__(holo.node.fL, newIv, holo.node.fR).getHolograph()

        h0.pred.remove((holo,0))
        newHolo.succ[0].succ.append(h0)
        h0.pred.append((newHolo.succ[0],0))
            
        if len(holo.pred[0][0].pred) > 0:
            del newHolo.pred[:] 
            for predTuple in holo.pred[0][0].pred:
                predTuple[0].succ[predTuple[1]] = newHolo
                newHolo.pred.append((predTuple[0], predTuple[1]))

        del holo.pred[0][0].pred[:]
        del holo.pred[:]
         
        return newHolo

class HFactorLeftAlphaOutOfIv(Rule):
    def __init__(self):
        super(HFactorLeftAlphaOutOfIv, self).__init__()

    def applicable(self, holo):
        return len(holo.pred) == 1 and isinstance(holo.pred[0][0].node, Iv) \
            and holo.succ[0].node.getOut().isScalar() \
            and not any( map(lambda s: holo.succ[0].node.dependsOn(s), holo.pred[0][0].node.cond.getSymAtoms()) )
 
    def genChoices(self, holo):
        return [ [] ]
     
    def apply(self, holo, choice):
        
        oldIv = holo.pred[0][0].node
        h1 = holo.succ[1]
        newIv = Iv(h1, oldIv.cond)
        newIv.init = oldIv.init
        newIvh = newIv.getHolograph()
        alpha = holo.succ[0]
        newHolo = Kro(alpha, newIvh).getHolograph()

        h1.pred.remove((holo,1))
        alpha.pred.remove((holo,0))
        newIvh.succ.append(h1)
        h1.pred.append((newIvh,0))
        newHolo.succ.extend([alpha, newIvh])
        alpha.pred.append((newHolo,0))
        newIvh.pred.append((newHolo,1))
            
        if len(holo.pred[0][0].pred) > 0:
            del newHolo.pred[:] 
            for predTuple in holo.pred[0][0].pred:
                predTuple[0].succ[predTuple[1]] = newHolo
                newHolo.pred.append((predTuple[0], predTuple[1]))

        del holo.pred[0][0].pred[:]
        del holo.pred[:]
         
        return newHolo

class HFactorIvOutOfSum(Rule):
    def __init__(self):
        super(HFactorIvOutOfSum, self).__init__()

    def applicable(self, holo):
        return len(holo.pred) == 1 and isinstance(holo.pred[0][0].node, NewSum) \
            and not holo.node.dependsOn(holo.pred[0][0].node.idx)   
 
    def genChoices(self, holo):
        return [ [] ]
     
    def apply(self, holo, choice):
        
        oldSum = holo.pred[0][0].node
        h0 = holo.succ[0]
        newSum = NewSum(h0, oldSum.idx, oldSum.lb, oldSum.ub, oldSum.s, oldSum.uFactor)
        newSum.init = oldSum.init
        newHolo = Iv(newSum, holo.node.cond).getHolograph()

        h0.pred.remove((holo,0))
        newHolo.succ[0].succ.append(h0)
        h0.pred.append((newHolo.succ[0],0))
            
        if len(holo.pred[0][0].pred) > 0:
            del newHolo.pred[:] 
            for predTuple in holo.pred[0][0].pred:
                predTuple[0].succ[predTuple[1]] = newHolo
                newHolo.pred.append((predTuple[0], predTuple[1]))

        del holo.pred[0][0].pred[:]
        del holo.pred[:]
         
        return newHolo

# class HFactorSalphaOutOfAdds(Rule):
#     def __init__(self):
#         super(HFactorSalphaOutOfAdds, self).__init__()
#         self.groupby = []
# 
#     def mask(self):
#         return [True, False]
# 
#     def applicable(self, holo):
#         l = holo.getLeavesWithDiffType()
#         n = len(l)
#         sas = filter(lambda h: isinstance(h.node, S) and isinstance(h.succ[0].node, Kro), l)
#         res = []
#         while l:
#             th = l.pop(0)
#             if th in sas:
#                 sas.remove(th)
#                 tl = filter(lambda h: th.node.fL==h.node.fL and th.node.fR==h.node.fR and th.succ[0].succ[0].node == h.succ[0].succ[0].node, sas)
#                 res.append([th]+tl)
#                 sas = [ h for h in sas if h not in tl ]
#                 l   = [ h for h in l if h not in tl ]
#             else:
#                 res.append([th]) 
# #         l = [ [h] for h in l if h not in sas ]
# #         while sas:
# #             th = sas.pop(0)
# #             tl = filter(lambda h: th.node.fL==h.node.fL and th.node.fR==h.node.fR and th.succ[0].succ[0].node == h.succ[0].succ[0].node, sas)
# #             res.append([th]+tl)
# #             sas = [ h for h in sas if h not in tl ]
# #         res.extend(l)
#         if n > len(res):
#             self.groupby = res
#             return True
#         return False
#     
#     def genChoices(self, holo):
#         return [ [] ]
#      
#     def apply(self, holo, choice):
#         
#         finalGroup = []
#         for g in self.groupby:
#             if len(g) > 1:
#                 node = []
#                 s = filter(lambda h: h.node.__class__ == S, g)
#                 clsS = S if s else Sacc
#                 node = [ h.succ[0].succ.pop() for h in g ]
#                 node.reverse()
#                 while len(node) > 1:
#                     h0, h1 = node.pop(), node.pop()
#                     del h0.pred[:]
#                     del h1.pred[:]
#                     ah = Add(h0, h1).getHolograph()
#                     ah.succ.extend([h0, h1])
#                     h0.pred.append((ah, 0))
#                     h1.pred.append((ah, 1))
#                     node.append(ah)
#     
#                 h = node[0]
#                 alpha = g[0].succ[0].succ[0] 
#                 newSa = clsS(g[0].node.fL, Kro(alpha, h), g[0].node.fR).getHolograph()
#                 for sh in g:
#                     del sh.succ[0].succ[:]
#                 del alpha.pred[:]
#                 newSa.succ[0].succ.extend([alpha, h])
#                 alpha.pred.append((newSa.succ[0], 0))
#                 h.pred.append((newSa.succ[0], 1))
#                 finalGroup.append(newSa)
#             else:
#                 oldH = g[0]
#                 for predTuple in oldH.pred:
#                     predTuple[0].succ[predTuple[1]] = None
#                 del oldH.pred[:]
#                 finalGroup.append(oldH)
#         
# #         s = filter(lambda h: h.node.__class__ == S, finalGroup)
# #         rest = [h for h in finalGroup if h not in s ]
# #         finalGroup = s + rest
#         finalGroup.reverse()
#         while len(finalGroup) > 1:
#             h0, h1 = finalGroup.pop(), finalGroup.pop()
#             del h0.pred[:]
#             del h1.pred[:]
#             ah = Add(h0, h1).getHolograph()
#             ah.succ.extend([h0, h1])
#             h0.pred.append((ah, 0))
#             h1.pred.append((ah, 1))
#             finalGroup.append(ah)
#         
#         newHolo = finalGroup[0]
# 
#         if len(holo.pred) > 0:
#             del newHolo.pred[:] 
#             for predTuple in holo.pred:
#                 predTuple[0].succ[predTuple[1]] = newHolo
#                 newHolo.pred.append((predTuple[0], predTuple[1]))
# 
#         del holo.pred[:]
#          
#         return newHolo

class HFactorSOutOfAdds(Rule):
    def __init__(self):
        super(HFactorSOutOfAdds, self).__init__()
        self.groupby = []

    def mask(self, node):
        return [True, False]

    def applicable(self, holo):
        l = holo.getLeavesWithDiffType()
        n = len(l)
        scats = filter(lambda h: isinstance(h.node, S), l)
        res = []
        while l:
            th = l.pop(0)
            if th in scats:
                scats.remove(th)
                tl = filter(lambda h: th.node.fL==h.node.fL and th.node.fR==h.node.fR, scats)
                res.append([th]+tl)
                scats = [ h for h in scats if h not in tl ]
                l   = [ h for h in l if h not in tl ]
            else:
                res.append([th]) 
        if n > len(res):
            self.groupby = res
            return True
        return False
    
    def genChoices(self, holo):
        return [ [] ]
     
    def apply(self, holo, choice):
        
        finalGroup = []
        for g in self.groupby:
            if len(g) > 1:
                node = []
                s = filter(lambda h: h.node.__class__ == S, g)
                clsS = S if s else Sacc
                node = [ h.succ.pop() for h in g ]
                node.reverse()
                while len(node) > 1:
                    h0, h1 = node.pop(), node.pop()
                    del h0.pred[:]
                    del h1.pred[:]
                    ah = Add(h0, h1).getHolograph()
                    ah.succ.extend([h0, h1])
                    h0.pred.append((ah, 0))
                    h1.pred.append((ah, 1))
                    node.append(ah)
    
                h = node[0]
                newSa = clsS(g[0].node.fL, h, g[0].node.fR).getHolograph()
                newSa.succ.append(h)
                h.pred.append((newSa, 0))
                finalGroup.append(newSa)
            else:
                oldH = g[0]
                for predTuple in oldH.pred:
                    predTuple[0].succ[predTuple[1]] = None
                del oldH.pred[:]
                finalGroup.append(oldH)
        
        finalGroup.reverse()
        while len(finalGroup) > 1:
            h0, h1 = finalGroup.pop(), finalGroup.pop()
            del h0.pred[:]
            del h1.pred[:]
            ah = Add(h0, h1).getHolograph()
            ah.succ.extend([h0, h1])
            h0.pred.append((ah, 0))
            h1.pred.append((ah, 1))
            finalGroup.append(ah)
        
        newHolo = finalGroup[0]

        if len(holo.pred) > 0:
            del newHolo.pred[:] 
            for predTuple in holo.pred:
                predTuple[0].succ[predTuple[1]] = newHolo
                newHolo.pred.append((predTuple[0], predTuple[1]))

        del holo.pred[:]
         
        return newHolo

class HFactorLeftAlphaOutOfAdds(Rule):
    def __init__(self):
        super(HFactorLeftAlphaOutOfAdds, self).__init__()
        self.groupby = []

    def mask(self, node):
        return [True, False]

    def applicable(self, holo):
        l = holo.getLeavesWithDiffType()
        n = len(l)
        kros = filter(lambda h: isinstance(h.node, Kro) and h.succ[0].node.getOut().isScalar(), l)
        res = []
        while l:
            th = l.pop(0)
            if th in kros:
                kros.remove(th)
                tl = filter(lambda h: th.succ[0].node.sameUpToNames(h.succ[0].node), kros)
                res.append([th]+tl)
                kros = [ h for h in kros if h not in tl ]
                l   = [ h for h in l if h not in tl ]
            else:
                res.append([th]) 
        if n > len(res):
            self.groupby = res
            return True
        return False
    
    def genChoices(self, holo):
        return [ [] ]
     
    def apply(self, holo, choice):
        
        finalGroup = []
        for g in self.groupby:
            if len(g) > 1:
                node = []
                node = [ h.succ.pop() for h in g ]
                node.reverse()
                while len(node) > 1:
                    h0, h1 = node.pop(), node.pop()
                    del h0.pred[:]
                    del h1.pred[:]
                    ah = Add(h0, h1).getHolograph()
                    ah.succ.extend([h0, h1])
                    h0.pred.append((ah, 0))
                    h1.pred.append((ah, 1))
                    node.append(ah)
    
                h = node[0]
                alpha = g[0].succ[0] 
                newKro = Kro(alpha, h).getHolograph()
                for sh in g:
                    del sh.succ[:]
                del alpha.pred[:]
                newKro.succ.extend([alpha, h])
                alpha.pred.append((newKro, 0))
                h.pred.append((newKro, 1))
                finalGroup.append(newKro)
            else:
                oldH = g[0]
                for predTuple in oldH.pred:
                    predTuple[0].succ[predTuple[1]] = None
                del oldH.pred[:]
                finalGroup.append(oldH)
        
        finalGroup.reverse()
        while len(finalGroup) > 1:
            h0, h1 = finalGroup.pop(), finalGroup.pop()
            del h0.pred[:]
            del h1.pred[:]
            ah = Add(h0, h1).getHolograph()
            ah.succ.extend([h0, h1])
            h0.pred.append((ah, 0))
            h1.pred.append((ah, 1))
            finalGroup.append(ah)
        
        newHolo = finalGroup[0]

        if len(holo.pred) > 0:
            del newHolo.pred[:] 
            for predTuple in holo.pred:
                predTuple[0].succ[predTuple[1]] = newHolo
                newHolo.pred.append((predTuple[0], predTuple[1]))

        del holo.pred[:]
         
        return newHolo

#-------------- Rule Sets ----------------

class HTransRuleSet(RuleSet):
    def __init__(self, opts):
        super(HTransRuleSet, self).__init__(opts)
        self.rs = { 
                   'Assign': [HPushTransDown()],
                   'Add': [HPushTransDown()],
                   'Kro': [HPushTransDown()],
                   'Mul': [],
                   'T': [HRemoveTransChain()]
                   }

class HFuseSLLRuleSet(RuleSet):
    def __init__(self, opts):
        super(HFuseSLLRuleSet, self).__init__(opts)
        self.rs = { 
                   'T': [HRemoveTransChain()],
                   'Neg': [HRemoveNegChain()],
                   'S': [HFuseScatters()],
                   'Sacc': [HFuseScatters()],
                   'G': [HFuseGathers()]
                   }

class HNegSaccSLLRuleSet(RuleSet):
    def __init__(self, opts):
        super(HNegSaccSLLRuleSet, self).__init__(opts)
        self.rs = { 
                   'Sacc': [HNegScatterAcc()]
                   }

class HFuseAndUnrollSLLRuleSet(RuleSet):
    def __init__(self, opts):
        super(HFuseAndUnrollSLLRuleSet, self).__init__(opts)
        self.rs = { 
                   'NewSum': [HUnrollSum(opts)],
                   'T': [HRemoveTransChain()],
                   'S': [HFuseScatters()],
                   'Sacc': [HFuseScatters()],
                   'G': [HFuseGathers()]
                   }

class HDistributeSLLRuleSet(RuleSet):
    def __init__(self, opts):
        super(HDistributeSLLRuleSet, self).__init__(opts)
        self.rs = { 
                   'NewSum': [HDistributeSum(opts)],
                   'Iv': [HDistributeIv()]
                   }

class HFactorOutSLLRuleSet(RuleSet):
    def __init__(self, opts):
        super(HFactorOutSLLRuleSet, self).__init__(opts)
        self.rs = {
                   'Add': [HFactorSOutOfAdds(), HFactorLeftAlphaOutOfAdds()], 
                   'S': [HFactorSalphaOutOfSum(), HFactorSOutOfIv()],
                   'Sacc': [HFactorSalphaOutOfSum(), HFactorSOutOfIv()],
                   'Iv': [HFactorIvOutOfSum()],
                   'Kro': [HFactorLeftAlphaOutOfIv()]
                   }


#######################################################

def applySimplifyIndices(expr, opts, caller, explored, oneValueIds):
    if expr in explored:
        return
    
    if isinstance(expr, Operator):
        explored.append(expr)
        for sub in expr.inexpr:
            applySimplifyIndices(sub, opts, expr, explored, oneValueIds)
        
        if isinstance(expr, Sum):
            iList, uFactors = [], []
            for i in range(len(expr.iList)):
                idx = expr.iList[i]
                idx.subs(oneValueIds)
                if not idx.assumesOneValue():
                    iList.append(idx)
                    uFactors.append(expr.uFactors[i])
                else:
                    oneValueIds[idx.i] = idx.b

            if not iList:
                if expr.acc:
                    expr.inexpr[1].delPred(expr)
                    expr.inexpr[1].remove()
                inner = expr.inexpr[0]
                del expr.inexpr[:]
                inner.delPred(expr)
                for p in expr.pred:
                    if p[0] is not None:
                        p[0].inexpr[p[1]] = inner
                        p[0].setAsPredOfInExpr(p[1])
                expr.delPred(caller)
            else:
                expr.iList, expr.uFactors = iList, uFactors
                syms = [ idx.i for idx in iList ]
                iPriority = {}
                for idx in expr.iPriority:
                    if idx in syms:
                        iPriority[idx] = expr.iPriority[idx]
                expr.iPriority = iPriority
                outDep, outerIdx, forceInitIdx = [], [], [] 
                for i in expr.outDep:
                    if not i in oneValueIds:
                        outDep.append(i)
                for i in expr.outerIdx:
                    if not i in oneValueIds:
                        outerIdx.append(i)
                for i in expr.forceInitIdx:
                    if not i in oneValueIds:
                        forceInitIdx.append(i)
                expr.outDep, expr.outerIdx, expr.forceInitIdx = outDep, outerIdx, forceInitIdx
            
                if expr.acc and all(map(lambda idx: any(map(lambda outExpr: idx.i in outExpr, expr.outDep)) or idx.isTop, expr.iList)):
                    expr.inexpr[1].delPred(expr)
                    expr.inexpr[1].remove()
                    del expr.inexpr[1]
                    expr.acc = False
                    
            

def simplifyIndices(expr, opts):
    oneValueIds = {}
    applySimplifyIndices(expr, opts, None, [], oneValueIds)
    
    expr.subs(oneValueIds, [])
    
    return expr

# Locate the first occurance of a Sum operator
def getSigmaExpr(expr, explored):
    if isinstance(expr, Sum):
        return expr
    if isinstance(expr, Operator) and not expr in explored:
        explored.append(expr)
        for sub in expr.inexpr:
            res = getSigmaExpr(sub, explored)
            if not res is None:
                return res
    return None

# Sigma-level merging
def merge(expr, opts):
    # get the first occurance of a Sum operator
    sigma = getSigmaExpr(expr, [])
    if sigma is not None:
        # clear all dependencies
        resetDependencies(sigma, opts, [])
        # find for each subexpression the set of symbols that it depends on
        computeDependencies(sigma, opts, [])
        # find all the subexpressions of sigma that don't depend upon the list of indices in sigma.iList 
        indExprList = computeIndependentSubexpr(sigma, sigma.iList, [], opts)
        
        for e in indExprList:
            if isinstance(e, Sum):
                e = merge(e, opts)
                applyMerge(sigma, e, opts)
    
    return expr

def applyMerge(outer, inner, opts):
    
    # Determine the Param. Matrices right Inside and Outside the inner Sum
    pInside = [ i for i in inner.inexpr if isinstance(i, ParamMat) ]
    pOutside = [ p[0] for p in inner.pred if isinstance(p[0], ParamMat) and len(p[0].depSet) > len(inner.depSet) ] 
    
    # every item in the list is associated to a param. mat. within inner Sum.
    # every item is composed of a tuple of tuples of length 2 (the 2 dims. of a matrix).
    # the tuple associated to the ith dimension contains indices used to gather/scatter on that dimension of the matrix 
    innerIds = [ inner.getIds(p.getSyms()) for p in pInside ]
    outerIds = [ outer.getIds(p.getSyms()) for p in pOutside ]
    
    subsDict = createSubsDict(innerIds, outerIds)
    
    for idx in subsDict:
        if not idx in outer.iPriority:
            outer.iPriority[subsDict[idx]] = max(outer.iPriority[subsDict[idx]], inner.iPriority[idx])
        
    if not subsDict:
        return
    
    newInner = inner.multByG(pOutside[0], pOutside[0].fL, pOutside[0].fR, subsDict, [], opts)
#     newInner = inner.multByG(pOutside[0], pOutside[0].fL, pOutside[0].fR, subsDict, {}, opts)
    
    # Remove G<->Sum(inner) link
    del pOutside[0].inexpr[:]
    inner.delPred(pOutside[0])
    
    for p in pOutside[0].pred:
#         if isinstance(newInner, Sum) and not newInner.acc and len(newInner.iList) == 0:
#             p[0].inexpr[p[1]] = newInner.inexpr[0]
#         else:
        p[0].inexpr[p[1]] = newInner
        p[0].setAsPredOfInExpr(p[1])
    
    


############################################################################################

def getSigmaExprWithPath(expr, explored):
    if isinstance(expr, Sum):
        return [ expr ]
    if isinstance(expr, Operator) and not expr in explored:
        explored.append(expr)
        for sub in expr.inexpr:
            res = getSigmaExprWithPath(sub, explored)
            if res:
                return [expr] + res
        return []
    return []

def lastOccuranceOfType(l, Type):
    elems = filter(lambda obj: isinstance(obj, Type), l)
    if not elems:
        return -1
    return max([ l.index(ob) for ob in elems ])

def obstacleInTheWay(path, resetStartTypes, obPosition, opts):
    if obPosition < 0:
        return False
    return any( map(lambda obj: not any(map(lambda C: isinstance(obj, C), resetStartTypes) ) and path.index(obj) < obPosition, path ) )
    
def applySumExchange(outSigma, inSigmaWithPath, outSigmaBoundaries, opts):
    
    inSigma = inSigmaWithPath.pop()
    lastAddPos = lastOccuranceOfType(inSigmaWithPath, Add)

    if outSigma.acc or not inSigma.acc or obstacleInTheWay(inSigmaWithPath, [Sum, S, Add], lastAddPos, opts): return
    
    #Update outer index list based on priorities
    outSigma.iPriority.update(inSigma.iPriority)
    
    iList, uFactors = [], []
    while len(outSigma.iList) > 0 and len(inSigma.iList) > 0:
        oIdx, iIdx = outSigma.iList[0], inSigma.iList[0]
        if outSigma.iPriority[oIdx.i] > outSigma.iPriority[iIdx.i]:
            iList.append(inSigma.iList.pop(0))
            uFactors.append(inSigma.uFactors.pop(0))
        else:
            iList.append(outSigma.iList.pop(0))
            uFactors.append(outSigma.uFactors.pop(0))

    while len(outSigma.iList) > 0:
        iList.append(outSigma.iList.pop(0))
        uFactors.append(outSigma.uFactors.pop(0))
    while len(inSigma.iList) > 0:
        iList.append(inSigma.iList.pop(0))
        uFactors.append(inSigma.uFactors.pop(0))
    
    outSigma.iList, outSigma.uFactors = iList, uFactors
    
    outSigma.acc = True

    for idx in inSigma.forceInitIdx:
        if not idx in outSigma.forceInitIdx:
            outSigma.forceInitIdx.append(idx)
    for idx in inSigma.outDep:
        if not idx in outSigma.outDep:
            outSigma.outDep.append(idx)
    for idx in inSigma.outerIdx:
        if not idx in outSigma.outerIdx:
            outSigma.outerIdx.append(idx)

    #Break inner Sum's links & create outer Sum's new links
    selfG = filter(lambda g: g.inexpr[0] == inSigma, computeDependentSubexprOfType(inSigma.inexpr[1], iList, [inSigma], opts, G))[0]
    del selfG.inexpr[:]
    inSigma.delPred(selfG)
    
    inPred = inSigma.pred.pop()
    in0 = inSigma.inexpr.pop(0)
    in1 = inSigma.inexpr.pop(0)
    in0.delPred(inSigma)
    in1.delPred(inSigma)
    inPred[0].inexpr[inPred[1]] = in0
    inPred[0].setAsPredOfInExpr(inPred[1])
    
    if lastAddPos < 0:
        remainder = outSigma.inexpr[0].inexpr[0]
    elif lastAddPos == len(inSigmaWithPath)-1:
        remainder = in0
    else:
        remainder = inSigmaWithPath[lastAddPos+1]
    
    newRemainder = remainder.duplicateUpToBoundaries(prefix="acc_", boundaries=outSigmaBoundaries)
    
    newG = G(outSigma.inexpr[0].fL, outSigma, outSigma.inexpr[0].fR)
    newAdd = newRemainder + newG

    newS = S(outSigma.inexpr[0].fL, newAdd, outSigma.inexpr[0].fR)
    outSigma.inexpr.append(newS)
    outSigma.setAsPredOfInExpr(1)    
    
def sumExchange(expr, opts):

    # get first sum
    outSigma = getSigmaExpr(expr, [])
    if outSigma is not None:
        resetDependencies(outSigma, opts, [])
        computeDependencies(outSigma, opts, [])
        
        outSigmaBoundaries = computeIndependentSubexpr(outSigma, outSigma.iList, [], opts)
        
        explored = [ e for e in outSigmaBoundaries ]
        inSigmaWithPath = getSigmaExprWithPath(outSigma.inexpr[0], explored)
        
        if inSigmaWithPath:
            inSigmaWithPath[-1] = sumExchange(inSigmaWithPath[-1], opts)
            applySumExchange(outSigma, inSigmaWithPath, outSigmaBoundaries, opts)
        
    return expr
