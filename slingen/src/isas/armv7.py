'''
Created on Dec 21, 2013

@author: nikolaoskyrtatas
'''

# from src.irbase import *
# from src.isas.isabase import *
from src.irbase import RValue
from src.isas.isabase import ISA
from src.irbase import ScaLoad, Deref, Mov
    
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


class ARMv7(ISA):
    def __init__(self, opts):
        super(ARMv7, self).__init__()
#         self.nu = [ 1 ]
        self.precision = opts['precision']
        self.name = "ARMv7"
#         self.vectorize = False
        fp_s = { 'type': self.precision } # input/output types allowed by the ISA for a given nu
        fp_s['arith'] = [ ScaAdd, ScaMul ]
        fp_s['load']  = [ ScaLoad, Deref ]
        fp_s['misc']  = [ ]
        fp_s['set']   = [ ]
        fp_s['move']  = [ ]
        fp_s['store'] = [ Mov ]
        self.types = { 'fp': { (self.precision, 1): fp_s } }

    