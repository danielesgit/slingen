'''
Created on May 9, 2014

@author: danieles
'''

from copy import deepcopy
import sympy
from sympy import Symbol, sympify
from itertools import ifilter

from islpy import dim_type, Set
from src.dsls.sllparser import sigmallParser, sigmallSemantics
from src.dsls.ll import llBlock, T, Add, Sub, Neg, Mul, LDiv, RDiv, Div, Kro, Sqrt, Assign, NewContextOperator, Expression, Quantity, G, S, Sacc, Iv, llProgram, globalSSAIndex, getNextCheckMark, IMF, fHbs, fI,\
    llStmt, llFor, llIf, constant_matrix_type_with_value, scalar_block, Condition, CondTerm, CondFactor, sym_locals
from src.dsls.processing import replaceWith, computeIndependentSubexpr, computeDependentSubexprOfType
from src.dsls.holograph import Holonode
# class sllStmt(llStmt):
#     def __init__(self, eq=None, ann=None):
#         super(sllStmt, self).__init__(eq, ann)

class sllProgram(llProgram):
    def __init__(self, semObj=None):
        super(sllProgram, self).__init__()
        self.mDict = {} if semObj is None else dict(semObj.mDict)
        self.ann = {'setIndices': set() }
        stmtList = llBlock()
#         if isinstance(semObj, sigmallExtSemantics):
        if semObj is not None:
            stmtList.append(semObj.stmtList)
            if 'indices' in semObj.ann:
                self.ann['setIndices'].update(semObj.ann['indices'])
#         elif isinstance(semObj, llProgram):
#             for s in semObj.stmtList:
#                 newStmt = llStmt(s.eq)
#                 newStmt.ann = dict(s.ann.items())
#                 stmtList.append(newStmt)
        self.stmtList = stmtList
    
    def extend(self, semObj):
        self.mDict.update(semObj.mDict)
        self.stmtList.append(semObj.stmtList)
        if 'indices' in semObj.ann:
            self.ann['setIndices'].update(semObj.ann['indices'])

#     def computeSpaceIdxNames(self, i, j, ipfix, jpfix, opts, depth=1, baselevel=2):
#         for b in self.stmtList:
#             b.computeSpaceIdxNames(i, j, ipfix, jpfix, opts, depth, baselevel)
    
#     def getHolograph(self):
#         newSllp = sllProgram()
#         newSllp.mDict = dict(self.mDict)
#         newSllp.ann = dict(self.ann)
#         newSllp.stmtList = self.stmtList.getHolograph()
#         return newSllp
# 
#     def getRealgraph(self):
#         newSllp = sllProgram()
#         newSllp.mDict = dict(self.mDict)
#         newSllp.ann = dict(self.ann)
#         newSllp.stmtList = self.stmtList.getRealgraph()
#         return newSllp
# 
#     def copySubs(self, dic):
#         newSllp = sllProgram()
#         newSllp.mDict = dict(self.mDict)
#         newSllp.ann = dict(self.ann)
#         newSllp.stmtList = self.stmtList.copySubs(dic)
#         return newSllp
#         
#     def resetComputed(self):
#         self.stmtList.resetComputed()
        
class sigmallExtSemantics(sigmallSemantics):
    def __init__(self, mDict, ann):
        self.mDict = dict(mDict)
        self.ann = ann
        self.indicesStack = [ [] ]
        self.iterspaceStack = [ Set("{[]}") ]
        self.rangeStack = [ [{},{},{}] ]
        self.numexprStack = []
        self.condStack = []
        self.imfStack = []
        self.eqStack = []
        self.stmtListStack = [ [] ]
        self.stmtList = None
    
    def program(self, ast):
        self.stmtList = llBlock(self.stmtListStack.pop())
        self.stmtList.updateAnn(self.ann)
        return ast
 
    def preprocs(self, ast):
        self.stmtListStack.append([])
        return ast

    def looptop(self, ast):
        sidx, sLb, sUb, sInc = str(ast['idx']), str(self.numexprStack[-3]), str(self.numexprStack[-2]), str(self.numexprStack[-1])
        iterspace = self.iterspaceStack[-1]
#         idcs = iterspace.get_var_names(dim_type.set) + [sidx]
        idcs = self.indicesStack[-1] + [sidx]
        setstr = str("{ [" + ",".join(idcs) + "] : exists s: " + sidx + "="+sInc+"s and " + sLb + " <= " + sidx + " <= " + sUb + " }") 
        newDimSet = Set(setstr)
        newIterspace = newDimSet.intersect(iterspace.add_dims(dim_type.set, 1))
        lexmin = newIterspace.lexmin()
        lexmax = newIterspace.lexmax()

        ps = []
        lexmin.foreach_point(ps.append)
        mins = [ ps[0].get_coordinate_val(dim_type.set, pos).to_python() for pos in range(len(idcs)) ]
        ps = []
        lexmax.foreach_point(ps.append)
        maxs = [ ps[0].get_coordinate_val(dim_type.set, pos).to_python() for pos in range(len(idcs)) ]

        prev_inc_dict = self.rangeStack[-1][-1]

        newRanges = []
        newRanges.append( { idx: sympify(pmin, locals=sym_locals) for idx,pmin in zip(idcs, mins) } )
        newRanges.append( { idx: sympify(pmax, locals=sym_locals) for idx,pmax in zip(idcs, maxs) } )
        newRanges.append( deepcopy(prev_inc_dict) )
        newRanges[-1][sidx] = self.numexprStack[-1]

#         ps = []
#         lexmin.foreach_point(ps.append)
#         pmin = ps[0].get_coordinate_val(dim_type.set, len(idcs)-1).to_python()
#         ps = []
#         lexmax.foreach_point(ps.append)
#         pmax = ps[0].get_coordinate_val(dim_type.set, len(idcs)-1).to_python()
# 
#         vtuple = (pmin, pmax, self.numexprStack[-1])
#         ranges = self.rangeStack[-1]
#         newRanges = []        
#         for r,v in zip(ranges, vtuple):
#             newRanges.append( { idx: r[idx] for idx in idcs[:-1] } )
#             newRanges[-1][sidx] = v
        self.indicesStack.append(idcs)
        self.iterspaceStack.append(newIterspace)
        self.rangeStack.append(newRanges)
        return ast
    
    def llfor(self, ast):
        s = self.numexprStack.pop()
        ub = self.numexprStack.pop()
        lb = self.numexprStack.pop()
        body = llBlock(self.stmtListStack.pop())
        self.stmtListStack[-1].append(llFor(sympify(ast['looptop']['idx']), lb, ub, s, body))
        self.indicesStack.pop()
        self.iterspaceStack.pop()
        self.rangeStack.pop()
        return ast

#     def llif(self, ast):
#         then = llBlock(self.stmtListStack.pop())
#         cond = self.condStack.pop()
#         
#         self.stmtListStack[-1].append( llIf([then], [cond]) )
#         return ast

    def guard(self, ast):
        cond = self.condStack[-1].getIslStr()

        iterspace = self.iterspaceStack[-1]
        idcs = self.indicesStack[-1]
        setstr = str("{ [" + ",".join(idcs) + "] : " + cond + " }") 
        newDimSet = Set(setstr)
        newIterspace = newDimSet.intersect(iterspace)

        newRanges = []
        lexmin = newIterspace.lexmin()
        lexmax = newIterspace.lexmax()

        ps = []
        lexmin.foreach_point(ps.append)
        mins = [ ps[0].get_coordinate_val(dim_type.set, pos).to_python() for pos in range(len(idcs)) ]
        ps = []
        lexmax.foreach_point(ps.append)
        maxs = [ ps[0].get_coordinate_val(dim_type.set, pos).to_python() for pos in range(len(idcs)) ]

        prev_inc_dict = self.rangeStack[-1][-1]

        newRanges.append( { idx: sympify(pmin, locals=sym_locals) for idx,pmin in zip(idcs, mins) } )
        newRanges.append( { idx: sympify(pmax, locals=sym_locals) for idx,pmax in zip(idcs, maxs) } )
        newRanges.append( deepcopy(prev_inc_dict) )
            
        self.iterspaceStack.append(newIterspace)
        self.rangeStack.append(newRanges)
        return ast

    def llif(self, ast):
        cond = self.condStack.pop()
        stmt_list = self.stmtListStack.pop()

        then = llBlock(stmt_list)
        self.stmtListStack[-1].append( llIf([then], [cond]) )
        
        self.iterspaceStack.pop()
        self.rangeStack.pop()
        return ast
        
    def equation(self, ast):
        rhs = self.eqStack.pop()
        eq = Assign(self.mDict[ast['lhs']['id']].duplicate(), rhs)
        self.stmtListStack[-1].append( llStmt(eq) )
        return ast
    
    def expr(self, ast):
        l = len(ast['term'])
        e = self.eqStack.pop(-l)
        l-=1
        while(l>0):
            t = self.eqStack.pop(-l)
            l-=1
            op = Add if ast['op'][l] == '+' else Sub
            e = op(e,t)
        self.eqStack.append(e)
        return ast
        
    def term(self, ast):
        l = len(ast['factor'])
        t = self.eqStack.pop(-l)
        l-=1
        while(l>0):
            f = self.eqStack.pop(-l)
            l-=1
            if ast['fop'][l] == '*':
                if (t.getOut().isScalar() or f.getOut().isScalar()):
                    op = Kro
                else:
                    op = Mul
            elif ast['fop'][l] == '/':
                if (t.getOut().isScalar() and f.getOut().isScalar()):
                    op = Div
                else:
                    op = RDiv
            else:
                op = LDiv
            t = op(t,f)
        self.eqStack.append(t)
        return ast
    
    def scatter(self, ast):
        e = self.eqStack.pop()
        fR = self.imfStack.pop()
        fL = self.imfStack.pop()
        self.eqStack.append(S(fL, e, fR))
        return ast

    def scatteracc(self, ast):
        e = self.eqStack.pop()
        fR = self.imfStack.pop()
        fL = self.imfStack.pop()
        self.eqStack.append(Sacc(fL, e, fR))
        return ast

    def preprocg(self, ast):
        self.imfStack.append("G")
        return ast

    def planefactor(self, ast):
        if 'id' in ast:
            self.eqStack.append(self.mDict[ast['id']].duplicate())
            self.eqStack[-1].set_info( ['min', 'max', 'inc', 'polytope', 'indices'], self.rangeStack[-1]+[ self.iterspaceStack[-1], self.indicesStack[-1] ] )
#             self.eqStack[-1].set_info(['min', 'max', 'inc', 'polytope'], self.rangeStack[-1]+[ self.iterspaceStack[-1] ])
        elif 'const' in ast:
            name = str(ast['const'])
            mat_type = constant_matrix_type_with_value( sympify(name) )
            self.eqStack.append( mat_type(name, scalar_block(), (1,1)) )
            self.eqStack[-1].set_info( ['min', 'max', 'inc', 'polytope', 'indices'], self.rangeStack[-1]+[ self.iterspaceStack[-1], self.indicesStack[-1] ] )
        if self.imfStack:
            if self.imfStack[-1] != 'G':
                e = self.eqStack.pop()
                imfs = []
                while self.imfStack[-1] != 'G':
                    fR = self.imfStack.pop()
                    fL = self.imfStack.pop()
                    imfs.append((fL,fR))
                for t in imfs[::-1]: 
                    e = G(t[0], e, t[1])
                self.eqStack.append(e)
            self.imfStack.pop() #Pop G-marker from the stack 
        if 'sign' in ast and ast['sign'] == '-':
            e = self.eqStack.pop()
            self.eqStack.append( Neg(e) )
        return ast
    
    def sum(self, ast):
        e = self.eqStack.pop()
        s = self.numexprStack.pop()
        ub = self.numexprStack.pop()
        lb = self.numexprStack.pop()
        self.eqStack.append(NewSum(e, sympify(ast['idx']), lb, ub, s))
        return ast
    
    def subexpr(self, ast):
        if 'guard' in ast:
            e = self.eqStack.pop()
            cond = self.condStack.pop()
            self.eqStack.append(Iv(e, cond))
        return ast
    
    def trans(self, ast):
        e = self.eqStack.pop()
        self.eqStack.append(T(e))
        return ast

    def sqrt(self, ast):
        e = self.eqStack.pop()
        self.eqStack.append(Sqrt(e))
        return ast
        
    def genimf(self, ast):
        params = []
        for i in range(4):
            params.append(self.numexprStack.pop(-4+i))
        self.imfStack.append(IMF(*params))
        return ast

    def himf(self, ast):
        l = len(ast['params'])
        params = []
        for i in range(l):
            params.append(self.numexprStack.pop(-l+i))
        f = fHbs(*params)
        f.use_floor_ceiling()
        self.imfStack.append( f )
        return ast

    def iimf(self, ast):
        param = self.numexprStack.pop()
        self.imfStack.append(fI(param))
        return ast

#     def numcond(self, ast):
#         condr = self.numexprStack.pop(-1)
#         condl = self.numexprStack.pop(-1)
# #         self.condStack.append(sympify(str(condl)+ast['condsym']+str(condr)))
#         self.condStack.append([condl, ast['condsym'], condr])
#         return ast

    def condexpr(self, ast):
        l = len(ast['condterm'])
        e = self.condStack.pop(-l)
        l-=1
        while(l>0):
            t = self.condStack.pop(-l)
            e = Condition([e,t])
            l-=1
        self.condStack.append(e)
        return ast

    def condterm(self, ast):
        l = len(ast['condfactor'])
        t = self.condStack.pop(-l)
        l-=1
        while(l>0):
            f = self.condStack.pop(-l)
            l-=1
#             t = (t)*(f)
            t = CondTerm([t,f])
        self.condStack.append(t)
        return ast

    def condfactor(self, ast):
        condr = self.numexprStack.pop()
        condl = self.numexprStack.pop()
#         self.condStack.append(sympify(str(condl)+ast['condsym']+str(condr)))
#         self.condStack.append([condl, ast['condsym'], condr])
        self.condStack.append(CondFactor([condl, condr], ast['condsym']))
        return ast
        
    def numexpr(self, ast):
        
        l = len(ast['numterm'])
        e = self.numexprStack.pop(-l)
        if 'sign' in ast:
            e = sympify(ast['sign'] + "("+ str(e) +")", locals=sym_locals)
        l-=1
        while(l>0):
            t = self.numexprStack.pop(-l)
            e = sympify("("+ str(e) +")"+ ast['op'][-l] +"("+ str(t)+")", locals=sym_locals)
            l-=1
        self.numexprStack.append(e)
        return ast

#     def numterm(self, ast):
#         l = len(ast['numfactor'])
#         t = self.numexprStack.pop(-l)
#         l-=1
#         while(l>0):
#             f = self.numexprStack.pop(-l)
#             l-=1
#             t = (t)*(f)
#         if 'numden' in ast:
#             t = (t) / sympify(ast['numden'])
#         elif 'nummod' in ast:
#             t = (t) % sympify(ast['nummod'])
#         self.numexprStack.append(t)
#         return ast

    def numterm(self, ast):
        if not self.iterspaceStack[-1].is_empty():
            l = len(ast['numfactor'])
            t = self.numexprStack.pop(-l)
            l-=1
            while(l>0):
                f = self.numexprStack.pop(-l)
                t = sympify("("+ str(t) +")"+ ast['op'][-l] +"("+ str(f)+")", locals=sym_locals)
                l-=1
            self.numexprStack.append(t)
        return ast


    def numfactor(self, ast):
        if 'modl' in ast:
            r = self.numexprStack.pop(-1)
            l = self.numexprStack.pop(-1)
            self.numexprStack.append(l%r)
        elif 'fnum' in ast:
            num = self.numexprStack.pop()
            self.numexprStack.append(sympify("floord("+str(num)+","+str(sympify(ast['fden']))+")", locals=sym_locals))
#             self.numexprStack.append(sympy.floor((sympify(str(num)).together()/sympify(ast['fden']).together()).together()))
        elif 'cnum' in ast:
            num = self.numexprStack.pop()
            self.numexprStack.append(sympify("ceild("+str(num)+","+str(sympify(ast['cden']))+")", locals=sym_locals))
#             self.numexprStack.append(sympy.ceiling((sympify(str(num)).together()/sympify(ast['cden']).together()).together()))
        elif 'minl' in ast:
            r = self.numexprStack.pop()
            l = self.numexprStack.pop()
            self.numexprStack.append(sympify("Min("+str(l)+","+str(r)+")", locals=sym_locals))
        elif 'maxl' in ast:
            r = self.numexprStack.pop()
            l = self.numexprStack.pop()
            self.numexprStack.append(sympify("Max("+str(l)+","+str(r)+")", locals=sym_locals))
        elif 'id' in ast:
            self.numexprStack.append(sympify(ast['id']))
        elif 'const' in ast:
            self.numexprStack.append(sympify(ast['const']))
        return ast

def parseSigmaLL(sllSrc, mDict, opts, ann=None):
    import string
    
    opts['currentSLLSrc'] = sllSrc
    
    parser = sigmallParser(parseinfo=False, nameguard=False, comments_re="%%.*")
    ann = {} if ann is None else ann
    sem = sigmallExtSemantics(mDict, ann)
    ast = parser.parse(sllSrc, rule_name="program", whitespace=string.whitespace, semantics=sem)
    
    return sem



class NewSum(NewContextOperator):
    '''
    Summation Operator.
    '''
    def __init__(self, inexpr, idx, lb, ub, s, uFactor=None, out=None):
        super(NewSum, self).__init__()
        self.idx = idx
        self.lb, self.ub, self.s = lb, ub, s
        self.init = False
        if uFactor is None:
            self.uFactor = sympify(1)
        else:
            self.uFactor = uFactor
        if isinstance(inexpr, Holonode):
            self.buildout(out, inexpr.node.getOut())
        else:
            self.inexpr = [ inexpr ]
            self.buildout(out)
            self.setAsPred()
            self.ann = {}
        
    def buildout(self, out, src=None):
        if src is None:
            src = self.getInexprMat(0)
            
        self.set_info_no_td(src.info.keys(), src.info.values())
        if(out):
            self.out = out
        else: 
            self.out = src.duplicate("S"+ str(globalSSAIndex()), o=[sympify(0),sympify(0)], fL=fI(src.size[0]), fR=fI(src.size[1]))
        self.set_out_info(src.info.keys(), src.info.values())

    def dependsOn(self, idx):
        return super(NewSum, self).dependsOn(idx) or any(map(lambda symExpr: idx in symExpr, [ self.lb, self.ub, self.s]))

    def subs(self, idsDict, explored=None):
        super(NewSum, self).subs(idsDict, explored)
        self.lb = self.lb.subs(idsDict)
        self.ub = self.ub.subs(idsDict)
        self.s = self.s.subs(idsDict)

    def duplicate(self, prefix="", everything=True, changeOut=False, changeHandle=False):
        tIn = [ inexpr.duplicate() if isinstance(inexpr, Quantity) else inexpr.duplicate(prefix, everything, changeOut, changeHandle) for inexpr in self.inexpr ] if everything else self.inexpr
        if changeOut:
            out = None
            changeHandle = True
        else:
            out = self.out.duplicate(prefix)
        res = NewSum(tIn[0], deepcopy(self.idx), deepcopy(self.lb), deepcopy(self.ub), deepcopy(self.s), deepcopy(self.uFactor), out)
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        res.ann = deepcopy(self.ann)
        res.init = self.init
        if not changeHandle:
            res.handle = self.handle
        return res
    
    def toLatex(self, context, ind=0, subs=None):
        subs = {} if subs is None else subs
        idx, lb, ub, s = str(self.idx), str(self.lb), str(self.ub), str(self.s)
        res = "\sum_{" + idx + " = " + lb + "," + s + "}^{" + ub + "} "
        for sub in subs:
            res = res.replace(sub, subs[sub])
        res += "($\n"
        res += ind*" " + "$" + self.inexpr[0].toLatex(context, ind+2, subs) + "$\n" 
        res += ind*" " + "$)"
        return res
    
    def toEG(self): 
        return "Sum_{" + str(self.idx) + "}"
        
    def __str__(self):
        return "Sum_{" + str(self.idx) + "} ( " + str(self.inexpr[0]) + " )"

    def __eq__(self, other):
        return super(NewSum, self).__eq__(other) and self.idx == other.idx and self.lb == other.lb \
             and self.ub == other.ub and self.s == other.s and self.init == other.init and self.uFactor == other.uFactor

    def sameUpToNames(self, other):
        return super(NewSum, self).sameUpToNames(other) and self.idx == other.idx and self.lb == other.lb \
             and self.ub == other.ub and self.s == other.s and self.init == other.init and self.uFactor == other.uFactor

    def __hash__(self):
        tin = tuple(self.inexpr)
        key = (hash('NewSum'), hash(tin), self.idx, self.lb, self.ub, self.s, self.init, self.uFactor)
        return hash(key)


class Sum(NewContextOperator):
    '''
    Summation Operator.
    '''
    def __init__(self, inexpr, iList, uFactors=None, out=None, acc=False, init=True, outerIdx=None, outDep=None, forceInitIdx=None, iPriority=None):
        super(Sum, self).__init__()
        self.inexpr = inexpr
        self.iList = iList
        if iPriority is None:
            self.iPriority = { idx: p for idx,p in zip([i.i for i in iList], range(len(iList))) }
        else:
            self.iPriority = iPriority
        # This is a list of indices the output of the summation depends upon
        if outDep is None:
            outDep = [ ]
        if forceInitIdx is None:
            forceInitIdx = [ ]
        #The list of top indices for the summation
        if outerIdx is None:
            outerIdx = [ ]
        self.outerIdx = outerIdx
        self.outDep = outDep
        self.forceInitIdx = forceInitIdx
        self.initCounter = 1
        self.initCounterIdx = []
        if uFactors is None:
            self.uFactors = [sympify(1)]*len(iList)
        else:
            self.uFactors = uFactors
        self.init = init
        self.acc = acc
        self.buildout(out)
        self.setAsPred()
        self.isBuilding = False
        self.isCheckingEq = False
        self.checkMark = -1
        self.isBinding = False
        self.isBoundToParam = False
        self.isDuplicating = False
        self.placeHolder = None
        self.depSums = None 
        self.partialComps = []
    
    def addPartialComp(self, bounds):
        del self.partialComps[:]
        partialComp = { s : bounds[s] for s in bounds if (any(map(lambda od: s in od, self.outDep)) or s in self.outerIdx) and not (any(map(lambda idx: s == idx.i, self.iList))) }
        self.partialComps.append(partialComp)

    def partiallyComputed(self, bounds):
        partialComp = { s : bounds[s] for s in bounds if any(map(lambda od: s in od, self.outDep)) or s in self.outerIdx }
        return partialComp in self.partialComps
                
    def duplicate(self, prefix="", everything=True):
        if self.isDuplicating:
            return self
        if self.acc:
            self.isDuplicating = True
            self.placeHolder = Expression()
        tIn = [ inexpr.duplicate() if isinstance(inexpr, Quantity) else inexpr.duplicate(prefix) for inexpr in self.inexpr ] if everything else self.inexpr 
        tIList = [ deepcopy(i) for i in self.iList ]
        tIPriority = deepcopy(self.iPriority)
        tUFactors = [ deepcopy(u) for u in self.uFactors ]
        newOut = self.out.duplicate(prefix) if self.out is not None else None
        tOuterIdx = [ deepcopy(i) for i in self.outerIdx ]
        tOutDep = [ deepcopy(i) for i in self.outDep ]
        tForceInitIdx = [ deepcopy(i) for i in self.forceInitIdx ]
        # inexpr, iList, uFactors=None, out=None, acc=False, init=False, outerIdx=None, outDep=None, forceInitIdx=None):
        res = Sum(inexpr=tIn, iList=tIList, uFactors=tUFactors, out=newOut, acc=self.acc, init=self.init, outerIdx=tOuterIdx, outDep=tOutDep, forceInitIdx=tForceInitIdx, iPriority=tIPriority)
        res.setComputed(self.computed)
        res.isBuilding = self.isBuilding
        res.isCheckingEq = self.isCheckingEq
        res.checkMark = self.checkMark
        res.isBinding = self.isBinding
        res.isBoundToParam = self.isBoundToParam
        res.depSet = deepcopy(self.depSet)
        res.handle = self.handle

        if self.acc:
            replaceWith(res, self.placeHolder, res)
        self.isDuplicating = False
        self.placeHolder = None

        return res

    def duplicateUpToBoundaries(self, prefix="", boundaries=None, changeHandle=True):
        if boundaries is None:
            boundaries = []
        if self.isDuplicating:
            return self
        if self.acc:
            self.isDuplicating = True
            self.placeHolder = Expression()
        tIn = [ inexpr if (inexpr in boundaries) else inexpr.duplicateUpToBoundaries(prefix, boundaries, changeHandle) for inexpr in self.inexpr ]
        tIList = [ deepcopy(i) for i in self.iList ]
        tIPriority = deepcopy(self.iPriority)
        tUFactors = [ deepcopy(u) for u in self.uFactors ]
        newOut = self.out.duplicate(prefix) if self.out is not None else None
        tOuterIdx = [ deepcopy(i) for i in self.outerIdx ]
        tOutDep = [ deepcopy(i) for i in self.outDep ]
        tForceInitIdx = [ deepcopy(i) for i in self.forceInitIdx ]
        res = Sum(inexpr=tIn, iList=tIList, uFactors=tUFactors, out=newOut, acc=self.acc, init=self.init, outerIdx=tOuterIdx, outDep=tOutDep, forceInitIdx=tForceInitIdx, iPriority=tIPriority)
        res.setComputed(self.computed)
        res.isBuilding = self.isBuilding
        res.isCheckingEq = self.isCheckingEq
        res.checkMark = self.checkMark
        res.isBinding = self.isBinding
        res.isBoundToParam = self.isBoundToParam
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        
        if self.acc:
            replaceWith(res, self.placeHolder, res)
        self.isDuplicating = False
        self.placeHolder = None
        
        return res
    
    def subs(self, idsDict, explored):
        super(Sum, self).subs(idsDict, explored)
        for idx in self.iList:
            idx.subs(idsDict)
        for i in range(len(self.uFactors)):
            self.uFactors[i] = self.uFactors[i].subs(idsDict) 
        for idx in idsDict:
            if idx in self.iPriority:
                self.iPriority[idsDict[idx]] = self.iPriority.pop(idx) 
        for i in range(len(self.outDep)):
            self.outDep[i] = self.outDep[i].subs(idsDict) 
        for i in range(len(self.outerIdx)):
            self.outerIdx[i] = self.outerIdx[i].subs(idsDict) 
        for i in range(len(self.forceInitIdx)):
            self.forceInitIdx[i] = self.forceInitIdx[i].subs(idsDict)
        
        
    def buildout(self, out, src=None):

        src = self.getInexprMat(0)
            
        if(out):
            self.out = out
        else: 
            self.out = src.duplicate("S"+ str(globalSSAIndex()), o=[sympify(0),sympify(0)], fL=fI(src.size[0]), fR=fI(src.size[1]))
    
    def getIds(self, symSets):
        # returns a tuple of sets of indices corresponding to the input symbols
        res = []
        
        for s in symSets:
            l = set()
            while(len(s) > 0):
                sym = s.pop()
                idx = next(ifilter(lambda i: i.hasSym(sym), self.iList), None)
                l.update( [idx] )
                s.update(idx.getSyms())
            res.append(l)
        return tuple(res)
    
    def getSyms(self):
        return set([ idx.i for idx in self.iList ])
    
    def multByG(self, caller, fL, fR, idsDict, explored, opts):
        
        if self in explored:
            return G(fL, self, fR)
#             return G(fL, explored[self], fR)
        
        explored.append(self)
        
        iList, uFactors, iPriority = [], [], {}
        for i in range(len(self.iList)):
            idx = self.iList[i]
            if not idx.i in idsDict:
                iList.append(idx)
                uFactors.append(self.uFactors[i])
                iPriority[idx.i] = self.iPriority[idx.i]
        
        if len(iList) == len(self.iList):
#             self.subs(idsDict, explored)
            self.subs(idsDict, [])
            return G(fL, self, fR)

#         dup = self.duplicate(everything=False)
#         explored[self] = dup 
        
        inexpr = [ e.multByG(self, fL, fR, idsDict, explored, opts) for e in self.inexpr ] # if isinstance(e, ParamMat) ]
        
        if not iList:
            del self.inexpr[:]
            inexpr[0].delPred(self)
            self.delPred(caller)
#             for p in self.pred:
#                 p[0].inexpr[p[1]] = inner
#                 p[0].setAsPredOfInExpr(p[1])
#             
            return inexpr[0]
        
        self.iList, self.uFactors, self.iPriority = iList, uFactors, iPriority
        self.inexpr = inexpr
        self.setAsPred()
        self.buildout(None)
        
        # Here we update the Sum's output.
        # In case of accumulation, we need to make sure
        # that the IMFs of the implicit G loose any reference to indices
        # no longer required.
        if self.acc:
            g = next(ifilter(lambda p: isinstance(p[0], G), self.pred), None)[0]
            ln, lN = g.fL.n, self.out.size[0] 
            rn, rN = g.fR.n, self.out.size[1]
             
            lb, rb = g.fL.of(0), g.fR.of(0)
               
            symList = self.getSyms()
            sL = g.fL.of(0).atoms(Symbol)
            for s in sL:
                if not s in symList:
                    lb = lb - s
            sR = g.fR.of(0).atoms(Symbol)
            for s in sR:
                if not s in symList:
                    rb = rb - s
            newfL, newfR = fHbs(ln, lN, lb, 1), fHbs(rn, rN, rb, 1)
             
            g.fL, g.fR = newfL, newfR
            g.buildout(None)

        for i in range(len(self.outDep)):
            self.outDep[i] = self.outDep[i].subs(idsDict) 
        for i in range(len(self.outerIdx)):
            self.outerIdx[i] = self.outerIdx[i].subs(idsDict) 
        for i in range(len(self.forceInitIdx)):
            self.forceInitIdx[i] = self.forceInitIdx[i].subs(idsDict)

        return self
    
    def isFullyUnrolled(self):
        ids, reqSubs = [], [ {} ]
        for idx in self.iList:
            if idx.isTop:
                tSubs = [{idx.i:idx.b}] + [{idx.i:idx.b+idx.s}] if idx.b+idx.s < idx.e else [ {} ]
                if len(reqSubs) > 0:
                    reqSubs = [ dict(r.items()+t.items()) for r in reqSubs for t in tSubs ]
                else: reqSubs = tSubs
            else:
                ids.append(idx)
        
        return not any(map(lambda idx: idx.needsLoop(reqSubs) , ids))


    def computeDepSums(self, opts, force=False):
        if force or self.depSums is None:
            self.depSums = set(computeDependentSubexprOfType(self.inexpr[0], self.iList, [], opts, Sum))
            for s in self.depSums:
                s.computeDepSums(opts, force)
        
    def __hash__(self):
        tin = tuple(self.inexpr)
        tIList = tuple(self.iList)
        key = (hash('Sum'), hash(tin), hash(tIList))
        return hash(key)
    
    def __eq__(self, other):
        if not isinstance(other, Sum):
            return False
        if self.isCheckingEq:
            return other.isCheckingEq and self.checkMark == other.checkMark
        
        self.isCheckingEq = other.isCheckingEq = True
        self.checkMark = other.checkMark = getNextCheckMark()
        for e,o in zip(self.inexpr, other.inexpr):
            if e != o:
                self.isCheckingEq = other.isCheckingEq = False
                self.checkMark = other.checkMark = -1
                return False
        for e,o in zip(self.iList, other.iList):
            if not e.equivalent(o):
                self.isCheckingEq = other.isCheckingEq = False
                self.checkMark = other.checkMark = -1
                return False
        
        self.isCheckingEq = other.isCheckingEq = False
        self.checkMark = other.checkMark = -1
        return True and (self.acc == other.acc)

    def __str__(self):
        acc = "( acc: " + str(self.inexpr[1]) + " )" if self.acc else ""
        return "Sum_{" + str(self.iList) + "} ( " + str(self.inexpr[0]) + " )" + acc

            
############################ (Temp) ##########################################


def avoidInit(expr, context, explored, opts):
    '''
    Intermediate Sums should initialize their outputs. 
    '''
    if isinstance(expr, Quantity): return
    
    if not expr in explored:
        explored.append(expr)
        subexprs = []
        if isinstance(expr, Sum):
            out = expr.getOut()
            if context.bindingTable.isBound(out):
                phys = context.bindingTable.getPhysicalLayout(out)
                if phys in context.signature:
                    expr.init = False
                    expr.isBoundToParam = True
            subexprs = computeIndependentSubexpr(expr.inexpr[0], expr.iList, explored, opts)
        else:
            subexprs = expr.inexpr
        for sub in subexprs:
            avoidInit(sub, context, explored, opts)

if __name__ == "__main__":
    c = Condition([CondTerm([CondFactor(['i','j'], '>')])])
    cc = deepcopy(c)
    print id(c.condterms[0].condfactors), id(cc.condterms[0].condfactors)
