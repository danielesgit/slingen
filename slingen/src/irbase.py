'''
Created on Apr 18, 2012

@author: danieles
'''

import sys
from itertools import product
from copy import deepcopy
from itertools import count
import time
from sympy import sympify

from islpy import Map, Set, dim_type

from src.dsls.ll import scalar_block, Scalar, Matrix, expr_is_bounded_over_domain, get_expr_bound_over_domain
from src.binding import getReference, BindingTable
from src.physical import Scalars, Array
# from src.binding import *
# from src.physical import *


class Inst(object):
    def __init__(self):
        super(Inst, self).__init__()
        self.env = {} # used by abstract interpretation
        self.bounds = {} # used by SLE
        self.iterSetIds = None
        self.iterSet = None

    def unparse(self, indent):
        return self.printInst(indent)
        
    def printInst(self, indent):
        return indent + "InstBase"
    
    def align(self, analysis):
        return self
    
    def setIterSet(self, indices, iterSet):
        self.iterSet = iterSet
        self.iterSetIds = indices
            
    def __repr__(self):
        return self.printInst("")

class Comment(Inst):
    def __init__(self, txt):
        super(Comment, self).__init__()
        self.txt = txt

#     def replaceRefs(self, refMap):
#         return self
    
    def unparse(self, indent):
        return "\n" + indent + "// " + self.txt

    def printInst(self, indent):
        return indent + "Comment( " + self.txt + " )"

class DebugPrint(Inst):
    def __init__(self, args):
        Inst.__init__(self)
        self.args = args
    
    def unparse(self, indent):
        fulllist = ["cout"] + self.args + ["endl"]
        inst = " << ".join(fulllist)
        full =  indent + "#ifdef DBG\n"
        full += indent + inst + ";\n"
        full += indent + "#endif\n"
        return full

    def printInst(self, indent):
        return indent + "DebugPrint( " + self.args + " )"

class Statement(Inst):
    def __init__(self):
        super(Statement, self).__init__()
        self.srcs = []

    def getSrc(self):
        '''Go down the Inst tree starting from self and gather all the Access (load) instructions (leaves of the tree).''' 
        if isinstance(self, Access):
            return [ self ]
        res = []
        for src in self.srcs:
            res += src.getSrc()
        return res
#         return self.src0.getSrc() + self.src1.getSrc()

    def replaceRefs(self, refMap):
        if isinstance(self, Access):
            return refMap[ self ]
        for i in range(len(self.srcs)):
            self.srcs[i] = self.srcs[i].replaceRefs(refMap) 
#         self.src0 = self.src0.replaceRefs(refMap)
#         self.src1 = self.src1.replaceRefs(refMap)
        return self
    
    def replaceRef(self, old, new):
        if isinstance(self, Access):
            return new if self == old else self
        if id(self) == id(new):
            return self
        for i in range(len(self.srcs)):
            self.srcs[i] = self.srcs[i].replaceRef(old, new) 
#         self.src0 = self.src0.replaceRef(old, new)
#         self.src1 = self.src1.replaceRef(old, new)
        return self
    
    def align(self, analysis):
        ''' Return the same statement with all sources replaced by their aligned version. '''
        for i, source in enumerate(self.srcs):
            self.srcs[i] = source.align(analysis)
        return self

    def setIterSet(self, indices, iterSet):
        super(Statement, self).setIterSet(indices, iterSet)
        for src in self.srcs:
            src.setIterSet(indices, iterSet)
            
class RValue(Statement):
    def __init__(self):
        super(RValue, self).__init__()

class LValue(RValue):
    def __init__(self):
        super(LValue, self).__init__()

class V(RValue):
    def __init__(self, value):
        super(V, self).__init__()
        self.value = value
    
    def computeSym(self, nameDict):
        return [ sympify(self.value) ]
    
    def unparse(self, indent):
        return indent + str(self.value) 

    def printInst(self, indent):
        return "V( " + str(self.value) + " )"
    
    def __eq__(self, other):
        return self.value == other.value
        
    def __hash__(self):
        return hash(self.value)

class Pointer(object):
    def __init__(self, matAt):
        super(Pointer, self).__init__()
        self.mat = matAt[0]
        self.at = matAt[1]
        self.tryToCache()
    
    def __deepcopy__(self, memo):
        return self
        
    @property
    def ref(self):
        if self._ref is None:
            self.tryToCache()
        return self._ref

    @property
    def linIdx(self):
        if self._ref is None:
            self.tryToCache()
        return self._linIdx
    
    def tryToCache(self):
        self._ref = getReference(icode, self.mat)
        self._linIdx = None if self._ref is None else self._ref.getLinIdx(self.at)
        self.whatRef = None if self._ref is None else self._ref.physLayout
        
    def computeSym(self, nameDict):
        return self.mat.name
    
    def unparse(self, indent):
#         ref = getReference(icode, self.mat)
        if self._ref is None:
            self.tryToCache()
        val = self._ref.pointerAt(self.at)
        return indent + val 
    
    def isRefTo(self, PhysLayout):
#         return isinstance(getReference(icode, self.mat), Reference.whatRef(PhysLayout))
        if self._ref is None:
            self.tryToCache()
#         return isinstance(self.ref, Reference.whatRef(PhysLayout))
        return isinstance(self.whatRef, PhysLayout)
    
    def isRefToParam(self, PhysLayout):
#         ref = getReference(icode, self.mat)
        if self._ref is None:
            self.tryToCache()
#         return isinstance(self.ref, Reference.whatRef(PhysLayout)) and self.ref.physLayout.isParam
        return isinstance(self.whatRef, PhysLayout) and self.whatRef.isParam

    def getMat(self):
        return self.mat
    
    def getAt(self):
        return self.at
        
    def getPhysAtPair(self):
#         selfRef = getReference(icode, self.mat)
        if self._ref is None:
            self.tryToCache()
        if self._ref is None:
            return None
        return (self._ref.physLayout, self.at)
        
    def printInst(self, indent):
#         return indent + "Pointer( " + str(getReference(icode, self.mat)) + ", " + str(self.at) + " )"
        if self._ref is None:
            self.tryToCache()
        return indent + "Pointer( " + str(self._ref) + ", " + str(self.at) + " )"
    
    def eqValueFirst(self, other):
        if not isinstance(other, Pointer): return False
        # get physical reference of self.mat and other.getMat()
#         selfRef = getReference(icode, self.mat)
#         otherRef = getReference(icode, other.getMat())
        if self._ref is None:
            self.tryToCache()
        if other._ref is None:
            other.tryToCache()
        if self._ref is None or other._ref is None:
            return self == other
#            return False
        return self._ref.physLayout == other._ref.physLayout and self.at == other.getAt() 

    def full_inclusion(self, other, mrmaps=None, not_using_masks=None):

        if not self.overlap(other, mrmaps, not_using_masks):
            return False

        if mrmaps is None: mrmaps = ([0],[0])

        sstart, ostart = self._linIdx, other._linIdx
        
        if ostart - sstart >= 0:
            return sstart + len(mrmaps[0]) - ostart - len(mrmaps[1])  >= 0
#             return sstart + len(mrmaps[0]) - ostart - len(mrmaps[1])  <= 0
        else:
            return False
    
    def overlap(self, other, mrmaps=None, notum=None):
#         if thresholds is None: thresholds = (1,1)
        if mrmaps is None: mrmaps = ([0],[0])
        if notum is None: notum = ([False]*len(mrmaps[0]),[False]*len(mrmaps[1]))
        if not isinstance(other, Pointer): return False
#         selfRef = getReference(icode, self.mat)
#         otherRef = getReference(icode, other.mat)
        if self._ref is None:
            self.tryToCache()
        if other._ref is None:
            other.tryToCache()
        if self._ref is None or other._ref is None or self._ref.physLayout != other._ref.physLayout:
#             return self == other
            return False
#         sstart, ostart = self.ref.getLinIdx(self.at), other.ref.getLinIdx(other.at)
        sstart, ostart = self._linIdx, other._linIdx
        smo = sstart + len(mrmaps[0]) - ostart
        oms = ostart + len(mrmaps[1]) - sstart
        intersect = smo.is_Number and oms.is_Number and smo > 0 and oms > 0
        if not (isinstance(intersect, bool) and intersect):
            return False
        if sstart - ostart >= 0:
            inf, infmrmap, infnotum = ostart, mrmaps[1], notum[1]
            sup, supmrmap, supnotum = sstart, mrmaps[0], notum[0]
        else:
            inf, infmrmap, infnotum = sstart, mrmaps[0], notum[0]
            sup, supmrmap, supnotum = ostart, mrmaps[1], notum[1]
        lim = inf + len(infmrmap) if (sup + len(supmrmap) - inf - len(infmrmap)) >= 0 else sup + len(supmrmap)     
        ia, ib = sup - inf, lim - inf
        sa, sb = 0, lim - sup
        isoverlapping = any(map(lambda pos: pos[0] >= 0 and pos[1] >= 0 and not pos[2] and pos[2]==pos[3], zip(infmrmap[ia:ib],supmrmap[sa:sb],infnotum[ia:ib],supnotum[sa:sb])))
        return isoverlapping
    
    def __ge__(self, other):
        if not isinstance(other, Pointer): return False
#         selfRef = getReference(icode, self.mat)
#         otherRef = getReference(icode, other.mat)
        if self._ref is None:
            self.tryToCache()
        if other._ref is None:
            other.tryToCache()
        if self._ref is None or other._ref is None:
            return False
#         sstart, ostart = self.ref.getLinIdx(self.at), other.ref.getLinIdx(other.at)
        sstart, ostart = self._linIdx, other._linIdx
        return self._ref.physLayout == other._ref.physLayout and sstart-ostart >= 0

    def __gt__(self, other):
        if not isinstance(other, Pointer): return False
#         selfRef = getReference(icode, self.mat)
#         otherRef = getReference(icode, other.mat)
        if self._ref is None:
            self.tryToCache()
        if other._ref is None:
            other.tryToCache()
        if self._ref is None or other._ref is None:
            return False
#         sstart, ostart = self.ref.getLinIdx(self.at), other.ref.getLinIdx(other.at)
        sstart, ostart = self._linIdx, other._linIdx
        return self._ref.physLayout == other._ref.physLayout and sstart-ostart > 0

    def __lt__(self, other):
        if not isinstance(other, Pointer): return False
#         selfRef = getReference(icode, self.mat)
#         otherRef = getReference(icode, other.mat)
        if self._ref is None:
            self.tryToCache()
        if other._ref is None:
            other.tryToCache()
        if self._ref is None or other._ref is None:
            return False
#         sstart, ostart = self.ref.getLinIdx(self.at), other.ref.getLinIdx(other.at)
        sstart, ostart = self._linIdx, other._linIdx
        return self._ref.physLayout == other._ref.physLayout and sstart-ostart < 0
        
    def __eq__(self, other):
        return isinstance(other, Pointer) and self.mat.name == other.mat.name and self.at == other.at

    def __repr__(self):
        return self.printInst("")
        
class AddressOf(Pointer):
    def __init__(self, access):
#         if isinstance(matAt, list): # Case where [Mat, at] is passed
#             self.matAt = At(matAt)
#             lMatAt = matAt
#         else:
        self.access = access
        matAt = [access.pointer.mat, access.pointer.at]
        super(AddressOf, self).__init__(matAt)
    
    def getType(self):
        return self.access.getType()
    
    def getDeclContext(self):
        return self.access.getDeclContext()
    
    def getDstName(self):
        return self.access.getDstName()
    
    def addToBlackList(self):
        self.access.addToBlackList()
        
    def unparse(self, indent):
        val = self.access.unparse("")
        return indent + "&(" + val + ")" 
    
    def printInst(self, indent):
        return indent + "AddressOf( " + self.access.printInst("") + " )"

class PointerCast(Pointer):
    def __init__(self, newType, pointer):
        super(PointerCast, self).__init__([pointer.mat, pointer.at])
        self.pointer = pointer
        self.newType = newType

#     def computeSym(self, nameDict):
#         return self.pointer.computeSym(nameDict)
#     
#     def isRefTo(self, PhysLayout):
#         return self.pointer.isRefTo(PhysLayout)
#     
#     def isRefToParam(self, PhysLayout):
#         return self.pointer.isRefToParam(PhysLayout)
# 
#     def getMat(self):
#         return self.pointer.getMat()
#     
#     def getAt(self):
#         return self.pointer.getAt()
#         
#     def getPhysAtPair(self):
#         return self.pointer.getPhysAtPair()
#         
#     def eqValueFirst(self, other):
#         return self.pointer.eqValueFirst(other)
# 
#     def overlap(self, other, thresholds=None):
#         return self.pointer.overlap(other, thresholds)
#     
#     def __ge__(self, other):
#         return self.pointer >= other
# 
#     def __gt__(self, other):
#         return self.pointer > other
# 
#     def __lt__(self, other):
#         return self.pointer < other
#         
#     def __eq__(self, other):
#         return self.pointer == other

    def unparse(self, indent):
        return indent + "(" + self.newType + "*)(" + self.pointer.unparse("") + ")" 

    def printInst(self, indent):
        return indent + "PointerCast( " + self.newType + ", " + self.pointer.printInst("") + " )"
    

class Access(object):
    def __init__(self):
        super(Access, self).__init__()
        self.inlen = 0 # deprecated
        self.outlen = 0 # deprecated
        self.reglen = 0
        # mrmap maps memory location to position in (vec)register.
        # Ex. 1, Accessing 3 cons. memory elements inserting them in reverse order in register: [2,1,0] 
        # Ex. 1, Accessing 1 memory element duplicating it for 4 reg. positions: [(0,1,2,3)]
        # Allowed values: i >= 0, or -1 if an element is not mapped to any reg. position   
        self.mrmap = None
        self.not_using_mask = None
        self.pointer = None
        self.horizontal = True
        self.orientation = 'horizontal'
        self.spaceReadMap = None
        self.access2D = None
#     def getSrc(self):
#         return [ self ]

    def eqValueFirst(self, other):
#         return other.outlen == 1 and self.pointer.eqValueFirst(other.pointer)
        eq_orientation = self.horizontal == other.horizontal
        if not eq_orientation:
            non_hor = self if not self.horizontal else other
            eq_orientation = non_hor.isCompact
        return self.reglen == other.reglen and self.mrmap == other.mrmap and eq_orientation and self.pointer.eqValueFirst(other.pointer)
    
    def isRefTo(self, PhysLayout):
        return self.pointer.isRefTo(PhysLayout)
    
    def isRefToParam(self, PhysLayout):
        return self.pointer.isRefToParam(PhysLayout)

#     def replaceRefs(self, refMap):
#         return refMap[ self ]
#     
#     def replaceRef(self, old, new):
#         return new if self == old else self

    def getPhysAtPair(self):
        return self.pointer.getPhysAtPair()

    def getPointerDict(self):
#         return { 'pList': [ self.pointer ], 'th': [self.inlen] }
        ref = getReference(icode, self.pointer.mat)
        l_mrmap = len(self.mrmap)
        corner = (self.pointer.at[0], self.pointer.at[1]+l_mrmap) if self.horizontal else (self.pointer.at[0]+l_mrmap, self.pointer.at[1])
        is_compact = (ref.getLinIdx(corner) - self.pointer.linIdx) == l_mrmap

        if self.horizontal or is_compact:
#             return { 'pList': [ self.pointer ], 'th': [len(self.mrmap)] }
            return { 'pList': [ self.pointer ], 'mrmap': [ self.mrmap ], 'notum': [ self.not_using_mask ] }
        else:
            pointer = self.pointer
            plist = [pointer] + [Pointer((pointer.mat, (pointer.at[0] + i, pointer.at[1]))) for i in range(1, len(self.mrmap))]
            mrmaps = [ [p] for p in self.mrmap ]
            notum = [ [m] for m in self.not_using_mask ]
            return { 'pList': plist, 'mrmap': mrmaps, 'notum': notum }
#             return { 'pList': plist, 'th': [1] * len(self.mrmap)}

    def getMat(self):
        return self.pointer.mat;
    
    def getAt(self):
        return self.pointer.at;

    def full_inclusion(self, other):
        pDictSelf, pDictOther = self.getPointerDict(), other.getPointerDict()
        for pSelf,thSelf,numSelf in zip(pDictSelf['pList'],pDictSelf['mrmap'],pDictSelf['notum']):
            for pOther,thOther,numOther in zip(pDictOther['pList'],pDictOther['mrmap'],pDictOther['notum']):
                if not pSelf.full_inclusion(pOther, (thSelf, thOther), (numSelf,numOther)):
                    return False
        return True

    def overlap(self, other):
        pDictSelf, pDictOther = self.getPointerDict(), other.getPointerDict()
        for pSelf,thSelf,numSelf in zip(pDictSelf['pList'],pDictSelf['mrmap'],pDictSelf['notum']):
            for pOther,thOther,numOther in zip(pDictOther['pList'],pDictOther['mrmap'],pDictOther['notum']):
                if pSelf.overlap(pOther, (thSelf, thOther), (numSelf,numOther)):
                    return True
        return False

    def intersect(self, other):
        if self.pointer.ref.physLayout == other.pointer.ref.physLayout:
            return not self.lin_access.intersect(other.lin_access).is_empty()
        else:
            return False
    
    def setSpaceReadMap(self, indices, iterSet):
        list_str_pts = []
        pDict = self.getPointerDict()
        for p,mrm,num in zip(pDict['pList'],pDict['mrmap'],pDict['notum']):
            for off,notused in zip(range(len(mrm)),num):
                if not notused:
                    list_str_pts.append('i='+str(p.linIdx) + "+" + str(off))
        str_pts = ' or '.join(list_str_pts)
        strmap = '{['+(','.join(indices))+'] -> [i]: ' + str_pts +'}'
        self.spaceReadMap = Map(strmap)
        self.lin_access = self.spaceReadMap.intersect_domain(iterSet).range() 
        
#         for i in range(len(self.mrmap)):
#             if self.horizontal:
#                 list_str_pts.append('i='+str(self.pointer.at[0])+' and j='+str(self.pointer.at[1]+i))
#             else:
#                 list_str_pts.append('i='+str(self.pointer.at[0]+i)+' and j='+str(self.pointer.at[1]))
#         str_pts = ' or '.join(list_str_pts)
# #         strmap = '{['+(','.join(indices))+'] -> [i,j]: i='+str(self.pointer.at[0])+' and j='+str(self.pointer.at[1])+'}'
#         strmap = '{['+(','.join(indices))+'] -> [i,j]: ' + str_pts +'}'
#         self.spaceReadMap = Map(strmap)
#         self.access2D = self.spaceReadMap.intersect_domain(iterSet).range() 
        
    def __repr__(self):
        return self.printInst("")

class ScaAccess(Access):
    def __init__(self):
        super(Access, self).__init__()
#         self.inlen = 1
#         self.outlen = 1
        self.reglen = 1
        self.mrmap = [ 0 ]
        self.not_using_mask = [False]
        self.zeromask = [0] # A zero-bitmask is meant for marking positions of a - in general - vector register that can be considered zeroed.
                            # It has the length of a register. At any position in the reg we can have either any value (zeromask[pos] == 0) or zero (zeromask[pos] == 1) 
    
    def setZMask(self, zeromask):
        if zeromask is not None:
            for pos in zeromask:
                self.zeromask[pos] = 1

    def getZMask(self):
        return self.zeromask
        
                
#     def eqValueFirst(self, other):
# #         return other.outlen == 1 and self.pointer.eqValueFirst(other.pointer)
#         return self.reglen == other.reglen and self.mrmap == other.mrmap and self.pointer.eqValueFirst(other.pointer)

    def computeSym(self, nameList):
        p = self.pointer.computeSym(nameList)
        return [ sympify(p+'_0') ] 
    
    def __eq__(self, other):
#         if other.outlen > 1: return False
#         return self.pointer == other.pointer
        return self.reglen == other.reglen and self.mrmap == other.mrmap and self.pointer == other.pointer
        
    def __hash__(self):
        return hash((hash("ScaAccess"), self.pointer.mat, self.pointer.at))

class Deref(LValue, ScaAccess):
    def __init__(self, pointer, zeromask=None):
        super(Deref, self).__init__()
        self.setZMask(zeromask)
        self.pointer = pointer

    def unparse(self, indent):
        return indent + "*(" + self.pointer.unparse("") + ")" 
    
    def printInst(self, indent):
        return indent + "Deref( " + self.pointer.printInst("") + " )"
    
    def setIterSet(self, indices, iterSet):
        super(Deref, self).setIterSet(indices, iterSet)
        self.setSpaceReadMap(indices, iterSet)
        
class ScaLoad(LValue, ScaAccess):
    def __init__(self, matAt, zeromask=None):
        super(ScaLoad, self).__init__()
        self.setZMask(zeromask)
        self.pointer = matAt if isinstance(matAt, Pointer) else Pointer(matAt)
        self.horizontal = True
        self.isAligned = False
        
    def unparse(self, indent):
#         ref = getReference(icode, self.pointer.mat)
        lval = self.pointer.ref[self.pointer.at]
        return indent + lval 
    
    def getType(self):
#         selfRef = getReference(icode, self.pointer.mat)
        if self.pointer.ref is None:
            return None
        return self.pointer.ref.physLayout.scalar
    
    def getDeclContext(self):
#         selfRef = getReference(icode, self.pointer.mat)
        if self.pointer.ref is None:
            return None
        return self.pointer.ref.physLayout.declIn
    
    def getDstName(self):
        return self.unparse("")
    
    def addToBlackList(self):
#         selfRef = getReference(icode, self.pointer.mat)
        self.pointer.ref.physLayout.blackList.append(self.pointer.ref[self.pointer.at])

    def setIterSet(self, indices, iterSet):
        super(ScaLoad, self).setIterSet(indices, iterSet)
        self.setSpaceReadMap(indices, iterSet)
        
    def printInst(self, indent):
#         return indent + "ScaLoad( " + str(getReference(icode, self.pointer.mat)) + ", " + str(self.pointer.at) + " )"
        return indent + "ScaLoad( " + str(self.pointer.ref) + ", " + str(self.pointer.at) + " )"

class ScaDest(ScaAccess): # deprecated (very likely)
    def __init__(self, pointer, zeromask=None):
        super(ScaDest, self).__init__()
        self.setZMask(zeromask)
        self.pointer = pointer

    #The two following replace must be implemented as ScaDest doesn't inherit from Statement
    def replaceRefs(self, refMap):
        return refMap[ self ]
    
    def replaceRef(self, old, new):
        return new if self == old else self

    def getType(self):
        return self.pointer.getType()
    
    def getDeclContext(self):
        return self.pointer.getDeclContext()
    
    def getDstName(self):
        return self.pointer.getDstName()

    def addToBlackList(self):
        self.pointer.addToBlackList()

    def unparse(self, indent):
        return self.pointer.unparse("")

    def printInst(self, indent):
        return indent + "ScaDest( " + self.pointer.printInst("") + " )"

class VecAccess(Access):
    def __init__(self):
        super(VecAccess, self).__init__()
    
    def getAlignedVersion(self):
        return self

class VecDest(VecAccess):
    def __init__(self, pointer, reglen, mrmap, horizontal=True, isCompact=True, isCorner=False, isAligned=False):
        super(VecDest, self).__init__()
        self.reglen = reglen
        self.mrmap = mrmap
        self.not_using_mask = [False]*len(mrmap)
        self.pointer = pointer
        self.horizontal = horizontal
        self.orientation = 'horizontal' if horizontal else 'vertical'
        self.isCompact = isCompact
        self.isCorner = isCorner
        self.isAligned = isAligned
    
    #The two following replace must be implemented as VecDest doesn't inherit from Statement
    def replaceRefs(self, refMap):
        return refMap[ self ]
    
    def replaceRef(self, old, new):
        return new if self == old else self

    def unparse(self, indent):
        return self.pointer.unparse("")
    
    def printInst(self, indent):
        return indent + "VecDest( " + self.pointer.printInst("") + ", " + str(self.mrmap) + ", " + str(self.not_using_mask) + ", " + self.orientation + " )"

    def __eq__(self, other):
#         return isinstance(other, VecDest) and self.inlen == other.inlen and self.outlen == other.outlen and self.pointer == other.pointer and self.horizontal == other.horizontal
        return isinstance(other, VecDest) and self.reglen == other.reglen and self.mrmap == other.mrmap and self.pointer == other.pointer and (self.horizontal == other.horizontal or self.isCompact and other.isCompact)
    
    def __hash__(self):
        return hash((hash("VecDest"), self.pointer.mat, self.pointer.at, tuple(self.mrmap), self.orientation))

class PointerDest(Access):
    def __init__(self, pointer, horizontal=True, isCompact=True, isCorner=False, isAligned=False):
        super(PointerDest, self).__init__()
        self.pointer = pointer
        self.horizontal = horizontal
        self.orientation = 'horizontal' if horizontal else 'vertical'
        self.isCompact = isCompact
        self.isCorner = isCorner
        self.isAligned = isAligned
    
    #The two following replace must be implemented as VecDest doesn't inherit from Statement
    def replaceRefs(self, refMap):
        return refMap[ self ]
    
    def replaceRef(self, old, new):
        return new if self == old else self

    def unparse(self, indent):
        return self.pointer.unparse("")
    
    def printInst(self, indent):
        return indent + "PointerDest( " + self.pointer.printInst("") + ", " + self.orientation + " )"

    def __eq__(self, other):
        return isinstance(other, PointerDest) and self.inlen == other.inlen and self.outlen == other.outlen and self.pointer == other.pointer and self.horizontal == other.horizontal
    
    def __hash__(self):
        return hash((hash("PointerDest"), self.pointer.mat, self.pointer.at, self.orientation))

class MovStatement(Statement):
    def __init__(self):
        super(MovStatement, self).__init__()    
        self.dst = None
#         self.slen = 0
#         self.dlen = 0
        
    def getDst(self):
        return self.dst

    def getRHS(self):
        return self.srcs[0]

    def replaceRefs(self, refMap):
        self.srcs[0] = self.srcs[0].replaceRefs(refMap)
        self.dst = self.dst.replaceRefs(refMap)
        return self

    def replaceInLHS(self, old, new):
        self.dst = self.dst.replaceRef(old, new)
        return self
        
    def replaceInRHS(self, old, new):
        if new is not None:
            self.srcs[0] = self.srcs[0].replaceRef(old, new)
            if self.iterSetIds is not None:
                self.srcs[0].setIterSet(self.iterSetIds, self.iterSet)

    def setIterSet(self, indices, iterSet):
        super(MovStatement, self).setIterSet(indices, iterSet)
        self.dst.setSpaceReadMap(indices, iterSet)
        
    @staticmethod
    def canStore(regnu, memnu, horizontal=True, isAligned=False):
        return False

    @staticmethod
    def getStore(src, dst):
        return None

class Mov(MovStatement):
    def __init__(self, src, dst):
        super(Mov, self).__init__()
        self.dst = ScaLoad(dst.pointer) if isinstance(dst, ScaDest) else dst
        self.srcs += [ src ]
#         self.slen = 1
#         self.dlen = 1

    def computeSym(self, nameList):
        return self.srcs[0].computeSym(nameList)
    
    def unparse(self, indent):
        return indent + self.dst.unparse("") + " = " + self.srcs[0].unparse("") + ";"
    
    def printInst(self, indent):
        return indent + "Mov( " + self.srcs[0].printInst("") + ", " + self.dst.printInst("") + " )"

    @staticmethod
    def canStore(reglen, mrmap, horizontal=True, isAligned=False):
        return reglen == 1 and mrmap == [ 0 ] # This is the only reg-mem mapping available when Mov is considered as a store  
    
    @staticmethod
    def getStore(src, dst):
        return Mov(src, dst)

########################################################################################################
#--------------------------------------------- Operators  ---------------------------------------------#
########################################################################################################

class Equals(RValue):
    def __init__(self, leftSrc, rightSrc):
        super(Equals, self).__init__()
        self.srcs.extend([leftSrc, rightSrc])
    
#     def computeSym(self, nameDict):
#         return [ sympify(self.value) ]
    
    def unparse(self, indent):
        return '%s == %s' % (self.srcs[0].unparse(indent), self.srcs[1].unparse(''))

    def printInst(self, indent):
        return '%sEquals( %s, %s )' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''))
    
    def __eq__(self, other):
        return self.srcs[0] == other.srcs[0] and self.srcs[1] == other.srcs[1]
        
    def __hash__(self):
        return hash(hash('Equals'), self.srcs[0], self.srcs[1])

class BoolAnd(RValue):
    def __init__(self, srcs):
        super(BoolAnd, self).__init__()
        self.srcs.extend(srcs)
    
#     def computeSym(self, nameDict):
#         return [ sympify(self.value) ]
    
    def unparse(self, indent):
        return '%s%s' % (indent, '  &&  '.join(src.unparse('') for src in self.srcs))

    def printInst(self, indent):
        return '%sBoolAnd( %s )' % (indent, ', '.join(src.printInst('') for src in self.srcs))
    
    def __eq__(self, other):
        return len(self.srcs) == len(other.srcs) and all(selfsrc == othersrc for selfsrc, othersrc in zip(self.srcs, other.srcs))
        
    def __hash__(self):
        return hash(hash('BoolAnd'), tuple(self.srcs))
    
class Mod(RValue):
    def __init__(self, leftSrc, rightSrc):
        super(Mod, self).__init__()
        self.srcs.extend([leftSrc, rightSrc])
    
#     def computeSym(self, nameDict):
#         return [ sympify(self.value) ]
    
    def unparse(self, indent):
        return '%s %% %s' % (self.srcs[0].unparse(indent), self.srcs[1].unparse(''))

    def printInst(self, indent):
        return '%sMod( %s, %s )' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''))
    
    def __eq__(self, other):
        return self.srcs[0] == other.srcs[0] and self.srcs[1] == other.srcs[1]
        
    def __hash__(self):
        return hash(hash('Mod'), self.srcs[0], self.srcs[1])

##########################################################################################################
#--------------------------------------------- New Context  ---------------------------------------------#    
##########################################################################################################

class CIRContext(object):
    def __init__(self):
        super(CIRContext, self).__init__()
        self.declare = []
        self.flatList = []
        self.precomp = []
        self.blocks = []
        self.postcomp = []
        self.bindingTable = BindingTable()
    
    def flatten(self, iblock, counter, contexts):
        return [ iblock ]
    
    def isBound(self, matrix):
        return self.bindingTable.isBound(matrix)
    
    def isIR(self):
        return isinstance(self, IR)
    
    def getPhysicalLayout(self, matrix):
        return self.bindingTable.getPhysicalLayout(matrix)
    
    def replacePhysicalLayout(self, oldPhys, newPhys):
        self.bindingTable.replacePhysicalLayout(oldPhys, newPhys)
        
    def addToFlatList(self, listIbs, contexts):
        self.flatList += listIbs
        for ib in listIbs:
            ib.contexts += contexts
        
    def align(self, analysis):
        ''' Replace all instructions of the context with their aligned version. '''
        for ib in self.flatList:
            for instr in ib.instructions:
                instr.align(analysis)
        return self

class SingleContext(CIRContext):
    def __init__(self):
        super(SingleContext, self).__init__()
        
class NewContextInst(Inst, SingleContext):
    def __init__(self):
        super(NewContextInst, self).__init__()

class ForLoop(NewContextInst):
    def __init__(self, idx, B, E, S, body=None, precomp=None, postcomp=None, idxDecl=1):
        super(ForLoop, self).__init__()
        self.idx = idx
        self.idxDecl = idxDecl # 0 don't declare; 1 declare in loop; 2 declare outside loop
        self.B = B      # start
        self.E = E      # end
        self.S = S      # step
        if precomp is not None:
            self.precomp = precomp
        if body is not None:
            self.blocks = body
        if postcomp is not None:
            self.postcomp = postcomp
        self.timesTaken = 0 # used by abstract interpretation in order to apply widening
    
    def __deepcopy__(self, memo):
        newone = type(self)(self.idx, self.B, self.E, self.S, self.blocks, self.precomp, self.postcomp)
        newone.flatList = deepcopy(self.flatList, memo)
        newone.bindingTable = self.bindingTable
        newone.declare = deepcopy(self.declare, memo)
        return newone
        
    def flatten(self, forBlock, counter, contexts):
        contexts.append(self)
        init = IBlock(counter.next())
        init.preds.append(forBlock)
        forBlock.succs.append(init)
        check = IBlock(counter.next())
        check.preds.append(init)
        init.succs.append(check)
        self.addToFlatList([ check ], contexts)
        body = IBlock(counter.next())
        body.preds.append(check)
        check.succs.append(body)
        self.addToFlatList([ body ], contexts)
        current = body
        for b in self.precomp + self.blocks + self.postcomp:
            for i in b.instructions:
                if isinstance(i, NewContextInst):
                    nextBlk = i.flatten(current, counter, contexts) # if i is For can return [init, check]
                    if not current.isEmpty():
                        self.addToFlatList([ nextBlk[0] ], contexts) # Insert init before "for" block
                        tblock = IBlock(counter.next())
                        current.succs.append(tblock)
                        tblock.preds.append(current)
                        tblock.succs.append(nextBlk[0])
                        nextBlk[0].preds.append(tblock)
                        current.succs.remove(nextBlk[0])
                        nextBlk[0].preds.remove(current)
                        current = tblock
                        self.addToFlatList([ current ], contexts)
                    else: #Insert init before "for" block
                        self.flatList.insert( len(self.flatList)-1, nextBlk[0] )
                        nextBlk[0].contexts += contexts
                    current.instructions += [ i ]
                    tblock = IBlock(counter.next())
                    nextBlk[1].succs.append(tblock)
                    tblock.preds.append(nextBlk[1])
                    current = tblock
                    self.addToFlatList([ current ], contexts)
                elif isinstance(i, MultiContextInst):
                    nextBlks = i.flatten(current, counter, contexts) # if i is If returns [ preIfBlk, IfBlk, MergeBlk ]
                    self.addToFlatList(nextBlks, contexts)
                    nextBlks[1].instructions += [ i ]
                    current = nextBlks[2]
                else:
                    current.instructions += [ i ]
        if current.isEmpty():
            incVar = current
        else:
            incVar = IBlock(counter.next())
            self.addToFlatList([ incVar ], contexts)
            current.succs.append(incVar)
            incVar.preds.append(current)
        incVar.succs.append(check)
        check.preds.append(incVar)
        contexts.remove(self)
        return [ init, check ]
        

    def printInst(self, indent):
        res = indent + "ForLoop( " + str(self.idx) + ", [" + str(self.B) + "," + str(self.E) + "," + str(self.S) + "] )\n"
        for ib in self.flatList:
            res += indent + "  { " + repr(ib) + "\n"
            for i in ib.phi + ib.instructions:
                res += i.printInst(indent+"  ") + "\n"
            res += indent + "  } " + repr(ib) + "\n"
        return res
    
    def unparse(self, indent):
        res = "\n"
        if self.idxDecl == 2:
            res += indent + "int " + str(self.idx) + ";\n"
            res += indent + "for( ; "
        elif self.idxDecl == 1 and self.B is not None:
#             begin = use_floord_ceild(self.B)
            begin = self.B
            res += indent + "for( int " + str(self.idx) + " = " + str(begin) + "; "
        else:
            res += indent + "for( ; "
        if self.E is not None:
#             end = use_floord_ceild(self.E)
            end = self.E
            res += str(self.idx) + " <= " + str(end) + "; "
        else:
            res += " ; "
        strinc = "+" if self.S == 1 else "=" + str( self.S )
        res += str(self.idx) + "+" + strinc + " ) {\n"
        if len(self.declare) > 0:
            res += indent + "\n"            
            for v in self.declare:
                res += v.declare(indent + "  ")
            res += indent + "\n"            
#        for block in self.precomp:
#            for i in block.instructions:
#                res += i.unparse(indent + "  ") + "\n"
#        for block in self.blocks:
#            for i in block.instructions:
#                res += i.unparse(indent + "  ") + "\n"
#        for block in self.postcomp:
#            for i in block.instructions:
#                res += i.unparse(indent + "  ") + "\n"
        for block in self.flatList:
            for i in block.instructions:
                res += i.unparse(indent + "  ") + "\n"
        res += indent + "}"            
        return res
    
    def align(self, analysis):
        CIRContext.align(self, analysis)
        return self
    
class MultiContext(object):
    def __init__(self):
        super(MultiContext, self).__init__()
        self.contexts = []
        
class MultiContextInst(Inst, MultiContext):
    def __init__(self):
        super(MultiContextInst, self).__init__()

class If(MultiContextInst):
    def __init__(self, contexts, conditions):
        super(MultiContextInst, self).__init__()
        if (len(contexts) - len(conditions)) not in [0, 1] or len(conditions) == 0:
            raise ValueError('Lengths of contexts (%d) and conditions(%d) lists don\'t match' % (len(contexts), len(conditions)))
        self.contexts = contexts
        self.conditions = conditions
    
    def __deepcopy__(self, memo):
        newcontexts = deepcopy(self.contexts, memo)
        newconditions = deepcopy(self.conditions, memo)
        newone = type(self)(newcontexts, newconditions)
        return newone

    def flattenPerContext(self, context, contexts, condBlk, counter):
        current = IBlock(counter.next())
        current.preds.append(condBlk)
        condBlk.succs.append(current)
        context.addToFlatList([ current ], contexts)
        for b in context.blocks:
            for i in b.instructions:
                if isinstance(i, NewContextInst):
                    nextBlk = i.flatten(current, counter, contexts) # if i is For can return [init, check]
                    if not current.isEmpty():
                        context.addToFlatList([ nextBlk[0] ], contexts) # Insert init before "for" block
                        tblock = IBlock(counter.next())
                        current.succs.append(tblock)
                        tblock.preds.append(current)
                        tblock.succs.append(nextBlk[0])
                        nextBlk[0].preds.append(tblock)
                        current.succs.remove(nextBlk[0])
                        nextBlk[0].preds.remove(current)
                        current = tblock
                        context.addToFlatList([ current ], contexts)
                    else: #Insert init before "for" block
                        context.flatList.insert( len(context.flatList)-1, nextBlk[0] )
                        nextBlk[0].contexts += contexts
                    current.instructions += [ i ]
                    tblock = IBlock(counter.next())
                    nextBlk[1].succs.append(tblock)
                    tblock.preds.append(nextBlk[1])
                    current = tblock
                    context.addToFlatList([ current ], contexts)
                elif isinstance(i, MultiContextInst):
                    nextBlks = i.flatten(current, counter, contexts) # if i is If returns [ preIfBlk, IfBlk, MergeBlk ]
                    context.addToFlatList(nextBlks, contexts)
                    nextBlks[1].instructions += [ i ]
                    current = nextBlks[2]
                else:
                    current.instructions += [ i ]
        return current
        
    def flatten(self, outerBlock, counter, contexts):
        preIfBlock = IBlock(counter.next())
        outerBlock.succs.append(preIfBlock)
        preIfBlock.preds.append(outerBlock)
        ifBlock = IBlock(counter.next())
        preIfBlock.succs.append(ifBlock)
        ifBlock.preds.append(preIfBlock)
        newCond = ifBlock
        condiBlock = None
        exitsList = []
        for context in self.contexts[:len(self.conditions)]:
            contexts.append(context)
            if condiBlock is not None:
                condiBlock.succs.append(newCond)
                newCond.preds.append(condiBlock)
                context.addToFlatList([ newCond ], contexts)
            condiBlock = newCond
            exitBlk = self.flattenPerContext(context, contexts, condiBlock, counter)
            exitsList.append(exitBlk)
            newCond = IBlock(counter.next())
            contexts.remove(context)
        if self.contexts[len(self.conditions):]:
            contexts.append(self.contexts[-1])
            exitBlk = self.flattenPerContext(context, contexts, condiBlock, counter)
            exitsList.append(exitBlk)
            contexts.remove(self.contexts[-1])
        else:
            exitsList.append(preIfBlock)
        mergeBlock = IBlock(counter.next())
        for blk in exitsList:
            blk.succs.append(mergeBlock)
            mergeBlock.preds.append(blk)
        
        return [preIfBlock, ifBlock, mergeBlock]

    def unparse(self, indent):
        branchBodies = []
        for context in self.contexts:
            body = ''
            if len(context.declare) > 0:
                body += indent + "\n"            
            for v in context.declare:
                body += v.declare(indent + "  ")
            body += indent + "\n"            
            for block in context.flatList:
                for i in block.instructions:
                    body += i.unparse(indent + "  ") + "\n"
            branchBodies.append(body)
        conditions = []
        for cond in self.conditions:
            conditions.append(str(cond))
        res = '%sif ( %s ) {\n%s\n' % (indent, str(conditions[0]), branchBodies[0])
        for branchBody, condition in zip(branchBodies[1:], conditions[1:]):
            res += '%s} else if ( %s ) {\n%s\n' % (indent, str(condition), branchBody)
        if len(branchBodies) > len(conditions):
            res += '%s} else {\n%s\n' % (indent, branchBodies[-1])
        res += indent + "}"            
        return res
        
#     def unparse(self, indent): Original method working with abstractint
#         branchBodies = []
#         for context in self.contexts:
#             body = ''
#             if len(context.declare) > 0:
#                 body += indent + "\n"            
#             for v in context.declare:
#                 body += v.declare(indent + "  ")
#             body += indent + "\n"            
#             for block in context.flatList:
#                 for i in block.instructions:
#                     body += i.unparse(indent + "  ") + "\n"
#             branchBodies.append(body)
#              
#         res = '%sif ( %s ) {\n%s\n' % (indent, self.conditions[0].unparse(''), branchBodies[0])
#         for branchBody, condition in zip(branchBodies[1:], self.conditions[1:]):
#             res += '%s} else if ( %s ) {\n%s\n' % (indent, condition.unparse(''), branchBody)
#         if len(branchBodies) > len(self.conditions):
#             res += '%s} else {\n%s\n' % (indent, branchBodies[-1])
#         res += indent + "}"            
#         return res
    
    def align(self, analysis):
        for context in self.contexts: 
            context.align(analysis)
        return self

########################################################################################

class Phi(RValue):
    def __init__(self, srcs):
        self.srcs = [ (ScaLoad(src.pointer) if isinstance(src, ScaDest) else src) for src in srcs ]
        
    
#     def getSrc(self):
#         return self.srcs
#     
#     def replaceRefs(self, refMap):
#         for i in range(len(self.srcs)):
#             self.srcs[i] = self.srcs[i].replaceRefs(refMap)
#         return self

    def getRefByPos(self, pos):
        return self.srcs[pos]
    
    def replaceRefByPos(self, pos, deref):
        self.srcs[pos] = deref

    def printInst(self, indent):
        res = indent + "PHI( " + self.srcs[0].printInst("") 
        for src in self.srcs[1:]:
            res += ", " + src.printInst("")
        res += " )"
        return res

###################################################################################

def sa(elem):
    '''
    Scalar Access to elements of a matrix 
    '''
    if isinstance(elem, list):
        return ScaLoad(elem)
    else:
        return V(elem)

###################################################################################

showingCFG = False

def groupByType(atList):
    vLists = {}
    Q = [ v for v in atList ]
    while len(Q) > 0:
        v = Q[0]
        vtype = v.getType()
        vLists[vtype] = [ v for v in Q if v.getType() == vtype ]
        for v in vLists[vtype]:
            Q.remove(v)
    return vLists

class IBlock(object):
    def __init__(self, n=None, isEntry=False, isExit=False):
        self.contexts=[]
        self.instructions = []
        self.preds = []
        self.succs = []
        self.dtChildren = []
        self.isEntry = isEntry
        self.isExit = isExit
        self.n = str(id(self)) if n is None else n
        self.pn = None # Postorder Number
        self.phi = [] #List of Phi-Functions
        
    def isEmpty(self):
        return len(self.instructions) == 0
    
    def getDstRefsTo(self, PhysLayout):
        res = []
        for i in self.phi + self.instructions:
            if isinstance(i, Statement):
                res += filter(lambda x: x.isRefTo(PhysLayout), [ i.getDst() ] )
        return res
    
    def getDstNoDupRefsTo(self, PhysLayout):
#        return list(set(self.getDstRefsTo(PhysLayout)))
        refsTo = self.getDstRefsTo(PhysLayout)
        res = []
        for r in refsTo:
            if not any(map(lambda rr: rr.eqValueFirst(r), res)):
                res.append(r)
        return res

    def getSrcRefsTo(self, PhysLayout):
        res = []
        for i in self.phi + self.instructions:
            if isinstance(i, Statement):
                res += filter(lambda x: x.isRefTo(PhysLayout), i.getSrc())
        return res
    
    def getSrcNoDupRefsTo(self, PhysLayout):
#        return list(set(self.getSrcRefsTo(PhysLayout)))
        refsTo = self.getSrcRefsTo(PhysLayout)
        res = []
        for r in refsTo:
            if not any(map(lambda rr: rr.eqValueFirst(r), res)):
                res.append(r)
        return res
    
#    def getNoDupRefsTo(self, PhysLayout):
#        return list(set(self.getSrcRefsTo(PhysLayout) + self.getDstRefsTo(PhysLayout)))

    def getDstRefsToWithLine(self, PhysLayout, line):
        res = []
        l = list(line) + [0]
        for i in self.instructions:
            if isinstance(i, Statement):
                refs = filter(lambda x: x.isRefTo(PhysLayout), [ i.getDst() ] )
                refsWithLine = zip([tuple(l)]*len(refs), refs)
                res += refsWithLine
            l[-1] += 1
        return res
    
    def getDstNoDupRefsToWithLine(self, PhysLayout, line, refsTo=None):
#        return list(set(self.getDstRefsTo(PhysLayout)))
        if not refsTo:
            refsTo = self.getDstRefsToWithLine(PhysLayout, line)
        res = []
        for r in refsTo:
            found_ref = filter(lambda rr: rr[1].eqValueFirst(r[1]), res)
            if not found_ref:
#             if not any(map(lambda rr: rr[1].eqValueFirst(r[1]), res)):
                res.append(list(r)+[ r[0] ]) # To include first and last pos. Last pos used to sort dsts for redundancy
            else:
                found_ref[-1][2] = r[0]
        return res

    def getSrcRefsToWithLine(self, PhysLayout, line):
        res = []
        l = list(line) + [0]
        for i in self.instructions:
            if isinstance(i, Statement):
                refs = filter(lambda x: x.isRefTo(PhysLayout), i.getSrc())
                refsWithLine = zip([tuple(l)]*len(refs), refs)
                res += refsWithLine
            l[-1] += 1
        return res
    
    def getSrcNoDupRefsToWithLine(self, PhysLayout, line):
#        return list(set(self.getSrcRefsTo(PhysLayout)))
        refsTo = self.getSrcRefsToWithLine(PhysLayout, line)
        res = []
        for r in refsTo:
            found_ref = filter(lambda rr: rr[1].eqValueFirst(r[1]), res)
#             if not any(map(lambda rr: rr[1].eqValueFirst(r[1]), res)):
            if not found_ref:
#                 res.append(r)
                res.append(list(r)+[ r[0] ]) # To include first and last pos.
            else:
                found_ref[-1][2] = r[0]
        return res
    
    def joinHeterogeneousRAW(self, PhysLayout, ctxMap, opts, poly_info=None, dsts=None):
        # get the destinations that refer to the physical layout from all the Statements in the current block
        # (a destination can be either a ScaLoad or a VecDest)
        dsts = [] if dsts is None else dsts
        dsts = dsts + self.getDstRefsToWithLine(PhysLayout, opts['line']) # dsts : [(line, dest)]
        # get all the destination array accesses that exist in the current context map
        ctxDsts = ctxMap.getDstList() # ctxDsts : [(pos, dest, last pos)]
#         replacer = LoadReplacer(opts)
        replacer = opts['loadreplacer']
        rep = [] # here we keep all the dsts that we will try to replace
        for i in range(len(self.instructions)):
            line = tuple(list(opts['line']) + [i])
            inst = self.instructions[i]
            if isinstance(inst, MovStatement):
                # for each MovStatement (vec store instruction) get all the sources (vec load instructions) that refer to
                # physical entities
                srcs = filter(lambda x: x.isRefTo(PhysLayout), inst.getSrc())
                for src in srcs:
#                     if src.pointer._ref.physLayout.name == 'A' and src.pointer.at == (5,6) and src.mrmap == [0,1]:
#                         pass
                    j = 0
                    lowbound = tuple(list(opts['line']) + [0])
                    eq = False
                    # for each src check if there is a dst before it that refers to the same physical entity or overlaps with it
                    # in the first case we will replace with scalars
                    # in the second case we will try to use the loadReplacer
                    # we are interested in the last dst that writes to our source (that's what lowbound is for) 
                    same_phys_dsts = filter(lambda tpl: tpl[1].pointer._ref.physLayout == src.pointer._ref.physLayout, dsts)
                    while j < len(same_phys_dsts) and same_phys_dsts[j][0] > lowbound and same_phys_dsts[j][0] < line:
                        if src.eqValueFirst(same_phys_dsts[j][1]): # equal entities
                            del rep[:]
                            lowbound = same_phys_dsts[j][0]
                            eq = True
#                         elif src.overlap(dsts[j][1]):
                        elif src.overlap(same_phys_dsts[j][1]) and not any(map(lambda dinrep: dinrep[1].eqValueFirst(same_phys_dsts[j][1]), rep)):
                            fully_inc_prev_dsts = filter(lambda dinrep: same_phys_dsts[j][1].full_inclusion(dinrep[1]), rep)
                            for dst in fully_inc_prev_dsts:
                                rep.remove(dst)
                            # entities overlap and there is no equal dst already in rep => add dst in rep in order to be replaced later 
                            rep.append(same_phys_dsts[j]) # Store ref to tuple
                            eq = False
                        j += 1
                    rep, src_uncovered = drop_redundant_dsts_to_same_src(rep, src, poly_info)
                    ctx_rep = [] 
#                     if ((not rep and not eq) or src_uncovered) and ctxDsts:
                    if not eq and src_uncovered and ctxDsts:
                        ctx_same_phys_dsts = filter(lambda tpl: tpl[1].pointer._ref.physLayout == src.pointer._ref.physLayout, ctxDsts)
                        # With dsts coming from context we consider overlaps starting from last uses (2nd pos stored in tuples)
                        # Above we don't use this with dsts from current block as intermediate uses before the src 
                        # we want to replace wouldn't be taken into account.
                        ctx_same_phys_dsts.sort(key=lambda t: t[2], reverse=True)
                        for d in ctx_same_phys_dsts:
                            if src.eqValueFirst(d[1]):
                                ctx_rep.append((d[2], d[1]))
                                break
#                                 del ctx_rep[:] # if we have already replaced src with a scalar, we don't need to loadReplace anything 
                            elif src.overlap(d[1]): # and not any(map(lambda dinrep: dinrep[1].eqValueFirst(d[1]), rep)):
                                ctx_rep.append((d[2], d[1])) # Store ref to tuple
                        ctx_rep.sort(key=lambda t: t[0], reverse=False)
                    rep, _ = drop_redundant_dsts_to_same_src(ctx_rep+rep, src, poly_info) 
                    if len(rep) > 0: # if there is something to replace
                        try:
                            inst.replaceInRHS(src, replacer.replace(src, rep, inst.bounds))
                        except Exception as e:
                            print e
                            ld = src.printInst('')
                            sList = sorted(rep, key=lambda t: t[0]) # sort by pointer (lower -> higher)
#                             sts = str([(s[1].reglen, s[1].mrmap) for s in sList])
                            sts = str(sList)
                            raise Exception('It seems that the LoadReplacer doesn\'t support the replacement of:\n%s\n after the stores:\n%s' % (ld, sts))
                    del rep[:]
        return dsts
        
    def markExit(self):
        self.isExit = True
    
    def __lt__(self, other):
        return self.pn < other.pn
    
    def shortStr(self):
        if self.isEntry:
            return " Entry"
        elif self.isExit:
            return " Exit"
        return "IB" + str(self.n)# + "(PN=" + str(self.pn) + ")"
    
    def verbStr(self):
#        return str(self.instructions)
        res = "---------------------------------------\n"
        res += "IBlock " + str(self.n)        
        if self.isEntry:
            res += " (Entry)"
        elif self.isExit:
            res += " (Exit)"
        res += "\nPreds: " + str(self.preds) + "\n"
        res += "Succs: " + str(self.succs) + "\n"
        res += "Contexts: " + str(self.contexts) + "\n"
        res += "---------------------------------------\n"
        return res
            
    def __repr__(self):
        return self.shortStr()
    
    def __str__(self):
        global showingCFG
        if showingCFG:
            return self.shortStr()
        return self.verbStr()

class IR(SingleContext):
    def __init__(self):
        super(IR, self).__init__()
        self.signature = []
        self.cfg = None
        
    def resetLists(self):
        del self.signature[:]
        del self.declare[:]
        del self.precomp[:]
        del self.blocks[:]
        del self.postcomp[:]
        del self.flatList[:]
        self.bindingTable.resetTable()
        
    def flatten(self):
        counter = count()
        contexts = [ self ]
        entry = IBlock(counter.next(), True)
        current = IBlock(counter.next())
        current.preds.append(entry)
        entry.succs.append(current)
        self.addToFlatList([ entry, current ], contexts)
        for b in self.precomp + self.blocks + self.postcomp:
            for i in b.instructions:
                if isinstance(i, NewContextInst):
                    nextBlk = i.flatten(current, counter, contexts)
                    if not current.isEmpty():
                        self.addToFlatList([ nextBlk[0] ], contexts)
                        tblock = IBlock(counter.next())
                        current.succs.append(tblock)
                        tblock.preds.append(current)
                        tblock.succs.append(nextBlk[0])
                        nextBlk[0].preds.append(tblock)
                        current.succs.remove(nextBlk[0])
                        nextBlk[0].preds.remove(current)
                        current = tblock
                        self.addToFlatList([ current ], contexts)
                    else:
                        self.flatList.insert( len(self.flatList)-1, nextBlk[0] )
                        nextBlk[0].contexts += contexts
                    current.instructions += [ i ]
                    tblock = IBlock(counter.next())
                    nextBlk[1].succs.append(tblock)
                    tblock.preds.append(nextBlk[1])
                    current = tblock
                    self.addToFlatList([ current ], contexts)
                elif isinstance(i, MultiContextInst):
                    nextBlks = i.flatten(current, counter, contexts) # if i is If returns [ preIfBlk, IfBlk, MergeBlk ]
                    self.addToFlatList(nextBlks, contexts)
                    nextBlks[1].instructions += [ i ]
                    current = nextBlks[2]
                else:
                    current.instructions += [ i ]
        if current.isEmpty():
            current.markExit()
            exitBlk = current
        else:
            exitBlk = IBlock(counter.next(), isExit=True)
            current.succs.append(exitBlk)
            exitBlk.preds.append(current)
            self.addToFlatList([ exitBlk ], contexts)
        
    
    def printFlat(self):
        for ib in self.flatList:
            print "{ " + repr(ib) 
            for i in ib.phi + ib.instructions:
                print i.printInst("") + "\n"
            print "}" + repr(ib)

    def traverseDFS(self, ib, visited, preVisit=lambda b: None, postVisit=lambda b: None):
        preVisit(ib)
        visited += [ ib ]
        for b in ib.succs:
            if not b in visited:
                self.traverseDFS(b, visited, preVisit)
        postVisit(ib)

    def collectPostorder(self, ib, visited, collection, counter):
        visited += [ ib ]
        for b in ib.succs:
            if not b in visited:
                self.collectPostorder(b, visited, collection, counter)
        ib.pn = counter.next()
        collection += [ ib ]
        
    def listReversePostorder(self):
        collection,visited = [],[]
        counter = count()
        self.collectPostorder(self.flatList[0], visited, collection, counter)
        collection.reverse() # Reverse Postorder
        return collection

    def printCFG(self):
        visited = []
        self.traverseDFS(self.flatList[0], visited, lambda b: sys.stdout.write(str(b)+"\n"))
    
#    def storeIBToGrap(self, ib, visited, level):
#        self.cfg.add_node(ib)
#        visited += [ ib ]
#        for b in ib.succs:
#            if not b in visited:
#                self.storeIBToGrap(b, visited, level+1)
#            self.cfg.add_edge(ib, b)
#        
#    def showCFG(self):
#        global showingCFG
#        del self.cfg
#        self.cfg = nx.DiGraph()
#        visited = []
#        self.storeIBToGrap(self.flatList[0], visited, 0)
#        
#        showingCFG = True
#        cols = []
#        for n in self.cfg:
#            cols += ["#6698FF"]
#        sizes = []
#        for n in self.cfg:
#            sizes += [400*len(str(n))]
#        
#        pos = nx.graphviz_layout(self.cfg, prog='dot')
#        nx.draw(self.cfg, pos, node_color=cols, node_size=sizes, cmap=plt.cm.Blues)
#        plt.show()
#        showingCFG = False
        
    def computeIterDOM(self):
        # implementation of the Iterative Dominator Algorithm
        doms = {}
        iblocks = self.listReversePostorder()
        for ib in iblocks:
            doms[ib] = set(iblocks)
        changed = True
        while changed:
            changed = False
            for ib in iblocks:
                newset = set([ ib ])
                if len(ib.preds) == 0:
                    inters = set()
                else:
                    inters = doms[ib.preds[0]]
                    for p in ib.preds[1:]:
                        inters &= doms[p]
                newset = newset | inters
                if newset != doms[ib]:
                    doms[ib] = newset
                    changed = True
        return doms
    
    def intersect(self, b1, b2, doms):
        finger1,finger2 = b1,b2
        while finger1 != finger2:
            while finger1 < finger2:
                finger1 = doms[finger1]
            while finger2 < finger1:
                finger2 = doms[finger2]
        return finger1
    
    def computeEngineeredDOM(self):
        # implementation of the Engineered Algorithm in Cooper et al. "A Simple, Fast Dominance Algorithm", Fig. 3
        doms = {}
        iblocks = self.listReversePostorder()
        for ib in iblocks:
            doms[ib] = None
        doms[self.flatList[0]] = self.flatList[0]
        iblocks.remove(self.flatList[0]) 
        changed = True
        while changed:
            changed = False
            for ib in iblocks:
                newIdom = ib.preds[0]
                for p in ib.preds[1:]:
                    if doms[p] is not None:
                        newIdom = self.intersect(p, newIdom, doms)
                if doms[ib] != newIdom:
                    doms[ib] = newIdom
                    changed = True
        return doms
    
    def computeDF(self):
        #In Cooper et al., "A Simple, Fast Dominance Algorithm", Fig. 5
        df = {}
        doms = self.computeEngineeredDOM()
        iblocks = self.listReversePostorder()

        for ib in iblocks:
            df[ib] = set()
        
        for ib in iblocks:
            if len(ib.preds) >= 2:
                for p in ib.preds:
                    runner = p
                    while runner != doms[ib]:
                        df[runner].update([ ib ])
                        runner = doms[runner]
        return df
    
    def computeDT(self):
        iblocks = self.listReversePostorder()
        doms = self.computeEngineeredDOM()

        for ib in iblocks:
            del ib.dtChildren[:]
        
        for ib in iblocks:
            if not ib.isEntry:
                doms[ib].dtChildren.append(ib)
    
    def printDTChildren(self, ib):
        print ib
        print "DT Children: " + str(ib.dtChildren)
        for b in ib.dtChildren:
            self.printDTChildren(b)
        
    def printDT(self):
        self.printDTChildren(self.flatList[0])
    
#     def getAllRefsTo(self, PhysLayout, iblocks=None):
#         allRefs = set()
#         if iblocks is None:
#             iblocks = self.listReversePostorder()
#         for ib in iblocks:
#             allRefs.update(ib.getDstRefsTo(PhysLayout))
#             allRefs.update(ib.getSrcRefsTo(PhysLayout))
#         return allRefs

    def getAllRefsTo(self, PhysLayout, iblocks=None, allRefsOnly=True):
        allRefs = set()
        if iblocks is None:
            iblocks = self.listReversePostorder()
        if allRefsOnly:
            for ib in iblocks:
                allRefs.update(ib.getDstRefsTo(PhysLayout))
                allRefs.update(ib.getSrcRefsTo(PhysLayout))
            return allRefs
        else:
            dSrc, dDst = {}, {}
            for ib in iblocks:
                lDst = ib.getDstRefsTo(PhysLayout)
                lSrc = ib.getSrcRefsTo(PhysLayout)
                dDst[ib] = lDst
                dSrc[ib] = lSrc
                allRefs.update(lDst)
                allRefs.update(lSrc)
            return (dSrc, dDst, allRefs)
    
    def placePhiFunctions(self):
        #Based on Cytron et al. "Efficiently Compute SSA Form and the Control Depen. Graph"
        iblocks = self.listReversePostorder()
        _ , dDst, V = self.getAllRefsTo(Scalars, iblocks, False)
        df = self.computeDF()
        hasAlready, work = {}, {}
        W = set()
        iterCount = 0
        for ib in iblocks:
            hasAlready[ib] = 0
            work[ib] = 0
        for v in V:
            iterCount += 1
            for ib in iblocks:
#                 if v in ib.getDstRefsTo(Scalars):
                if v in dDst[ib]:
                    work[ib] = iterCount
                    W.update([ ib ])
            while len(W) > 0:
                ib = W.pop()
                for b in df[ib]:
                    if hasAlready[b] < iterCount and v.getDeclContext() in b.contexts[:-1]:
#                         phiv = v.pointer.matAt if isinstance(v, Vec) else v
#                         b.phi.append(Mov(Phi([phiv,phiv]), phiv))
                        b.phi.append(Mov(Phi([v,v]), v))
                        hasAlready[b] = iterCount
                        if work[b] < iterCount:
                            work[b] = iterCount
                            W.update([ b ])
    
    def search(self, ib, C, S, newV):
        top = lambda l: l[len(l)-1]
        oldLHS = {}
        for instList in [ib.phi, ib.instructions]:
            for i in range(len(instList)):
                if isinstance(instList[i], MovStatement):
                    if not instList[i] in ib.phi:
                        for v in [scav for scav in instList[i].getSrc() if scav.isRefTo(Scalars) and not scav.isRefToParam(Scalars)]:
                            instList[i].replaceInRHS(v, ScaLoad([newV[v], (0, top(S[v]))]))
                    v = instList[i].getDst()
                    if v.isRefTo(Scalars):
                        c = C[v]
                        instList[i] = instList[i].replaceInLHS(v, ScaLoad([newV[v], (0, c)]))
                        oldLHS[instList[i]] = v
                        v.addToBlackList()
                        S[v].append(c)
                        C[v] = c+1
        
        if not ib.isEntry:
            for y in ib.succs:
                j = y.preds.index(ib)
                for a in y.phi:
                    phi = a.getRHS()
                    v = phi.getRefByPos(j)
                    if len(S[v]) > 0:
                        rep = ScaLoad([newV[v], (0, top(S[v]))])
                    else:
                        rep = V(0) #TODO: should this branch ever be taken?
                    phi.replaceRefByPos(j, rep)
        
        for y in ib.dtChildren:
            self.search(y, C, S, newV)
        
        for a in ib.phi+ib.instructions:
            if isinstance(a, MovStatement) and a in oldLHS:
                v = oldLHS[a]
                S[v].pop()

    def rename(self, opts):
        global icode
        self.computeDT()
        V = self.getAllRefsTo(Scalars)
        # Filter out scalar params
        V = [ v for v in V if not v.isRefToParam(Scalars) ]            
        C,S,newV = {}, {}, {}
        counter = count()
        for v in V:
            C[v] = 0
            S[v] = []
#             newV[v] = Matrix("S"+str(counter.next()), scalar, (1,1))
            newV[v] = Scalar("S"+str(counter.next()), scalar_block())
        self.search(self.flatList[0], C, S, newV)
        #Create here the new Physical Layout based on names in V and sizes in C
        vLists = groupByType(V)
        for vtype in vLists:
            vList = vLists[vtype]
            for v in vList:
                vContext = v.getDeclContext()
                physLayout = Scalars(v.getDstName() + "_", (1,C[v]), opts, ctx=vContext, vtype=vtype)
                icode.bindingTable.addBinding(newV[v], physLayout)
                icode.declare += [physLayout]
#                 vContext.declare += [physLayout]
    
    def removePhi(self, ib):
        if len(ib.phi) > 0:
            for a in ib.phi:
                v = a.getDst()
                phi = a.getRHS()
                i = 0
                for vi in phi.getSrc():
                    pred = ib.preds[i]
                    if pred.isEntry:
                        vi = V(0)
                    pred.instructions.append( Mov(vi, v) )
                    i += 1
        del ib.phi[:]
        for y in ib.dtChildren:
            self.removePhi(y)
    
    def deSSA(self):
        self.removePhi(self.flatList[0])
                
    def __str__(self):
        res = "Signature: " + str(self.signature) +"\nDeclare: " + str(self.declare) + "\nBlocks: " + str(self.blocks)
        return res
    
    def __repr__(self):
        return self.__str__()

icode = IR()

####################################################################################

class ArrayToScalarMap(object):
    def __init__(self, mat, accessList, dstSrcMap=None):
        '''accessList is the unified list created from applyScaRep.'''
        self.refDict = {} # map: access to array -> scalar variable 
#         self.dstSrcMap = {} if dstSrcMap is None else dstSrcMap # in case of equal dsts and srcs
#         self.max = -1
        i = 0
        for a in accessList:
            self.refDict[a[1][1]] = [ a[0], a[1][0], ScaLoad([mat,(sympify(0),sympify(i))]), a[1][2] ] # [ 's'|'d', 1. pos, load, last pos ]
#             self.max = max(self.max, a[1][0])
            i += 1
    
#     def isMappingAtObj(self, atObj):
#         return (atObj[0], atObj[1].getPhysAtPair()) in self.refDict  

    def getDstList(self):
        '''Return the destination array accesses as a list of tuples (pos, dst), sorted by pos.'''
        res = [ (i[1][1], i[0], i[1][3]) for i in self.refDict.items() if i[1][0] == 'd' ] # List of dsts with their block position
        return sorted(res, key=lambda t: t[0])

    def getSrcList(self):
        '''Return array accesses as a list of tuples (pos, src), sorted by pos.'''
        res = [ (i[1][1], i[0], i[1][3]) for i in self.refDict.items() if i[1][0] == 's' ] 
        return sorted(res, key=lambda t: t[0])

    def remove(self, access):
        res = [ r for r in self.refDict if access.eqValueFirst(r) ]
        for r in res:
            del self.refDict[r]
#             if r in self.dstSrcMap:
#                 del self.dstSrcMap[r]
    
    def __contains__(self, access):
#        return atObj in self.refDict
        res = [ r for r in self.refDict if access.eqValueFirst(r) ]
        return len(res) == 1
    
    def __add__(self, other):
        if other is None:
            return self
        newMap = ArrayToScalarMap(None, [ ])
#         rebase = other.max + 1
#         selfitems = [ (key, [ self.refDict[key][0], rebase + self.refDict[key][1], self.refDict[key][2] ]) for key in self.refDict ]
        newMap.refDict = dict(other.refDict.items() + self.refDict.items())
#         newMap.refDict = dict(other.refDict.items() + selfitems)
#         newMap.max = selfitems[-1][1][1] if len(selfitems) > 0 else other.max
        return newMap
    
    def get(self, access, otherwise=None):
        res = [ r for r in self.refDict if access.eqValueFirst(r) ]
        if len(res) == 1:
            return self.refDict[ res[0] ]
        return otherwise
    
    def __getitem__(self, access):
        res = [ r for r in self.refDict if access.eqValueFirst(r) ]
        if len(res) == 1:
            return self.refDict[ res[0] ][2]
        return access
    
    def __str__(self):
        return "refDict: " + str(self.refDict)

def buildUnifiedSrcDstLists(srcAtObjs, dstAtObjs, opts):
    ''' Returns all elements in src and dst (removes the intersection of the two sets).'''
    uList = {}
#     sameSrcDst = {}
    nuTypeDict = opts['isaman'].getNuTypeDict('fp', opts['precision'])
    
    for nu in nuTypeDict.keys():
        srcList = [ ['s', s] for s in srcAtObjs if s[1].reglen == nu]
        dstList = [ ['d', d] for d in dstAtObjs if d[1].reglen == nu]
        uList[nu] = [ s for s in srcList if not any(map(lambda d: d[1][1].eqValueFirst(s[1][1]), dstList)) ]
        uList[nu] += dstList
#         for d in dstList:
#             fs = filter(lambda s: d[1][1].eqValueFirst(s[1][1]), srcList)
#             if fs:
#                 sameSrcDst[d[1][1]] = [ s[1][1] for s in fs ]

    return (uList, nuTypeDict)

def filter_dsts_in_pot_RAW(accObjs, dstObjs):
    dstRaw = set()
    for d in dstObjs:
        potRawCase = False
        i = 0
        while not potRawCase and i < len(accObjs):
            acc = accObjs[i]
#             if d[1].pointer._ref.physLayout.name == 'C' and s[1].pointer._ref.physLayout.name == 'C':
#                 pass
            if d[1].intersect(acc[1]) and not d[1].eqValueFirst(acc[1]): 
                dstRaw.update([d])
                potRawCase = True
            i += 1
    return dstRaw

def filter_srcs_in_pot_WAR(dstAccObjs, srcObjs):
    srcWar = set()
    for s in srcObjs:
        potWarCase = False
        i = 0
        while not potWarCase and i < len(dstAccObjs):
            acc = dstAccObjs[i]
#             if d[1].pointer._ref.physLayout.name == 'C' and s[1].pointer._ref.physLayout.name == 'C':
#                 pass
            if s[1].intersect(acc[1]) and not s[1].eqValueFirst(acc[1]): 
                srcWar.add(s)
                potWarCase = True
            i += 1
    return srcWar

def filterSrcDueToRAW(srcObjs, dstObjs):
    srcRes = []
    for sd in srcObjs:
        rawCase = False
        i = 0
        while not rawCase and i < len(dstObjs):
            d = dstObjs[i]
            rawCase = d[1].eqValueFirst(sd[1]) and d[0] < sd[0]
            i += 1
        if not rawCase:
            srcRes.append(sd)
    return srcRes

def access_to_access_map(acc1, acc2, poly_info=None):
    '''
    Return a mapping between two accesses's mrmaps 
    '''
    res = []
    taken_pos = set()
    p_dict_acc1 = acc1.getPointerDict()
    p_dict_acc2 = acc2.getPointerDict()
#     idcs, dom_info = poly_info.get('indices', []), poly_info.get('polytope', Set("{[]}"))
    for p_acc1,th_acc1 in zip(p_dict_acc1['pList'],p_dict_acc1['mrmap']):
        sidx = p_acc1.linIdx
        for p_acc2,th_acc2 in zip(p_dict_acc2['pList'],p_dict_acc2['mrmap']):
            didx = p_acc2.linIdx
            diff = sidx - didx

            if not diff.is_Number: #If the distance varies as a func of variables is not safe to assume same mapping
                continue

            if diff >= 0:
                who_inf, inf, infmrmap = 2, didx, th_acc2
                sup, supmrmap = sidx, th_acc1
            else:
                who_inf, inf, infmrmap = 1, sidx, th_acc1
                sup, supmrmap = didx, th_acc2
            lim = inf + len(infmrmap) if (sup + len(supmrmap) - inf - len(infmrmap)) >= 0 else sup + len(supmrmap)     
                
            acc1_begin, acc1_end = (sup - inf, lim - inf) if who_inf == 1 else (0, lim - sup)
            acc2_begin, acc2_end = (sup - inf, lim - inf) if who_inf == 2 else (0, lim - sup)
            acc1_pos_list, acc2_pos_list = [], []
            for spos, dpos in zip(th_acc1[acc1_begin:acc1_end],th_acc2[acc2_begin:acc2_end]):
                if not spos in taken_pos:
                    acc1_pos_list.append(spos)
                    acc2_pos_list.append(dpos)
                    taken_pos.add(spos)
            if acc1_pos_list:
                res.append( (acc1_pos_list, acc2_pos_list) )

    res = sorted(res, key=lambda t: t[0])
    leftovers = [ p for p in acc1.mrmap if p not in taken_pos ]
    if leftovers:
        res.append( (leftovers, None) )
    return res

def drop_redundant_stores(store_list, poly_info=None):
    final_list = []
    for s in store_list[::-1]:
        lmrmap = len(s.dst.mrmap)
        can_touch = [True]*lmrmap
        for conf_s in final_list:
            if s.dst.pointer.ref.physLayout == conf_s.dst.pointer.ref.physLayout:
                acc_mapping = access_to_access_map(s.dst, conf_s.dst, poly_info)[-1]
                if acc_mapping[1] is None:
                    for p in range(lmrmap):
                        if s.dst.mrmap[p] not in acc_mapping[0]:
                            can_touch[p] = False
                else:
                    can_touch = [False]*lmrmap
                    break
        if any(can_touch):
            final_list.append(s)
    final_list.reverse()
    return final_list

def extend_inst_list_with_stores(inst_list, inst_list_with_pos, poly_info=None):
    if inst_list_with_pos:
        inst_list_with_pos.sort(key=lambda t_pos_inst: t_pos_inst[0])
        final_list = drop_redundant_stores([t_iwp[1] for t_iwp in inst_list_with_pos], poly_info)
        inst_list.extend(final_list)
        del inst_list_with_pos[:]
    
def drop_redundant_dsts_to_same_src(dst_tuple_list, src, poly_info=None):
    # Assuming all dsts share same physlayout as src. dst tuple has (line, dst, ...)
    final_list = []
    lmrmap = len(src.mrmap)
    can_touch = [True]*lmrmap
    i=0
    while any(can_touch) and i<len(dst_tuple_list):
        dst_tuple = dst_tuple_list[-(1+i)]
        acc_mapping = access_to_access_map(src, dst_tuple[1], poly_info)[-1]
        if acc_mapping[1] is None:
            for p in range(lmrmap):
                if src.mrmap[p] not in acc_mapping[0]:
                    can_touch[p] = False
        else:
            can_touch = [False]*lmrmap
#             break
        final_list.append(dst_tuple)
        i += 1
    final_list.reverse()
    if len(final_list) == 1 and not any(can_touch):
        d = final_list[-1]
        if src.eqValueFirst(d[1]):
            return [], [True]*lmrmap
    return final_list, any(can_touch)

def applyScaRep(context, counter, opts, arrMap=None, neighbor_ctx_pot_mod=None, poly_info=None):
    
#     poly_info = {'indices': [], 'polytope': Set("{[]}") } if poly_info is None else poly_info
    ctxMap = ArrayToScalarMap(None, [ ]) + arrMap
    
    # Determine any dsts from calling ctx that are in a pot. RAW with srcs or pot. WAW with dsts from present ctx.
    # This will be stored right before this ctx (callee) and read again inside it (that's why they
    # are removed from ctxMap).
    ctxDsts = ctxMap.getDstList()
#     intersectingDstsPerIB = []
    intersectingDsts = set()
    line = list(opts['line']) + [-1] # For IBs
    dstObjs = []
    for ib in context.flatList:
        if not ib.instructions:
            continue
        line[-1] += 1
        opts['line'] = tuple(line)
#         dstObjs = None
        if opts['nu'] > 1:
#             dstObjs = ib.joinHeterogeneousRAW(Array, ctxMap, opts, poly_info, dstObjs)
            dstObjs = ib.joinHeterogeneousRAW(Array, ctxMap, opts, dstObjs)
        dstObjs = ib.getDstNoDupRefsToWithLine(Array, opts['line'], refsTo=dstObjs)
        srcObjs = ib.getSrcNoDupRefsToWithLine(Array, opts['line'])
#         intersectingDstsPerIB.append(filterDstDueToRAW(srcObjs, ctxDsts))
        intersectingDsts.update(filter_dsts_in_pot_RAW(srcObjs, ctxDsts))
        intersectingDsts.update(filter_dsts_in_pot_RAW(dstObjs, ctxDsts))
#     for idset in intersectingDstsPerIB:
#         intersectingDsts.update(idset)
    for intDst in intersectingDsts:
        ctxMap.remove(intDst[1])
        
    dsts = []
    #Whenever entering a new context stores that cannot be caught with simple access comparison 
    # may alter values currently scalarized. Need to store and load around that context.
    #Following sets are used to detect such cases.
    dsts2BeStored = set() # Collect dsts that should be stored in caller contexts (as they do not appear in this one)
    # In case a dsts was stored before a new context but it appears again in some IB after it, they are collected here
    # so that it could still be stored at the very end (or before if it becomes a rDst again).
    alreadyStored = set() 
    # Collect dsts that were potentially modified () within the ctx. Will be sent to caller
    potModDsts = set() 
    # To collect pot. mod. dsts at the level of the present ctx. dsts are added or removed depending wether they need to be read again or not
    # between IBs. They will also figure in outer ctxs through potModDsts 
    localIBPotModDsts = set()  
    #Collect srcs invalidated by stores with which dsts they overlap (only - equality doesn't invalidate).
    #Will also be passed to the caller.
    invalidated_srcs = set()
    
    if neighbor_ctx_pot_mod:
        localIBPotModDsts.update(neighbor_ctx_pot_mod)
    
    line[-1] = -1
    for ib in context.flatList:
        if not ib.instructions:
            continue
        
        line[-1] += 1
        opts['line'] = tuple(line)
        #Have to rerun as ctxMap may have changed
#         dstsWithLine = ib.joinHeterogeneousRAW(Array, ctxMap, opts, poly_info) if opts['nu'] > 1 else None
        dstsWithLine = ib.joinHeterogeneousRAW(Array, ctxMap, opts) if opts['nu'] > 1 else None
        fullSrcAt = srcAtObjs = ib.getSrcNoDupRefsToWithLine(Array, opts['line']) # e.g. loads [(src, pos)]
        dstAtObjs = ib.getDstNoDupRefsToWithLine(Array, opts['line'], dstsWithLine) # e.g. VecDests
#         dstAtObjs = ib.getDstNoDupRefsToWithLine(Array) # e.g. VecDests
        
        # Remove srcs from ctxMap invalidated by present IB 
        ctx_srcs = ctxMap.getSrcList()
        inv_srcs = filter_srcs_in_pot_WAR(dstAtObjs, ctx_srcs)
        invalidated_srcs.update( inv_srcs )
        for s_tuple in invalidated_srcs:
            ctxMap.remove(s_tuple[1])
        
        # we don't take into account what is already in ctxMap
        srcAtObjs = [ s for s in srcAtObjs if not s[1] in ctxMap ]
        
        toReadd = set()
        for d in dstAtObjs:
            fd = filter(lambda asDst: asDst[1].eqValueFirst(d[1]), alreadyStored)
            toReadd.update(fd)
        alreadyStored.difference_update(toReadd)

        srcs_2be_stored = [ d for d in dstAtObjs if d[1] in ctxMap and ctxMap.get(d[1])[0] == 's' ]
        
        dsts_from_potmod, dsts_from_neighbor_ctx_potmod = set(), set()
        if neighbor_ctx_pot_mod:
            for d in dstAtObjs:
                fd = filter(lambda pmDst: pmDst[1].eqValueFirst(d[1]), localIBPotModDsts)
                dsts_from_potmod.update(fd)
            for d in dsts_from_potmod:
                ffd = filter(lambda pmDst: pmDst[1].eqValueFirst(d[1]), neighbor_ctx_pot_mod)
                dsts_from_neighbor_ctx_potmod.update(ffd)
        
        dstAtObjs = [ d for d in dstAtObjs if not d[1] in ctxMap ]
        
        # keep srcs that have no RAW dependency with any of the dsts
        srcAtObjs  = filterSrcDueToRAW(srcAtObjs, dstAtObjs)
        
        dsts += dstAtObjs + list(toReadd) + srcs_2be_stored + list(dsts_from_neighbor_ctx_potmod)
        dsts.sort(key=lambda d: d[0])
        # sorting
        srcAtObjs.sort(key=lambda s: (s[1].getMat().name, s[1].getAt()), reverse=True)
        dstAtObjs.sort(key=lambda d: (d[1].getMat().name, d[1].getAt()))
        
        if(len(dstAtObjs) + len(srcAtObjs) > 0):
            # handles co-existence of scalar and vector code (common when we didn't have loadreplacers) 
            unifiedLists,types = buildUnifiedSrcDstLists(srcAtObjs, dstAtObjs, opts)
            # unifiedLists cantains the elements that we want to replace with scalars
            for nu in unifiedLists.keys():
                if len(unifiedLists[nu]) > 0:
                    cid = counter.next()
                    scaMat = Matrix("_T" + str(cid), scalar_block(), (1, len(unifiedLists[nu])))
                    physLayout = Scalars("_t" + str(cid)+"_", scaMat.size, opts, ctx=context, vtype=types[nu]) # vtype is retrieved from the ISA definition
                    # for now let's stick to a unified table stored in the top-level context (icode) 
                    icode.bindingTable.addBinding(scaMat, physLayout)
#                     context.declare += [physLayout]
                    icode.declare += [physLayout]
                    # update the scalar map
                    ctxMap = ArrayToScalarMap(scaMat, unifiedLists[nu]) + ctxMap
#             ctxMap.dstSrcMap.update(dstSrcMap)
        # do the actual replacement
        instList = []
        tmp_inst_list_with_pos = []
        def _insert_stores_before_context(list_rDsts):
            for rd in list_rDsts:
                fd = filter(lambda d: d[1].eqValueFirst(rd[1]), dsts)
                if fd:
                    if not rd[1].getPhysAtPair()[0].safelyScalarize:
                        store_class = opts['isaman'].getStore('fp', rd[1].reglen, rd[1].mrmap, opts['precision'], rd[1].horizontal, rd[1].isAligned)
#                             instList.append(store_class.getStore(ctxMap[rd[1]], rd[1]))
                        tmp_inst_list_with_pos.append((fd[-1][2], store_class.getStore(ctxMap[rd[1]], rd[1])))
                    for d in fd:
                        dsts.remove(d)
                    alreadyStored.add(rd)
                else:
                    dsts2BeStored.add(rd)
        
        def _update_poly_info(inst):
            '''
            Not used anymore. Was mainly meant for mapping vector accesses (when dropping stores).
            At the moment all drop attempts based on a difference between addresses which is not
            constant are not considered.
            '''
            new_poly_info = None 
            if isinstance(inst, NewContextInst):
                idcs = poly_info['indices'] + [str(inst.idx)]
                setstr = "{{ [{0}] : exists s: {1}={2}s and {3} <= {1} <= {4} }}".format(",".join(idcs), inst.idx, inst.S, inst.B, inst.E) 
                newDimSet = Set(setstr)
                newIterspace = newDimSet.intersect(poly_info['polytope'].add_dims(dim_type.set, 1))
                new_poly_info = { 'indices': idcs, 'polytope': newIterspace }
            elif isinstance(inst, MultiContextInst):
                new_poly_info = []
                for cond in inst.conditions:
                    # else stmt is not taken into account - when added as a possible construct this branch should be adapted
                    setstr = "{{ [{}] : {} }".format(",".join(poly_info['indices']), cond.getIslStr()) 
                    newDimSet = Set(setstr)
                    newIterspace = newDimSet.intersect(poly_info['polytope'])
                    new_poly_info.append( { 'indices': poly_info['indices'], 'polytope': newIterspace } )
            else:
                new_poly_info = poly_info
            return new_poly_info
            
        for i in range(len(ib.instructions)):
#             new_poly_info = _update_poly_info(ib.instructions[i])
            if isinstance(ib.instructions[i], NewContextInst): # if it is a for-loop apply scarep to it
#                 if str(ib.instructions[i].idx) == 'i66':
#                     pass
                opts['line'] = tuple(list(opts['line']) + [i])
#                 rDsts, pmDsts = applyScaRep(ib.instructions[i], counter, opts, ctxMap, localIBPotModDsts, poly_info=new_poly_info)
                rDsts, pmDsts, inv_srcs = applyScaRep(ib.instructions[i], counter, opts, ctxMap, localIBPotModDsts)
                opts['line'] = tuple(list(opts['line'])[:-1])
                localIBPotModDsts.update(rDsts)
                localIBPotModDsts.update(pmDsts)
                list_rDsts = list(rDsts)
                _insert_stores_before_context(list_rDsts)
                invalidated_srcs.update( inv_srcs )
#                 for rd in list_rDsts:
#                     fd = filter(lambda d: d[1].eqValueFirst(rd[1]), dsts)
#                     if fd:
#                         if not rd[1].getPhysAtPair()[0].safelyScalarize:
#                             store_class = opts['isaman'].getStore('fp', rd[1].reglen, rd[1].mrmap, opts['precision'], rd[1].horizontal, rd[1].isAligned)
# #                             instList.append(store_class.getStore(ctxMap[rd[1]], rd[1]))
#                             tmp_inst_list_with_pos.append((fd[-1][2], store_class.getStore(ctxMap[rd[1]], rd[1])))
#                         for d in fd:
#                             dsts.remove(d)
#                         alreadyStored.add(rd)
#                     else:
#                         dsts2BeStored.add(rd)
                extend_inst_list_with_stores(instList, tmp_inst_list_with_pos, poly_info)
                instList.append(ib.instructions[i])
            elif isinstance(ib.instructions[i], MultiContextInst): # if it is an if statement apply scarep to its branches
                rDsts = set()
                pmDsts = set()
#                 for ctxt, p_info in zip(ib.instructions[i].contexts, new_poly_info):
                for ctxt in ib.instructions[i].contexts:
                    opts['line'] = tuple(list(opts['line']) + [i])
                    t0, t1, inv_srcs = applyScaRep(ctxt, counter, opts, ctxMap, localIBPotModDsts)
                    opts['line'] = tuple(list(opts['line'])[:-1])
                    rDsts.update(t0)
                    pmDsts.update(t1)
                    invalidated_srcs.update( inv_srcs )
                localIBPotModDsts.update(rDsts)
                localIBPotModDsts.update(pmDsts)
                list_rDsts = list(rDsts)
                _insert_stores_before_context(list_rDsts)
#                 for rd in list_rDsts:
#                     fd = filter(lambda d: d[1].eqValueFirst(rd[1]), dsts)
#                     if fd:
#                         if not rd[1].getPhysAtPair()[0].safelyScalarize:
#                             store_class = opts['isaman'].getStore('fp', rd[1].reglen, rd[1].mrmap, opts['precision'], rd[1].horizontal, rd[1].isAligned)
# #                             instList.append(store_class.getStore(ctxMap[rd[1]], rd[1]))
#                             tmp_inst_list_with_pos.append((fd[-1][2], store_class.getStore(ctxMap[rd[1]], rd[1])))
#                         for d in fd:
#                             dsts.remove(d)
#                         alreadyStored.add(rd)
#                     else:
#                         dsts2BeStored.add(rd)
                extend_inst_list_with_stores(instList, tmp_inst_list_with_pos, poly_info)
                instList.append(ib.instructions[i])
            elif isinstance(ib.instructions[i], MovStatement): # if it is a mov, replace its contents
                instList.append(ib.instructions[i].replaceRefs(ctxMap))
            else:
                instList.append(ib.instructions[i])
        # End of loop over instructions in current IB
        
        del ib.instructions[:]
        ib.instructions = instList
        potModDsts.update(localIBPotModDsts)
        
        #DEBUG
        def _print_dbg_loadlines(acc):
#                 ib.instructions.insert(1, DebugPrint(["\"Loading "+getReference(icode, d[1].pointer.mat).physLayout.name+"\"", "\" [ \"", str(d[1].pointer.at[0]), "\" , \"", str(d[1].pointer.at[1]), "\" ] at line \"", "__LINE__"]))
            pi,pj=0,0
            for _ in range(len(acc.mrmap)):
                ptr = acc.pointer
                ib.instructions.insert(0, DebugPrint(["\"Loading "+getReference(icode, ptr.mat).physLayout.name+"\"", "\" [ \"", str(ptr.at[0]+pi), "\" , \"", str(ptr.at[1]+pj), "\" ] at line \"", "__LINE__"]));
                if acc.horizontal:
                    pj += 1
                else:
                    pi += 1
        #DEBUG
            
        # prepend the loads of new srcs from the IB that cannot be replaced by dsts in RAW with them
        for d in srcAtObjs:
            if not d[1].getPhysAtPair()[0].safelyScalarize:
                ib.instructions.insert(0, Mov(d[1], ctxMap[d[1]]))
#                 _print_dbg_loadlines(d[1])
#                 if(getReference(icode, d[1].pointer.mat).physLayout.name == 'C' and list(d[1].pointer.at) == [8,0]):
#                     ib.instructions.insert(2, Comment("Inserted from srcAtObjs Section - IB" + str(ib.n)))
                
        #if any srcs in the IB were potentially modified in an intermediate ctx reload 
        readDsts = [] 
        if fullSrcAt:
            for d in localIBPotModDsts:
                fs = filter(lambda s: s[1].eqValueFirst(d[1]), fullSrcAt)
                for s in fs:
                    if not s[1].getPhysAtPair()[0].safelyScalarize:
                        ib.instructions.insert(0, Mov(s[1], ctxMap[s[1]]))
                        readDsts.append(d)
#                     _print_dbg_loadlines(s[1])
#                     if(getReference(icode, s[1].pointer.mat).physLayout.name == 'C' and list(s[1].pointer.at) == [8,0]):
#                         ib.instructions.insert(2, Comment("Inserted from potMod Section - IB" + str(ib.n)))
        
        # In case a dsts was loaded no need to push further to other IBs.  
        localIBPotModDsts.difference_update(readDsts)
    #End of loop over IBs in context.flatList
    
    # append the stores to the end of the body
    tmp_inst_list_with_pos = []
    for d in dsts:
        if not d[1].getPhysAtPair()[0].safelyScalarize:
            store_class = opts['isaman'].getStore('fp', d[1].reglen, d[1].mrmap, opts['precision'], d[1].horizontal, d[1].isAligned)
#             context.flatList[-1].instructions.append(store_class.getStore(ctxMap[d[1]], d[1]))
            tmp_inst_list_with_pos.append( (d[2], store_class.getStore(ctxMap[d[1]], d[1])) )
    
    extend_inst_list_with_stores(context.flatList[-1].instructions, tmp_inst_list_with_pos, poly_info)
    # In case some dsts could not be stored in this context push them up to the caller.
    intersectingDsts.update(dsts2BeStored)
    # Notify caller ctx of any pot. mod. mem. dst. (superset of intersectingDsts)
    potModDsts.update(intersectingDsts)
    return intersectingDsts, potModDsts, invalidated_srcs
            
def scalarRep(opts):
    counter = count()
    opts['loadreplacer'] = opts['isaman'].getLoadReplacer(opts['precision'], opts['nu'])
    opts['line'] = tuple()
    applyScaRep(icode, counter, opts)    

# this import statement is put here in order to avoid the circular dependency between irbase.py and abstractint.py
from src.abstractint import IntervalCongruenceReductionAnalysis, IntervalAnalysis, AbstractElement

def alignRep(opts):
    global icode
    arrays = [param for param in icode.signature if isinstance(param, Array) and param.size > 1]
    maxAlignLength = max(opts['alignsizes'])
    if opts.get('assumealigned', False):
        initialAlignmentList = [[0] * len(arrays)]
    else:
        initialAlignmentList = list(product(range(maxAlignLength), repeat=len(arrays)))
    
    # Create different versions of the kernel body depending on the alignment of the array arguments
    icodeVersions = []
    start_time = time.time()
    copytime = 0
    cleartime = 0
    applytime = 0
    propagatetime = 0
    aligntime = 0
    for i, initialAlignment in enumerate(initialAlignmentList):
#         print 'AlignRep: Analyzing %d version out of %d...' % (i+1, len(initialAlignmentList))
        t1 = time.time()
        icodeVersion = deepcopyIcode()
        copytime += time.time() - t1
        for n in opts['alignsizes']:
            intervalAnalysis = IntervalAnalysis()
            initialEnv = {sympify(array.name): (intervalAnalysis.TOP, AbstractElement((initialAlignment[i] % n, n))) for i, array in enumerate(arrays)}
            analysis = IntervalCongruenceReductionAnalysis()
            t1 = time.time()
            analysis.clearInstEnv(icodeVersion)
            cleartime += time.time() - t1
            analysis.env = initialEnv
#             print 'AlignRep: applying semantics...'
            t1 = time.time()
            analysis.applySemantics(icodeVersion)
            applytime += time.time() - t1
#             print 'AlignRep: propagating env to srcs...'
            t1 = time.time()
            analysis.propagateEnvToSrcs(icodeVersion)
            propagatetime += time.time() - t1
#             print 'AlignRep: aligning...'
            t1 = time.time()
            icodeVersion.align(analysis)
            aligntime += time.time() - t1
        icodeVersions.append(icodeVersion)
    elapsed_time = time.time() - start_time
    print 'AlignRep applied in %.3f sec (deepcopy: %.3f, clear: %.3f, apply: %.3f, propagate: %.3f, align: %.3f)' % (elapsed_time, copytime, cleartime, applytime, propagatetime, aligntime)
    if opts.get('assumealigned', False):
        icode.flatList = icodeVersions[0].flatList
    else:
        # we add an "else" branch in the end that will be taken if there is an array whose alignment doesn't comply to 
        # the size of our data type, e.g. we have 4-byte alignment and we are working with doubles 
        icodeVersions.append(deepcopyIcode())
        
        # Create the conditions that correspond to the different alignment possibilities
        conditions = []
        for initialAlignment in initialAlignmentList:
            conditions.append(BoolAnd([Equals(Mod(V('((uintptr_t) %s)' % array.name), V('(%s * sizeof(%s))' % (maxAlignLength, opts['precision']))), 
                                              V('%s * sizeof(%s)' % (initialAlignment[i], opts['precision']))) for i, array in enumerate(arrays)]))
        
        iblock = IBlock()
        iblock.instructions = [If(icodeVersions, conditions)]
        icode.flatList = [iblock]
        
def deepcopyIcode():
    return deepcopy(icode)
