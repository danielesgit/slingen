'''
Created on Apr 18, 2012

@author: danieles
'''

from sympy import sympify 

class PhysicalLayout(object):
    pass

class ImplicitLayout(PhysicalLayout):
    def __init__(self):
        super(ImplicitLayout, self).__init__()

class Constant(ImplicitLayout):
    def __init__(self):
        super(Constant, self).__init__()

    def __str__(self):
        return "Constant layout."

class ExplicitLayout(PhysicalLayout):
    def __init__(self, name, isIn, isOut, opts):
        super(ExplicitLayout, self).__init__()
        self.name = name
        self.scalar = opts['precision']
        self.isIn = isIn
        self.isOut = isOut

    def declareAsPointer(self, prefix=None):
        name = self.name if prefix is None else prefix+self.name
        return self.scalar + " * " + name 

    def declareAsDblPointer(self, prefix=None):
        name = self.name if prefix is None else prefix+self.name
        return self.scalar + " ** " + name 

    def allocMem(self, indent, align, prefix=None):
        name = self.name if prefix is None else prefix+self.name
        return indent + "*" + name + " = static_cast<"+self.scalar+" *>(aligned_malloc("+str(self.size)+"*sizeof("+self.scalar+"), "+str(align)+"));\n"

    def deallocMem(self, indent, prefix=None):
        name = self.name if prefix is None else prefix+self.name
        return indent + "aligned_free("+name+");\n"

    def memCpy(self, indent, dst, prefix=None):
        name = self.name if prefix is None else prefix+self.name
        return indent + "memcpy("+dst+", "+name+", "+str(self.size)+"*sizeof("+self.scalar+"));\n"
                
    def __str__(self):
        res = self.name +"'s physical Layout - Size: " + str(self.size)
        return res
    
    def __repr__(self):
        return self.__str__()

class Array(ExplicitLayout):
    def __init__(self, name, size, opts, pitch=None, isIn=False, isOut=False, safelyScalarize=False):
        super(Array, self).__init__(name, isIn, isOut, opts)
        if pitch is None:
            self.size = sympify(size[0]*size[1])
            self.pitch = sympify(size[1])
        else:
            self.pitch = sympify(pitch)
            self.size = sympify(size[0]*pitch)
        self.safelyScalarize = safelyScalarize
        
    def declare(self, indent):
        res = indent + self.scalar + " " + self.name + "[" + str(self.size) + "];\n" if not self.safelyScalarize else ""
        return res

    def declareAsStdVector(self, indent, prefix=None):
        name = self.name if prefix is None else prefix+self.name
        res = indent + "std::vector<"+self.scalar+"> " + name + "(" + str(self.size) + ", 0.);" 
        return res

    def declareAsInParam(self):
        return self.scalar + " const * " + self.name

    def declareAsOutParam(self, prefix=None):
        name = self.name if prefix is None else prefix+self.name
        return self.scalar + " * " + name 
    
    def pointerAt(self, key):
        skey = " + " + str(key) if key != 0 else ""
        return self.name + skey
    
    def hasIdx(self, idx):
        return (idx in self.size) or (idx in self.pitch)
    
    def subs(self, bounds):
        self.size = self.size.subs(bounds)
        self.pitch = self.pitch.subs(bounds)
    
    def __getitem__(self, key):
        return self.name + "[" + str(key) + "]"
    
    def __str__(self):
        res = self.name +" is an Array - Size:" + str(self.size)
        return res

class Scalars(ExplicitLayout):
    def __init__(self, name, size, opts, isIn=False, isParam=False, vtype=None, ctx=None):
        super(Scalars, self).__init__(name, isIn, False, opts)
        self.size = size
        self.blackList = [] # Perhaps could become a set?
        self.isOut = False
        self.isParam = isParam
        self.declIn = ctx
        if vtype is not None:
            self.scalar = vtype
        
    def declare(self, indent):
        
        perLine = 8;
        vList = []
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                vList.append(self.name + str(i*self.size[1] + j))
        
        vList = [ v for v in vList if v not in self.blackList ]
        
        n = len(vList) 
        if n > 0:
            res = indent + self.scalar + " "

            if n <= perLine:
                res += vList[0]
                for v in vList[1:]:
                    res += ", " + v
                res += ";\n"
            else:
                q = n//perLine
                r = n%perLine
                
                res += vList[0]
                for v in vList[1:perLine]:
                    res += ", " + v
                i = perLine
                for _ in range(1,q):
                    res += ",\n\t" + vList[i] 
                    for v in vList[i+1:i+perLine]:
                        res += ", " + v
                    i += perLine
                if r > 0:
                    res += ",\n\t" + vList[i]
                    for v in vList[i+1:i+r]:
                        res += ", " + v
    
                res += ";\n"
        else:
            res = ""

        return res
    
    def declareAsInParam(self):
        return self.scalar + " " + self.name 

    def allocMem(self, indent, align, prefix=None):
        name = self.name if prefix is None else prefix+self.name
        vList = []
        if self.size[0]*self.size[1] > 1:
            for i in range(self.size[0]):
                for j in range(self.size[1]):
                    vList.append(name + str(i*self.size[1] + j))
        else:
            vList.append(name)
        res = ""
        for s in vList:
            res += indent + "*" + s + " = static_cast<"+self.scalar+" *>(aligned_malloc(sizeof("+self.scalar+"), "+str(align)+"));\n"
    
        return res
    
    def __getitem__(self, key):
        res = self.name
        if not self.isParam:
            res += str(key)
        return res
    
    def __str__(self):
        res = self.name +" is a pool of scalars - Size:" + str(self.size)
        return res


if __name__ == "__main__":
    pass
    
    