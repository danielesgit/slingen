'''
Created on Mar 13, 2014

@author: danieles
'''

from copy import deepcopy

class Holonode(object):
    def __init__(self, node=None):
        super(Holonode, self).__init__()
        self.pred = []
        self.succ = []
        self.choices = {}
#         self.mask = True
        self.node = node
    
    def pRepr(self, tab=0):
#         res = tab*" " + "(" + str(id(self)) + ", " + repr(self.node) + ", pred: "+ str([ (id(p[0]),p[1]) for p in self.pred ]) + " )\n"
#         tab += 1
#         for s in self.succ:
#             res += s.pRepr(tab)
        if hasattr(self.node, 'name'):
            return self.node.name
        res = self.node.__class__.__name__ + " ( "
        res += self.succ[0].pRepr()
        for s in self.succ[1:]:
            res += " , "
            res += s.pRepr()
        res += " )"
        return res
    
    def getRealgraph(self, memo=None):
        self.node.inexpr = []
        self.node.pred = [ (None, None) ]
        
        if memo is None:
            memo = []
        memo.append(self)
        
        for i,s in zip(range(len(self.succ)),self.succ):
            rs = s.node if s in memo else s.getRealgraph(memo)
            self.node.inexpr.append(rs)
            self.node.setAsPredOfInExpr(i)
        
        return self.node
    
    def getLeavesWithDiffType(self):
        res = []
        for s in self.succ:
            if isinstance(s.node, self.node.__class__):
                res.extend(s.getLeavesWithDiffType())
            else:
                res.append(s)
        return res
        
    def __deepcopy__(self, memo):
        newHolo = type(self)(self.node)
#         newHolo.mask = self.mask

        for i,s in zip(range(len(self.succ)),self.succ):
            news = deepcopy(s, memo)
            newHolo.succ.append(news)
            news.pred.append((newHolo,i))
        
        newHolo.choices = deepcopy(self.choices)
        return newHolo
        
    def __str__(self):
        return self.pRepr()
#        return str(self.getRealgraph())
    
    def __repr__(self):
#        return str(self.getRealgraph())
        return str(self)

if __name__ == "__main__":
    pass