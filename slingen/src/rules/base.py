class Rule(object):
    def __init__(self):
        super(Rule, self).__init__()
        self.priority = 0
    
    def mask(self, node):
        return None
    
    def __str__(self):
        return self.__class__.__name__
    
    def __repr__(self):
        return self.__str__()
    
#####################################################

class OptClass(object):
    def __init__(self, opts):
        super(OptClass, self).__init__()
        self.opts = opts
        
    def getOpt(self):
        return None

class RuleSet(OptClass):
    def __init__(self, opts):
        super(RuleSet, self).__init__(opts)
        self.rs = None
        
    def getOpt(self):
        return self.rs