'''
    Created on Dec 21, 2013
    
    @author: nkyrt
    '''
# from src.irbase import *
# from src.isas.isabase import *
# from src.isas.armv7 import *

from sympy import sympify

from src.irbase import RValue, VecAccess, VecDest, V, Pointer, AddressOf, Comment, MovStatement, Mov, sa
from src.isas.isabase import ISA, Loader, Storer, LoadReplacer

#################################################################################################################
#--------------------------------------------- Doubleword intrinsics ---------------------------------------------#
#################################################################################################################

class vldGenF32(RValue, VecAccess):
    ''' Wrapper of a doubleword load instruction.
        
        Useful when we want to represent a composite load instruction as a single logical instruction and then have it
        easily replaced by a scalar during scalar replacement.
        '''
    def __init__(self, pointer, mrmap, isCompact=False, isCorner=True, horizontal=True, zeromask=[]):
        super(vldGenF32, self).__init__()
        self.pointer = pointer
        self.mrmap = mrmap
        self.horizontal = horizontal
        self.orientation = 'horizontal' if horizontal else 'vertical'
        self.reglen = 2
        
        content = None
        if len(mrmap) == 1:
            #             TODO: is it in all cases ok not to set the other lane to zero?
            content = vld1DupF32(pointer, zeromask)
        elif mrmap == [0, 1]:
            if horizontal or isCompact:
                content = vld1F32(pointer, zeromask)
            else:
                zm0 = [0] if 0 in zeromask else []
                zm1 = [0] if 1 in zeromask else []
                p1 = Pointer((pointer.mat, (pointer.at[0] + 1, pointer.at[1])))
                content = vld1LaneF32(p1, vld1DupF32(pointer, zm0), 1, zm1)
        
        if content is None:
            raise ValueError('vldGenF32 does not support mrmap %s with %s layout yet' % (str(mrmap), 'horizontal' if horizontal else 'vertical'))
        self._content = content
    
    def computeSym(self, nameList):
        return self._content.computeSym(self, nameList)
    
    def getZMask(self):
        return self._content.getZMask()
    
    def unparse(self, indent):
        return self._content.unparse(indent)
    
    def printInst(self, indent):
        return 'vldGenF32(%s, %s, %s)' % (str(self.mrmap), self.orientation, self._content.printInst(indent))
    
    def __eq__(self, other):
        return isinstance(other, VecAccess) and self.reglen == other.reglen and self.pointer == other.pointer and self.mrmap == other.mrmap and self.horizontal == other.horizontal
    
    def __hash__(self):
        return hash((hash('vldGenF32'), self.pointer.mat, self.pointer.at, str(self.mrmap), self.orientation))

class vstGenF32(MovStatement):
    '''Wrapper of a doubleword store instruction.
        
        Useful when we want to represent a composite store instruction as a single logical instruction and then have it
        easily replaced by a scalar during scalar replacement.
        '''
    def __init__(self, src, dst, mrmap, isCompact=False, isCorner=True, horizontal=True):
        super(vstGenF32, self).__init__()
        self.srcs += [src]
        #         self.mrmap = mrmap if horizontal else [-1 * el if isinstance(el, int) else tuple(-1 * elel for elel in el) for el in mrmap]
        self.mrmap = mrmap
        dstptr = dst if isinstance(dst, Pointer) else dst.pointer 
        self.dst = VecDest(dstptr, 2, mrmap, horizontal, isCompact, isCorner)
        self.horizontal = horizontal
        self.isCompact = isCompact
        self.isCorner = isCorner
        self.orientation = 'horizontal' if horizontal else 'vertical'
        self.reglen = 2
    
    @property
    def _content(self):
        dst = self.dst.pointer
        src = self.srcs[0]
        mrmap = self.mrmap
        horizontal = self.horizontal
        isCompact = self.isCompact
        content = None
        if len(mrmap) == 1:
            lane = mrmap[0]
            content = [vst1LaneF32(src, dst, lane)]
        elif mrmap == [0, 1]:
            if horizontal or isCompact:
                content = [vst1F32(src, dst)]
            else:
                p0 = dst
                p1 = Pointer((dst.mat, (dst.at[0] + 1, dst.at[1])))
                content = [vst1LaneF32(src, p0, 0), vst1LaneF32(src, p1, 1)]
        
        if content is None:
            raise ValueError('vstGenF32 does not support mrmap %s with %s layout yet' % (str(mrmap), 'horizontal' if horizontal else 'vertical'))
        return content
    
    def replaceRefs(self, refMap):
        #         self._content = [c.replaceRefs(refMap) for c in self._content]
        dst = self.dst.replaceRefs(refMap)
        src = self.srcs[0].replaceRefs(refMap)
        if isinstance(dst, VecDest):
            self.dst = dst
            self.srcs[0] = src
            return self
        return Mov(src, dst)
    
    @staticmethod
    def canStore(reglen, mrmap, horizontal, isAligned=False):
        return reglen == 2
    
    @staticmethod
    def getStore(src, dst):
        mrmap = dst.mrmap
        if isinstance(mrmap, int):
            mrmap = [mrmap]
        return vstGenF32(src, dst, mrmap, dst.isCompact, dst.isCorner, dst.horizontal)
    
    def computeSym(self, nameList):
        return self.srcs[0].computeSym(nameList)[:len(self.mrmap)]
    
    def unparse(self, indent):
        return '\n'.join(instr.unparse(indent) for instr in self._content)
    
    def printInst(self, indent):
        return 'vstGenF32(%s, %s, %s)' % (str(self.mrmap), self.orientation, ','.join([instr.printInst(indent) for instr in self._content]))

class vld1F32(RValue, VecAccess):
    '''Load a doubleword vector from memory.'''
    def __init__(self, pointer, zeromask=None):
        super(vld1F32, self).__init__()
        self.reglen = 2
        self.mrmap = [0,1]
        self.zeromask = [0]*self.reglen
        if zeromask is not None:
            for pos in zeromask:
                self.zeromask[pos] = 1
        self.pointer = pointer
    
    def computeSym(self, nameList):
        p = self.pointer.computeSym(nameList)
        return [sympify(p+'_0'), sympify(p+'_1')]
    
    def getZMask(self):
        return self.zeromask
    
    def unparse(self, indent):
        return '%svld1_f32(%s)' % (indent, self.pointer.unparse(''))
    
    def printInst(self, indent):
        return '%svld1F32( %s )' % (indent, self.pointer.printInst(''))
    
    def __eq__(self, other):
        return isinstance(other, vld1F32) and self.pointer == other.pointer
    
    def __hash__(self):
        return hash((hash("vld1F32"), self.pointer.mat, self.pointer.at))

class vld1DupF32(RValue, VecAccess):
    '''Load all lanes of doubleword vector with the same value from memory.'''
    def __init__(self, pointer, zeromask=None):
        super(vld1DupF32, self).__init__()
        self.reglen = 2
        self.mrmap = [(0,1)]
        self.zeromask = [0]*self.reglen
        if zeromask is not None: # In this case all the positions have to be zero
            self.zeromask = [1]*self.reglen
        self.pointer = pointer
    
    def computeSym(self, nameList):
        p = self.pointer.computeSym(nameList)
        return [sympify(p+'_0'), sympify(p+'_0')]
    
    def getZMask(self):
        return self.zeromask
    
    def unparse(self, indent):
        return '%svld1_dup_f32(%s)' % (indent, self.pointer.unparse(''))
    
    def printInst(self, indent):
        return '%svld1DupF32(%s)' % (indent, self.pointer.printInst(''))
    
    def __eq__(self, other):
        return isinstance(other, vld1qDupF32) and self.pointer == other.pointer
    
    def __hash__(self):
        return hash((hash('vld1DupF32'), self.pointer.mat, self.pointer.at))

class vld1LaneF32(RValue, VecAccess):
    '''Load one of the lanes of a doubleword vector from memory and the rest from another vector.'''
    def __init__(self, pointer, src, lane, zeromask=None):
        super(vld1LaneF32, self).__init__()
        self.reglen = 2
        self.mrmap = [lane]
        self.zeromask = [0]*self.reglen
        if zeromask is not None:
            for pos in zeromask:
                self.zeromask[pos] = 1
        self.srcs += [src]
        self.pointer = pointer
        self.lane = lane
    
    def computeSym(self, nameList):
        p = self.pointer.computeSym(nameList)
        sym = self.srcs[0].computeSym(nameList)
        sym[self.lane] = sympify(p+'_0')
        return sym
    
    def getZMask(self):
        # TODO: Shouldn't we take into account the zeromask of src? In sse.mmLoadlPi we don't, while in mmMoveSs we do.
        return self.zeromask
    
    def unparse(self, indent):
        return '{indent}vld1_lane_f32({ptr}, {vec}, {lane})'.format(indent=indent, ptr=self.pointer.unparse(''),
                                                                    vec=self.srcs[0].unparse(''), lane=self.lane)
    
    def printInst(self, indent):
        return '{indent}vld1LaneF32({ptr}, {vec}, {lane})'.format(indent=indent, ptr=self.pointer.printInst(''),
                                                                  vec=self.srcs[0].printInst(''), lane=self.lane)
    
    def __eq__(self, other):
        return isinstance(other, vld1LaneF32) and self.pointer == other.pointer and self.lane == other.lane
    
    def __hash__(self):
        return hash((hash("vld1LaneF32"), self.pointer.mat, self.pointer.at, self.lane))

class vgetLowF32(RValue):
    '''Get the lower half of a quadword vector.'''
    def __init__(self, src):
        super(vgetLowF32, self).__init__()
        self.srcs += [src]
    
    def computeSym(self, nameList):
        return self.srcs[0].computeSym(nameList)[:2]
    
    def getZMask(self):
        return self.srcs[0].getZMask()[:2]
    
    def unparse(self, indent):
        return '%svget_low_f32(%s)' % (indent, self.srcs[0].unparse(''))
    
    def printInst(self, indent):
        return '%svgetLowF32(%s)' % (indent, self.srcs[0].printInst(''))

class vgetHighF32(RValue):
    '''Get the lower half of a quadword vector.'''
    def __init__(self, src):
        super(vgetHighF32, self).__init__()
        self.srcs += [src]
    
    def computeSym(self, nameList):
        return self.srcs[0].computeSym(nameList)[2:]
    
    def getZMask(self):
        return self.srcs[0].getZMask()[2:]
    
    def unparse(self, indent):
        return '%svget_high_f32(%s)' % (indent, self.srcs[0].unparse(''))
    
    def printInst(self, indent):
        return '%svgetHighF32(%s)' % (indent, self.srcs[0].unparse(''))

class vaddF32(RValue):
    '''Add two doubleword vectors.'''
    def __init__(self, src0, src1):
        super(vaddF32, self).__init__()
        self.srcs += [src0, src1]
    
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [src0[0] + src1[0], src0[1] + src1[1]]
    
    def unparse(self, indent):
        return '%svadd_f32(%s, %s)' % (indent, self.srcs[0].unparse(''), self.srcs[1].unparse(''))
    
    def printInst(self, indent):
        return '%svaddF32(%s, %s)' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''))

class vpaddF32(RValue):
    '''Pairwise (horizontal) addition of two doubleword vectors.'''
    def __init__(self, src0, src1):
        super(vpaddF32, self).__init__()
        self.srcs += [src0, src1]
    
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [src0[0] + src1[0], src0[1] + src1[1]]
    
    def unparse(self, indent):
        return '%svpadd_f32(%s, %s)' % (indent, self.srcs[0].unparse(''), self.srcs[1].unparse(''))
    
    def printInst(self, indent):
        return '%svpaddF32(%s, %s)' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''))

class vmulF32(RValue):
    '''Multiply two doubleword vectors.'''
    def __init__(self, src0, src1):
        super(vmulF32, self).__init__()
        self.srcs += [src0, src1]
    
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [src0[0] * src1[0], src0[1] * src1[1]]
    
    def unparse(self, indent):
        return '%svmul_f32(%s, %s)' % (indent, self.srcs[0].unparse(''), self.srcs[1].unparse(''))
    
    def printInst(self, indent):
        return '%svmulF32(%s, %s)' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''))

class vmulLaneF32(RValue):
    '''Multiply all elements of a doubleword vector with one element of another doubleword vector.
        
        Since there is no intrinsic for VMUL Dd,Dn,Dm[x], we combine a vmul_n_f32 with a vget_lane_f32 and we hope that the
        compiler is smart enough to replace the vget_lane_f32 with a direct access of the corresponding doubleword vector Dm[x].
        '''
    def __init__(self, src0, src1, lane):
        super(vmulLaneF32, self).__init__()
        self.srcs += [src0, src1]
        self.lane = lane
    
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1val = self.srcs[1].computeSym(nameList)[self.lane]
        return [src0[0] * src1val, src0[1] * src1val]
    
    def unparse(self, indent):
        return '%svmul_n_f32(%s, vget_lane_f32(%s, %d))' % (indent, self.srcs[0].unparse(''), self.srcs[1].unparse(''), self.lane)
    
    def printInst(self, indent):
        return '%svmulLaneF32(%s, %s, %d)' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''), self.lane)

class vmulLaneqF32(RValue):
    '''Multiply all elements of a doubleword vector with one element of a quadword vector.
        
        Since there is no intrinsic for VMUL Dd,Dn,Dm[x], we combine a vmul_n_f32 with a vgetq_lane_f32 and we hope that the
        compiler is smart enough to replace the vget_lane_f32 with a direct access of the corresponding doubleword vector Dm[x].
        '''
    def __init__(self, src0, src1, lane):
        super(vmulLaneqF32, self).__init__()
        self.srcs += [src0, src1]
        self.lane = lane
    
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1val = self.srcs[1].computeSym(nameList)[self.lane]
        return [src0[0] * src1val, src0[1] * src1val]
    
    def unparse(self, indent):
        return '%svmul_n_f32(%s, vgetq_lane_f32(%s, %d))' % (indent, self.srcs[0].unparse(''), self.srcs[1].unparse(''), self.lane)
    
    def printInst(self, indent):
        return '%svmulLaneqF32(%s, %s, %d)' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''), self.lane)

class vmlaF32(RValue):
    '''Doubledword vector multiply-accumulate.'''
    def __init__(self, src0, src1, src2):
        '''We multiply src1 with src2 and accumulate on src0.'''
        super(vmlaF32, self).__init__()
        self.srcs += [src0, src1, src2]
    
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        src2 = self.srcs[2].computeSym(nameList)
        return [(src1[0] * src2[0]) + src0[0], (src1[1] * src2[1]) + src0[1]]
    
    def unparse(self, indent):
        return '%svmla_f32(%s, %s, %s)' % (indent, self.srcs[0].unparse(''), self.srcs[1].unparse(''), self.srcs[2].unparse(''))
    
    def printInst(self, indent):
        return '%svmlaF32(%s, %s, %s)' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''), self.srcs[2].printInst(''))

class vmlaLaneF32(RValue):
    '''Multiply all elements of a doubleword vector with one element of another doubleword vector and accumulate result on another doubleword vector.
        
        Since there is no intrinsic for VMLA Qd,Qn,Dm[x], we combine a vmla_n_f32 with a vget_lane_f32 and we hope that the
        compiler is smart enough to replace the vget_lane_f32 with a direct access of the corresponding doubleword vector Dm[x].
        '''
    def __init__(self, src0, src1, src2, lane):
        '''We multiply src1 with src2[lane] and accumulate on src0.'''
        super(vmlaLaneF32, self).__init__()
        self.srcs += [src0, src1, src2]
        self.lane = lane
    
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        src2val = self.srcs[2].computeSym(nameList)[self.lane]
        return [(src1[0] * src2val) + src0[0], (src1[1] * src2val) + src0[1]]
    
    def unparse(self, indent):
        return '%svmla_n_f32(%s, %s, vget_lane_f32(%s, %d))' % (indent, self.srcs[0].unparse(''), self.srcs[1].unparse(''), self.srcs[2].unparse(''), self.lane)
    
    def printInst(self, indent):
        return '%svmlaLaneF32(%s, %s, %s[%d])' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''), self.srcs[2].printInst(''), self.lane)

class vmlaLaneqF32(RValue):
    '''Multiply all elements of a doubleword vector with one element of a quadword vector and accumulate result on another doubleword vector.
        
        Since there is no intrinsic for VMLA Qd,Qn,Dm[x], we combine a vmla_n_f32 with a vgetq_lane_f32 and we hope that the
        compiler is smart enough to replace the vget_lane_f32 with a direct access of the corresponding doubleword vector Dm[x].
        '''
    def __init__(self, src0, src1, src2, lane):
        '''We multiply src1 with src2[lane] and accumulate on src0.'''
        super(vmlaLaneqF32, self).__init__()
        self.srcs += [src0, src1, src2]
        self.lane = lane
    
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        src2val = self.srcs[2].computeSym(nameList)[self.lane]
        return [(src1[0] * src2val) + src0[0], (src1[1] * src2val) + src0[1]]
    
    def unparse(self, indent):
        return '%svmla_n_f32(%s, %s, vgetq_lane_f32(%s, %d))' % (indent, self.srcs[0].unparse(''), self.srcs[1].unparse(''), self.srcs[2].unparse(''), self.lane)
    
    def printInst(self, indent):
        return '%svmlaLaneqF32(%s, %s, %s[%d])' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''), self.srcs[2].printInst(''), self.lane)

class vdupNF32(RValue):
    '''Load all lanes of a doubleword vector to the same value.'''
    def __init__(self, src):
        super(vdupNF32, self).__init__()
        self.srcs += [src]
    
    def computeSym(self, nameList):
        sym = self.srcs[0].computeSym(nameList)[0]
        return [sym, sym]
    
    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        return [s0ZMask[0], s0ZMask[0]]
    
    def unparse(self, indent):
        return '%svdup_n_f32(%s)' % (indent, self.srcs[0].unparse(''))
    
    def printInst(self, indent):
        return '%svdupNF32(%s)' % (indent, self.srcs[0].printInst(''))

class vst1F32(MovStatement):
    '''Store a doubleword vector into memory.'''
    mrmap = [0,1] # static definition of the mem-reg mapping imposed by the store
    def __init__(self, src, dst):
        super(vst1F32, self).__init__()
        self.dst = VecDest(dst, 2, self.mrmap) if isinstance(dst, Pointer) else VecDest(dst.pointer, 2, self.mrmap)
        self.srcs += [src]
    
    def replaceRefs(self, refMap):
        dst = self.dst.replaceRefs(refMap)
        src = self.srcs[0].replaceRefs(refMap)
        if isinstance(dst, VecDest):
            self.dst = dst
            self.srcs[0] = src
            return self
        return Mov(src, dst)
    
    @staticmethod
    def canStore(reglen, mrmap, horizontal=True, isAligned=False):
        if not horizontal: return False
        return reglen == 2 and mrmap == vst1F32.mrmap
    
    @staticmethod
    def getStore(src, dst):
        return vst1F32(src, dst)
    
    def computeSym(self, nameList):
        return self.srcs[0].computeSym(nameList)
    
    def unparse(self, indent):
        return indent + "vst1_f32(" + self.dst.unparse("") + ", " + self.srcs[0].unparse("") + ");"
    
    def printInst(self, indent):
        return indent + "vst1F32( " + self.srcs[0].printInst("") + ", " + self.dst.printInst("") + " )"

class vst1LaneF32(MovStatement):
    '''Store a lane of a doubleword vector into memory.'''
    def __init__(self, src, dst, lane):
        '''Apart from the src and dst, we also need the lane as argument, since this instruction can be used to store
            any lane of the src vector into memory.'''
        super(vst1LaneF32, self).__init__()
        self.mrmap = [lane]
        self.dst = VecDest(dst, 2, self.mrmap) if isinstance(dst, Pointer) else VecDest(dst.pointer, 2, self.mrmap) # When passing VecAccess in ScaRep
        self.srcs += [src]
        self.lane = lane
        self.srcZMask = src.getZMask()
    
    @staticmethod
    def canStore(reglen, mrmap, horizontal=True, isAligned=False):
        return reglen == 2 and len(mrmap) == 1 and (isinstance(mrmap[0], int) or len(mrmap[0]) == 1)
    
    @staticmethod
    def getStore(src, dst):
        lane = dst.mrmap[0]
        if not isinstance(lane, int):
            lane = lane[0]
        return vst1LaneF32(src, dst, lane)
    
    def replaceRefs(self, refMap):
        '''Replace src and dst with their new references (according to refMap) and return an object that can replace self.'''
        dst = self.dst.replaceRefs(refMap)
        src = self.srcs[0].replaceRefs(refMap)
        # if the new destination is a VecDest we just need to update src and dest
        if isinstance(dst, VecDest):
            self.dst = dst
            self.srcs[0] = src
            return self
        return Mov(src, dst)
    
    def computeSym(self, nameList):
        return [self.srcs[0].computeSym(nameList)[self.lane]]
    
    def unparse(self, indent):
        return '%svst1_lane_f32(%s, %s, %d);' % (indent, self.dst.unparse(''), self.srcs[0].unparse(''), self.lane)
    
    def printInst(self, indent):
        return '%svst1LaneF32(%s, %s, %d)' % (indent, self.srcs[0].printInst(''), self.dst.printInst(''), self.lane)

#################################################################################################################
#------------------------------------------- Doubleword x 2 intrinsics -----------------------------------------#
#################################################################################################################

class vtrnF32(RValue):
    '''Doubleword vector transpose.
        
        The (2n+1)-th element of the first vector is swapped with the (2n)-element of the second. Two new vectors are returned.
        '''
    def __init__(self, src0, src1):
        super(vtrnF32, self).__init__()
        self.srcs += [src0, src1]
    
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [src0[0], src1[0], src0[1], src1[1]]
    
    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [s0ZMask[0], s1ZMask[0], s0ZMask[1], s1ZMask[1]]
    
    def unparse(self, indent):
        return '%svtrn_f32(%s, %s)' % (indent, self.srcs[0].unparse(''), self.srcs[1].unparse(''))
    
    def printInst(self, indent):
        return '%svtrnF32(%s, %s)' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''))

class vzipF32(RValue):
    '''Doubleword vector interleave.
        
        Dd = [A0, A1] , Dm = [B0, B1] --> Dd' = [A0, B0] , Dm' = [A1, B1]
        '''
    def __init__(self, src0, src1):
        super(vzipF32, self).__init__()
        self.srcs += [src0, src1]
    
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [src0[0], src1[0], src0[1], src1[1]]
    
    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [s0ZMask[0], s1ZMask[0], s0ZMask[1]]
    
    def unparse(self, indent):
        return '%svzip_f32(%s, %s)' % (indent, self.srcs[0].unparse(''), self.srcs[1].unparse(''))
    
    def printInst(self, indent):
        return '%svzipF32(%s, %s)' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''))

class vuzpF32(RValue):
    '''Doubleword vector de-interleave.
        
        Dd = [A0, A1] , Dm = [B0, B1] --> Dd' = [A0, B0] , Qm' = [A1, B1]
        '''
    def __init__(self, src0, src1):
        super(vuzpF32, self).__init__()
        self.srcs += [src0, src1]
    
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [src0[0], src1[0], src0[1], src1[1]]
    
    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [s0ZMask[0], s1ZMask[0], s0ZMask[1], s1ZMask[1]]
    
    def unparse(self, indent):
        return '%svuzp_f32(%s, %s)' % (indent, self.srcs[0].unparse(''), self.srcs[1].unparse(''))
    
    def printInst(self, indent):
        return '%svuzpF32(%s, %s)' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''))
    
#################################################################################################################
#--------------------------------------------- Quadword intrinsics ---------------------------------------------#
#################################################################################################################

class vldqGenF32(RValue, VecAccess):
    ''' Wrapper of a quadword load instruction.
        
        Useful when we want to represent a composite load instruction as a single logical instruction and then have it
        easily replaced by a scalar during scalar replacement.
        '''
    def __init__(self, pointer, mrmap, isCompact=False, isCorner=True, horizontal=True, zeromask=[]):
        super(vldqGenF32, self).__init__()
        self.pointer = pointer
        # this is an easy way to distinguish vertical from horizontal layouts
        #         self.mrmap = mrmap if horizontal else [-1 * el if isinstance(el, int) else tuple(-1 * elel for elel in el) for el in mrmap]
        self.mrmap = mrmap
        self.horizontal = horizontal
        self.orientation = 'horizontal' if horizontal else 'vertical'
        self.reglen = 4
        
        content = None
        if len(mrmap) == 1:
            lane = mrmap[0]
            content = vld1qLaneF32(pointer, vdupqNF32(sa(0)), lane, zeromask)
        elif mrmap == [0, 1]:
            if horizontal or isCompact:
                content = vcombineF32(vld1F32(pointer, zeromask), vdupNF32(sa(0)))
            else:
                zm0 = [0] if 0 in zeromask else []
                zm1 = [0] if 1 in zeromask else []
                p1 = Pointer((pointer.mat, (pointer.at[0] + 1, pointer.at[1])))
                content = vcombineF32(vld1LaneF32(p1, vld1DupF32(pointer, zm0), 1, zm1), vdupNF32(sa(0)))
        elif mrmap == [0, 1, 2]:
            if horizontal or isCompact:
                if isCorner:
                    zm0_1 = []
                    zm2 = []
                    for el in zeromask:
                        if el < 2:
                            zm0_1.append(el)
                        else:
                            zm2.append(el - 2)
                    p2 = Pointer((pointer.mat, (pointer.at[0], pointer.at[1] + 2)))
#                     content = vcombineF32(vld1F32(pointer, zm0_1), vld1LaneF32(p2, vdupNF32(sa(0)), 0, zm2))
                    if 0 in zm2: zm2 = [0, 1]
                    # TODO: Is it ok that the 4th element is not zero?
                    content = vcombineF32(vld1F32(pointer, zm0_1), vld1DupF32(p2, zm2))
                else:
#                     content = vsetqLaneF32(sa(0), vld1qF32(pointer, zeromask), 3)
                    # TODO: Is it ok that the 4th element is not zero?
                    content = vld1qF32(pointer, zeromask)
            else:
                ps = [pointer] + [Pointer((pointer.mat, (pointer.at[0] + i, pointer.at[1]))) for i in range(1, 3)]
                zms = [[0] if i in zeromask else [] for i in range(3)]
                v0_1 = vld1LaneF32(ps[1], vld1DupF32(ps[0], zms[0]), 1, zms[1])
                if isCorner:
                    v1_2 = vld1LaneF32(ps[2], vdupNF32(sa(0)), 0, zms[2])
                else:
                    if 0 in zms[2]: zms[2] = [0, 1]
                    # TODO: Is it ok that the 2nd element is not zero?
                    v1_2 = vld1DupF32(ps[2], zms[2])
                content = vcombineF32(v0_1, v1_2)
        elif mrmap == [0, 1, 2, 3]:
            if horizontal or isCompact:
                content = vld1qF32(pointer, zeromask)
            else:
                ps = [pointer] + [Pointer((pointer.mat, (pointer.at[0] + i, pointer.at[1]))) for i in range(1, 4)]
                zms = [[0] if i in zeromask else [] for i in range(4)]
                v0_1 = vld1LaneF32(ps[1], vld1DupF32(ps[0], zms[0]), 1, zms[1])
                v2_3 = vld1LaneF32(ps[3], vld1DupF32(ps[2], zms[2]), 1, zms[3])
                content = vcombineF32(v0_1, v2_3)
        
        if content is None:
            raise ValueError('vldqGenF32 does not support mrmap %s with %s layout yet' % (str(mrmap), 'horizontal' if horizontal else 'vertical'))
        self._content = content
    
    def computeSym(self, nameList):
        return self._content.computeSym(self, nameList)
    
    def getZMask(self):
        return self._content.getZMask()
    
    def unparse(self, indent):
        return self._content.unparse(indent)
    
    def printInst(self, indent):
        return 'vldqGenF32(%s, %s, %s)' % (str(self.mrmap), self.orientation, self._content.printInst(indent))
    
    def __eq__(self, other):
        return isinstance(other, VecAccess) and self.reglen == other.reglen and self.pointer == other.pointer and self.mrmap == other.mrmap and self.horizontal == other.horizontal
    
    def __hash__(self):
        return hash((hash('vldqGenF32'), self.pointer.mat, self.pointer.at, str(self.mrmap), self.orientation))

class vstqGenF32(MovStatement):
    '''Wrapper of a quadword store instruction.
        
        Useful when we want to represent a composite store instruction as a single logical instruction and then have it
        easily replaced by a scalar during scalar replacement.
        '''
    def __init__(self, src, dst, mrmap, isCompact=False, isCorner=True, horizontal=True):
        super(vstqGenF32, self).__init__()
        self.srcs += [src]
        self.mrmap = mrmap
        dstptr = dst if isinstance(dst, Pointer) else dst.pointer
        self.dst = VecDest(dstptr, 4, mrmap, horizontal, isCompact, isCorner)
        self.horizontal = horizontal
        self.isCompact = isCompact
        self.isCorner = isCorner
        self.orientation = 'horizontal' if horizontal else 'vertical'
        self.reglen = 4
    
    #         if not isinstance(dst, Pointer): dst = dst.pointer
    #         content = None
    #         if len(mrmap) == 1:
    #             lane = mrmap[0]
    #             content = [vst1qLaneF32(src, dst, lane)]
    #         elif mrmap == [0, 1]:
    #             if horizontal or isCompact:
    #                 content = [vst1F32(vgetLowF32(src), dst)]
    #             else:
    #                 p0 = dst
    #                 p1 = Pointer((dst.mat, (dst.at[0] + 1, dst.at[1])))
    #                 content = [vst1qLaneF32(src, p0, 0), vst1qLaneF32(src, p1, 1)]
    #         elif mrmap == [0, 1, 2]:
    #             if horizontal or isCompact:
    #                 p0 = dst
    #                 p2 = Pointer((dst.mat, (dst.at[0] + 2, dst.at[1])))
    #                 content = [vst1F32(vgetLowF32(src), p0), vst1qLaneF32(src, p2, 2)]
    #             else:
    #                 ps = [dst, Pointer((dst.mat, (dst.at[0] + 1, dst.at[1]))), Pointer((dst.mat, (dst.at[0] + 2, dst.at[1])))]
    #                 content = [vst1qLaneF32(src, ps[i], i) for i in range(3)]
    #         elif mrmap == [0, 1, 2, 3]:
    #             if horizontal or isCompact:
    #                 content = [vst1qF32(src, dst)]
    #             else:
    #                 ps = [dst] + [Pointer((dst.mat, (dst.at[0] + i, dst.at[1]))) for i in range(1, 4)]
    #                 content = [vst1qLaneF32(src, ps[i], i) for i in range(4)]
    #
    #         if content is None:
    #             raise ValueError('vstqGenF32 does not support mrmap %s with %s layout yet' % (str(mrmap), 'horizontal' if horizontal else 'vertical'))
    #         self._content = content
    
    @property
    def _content(self):
        dst = self.dst.pointer
        src = self.srcs[0]
        mrmap = self.mrmap
        horizontal = self.horizontal
        isCompact = self.isCompact
        content = None
        if len(mrmap) == 1:
            lane = mrmap[0]
            content = [vst1qLaneF32(src, dst, lane)]
        elif mrmap == [0, 1]:
            if horizontal or isCompact:
                content = [vst1F32(vgetLowF32(src), dst)]
            else:
                p0 = dst
                p1 = Pointer((dst.mat, (dst.at[0] + 1, dst.at[1])))
                content = [vst1qLaneF32(src, p0, 0), vst1qLaneF32(src, p1, 1)]
        elif mrmap == [0, 1, 2]:
            if horizontal or isCompact:
                p0 = dst
                p2 = Pointer((dst.mat, (dst.at[0], dst.at[1] + 2)))
                content = [vst1F32(vgetLowF32(src), p0), vst1qLaneF32(src, p2, 2)]
            else:
                ps = [dst, Pointer((dst.mat, (dst.at[0] + 1, dst.at[1]))), Pointer((dst.mat, (dst.at[0] + 2, dst.at[1])))]
                content = [vst1qLaneF32(src, ps[i], i) for i in range(3)]
        elif mrmap == [0, 1, 2, 3]:
            if horizontal or isCompact:
                content = [vst1qF32(src, dst)]
            else:
                ps = [dst] + [Pointer((dst.mat, (dst.at[0] + i, dst.at[1]))) for i in range(1, 4)]
                content = [vst1qLaneF32(src, ps[i], i) for i in range(4)]
        
        if content is None:
            raise ValueError('vstqGenF32 does not support mrmap %s with %s layout yet' % (str(mrmap), 'horizontal' if horizontal else 'vertical'))
        return content
    
    def replaceRefs(self, refMap):
        #         self._content = [c.replaceRefs(refMap) for c in self._content]
        dst = self.dst.replaceRefs(refMap)
        src = self.srcs[0].replaceRefs(refMap)
        if isinstance(dst, VecDest):
            self.dst = dst
            self.srcs[0] = src
            return self
        return Mov(src, dst)
    
    @staticmethod
    def canStore(reglen, mrmap, horizontal, isAligned=False):
        return reglen == 4
    
    @staticmethod
    def getStore(src, dst):
        mrmap = dst.mrmap
        if isinstance(mrmap, int):
            mrmap = [mrmap]
        return vstqGenF32(src, dst, mrmap, dst.isCompact, dst.isCorner, dst.horizontal)
    
    def computeSym(self, nameList):
        return self.srcs[0].computeSym(nameList)[:len(self.mrmap)]
    
    def unparse(self, indent):
        return '\n'.join(instr.unparse(indent) for instr in self._content)
    
    def printInst(self, indent):
        return 'vstqGenF32(%s, %s, %s)' % (str(self.mrmap), self.orientation, ','.join([instr.printInst(indent) for instr in self._content]))

class vld1qF32(RValue, VecAccess):
    '''Load a quadword vector from memory.'''
    def __init__(self, pointer, zeromask=None):
        super(vld1qF32, self).__init__()
        self.reglen = 4
        self.mrmap = [0,1,2,3]
        self.zeromask = [0]*self.reglen
        if zeromask is not None:
            for pos in zeromask:
                self.zeromask[pos] = 1
        self.pointer = pointer
    
    def computeSym(self, nameList):
        p = self.pointer.computeSym(nameList)
        return [sympify(p+'_0'), sympify(p+'_1'), sympify(p+'_2'), sympify(p+'_3')]
    
    def getZMask(self):
        return self.zeromask
    
    def unparse(self, indent):
        return '%svld1q_f32(%s)' % (indent, self.pointer.unparse(''))
    
    def printInst(self, indent):
        return '%svld1qF32(%s)' % (indent, self.pointer.printInst(''))
    
    def __eq__(self, other):
        return isinstance(other, vld1qF32) and self.pointer == other.pointer
    
    def __hash__(self):
        return hash((hash('vld1qF32'), self.pointer.mat, self.pointer.at))

class vld1qDupF32(RValue, VecAccess):
    '''Load all lanes of quadword vector with the same value from memory.'''
    def __init__(self, pointer, zeromask=None):
        super(vld1qDupF32, self).__init__()
        self.reglen = 4
        self.mrmap = [(0,1,2,3)]
        self.zeromask = [0]*self.reglen
        if zeromask is not None: # In this case all the positions have to be zero
            self.zeromask = [1]*self.reglen
        self.pointer = pointer
    
    def computeSym(self, nameList):
        p = self.pointer.computeSym(nameList)
        return [sympify(p+'_0'), sympify(p+'_0'), sympify(p+'_0'), sympify(p+'_0')]
    
    def getZMask(self):
        return self.zeromask
    
    def unparse(self, indent):
        return '%svld1q_dup_f32(%s)' % (indent, self.pointer.unparse(''))
    
    def printInst(self, indent):
        return '%svld1qDupF32(%s)' % (indent, self.pointer.printInst(''))
    
    def __eq__(self, other):
        return isinstance(other, vld1qDupF32) and self.pointer == other.pointer
    
    def __hash__(self):
        return hash((hash('vld1qDupF32'), self.pointer.mat, self.pointer.at))

class vld1qLaneF32(RValue, VecAccess):
    '''Load one of the lanes of a quadword vector from memory and the rest from another vector.'''
    def __init__(self, pointer, src, lane, zeromask=None):
        super(vld1qLaneF32, self).__init__()
        self.reglen = 4
        self.mrmap = [lane]
        self.zeromask = [0]*self.reglen
        if zeromask is not None:
            for pos in zeromask:
                self.zeromask[pos] = 1
        self.srcs += [src]
        self.pointer = pointer
        self.lane = lane
    
    def computeSym(self, nameList):
        p = self.pointer.computeSym(nameList)
        sym = self.srcs[0].computeSym(nameList)
        sym[self.lane] = sympify(p+'_0')
        return sym
    
    def getZMask(self):
        # TODO: Shouldn't we take into account the zeromask of src? In sse.mmLoadlPi we don't, while in mmMoveSs we do.
        return self.zeromask
    
    def unparse(self, indent):
        return '{indent}vld1q_lane_f32({ptr}, {vec}, {lane})'.format(indent=indent, ptr=self.pointer.unparse(''),
                                                                     vec=self.srcs[0].unparse(''), lane=self.lane)
    
    def printInst(self, indent):
        return '{indent}vld1qLaneF32({ptr}, {vec}, {lane})'.format(indent=indent, ptr=self.pointer.printInst(''),
                                                                   vec=self.srcs[0].printInst(''), lane=self.lane)
    
    def __eq__(self, other):
        return isinstance(other, vld1qLaneF32) and self.pointer == other.pointer and self.lane == other.lane
    
    def __hash__(self):
        return hash((hash("vld1qLaneF32"), self.pointer.mat, self.pointer.at, self.lane))

class vaddqF32(RValue):
    def __init__(self, src0, src1):
        super(vaddqF32, self).__init__()
        self.srcs += [src0, src1]
    
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [src0[0] + src1[0], src0[1] + src1[1], src0[2] + src1[2], src0[3] + src1[3]]
    
    def unparse(self, indent):
        return '%svaddq_f32(%s, %s)' % (indent, self.srcs[0].unparse(''), self.srcs[1].unparse(''))
    
    def printInst(self, indent):
        return '%svaddqF32(%s, %s)' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''))

def vpaddqF32(src0, src1):
    return vcombineF32(vpaddF32(vgetLowF32(src0), vgetHighF32(src0)), vpaddF32(vgetLowF32(src1), vgetHighF32(src1)))

class vmulqF32(RValue):
    '''Multiply two quadword vectors.'''
    def __init__(self, src0, src1):
        super(vmulqF32, self).__init__()
        self.srcs += [src0, src1]
    
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [src0[0] * src1[0], src0[1] * src1[1], src0[2] * src1[2], src0[3] * src1[3]]
    
    def unparse(self, indent):
        return '%svmulq_f32(%s, %s)' % (indent, self.srcs[0].unparse(''), self.srcs[1].unparse(''))
    
    def printInst(self, indent):
        return '%svmulqF32(%s, %s)' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''))

class vmulqLaneqF32(RValue):
    '''Multiply all elements of a quadword vector with one element of another quadword vector.
        
        Since there is no intrinsic for VMUL Qd,Qn,Dm[x], we combine a vmulq_n_f32 with a vgetq_lane_f32 and we hope that the
        compiler is smart enough to replace the vgetq_lane_f32 with a direct access of the corresponding doubleword vector Dm[x].
        '''
    def __init__(self, src0, src1, lane):
        super(vmulqLaneqF32, self).__init__()
        self.srcs += [src0, src1]
        self.lane = lane
    
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1val = self.srcs[1].computeSym(nameList)[self.lane]
        return [src0[0] * src1val, src0[1] * src1val, src0[2] * src1val, src0[3] * src1val]
    
    def unparse(self, indent):
        return '%svmulq_n_f32(%s, vgetq_lane_f32(%s, %d))' % (indent, self.srcs[0].unparse(''), self.srcs[1].unparse(''), self.lane)
    
    def printInst(self, indent):
        return '%svmulqLaneqF32(%s, %s, %d)' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''), self.lane)

class vmulqLaneF32(RValue):
    '''Multiply all elements of a quadword vector with one element of a doubleword vector.
        
        Since there is no intrinsic for VMUL Qd,Qn,Dm[x], we combine a vmulq_n_f32 with a vget_lane_f32 and we hope that the
        compiler is smart enough to replace the vget_lane_f32 with a direct access of the corresponding doubleword vector Dm[x].
        '''
    def __init__(self, src0, src1, lane):
        super(vmulqLaneF32, self).__init__()
        self.srcs += [src0, src1]
        self.lane = lane
    
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1val = self.srcs[1].computeSym(nameList)[self.lane]
        return [src0[0] * src1val, src0[1] * src1val, src0[2] * src1val, src0[3] * src1val]
    
    def unparse(self, indent):
        return '%svmulq_n_f32(%s, vget_lane_f32(%s, %d))' % (indent, self.srcs[0].unparse(''), self.srcs[1].unparse(''), self.lane)
    
    def printInst(self, indent):
        return '%svmulqLaneF32(%s, %s, %d)' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''), self.lane)

class vmlaqF32(RValue):
    '''Quadword vector multiply-accumulate.'''
    def __init__(self, src0, src1, src2):
        '''We multiply src1 with src2 and accumulate on src0.'''
        super(vmlaqF32, self).__init__()
        self.srcs += [src0, src1, src2]
    
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        src2 = self.srcs[2].computeSym(nameList)
        return [(src1[0] * src2[0]) + src0[0], (src1[1] * src2[1]) + src0[1], (src1[2] * src2[2]) + src0[2], (src1[3] * src2[3]) + src0[3]]
    
    def unparse(self, indent):
        return '%svmlaq_f32(%s, %s, %s)' % (indent, self.srcs[0].unparse(''), self.srcs[1].unparse(''), self.srcs[2].unparse(''))
    
    def printInst(self, indent):
        return '%svmlaqF32(%s, %s, %s)' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''), self.srcs[2].printInst(''))

class vmlaqLaneF32(RValue):
    '''Multiply all elements of a quadword vector with one element of a doubleword vector and accumulate the result on another quadword vector.
        
        Since there is no intrinsic for VMLA Qd,Qn,Dm[x], we combine a vmlaq_n_f32 with a vget_lane_f32 and we hope that the
        compiler is smart enough to replace the vget_lane_f32 with a direct access of the corresponding doubleword vector Dm[x].
        '''
    def __init__(self, src0, src1, src2, lane):
        '''We multiply src1 with src2[lane] and accumulate on src0.'''
        super(vmlaqLaneF32, self).__init__()
        self.srcs += [src0, src1, src2]
        self.lane = lane
    
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        src2val = self.srcs[2].computeSym(nameList)[self.lane]
        return [(src1[0] * src2val) + src0[0], (src1[1] * src2val) + src0[1], (src1[2] * src2val) + src0[2], (src1[3] * src2val) + src0[3]]
    
    def unparse(self, indent):
        return '%svmlaq_n_f32(%s, %s, vget_lane_f32(%s, %d))' % (indent, self.srcs[0].unparse(''), self.srcs[1].unparse(''), self.srcs[2].unparse(''), self.lane)
    
    def printInst(self, indent):
        return '%svmlaqLaneF32(%s, %s, %s[%d])' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''), self.srcs[2].printInst(''), self.lane)

class vmlaqLaneqF32(RValue):
    '''Multiply all elements of a quadword vector with one element of another quadword vector and accumulate result on another vector.
        
        Since there is no intrinsic for VMLA Qd,Qn,Dm[x], we combine a vmlaq_n_f32 with a vgetq_lane_f32 and we hope that the
        compiler is smart enough to replace the vgetq_lane_f32 with a direct access of the corresponding doubleword vector Dm[x].
        '''
    def __init__(self, src0, src1, src2, lane):
        '''We multiply src1 with src2[lane] and accumulate on src0.'''
        super(vmlaqLaneqF32, self).__init__()
        self.srcs += [src0, src1, src2]
        self.lane = lane
    
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        src2val = self.srcs[2].computeSym(nameList)[self.lane]
        return [(src1[0] * src2val) + src0[0], (src1[1] * src2val) + src0[1], (src1[2] * src2val) + src0[2], (src1[3] * src2val) + src0[3]]
    
    def unparse(self, indent):
        return '%svmlaq_n_f32(%s, %s, vgetq_lane_f32(%s, %d))' % (indent, self.srcs[0].unparse(''), self.srcs[1].unparse(''), self.srcs[2].unparse(''), self.lane)
    
    def printInst(self, indent):
        return '%svmlaqLaneqF32(%s, %s, %s[%d])' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''), self.srcs[2].printInst(''), self.lane)

class vsetqLaneF32(RValue):
    '''Load one of the lanes of a quadword vector from a literal and the rest from another vector.'''
    def __init__(self, val, src, lane):
        super(vsetqLaneF32, self).__init__()
        self.srcs += [val, src]
        self.lane = lane
    
    def computeSym(self, nameList):
        return [self.srcs[0].computeSym(nameList)[0] if i == self.lane else self.srcs[1].computeSym(nameList)[i] for i in range(4)]
    
    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [s0ZMask[0] if i == self.lane else s1ZMask[i] for i in range(4)]
    
    def unparse(self, indent):
        return '{indent}vsetq_lane_f32({value}, {vec}, {lane})'.format(indent=indent, value=self.srcs[0].unparse(''), vec=self.srcs[1].unparse(''), lane=self.lane)
    
    def printInst(self, indent):
        return '{indent}vsetqLaneF32({value}, {vec}, {lane})'.format(indent=indent, value=self.srcs[0].printInst(''), vec=self.srcs[1].printInst(''), lane=self.lane)

class vdupqNF32(RValue):
    '''Load all lanes of a quadword vector to the same value.'''
    def __init__(self, src):
        super(vdupqNF32, self).__init__()
        self.srcs += [src]
    
    def computeSym(self, nameList):
        sym = self.srcs[0].computeSym(nameList)[0]
        return [sym, sym, sym, sym]
    
    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        return [s0ZMask[0], s0ZMask[0], s0ZMask[0], s0ZMask[0]]
    
    def unparse(self, indent):
        return '%svdupq_n_f32(%s)' % (indent, self.srcs[0].unparse(''))
    
    def printInst(self, indent):
        return '%svdupqNF32(%s)' % (indent, self.srcs[0].printInst(''))

class vdupqLaneF32(RValue):
    '''Load all lanes of a quadword vector to the value of a lane of a doubleword vector.'''
    def __init__(self, src, lane):
        super(vdupqLaneF32, self).__init__()
        self.srcs += [src]
        self.lane = lane
    
    def computeSym(self, nameList):
        sym = self.srcs[0].computeSym(nameList)[self.lane]
        return [sym, sym, sym, sym]
    
    def getZMask(self):
        zm = self.srcs[0].getZMask()[self.lane]
        return [zm, zm, zm, zm]
    
    def unparse(self, indent):
        return '%svdupq_lane_f32(%s, %d)' % (indent, self.srcs[0].unparse(''), self.lane)
    
    def printInst(self, indent):
        return '%svdupqLaneF32(%s, %d)' % (indent, self.srcs[0].printInst(''), self.lane)

class vcombineF32(RValue):
    '''Combine two doubleword vectors into one quadword vector.'''
    def __init__(self, src0, src1):
        super(vcombineF32, self).__init__()
        self.srcs += [src0, src1]
    
    def computeSym(self, nameList):
        sym0 = self.srcs[0].computeSym(nameList)[self.lane]
        sym1 = self.srcs[1].computeSym(nameList)[self.lane]
        return [sym0[0], sym0[1], sym1[0], sym1[1]]
    
    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [s0ZMask[0], s0ZMask[1], s1ZMask[0], s1ZMask[1]]
    
    def unparse(self, indent):
        return '%svcombine_f32(%s, %s)' % (indent, self.srcs[0].unparse(''), self.srcs[1].unparse(''))
    
    def printInst(self, indent):
        return '%svcombineF32(%s, %s)' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''))

class vextqF32(RValue):
    '''Quadword vector extract.
        
        The two quadword vectors are concatenated, shifted to the left and the 4 least significant words are returned in the
        result quadword vector (assume lefttmost = least significant). Since the NEON intrinsics don't support floating-point vector extract,
        we convert to unsinged int vectors, we extract and finally we convert back to floating point vector.
        '''
    def __init__(self, src0, src1, imm):
        '''The two quadword vector arguments are concatenated in the order they are given and then shifted to the left by imm words
            (assume leftmost = least significant)'''
        super(vextqF32, self).__init__()
        if imm < 0 or imm > 3:
            raise ValueError('Expected imm in the range [0,3], but received imm = %d.' % imm)
        self.srcs += [src0, src1]
        # number of 32-bit elements the combination [src0 | src1 ] should be shifted to the left
        # (assume leftmost = least significant)
        self.imm = imm
    
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        conc = src0 + src1
        return conc[self.imm:self.imm+4]
    
    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        conc = s0ZMask + s1ZMask
        return conc[self.imm:self.imm+4]
    
    def unparse(self, indent):
        return '%svreinterpretq_f32_u32(vextq_u32(vreinterpretq_u32_f32(%s), vreinterpretq_u32_f32(%s), %d)' % (indent,
                                                                                                                self.srcs[0].unparse(''), self.srcs[1].unparse(''), self.imm)
    
    def printInst(self, indent):
        return '%svextqF32(%s, %s)' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''))

class vst1qF32(MovStatement):
    '''Store a quadword vector into memory.'''
    mrmap = [0,1,2,3] # static definition of the mem-reg mapping imposed by the store
    def __init__(self, src, dst):
        super(vst1qF32, self).__init__()
        self.dst = VecDest(dst, 4, self.mrmap) if isinstance(dst, Pointer) else VecDest(dst.pointer, 4, self.mrmap)
        self.srcs += [src]
    
    def replaceRefs(self, refMap):
        dst = self.dst.replaceRefs(refMap)
        src = self.srcs[0].replaceRefs(refMap)
        if isinstance(dst, VecDest):
            self.dst = dst
            self.srcs[0] = src
            return self
        return Mov(src, dst)
    
    @staticmethod
    def canStore(reglen, mrmap, horizontal=True, isAligned=False):
        if not horizontal: return False
        return reglen == 4 and mrmap == vst1qF32.mrmap
    
    @staticmethod
    def getStore(src, dst):
        return vst1qF32(src, dst)
    
    def computeSym(self, nameList):
        return self.srcs[0].computeSym(nameList)
    
    def unparse(self, indent):
        return '%svst1q_f32(%s, %s);' % (indent, self.dst.unparse(''), self.srcs[0].unparse(''))
    
    def printInst(self, indent):
        return "%svst1qF32( %s, %s )" % (indent, self.srcs[0].printInst(''), self.dst.printInst(''))

class vst1qLaneF32(MovStatement):
    '''Store a lane of a quadword vector into memory.'''
    def __init__(self, src, dst, lane):
        '''Apart from the src and dst, we also need the lane as argument, since this instruction can be used to store
            any lane of the src vector into memory.'''
        super(vst1qLaneF32, self).__init__()
        self.mrmap = [lane]
        self.dst = VecDest(dst, 4, self.mrmap) if isinstance(dst, Pointer) else VecDest(dst.pointer, 4, self.mrmap) # When passing VecAccess in ScaRep
        self.srcs += [src]
        self.lane = lane
        self.srcZMask = src.getZMask()
    
    @staticmethod
    def canStore(reglen, mrmap, horizontal=True, isAligned=False):
        return reglen == 4 and len(mrmap) == 1 and (isinstance(mrmap[0], int) or len(mrmap[0]) == 1)
    
    @staticmethod
    def getStore(src, dst):
        lane = dst.mrmap[0]
        if not isinstance(lane, int):
            lane = lane[0]
        return vst1qLaneF32(src, dst, lane)
    
    def replaceRefs(self, refMap):
        '''Replace src and dst with their new references (according to refMap) and return an object that can replace self.'''
        dst = self.dst.replaceRefs(refMap)
        src = self.srcs[0].replaceRefs(refMap)
        # if the new destination is a VecDest we just need to update src and dest
        if isinstance(dst, VecDest):
            self.dst = dst
            self.srcs[0] = src
            return self
        return Mov(src, dst)
    
    def computeSym(self, nameList):
        return [self.srcs[0].computeSym(nameList)[self.lane]]
    
    def unparse(self, indent):
        return '%svst1q_lane_f32(%s, %s, %d);' % (indent, self.dst.unparse(''), self.srcs[0].unparse(''), self.lane)
    
    def printInst(self, indent):
        return '%svst1qLaneF32(%s, %s, %d)' % (indent, self.srcs[0].printInst(''), self.dst.printInst(''), self.lane)

class vaccessStructureF32(RValue):
    '''Access a quadword vector from within a float32x2x2_t or float32x2x4_t or float32x4x2_t or float32x4x4_t structure.'''
    def __init__(self, src, pos):
        super(vaccessStructureF32, self).__init__()
        self.srcs += [src]
        self.pos = pos
    
    def computeSym(self, nameList):
        return self.srcs[0].computeSym(nameList)[2:]
    
    def getZMask(self):
        return self.srcs[0].getZMask()[2:]
    
    def unparse(self, indent):
        return '%s%s.val[%d]' % (indent, self.srcs[0].unparse(''), self.pos)
    
    def printInst(self, indent):
        return '%svaccessStructureF32(%s, %d)' % (indent, self.srcs[0].printInst(''), self.pos)

#################################################################################################################
#-------------------------------------------- Quadword x 2 intrinsics -------------------------------------------#
#################################################################################################################

class vtrnqF32(RValue):
    '''Quadword vector transpose.
        
        The (2n+1)-th element of the first vector is swapped with the (2n)-element of the second. Two new vectors are returned.
        '''
    def __init__(self, src0, src1):
        super(vtrnqF32, self).__init__()
        self.srcs += [src0, src1]
    
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [src0[0], src1[0], src0[2], src1[2], src0[1], src1[1], src0[3], src1[3]]
    
    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [s0ZMask[0], s1ZMask[0], s0ZMask[2], s1ZMask[2], s0ZMask[1], s1ZMask[1], s0ZMask[3], s1ZMask[3]]
    
    def unparse(self, indent):
        return '%svtrnq_f32(%s, %s)' % (indent, self.srcs[0].unparse(''), self.srcs[1].unparse(''))
    
    def printInst(self, indent):
        return '%svtrnqF32(%s, %s)' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''))

class vzipqF32(RValue):
    '''Quadword vector interleave.
        
        Qd = [A0, A1, A2, A3] , Qm = [B0, B1, B2, B3] --> Qd' = [A0, B0, A1, B1] , Qm' = [A2, B2, A3, B3]
        '''
    def __init__(self, src0, src1):
        super(vzipqF32, self).__init__()
        self.srcs += [src0, src1]
    
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [src0[0], src1[0], src0[1], src1[1], src0[2], src1[2], src0[3], src1[3]]
    
    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [s0ZMask[0], s1ZMask[0], s0ZMask[1], s1ZMask[1], s0ZMask[2], s1ZMask[2], s0ZMask[3], s1ZMask[3]]
    
    def unparse(self, indent):
        return '%svzipq_f32(%s, %s)' % (indent, self.srcs[0].unparse(''), self.srcs[1].unparse(''))
    
    def printInst(self, indent):
        return '%svzipqF32(%s, %s)' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''))

class vuzpqF32(RValue):
    '''Quadword vector de-interleave.
        
        Qd = [A0, A1, A2, A3] , Qm = [B0, B1, B2, B3] --> Qd' = [A0, A2, B0, B2] , Qm' = [A1, A3, B1, B3]
        '''
    def __init__(self, src0, src1):
        super(vuzpqF32, self).__init__()
        self.srcs += [src0, src1]
    
    def computeSym(self, nameList):
        src0 = self.srcs[0].computeSym(nameList)
        src1 = self.srcs[1].computeSym(nameList)
        return [src0[0], src0[2], src1[0], src1[2], src0[1], src0[3], src1[1], src1[3]]
    
    def getZMask(self):
        s0ZMask = self.srcs[0].getZMask()
        s1ZMask = self.srcs[1].getZMask()
        return [s0ZMask[0], s0ZMask[2], s1ZMask[0], s1ZMask[2], s0ZMask[1], s0ZMask[3], s1ZMask[1], s1ZMask[3]]
    
    def unparse(self, indent):
        return '%svuzpq_f32(%s, %s)' % (indent, self.srcs[0].unparse(''), self.srcs[1].unparse(''))
    
    def printInst(self, indent):
        return '%svuzpqF32(%s, %s)' % (indent, self.srcs[0].printInst(''), self.srcs[1].printInst(''))


class _Flt4Loader(Loader):
    def __init__(self):
        super(_Flt4Loader, self).__init__()
    
    def loadMatrix(self, mParams):
        # src: submatrix of original matrix, dst: nu-matrix
        src, dst = mParams['m'], mParams['nuM']
        # IMFs for source
        sL, sR = mParams['mL'], mParams['mR']
        # IMFs for destination
        dL, dR = mParams['nuML'], mParams['nuMR']
        # dimensions of source
        M, N = mParams['M'], mParams['N']
        isCompact, isCorner = mParams['compact'], mParams['corner']
        instructions = []
        
        if M == 1:
            if N == 1:
                v0 = vldGenF32(AddressOf(sa(src[sL.of(0),sR.of(0)])), [0], isCompact, isCorner)
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = vstGenF32(v0, pc, [0, 1])
                instructions.extend([Comment('1x1 -> 1x2'), instr])
            #             elif N == 2:
            #                 v0_1 = vldGenF32(Pointer(src[sL.of(0),sR.of(0)]), [0, 1], isCompact, isCorner)
            #                 pc = Pointer(dst[dL.of(0),dR.of(0)])
            #                 instr = vstGenF32(v0_1, pc, [0, 1])
            #                 instructions.extend([Comment('1x1 -> 1x2'), instr])
            elif N == 3:
                v0_2 = vldqGenF32(Pointer(src[sL.of(0),sR.of(0)]), [0, 1, 2], isCompact, isCorner)
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = vstqGenF32(v0_2, pc, [0, 1, 2, 3])
                instructions.extend([Comment('1x3 -> 1x4'), instr])
        elif M == 2:
            if N == 1 and not isCompact:
                v0_1 = vldGenF32(Pointer(src[sL.of(0),sR.of(0)]), [0, 1], isCompact, isCorner, horizontal=False)
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                comm = Comment('2x1 -> 2x1 - Incompact')
                instr = vstGenF32(v0_1, pc, [0, 1])
                instructions.extend([comm, instr])
            elif N == 2 and isCompact:
                pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(2)]
                v0_4 = vldqGenF32(Pointer(src[sL.of(0),sR.of(0)]), [0, 1, 2, 3], isCompact, isCorner)
                v0_1 = vgetLowF32(v0_4)
                v2_3 = vgetHighF32(v0_4)
                instr0 = vstGenF32(v0_1, pcs[0], [0, 1])
                instr1 = vstGenF32(v2_3, pcs[1], [0, 1])
                comm = Comment('2x2 -> 2x2 - Compact')
                instructions.extend([comm, instr0, instr1])
            elif N == 3:
                v0_2 = vldqGenF32(Pointer(src[sL.of(0),sR.of(0)]), [0, 1, 2], isCompact, isCorner=False)
                v3_5 = vldqGenF32(Pointer(src[sL.of(1),sR.of(0)]), [0, 1, 2], isCompact, isCorner=isCorner)
                pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(2)]
                instr0 = vstqGenF32(v0_2, pcs[0], [0, 1, 2, 3])
                instr1 = vstqGenF32(v3_5, pcs[1], [0, 1, 2, 3])
                comm = Comment('2x3 -> 2x4 - %sCorner' % ('' if isCorner else 'not '))
                instructions.extend([comm, instr0, instr1])
        #             elif N == 4:
        #                 v0_3 = vldqGenF32(Pointer(src[sL.of(0),sR.of(0)]), [0, 1, 2, 3], isCompact, isCorner=False)
        #                 v4_7 = vldqGenF32(Pointer(src[sL.of(1),sR.of(0)]), [0, 1, 2, 3], isCompact, isCorner=isCorner)
        #                 pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(2)]
        #                 instr0 = vstqGenF32(v0_3, pcs[0], [0, 1, 2, 3])
        #                 instr1 = vstqGenF32(v4_7, pcs[1], [0, 1, 2, 3])
        #                 instructions.extend([Comment('2x4 -> 2x4'), instr0, instr1])
        elif M == 3:
            if N == 1:
                v0_2 = vldqGenF32(Pointer(src[sL.of(0),sR.of(0)]), [0, 1, 2], isCompact, isCorner, horizontal=False)
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = vstqGenF32(v0_2, pc, [0, 1, 2, 3])
                comm = Comment('3x1 -> 4x1 - %s' % ('Compact' if isCompact else 'Incompact'))
                instructions.extend([comm, instr])
            elif N == 2 and isCompact:
                v0_3 = vldqGenF32(Pointer(src[sL.of(0),sR.of(0)]), [0, 1, 2, 3], isCompact, isCorner=False)
                v4_5 = vldGenF32(Pointer(src[sL.of(2),sR.of(0)]), [0, 1], isCompact, isCorner=isCorner)
                v0_1 = vgetLowF32(v0_3)
                v2_3 = vgetHighF32(v0_3)
                pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(3)]
                instr0 = vstGenF32(v0_1, pcs[0], [0, 1])
                instr1 = vstGenF32(v2_3, pcs[1], [0, 1])
                instr2 = vstGenF32(v4_5, pcs[2], [0, 1])
                instructions.extend([Comment('3x2 -> 3x2'), instr0, instr1, instr2])
            elif N == 3:
                v0_2 = vldqGenF32(Pointer(src[sL.of(0),sR.of(0)]), [0, 1, 2], isCompact, isCorner=False)
                v3_5 = vldqGenF32(Pointer(src[sL.of(1),sR.of(0)]), [0, 1, 2], isCompact, isCorner=False)
                v6_8 = vldqGenF32(Pointer(src[sL.of(2),sR.of(0)]), [0, 1, 2], isCompact, isCorner=isCorner)
                comm = Comment('3x3 -> 3x4 - %sCorner' % ('' if isCorner else 'not '))
                pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(3)]
                instr0 = vstqGenF32(v0_2, pcs[0], [0, 1, 2, 3])
                instr1 = vstqGenF32(v3_5, pcs[1], [0, 1, 2, 3])
                instr2 = vstqGenF32(v6_8, pcs[2], [0, 1, 2, 3])
                instructions.extend([comm, instr0, instr1, instr2])
        #             elif N == 4:
        #                 rows = [vldqGenF32(Pointer(src[sL.of(i),sR.of(0)]), [0, 1, 2, 3], isCompact, isCorner=False) for i in range(2)]
        #                 rows.append(vldqGenF32(Pointer(src[sL.of(2),sR.of(0)]), [0, 1, 2, 3], isCompact, isCorner=isCorner))
        #                 pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(3)]
        #                 instrs = [vstqGenF32(rows[i], pcs[i], [0, 1, 2, 3]) for i in range(3)]
        #                 instructions.extend([Comment('3x4 -> 3x4')] + instrs)
        elif M == 4:
            if N == 1 and not isCompact:
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = vstqGenF32(vldqGenF32(Pointer(src[sL.of(0),sR.of(0)]), [0, 1, 2, 3], isCompact=isCompact, isCorner=isCorner, horizontal=False), pc, [0, 1, 2, 3])
                instructions.extend([Comment('4x1 -> 4x1 - Incompact'), instr])
            elif N == 2 and isCompact:
                pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
                v0_3 = vldqGenF32(Pointer(src[sL.of(0),sR.of(0)]), [0, 1, 2, 3], isCompact=isCompact, isCorner=False)
                v4_7 = vldqGenF32(Pointer(src[sL.of(2),sR.of(0)]), [0, 1, 2, 3], isCompact=isCompact, isCorner=isCorner)
                v0_1 = vgetLowF32(v0_3)
                v2_3 = vgetHighF32(v0_3)
                v4_5 = vgetLowF32(v4_7)
                v6_7 = vgetHighF32(v4_7)
                instr0 = vstGenF32(v0_1, pcs[0], [0, 1])
                instr1 = vstGenF32(v2_3, pcs[1], [0, 1])
                instr2 = vstGenF32(v4_5, pcs[2], [0, 1])
                instr3 = vstGenF32(v6_7, pcs[3], [0, 1])
                comm = Comment('4x2 -> 4x2 - Compact')
                instructions.extend([comm, instr0, instr1, instr2, instr3])
            elif N == 3:
                v0_2 = vldqGenF32(Pointer(src[sL.of(0),sR.of(0)]), [0, 1, 2], isCompact=isCompact, isCorner=False)
                v3_5 = vldqGenF32(Pointer(src[sL.of(1),sR.of(0)]), [0, 1, 2], isCompact=isCompact, isCorner=False)
                v6_8 = vldqGenF32(Pointer(src[sL.of(2),sR.of(0)]), [0, 1, 2], isCompact=isCompact, isCorner=False)
                v9_11 = vldqGenF32(Pointer(src[sL.of(3),sR.of(0)]), [0, 1, 2], isCompact=isCompact, isCorner=isCorner)
                pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
                instr0 = vstqGenF32(v0_2, pcs[0], [0, 1, 2, 3])
                instr1 = vstqGenF32(v3_5, pcs[1], [0, 1, 2, 3])
                instr2 = vstqGenF32(v6_8, pcs[2], [0, 1, 2, 3])
                instr3 = vstqGenF32(v9_11, pcs[3], [0, 1, 2, 3])
                comm =  Comment('4x3 -> 4x4 - %sCorner' % ('' if isCorner else 'not '))
                instructions.extend([comm, instr0, instr1, instr2, instr3])
        
        return instructions

class _Flt4BLAC(object):
    def __init__(self):
        super(_Flt4BLAC, self).__init__()
    
    def Add(self, s0Params, s1Params, dParams, opts):
        # these are the 3 Matrix objects involved
        src0, src1, dst = s0Params['nuM'], s1Params['nuM'], dParams['nuM']
        # these are the IMFs of each of the three matrices
        s0L, s0R = s0Params['nuML'], s0Params['nuMR']
        s1L, s1R = s1Params['nuML'], s1Params['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        # these are the sizes of the nu-matrices
        M, N     = dParams['nuMM'], dParams['nuMN']
        nu       = N if N > 1 else M    # size of the vectors to be used
        nvec     = M if N > 1 else 1    # number of vectors to be used
        instructions = []
        
        instructions.append(Comment('%d/%d - BLAC: %dx%d + %dx%d' % (nu, nu, M, N, M, N)))
        if nu == 2:
            loadInstr = vldGenF32
            storeInstr = vstGenF32
            addInstr = vaddF32
        elif nu == 4:
            loadInstr = vldqGenF32
            storeInstr = vstqGenF32
            addInstr = vaddqF32
        mrmap = range(nu)
        for i in range(nvec):
            va = loadInstr(Pointer(src0[s0L.of(i),s0R.of(0)]), mrmap)
            vb = loadInstr(Pointer(src1[s1L.of(i),s1R.of(0)]), mrmap)
            pc = Pointer(dst[dL.of(i),dR.of(0)])
            instructions.append(storeInstr(addInstr(va, vb), pc, mrmap))
        
        return instructions
    
    def Kro(self, s0Params, s1Params, dParams, opts):
        
        src0, src1, dst = s0Params['nuM'], s1Params['nuM'], dParams['nuM']
        s0L, s0R = s0Params['nuML'], s0Params['nuMR']
        s1L, s1R = s1Params['nuML'], s1Params['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        oM, oK, oN, oP = s0Params['M'], s0Params['N'], s1Params['M'], s1Params['N']
        M, K, N, P = s0Params['nuMM'], s0Params['nuMN'], s1Params['nuMM'], s1Params['nuMN']
        nu0, nu1 = K if K > 1 else M, P if P > 1 else N
        instructions = []
        
        instructions += [Comment("%d/%d - BLAC: %dx%d Kro %dx%d" % (nu0, nu1, M, K, N, P))]
        
        if oM*oK == 1:
            va = vldGenF32(Pointer(src0[s0L.of(0),s0R.of(0)]), [0, 1])
            if oN*oP == 1:
                vb = vldGenF32(Pointer(src1[s1L.of(0),s1R.of(0)]), [0, 1])
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instructions.append(vstGenF32(vmulF32(va, vb), pc, [0, 1]))
            else:
                if nu1 == 2:
                    loadInstr = vldGenF32
                    storeInstr = vstGenF32
                    mulLaneInstr = vmulLaneF32
                elif nu1 == 4:
                    loadInstr = vldqGenF32
                    storeInstr = vstqGenF32
                    mulLaneInstr = vmulqLaneF32
                mrmap = range(nu1)
                nvec = N if P > 1 else 1
                for i in range(nvec):
                    vb = loadInstr(Pointer(src1[s1L.of(i),s1R.of(0)]), mrmap)
                    pc = Pointer(dst[dL.of(i),dR.of(0)])
                    instructions.append(storeInstr(mulLaneInstr(vb, va, 0), pc, mrmap))
        elif oN*oP == 1:
            vb = vldGenF32(Pointer(src1[s1L.of(0),s1R.of(0)]), [0, 1])
            if nu0 == 2:
                loadInstr = vldGenF32
                storeInstr = vstGenF32
                mulLaneInstr = vmulLaneF32
            elif nu0 == 4:
                loadInstr = vldqGenF32
                storeInstr = vstqGenF32
                mulLaneInstr = vmulqLaneF32
            mrmap = range(nu0)
            nvec = M if K > 1 else 1
            for i in range(nvec):
                va = loadInstr(Pointer(src0[s0L.of(i),s0R.of(0)]), mrmap)
                pc = Pointer(dst[dL.of(i),dR.of(0)])
                instructions.append(storeInstr(mulLaneInstr(va, vb, 0), pc, mrmap))
        else:
            raise Exception('%dx%d Kro %dx%d not supported yet' % (oM, oK, oN, oP))
        
        return instructions
    
    def Mul(self, s0Params, s1Params, dParams, opts):
        
        src0, src1, dst = s0Params['nuM'], s1Params['nuM'], dParams['nuM']
        s0L, s0R = s0Params['nuML'], s0Params['nuMR']
        s1L, s1R = s1Params['nuML'], s1Params['nuMR']
        dL, dR   = dParams['nuML'], dParams['nuMR']
        M, K, N, P = s0Params['nuMM'], s0Params['nuMN'], s1Params['nuMM'], s1Params['nuMN']
        oM, oK, oN = s0Params['M'], s0Params['N'], s1Params['N']
        nu0 = K if K > 1 else M
        nu1 = P if P > 1 else N
        instructions = [ Comment("%d/%d - BLAC: %dx%d * %dx%d (originally %dx%d * %dx%d)" % (nu0, nu1, M, K, N, P, oM, oK, oK, oN)) ]
        
        if oM > 1 and oK > 1 and oN > 1:
            if nu0 == 2:
                loadInstra = vldGenF32
                if nu1 == 2:
                    mulInstr = vmulLaneF32
                    mlaInstr = vmlaLaneF32
                elif nu1 == 4:
                    mulInstr = vmulqLaneF32
                    mlaInstr = vmlaqLaneF32
            elif nu0 == 4:
                loadInstra = vldqGenF32
                if nu1 == 2:
                    mulInstr = vmulLaneqF32
                    mlaInstr = vmlaLaneqF32
                elif nu1 == 4:
                    mulInstr = vmulqLaneqF32
                    mlaInstr = vmlaqLaneqF32
            if nu1 == 2:
                loadInstrb = vldGenF32
                storeInstr = vstGenF32 
            elif nu1 == 4: 
                loadInstrb = vldqGenF32
                storeInstr = vstqGenF32
            mrmapa = range(nu0)
            mrmapb = range(nu1)
            vas = [loadInstra(Pointer(src0[s0L.of(i),s0R.of(0)]), mrmapa) for i in range(oM)]
            vbs = [loadInstrb(Pointer(src1[s1L.of(i),s1R.of(0)]), mrmapb) for i in range(oK)]
            pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(oM)]
            muls = [mulInstr(vbs[0], va, 0) for va in vas]
            for i in range(1, oK):
                ress = [mlaInstr(mul, vbs[i], va, i) for va, mul in zip(vas, muls)]
                muls = ress
            instructions.extend([storeInstr(res, pc, mrmapb) for res, pc in zip(ress, pcs)])
            
        elif oM == 1:
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            if oK == 2:
                va = vldGenF32(Pointer(src0[s0L.of(0),s0R.of(0)]), [0, 1])
                if oN == 1:
                    vb = vldGenF32(Pointer(src1[s1L.of(0),s1R.of(0)]), [0, 1])
                    mul = vmulF32(va, vb)
                    res = vpaddF32(mul, mul)
                    instructions.append(vstGenF32(res, pc, [0, 1]))
                elif oN == 2:
                    vb = [vldGenF32(Pointer(src1[s1L.of(i),s1R.of(0)]), [0, 1]) for i in range(oK)]
                    mul0 = vmulLaneF32(vb[0], va, 0)
                    res = vmlaLaneF32(mul0, vb[1], va, 1)
                    instructions.append(vstGenF32(res, pc, [0, 1]))
                elif oN in [3, 4]:
                    vb = [vldqGenF32(Pointer(src1[s1L.of(i),s1R.of(0)]), [0, 1, 2, 3]) for i in range(oK)]
                    mul0 = vmulqLaneF32(vb[0], va, 0)
                    res = vmlaqLaneF32(mul0, vb[1], va, 1)
                    instructions.append(vstqGenF32(res, pc, [0, 1, 2, 3]))
            elif oK in [3, 4]:
                va = vldqGenF32(Pointer(src0[s0L.of(0),s0R.of(0)]), [0, 1, 2, 3])
                if oN == 1:
                    vb = vldqGenF32(Pointer(src1[s1L.of(0),s1R.of(0)]), [0, 1, 2, 3])
                    if oK == 3:
                        mul = vmulqF32(va, vb)
                        padd = vpaddF32(vgetLowF32(mul), vgetLowF32(mul))
                        # TODO: Is it ok that the last element is not zero?
                        res = vaddF32(vgetHighF32(mul), padd)
                        # the following approach is slightly slower (at least with clang++)
    #                     mul = vmulF32(vgetLowF32(va), vgetLowF32(vb))
    #                     padd = vpaddF32(mul, mul)
    #                     res = vmlaF32(padd, vgetHighF32(va), vgetHighF32(vb))
                    else:
                        mul0 = vmulF32(vgetLowF32(va), vgetLowF32(vb))
                        add = vmlaF32(mul0, vgetHighF32(va), vgetHighF32(vb))
                        res = vpaddF32(add, add)
                    instructions.append(vstGenF32(res, pc, [0, 1]))
                elif oN == 2:
                    vb = [vldGenF32(Pointer(src1[s1L.of(i),s1R.of(0)]), [0, 1]) for i in range(oK)]
                    res = vmulLaneqF32(vb[0], va, 0)
                    for i in range(1, oK):
                        res = vmlaLaneqF32(res, vb[i], va, i)
                    instructions.append(vstGenF32(res, pc, [0, 1]))
                elif oN in [3, 4]:
                    vb = [vldqGenF32(Pointer(src1[s1L.of(i),s1R.of(0)]), [0, 1, 2, 3]) for i in range(oK)]
                    res = vmulqLaneqF32(vb[0], va, 0)
                    for i in range(1, oK):
                        res = vmlaqLaneqF32(res, vb[i], va, i)
                    instructions.append(vstqGenF32(res, pc, [0, 1, 2, 3]))
        elif oM == 2:
            if oK == 1:
                va = vldGenF32(Pointer(src0[s0L.of(0),s0R.of(0)]), [0, 1])
                if nu1 == 2:
                    loadInstr = vldGenF32
                    mulInstr = vmulLaneF32
                    storeInstr = vstGenF32
                elif nu1 == 4:
                    loadInstr = vldqGenF32
                    mulInstr = vmulqLaneF32
                    storeInstr = vstqGenF32
                vb = loadInstr(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu1))
                res = [mulInstr(vb, va, i) for i in range(oM)]
                pc = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(oM)]
                instructions.extend([storeInstr(r, p, range(nu1)) for r, p in zip(res, pc)])
            elif oK == 2:
                va = [vldGenF32(Pointer(src0[s0L.of(i),s0R.of(0)]), [0, 1]) for i in range(oM)]
                if oN == 1:
                    vb = vldGenF32(Pointer(src1[s1L.of(0),s1R.of(0)]), [0, 1])
                    mul0 = vmulF32(va[0], vb)
                    mul1 = vmulF32(va[1], vb)
                    res = vpaddF32(mul0, mul1)
                    pc = Pointer(dst[dL.of(0),dR.of(0)])
                    instructions.append(vstGenF32(res, pc, [0, 1]))
            elif oK in [3, 4]:
                va = [vldqGenF32(Pointer(src0[s0L.of(i),s0R.of(0)]), [0, 1, 2, 3]) for i in range(oM)]
                if oN == 1:
                    vb = vldqGenF32(Pointer(src1[s1L.of(0),s1R.of(0)]), [0, 1, 2, 3])
                    mul0 = vmulqF32(va[0], vb)
                    mul1 = vmulqF32(va[1], vb)
                    if oK == 3:
                        add = vpaddF32(vgetLowF32(mul0), vgetLowF32(mul1))
                        tmp = vaccessStructureF32(vzipF32(vgetHighF32(mul0), vgetHighF32(mul1)), 0)
                        res = vaddF32(add, tmp)
                    else:
                        add0 = vpaddF32(vgetLowF32(mul0), vgetLowF32(mul1))
                        add1 = vpaddF32(vgetHighF32(mul0), vgetHighF32(mul1))
                        res = vaddF32(add0, add1)
                    pc = Pointer(dst[dL.of(0),dR.of(0)])
                    instructions.append(vstGenF32(res, pc, [0, 1]))
        elif oM == 3:
            if oK == 1:
                va = vldqGenF32(Pointer(src0[s0L.of(0),s0R.of(0)]), range(nu0))
                if nu1 == 2:
                    loadInstr = vldGenF32
                    mulInstr = vmulLaneqF32
                    storeInstr = vstGenF32
                elif nu1 == 4:
                    loadInstr = vldqGenF32
                    mulInstr = vmulqLaneqF32
                    storeInstr = vstqGenF32
                vb = loadInstr(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu1))
                res = [mulInstr(vb, va, i) for i in range(oM)]
                pc = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(oM)]
                instructions.extend([storeInstr(r, p, range(nu1)) for r, p in zip(res, pc)])
            elif oK == 2:
                vas = [vldGenF32(Pointer(src0[s0L.of(i),s0R.of(0)]), [0, 1]) for i in range(oM)]
                if oN == 1:
                    vb = vldGenF32(Pointer(src1[s1L.of(0),s1R.of(0)]), [0, 1])
                    muls = [vmulF32(va, vb) for va in vas]
                    add0 = vpaddF32(muls[0], muls[1])
                    add1 = vpaddF32(muls[2], muls[2])
                    res = vcombineF32(add0, add1)
                    pc = Pointer(dst[dL.of(0),dR.of(0)])
                    instructions.append(vstqGenF32(res, pc, [0, 1, 2, 3]))
            elif oK in [3, 4]:
                vas = [vldqGenF32(Pointer(src0[s0L.of(i),s0R.of(0)]), [0, 1, 2, 3]) for i in range(oM)]
                if oN == 1:
                    vb = vldqGenF32(Pointer(src1[s1L.of(0),s1R.of(0)]), [0, 1, 2, 3])
                    muls = [vmulqF32(vas[i], vb) for i in range(oM)]
                    if oK == 3:
                        padd0 = vpaddF32(vgetLowF32(muls[0]), vgetLowF32(muls[1]))
                        tmp = vaccessStructureF32(vzipF32(vgetHighF32(muls[0]), vgetHighF32(muls[1])), 0)
                        res0_1 = vaddF32(padd0, tmp)
                        padd1 = vpaddF32(vgetLowF32(muls[2]), vgetLowF32(muls[2]))
                        res2_3 = vaddF32(padd1, vgetHighF32(muls[2]))
                    else:
                        padd0 = vpaddF32(vgetLowF32(muls[0]), vgetLowF32(muls[1]))
                        padd1 = vpaddF32(vgetHighF32(muls[0]), vgetHighF32(muls[1]))
                        res0_1 = vaddF32(padd0, padd1)
                        padd2 = vpaddF32(vgetLowF32(muls[2]), vgetHighF32(muls[2]))
                        res2_3 = vpaddF32(padd2, padd2)
                    res = vcombineF32(res0_1, res2_3)
                    pc = Pointer(dst[dL.of(0),dR.of(0)])
                    instructions.append(vstqGenF32(res, pc, [0, 1, 2, 3]))
        elif oM == 4:
            if oK == 1:
                va = vldqGenF32(Pointer(src0[s0L.of(0),s0R.of(0)]), [0, 1, 2, 3])
                if nu1 == 2:
                    loadInstr = vldGenF32
                    mulInstr = vmulLaneqF32
                    storeInstr = vstGenF32
                elif nu1 == 4:
                    loadInstr = vldqGenF32
                    mulInstr = vmulqLaneqF32
                    storeInstr = vstqGenF32
                vb = loadInstr(Pointer(src1[s1L.of(0),s1R.of(0)]), range(nu1))
                res = [mulInstr(vb, va, i) for i in range(oM)]
                pc = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(oM)]
                instructions.extend([storeInstr(r, p, range(nu1)) for r, p in zip(res, pc)])
            elif oK == 2:
                vas = [vldGenF32(Pointer(src0[s0L.of(i),s0R.of(0)]), [0, 1]) for i in range(oM)]
                if oN == 1:
                    vb = vldGenF32(Pointer(src1[s1L.of(0),s1R.of(0)]), [0, 1])
                    muls = [vmulF32(va, vb) for va in vas]
                    add0 = vpaddF32(muls[0], muls[1])
                    add1 = vpaddF32(muls[2], muls[3])
                    res = vcombineF32(add0, add1)
                    pc = Pointer(dst[dL.of(0),dR.of(0)])
                    instructions.append(vstqGenF32(res, pc, [0, 1, 2, 3]))
            elif oK in [3, 4]:
                vas = [vldqGenF32(Pointer(src0[s0L.of(i),s0R.of(0)]), [0, 1, 2, 3]) for i in range(oM)]
                if oN == 1:
                    vb = vldqGenF32(Pointer(src1[s1L.of(0),s1R.of(0)]), [0, 1, 2, 3])
                    muls = [vmulqF32(vas[i], vb) for i in range(oM)]
                    if oK == 3:
                        padds = [vpaddF32(vgetLowF32(muls[i]), vgetLowF32(muls[i+1])) for i in range(0, 4, 2)]
                        tmps = [vaccessStructureF32(vzipF32(vgetHighF32(muls[i]), vgetHighF32(muls[i+1])), 0) for i in range(0, 4, 2)]
                        ress = [vaddF32(padd, tmp) for padd, tmp in zip(padds, tmps)]
                    else:
                        padd0s = [vpaddF32(vgetLowF32(muls[i]), vgetLowF32(muls[i+1])) for i in range(0, 4, 2)]
                        padd1s = [vpaddF32(vgetHighF32(muls[i]), vgetHighF32(muls[i+1])) for i in range(0, 4, 2)]
                        ress = [vaddF32(padd0, padd1) for padd0, padd1 in zip(padd0s, padd1s)]
                    res = vcombineF32(*ress)
                    pc = Pointer(dst[dL.of(0),dR.of(0)])
                    instructions.append(vstqGenF32(res, pc, [0, 1, 2, 3]))
                     
            
                    
                    
                    
#         if M == 1:
#             if N == 1: # 1xnu * nux1
#                 va = vld1qF32(Pointer(src0[s0L.of(0),s0R.of(0)]))
#                 vb = vld1qF32(Pointer(src1[s1L.of(0),s1R.of(0)]))
#                 pc = Pointer(dst[dL.of(0),dR.of(0)])
#                 mul1 = vmulqF32(va, vb)
#                 mul2 = vpaddqF32(mul1, mul1)
#                 mul3 = vpaddqF32(mul2, mul2)
#                 instr = vst1qF32(mul3, pc)
#                 instructions.append(instr)
#             else: # 1xnu * nuxnu
#                 va = vld1qF32(Pointer(src0[s0L.of(0),s0R.of(0)]))
#                 vbs = [vld1qF32(Pointer(src1[s1L.of(i),s1R.of(0)])) for i in range(4)]
#                 
#                 mul = vmulqLaneF32(vbs[0], va, 0)
#                 for i in range(1, 4):
#                     mul = vmlaqLaneF32(mul, vbs[i], va, i)
#                 
#                 pc = Pointer(dst[dL.of(0),dR.of(0)])
#                 instr = vst1qF32(mul, pc)
#                 instructions.append(instr)
#         else:
#             if K == 1: # nux1 * 1xnu
#                 va = vld1qF32(Pointer(src0[s0L.of(0),s0R.of(0)]))
#                 vb = vld1qF32(Pointer(src1[s1L.of(0),s1R.of(0)]))
#                 
#                 muls = [vmulqLaneF32(vb, va, i) for i in range(4)]
#                 pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
#                 instrs = [vst1qF32(mul, pc) for mul, pc in zip(muls, pcs)]
#                 instructions.extend(instrs)
#             else:
#                 if N == 1: # nuxnu * nux1
#                     # TODO: it would be very efficient to use vld4 for loading a 4-element structure!
#                     vas = [vld1qF32(Pointer(src0[s0L.of(i),s0R.of(0)])) for i in range(4)]
#                     vb = vld1qF32(Pointer(src1[s1L.of(0),s1R.of(0)]))
#                     
#                     muls = [vmulqF32(vas[i], vb) for i in range(4)]
#                     hadd0 = vpaddqF32(muls[0], muls[1])
#                     hadd1 = vpaddqF32(muls[2], muls[3])
#                     pc = Pointer(dst[dL.of(0),dR.of(0)])
#                     instr = vst1qF32(vpaddqF32(hadd0, hadd1), pc)
#                     instructions.append(instr)
#                 else: # nuxnu * nuxnu
#                     #                     vas = [vld1qF32(Pointer(src0[s0L.of(i),s0R.of(0)])) for i in range(4)]
#                     #                     vbs = [vld1qF32(Pointer(src1[s1L.of(i),s1R.of(0)])) for i in range(4)]
#                     #                     muls = [vmulqLaneF32(vbs[0], vas[i], 0) for i in range(4)]
#                     #                     for k in range(1, 4):
#                     #                         for i in range(0, 4):
#                     #                             muls[i] = vmlaqLaneF32(muls[i], vbs[k], vas[i], k)
#                     #
#                     #                     pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
#                     #                     instrs = [vst1qF32(mul, pc) for mul, pc in zip(muls, pcs)]
#                     #                     instructions.extend(instrs)
#                     
#                     #                     vas = [vld1qF32(Pointer(src0[s0L.of(i),s0R.of(0)])) for i in range(4)]
#                     #                     vbs = [vld1qF32(Pointer(src1[s1L.of(i),s1R.of(0)])) for i in range(4)]
#                     if oM == 2 and oK == 2 and oN == 2:
#                         #                         val = [vgetLowF32(vas[i]) for i in range(2)]
#                         #                         vbl = [vgetLowF32(vbs[i]) for i in range(2)]
#                         val = [vld1F32(Pointer(src0[s0L.of(i),s0R.of(0)])) for i in range(2)]
#                         vbl = [vld1F32(Pointer(src1[s1L.of(i),s1R.of(0)])) for i in range(2)]
#                         muls = [vmulLaneF32(vbl[0], val[i], 0) for i in range(oM)]
#                         for k in range(1, oK):
#                             for i in range(0, oM):
#                                 muls[i] = vmlaLaneF32(muls[i], vbl[k], val[i], k)
#                         pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
#                         #                         vzd = vdupNF32(V(0))
#                         #                         instrs = [vst1qF32(vcombineF32(mul, vzd), pc) for mul, pc in zip(muls, pcs)] + [vst1qF32(vdupqNF32(V(0)), pc) for pc in pcs[oM:]]
#                         instrs = [vst1F32(mul, pc) for mul, pc in zip(muls, pcs)]
#                     else:
#                         vas = [vld1qF32(Pointer(src0[s0L.of(i),s0R.of(0)])) for i in range(4)]
#                         vbs = [vld1qF32(Pointer(src1[s1L.of(i),s1R.of(0)])) for i in range(4)]
#                         muls = [vmulqLaneF32(vbs[0], vas[i], 0) for i in range(oM)]
#                         for k in range(1, oK):
#                             for i in range(0, oM):
#                                 muls[i] = vmlaqLaneF32(muls[i], vbs[k], vas[i], k)
#                         
#                         pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
#                         instrs = [vst1qF32(mul, pc) for mul, pc in zip(muls, pcs)] + [vst1qF32(vdupqNF32(V(0)), pc) for pc in pcs[oM:]]
#                     instructions.extend(instrs)
        
        return instructions
    
    def T(self, sParams, dParams, opts):
        
        src, dst = sParams['nuM'], dParams['nuM']
        sL, sR = sParams['nuML'], sParams['nuMR']
        dL, dR = dParams['nuML'], dParams['nuMR']
        M, N = dParams['nuMM'], dParams['nuMN']
        oM, oN = sParams['M'], sParams['N']
        nu = N if N > 1 else M
        instructions = []
        
        instructions.append(Comment('%d-BLAC: (%dx%d)^T' % (nu, oM, oN)))
        
        if oM == 1 or oN == 1:
            if nu == 2:
                loadInstr = vldGenF32
                storeInstr = vstGenF32
            elif nu == 4:
                loadInstr = vldqGenF32
                storeInstr = vstqGenF32
            va = loadInstr(Pointer(src[sL.of(0),sR.of(0)]), range(nu))
            pc = Pointer(dst[dL.of(0),dR.of(0)])
            instr = storeInstr(va, pc, range(nu))
            instructions.append(instr)
        elif oM == 2:
            if oN == 2:
                vas = [vldGenF32(Pointer(src[sL.of(i),sR.of(0)]), [0, 1]) for i in range(oM)]
                res = vtrnF32(*vas)
                pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(oN)]
                instructions.extend([vst1F32(vaccessStructureF32(res, i), pcs[i]) for i in range(2)])
            if oN in [3, 4]:
                vas = [vldqGenF32(Pointer(src[sL.of(i),sR.of(0)]), [0, 1, 2, 3]) for i in range(oM)]
                zipStruct = vzipqF32(*vas)
                ress = [vgetLowF32(vaccessStructureF32(zipStruct, 0)), vgetHighF32(vaccessStructureF32(zipStruct, 0)),
                       vgetLowF32(vaccessStructureF32(zipStruct, 1)), vgetHighF32(vaccessStructureF32(zipStruct, 1))]
                pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(oN)]
                instructions.extend([vstGenF32(res, pc, [0, 1]) for res, pc in zip(ress, pcs)])
        elif oM in [3, 4]:
            if oN == 2:
                vas = [vldGenF32(Pointer(src[sL.of(i),sR.of(0)]), [0, 1]) for i in range(oM)]
                res0_1 = vtrnF32(vas[0], vas[1])
                if oM == 3:
                    res2_3 = vtrnF32(vas[2], vdupNF32(V(0)))
                else:
                    res2_3 = vtrnF32(vas[2], vas[3])
                res = [vaccessStructureF32(res0_1, 0), vaccessStructureF32(res2_3, 0), 
                       vaccessStructureF32(res0_1, 1), vaccessStructureF32(res2_3, 1)]
                pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(oN)]
                instructions.extend([vstqGenF32(vcombineF32(res[2*i], res[2*i+1]), pc, [0, 1, 2, 3]) for i, pc in enumerate(pcs)])
            elif oN in [3, 4]:
                vas = [vldqGenF32(Pointer(src[sL.of(i),sR.of(0)]), [0, 1, 2, 3]) for i in range(oM)]
                if oM == 3: vas.append(vdupqNF32(V(0)))
                q00 = vtrnF32(vgetLowF32(vas[0]), vgetLowF32(vas[1]))
                q01 = vtrnF32(vgetHighF32(vas[0]), vgetHighF32(vas[1]))
                q10 = vtrnF32(vgetLowF32(vas[2]), vgetLowF32(vas[3]))
                q11 = vtrnF32(vgetHighF32(vas[2]), vgetHighF32(vas[3]))
                    
                ress0 = [vaccessStructureF32(q00, 0), vaccessStructureF32(q10, 0),
                         vaccessStructureF32(q00, 1), vaccessStructureF32(q10, 1)]
                if oM == 3 and oN == 3:
                    ress0.extend([vaccessStructureF32(q01, 0), vgetHighF32(vas[2])])
                else: 
                    ress0.extend([vaccessStructureF32(q01, 0), vaccessStructureF32(q11, 0), vaccessStructureF32(q01, 1), vaccessStructureF32(q11, 1)])
                ress = [vcombineF32(ress0[i], ress0[i+1]) for i in range(0, len(ress0), 2)]
                pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(oN)]
                instructions.extend([vstqGenF32(res, pc, [0, 1, 2, 3]) for res, pc in zip(ress, pcs)])
                
#         if M*N == nu:
#             va = vld1qF32(Pointer(src[sL.of(0),sR.of(0)]))
#             pc = Pointer(dst[dL.of(0),dR.of(0)])
#             instr = vst1qF32(va, pc)
#             instructions.append(instr)
#         else: # M = N = nu
#             vas = [vld1qF32(Pointer(src[sL.of(i),sR.of(0)])) for i in range(4)]
#             struct01tmp = vzipqF32(vas[0], vas[2])
#             struct23tmp = vzipqF32(vas[1], vas[3])
#             struct01 = vzipqF32(vaccessStructureF32(struct01tmp, 0), vaccessStructureF32(struct23tmp, 0))
#             struct23 = vzipqF32(vaccessStructureF32(struct01tmp, 1), vaccessStructureF32(struct23tmp, 1))
#             v0 = vaccessStructureF32(struct01, 0)
#             v1 = vaccessStructureF32(struct01, 1)
#             v2 = vaccessStructureF32(struct23, 0)
#             v3 = vaccessStructureF32(struct23, 1)
#             
#             pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
#             instrs = [vst1qF32(v, pc) for v, pc in zip([v0, v1, v2, v3], pcs)]
#             instructions.extend(instrs)
        
        return instructions

class _Flt4Storer(Storer):
    def __init__(self):
        super(_Flt4Storer, self).__init__()
    
    def storeMatrix(self, mParams):
        src, dst = mParams['nuM'], mParams['m']
        sL, sR = mParams['nuML'], mParams['nuMR']
        dL, dR = mParams['mL'], mParams['mR']
        M, N = mParams['M'], mParams['N']
        isCompact = mParams['compact']
        instructions = []
        
        if M == 1:
            if N == 1:
                nuv = vldGenF32(Pointer(src[sL.of(0),sR.of(0)]), [0, 1], zeromask=[1])
                pc = AddressOf(sa(dst[dL.of(0),dR.of(0)]))
                instr = vstGenF32(nuv, pc, [0], isCompact)
                instructions.extend([Comment("1x2 -> 1x1"), instr])
            elif N == 3:
                nuv = vldqGenF32(Pointer(src[sL.of(0),sR.of(0)]), [0, 1, 2, 3], zeromask=[3])
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = vstqGenF32(nuv, pc, [0, 1, 2], isCompact)
                instructions.extend([Comment("1x4 -> 1x3 - Corner"), instr])
        elif M == 2:
            if N == 1 and not isCompact:
                nuv = vldGenF32(Pointer(src[sL.of(0),sR.of(0)]), [0, 1])
                pc = Pointer(dst[dL.of(0),dR.of(0)])
                instr = vstGenF32(nuv, pc, [0, 1], isCompact, horizontal=False)
                comm = Comment('2x1 -> 2x1 - %s' % ('Compact' if isCompact else 'Incompact'))
                instructions.extend([comm, instr])
            elif N == 2 and isCompact:
                nuvs = [vldGenF32(Pointer(src[sL.of(i),sR.of(0)]), [0, 1]) for i in range(2)]
                pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(2)]
                # TODO: Is this better than two separate stores (and correspondingly two separate loads in the loader)?
                # In other words, do the combine/getLow/getHigh confuse the compiler and make it generate mov instructions?
                instrs = [vstqGenF32(vcombineF32(nuvs[0], nuvs[1]), pcs[0], [0, 1, 2, 3], isCompact)]
                instructions.extend([Comment('2x2 -> 2x2')] + instrs)
            elif N == 3:
                nuvs = [vldqGenF32(Pointer(src[sL.of(i),sR.of(0)]), [0, 1, 2, 3], zeromask=[3]) for i in range(2)]
                instrs = [vstqGenF32(nuvs[i], Pointer(dst[dL.of(i),dR.of(0)]), [0, 1, 2], isCompact) for i in range(2)]
                instructions.extend([Comment('2x3 -> 2x3')] + instrs)
        elif M == 3:
            if N == 1:
                nuv = vld1qF32(Pointer(src[sL.of(0),sR.of(0)]), [3])
                instr = vstqGenF32(nuv, Pointer(dst[dL.of(0),dR.of(0)]), [0, 1, 2], isCompact, horizontal=False)
                comm = Comment('4x1 -> 3x1 - %s' % ('Compact' if isCompact else 'Incompact'))
                instructions.extend([comm, instr])
            elif N == 2 and isCompact:
                nuvs = [vld1F32(Pointer(src[sL.of(i),sR.of(0)])) for i in range(3)]
                pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(3)]
                instrs = [vstqGenF32(vcombineF32(nuvs[0], nuvs[1]), pcs[0], [0, 1, 2, 3]), vstGenF32(nuvs[2], pcs[2], [0, 1])]
                comm = Comment('3x2 -> 3x2 - Compact')
                instructions.extend([comm] + instrs)
            elif N == 3:
                nuvs = [vld1qF32(Pointer(src[sL.of(i),sR.of(0)]), [3]) for i in range(3)]
                instrs = [vstqGenF32(nuvs[i], Pointer(dst[dL.of(i),dR.of(0)]), [0, 1, 2], isCompact) for i in range(3)]
                instructions.extend([Comment('4x4 -> 3x3')] + instrs)
        elif M == 4:
            if N == 1 and not isCompact:
                nuv = vld1qF32(Pointer(src[sL.of(0),sR.of(0)]))
                instrs = [vstqGenF32(nuv, Pointer(dst[dL.of(0),dR.of(0)]), [0, 1, 2, 3], isCompact, horizontal=False)]
                instructions.extend([Comment('4x1 -> 4x1 - (Store) Incompact')] + instrs)
            elif N == 2 and isCompact:
                nuvs = [vld1F32(Pointer(src[sL.of(i),sR.of(0)])) for i in range(4)]
                pcs = [Pointer(dst[dL.of(i),dR.of(0)]) for i in range(4)]
                instrs = [vstqGenF32(vcombineF32(nuvs[i], nuvs[i+1]), pcs[i], [0, 1, 2, 3]) for i in range(0, 4, 2)]
                instructions.extend([Comment('4x2 -> 4x2 - Compact')] + instrs)
            elif N == 3:
                nuvs = [vld1qF32(Pointer(src[sL.of(i),sR.of(0)]), [3]) for i in range(4)]
                instrs = [vstqGenF32(nuvs[i], Pointer(dst[dL.of(i),dR.of(0)]), [0, 1, 2], isCompact) for i in range(4)]
                instructions.extend([Comment('4x4 -> 4x3')] + instrs)
        
        return instructions

class _LoadReplacer(LoadReplacer):
    def __init__(self, opts):
        super(_LoadReplacer, self).__init__(opts)

class NEON(ISA):
    def __init__(self, opts):
        super(NEON, self).__init__()
        
        self.name = "NEON"
#         float32 =  {'type': 'float32_t'}
#         float32['misc']     = [vgetLane, vgetqLane]
        
        float32x2 = {'type': 'float32x2_t'}
        float32x2['arith']  = [vaddF32, vmulF32, vmulLaneF32, vmlaF32, vmlaLaneF32, vpaddF32]
        float32x2['load']   = [vld1F32, vld1DupF32, vld1LaneF32, vldGenF32]
        float32x2['misc']   = [vgetLowF32, vgetHighF32, vaccessStructureF32]
        float32x2['set']    = [vdupNF32]
#         float32x2['store']  = [vst1F32, vst1LaneF32, vstGenF32]
        float32x2['store']  = [vstGenF32]
        
        float32x4 = {'type': 'float32x4_t'}
        float32x4['arith']  = [vaddqF32, vmulqF32, vmulqLaneqF32, vmulqLaneF32, vmlaqF32, vmlaqLaneF32]
        float32x4['load']   = [vld1qF32, vld1qDupF32, vld1qLaneF32, vldqGenF32]
        float32x4['misc']   = [vsetqLaneF32, vextqF32, vdupqLaneF32, vcombineF32, vaccessStructureF32]
        float32x4['cvt']    = []
        float32x4['set']    = [vdupqNF32]
        float32x4['move']   = []
#         float32x4['store']  = [vst1qF32, vst1qLaneF32, vstqGenF32]
        float32x4['store']  = [vstqGenF32]
        float32x4['loader'] = _Flt4Loader()
        float32x4['nublac'] = _Flt4BLAC()
        float32x4['storer'] = _Flt4Storer()
        float32x4['loadreplacer'] = _LoadReplacer(opts)
        
        float32x2x2 = {'type': 'float32x2x2_t'}
        float32x2x2['misc']  = [vtrnF32, vzipF32, vuzpF32]
        
        float32x4x2 = {'type': 'float32x4x2_t'}
        float32x4x2['misc']  = [vtrnqF32, vzipqF32, vuzpqF32]
        
        float32x4x4 = {'type': 'float32x4x4_t'}
        #         float32x4x4['load']   = [vld4qF32]
        #         float32x4x4['store']  = [vst4qF32]
        
        self.types = {
            'fp': {
#                 ('float', 1): float32,
                ('float', 2): float32x2,
                ('float', 4): float32x4,
                ('float', 8): float32x4x2,
                ('float', 16): float32x4x4,
            }
        }