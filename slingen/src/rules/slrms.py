'''
Created on Jan 23, 2015

@author: danieles
'''

from itertools import product

from src.dsls.processing import duplicateAtHandleHolo
from src.dsls.ll import llBlock, llLoop, llGuard


class SLRM(object):
    '''
    SLRM - Sigma-LL-Rules Manager
    '''
    def __init__(self, opts):
        super(SLRM, self).__init__()
        self.opts = opts
        self.current = None

class HOfflineSLRM(SLRM):
    """
    SLRM processing holographs. Mind: there cannot be two realgraphs at once as they are created combining same real nodes.
    """
    def __init__(self, sllprog, rs, opts):
        super(HOfflineSLRM, self).__init__(opts)
        self.rs = rs
        self.sllprog = sllprog
#         self.holoEqs = [ s.eq.getHolograph() for s in sllprog.stmtList ]
        self.holoSllProg = sllprog.getHolograph()
        self.holoEqs = self._getHoloEqs(self.holoSllProg.stmtList)
        self.candidateEqs = {}
        self.populate()
        self.initIterator()

    def initIterator(self):
#         self.iter = ( e for e in self.candidateEqs ) # Create a generator for the expressions
        self.iter = ( dict(zip(self.candidateEqs.keys(), cp)) for cp in product(*self.candidateEqs.values()) ) 
        
    def next(self):
        try:
            _next = self.iter.next()
        except StopIteration:
            _next = None
        self.current = _next
#         return None if _next is None else _next.getRealgraph() 
        sllprog = None
        if _next is not None:
            sllprog = self.holoSllProg.copySubs(_next)
            sllprog = sllprog.getRealgraph()
            
        return sllprog 
    
    def _getHoloEqs(self, expr):
        res = []
        if isinstance(expr, llBlock):
            for s in expr:
                res.extend( self._getHoloEqs(s) )
        elif isinstance(expr, llLoop):
            res.extend( self._getHoloEqs(expr.body) )
        elif isinstance(expr, llGuard):
            for b in expr.bodys:
                res.extend( self._getHoloEqs(b) )
        else:
            res.append(expr.eq)
        return res
        
    def groupCandidateEqs(self, origEq):
        cands = [ e for e in self.links if self.links[e] == [] ]
#         self.candidateEqs.append(cands)
        self.candidateEqs[origEq] = cands
        
    def populate(self):
        for eq in self.holoEqs:
            self.generated = []
            self.newRoots = [] 
            self.links = {}
            self.roots = [eq]
            self.apply()
            while(self.newRoots):
                self.roots = self.newRoots
                self.newRoots = []
                self.generated = []
                self.apply()
            self.groupCandidateEqs(eq)
            
    def apply(self): # This should disappear and the logic transferred one level up (populate)
        for root in self.roots:
            self.actualRoot = root
            self.links[self.actualRoot] = []
            self._apply(root)
        self.newRoots = [ e for e in self.links if not self.links[e] and e in self.generated ]

    def _apply(self, holo, mask=None):
#         rs = self.opts['slrs']
        ruleList = filter(lambda rr: rr.applicable(holo), self.rs[holo.node.__class__.__name__]) if holo.node.__class__.__name__ in self.rs else []

        if ruleList:
            for r in ruleList:
                choices = r.genChoices(holo)
                for c in choices:
                    rootHandle = duplicateAtHandleHolo(holo) #returns tuple (newroot, exprHandle)
                    newHolo = r.apply(rootHandle[1], c)
                    newRoot = newHolo if len(newHolo.pred) == 0 else rootHandle[0] 
                    self.links[self.actualRoot].append((r, c, newRoot))
                    self.generated.append(newRoot)
                    tempRoot = self.actualRoot
                    self.actualRoot = newRoot
                    self.links[self.actualRoot] = []
                    self._apply(newHolo, r.mask(holo))
                    self.actualRoot = tempRoot
            return True # If any rule was applied we notify it.
        else:
            if mask is None:
                mask = [True]*len(holo.succ)
#             tempRoot = self.actualRoot
            for s,m in zip(holo.succ, mask):
#                 if tempRoot != self.actualRoot:
#                     s = searchGenHandle(id(s.node), self.actualRoot, lambda h: id(h.node), lambda h: h.succ)
                if m: 
                    generated = self._apply(s)
                    if generated: return True
            return False # No rule applied starting from this node
