'''
Created on Apr 18, 2012

@author: danieles
'''

import src.irbase

class Unparser(object):
    def __init__(self, fileobj):
        self.file = fileobj

    def unparse(self, funcname):
        self.tab = "  "
        self.indent = 0
        
        self.openFunction(funcname)
        for t in src.irbase.icode.declare:
            self.file.write(t.declare(self.indent*self.tab))

        for b in src.irbase.icode.flatList:
            if len(b.instructions) > 0:
                self.file.write("\n")            
                for i in b.instructions:
                    self.file.write(i.unparse(self.indent*self.tab) + "\n")
        
        self.closeFunction()
    
    def openFunction(self, funcname):
        out = []
        inp = []
        for p in src.irbase.icode.signature:
            if p.isOut:
                out += [p]
            else:
                inp += [p]
        params = ""
        for p in inp:
            params += p.declareAsInParam() + ", "
#            if p.size == 1:
#                params += p.scalar + " " + p.name + ", "
#            else:
#                params += p.scalar + " const * " + p.name + ", "
        
        maxidxout = len(out)-1
        for i in range(maxidxout):
            params += out[i].declareAsOutParam() + ", "
        params += out[maxidxout].declareAsOutParam()
        
#        print self.indent*self.tab + "void " + fname + "()\n{"
        if funcname == 'kernel':
            # force compiler not to inline the kernel function 
            # (this may result in compiler optimizations that can make the tester loop not terminate)
            self.file.write(self.indent*self.tab + "static __attribute__((noinline)) void " + funcname + "(" + params + ")\n{\n")
        else:
            self.file.write(self.indent*self.tab + "void " + funcname + "(" + params + ")\n{\n")
        self.indent += 1

    def closeFunction(self):
        self.indent -= 1
        self.file.write("\n" + self.indent*self.tab + "}\n")
