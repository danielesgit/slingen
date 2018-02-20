'''
Created on Apr 18, 2012

@author: danieles
'''

import sys

from src.physical import Array, Scalars, Constant
#from math import *
from copy import copy

#from src.alexpr import *
from src.dsls.ll import Quantity, Operator, G, S, llLoop, llBlock, Sacc,\
    ParamMat, Assign
from src.dsls.sigmall import NewSum, Sum, llIf
from src.dsls.processing import computeIndependentSubexpr

  
class BindingTable(object):
    
    class myDict(dict):
        def __getitem__(self, *args, **kwargs):
            return dict.__getitem__(self, *args, **kwargs)
    
    def __init__(self):
        self.table = {}
#         self.table = BindingTable.myDict()
    
    def addBinding(self, matrix, physLayout):
        if matrix.name in self.table: return False
        self.table[matrix.name] = physLayout
        return True
    
    def add_binding_overwrite(self, matrix):
        if matrix.name in self.table: return False
        if matrix.attr['ow'] not in self.table:
            sys.exit("Could bind matrix %: %'s PhysLayout is missing." % (matrix.name, matrix.attr['ow']) )
        self.table[matrix.name] = self.table[matrix.attr['ow']]
        return True
        
    def delBindings(self, matrix):
        if matrix.name in self.table: del self.table[matrix.name] 
        
    def replacePhysicalLayout(self, oldPhys, newPhys):
        oldKeys = [ k for k, v in self.table.iteritems() if v == oldPhys]
        newPairs = [(k, newPhys) for k in oldKeys]
        self.table.update(newPairs)

    def replaceConnectedPhysicalLayout(self, oldPhys, newPhys, expr):
        logic = expr.getOut().name
        phys = self.table[logic]
        replaced = set()
        if phys is None:
            if isinstance(expr, Operator):
                for sub in expr.inexpr:
                    subPhys = self.table[sub.getOut().name]
                    replaced.update( self.replaceConnectedPhysicalLayout(subPhys, newPhys, sub) )
        elif phys == oldPhys:
            self.table.update([(logic,newPhys)])
            replaced.update([phys])
            if isinstance(expr, Operator):
                for sub in expr.inexpr:
                    replaced.update( self.replaceConnectedPhysicalLayout(oldPhys, newPhys, sub) )
        return replaced
    
    def isBound(self, mat):
        return mat.name in self.table #and self.table[mat.name] is not None

    def existPhysicalLayout(self, phys):
        return phys in self.table.values()
            
    def getPhysicalLayout(self, matrix):
        return self.table[matrix.name]
    
    def resetTable(self):
        self.table.clear()
                
    def __str__(self):
        return str(sorted(self.table.items(), key=lambda x: x[0])) # str(self.table)

#bindingTable = BindingTable()

###################################################################################

class Binder(object):
    def __init__(self, context):
        super(Binder, self).__init__()
        self.context = context
    
    def apply(self, sllprog, opts):
        self._populate_binding_table(sllprog.mDict, opts)
        self._apply(sllprog.stmtList, opts)

    def _populate_binding_table(self, mat_dict, opts):
        import networkx as nx
        g = nx.DiGraph()
        for name,mat in mat_dict.iteritems():
            ow = mat.attr.get('ow', None)
            if ow is None:
                g.add_node(name)
            else:
                g.add_edge(name, ow)
        order_of_decl = nx.topological_sort(g, reverse=True)
        for name in order_of_decl:
            mat = mat_dict[name]
            if mat.attr.get('ow', None) is not None:
                self.context.bindingTable.add_binding_overwrite(mat)
            else:
                if not mat.attr['o'] and mat.isScalar():
                    physLayout = Scalars(mat.name, mat.size, opts, isIn=mat.attr['i'], isParam=True)
                else:
                    physLayout = Array(mat.name, mat.size, opts, isIn=mat.attr['i'], isOut=mat.attr['o'])
                if self.context.bindingTable.addBinding(mat, physLayout):
                    if mat.attr['t']:
                        physLayout.safelyScalarize = opts['scarep']
                        self.context.declare += [physLayout]
                    else:
                        self.context.signature += [physLayout]
        
        
    def _apply(self, expr, opts):
        if isinstance(expr, llBlock):
            for s in expr:
                self._apply(s, opts)
        elif isinstance(expr, llLoop):
            self._apply(expr.body, opts)
        elif isinstance(expr, llIf):
            for b in expr.bodys:
                self._apply(b, opts)
        else:
            getattr(self, expr.eq.__class__.__name__)(expr.eq, opts)

    def replaceConnectedPhysicalLayout(self, newPhys, expr, i):
        subPhys = self.context.bindingTable.getPhysicalLayout(expr.getInexprMat(i))
        self.context.bindingTable.replaceConnectedPhysicalLayout(subPhys, newPhys, expr.inexpr[i])
        if not self.context.bindingTable.existPhysicalLayout(subPhys):
            self.context.declare.remove(subPhys)
        
    def Assign(self, expr, opts):

        out = expr.getOut()
        if self.context.bindingTable.isBound(out):
            return
        
        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)
        getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], opts)

        mLhs = expr.getInexprMat(0)
        mRhs = expr.getInexprMat(1)
        
        if mLhs.attr['o']:
            src = mRhs
            dst = mLhs
            subExpr = expr.inexpr[1]
        else:
            src = mLhs
            dst = mRhs
            subExpr = expr.inexpr[0]
            
        #Replace the PhysLayout of the destination with the one of the source
#         if not subExpr.reqAss and not dst.attr['i']:
        if not subExpr.reqAss:
            srcPhys = self.context.bindingTable.getPhysicalLayout(src)
            dstPhys = self.context.bindingTable.getPhysicalLayout(dst)
            replaced = self.context.bindingTable.replaceConnectedPhysicalLayout(srcPhys, dstPhys, subExpr)
            for phys in replaced:
                if not self.context.bindingTable.existPhysicalLayout(phys):
                    self.context.declare.remove(phys)

    def Scalar(self, expr, opts):
        self.Matrix(expr, opts)
    
    def SquaredMatrix(self, expr, opts):
        self.Matrix(expr, opts)

    def Matrix(self, expr, opts):
        return
#         if self.context.bindingTable.isBound(expr):
#             return
#         if expr.attr.get('ow', None) is not None:
#             self.context.bindingTable.add_binding_overwrite(expr)
#         if not expr.attr['o'] and expr.isScalar():
#             physLayout = Scalars(expr.name, expr.size, opts, isIn=expr.attr['i'], isParam=True)
#         else:
#             physLayout = Array(expr.name, expr.size, opts, isIn=expr.attr['i'], isOut=expr.attr['o'])
#         if self.context.bindingTable.addBinding(expr, physLayout):
#             if expr.attr['t']:
#                 physLayout.safelyScalarize = opts['scarep']
#                 self.context.declare += [physLayout]
#             else:
#                 self.context.signature += [physLayout]
    
    def bindSimpleOp(self, expr, opts):
        out = expr.getOut()
        if self.context.bindingTable.isBound(out):
            return
        
        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)
        getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], opts)
        
        outPhys = Array(out.name, out.size, opts, safelyScalarize=opts['scarep'])
        if self.context.bindingTable.addBinding(out, outPhys):
            self.context.declare += [outPhys]
        
    def Add(self, expr, opts):
        self.bindSimpleOp(expr, opts)
        
    def Kro(self, expr, opts): # Temporarily only dealing with sca-mat mul
        self.bindSimpleOp(expr, opts)
            
    def Mul(self, expr, opts):
        self.bindSimpleOp(expr, opts)
    
    def PMul(self, expr, opts):
        self.bindSimpleOp(expr, opts)

    def bindSimpleUnary(self, expr, opts):
        out = expr.getOut()
        if self.context.bindingTable.isBound(out):
            return

        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)
        
        outPhys = Array(out.name, out.size, opts, safelyScalarize=opts['scarep'])
        if self.context.bindingTable.addBinding(out, outPhys):
            self.context.declare += [outPhys]

    def T(self, expr, opts):
        self.bindSimpleUnary(expr, opts)
        
    def HRed(self, expr, opts):
        out = expr.getOut()
        if self.context.bindingTable.isBound(out):
            return

        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)
        
        outPhys = Array(out.name, out.size, opts, safelyScalarize=opts['scarep'])
        if self.context.bindingTable.addBinding(out, outPhys):
            self.context.declare += [outPhys]
            
    def G(self, expr, opts):
        out = expr.getOut()
        if self.context.bindingTable.isBound(out):
            return

        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)
        
        subPhys = self.context.bindingTable.getPhysicalLayout(expr.getInexprMat(0))
        self.context.bindingTable.addBinding(out, subPhys)

    def S(self, expr, opts):

        out = expr.getOut()
        if self.context.bindingTable.isBound(out):
            return

        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)

        outPhys = Array(out.name, out.size, opts, safelyScalarize=opts['scarep'])
        if self.context.bindingTable.addBinding(out, outPhys):
            self.context.declare += [outPhys]
        if not isinstance(expr.inexpr[0], G):
            # If we directly scatter a gather we should keep the phys. layout separated
            # Otherwise we can bind the subexpr's phys. layout to a larger one where 
            # the op. S is supposed to scatter its input.
            self.replaceConnectedPhysicalLayout(outPhys, expr, 0)
    
    def Sum(self, expr, opts):
        
        out = expr.getOut()
        if self.context.bindingTable.isBound(out) or expr.isBinding:
            return
        
        expr.isBinding = True

        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)
        
        outPhys = None
        if isinstance(expr.inexpr[0], S):
            # In case of summing up scattered matrices we can either use S's physLayout
            # or making S use a new one. Here we go for the first option.
            outPhys = self.context.bindingTable.getPhysicalLayout(expr.getInexprMat(0))
            self.context.bindingTable.addBinding(out, outPhys)
        elif not isinstance(expr.inexpr[0], G):
            # If not directly summing up gathered matrices we can bind sub-expressions to the same
            # phys. layout.  
            outPhys = Array(out.name, out.size, opts, safelyScalarize=opts['scarep'])
            if self.context.bindingTable.addBinding(out, outPhys):
                self.context.declare += [outPhys]
            self.replaceConnectedPhysicalLayout(outPhys, expr, 0)
        
        # If the sum is accumulating, it should do it referring to same phys. layout
        if len(expr.inexpr) > 1:
            for i in range(1, len(expr.inexpr)):
                getattr(self, expr.inexpr[i].__class__.__name__)(expr.inexpr[i], opts)
                if not isinstance(expr.inexpr[i], G): 
                    # I'm not sure it can happen to have G subexprs when accumulating.
                    # By now checking such a condition just in case.
                    self.replaceConnectedPhysicalLayout(outPhys, expr, i)
        
        expr.isBinding = False

def old_detectScalarizableEquation(expr, context, explored, opts, prevSigma):
    '''
    When ScaRep is set many intermediate arrays can be completely removed (safelyScalarize).
    However, when this intermediate arrays are used to pass values between loop nests 
    they must be preserved.
    '''
    if isinstance(expr, Quantity): return

    ss = True # SafelyScalarize

    if (isinstance(expr, Sum) and not expr.isFullyUnrolled()) \
        or (expr in prevSigma and (len(prevSigma[expr]) != len(expr.pred) or not all(prevSigma[expr]))):
            ss = False

    out = expr.getOut()
    if context.bindingTable.isBound(out):
        phys = context.bindingTable.getPhysicalLayout(out)
        if isinstance(phys, Array):
            if not phys in context.signature: # Could be dropped - args are set not scalar. at binding time
#                 ss = False
                phys.safelyScalarize = ss
        
    if not expr in explored:
        explored.append(expr)
        subexprs = []
        isSum = False
        if isinstance(expr, Sum):
            isSum = True
            subexprs = computeIndependentSubexpr(expr.inexpr[0], expr.iList, explored, opts)
        else:
            subexprs = expr.inexpr
        
        for sub in subexprs:
            if isSum:
                if not sub in prevSigma:
                    prevSigma[sub] = [ ss ]
                else:
                    prevSigma[sub] += [ ss ]
            old_detectScalarizableEquation(sub, context, explored, opts, prevSigma)

def buildDUListEquation(expr, context, opts, duList, ctxList):

    if isinstance(expr, Quantity): return

    if isinstance(expr, NewSum):
        ctxList.append(expr)
        buildDUListEquation(expr.inexpr[0], context, opts, duList, ctxList)
        ctxList.pop()
    else:
        if isinstance(expr, Assign):
            lhs = expr.inexpr[0]
            if lhs.attr['t']:
                if context.bindingTable.isBound(lhs):
                    phys = context.bindingTable.getPhysicalLayout(lhs)
                    duList.append([phys])
        if isinstance(expr, ParamMat):
            out = expr.getOut()
            if context.bindingTable.isBound(out):
                phys = context.bindingTable.getPhysicalLayout(out)
                dus = filter(lambda du: du[0] == phys, duList)
                if dus:
                    ctxl = [ ctx for ctx in ctxList if ctx.idx in expr.fL.func or ctx.idx in expr.fR.func ]
                    if isinstance(expr, Sacc):
                        du,top = (dus[-2],dus[-1]) if len(dus[-1]) == 1 else (dus[-1], None)
                        du.append( ('u', ctxl) )
                        if top is None:
                            newdu = [ du[0], ('d', ctxl) ] 
                            duList.append(newdu)
                        else:
                            top.append( ('d', ctxl) )
                    elif isinstance(expr, G):
                        du = dus[-2] if len(dus[-1]) == 1 else dus[-1]
                        du.append( ('u', ctxl) )
                    elif isinstance(expr, S):
                        dus[-1].append( ('d', ctxl) )
        for sub in expr.inexpr:
            buildDUListEquation(sub, context, opts, duList, ctxList)

def buildDUList(expr, context, opts, duList, ctxList=None):
    ctxList = [] if ctxList is None else ctxList
    if isinstance(expr, llBlock):
        for s in expr:
            buildDUList(s, context, opts, duList, ctxList)
    elif isinstance(expr, llLoop):
        ctxList.append(expr)
        buildDUList(expr.body, context, opts, duList, ctxList)
        ctxList.pop()
    elif isinstance(expr, llIf):
        for b in expr.bodys:
            buildDUList(b, context, opts, duList, ctxList)
    else:
        buildDUListEquation(expr.eq, context, opts, duList, ctxList)
    
def detectNonScalarizableMats(duList, opts):
    nonScal = []
    for du in duList: # [ MATLayout, ('d', [for0, for1, ...]), ('u', [for0, for1, ...]), ... ]
        if du[0] in nonScal:
            continue
        dctxs = du[1][1]
        for u in du[2:]:
            i=0
            while i < min(len(dctxs),len(u[1])):
#                 if dctxs[i].idx != u[1][i].idx:
                if id(dctxs[i]) != id(u[1][i]):
                    break
                i += 1
            checkUnrollable = dctxs[i:] + u[1][i:]
            for f in checkUnrollable:
                L = f.ub-f.lb+1
                if (opts['unroll'][str(f.idx)] == 0) or ((opts['unroll'][str(f.idx)] > 0) and not L.is_Number):
                    du[0].safelyScalarize = False
                    nonScal.append(du[0])
                    break

def bindExpression(sllprog, context, opts=None):
#     binder = Binder(context)
    binder = NewBinder(context)
    binder.apply(sllprog, opts)
    tsig = []
    for m in opts['inoutorder']:
        tsig += filter(lambda phys: phys.name == m, context.signature)
    del context.signature[:]
    context.signature = tsig
    if opts is not None and opts.get('scarep', False):
        duList = []
        buildDUList(sllprog.stmtList, context, opts, duList)
        detectNonScalarizableMats(duList, opts)


class NewBinder(Binder):
    def __init__(self, context):
        super(NewBinder, self).__init__(context)
        self.scattering = 0

    def G(self, expr, opts):
        out = expr.getOut()
        if out.size[0] <= opts['nu'] and out.size[1] <= opts['nu']: 
            getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)
            
            subPhys = self.context.bindingTable.getPhysicalLayout(expr.getInexprMat(0))
            self.context.bindingTable.addBinding(out, subPhys)
            out.fL, out.fR = expr.fL, expr.fR
        else:
            if self.context.bindingTable.isBound(out):
                return
            getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)
            outPhys = Array(out.name, out.size, opts)
            if self.context.bindingTable.addBinding(out, outPhys):
                self.context.declare += [outPhys]
            
    def S(self, expr, opts):
        self.scattering += 1
        out = expr.getOut()
        if self.context.bindingTable.isBound(out):
            return
        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)

        sub = expr.getInexprMat(0)
        safelyScalarize = opts['scarep'] and sub.size[0] <= opts['nu'] and sub.size[1] <= opts['nu']
        outPhys = Array(out.name, out.size, opts, safelyScalarize=safelyScalarize)
        if self.context.bindingTable.addBinding(out, outPhys):
            self.context.declare += [outPhys]
####### PhysLayout replacement should be delayed until structures and accesses are computed ############
 
#         if sub.size[0] <= opts['nu'] and sub.size[1] <= opts['nu']: 
#             outPhys = Array(out.name, out.size, opts, safelyScalarize=opts['scarep'])
#             if self.context.bindingTable.addBinding(out, outPhys):
#                 self.context.declare += [outPhys]
#             
#             if not isinstance(expr.inexpr[0], G):
#                 # If we directly scatter a gather we should keep the phys. layout separated
#                 # Otherwise we can bind the subexpr's phys. layout to a larger one where 
#                 # the op. S is supposed to scatter its input.
#                 self.replaceConnectedPhysicalLayout(outPhys, expr, 0)
#                 sub.fL, sub.fR = expr.fL, expr.fR
#         else:
#             outPhys = Array(out.name, out.size, opts)
#             if self.context.bindingTable.addBinding(out, outPhys):
#                 self.context.declare += [outPhys]
            
        self.scattering -= 1

    def Sacc(self, expr, opts):
#         self.S(expr, opts)
        self.scattering += 1
        out = expr.getOut()
        if self.context.bindingTable.isBound(out):
            return
        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)

        sub = expr.getInexprMat(0)

        if sub.size[0]*sub.size[1] <= opts['nu']*opts['nu']:
            outPhys = Array(out.name, out.size, opts, safelyScalarize=opts['scarep'])
            if self.context.bindingTable.addBinding(out, outPhys):
                self.context.declare += [outPhys]
        else:
            outPhys = Array(out.name, out.size, opts)
            if self.context.bindingTable.addBinding(out, outPhys):
                self.context.declare += [outPhys]

        self.scattering -= 1

    def Neg(self, expr, opts):
        self.bindSimpleUnary(expr, opts)

    def NewSum(self, expr, opts):
        out = expr.getOut()
        if self.context.bindingTable.isBound(out):
            return
        
        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)
        
        outPhys = self.context.bindingTable.getPhysicalLayout(expr.getInexprMat(0))
        self.context.bindingTable.addBinding(out, outPhys)

    def Add(self, expr, opts):
        out = expr.getOut()
        if self.context.bindingTable.isBound(out):
            return
        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)
        getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], opts)
        if not self.scattering:
            self.context.bindingTable.addBinding(out, None)
        else:
            self.bindSimpleOp(expr, opts)

    def LDiv(self, expr, opts):
        self.bindSimpleOp(expr, opts)

    def Div(self, expr, opts):
        self.bindSimpleOp(expr, opts)

    def Sqrt(self, expr, opts):
        self.bindSimpleUnary(expr, opts)

    def Sub(self, expr, opts):
        self.bindSimpleOp(expr, opts)

    def Iv(self, expr, opts):        
        out = expr.getOut()
        if self.context.bindingTable.isBound(out):
            return

        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)
        
        outPhys = self.context.bindingTable.getPhysicalLayout(expr.getInexprMat(0))
        self.context.bindingTable.addBinding(out, outPhys)

    def LowerTriangular(self, expr, opts):
        self.Matrix(expr, opts)

    def LowerUnitTriangular(self, expr, opts):
        self.Matrix(expr, opts)

    def UpperTriangular(self, expr, opts):
        self.Matrix(expr, opts)

    def UpperUnitTriangular(self, expr, opts):
        self.Matrix(expr, opts)

    def Symmetric(self, expr, opts):
        self.Matrix(expr, opts)
    
    def ConstantMatrix(self, expr, opts):
        
        if self.context.bindingTable.isBound(expr):
            return
        
        physLayout = Constant()
        self.context.bindingTable.addBinding(expr, physLayout)

    def IdentityMatrix(self, expr, opts):
        self.ConstantMatrix(expr, opts)

    def AllEntriesConstantMatrixWithValue(self, expr, opts):
        self.ConstantMatrix(expr, opts)

###################################################################################

class Reference(object):
    def __init__(self, matrix, physLayout):
        self.matrix = matrix
        self.physLayout = physLayout

    @staticmethod
    def whatRef(PhysLayout):
        if issubclass(PhysLayout, Array):
            return ArrayReference
        if issubclass(PhysLayout, Scalars):
            return ScalarsReference
        if issubclass(PhysLayout, Constant):
            return ConstantReference
        else:
            return None
    
    def __eq__(self, other):
        return self.physLayout == other.physLayout

    def __str__(self):
        return self.matrix.name + " -> " + self.physLayout.name
    
class ConstantReference(Reference):
    def __init__(self, matrix, physLayout):
        super(ConstantReference, self).__init__(matrix, physLayout)

class ExplicitPhysicalReference(Reference):
    def __init__(self, matrix, physLayout):
        super(ExplicitPhysicalReference, self).__init__(matrix, physLayout)
    
    def getLinIdx(self, key):
        return None

    def __getitem__(self, key):
        linIdx = self.getLinIdx(key)
        return self.physLayout[linIdx]
    

class ArrayReference(ExplicitPhysicalReference):
    def __init__(self, matrix, physLayout):
        super(ArrayReference, self).__init__(matrix, physLayout)
    
    def getLinIdx(self, key):
        idx = copy(self.matrix.getOrigin())
        idx[0] += key[0]
        idx[1] += key[1]
        
        return idx[0]*self.physLayout.pitch + idx[1]
        
    def pointerAt(self, key):
#         idx = copy(self.matrix.getOrigin())
#         idx[0] += key[0]
#         idx[1] += key[1]
#         
#         linIdx = idx[0]*self.physLayout.pitch + idx[1]
        linIdx = self.getLinIdx(key)
        return self.physLayout.pointerAt(linIdx)

    def isCorner(self, key):
        linIdx = self.getLinIdx(key)
        return self.physLayout.size-1 == linIdx
#     def __getitem__(self, key):
#         idx = copy(self.matrix.getOrigin())
#         idx[0] += key[0]
#         idx[1] += key[1]
#         
#         linIdx = idx[0]*self.physLayout.pitch + idx[1]
#         linIdx = self.getLinIdx(key)
#         return self.physLayout[linIdx]

class ScalarsReference(ExplicitPhysicalReference):
    def __init__(self, matrix, physLayout):
        super(ScalarsReference, self).__init__(matrix, physLayout)

    def getLinIdx(self, key):
        idx = copy(self.matrix.getOrigin())
        idx[0] += key[0]
        idx[1] += key[1]
        
        return idx[0]*self.physLayout.size[1] + idx[1]

    def isCorner(self, key):
        return True 

#     def __getitem__(self, key):
#         idx = copy(self.matrix.getOrigin())
#         idx[0] += key[0]
#         idx[1] += key[1]
#         
#         linIdx = idx[0]*self.physLayout.size[1] + idx[1]
#         linIdx = self.getLinIdx(key)
#         return self.physLayout[linIdx]


###################################################################################


def getReference(context, matrix):
    '''Get physical layout reference.'''
    if not context.bindingTable.isBound(matrix):
        return None
    physLayout = context.bindingTable.getPhysicalLayout(matrix)
    Ref = Reference.whatRef(physLayout.__class__)
    return Ref(matrix, physLayout)

###################################################################################


if __name__ == "__main__":
    pass    
