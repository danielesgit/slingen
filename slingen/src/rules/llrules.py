'''
Created on Jan 23, 2015

@author: danieles
'''

from copy import deepcopy
from islpy import Set

from src.dsls.ll import Matrix, Tile, Assign, Mul, Kro, Add, Sub, Neg, T, LDiv, G, Symmetric, Quantity, SquaredMatrix, Function, get_expr_bound_over_domain,\
    Triangular
from src.rules.base import Rule, RuleSet
from sympy import Le, Ge, Lt, Gt, Eq

class TileLoopFriendly(Rule):
    def __init__(self, step=None):
        super(TileLoopFriendly, self).__init__()
        self.step = step if step is not None else (0,0)
        
    def applicable(self, expr):
        return len(expr.pred) == 1 and expr.pred[0][0] is None and expr.getOut().level > 2 and expr.getOut().level <= 4

    def genChoices(self, expr):
        out = expr.getOut()

        if out.isHomogeneous():
            stepi = self.step[0] if self.step[0] > 0 and self.step[0] <= out.size[0] else out.size[0]   
            stepj = self.step[1] if self.step[1] > 0 and self.step[1] <= out.size[1] else out.size[1]   
            choices = [ [i,j] for i in range(1, out.size[0]+1, out.size[1]//stepi) for j in range(1, out.size[1]+1, out.size[1]//stepj) ]
        else:
            size = out.getPartitionSize(0,0)
            hi, hj = out.size[0]-size[0] == 0, out.size[1]-size[1] == 0
            stepi = self.step[0] if self.step[0] > 0 and self.step[0] <= size[0] else size[0]   
            stepj = self.step[1] if self.step[1] > 0 and self.step[1] <= size[1] else size[1]   
            choices = [ [i,j] for i in range(1,size[0]+1, size[0]//stepi) for j in range(1,size[1]+1, size[1]//stepj) ]
            if not hi:
                choices = [ c for c in choices if size[0]%c[0] == 0 ]
            if not hj:
                choices = [ c for c in choices if size[1]%c[1] == 0 ]
        return choices
    
    def apply(self, expr, choice):
        newExpr = Tile( (choice[0], choice[1]), expr)
        expr.pred = [(newExpr, 0)]
        
        return newExpr

class HTileLoopFriendly(Rule):
    def __init__(self, step=None):
        super(HTileLoopFriendly, self).__init__()
        self.step = step if step is not None else (0,0)
        
    def applicable(self, holo):
        return len(holo.pred) == 0 and holo.node.getOut().level > 2 and holo.node.getOut().level <= 4

    def genChoices(self, holo):
        out = holo.node.getOut()

        if out.isHomogeneous():
            stepi = self.step[0] if self.step[0] > 0 and self.step[0] <= out.size[0] else out.size[0]   
            stepj = self.step[1] if self.step[1] > 0 and self.step[1] <= out.size[1] else out.size[1]   
            choices = [ [i,j] for i in range(1, out.size[0]+1, out.size[1]//stepi) for j in range(1, out.size[1]+1, out.size[1]//stepj) ]
        else:
            size = out.getPartitionSize(0,0)
            hi, hj = out.size[0]-size[0] == 0, out.size[1]-size[1] == 0
            stepi = self.step[0] if self.step[0] > 0 and self.step[0] <= size[0] else size[0]   
            stepj = self.step[1] if self.step[1] > 0 and self.step[1] <= size[1] else size[1]   
            choices = [ [i,j] for i in range(1,size[0]+1, size[0]//stepi) for j in range(1,size[1]+1, size[1]//stepj) ]
            if not hi:
                choices = [ c for c in choices if size[0]%c[0] == 0 ]
            if not hj:
                choices = [ c for c in choices if size[1]%c[1] == 0 ]
        return choices
    
    def apply(self, holo, choice):
        newExpr = Tile( (choice[0], choice[1]), holo)
        newHolo = newExpr.getHolograph()
        
        newHolo.succ.append(holo)
        holo.pred.append((newHolo, 0))
        
        return newHolo

class TileVectorize(Rule):
    def __init__(self, nu):
        super(TileVectorize, self).__init__()
        self.nu = nu
        
    def applicable(self, expr):
        return self.nu > 1 and len(expr.pred) == 1 and expr.pred[0][0] is None and expr.getOut().level == 2

    def genChoices(self, expr):
#        out = expr.getOut()
#         choices = [ [1,self.nu], [self.nu,self.nu] ]
        choices = [ [self.nu,self.nu] ]
        return choices
    
    def apply(self, expr, choice):
        newExpr = Tile( (choice[0], choice[1]), expr)
        expr.pred = [(newExpr, 0)]
        
        return newExpr

class HStructurePropagate(Rule):
    def __init__(self):
        super(HStructurePropagate, self).__init__()
        self.priority = 1

    def genChoices(self, holo):
        choices = [ [] ]
        return choices

class HSymmetryProp(HStructurePropagate):
    def __init__(self):
        super(HSymmetryProp, self).__init__()

    def mask(self, node):
        return [True, False]
 
    def applicable(self, holo):
        return len(holo.pred) == 0 and all(map(lambda succ: isinstance(succ.node.getOut(), Symmetric), holo.succ)) \
            and holo.succ[0].node.getOut().access.__class__ != holo.succ[1].node.getOut().access.__class__
     
    def apply(self, holo, choice):
        if not isinstance(holo.succ[1].node.getOut(), Symmetric):
            raise TypeError("LHS' top operator should be symmetric.")
        lhsOut = holo.succ[1].node.getOut()
        lhsOut.access = (holo.succ[0].node.getOut().access.__class__)(lhsOut)
        return holo

class HAAT(HStructurePropagate):
    def __init__(self):
        super(HAAT, self).__init__()

    def mask(self, node):
        return [True, False]
 
    def applicable(self, holo):
        if holo.node.getOut().__class__ is SquaredMatrix:
            holo.getRealgraph()
            if isinstance(holo.succ[0].node, T) and holo.succ[0].succ[0].node.sameUpToNames(holo.succ[1].node):
                return True 
            elif isinstance(holo.succ[1].node, T) and holo.succ[1].succ[0].node.sameUpToNames(holo.succ[0].node):
                return True
        return False
     
    def apply(self, holo, choice):
        m = holo.node.getOut()
        sm = Symmetric(m.name, m.descriptor, m.size, m.o, m.attr, m.fL, m.fR)
        holo.node.out = sm
        return holo

class HSyrk2k(HStructurePropagate):
    def __init__(self):
        super(HSyrk2k, self).__init__()

    def mask(self, node):
        return [True, False]
 
    def applicable(self, holo):
        if holo.node.getOut().__class__ is SquaredMatrix:
            holo.getRealgraph()
            if isinstance(holo.succ[0].node, Mul) and isinstance(holo.succ[1].node, Mul):
                hmul0, hmul1 = holo.succ[0], holo.succ[1] 
                if isinstance(hmul0.succ[1].node, T) and isinstance(hmul1.succ[1].node, T):
                    ht0, ht1 = hmul0.succ[1], hmul1.succ[1]
                    if hmul0.succ[0].node.sameUpToNames(ht1.succ[0].node):
                        if hmul1.succ[0].node.sameUpToNames(ht0.succ[0].node):
                            return True
        return False
     
    def apply(self, holo, choice):
        m = holo.node.getOut()
        sm = Symmetric(m.name, m.descriptor, m.size, m.o, m.attr, m.fL, m.fR)
        holo.node.out = sm
        return holo

class H_temp_ASAT(HStructurePropagate):
    def __init__(self):
        super(H_temp_ASAT, self).__init__()

    def mask(self, node):
        return [True, False]
 
    def applicable(self, holo):
        if holo.node.getOut().__class__ is SquaredMatrix:
            holo.getRealgraph()
            return isinstance(holo.succ[1].node, T)
        return False
     
    def apply(self, holo, choice):
        m = holo.node.getOut()
        sm = Symmetric(m.name, m.descriptor, m.size, m.o, m.attr, m.fL, m.fR)
        holo.node.out = sm
        return holo

class HSplusS(HStructurePropagate):
    def __init__(self):
        super(HSplusS, self).__init__()

    def mask(self, node):
        return [True, False]
 
    def applicable(self, holo):
        return holo.node.getOut().__class__ is SquaredMatrix and all(map(lambda succ: isinstance(succ.node.getOut(), Symmetric), holo.succ))
     
    def apply(self, holo, choice):
        m = holo.node.getOut()
        sm = Symmetric(m.name, m.descriptor, m.size, m.o, m.attr, m.fL, m.fR)
        holo.node.out = sm
        return holo

class HTileVectorize(Rule):
    def __init__(self, nu):
        super(HTileVectorize, self).__init__()
        self.nu = nu
        self.fixedchoice = [[self.nu,1], [self.nu,1], [self.nu,1], [self.nu,1], [self.nu,1], [self.nu,1], [self.nu,1], [self.nu,1]]
        
    def applicable(self, holo):
        return self.nu > 1 and len(holo.pred) == 0 and holo.node.getOut().level == 2

    def genChoices(self, holo):
#         out = holo.node.getOut()
#         idcs, dom_info = holo.node.info.get('indices', []), holo.node.info.get('polytope', Set("{[]}"))
#         get_min = lambda e: get_expr_bound_over_domain(idcs, dom_info, e, 'min')
#         size = [ get_min( s ) for s in out.getFlatSize() ]
#         if not size[0].is_Number or size[0] > 1:
#             if isinstance(out, Symmetric) or isinstance(out, Triangular):  
#                 row_choices = [self.nu]
#             else:
#                 row_choices = [1,self.nu]
#         else:
#             row_choices = [1]
#         choices = []
#         if not size[1].is_Number or size[1] > 1:
#             for c in row_choices:
#                 choices.append( [c, self.nu] )
#         else:
#             choices.append( [self.nu,1] )

#         choices = [ [1,self.nu], [self.nu,self.nu] ]
        choices = [ [self.nu,self.nu] ]
#         choices = [ [1,self.nu] ]
#         choices = [ self.fixedchoice.pop() ]
        return choices
    
    def apply(self, holo, choice):
        newExpr = Tile( (choice[0], choice[1]), holo)
        newHolo = newExpr.getHolograph()
        
        newHolo.succ.append(holo)
        holo.pred.append((newHolo, 0))
        
        return newHolo

class HTileVectorize_Square(HTileVectorize):
    def __init__(self, nu):
        super(HTileVectorize_Square, self).__init__(nu)

    def genChoices(self, holo):

        choices = [ [1,self.nu], [self.nu,self.nu] ]

        return choices

class HTileScalar(Rule):
    def __init__(self):
        super(HTileScalar, self).__init__()
        
    def applicable(self, holo):
        return len(holo.pred) == 0 and holo.node.getOut().level == 2

    def genChoices(self, holo):
#        out = expr.getOut()
#         choices = [ [1,self.nu], [self.nu,self.nu] ]
        choices = [ [1,1] ]
        return choices
    
    def apply(self, holo, choice):
        newExpr = Tile( (choice[0], choice[1]), holo)
        newHolo = newExpr.getHolograph()
        
        newHolo.succ.append(holo)
        holo.pred.append((newHolo, 0))
        
        return newHolo

class TileLF4NuReg(TileLoopFriendly):
    def __init__(self, NR, nu, step=None):
        super(TileLF4NuReg, self).__init__(step)
        self.NR = NR
        self.nu = nu
        self.Ls = 1
        
    def applicable(self, expr):
        return self.nu > 1 and len(expr.pred) == 1 and expr.pred[0][0] is None and expr.getOut().level == 3

    def condition(self, MU, NU, bSize):
        return MU*NU*bSize/self.nu <= self.NR
    
    def genChoices(self, expr):
        out = expr.getOut()
        bSize = out.getBlock(0,0).size[0]*out.getBlock(0,0).size[1]
        if out.isHomogeneous():
            stepi = self.step[0] if self.step[0] > 0 and self.step[0] <= out.size[0] else out.size[0]   
            stepj = self.step[1] if self.step[1] > 0 and self.step[1] <= out.size[1] else out.size[1]   
            choices = [ [i,j] for i in range(1,out.size[0]+1, out.size[0]//stepi) for j in range(1,out.size[1]+1, out.size[1]//stepj) if self.condition(i, j, bSize) ]
        else:
            size = out.getPartitionSize(0,0)
            hi, hj = out.size[0]-size[0] == 0, out.size[1]-size[1] == 0
            stepi = self.step[0] if self.step[0] > 0 and self.step[0] <= size[0] else size[0]   
            stepj = self.step[1] if self.step[1] > 0 and self.step[1] <= size[1] else size[1]   
            choices = [ [i,j] for i in range(1,size[0]+1, size[0]//stepi) for j in range(1,size[1]+1, size[1]//stepj) if self.condition(i, j, bSize) ]
            if not hi:
                choices = [ c for c in choices if size[0]%c[0] == 0 ]
            if not hj:
                choices = [ c for c in choices if size[1]%c[1] == 0 ]
        return choices

class HTileLF4NuReg(HTileLoopFriendly):
    def __init__(self, NR, nu, step=None):
        super(HTileLF4NuReg, self).__init__(step)
        self.NR = NR
        self.nu = nu
        self.Ls = 1
        
    def applicable(self, holo):
        return self.nu > 1 and len(holo.pred) == 0 and holo.node.getOut().level == 3

    def condition(self, MU, NU, bSize):
        return MU*NU*bSize/self.nu <= self.NR
    
    def genChoices(self, holo):
        out = holo.node.getOut()
        bSize = out.getBlock(0,0).size[0]*out.getBlock(0,0).size[1]
        if out.isHomogeneous():
            stepi = self.step[0] if self.step[0] > 0 and self.step[0] <= out.size[0] else out.size[0]   
            stepj = self.step[1] if self.step[1] > 0 and self.step[1] <= out.size[1] else out.size[1]   
            choices = [ [i,j] for i in range(1,out.size[0]+1, out.size[0]//stepi) for j in range(1,out.size[1]+1, out.size[1]//stepj) if self.condition(i, j, bSize) ]
        else:
            size = out.getPartitionSize(0,0)
            hi, hj = out.size[0]-size[0] == 0, out.size[1]-size[1] == 0
            stepi = self.step[0] if self.step[0] > 0 and self.step[0] <= size[0] else size[0]   
            stepj = self.step[1] if self.step[1] > 0 and self.step[1] <= size[1] else size[1]   
            choices = [ [i,j] for i in range(1,size[0]+1, size[0]//stepi) for j in range(1,size[1]+1, size[1]//stepj) if self.condition(i, j, bSize) ]
            if not hi:
                choices = [ c for c in choices if size[0]%c[0] == 0 ]
            if not hj:
                choices = [ c for c in choices if size[1]%c[1] == 0 ]
        return choices

class  HSquareTileLF4NuReg(HTileLF4NuReg):
    def __init__(self, NR, nu, step=None):
        super(HSquareTileLF4NuReg, self).__init__(NR, nu, step)
        self.fixedchoice = [ 2,1,1,1,1,1,1,1]

    def condition(self, MU, NU, bSize):
        return MU*NU*bSize <= self.NR
            
    def genChoices(self, holo):
#         out = holo.node.getOut()
#         idcs, dom_info = holo.node.info.get('indices', []), holo.node.info.get('polytope', Set("{[]}"))
# #         bSize = (out.getBlock(0,0).size[0]*out.getBlock(0,0).size[1]).subs(min_info)
# #         osize = [ s.subs(min_info) for s in out.size ]
#         get_min = lambda e: get_expr_bound_over_domain(idcs, dom_info, e, 'min')
#         bSize = get_min( out.getBlock(0,0).size[0]*(-(-out.getBlock(0,0).size[1]//self.nu)) )
#         if any(map(lambda s: not s.is_Number, out.size)):
#             return [[1,1]]
#         osize = [ get_min(s) for s in out.size ]
#         if out.isHomogeneous():
#             step = self.step[0] if self.step[0] > 0 and self.step[0] <= osize[0] else osize[0]
# #             choices = [ [i,i] for i in range(1,osize[0]+1, osize[0]//step) if self.condition(i, i, bSize) ]
#             choices = [ [i,i] for i in range(1,osize[0]+1, osize[0]//step) if (self.condition(i, i, bSize) and (i==1 or i%2 == 0)) ]
#         else:
# #             size = [ s.subs(min_info) for s in out.getPartitionSize(0,0) ]
#             size = [ get_min(s) for s in out.getPartitionSize(0,0) ]
#             hi, hj = osize[0]-size[0] == 0, osize[1]-size[1] == 0
#             step = self.step[0] if self.step[0] > 0 and self.step[0] <= size[0] else size[0]
#             choices = [ [i,i] for i in range(1,size[0]+1, size[0]//step) if self.condition(i, i, bSize) ]
#             if not hi:
#                 choices = [ c for c in choices if size[0]%c[0] == 0 ]
#             if not hj:
#                 choices = [ c for c in choices if size[1]%c[1] == 0 ]
#         i = self.fixedchoice.pop()
        choices = [[1,1]]
        return choices

class TileLF4RegAtlas(TileLoopFriendly):
    def __init__(self, NR, step=None):
        super(TileLF4RegAtlas, self).__init__(step)
        self.NR = NR
        self.Ls = 1
        
    def applicable(self, expr):
        return len(expr.pred) == 1 and expr.pred[0][0] is None and expr.getOut().level == 3

    def condition(self, MU, NU):
        return MU*NU + MU + NU <= self.NR - self.Ls
    
    def genChoices(self, expr):
        out = expr.getOut()
#        nu = out.getBlock(0,0).size[1]
        if out.isHomogeneous():
            stepi = self.step[0] if self.step[0] > 0 and self.step[0] <= out.size[0] else out.size[0]   
            stepj = self.step[1] if self.step[1] > 0 and self.step[1] <= out.size[1] else out.size[1]   
            choices = [ [i,j] for i in range(1,out.size[0]+1, out.size[0]//stepi) for j in range(1,out.size[1]+1, out.size[1]//stepj) if self.condition(i, j) ]
        else:
            size = out.getPartitionSize(0,0)
            hi, hj = out.size[0]-size[0] == 0, out.size[1]-size[1] == 0
            stepi = self.step[0] if self.step[0] > 0 and self.step[0] <= size[0] else size[0]   
            stepj = self.step[1] if self.step[1] > 0 and self.step[1] <= size[1] else size[1]   
            choices = [ [i,j] for i in range(1,size[0]+1, size[0]//stepi) for j in range(1,size[1]+1, size[1]//stepj) if self.condition(i, j) ]
            if not hi:
                choices = [ c for c in choices if size[0]%c[0] == 0 ]
            if not hj:
                choices = [ c for c in choices if size[1]%c[1] == 0 ]
        return choices

class TileLF4L1Atlas(TileLoopFriendly):
    def __init__(self, B1, C1, step=None):
        super(TileLF4L1Atlas, self).__init__(step)
        self.B1 = B1
        self.C1 = C1
        
    def applicable(self, expr):
        return len(expr.pred) == 1 and expr.pred[0][0] is None and expr.getOut().level == 4

    #Just for the moment
    def condition(self, MB, NB, MU, NU):
#        return ceil(MB*NB/float(self.B1)) + 3*ceil(NB*NU/float(self.B1)) +ceil(MU/float(self.B1))*NU <= self.C1/self.B1
        return 3*MB*NB*MU*NU <= self.C1    
    
    def genChoices(self, expr):
        out = expr.getOut()
        regBlk = out.getBlock(0,0)
        MU,NU = regBlk.size[0], regBlk.size[1] 
        if out.isHomogeneous():
            stepi = self.step[0] if self.step[0] > 0 and self.step[0] <= out.size[0] else out.size[0]   
            stepj = self.step[1] if self.step[1] > 0 and self.step[1] <= out.size[1] else out.size[1]   
            choices = [ [i,j] for i in range(1,out.size[0]+1, out.size[0]//stepi) for j in range(1,out.size[1]+1, out.size[1]//stepj) if self.condition(i, j, MU, NU) ]
        else:
            size = out.getPartitionSize(0,0)
            hi, hj = out.size[0]-size[0] == 0, out.size[1]-size[1] == 0
            stepi = self.step[0] if self.step[0] > 0 and self.step[0] <= size[0] else size[0]   
            stepj = self.step[1] if self.step[1] > 0 and self.step[1] <= size[1] else size[1]   
            choices = [ [i,j] for i in range(1,size[0]+1, size[0]//stepi) for j in range(1,size[1]+1, out.size[1]//stepj) if self.condition(i, j, MU, NU) ]
            if not hi:
                choices = [ c for c in choices if size[0]%c[0] == 0 ]
            if not hj:
                choices = [ c for c in choices if size[1]%c[1] == 0 ]
        return choices

class Tile4Reg(Rule):
    def __init__(self):
        super(Tile4Reg, self).__init__()

    def applicable(self, expr):
        return len(expr.pred) == 1 and expr.pred[0][0] is None and expr.getOut().level == 2

    def genChoices(self, expr):
        out = expr.getOut()
        choices = [ [i,j] for i in range(1,out.size[0]+1) for j in range(1,out.size[1]+1) ]
        return choices
    
    def apply(self, expr, choice):
        newExpr = Tile( (choice[0], choice[1]), expr)
        expr.pred = [(newExpr, 0)]
        
        return newExpr

class HTile4Reg(Rule):
    def __init__(self):
        super(HTile4Reg, self).__init__()

    def applicable(self, holo):
        return len(holo.pred) == 0 and holo.node.getOut().level == 2

    def genChoices(self, holo):
        out = holo.node.getOut()
        choices = [ [i,j] for i in range(1,out.size[0]+1) for j in range(1,out.size[1]+1) ]
        return choices
    
    def apply(self, holo, choice):
        newExpr = Tile( (choice[0], choice[1]), holo)
        newHolo = newExpr.getHolograph()
        
        newHolo.succ.append(holo)
        holo.pred = [(newHolo, 0)]
        
        return newHolo

class TileRule(Rule):
    def __init__(self):
        super(TileRule, self).__init__()

    def applicable(self, expr):
        return len(expr.pred) == 1 and isinstance(expr.pred[0][0], Tile)

    def genChoices(self, expr):
        return [ [] ]

class HTileRule(Rule):
    def __init__(self):
        super(HTileRule, self).__init__()

    def applicable(self, holo):
        return len(holo.pred) == 1 and isinstance(holo.pred[0][0].node, Tile)

    def genChoices(self, holo):
        return [ [] ]

class HAddNegs(Rule):
    def __init__(self):
        super(HAddNegs, self).__init__()

    def applicable(self, holo):
        return isinstance(holo.node, Add) and ( isinstance(holo.succ[0].node, Neg) or isinstance(holo.succ[1].node, Neg)  ) 

    def mask(self, node):
        return [True, False]

    def genChoices(self, holo):
        return [ [] ]

    def apply(self, holo, choice):
        
        r_is_neg = isinstance(holo.succ[1].node, Neg)
        h0, h1 = holo.succ 

        if not r_is_neg:
            newExpr = Sub(h1, h0.succ[0])
        else:
            newExpr = Sub(h0, h1.succ[0])
            
        newHolo = newExpr.getHolograph()

        if not r_is_neg:
            newHolo.succ.append(h1)
            newHolo.succ.append(h0.succ[0])
            h1.pred.remove((holo,1))
            h0.succ[0].pred.remove((h0,0))
            h1.pred.append((newHolo,0))
            h0.succ[0].pred.append((newHolo,1))
        else:
            newHolo.succ.append(h0)
            newHolo.succ.append(h1.succ[0])
            h0.pred.remove((holo,0))
            h1.succ[0].pred.remove((h1,0))
            h0.pred.append((newHolo,0))
            h1.succ[0].pred.append((newHolo,1))
        
        newHolo.pred = holo.pred
        
        for predTuple in holo.pred:
            pred = predTuple[0]
            pos  = predTuple[1]
            pred.succ[pos] = newHolo 
        
        return newHolo

class HMulNegs(Rule):
    def __init__(self):
        super(HMulNegs, self).__init__()

    def applicable(self, holo):
        return (isinstance(holo.node, Mul) or isinstance(holo.node, Kro)) and ( isinstance(holo.succ[0].node, Neg) or isinstance(holo.succ[1].node, Neg)  ) 

    def mask(self, node):
        return [True, False]

    def genChoices(self, holo):
        return [ [] ]

    def apply(self, holo, choice):
        
        l_is_neg, r_is_neg = isinstance(holo.succ[0].node, Neg), isinstance(holo.succ[1].node, Neg)
        h0, h1 = holo.succ 
         
        if not l_is_neg or not r_is_neg:
            l_node = h0.succ[0] if l_is_neg else h0
            r_node = h1.succ[0] if r_is_neg else h1
            newExpr = Neg( type(holo.node)(l_node, r_node) )
        else:
            newExpr = type(holo.node)(h0.succ[0], h1.succ[0])
            
        newHolo = newExpr.getHolograph()

        if not l_is_neg:
            newHolo.succ[0].succ.append(h0)
            newHolo.succ[0].succ.append(h1.succ[0])
            h0.pred.remove((holo,0))
            h1.succ[0].pred.remove((h1,0))
            h0.pred.append((newHolo,0))
            h1.succ[0].pred.append((newHolo,1))
        elif not r_is_neg:
            newHolo.succ[0].succ.append(h0.succ[0])
            newHolo.succ[0].succ.append(h1)
            h0.succ[0].pred.remove((h0,0))
            h1.pred.remove((holo,1))
            h0.succ[0].pred.append((newHolo,0))
            h1.pred.append((newHolo,1))
        else:
            for i,h in enumerate(holo.succ):
                newHolo.succ.append(h.succ[0])
                h.succ[0].pred.remove((h,i))
                h.succ[0].pred.append((newHolo,i))
        
        newHolo.pred = holo.pred
        
        for predTuple in holo.pred:
            pred = predTuple[0]
            pos  = predTuple[1]
            pred.succ[pos] = newHolo 
        
        return newHolo

class HFuseGathers(Rule):
    def __init__(self):
        super(HFuseGathers, self).__init__()

    def applicable(self, holo):
        return isinstance(holo.succ[0].node, G) and holo.node.__class__ == holo.succ[0].node.__class__ 
 
    def genChoices(self, holo):
        return [ [] ]
     
    def apply(self, holo, choice):
        
        hsuccG = holo.succ[0]
        succG = hsuccG.node
        
        fL = succG.fL.compose(holo.node.fL)
        fR = succG.fR.compose(holo.node.fR)
        newHolo = holo.node.__class__(fL, hsuccG.succ[0], fR, ann=deepcopy(holo.node.ann)).getHolograph()
        
        newHolo.succ.append(hsuccG.succ[0])
        hsuccG.succ[0].pred.remove((hsuccG,0))
        hsuccG.succ[0].pred.append((newHolo,0))
        
        if len(holo.pred) > 0:
            del newHolo.pred[:] 
            for predTuple in holo.pred:
                predTuple[0].succ[predTuple[1]] = newHolo
                newHolo.pred.append((predTuple[0], predTuple[1]))

        del holo.pred[:]
        del hsuccG.succ[:]
         
        return newHolo

class HGatherRule(Rule):
    def __init__(self):
        super(HGatherRule, self).__init__()

    def applicable(self, holo):
        return len(holo.pred) == 1 and isinstance(holo.pred[0][0].node, G) and not isinstance(holo.node, Quantity) 

    def genChoices(self, holo):
        return [ [] ]

class TwinTiles(TileRule):
    def __init__(self):
        super(TwinTiles, self).__init__()

    def apply(self, expr, choice):
        tile = expr.pred[0][0]
        e0 = expr.inexpr[0]
        e1 = expr.inexpr[1]
        
        te0, te1 = Tile((tile.nu[0],tile.nu[1]), e0), Tile((tile.nu[0],tile.nu[1]), e1)
        e0.pred = [(te0,0)]
        e1.pred = [(te1,0)]

        newExpr = expr.__class__(te0, te1)
        te0.pred = [(newExpr, 0)]
        te1.pred = [(newExpr, 1)]
        newExpr.pred = tile.pred
        
        for predTuple in tile.pred:
            pred = predTuple[0]
            pos  = predTuple[1]
            if pred is not None:
                pred.inexpr[pos] = newExpr 
        
        return newExpr

class HPropTile(HTileRule):
    def __init__(self):
        super(HPropTile, self).__init__()

    def apply(self, holo, choice):
        tile = holo.pred[0][0].node
        h0 = holo.succ[0]
        
        t0 = Tile((tile.nu[0],tile.nu[1]), h0)
        newExpr = holo.node.__class__(t0)
        
        newHolo = newExpr.getHolograph()
        
        newHolo.succ[0].succ.append(h0)
        h0.pred.remove((holo,0))
        h0.pred.append((newHolo.succ[0],0))
        
        newHolo.pred = holo.pred[0][0].pred
        
        for predTuple in holo.pred[0][0].pred:
            pred = predTuple[0]
            pos  = predTuple[1]
            pred.succ[pos] = newHolo 
        
        return newHolo

class HTwinTiles(HTileRule):
    def __init__(self):
        super(HTwinTiles, self).__init__()

    def mask(self, node):
        return [True, False]

    def apply(self, holo, choice):
        tile = holo.pred[0][0].node
        h0 = holo.succ[0]
        h1 = holo.succ[1]
        
        t0, t1 = Tile((tile.nu[0],tile.nu[1]), h0), Tile((tile.nu[0],tile.nu[1]), h1)
        newExpr = type(holo.node)(t0, t1)
        
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
    
class HTileFunction(HTileRule):
    def __init__(self):
        super(HTileFunction, self).__init__()

    def mask(self, node):
        res = [False]*len(node.succ)
        res[0] = True
        return res
    
    def apply(self, holo, choice):
        tile = holo.pred[0][0].node
        ts = [ Tile((tile.nu[0],tile.nu[1]), h) for h in holo.succ ]
        newExpr = Function(holo.node.name, holo.node.domsize, ts)
        newHolo = newExpr.getHolograph()
        
        for i,h in enumerate(holo.succ):
            newHolo.succ[i].succ.append(h)
            h.pred.remove((holo,i))
            h.pred.append((newHolo.succ[i],i))
        
        newHolo.pred = holo.pred[0][0].pred
        
        for predTuple in holo.pred[0][0].pred:
            pred = predTuple[0]
            pos  = predTuple[1]
            pred.succ[pos] = newHolo 
        
        return newHolo
    
class TileT(TileRule):
    def __init__(self):
        super(TileT, self).__init__()

    def apply(self, expr, choice):
        tile = expr.pred[0][0]
        e = expr.inexpr[0]
        
        te = Tile((tile.nu[1],tile.nu[0]), e)
        e.pred = [(te,0)]

        newExpr = T(te)
        te.pred = [(newExpr, 0)]
        newExpr.pred = tile.pred
        
        for predTuple in tile.pred:
            pred = predTuple[0]
            pos  = predTuple[1]
            if pred is not None:
                pred.inexpr[pos] = newExpr 
        
        return newExpr


class HTileT(HTileRule):
    def __init__(self):
        super(HTileT, self).__init__()

    def apply(self, holo, choice):
        tile = holo.pred[0][0].node
        h = holo.succ[0]
        
        tt = Tile((tile.nu[1],tile.nu[0]), h)
        newExpr = T(tt)
        
        newHolo = newExpr.getHolograph()
        
        newHolo.succ[0].succ.append(h)
        h.pred.remove((holo,0))
        h.pred.append((newHolo.succ[0],0))
        
        newHolo.pred = holo.pred[0][0].pred
        
        for predTuple in holo.pred[0][0].pred:
            pred = predTuple[0]
            pos  = predTuple[1]
            pred.succ[pos] = newHolo 
        
        return newHolo

class HGatherT(HGatherRule):
    def __init__(self):
        super(HGatherT, self).__init__()

    def apply(self, holo, choice):
        gat = holo.pred[0][0].node
        h = holo.succ[0]
        
        gh = G(deepcopy(gat.fR), h, deepcopy(gat.fL))
        newExpr = T(gh, out=gat.out.duplicate(prefix="t"))
        
        newHolo = newExpr.getHolograph()
        
        newHolo.succ[0].succ.append(h)
        h.pred.remove((holo,0))
        h.pred.append((newHolo.succ[0],0))
        
        newHolo.pred = holo.pred[0][0].pred
        
        for predTuple in holo.pred[0][0].pred:
            pred = predTuple[0]
            pos  = predTuple[1]
            pred.succ[pos] = newHolo 
        
        return newHolo

class TileMul(TileRule):
    def __init__(self):
        super(TileMul, self).__init__()

    def genChoices(self, expr):
        e0 = expr.inexpr[0]
        choices = [ [k] for k in range(1,e0.size[1]+1) ]
        return choices

    def apply(self, expr, choice):
        tile = expr.pred[0][0]
        e0 = expr.inexpr[0]
        e1 = expr.inexpr[1]
        
        te0, te1 = Tile((tile.nu[0], choice[0]), e0), Tile((choice[0],tile.nu[1]), e1)
        e0.pred = [(te0,0)]
        e1.pred = [(te1,0)]

#         newExpr = Mul(te0, te1)
        newExpr = te0*te1
        te0.pred = [(newExpr, 0)]
        te1.pred = [(newExpr, 1)]
        newExpr.pred = tile.pred
        
        for predTuple in tile.pred:
            pred = predTuple[0]
            pos  = predTuple[1]
            if pred is not None:
                pred.inexpr[pos] = newExpr 
        
        return newExpr

class HTileMul(HTileRule):
    def __init__(self):
        super(HTileMul, self).__init__()

    def mask(self, node):
        return [True, False]

    def genChoices(self, holo):
        out0 = holo.succ[0].node.getOut()
        choices = [ [k] for k in range(1,out0.size[1]+1) ]
        return choices

    def apply(self, holo, choice):
        tile = holo.pred[0][0].node
        h0 = holo.succ[0]
        h1 = holo.succ[1]
        
        t0, t1 = Tile((tile.nu[0],choice[0]), h0), Tile((choice[0],tile.nu[1]), h1)
        newExpr = t0*t1
        
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

class HTileLDiv(HTileRule):
    def __init__(self):
        super(HTileLDiv, self).__init__()

    def mask(self, node):
        return [True, False]

    def genChoices(self, holo):
        out0 = holo.succ[0].node.getOut()
        choices = [ [i] for i in range(1,out0.size[0]+1) ]
        return choices

    def apply(self, holo, choice):
        tile = holo.pred[0][0].node
        h0 = holo.succ[0]
        h1 = holo.succ[1]
        
        t0, t1 = Tile((choice[0], tile.nu[0]), h0), Tile((choice[0],tile.nu[1]), h1)
        newExpr = LDiv(t0,t1)
        
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

class HTileLDivTriang(HTileLDiv):
    def __init__(self):
        super(HTileLDivTriang, self).__init__()

    def mask(self, node):
        return [True, False]

    def genChoices(self, holo):
        choices = [ [holo.pred[0][0].node.nu[0]] ]
        return choices

class TileMulVectorize(TileMul):
    def __init__(self, nu):
        super(TileMulVectorize, self).__init__()
        self.nu = nu
        
    def applicable(self, expr):
        return self.nu > 1 and len(expr.pred) == 1 and isinstance(expr.pred[0][0], Tile) and expr.getOut().level == 2

    def genChoices(self, expr):
        return [ [ expr.pred[0][0].nu[1] ] ]

class HTileMulVectorize(HTileMul):
    def __init__(self, nu):
        super(HTileMulVectorize, self).__init__()
        self.nu = nu
        self.fixedchoice = [[1],[1],[1],[1],[1],[1],[1],[1]]
        
    def applicable(self, holo):
#         return len(holo.pred) == 1 and isinstance(holo.pred[0][0].node, Tile)
        return self.nu > 1 and len(holo.pred) == 1 and isinstance(holo.pred[0][0].node, Tile) and holo.node.getOut().level == 2

    def genChoices(self, holo):
#         choice = [ [ 1 ], [ holo.pred[0][0].node.nu[1] ] ] if holo.pred[0][0].node.nu[1] > 1 else [ [ 1 ] ]  
        choice = [ [ holo.pred[0][0].node.nu[1] ] ]
#         choice = [ [ 1 ] ]
    
# #         out = holo.node.getOut()
#         succ0_out = holo.succ[0].node.getOut()
#         succ1_out = holo.succ[1].node.getOut()
#         idcs, dom_info = holo.node.info.get('indices', []), holo.node.info.get('polytope', Set("{[]}"))
#         s = get_expr_bound_over_domain(idcs, dom_info, succ0_out.getFlatSize()[1], 'min')
#         if not s.is_Number or s > 1:
#             cond = lambda out: any(map(lambda mat_type: isinstance(out, mat_type), [Symmetric, Triangular])) 
#             if cond(succ0_out) or cond(succ1_out):  
#                 choice = [ [ self.nu ] ]
#             else:
#                 choice = [ [ 1 ], [ self.nu ] ]
#         else:
#             choice = [ [ 1 ] ]

#         choice = [ self.fixedchoice.pop() ]

        return choice

# class HTileMulScalar(HTileMul):
#     def __init__(self, nu):
#         super(HTileMulScalar, self).__init__()
#         
#     def applicable(self, holo):
# #         return len(holo.pred) == 1 and isinstance(holo.pred[0][0].node, Tile)
#         return len(holo.pred) == 1 and isinstance(holo.pred[0][0].node, Tile) and holo.node.getOut().level == 2
# 
#     def genChoices(self, holo):
#         return [ [ 1 ] ]

# class HTileLDivTriangVectorize(HTileLDivTriang):
#     def __init__(self, nu):
#         super(HTileMulVectorize, self).__init__()
#         self.nu = nu
#         
#     def applicable(self, holo):
# #         return len(holo.pred) == 1 and isinstance(holo.pred[0][0].node, Tile)
#         return self.nu > 1 and len(holo.pred) == 1 and isinstance(holo.pred[0][0].node, Tile) and holo.node.getOut().level == 2


class TileMulLFAtlas(TileMul):
    def __init__(self, step=0):
        super(TileMulLFAtlas, self).__init__()
        self.step = step
        
    def applicable(self, expr):
        return len(expr.pred) == 1 and isinstance(expr.pred[0][0], Tile) and expr.getOut().level > 2 and expr.getOut().level <= 4

    def genChoices(self, expr):
        inA = expr.inexpr[0].getOut()
        K = inA.size[1]
        extrema = [ [1] ]
#         if K > 1:
#             extrema.append([K])
        if inA.isHomogeneous():
            step = self.step if self.step > 0 and self.step <= K else K 
            choices = [ [k] for k in range(4, K//2, K//step) ] + extrema
        else:
            size = inA.getPartitionSize(0,0)
            hk = K-size[1] == 0
            step = self.step if self.step > 0 and self.step <= size[1] else size[1] 
            choices = [ [k] for k in range(4, K//2, size[1]//step) ] + extrema
            if not hk:
                choices = [ c for c in choices if size[1]%c[0] == 0 ]
        return choices

class TileMulLF_IL1(TileMul):
    def __init__(self, iLimit, nu=1,step=0):
        super(TileMulLF_IL1, self).__init__()
        self.step = step
        self.iLimit = iLimit
        self.nu = nu
        
    def applicable(self, expr):
        return len(expr.pred) == 1 and isinstance(expr.pred[0][0], Tile) and expr.getOut().level > 2 and expr.getOut().level <= 4

    def genChoices(self, expr):
        inA = expr.inexpr[0].getOut()
#        inB = expr.inexpr[1].getOut()
        tile = expr.pred[0][0]
        
        bOfA = inA.getBlock(0,0)
#         iSizeK1 = tile.nu[0]*tile.nu[1]*bOfA.size[0]*bOfA.size[1]*inB.getBlock(0,0).size[1]
        iSizeK1 = tile.nu[1]*bOfA.size[1]
        
        K = inA.size[1]

        if inA.isHomogeneous():
            step = self.step if self.step > 0 and self.step <= K else K 
#             choices = [ [k] for k in range(1, K+1, K//step) if iSizeK1*k/self.nu <= self.iLimit ]
            choices = [ [k] for k in range(1, K+1, K//step) if iSizeK1*k/self.nu <= 32/self.nu ] # ... <= NB/2/nu
        else:
            size = inA.getPartitionSize(0,0)
            hk = K-size[1] == 0
            step = self.step if self.step > 0 and self.step <= size[1] else size[1] 
#             choices = [ [k] for k in range(1, K+1, size[1]//step) if iSizeK1*k/self.nu <= self.iLimit ]
            choices = [ [k] for k in range(1, K+1, size[1]//step) if iSizeK1*k/self.nu <= 32/self.nu ] 
            if not hk:
                choices = [ c for c in choices if size[1]%c[0] == 0 ]
        return choices

class HTileMulLF_IL1(HTileMul):
    def __init__(self, iLimit, nu=1,step=0):
        super(HTileMulLF_IL1, self).__init__()
        self.step = step
        self.iLimit = iLimit
        self.nu = nu
        
    def applicable(self, holo):
        return len(holo.pred) == 1 and isinstance(holo.pred[0][0].node, Tile) and holo.node.getOut().level > 2 and holo.node.getOut().level <= 4

    def genChoices(self, holo):
        inA = holo.succ[0].node.getOut()
        tile = holo.pred[0][0].node
        
        bOfA = inA.getBlock(0,0)
#         iSizeK1 = tile.nu[0]*tile.nu[1]*bOfA.size[0]*bOfA.size[1]*inB.getBlock(0,0).size[1]
        iSizeK1 = tile.nu[1]*bOfA.size[1]
        
        K = inA.size[1]

        if inA.isHomogeneous():
            step = self.step if self.step > 0 and self.step <= K else K 
#             choices = [ [k] for k in range(1, K+1, K//step) if iSizeK1*k/self.nu <= self.iLimit ]
            choices = [ [k] for k in range(1, K+1, K//step) if iSizeK1*k/self.nu <= 32/self.nu ] # ... <= NB/2/nu
        else:
            size = inA.getPartitionSize(0,0)
            hk = K-size[1] == 0
            step = self.step if self.step > 0 and self.step <= size[1] else size[1] 
#             choices = [ [k] for k in range(1, K+1, size[1]//step) if iSizeK1*k/self.nu <= self.iLimit ]
            choices = [ [k] for k in range(1, K+1, size[1]//step) if iSizeK1*k/self.nu <= 32/self.nu ] 
            if not hk:
                choices = [ c for c in choices if size[1]%c[0] == 0 ]
            if not choices:
                choices = [ [1] ]
        return choices

class HTileLDivTriangLF_IL1(HTileLDivTriang):
    def __init__(self, iLimit, nu=1,step=0):
        super(HTileLDivTriangLF_IL1, self).__init__()
        self.step = step
        self.iLimit = iLimit
        self.nu = nu
        
    def applicable(self, holo):
        return len(holo.pred) == 1 and isinstance(holo.pred[0][0].node, Tile) and holo.node.getOut().level > 2 and holo.node.getOut().level <= 4

    def genChoices(self, holo):
        inA = holo.succ[0].node.getOut()
        tile = holo.pred[0][0].node
        
        bOfA = inA.getBlock(0,0)
#         iSizeK1 = tile.nu[0]*tile.nu[1]*bOfA.size[0]*bOfA.size[1]*inB.getBlock(0,0).size[1]
        iSizeK1 = tile.nu[1]*bOfA.size[1]
        
        K = inA.size[1]

        if inA.isHomogeneous():
            step = self.step if self.step > 0 and self.step <= K else K 
#             choices = [ [k] for k in range(1, K+1, K//step) if iSizeK1*k/self.nu <= self.iLimit ]
            choices = [ [k] for k in range(1, K+1, K//step) if iSizeK1*k/self.nu <= 32/self.nu ] # ... <= NB/2/nu
        else:
            size = inA.getPartitionSize(0,0)
            hk = K-size[1] == 0
            step = self.step if self.step > 0 and self.step <= size[1] else size[1] 
#             choices = [ [k] for k in range(1, K+1, size[1]//step) if iSizeK1*k/self.nu <= self.iLimit ]
            choices = [ [k] for k in range(1, K+1, size[1]//step) if iSizeK1*k/self.nu <= 32/self.nu ] 
            if not hk:
                choices = [ c for c in choices if size[1]%c[0] == 0 ]
            if not choices:
                choices = [ [1] ]
        return choices

class HSquareTileMulLF_IL1(HTileMulLF_IL1):
    def __init__(self, iLimit, nu=1,step=0):
        super(HSquareTileMulLF_IL1, self).__init__(iLimit, nu, step)
        
    def genChoices(self, holo):
#         inA = holo.succ[0].node.getOut()
#         tile = holo.pred[0][0].node
#         
#         bOfA = inA.getBlock(0,0)
# #         iSizeK1 = tile.nu[0]*tile.nu[1]*bOfA.size[0]*bOfA.size[1]*inB.getBlock(0,0).size[1]
#         iSizeK1 = tile.nu[1]*bOfA.size[1]
#         
#         K = inA.size[1]
# 
#         if inA.isHomogeneous():
# #             step = self.step if self.step > 0 and self.step <= K else K 
# #             choices = [ [k] for k in range(1, K+1, K//step) if iSizeK1*k/self.nu <= self.iLimit ]
# #             choices = [ [tile.nu[0]] if (iSizeK1*tile.nu[0]/self.nu <= 32/self.nu) else [1] ] # ... <= NB/2/nu
#             choices = [ [tile.nu[0]] if (iSizeK1*tile.nu[0]/self.nu <= 32/self.nu) and (tile.nu[0]%2 == 0) else [1] ] # ... <= NB/2/nu
#         else:
#             size = inA.getPartitionSize(0,0)
#             hk = K-size[1] == 0
# #             step = self.step if self.step > 0 and self.step <= size[1] else size[1] 
# #             choices = [ [k] for k in range(1, K+1, size[1]//step) if iSizeK1*k/self.nu <= self.iLimit ]
#             choices = [ [tile.nu[0]] if iSizeK1*tile.nu[0]/self.nu <= 32/self.nu else [1] ] 
#             if not hk:
#                 choices = [ c for c in choices if size[1]%c[0] == 0 ]
#             if not choices:
#                 choices = [ [1] ] # Dirty workaround: if there is no possibility to choose nu[0] means I cannot have a squared tile.
        choices = [ [1] ] 
        return choices            # Need to add possibility to abort an apply and exclude the initial root.

class Tile4RegAtlas(Tile4Reg):
    def __init__(self, NR):
        super(Tile4RegAtlas, self).__init__()
        self.NR = NR
        
    def condition(self, MU, NU):
        return MU*NU <= self.NR

    def genChoices(self, expr):
        out = expr.getOut()
#        choices = [ [i,j] for i in range(1, out.size[0]+1) for j in range(1, out.size[1]+1) if i*j+i+j<= 15 ] + [[out.size[0],out.size[1]]]
        choices = [ [i,j] for i in range(1, out.size[0]+1) for j in range(1, out.size[1]+1) if self.condition(i, j) ]
        return choices

class HTile4RegAtlas(HTile4Reg):
    def __init__(self, NR):
        super(HTile4RegAtlas, self).__init__()
        self.NR = NR
        
    def condition(self, MU, NU):
        return MU*NU <= self.NR

    def genChoices(self, holo):
        out = holo.node.getOut()
#        choices = [ [i,j] for i in range(1, out.size[0]+1) for j in range(1, out.size[1]+1) if i*j+i+j<= 15 ] + [[out.size[0],out.size[1]]]
        choices = [ [i,j] for i in range(1, out.size[0]+1) for j in range(1, out.size[1]+1) if self.condition(i, j) ]
        return choices

class HSquareTile4RegAtlas(HTile4RegAtlas):
    def __init__(self, NR):
        super(HSquareTile4RegAtlas, self).__init__(NR)
        self.NR = NR

    def genChoices(self, holo):
        out = holo.node.getOut()
        choices = [ [i,i] for i in range(1, out.size[0]+1) if self.condition(i, i) ]
        return choices
    
class TileMulAtlas(TileMul):
    def __init__(self):
        super(TileMulAtlas, self).__init__()
        
    def genChoices(self, expr):
        e0 = expr.inexpr[0].getOut()
        choices = [ [k] for k in range(1,e0.size[1]+1) if k <= 32] # k <= Assuming NB(=64 values in Atlas model paper) / 2
        return choices

class HTileMulAtlas(HTileMul):
    def __init__(self):
        super(HTileMulAtlas, self).__init__()

    def genChoices(self, holo):
        out0 = holo.succ[0].node.getOut()
        choices = [ [k] for k in range(1,out0.size[1]+1) if k <= 32] # k <= Assuming NB(=64 values in Atlas model paper) / 2
        return choices

class HSquareTileMulAtlas(HTileMul):
    def __init__(self):
        super(HSquareTileMulAtlas, self).__init__()

    def genChoices(self, holo):
        tile = holo.pred[0][0].node
        choices = [ [tile.nu[0]] ]
        return choices

class Tile4RegFixed(Tile4Reg):
    def __init__(self, M, N=None):
        super(Tile4RegFixed, self).__init__()
        self.M = M
        if N is None:
            self.N = M
        else:
            self.N = N

#    def applicable(self, expr):
#        return len(expr.pred) == 1 and expr.pred[0][0] is None and expr.getOut().level == 3

    def genChoices(self, expr):
#        choices = [ [1,j] for j in range(1, self.N) ]
#        return choices
        return [ [self.M,self.N] ]

class Tile4L1Fixed(TileLoopFriendly):
    def __init__(self, M, N=None):
        super(Tile4L1Fixed, self).__init__()
        self.M = M
        if N is None:
            self.N = M
        else:
            self.N = N

    def applicable(self, expr):
        return len(expr.pred) == 1 and expr.pred[0][0] is None and expr.getOut().level == 4

    def genChoices(self, expr):
#        choices = [ [1,j] for j in range(1, self.N) ]
#        return choices
        return [ [self.M,self.N] ]
    
class TileMulFixed(TileMul):
    def __init__(self, K):
        super(TileMulFixed, self).__init__()
        self.K = K
    def genChoices(self, expr):
        return [ [self.K] ]
    

#----------------------- RuleSets -----------------------

class BasicRuleSet(RuleSet):
    def __init__(self, opts):
        super(BasicRuleSet, self).__init__(opts)
        self.rs = { 
                   'Assign': [TwinTiles()],
                   'Add': [TwinTiles()],
                   'Kro': [TwinTiles()],
                   'Mul': [TileMul()],
                   'T': [TileT()]
                   }

class HBasicRuleSet(RuleSet):
    def __init__(self, opts):
        super(HBasicRuleSet, self).__init__(opts)
        self.rs = { 
                   'Assign': [HTwinTiles(), HSymmetryProp()],
                   'Add': [HTwinTiles()],
                   'Kro': [HTwinTiles()],
                   'Mul': [HTileMul()],
                   'T': [HTileT()]
                   }

class HValidateLLRuleSet(RuleSet):
    def __init__(self, opts):
        super(HValidateLLRuleSet, self).__init__(opts)
        self.rs = { 
                   'Assign': [HTileVectorize(self.opts['nu']), HTwinTiles(), HSymmetryProp()],
                   'Add': [HTwinTiles()],
                   'Kro': [HTwinTiles()],
                   'Mul': [HTileMul()],
                   'T': [HTileT()]
                   }

class AtlasRuleSet_TileForReg(RuleSet):
    def __init__(self, opts):
        super(AtlasRuleSet_TileForReg, self).__init__(opts)
        self.rs = { 
                   'Assign': [Tile4RegAtlas(self.opts['nr']), TwinTiles()],
                   'Add': [TwinTiles()],
                   'Kro': [TwinTiles()],
#                    'Mul': [TileMulVectorize(), TileMulLFAtlas()],
                   'Mul': [ TileMulAtlas() ],
                   'T': [TileT()]
                   }

class AtlasRuleSet_HTileForReg(RuleSet):
    def __init__(self, opts):
        super(AtlasRuleSet_HTileForReg, self).__init__(opts)
        self.rs = { 
                   'Assign': [HTile4RegAtlas(self.opts['nr']), HTwinTiles(), HSymmetryProp()],
                   'Add': [HTwinTiles()],
                   'Kro': [HTwinTiles()],
#                    'Mul': [TileMulVectorize(), TileMulLFAtlas()],
                   'Mul': [ HTileMulAtlas() ],
                   'T': [HTileT()]
                   }

class AtlasRuleSet_HSquareTileForReg(AtlasRuleSet_HTileForReg):
    def __init__(self, opts):
        super(AtlasRuleSet_HSquareTileForReg, self).__init__(opts)
        self.rs['Assign'] = [HSquareTile4RegAtlas(self.opts['nr']), HTwinTiles(), HSymmetryProp()]
        self.rs['Mul'] = [ HSquareTileMulAtlas() ]

class AtlasRuleSet_NuWay_TileForReg(RuleSet):
    def __init__(self, opts):
        super(AtlasRuleSet_NuWay_TileForReg, self).__init__(opts)
        self.rs = { 
                   'Assign': [TileVectorize(self.opts['nu']), TileLF4NuReg(self.opts['nr'], self.opts['nu']), TwinTiles()],
                   'Add': [TwinTiles()],
                   'Kro': [TwinTiles()],
#                    'Mul': [TileMulVectorize(), TileMulLFAtlas()],
                   'Mul': [TileMulVectorize(self.opts['nu']), TileMulLF_IL1(self.opts['icachel1'], self.opts['nu'])],
                   'T': [TileT()]
                   }

class AtlasRuleSet_NuWay_HTileForReg(RuleSet):
    def __init__(self, opts):
        super(AtlasRuleSet_NuWay_HTileForReg, self).__init__(opts)
        self.rs = { 
                   'Assign': [HTileVectorize(self.opts['nu']), HTileLF4NuReg(self.opts['nr'], self.opts['nu']), HTwinTiles(), HSymmetryProp()],
                   'Add': [HTwinTiles(), HSplusS(), HSyrk2k(), HAddNegs() ],
                   'Sub': [HTwinTiles(), HSplusS()],
                   'Kro': [HTwinTiles(), HMulNegs() ],
                   'Neg': [HPropTile()],
#                    'RDiv': [HTwinTiles()],
#                    'Function': [HTileFunction()],
#                    'Mul': [TileMulVectorize(), TileMulLFAtlas()],
                   'Mul': [HTileMulVectorize(self.opts['nu']), HTileMulLF_IL1(self.opts['icachel1'], self.opts['nu'])],
                   'LDiv': [ HTileLDivTriang() ],
                   'T': [HTileT(), HGatherT()],
                   'G': [HFuseGathers()]                   
                   }

class HApplyProperties(RuleSet):
    def __init__(self, opts):
        super(HApplyProperties, self).__init__(opts)
        self.rs = { 
                   'Assign': [HSymmetryProp()]
                   }

class AtlasRuleSet_NuWay_HSquareTileForReg(AtlasRuleSet_NuWay_HTileForReg):
    def __init__(self, opts):
        super(AtlasRuleSet_NuWay_HSquareTileForReg, self).__init__(opts)
        self.rs['Assign'] = [HTileVectorize(self.opts['nu']), HSquareTileLF4NuReg(self.opts['nr'], self.opts['nu']), HTwinTiles(), HSymmetryProp()]
#         self.rs['Mul'] = [HTileMulVectorize(self.opts['nu']), HSquareTileMulLF_IL1(self.opts['icachel1'], self.opts['nu']), HAAT(), HMulNegs() ]
        self.rs['Mul'] = [HTileMulVectorize(self.opts['nu']), HSquareTileMulLF_IL1(self.opts['icachel1'], self.opts['nu']), HAAT(), H_temp_ASAT(), HMulNegs() ]

class AtlasRuleSet_NuWay(RuleSet):
    def __init__(self, opts):
        super(AtlasRuleSet_NuWay, self).__init__(opts)
        self.rs = { 
                   'Assign': [TileVectorize(self.opts['nu']), TwinTiles()],
                   'Add': [TwinTiles()],
                   'Kro': [TwinTiles()],
                   'Mul': [TileMulVectorize(self.opts['nu']), TileMulLFAtlas()],
                   'T': [TileT()]
                   }

class AtlasRuleSet_HNuWay(RuleSet):
    def __init__(self, opts):
        super(AtlasRuleSet_HNuWay, self).__init__(opts)
        self.rs = { 
                   'Assign': [HTileVectorize(self.opts['nu']), HTwinTiles(), HSymmetryProp()],
                   'Add': [HTwinTiles(), HSplusS()],
                   'Kro': [HTwinTiles()],
                   'Mul': [HTileMulVectorize(self.opts['nu']), HTileMulAtlas(), HAAT()],
                   'LDiv': [ HTileLDivTriang() ],
                   'T': [HTileT()]
                   }

class AtlasRuleSet_HVal(RuleSet):
    def __init__(self, opts):
        super(AtlasRuleSet_HVal, self).__init__(opts)
        self.rs = { 
                   'Assign': [HTileScalar(), HTwinTiles(), HSymmetryProp()],
                   'Add': [HTwinTiles(), HSplusS(), HAddNegs()],
                   'Sub': [HTwinTiles(), HSplusS()],
                   'Kro': [HTwinTiles(), HMulNegs()],
                   'Div': [HTwinTiles()],
                   'Sqrt': [HPropTile()],
                   'Neg': [HPropTile()],
                   'Mul': [HSquareTileMulAtlas(), HAAT(), HMulNegs()],
#                    'LDiv': [ HTileLDivTriang() ],
                   'T': [HTileT(), HGatherT()],
                   'G': [HFuseGathers()]
                   
                   }

class FixedRuleSet(RuleSet):
    def __init__(self, opts):
        super(FixedRuleSet, self).__init__(opts)
        self.rs = { 
                   'Assign': [Tile4RegFixed(2,2), TwinTiles()],
                   'Add': [TwinTiles()],
                   'Kro': [TwinTiles()],
                   'Mul': [TileMulVectorize(), TileMulLFAtlas(4)],
                   'T': [TileT()]
                   }
