'''
Created on May 9, 2014

@author: danieles
'''

import sympy
import re
from copy import copy, deepcopy
from sympy import Symbol, sympify, Max, Min, Tuple, Eq, Gt, Wild\
# , Basic
# from sympy.printing.str import StrPrinter
from itertools import count
from src.dsls.llparser import llParser, llSemantics
from src.dsls.holograph import Holonode
from _pyio import __metaclass__

from islpy import Set, Map, dim_type

__VERBOSE__ = False

drawing = True

ssaCounter = -1
uId = -1
exprCounter = count()
nameCounter = count()
checkCounter = count()
dimCounter = count()

def resetCounters():
    global ssaCounter, uId, exprCounter, nameCounter, checkCounter, dimCounter
    ssaCounter, uId = -1, -1
    exprCounter = count()
    nameCounter = count()
    checkCounter = count()
    dimCounter = count()

def globalSSAIndex():
    global ssaCounter
    ssaCounter += 1
    return ssaCounter

def getUId():
    global uId
    uId += 1
    return uId

def getNextCount():
    global exprCounter
    return exprCounter.next()

def getNextName():
    global nameCounter
    return 't' + str(nameCounter.next())

def getNextDim():
    global dimCounter
    return 'm' + str(dimCounter.next())

def getNextCheckMark():
    global checkCounter
    return 't' + str(checkCounter.next())

###################################################################

def floord(num, den):
    return sympy.floor((sympy.sympify(num).together()/sympy.sympify(den).together()).together())

def ceild(num, den):
    return sympy.ceiling((sympy.sympify(num).together()/sympy.sympify(den).together()).together())

sym_locals = {'floord': floord, 'ceild': ceild}

###################################################################

class llStmt(object):
    def __init__(self, eq=None, ann=None):
        if ann is None:
            ann = {}
        self.eq = eq
        self.ann = ann

    def get_pot_zero_dims(self):
        return self.eq.get_pot_zero_dims() 

    def computeSpaceIdxNames(self, opts, depth=1, baselevel=2):
        nublac = opts['isaman'].getNuBLAC(opts['precision'], opts['nu'])
        if not self.can_gen_with_nublac(nublac):
            baselevel = 2
        self.eq.computeSpaceIdxNames(i='i',j='j', ipfix=str(globalSSAIndex()), jpfix=str(globalSSAIndex()), opts=opts, depth=depth, baselevel=baselevel)

    def getSpaceIdxSet(self):
        return self.eq.getSpaceIdxSet()

    def can_gen_with_nublac(self, nublac, exclude=None, at_least_has_op=False):
        exclude = [] if exclude is None else exclude
        return self._can_gen_with_nublac(self.eq, nublac, exclude, at_least_has_op)
    
    def _can_gen_with_nublac(self, expr, nublac_db, exclude, at_least_has_op):
        if isinstance(expr, Assign):
            if not any(map(lambda t: isinstance(expr.inexpr[0], t), [Quantity, ParamMat, Tile])):
#             if not isinstance(expr.inexpr[0], ParamMat) and not isinstance(expr.inexpr[0], Quantity):
                return False
        if isinstance(expr, Operator):
            if not any(map(lambda t: isinstance(expr, t), [Assign, ParamMat, Tile]+exclude)):
                if at_least_has_op and not hasattr(nublac_db, expr.__class__.__name__) and not hasattr(nublac_db, '_'+expr.__class__.__name__):
                        return False
                elif not at_least_has_op and not hasattr(nublac_db, expr.__class__.__name__):
                        return False
            return all(map(lambda s: self._can_gen_with_nublac(s, nublac_db, exclude, at_least_has_op), expr.inexpr))
        return True
        
    def getHolograph(self):
        res = llStmt()
        res.ann = deepcopy(self.ann)
        res.eq = self.eq.getHolograph()
        return res

    def getRealgraph(self):
        res = llStmt()
        res.ann = deepcopy(self.ann)
        res.eq = self.eq.getRealgraph()
        return res

    def copySubs(self, dic):
        res = llStmt()
        res.ann = deepcopy(self.ann)
        res.eq = dic.get(self.eq, self.eq)
        return res

    def get_ordered_choices(self, dic, choices_list):
        choices_list.append(dic.get(self.eq, self.eq).choices)

    def __deepcopy__(self, memo):
        res = llStmt()
        res.ann = deepcopy(self.ann)
        res.eq = self.eq.duplicate()
        return res

    def resetComputed(self):
        self.eq.resetComputed()

    def getInOutOrder(self):
        return self.eq.getInOutOrder()

    def toLatex(self, context, ind=0, subs=None):
        res = ind*" " + "$" + self.eq.toLatex(context, ind, subs) + "$"
        return res
    
    def unroll(self, ids_dict):
        self.eq.subs(ids_dict)

    def expose_empty_eqs_unroll(self, ids_dict):
        self.eq.subs(ids_dict)
    
    def flatten(self):
        pass
    
    def getOps(self):
        return self.eq.getOps()

    def getFlops(self):
        return self.eq.getFlops()
        
    def __str__(self):
        res = "Eq: " + str(self.eq) + "\n"
        res += "Eq.ann: " + str(self.ann) + "\n"
        return res

    def toLL(self, tab=""):
#         res = "/*\n  " + str(self.eq.info) + "\n*/\n"
        res = tab + self.eq.toLL()
        return res

    def _declare(self, tab, dep_map, dims_map, expr_map, order):
        #order gives the left-to-right order of appearance in the expr 
        #TODO: Vectors could still be interpreted as matrices. Scalar currently not supported.
        in_expr_list, out_expr_list = [], []
        name_list = [ m.name for m in dep_map ]
        def _declare_no_dep(m):
#             dims = m.getFlatSize()
#             sdims = [ dims_map[d] for d in dims ]
            sdims = dims_map[m]
            iotype = m.attr['ckiotype']
            expr_list = in_expr_list if iotype == "Input" else out_expr_list
            expr_list.append(expr_map[m])
            props = ", ".join(m.attr.get('props', []))
            if props:
                props = ", " + props
            ow = m.attr.get('ow', None)
            sow = "" if not ow or ow not in name_list else (", overwrites(%s)" % ow) 
            decl = tab + "Matrix %s(%s,%s) <%s%s%s>;\n" % (m.name, sdims[0], sdims[1], iotype, props, sow)
            return decl  
        def _declare_with_dep(m, dep, ow):
#             dims = m.getFlatSize()
#             sdims = [ dims_map[d] for d in dims ]
            sdims = dims_map[m]
            iotype = dep.attr['ckiotype']
            expr_list = in_expr_list if iotype == "Input" else out_expr_list
            expr_list.append(expr_map[m])
            props = ", ".join(m.attr.get('props', []))
            if props:
                props = ", " + props
            sow = "" if not ow or ow not in name_list else (", overwrites(%s)" % ow) 
            decl = tab + "Matrix %s(%s,%s) <%s%s%s>;\n" % (m.name, sdims[0], sdims[1], iotype, props, sow)
            return decl  

        m_ow_no_dep, with_dep = [], {} 
        for k,v in dep_map.iteritems():
            if v is None:
                m_ow_no_dep.append(k)
            else:
                with_dep[k] = v
        
        import networkx as nx
        g_ow_no_dep = nx.DiGraph()
        for m in m_ow_no_dep:
            ow = m.attr.get('ow', None)
            m_list = filter(lambda m: m.name == ow, m_ow_no_dep) #Should produce exactly one
            if not m_list:
                g_ow_no_dep.add_node(m)
            else:
                g_ow_no_dep.add_edge(m, m_list[0])
        nbunch = [ m for m in order if m in g_ow_no_dep ]
        order_of_decl = nx.topological_sort(g_ow_no_dep, nbunch=nbunch, reverse=True)
#         #revert dict: m: dep ==> dep: m - to make lookup easier
#         with_dep_rev = { v: k for k,v in with_dep.iteritems() }
        g_ow_with_dep = nx.DiGraph()
        for m,dep in with_dep:
            ow = dep.attr.get('ow', None)
            m_list = filter(lambda m_dep: m_dep[1].name == ow, with_dep.iteritems()) #Should produce exactly one
            if not m_list:
                g_ow_no_dep.add_node((m, None))
            else:
                g_ow_no_dep.add_edge((m,m_list[0][1],m_list[0][0].name), m_list[0][0])
        nbunch = [ m for m in order if m in g_ow_with_dep ]
        order_of_decl_with_dep = nx.topological_sort(g_ow_with_dep, nbunch=nbunch, reverse=True)

        ck_decl = '';
        for m in order_of_decl:
            ck_decl += _declare_no_dep(m)
        for m_dep_ow in order_of_decl_with_dep:
            ck_decl += _declare_with_dep(*m_dep_ow)

        return ck_decl, in_expr_list, out_expr_list

    def to_algo(self):
        global dimCounter
        dimCounter = count()
        decl_map, dep_map, dims_map, expr_map, order, sizes_map = {}, {}, {}, {}, [], {}
        eq_ck = self.eq.to_algo(decl_map, dep_map, dims_map, expr_map, order, sizes_map)
        ck_prog = "program %s\n" % self.eq.algo_signature()
        ck_decl, in_expr_list, out_expr_list = self._declare(" ", dep_map, dims_map, expr_map, order)
        ck_prog += ck_decl
        ck_prog += " " + eq_ck
        return ck_prog, sizes_map, in_expr_list, out_expr_list
        
    
    def __repr__(self):
        return str(self)
        
class llProgram(object):
    def __init__(self, semObj=None):
        super(llProgram, self).__init__()
        self.mDict = {} if semObj is None else dict(semObj.mDict)
        self.ann = { }
        stmtList = llBlock()
        if isinstance(semObj, llExtSemantics):
            stmtList.append(semObj.stmtList) 
#             stmtList.extend([ llStmt(eq) for eq in semObj.eqList ])
#         elif isinstance(semObj, llProgram):
#             for s in semObj.stmtList:
#                 newStmt = llStmt(s.eq)
#                 newStmt.ann = dict(s.ann.items())
#                 stmtList.append(newStmt)
        self.stmtList = stmtList
#         self.set_ids_bounds()

    def __deepcopy__(self, memo):
        res = llProgram()
        res.ann = deepcopy(self.ann)
        res.mDict = { k: self.mDict[k].duplicate() for k in self.mDict }
        res.stmtList = deepcopy(self.stmtList, memo)
        return res
    
    def update_info(self):
        rc = RangeCalculator()
        rc.calc(self)
    
    def getEqsList(self):
        return self._getEqsList(self.stmtList)

    def getStmtList(self):
        return self._getStmtList(self.stmtList)
    
    def _getEqsList(self, expr):
        res = []
        if isinstance(expr, llBlock):
            for s in expr:
                res.extend( self._getEqsList(s) )
        elif isinstance(expr, llLoop):
            res.extend( self._getEqsList(expr.body) )
        elif isinstance(expr, llGuard):
            for b in expr.bodys:
                res.extend( self._getEqsList(b) )
        else:
            res.append(expr.eq)
        return res

    def _getStmtList(self, expr):
        res = []
        if isinstance(expr, llBlock):
            for s in expr:
                res.extend( self._getStmtList(s) )
        elif isinstance(expr, llLoop):
            res.extend( self._getStmtList(expr.body) )
        elif isinstance(expr, llGuard):
            for b in expr.bodys:
                res.extend( self._getStmtList(b) )
        else:
            res.append(expr)
        return res

    def get_funcs_nongen_with_nublac(self, nublac):
        return self._get_funcs_nongen_with_nublac(self.stmtList, nublac)

    def _get_funcs_nongen_with_nublac(self, expr, nublac):
        res = []
        if isinstance(expr, llBlock):
            for i in range(len(expr)):
                blk_res =  self._get_funcs_nongen_with_nublac(expr[i], nublac)
                if blk_res:
                    if isinstance(blk_res, list):
                        res.extend( blk_res )
                    else:
                        res.append( [blk_res, expr, i] )
        elif isinstance(expr, llLoop):
            return self._get_funcs_nongen_with_nublac(expr.body, nublac)
        elif isinstance(expr, llGuard):
            for b in expr.bodys:
                res.extend( self._get_funcs_nongen_with_nublac(b, nublac) )
        else:
            return self._get_first_nongen_func(expr.eq, nublac)
        return res
    
    def get_first_eq_nongen_with_nublac(self, nublac):
        return self._get_first_eq_nongen_with_nublac(self.stmtList, nublac)

    def _get_first_eq_nongen_with_nublac(self, expr, nublac):
        if expr is None:
            return None
        if isinstance(expr, llBlock):
            for i in range(len(expr)):
                res = self._get_first_eq_nongen_with_nublac(expr[i], nublac)
                if res:
                    if isinstance(res, list):
                        return res
                    func = res.inexpr[1] if res.inexpr[1].is_func() else None
                    return [res.algo_signature(), expr, i, func]
        elif isinstance(expr, llLoop):
            return self._get_first_eq_nongen_with_nublac(expr.body, nublac)
        elif isinstance(expr, llGuard):
            for b in expr.bodys:
                res = self._get_first_eq_nongen_with_nublac(b, nublac)
                if isinstance(res, list):
                    return res
        else:
            if not expr.can_gen_with_nublac(nublac, at_least_has_op=True):
                return expr.eq
        return None

    def get_first_func_nongen_with_nublac(self, nublac):
        return self._get_first_func_nongen_with_nublac(self.stmtList, nublac)

    def _get_first_func_nongen_with_nublac(self, expr, nublac):
        if isinstance(expr, llBlock):
            for i in range(len(expr)):
                res = self._get_first_func_nongen_with_nublac(expr[i], nublac)
                if res:
                    if isinstance(res, list):
                        return res
                    return [res, expr, i]
        elif isinstance(expr, llLoop):
            return self._get_first_func_nongen_with_nublac(expr.body, nublac)
        elif isinstance(expr, llGuard):
            for b in expr.bodys:
                res = self._get_first_func_nongen_with_nublac(b, nublac)
                if isinstance(res, list):
                    return res
        else:
            return self._get_first_nongen_func(expr.eq, nublac)
        return None

    def _get_first_nongen_func(self, expr, nublac):
        if isinstance(expr, Operator):
            if isinstance(expr, Function) and not hasattr(nublac, expr.name):
                return expr
            for s in expr.inexpr:
                res = self._get_first_nongen_func(s, nublac)
                if res:
                    return res
        return None
    
    def get_can_vec_with_nublac_list(self, nublac):
        stmt_list = self._getStmtList(self.stmtList)
        return [ s.can_gen_with_nublac(nublac) for s in stmt_list ]
    
    def unroll(self):
        self.stmtList.unroll(ids_dict={})

    def flatten(self):
        self.stmtList.flatten()

    def remove_empty_eqs(self):
        self.stmtList.remove_empty_eqs()

    def expose_empty_eqs(self):
        self.stmtList.expose_empty_eqs_unroll(ids_dict={})
        
    def getSpaceIdxSet(self):
        return self.stmtList.getSpaceIdxSet()

    def get_pot_zero_dims(self):
        return self.stmtList.get_pot_zero_dims()
    
    def getHolograph(self):
        newLlp = self.__class__()
        newLlp.mDict = dict(self.mDict)
        newLlp.ann = dict(self.ann)
        newLlp.stmtList = self.stmtList.getHolograph()
        return newLlp

    def getRealgraph(self):
        newLlp = self.__class__()
        newLlp.mDict = dict(self.mDict)
        newLlp.ann = dict(self.ann)
        newLlp.stmtList = self.stmtList.getRealgraph()
        return newLlp

    def copySubs(self, dic):
        newLlp = self.__class__()
        newLlp.mDict = dict(self.mDict)
        newLlp.ann = dict(self.ann)
        newLlp.stmtList = self.stmtList.copySubs(dic)
        return newLlp
    
    def get_ordered_choices(self, dic, choices_list):
        self.stmtList.get_ordered_choices(dic, choices_list)
        
    def resetComputed(self):
        self.stmtList.resetComputed()

    def computeSpaceIdxNames(self, opts, depth=1, baselevel=2):
        for b in self.stmtList:
            b.computeSpaceIdxNames(opts, depth, baselevel)
        
    def __str__(self):
        res = "Decl { " + str(self.mDict) + " }\n"
        res += "~"*30 + "\n\n"
        res += "Ann: " + str(self.ann) + "\n\n"
        res += "~"*30 + "\n\n"
        res += str(self.stmtList)
        return res

    def toLL(self):
        return self.stmtList.toLL()

    def toLatex(self, context, ind=0, comment=None):
        subs = None
        if 'setIndices' in self.ann:
            r = re.compile("([a-zA-Z]+)([0-9]*)")
            subs = { i: r.match(i) for i in self.ann['setIndices'] }
            subs = { i: subs[i].group(1)+"_{" + subs[i].group(2) + "}" for i in subs }
        res = ("% " + comment + "\n\n\n") if comment is not None else ""
        res += "\documentclass{article}\n"
        res += "\usepackage{mathtools}\n\usepackage{listings}\n\usepackage{leftidx}\n\usepackage[a0paper]{geometry}\n\n"
        res += "\everymath{\displaystyle}\n\n"
        res += "\\begin{document}\n\lstset{language=Matlab}\n"
        res += "\\begin{lstlisting}[mathescape]\n"
        res += self.stmtList.toLatex(context, ind, subs)
        res += "\end{lstlisting}\n"
        res += "\end{document}\n"
        return res
    
    def getInOutOrder(self):
        return self.stmtList.getInOutOrder()
    
    def getFlops(self):
#         c = 0;
#         for s in self.stmtList:
#             c += s.getFlops()
#         return c
        return self.stmtList.getFlops()

    def getOps(self):
        return self.stmtList.getOps()
    
    def __repr__(self):
        return str(self)
    
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def create_map_from_expression(sym_expr, indices=None, isl_set=None):
    if indices is None:
        if isl_set is None:
            raise Exception('Cannot create a map without a context.')
        indices = isl_set.get_var_names(dim_type.set)
    expr_map = Map("{[%s] -> [%s]}" % (",".join(indices), str(sym_expr)))
    return expr_map

def get_range_bound_over_domain(domain, expr_map, fold_type):
    r = expr_map.intersect_domain(domain).range()
    if fold_type == 'min':
        foldset = r.lexmin()
    else:
        foldset = r.lexmax()
    pnts = []
    foldset.foreach_point(pnts.append)
    fold = sympify( pnts[0].get_coordinate_val(dim_type.set, 0).to_python() , locals=sym_locals)
    return fold

def get_expr_bound_over_domain(indices, domain, sym_expr, fold_type):
    if sym_expr.is_Number:
        return sym_expr
#     expr_map = create_map_from_expression(sym_expr, isl_set=domain)
    expr_map = create_map_from_expression(sym_expr, indices=indices)
    return get_range_bound_over_domain(domain, expr_map, fold_type)

def expr_is_bounded_over_domain(indices, domain, sym_expr):
    if sym_expr.is_Number:
        return True
    expr_map = create_map_from_expression(sym_expr, indices=indices)
    return expr_map.intersect_domain(domain).range().is_bounded()

def use_floord_ceild(sym_expr):
    a,b = Wild('a'), Wild('b', exclude=[sympy.Add, sympy.Symbol], properties=[lambda f: f>0])
    floord = sympy.Function('floord')
    ceild = sympy.Function('ceild')
    sym_expr = sym_expr.replace(sympy.floor(a/b), lambda a,b: floord(a,b))
    sym_expr = sym_expr.replace(sympy.ceiling(a/b), lambda a,b: ceild(a,b))
    return sym_expr
    
def use_floor_ceiling(sym_expr):
    a,b = Wild('a'), Wild('b', exclude=[sympy.Add, sympy.Symbol], properties=[lambda f: f>0])
    floord = sympy.Function('floord')
    ceild = sympy.Function('ceild')
    sym_expr = sym_expr.replace(floord(a,b), lambda a,b: sympy.floor((a.together()/b.together()).together()))
    sym_expr = sym_expr.replace(ceild(a,b), lambda a,b: sympy.ceiling((a.together()/b.together()).together()))
    return sym_expr

class llExtSemantics(llSemantics):
     
    
    def __init__(self, sizes=None, mDict=None, opts=None):
        super(llExtSemantics, self).__init__()
        self.mDict = {} if not mDict else mDict
        self.sizes = {} if not sizes else sizes
        self.opts = {} if not opts else opts
        
        self.curr_lhs_out = None
        
        self.stmtListStack = [ [] ]
        self.stmtList = None
#         self.eqList = []
        init_info = self.opts.get('init_info', {})
        self.indicesStack = [ init_info.get('indices', []) ]
        self.iterspaceStack = [ init_info.get('polytope', Set("{[]}")) ]
        init_range = []
        for key in ['min', 'max', 'inc']:
            init_range.append( init_info.get(key, {}) )
        self.rangeStack = [ init_range ]
#         self.iterspaceStack = [ Set("{[]}") ]
#         self.rangeStack = [ [{},{},{}] ]
        self.resized_mats = {}
        self.imfStack = []
        self.annStack = []
        self.eqStack = []
        self.numexprStack = []
        self.condStack = []
        
#     def checkMat(self, varList):
#         for var in varList:
#             if var in self.mDict:
#                 exit("Parsing error > " + var + " already defined.")
    
#     def buildMatAttr(self, astVarType):
#         attr = {}
#         if 'attr' in astVarType:
#             if 'tin' in astVarType['attr']:
#                 attr = { 't':True }
#             elif 'tout' in astVarType['attr']:
#                 attr = { 't':True, 'o':True, 'i':False }
#             elif 'tinout' in astVarType['attr']:
#                 attr = { 't':True, 'o':True }
#             elif 'out' in astVarType['attr']:
#                 attr = { 'o':True, 'i':False }
#             elif 'inout' in astVarType['attr']:
#                 attr = { 'o':True }
# 
#         return attr
    
#     def matStruct(self, astVarType, sizes=None):
#         Struct = Matrix
#         if astVarType['mtype'] == 'symmetric':
#             Struct = Symmetric
#         elif 'attr' in astVarType:
#             if 'l' in astVarType['attr']:
#                 Struct = LowerTriangular
#             elif 'u' in astVarType['attr']:
#                 Struct = UpperTriangular
#             else:
#                 if sizes[0] == sizes[1]:
#                     Struct = SquaredMatrix
#         return Struct
# 
#     def matAccess(self, astVarType):
#         access = None
#         if astVarType['mtype'] == 'symmetric':
#             if 'l' in astVarType['attr']:
#                 access = LSMatAccess
#             elif 'u' in astVarType['attr']:
#                 access = USMatAccess
#         return access

    
    def declaration(self, ast):
#         varList = ast['name']
#         self.checkMat(varList)
#         for var in varList:
        var = ast['name']
        if var in self.mDict:
            exit("Parsing error > " + var + " already defined.")
        self.mDict[var] = getattr(self, 'type'+ast['vartype'])(str(var), ast.get('dims', None), ast['iotype'], ast.get('props', []), ast.get('ow', None))
        return ast

    def typeScalar(self, var, dims, iotype, props, ow):
        mAttr = self.buildMatAttr(dims, iotype, props, ow)
        return Scalar(var, scalar_block(), attr=mAttr)

    def typeVector(self, var, dims, iotype, props, ow):
        mAttr = self.buildMatAttr(dims, iotype, props, ow)
        sM = self.numexprStack.pop()
        M = self.maximize_size(var, sM)
#         sM = astVarType['attr'][0]
#         M = str(sM) if is_number(sM) else self.sizes[sM]
        return Matrix(var, scalar_block(), (M,1), attr=mAttr)
    
    def typeMatrix(self, var, dims, iotype, props, ow):
        mAttr = self.buildMatAttr(dims, iotype, props, ow)

        sN = self.numexprStack.pop()
        sM = self.numexprStack.pop()
        M = self.maximize_size(var, sM, [0])
        N = self.maximize_size(var, sN, [1])
        
        Struct = self.matStruct(props, (M,N))
        return Struct(var, scalar_block(), (M,N), attr=mAttr, access=self.matAccess(props))

    def buildMatAttr(self, dims, iotype, props, ow):
        attr = {'ckiotype': iotype, 'props': deepcopy(props), 'ow': ow}
        if ow is not None:
            self.mDict[ow].attr['o'] = True
        if dims is not None and 'id' in dims:
            attr['dims'] = deepcopy(dims['id'])
        if iotype == 'tInput':
            attr.update({ 't':True })
        elif iotype == 'tOutput':
            attr.update({ 't':True, 'o':True, 'i':False })
        elif iotype == 'tInOut':
            attr.update({ 't':True, 'o':True })
        elif iotype == 'Output':
            attr.update({ 'o':True, 'i':False })
        elif iotype == 'InOut':
            attr.update({ 'o':True })

        return attr

    def matStruct(self, props, sizes=None):
        Struct = Matrix
        if 'Symmetric' in props:
            Struct = Symmetric
        elif 'LowerTriangular' in props:
            if 'ImplicitUnitDiagonal' in props:
                Struct = LowerUnitTriangular
            else:
                Struct = LowerTriangular
        elif 'UpperTriangular' in props:
            if 'ImplicitUnitDiagonal' in props:
                Struct = UpperUnitTriangular
            else:
                Struct = UpperTriangular
        elif 'Square' in props:
            Struct = SquaredMatrix
        return Struct

    def matAccess(self, props):
        access = None
        if 'Symmetric' in props:
            if 'LowerStorage' in props:
                access = LSMatAccess
            elif 'UpperStorage' in props:
                access = USMatAccess
        return access
    
    def maximize_size(self, mat_name, size, pos=None):
        if size.is_Number:
            return size
        pos = [0] if pos is None else pos
        new_size = get_expr_bound_over_domain(self.indicesStack[-1], self.iterspaceStack[-1], size, 'max') 
        if mat_name not in self.resized_mats:
            self.resized_mats[mat_name] = [None]*2
        for p in pos:
            self.resized_mats[mat_name][p] = new_size
        return new_size
        
        
#     def typescalar(self, var, astVarType):
#         mAttr = self.buildMatAttr(astVarType)
#         return Scalar(var, scalar_block(), attr=mAttr)
# 
#     def typevector(self, var, astVarType):
#         mAttr = self.buildMatAttr(astVarType)
#         sM = self.numexprStack.pop()
#         M = self.maximize_size(var, sM)
# #         sM = astVarType['attr'][0]
# #         M = str(sM) if is_number(sM) else self.sizes[sM]
#         return Matrix(var, scalar_block(), (M,1), attr=mAttr)
#     
#     def typematrix(self, var, astVarType):
#         mAttr = self.buildMatAttr(astVarType)
# 
#         sN = self.numexprStack.pop()
#         sM = self.numexprStack.pop()
#         M = self.maximize_size(var, sM, [0])
#         N = self.maximize_size(var, sN, [1])
# #         M = str(sM) if is_number(sM) else self.sizes[sM]
# #         N = str(sN) if is_number(sN) else self.sizes[sN]
#         
#         Struct = self.matStruct(astVarType, (M,N))
#         return Struct(var, scalar_block(), (M,N), attr=mAttr, access=self.matAccess(astVarType))

    def typetriangular(self, var, astVarType):
        mAttr = self.buildMatAttr(astVarType)
        Struct = self.matStruct(astVarType)
        sM = self.numexprStack.pop()
        M = self.maximize_size(var, sM, [0,1])
#         sM = astVarType['attr'][0]
#         M = str(sM) if is_number(sM) else self.sizes[sM]

        return Struct(var, scalar_block(), M, attr=mAttr)

    def typesymmetric(self, var, astVarType):
        mAttr = self.buildMatAttr(astVarType)
        Struct = self.matStruct(astVarType)
        sM = self.numexprStack.pop()
        M = self.maximize_size(var, sM, [0,1])
#         sM = astVarType['attr'][0]
#         M = str(sM) if is_number(sM) else self.sizes[sM]

        if 'l' in astVarType['attr']:
            access = LSMatAccess
        elif 'u' in astVarType['attr']:
            access = USMatAccess
        return Struct(var, scalar_block(), M, attr=mAttr, access=access)

    def typeidentity(self, var, astVarType):
        mAttr = self.buildMatAttr(astVarType)
        Struct = IdentityMatrix
        sM = self.numexprStack.pop()
        M = self.maximize_size(var, sM, [0,1])
#         sM = astVarType['attr'][0]
#         M = str(sM) if is_number(sM) else self.sizes[sM]

        return Struct(var, scalar_block(), M, attr=mAttr)

    def program(self, ast):
        self.stmtList = llBlock(self.stmtListStack.pop())
#         self.stmtList.updateAnn(self.ann)
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
        newRanges = []
        if not newIterspace.is_empty():
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
            newRanges[-1][sidx] = self.numexprStack[-1]
            
    #         ps = []
    #         lexmin.foreach_point(ps.append)
    #         pmin = ps[0].get_coordinate_val(dim_type.set, len(idcs)-1).to_python()
    #         ps = []
    #         lexmax.foreach_point(ps.append)
    #         pmax = ps[0].get_coordinate_val(dim_type.set, len(idcs)-1).to_python()
    
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
#         s = self.numexprStack.pop(-1)
#         ub = self.numexprStack.pop(-1)
#         lb = self.numexprStack.pop(-1)
#         body = llBlock(self.stmtListStack.pop())
#         self.stmtListStack[-1].append(llFor( sympify( ast['idx'] ), lb, ub, s, body) )
        s = self.numexprStack.pop()
        ub = self.numexprStack.pop()
        lb = self.numexprStack.pop()
        stmt_list = self.stmtListStack.pop()
        if not self.iterspaceStack[-1].is_empty():
            body = llBlock(stmt_list)
            loop = llFor(sympify(ast['looptop']['idx']), lb, ub, s, body)
            loop.mark_unroll( self.opts.get('tag_unroll', False) )
            self.stmtListStack[-1].append(loop)
        self.indicesStack.pop()
        self.iterspaceStack.pop()
        self.rangeStack.pop()
        return ast

    def guard(self, ast):
        cond = self.condStack[-1].getIslStr()

        iterspace = self.iterspaceStack[-1]
        idcs = self.indicesStack[-1]
        setstr = str("{ [" + ",".join(idcs) + "] : " + cond + " }") 
        newDimSet = Set(setstr)
        newIterspace = newDimSet.intersect(iterspace)

        newRanges = []
        if not newIterspace.is_empty():
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
        if not self.iterspaceStack[-1].is_empty():
            then = llBlock(stmt_list)
            self.stmtListStack[-1].append( llIf([then], [cond]) )
        self.iterspaceStack.pop()
        self.rangeStack.pop()
        return ast
        
    def equation(self, ast):
        if not self.iterspaceStack[-1].is_empty():
            rhs = self.eqStack.pop()
            if 'multiout' in ast['lhs']:
                lhs_list = []
                for i in range(len(ast['lhs']['multiout']),0,-1):
                    lhs_list.append( self.eqStack.pop(-i) )
                lhs = CartesianProduct(*lhs_list)
            else:
                lhs = self.eqStack.pop()
            self.curr_lhs_out = None
    #         eq = Assign(self.mDict[ast['lhs']['id']], rhs)
            eq = Assign(lhs, rhs)
            if not eq.is_empty():
                ann = ast.get('eqann', None)
                self.stmtListStack[-1].append( llStmt(eq, ann=ann) )
        return ast

#     def equation(self, ast):
#         rhs = self.eqStack.pop()
#         eq = Assign(self.mDict[ast['lhs']['id']], rhs)
#         self.eqList.append(eq)
#         return ast
    
    def lhs(self, ast):
        if not self.iterspaceStack[-1].is_empty():
            if not 'multiout' in ast:
                self.curr_lhs_out = self.eqStack[-1].getOut()
            else:
                out_list = []
                for i in range(len(ast['multiout']),0,-1):
                    out_list.append( self.eqStack[-i].getOut() )
                self.curr_lhs_out = QuantityCartesianProduct(*out_list) 
        return ast

    def lexpr(self, ast):
        if not self.iterspaceStack[-1].is_empty():
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
        
    def lterm(self, ast):
        if not self.iterspaceStack[-1].is_empty():
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
#                     if (t.getOut().isScalar() and f.getOut().isScalar()):
                    op = Div
#                     else:
#                         op = RDiv
                else:
                    op = LDiv
                    
                t = op(t,f)
    #             t = t*f
            self.eqStack.append(t)
        return ast

    def expr(self, ast):
        if not self.iterspaceStack[-1].is_empty():
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
        if not self.iterspaceStack[-1].is_empty():
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
#                     if (t.getOut().isScalar() and f.getOut().isScalar()):
                    op = Div
#                     else:
#                         op = RDiv
                else:
                    op = LDiv
                    
                t = op(t,f)
    #             t = t*f
            self.eqStack.append(t)
        return ast
    
#     def factor(self, ast):
#         if 'trans' in ast:
#             expr = self.eqStack.pop()
#             self.eqStack.append(T(expr))
#         elif 'id' in ast:
#             self.mDict[ast['id']].attr['eqi'] = True
#             self.eqStack.append(self.mDict[ast['id']])
#         return ast

    def gather(self, ast):
        if not self.iterspaceStack[-1].is_empty():
            if ast:
                if isinstance(ast, list):
                    self.annStack.append(None)
                else:
                    self.annStack.append(ast.get('ann', None))
        return ast

    def scatter(self, ast):
        if not self.iterspaceStack[-1].is_empty():
            e = self.eqStack.pop(-1)
            fR = self.imfStack.pop(-1)
            fL = self.imfStack.pop(-1)
            self.eqStack.append(S(fL, e, fR))
        return ast

    def scatteracc(self, ast):
        if not self.iterspaceStack[-1].is_empty():
            e = self.eqStack.pop(-1)
            fR = self.imfStack.pop(-1)
            fL = self.imfStack.pop(-1)
            self.eqStack.append(Sacc(fL, e, fR))
        return ast

    def preprocg(self, ast):
        if not self.iterspaceStack[-1].is_empty():
            self.imfStack.append("G")
        return ast

    def planefactor(self, ast):
        if not self.iterspaceStack[-1].is_empty():
            resize_N = False
            if 'inv' in ast:
                e = self.eqStack.pop()
                self.eqStack.append(Inverse(e))
            elif 'trans' in ast:
                e = self.eqStack.pop()
                self.eqStack.append(T(e))
            elif 'sqrt' in ast:
                e = self.eqStack.pop()
                self.eqStack.append(Sqrt(e))
            elif 'id' in ast:
                self.eqStack.append(self.mDict[ast['id']].duplicate())
                self.eqStack[-1].set_info( ['min', 'max', 'inc', 'polytope', 'indices'], self.rangeStack[-1]+[ self.iterspaceStack[-1], self.indicesStack[-1] ] )
                if ast['id'] in self.resized_mats:
                    resize_N = True
            elif 'const' in ast:
                name = str(ast['const'])
                mat_type = constant_matrix_type_with_value( sympify(name) )
                self.eqStack.append( mat_type(name, scalar_block(), (1,1)) )
                self.eqStack[-1].set_info( ['min', 'max', 'inc', 'polytope', 'indices'], self.rangeStack[-1]+[ self.iterspaceStack[-1], self.indicesStack[-1] ] )
            elif 'func' in ast:
                sub_exprs = []
                for _ in range(len(ast['func']['params'])):
                    sub_exprs.append(self.eqStack.pop())
                sub_exprs.reverse()
                n, m = self.numexprStack.pop(), self.numexprStack.pop()
                if isinstance(self.curr_lhs_out, QuantityCartesianProduct):
                    out_class, out_access = [], []
                    for lout in self.curr_lhs_out.qnt_list:
                        out_class.append(lout.__class__)
                        out_access.append(lout.access.__class__)
                else:
                    out_class, out_access = self.curr_lhs_out.__class__, self.curr_lhs_out.access.__class__
                self.eqStack.append(Function(str(ast['func']['name']), (m,n), sub_exprs, out_class=out_class, out_access=out_access))
            if self.imfStack:
                if self.imfStack[-1] != 'G':
                    e = self.eqStack.pop()
                    imfs = []
                    anns = []
                    while self.imfStack[-1] != 'G':
                        fR = self.imfStack.pop()
                        fL = self.imfStack.pop()
                        imfs.append((fL,fR))
                        anns.append(self.annStack.pop())
                    fL, fR = imfs[-1]
                    if resize_N:
                        if self.resized_mats[ast['id']][0] is not None:
                            fL.N = self.resized_mats[ast['id']][0]
                        if self.resized_mats[ast['id']][1] is not None:
                            fR.N = self.resized_mats[ast['id']][1]
                    if self.opts.get('fuse_gat', False):
    #                     fL, fR = imfs[-1]
                        for t in imfs[-2::-1]: 
                            fL, fR = fL.compose(t[0]), fR.compose(t[1])
                        e = G(fL, e, fR, ann=anns[-1])
                    else:
                        for t,a in zip(imfs[::-1],anns[::-1]): 
                            e = G(t[0], e, t[1], ann=a)
                    self.eqStack.append(e)
                self.imfStack.pop() #Pop G-marker from the stack 
            if 'sign' in ast and ast['sign'] == '-':
                e = self.eqStack.pop()
                self.eqStack.append( Neg(e) )
        return ast
    
    def genimf(self, ast):
        if not self.iterspaceStack[-1].is_empty():
            params = []
            for i in range(4):
                params.append(self.numexprStack.pop(-4+i))
            self.imfStack.append(IMF(*params))
        return ast

    def himf(self, ast):
        if not self.iterspaceStack[-1].is_empty():
            l = len(ast['params'])
            params = []
            for i in range(l):
                params.append(self.numexprStack.pop(-l+i))
            self.imfStack.append(fHbs(*params))
        return ast

    def iimf(self, ast):
        if not self.iterspaceStack[-1].is_empty():
            param = self.numexprStack.pop(-1)
            self.imfStack.append(fI(param))
        return ast

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
        if not self.iterspaceStack[-1].is_empty():
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

#     def numterm(self, ast):
#         if not self.iterspaceStack[-1].is_empty():
#             l = len(ast['numfactor'])
#             t = self.numexprStack.pop(-l)
#             l-=1
#             while(l>0):
#                 f = self.numexprStack.pop(-l)
#                 l-=1
#                 t = (t)*(f)
#             if 'numden' in ast:
#                 t = (t) / sympify(ast['numden'])
#             elif 'nummod' in ast:
#                 t = (t) % sympify(ast['nummod'])
#             self.numexprStack.append(t)
#         return ast

    def numfactor(self, ast):
        if not self.iterspaceStack[-1].is_empty():
            if 'modl' in ast:
                r = self.numexprStack.pop(-1)
                l = self.numexprStack.pop(-1)
                self.numexprStack.append(l%r)
            elif 'fnum' in ast:
                num = self.numexprStack.pop(-1)
                self.numexprStack.append(sympify("floord("+str(num)+","+str(sympify(ast['fden']))+")", locals=sym_locals))
            elif 'cnum' in ast:
                num = self.numexprStack.pop(-1)
                self.numexprStack.append(sympify("ceild("+str(num)+","+str(sympify(ast['cden']))+")", locals=sym_locals))
            elif 'minl' in ast:
                r = self.numexprStack.pop(-1)
                l = self.numexprStack.pop(-1)
                self.numexprStack.append(sympify("Min("+str(l)+","+str(r)+")", locals=sym_locals))
            elif 'maxl' in ast:
                r = self.numexprStack.pop(-1)
                l = self.numexprStack.pop(-1)
                self.numexprStack.append(sympify("Max("+str(l)+","+str(r)+")", locals=sym_locals))
            elif 'id' in ast:
                self.numexprStack.append(sympify(ast['id']))
            elif 'const' in ast:
                self.numexprStack.append(sympify(ast['const']))
        return ast

class RangeCalculator(object):
    def __init__(self):
        super(RangeCalculator, self).__init__()

    def calc(self, llprog, opts=None, ranges=None, iterspace=None, indices=None):
        if ranges is None:
            ranges = [{},{},{}]
        if iterspace is None:
            iterspace = Set("{[]}")
        if indices is None:
            indices = []
        self.llBlock(llprog.stmtList, opts, ranges, iterspace, indices)

    def llBlock(self, expr, opts, ranges, iterspace, indices):
        for s in expr:
            getattr(self, s.__class__.__name__)(s, opts, ranges, iterspace, indices)
    
    def llFor(self, expr, opts, ranges, iterspace, indices):
        sidx, sLb, sUb, sInc = str(expr.idx), str(expr.lb), str(expr.ub), str(expr.s)
        idcs = indices + [sidx]
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

        prev_inc_dict = ranges[-1]

        newRanges = []
        newRanges.append( { idx: sympify(pmin, locals=sym_locals) for idx,pmin in zip(idcs, mins) } )
        newRanges.append( { idx: sympify(pmax, locals=sym_locals) for idx,pmax in zip(idcs, maxs) } )
        newRanges.append( deepcopy(prev_inc_dict) )
        newRanges[-1][sidx] = expr.s

        getattr(self, expr.body.__class__.__name__)(expr.body, opts, newRanges, newIterspace, idcs)

    def llIf(self, expr, opts, ranges, iterspace, indices):
        cond = expr.conds[0].getIslStr() # Assuming a single branch
        idcs = indices
        setstr = str("{ [" + ",".join(idcs) + "] : " + cond + " }") 
        newDimSet = Set(setstr)
        newIterspace = newDimSet.intersect(iterspace)
        lexmin = newIterspace.lexmin()
        lexmax = newIterspace.lexmax()

        ps = []
        lexmin.foreach_point(ps.append)
        mins = [ ps[0].get_coordinate_val(dim_type.set, pos).to_python() for pos in range(len(idcs)) ]
        ps = []
        lexmax.foreach_point(ps.append)
        maxs = [ ps[0].get_coordinate_val(dim_type.set, pos).to_python() for pos in range(len(idcs)) ]

        prev_inc_dict = ranges[-1]

        newRanges = []
        newRanges.append( { idx: sympify(pmin, locals=sym_locals) for idx,pmin in zip(idcs, mins) } )
        newRanges.append( { idx: sympify(pmax, locals=sym_locals) for idx,pmax in zip(idcs, maxs) } )
        newRanges.append( deepcopy(prev_inc_dict) )

        getattr(self, expr.bodys[0].__class__.__name__)(expr.bodys[0], opts, newRanges, newIterspace, idcs)
        
    def llStmt(self, expr, opts, ranges, iterspace, indices):
        expr.eq.set_info(['min', 'max', 'inc', 'polytope', 'indices'], ranges+[iterspace, indices])
    
    
def parseLL(sizes, opts):
    import string
    
    with open(opts["source"]) as f:
        text = f.read()
    for p in sizes:
        text = text.replace('@'+p, str(sizes[p]))
    opts['currentLLSrc'] = text
    parser = llParser(parseinfo=False, comments_re="%%.*")
    sem = llExtSemantics(sizes)
    parser.parse(text, rule_name="program", whitespace=string.whitespace, semantics=sem)
    
    return llProgram(sem)

###################################################################

class llContainer(object):
    pass

class llBlock(list, llContainer):
    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)
        self.ann = {}

    def toLatex(self, context, ind=0, subs=None):
        res = ind*" " + "{\n"
        for b in self:
            res += b.toLatex(context, ind+2, subs) + "\n"
        res += ind*" " + "}\n"
        return res
    
    def updateAnn(self, ann):
        self.ann.update(ann)

    def computeSpaceIdxNames(self, opts, depth=1, baselevel=2):
        for b in self:
            b.computeSpaceIdxNames(opts, depth, baselevel)

    def getSpaceIdxSet(self):
        res = set()
        for b in self:
            res = res.union(b.getSpaceIdxSet())
        return res

    def get_pot_zero_dims(self):
        res = []
        for b in self:
            res.extend(b.get_pot_zero_dims()) 
        return res
    
    def getHolograph(self):
        res = llBlock()
        res.ann = deepcopy(self.ann)
        for s in self:
            res.append( s.getHolograph() )
        return res

    def getRealgraph(self):
        res = llBlock()
        res.ann = deepcopy(self.ann)
        for s in self:
            res.append( s.getRealgraph() )
        return res

    def copySubs(self, dic):
        res = llBlock()
        res.ann = deepcopy(self.ann)
        for s in self:
            res.append( s.copySubs(dic) )
        return res

    def get_ordered_choices(self, dic, choices_list):
        for s in self:
            s.get_ordered_choices(dic, choices_list)

    def __deepcopy__(self, memo):
        res = llBlock()
        res.ann = deepcopy(self.ann)
        for s in self:
            res.append( deepcopy(s, memo) )
        return res

    def getInOutOrder(self):
        res = []
        for s in self:
            res += s.getInOutOrder()
        finres = []
        for s in res:
            if s not in finres:
                finres.append(s)
        return finres

    def resetComputed(self):
        for s in self:
            s.resetComputed()
    
    def unroll(self, ids_dict):
        i = 0
        while i < len(self):
            self[i].unroll(ids_dict)
            if isinstance(self[i], llFor) and self[i].is_marked_unroll(ids_dict):
                loop = self.pop(i)
                k = len(loop.body)
                while loop.body:
                    stmt = loop.body.pop()
                    if not isinstance(stmt, llStmt) or not stmt.eq.is_empty():
                        self.insert(i, stmt)
                i+=k
            elif isinstance(self[i], llIf) and not self[i].conds[0].isSymbolic(ids_dict) and self[i].conds[0].isTrue(ids_dict):
                #Assuming only one branch
                if_stmt = self.pop(i)
                k = len(if_stmt.bodys[0])
                while if_stmt.bodys[0]:
                    stmt = if_stmt.bodys[0].pop()
                    if not isinstance(stmt, llStmt) or not stmt.eq.is_empty():
                        self.insert(i, stmt)
                i+=k
            else:
                i+=1
                
    def flatten(self):
        flat = False
        i = 0
        while not flat:
            while i<len(self) and not isinstance(self[i], llBlock):
                i+=1
            if i<len(self):
                b = self.pop(i)
                while b:
                    self.insert(i, b.pop())
            else:
                flat = True
        for s in self:
            s.flatten()

    def remove_empty_eqs(self):
        i = 0
        while i<len(self):
            if isinstance(self[i], llStmt):
                if self[i].eq.is_empty():
                    self.pop(i)
                elif self[i].eq.is_also_empty():
                    then = llBlock( [self.pop(i)] )
                    set_pot_zeros = set(then.get_pot_zero_dims())
                    need_cond = filter(lambda dim: not dim.is_Number, set_pot_zeros)
                    cond = Condition([ CondTerm([ CondFactor([str(d),'0'], '>') for d in need_cond ]) ])
                    if_stmt = llIf([then], [cond])
                    self.insert(i, if_stmt)
                    i+=1                    
                else:
                    i+=1
            elif isinstance(self[i], llFor) or isinstance(self[i], llBlock): 
                ll_b = self[i].body if isinstance(self[i], llFor) else self[i]
                ll_b.remove_empty_eqs()
                if not ll_b:
                    self.pop(i)
                else:
                    i+=1
            elif isinstance(self[i], llIf):
                for b in self[i].bodys:
                    b.remove_empty_eqs()
                j = 0
                while j < len(self[i].bodys):
                    if not self[i].bodys[j]:
                        self[i].bodys.pop(j)
                        self[i].conds.pop(j)
                    else:
                        j+=1
                if not self[i].bodys:
                    self.pop(i)
                else:
                    i+=1
                    

    def expose_empty_eqs_unroll(self, ids_dict):
        i = 0
        while i < len(self):
            self[i].expose_empty_eqs_unroll(ids_dict)
            if isinstance(self[i], llFor) and self[i].is_marked_unroll(ids_dict):
                loop = self.pop(i)
                k = len(loop.body)
                while loop.body:
                    stmt = loop.body.pop()
                    if not isinstance(stmt, llStmt) or not stmt.eq.is_empty():
                        self.insert(i, stmt)
                i+=k
            else:
                i+=1
            
    def getOps(self):
        c = 0;
        for s in self:
            c += s.getOps()
        return c

    def getFlops(self):
        c = 0;
        for s in self:
            c += s.getFlops()
        return c
        
    def __str__(self):
        res = ""
        i = 0
        for s in self:
            res += "Entry " + str(i) + ":\n" + str(s)
            i+=1
        return res

    def toLL(self, tab=""):
        res = ""
        for s in self:
            res += s.toLL(tab+"  ")
        return res
        
class llLoop(llContainer):
    def __init__(self):
        self.body = None

class llGuard(llContainer):
    def __init__(self):
        self.bodys = None
        self.conds = None

class llFor(llLoop):
    def __init__(self, idx, lb, ub, s, body=None, uFactor=None, ann=None):
        super(llFor, self).__init__()
        body = [] if body is None else body
        self.body = llBlock(body)
        self.idx = idx
        self.lb, self.ub, self.s = lb, ub, s
        if uFactor is None:
            self.uFactor = sympify(1)
        else:
            self.uFactor = uFactor
        self.ann = {} if ann is None else ann

        self.isBuilding = False
        self.isCheckingEq = False
        self.checkMark = -1
        self.isBinding = False
        self.isBoundToParam = False
        self.isDuplicating = False
        self.placeHolder = None
        self.depSums = None 
        self._unroll = False
    
    def mark_unroll(self, unroll):
        self._unroll = unroll
    
    def is_marked_unroll(self, ids_dict=None):
#         ids_dict = {} if ids_dict is None else ids_dict
#         lb, ub, s = self.lb.subs(ids_dict), self.ub.subs(ids_dict)+1, self.s.subs(ids_dict)
#         diff = ub-lb
#         return self._unroll or (diff.is_Number and s.is_Number and diff < s)
        return self._unroll
    
    def flatten(self):
        self.body.flatten()
        
#     def unroll(self, ids_dict):
#         if self._unroll:
#             lb, ub, s = self.lb.subs(ids_dict), self.ub.subs(ids_dict)+1, self.s.subs(ids_dict)
#             if any( map(lambda v: not v.is_Number,(lb,ub,s)) ):
#                 self.body.unroll(ids_dict)
#             else:
#                 new_body = llBlock()
#                 for i in range(lb, ub, s):
#                     tbody = deepcopy(self.body)
#                     tbody.unroll( dict( ids_dict.items() + [(self.idx,i)] ) )
#                     new_body.extend(tbody)
#                 del self.body[:]
#                 self.body = new_body
#         else:
#             lb, ub, s = self.lb.subs(ids_dict), self.ub.subs(ids_dict), self.s.subs(ids_dict)
#             diff = ub-lb
#             if diff.is_Number and s.is_Number and diff < s:
#                 self.mark_unroll(True)
#                 new_body = llBlock()
#                 tbody = deepcopy(self.body)
#                 tbody.unroll( dict( ids_dict.items() + [(self.idx,lb)] ) )
#                 new_body.extend(tbody)
#                 del self.body[:]
#                 self.body = new_body
#             else:
#                 self.body.unroll(ids_dict)

    def unroll(self, ids_dict):
        lb, ub, s = self.lb.subs(ids_dict), self.ub.subs(ids_dict), self.s.subs(ids_dict)
        diff = ub-lb
        if not self._unroll:
            if diff.is_Number and s.is_Number and diff < s:
                self.mark_unroll(True)
#             else:
#                 set_pot_zeros = set(self.body.get_pot_zero_dims())
#                 if filter(lambda dim: self.idx in dim, set_pot_zeros):
#                     self.mark_unroll(True)
        
        if self._unroll and not any( map(lambda v: not v.is_Number,(lb,ub,s)) ):
            if diff.is_Number and s.is_Number and diff%s == 0:
                ub = ub+1
            new_body = llBlock()
            for i in range(lb, ub, s):
                tbody = deepcopy(self.body)
                tbody.unroll( dict( ids_dict.items() + [(self.idx,i)] ) )
                new_body.extend(tbody)
            del self.body[:]
            self.body = new_body
        else:
            self.body.unroll(ids_dict)

    def expose_empty_eqs_unroll(self, ids_dict):
        set_pot_zeros = set(self.body.get_pot_zero_dims())
        if filter(lambda dim: self.idx in dim, set_pot_zeros):
            self.mark_unroll(True)
        
        lb, ub, s = self.lb.subs(ids_dict), self.ub.subs(ids_dict), self.s.subs(ids_dict)
        if self._unroll and not any( map(lambda v: not v.is_Number,(lb,ub,s)) ):
            diff = ub-lb
            if diff.is_Number and s.is_Number and diff%s == 0:
                ub = ub+1
            new_body = llBlock()
            for i in range(lb, ub, s):
                tbody = deepcopy(self.body)
                tbody.expose_empty_eqs_unroll( dict( ids_dict.items() + [(self.idx,i)] ) )
                new_body.extend(tbody)
            del self.body[:]
            self.body = new_body
        else:
            self.body.expose_empty_eqs_unroll(ids_dict)

    def computeSpaceIdxNames(self, opts, depth=1, baselevel=2):
        for s in self.body:
            s.computeSpaceIdxNames(opts, depth, baselevel)

    def get_pot_zero_dims(self):
        return self.body.get_pot_zero_dims()

    def getSpaceIdxSet(self):
        res = set( [str(self.idx)] )
        for b in self.body:
            res = res.union(b.getSpaceIdxSet())
        return res

    def getHolograph(self):
        res = llFor(deepcopy(self.idx), deepcopy(self.lb), deepcopy(self.ub), deepcopy(self.s))
        res.ann = deepcopy(self.ann)
        for s in self.body:
            res.body.append( s.getHolograph() )
        return res

    def getRealgraph(self):
        res = llFor(deepcopy(self.idx), deepcopy(self.lb), deepcopy(self.ub), deepcopy(self.s))
        res.ann = deepcopy(self.ann)
        for s in self.body:
            res.body.append( s.getRealgraph() )
        return res

    def copySubs(self, dic):
        res = llFor(deepcopy(self.idx), deepcopy(self.lb), deepcopy(self.ub), deepcopy(self.s))
        res.ann = deepcopy(self.ann)
        for s in self.body:
            res.body.append( s.copySubs(dic) )
        return res

    def get_ordered_choices(self, dic, choices_list):
        for s in self.body:
            s.get_ordered_choices(dic, choices_list)

    def __deepcopy__(self, memo):
        newFor = type(self)(deepcopy(self.idx), deepcopy(self.lb), deepcopy(self.ub), deepcopy(self.s))
        newFor.ann = deepcopy(self.ann)
        newFor.body = deepcopy(self.body, memo)
        newFor.isBuilding = self.isBuilding
        newFor.isCheckingEq = self.isCheckingEq
        newFor.checkMark = self.checkMark
        newFor.isBinding = self.isBinding
        newFor.isBoundToParam = self.isBoundToParam
        newFor.isDuplicating = self.isDuplicating
        newFor.placeHolder = self.placeHolder
        newFor.depSums = self.depSums 
        newFor._unroll = self._unroll

        return newFor

    def resetComputed(self):
        self.body.resetComputed()

    def getInOutOrder(self):
        return self.body.getInOutOrder()

    def toLatex(self, context, ind=0, subs=None):
        subs = {} if subs is None else subs
        idx, lb, ub, s = str(self.idx), str(self.lb), str(self.ub), str(self.s)
        res = ind*" " + "for $" + idx + "$ = $" + lb + "$ : $" + ub + "$ : $" + s + "$\n"
        for sub in subs:
            res = res.replace(sub, subs[sub])
        res += self.body.toLatex(context, ind+2, subs)
        return res

    def getOps(self):
        return self.body.getOps()

    def getFlops(self):
        return self.body.getFlops()
        
    def toEG(self): 
        return "For_{" + str(self.idx) + "}"

    def __str__(self):
        return "For_{" + str(self.idx)+";"+ str(self.lb)+";"+ str(self.ub)+";"+ str(self.s)+ "} ( " + str(self.body) + " )"

    def toLL(self, tab=""):
        return tab + "For [" + str(self.idx)+";"+ str(self.lb)+";"+ str(self.ub)+";"+ str(self.s)+ "] {\n\n" + self.body.toLL(tab) + "\n" + tab + "};\n"

class llIf(llGuard):
    def __init__(self, bodys=None, conds=None, ann=None):
        super(llIf, self).__init__()
        bodys = [] if bodys is None else bodys
        self.bodys = [ llBlock(b) for b in bodys ]
        self.conds = [] if conds is None else conds
        self.ann = {} if ann is None else ann

    def flatten(self):
        for b in self.bodys:
            b.flatten()
        
    def unroll(self, ids_dict):
        for b,cond in zip(self.bodys,self.conds):
            if cond.isSymbolic(ids_dict) or cond.isTrue(ids_dict):
                b.unroll(ids_dict)

    def expose_empty_eqs_unroll(self, ids_dict):
        for b in self.bodys:
            b.expose_empty_eqs_unroll(ids_dict)

    def get_pot_zero_dims(self):
        res = []
        for b in self.bodys:
            res.extend(b.get_pot_zero_dims()) 
        return res

    def computeSpaceIdxNames(self, opts, depth=1, baselevel=2):
        for b in self.bodys:
            b.computeSpaceIdxNames(opts, depth, baselevel)

    def getSpaceIdxSet(self):
        res = set()
        for b in self.bodys:
            res = res.union(b.getSpaceIdxSet())
        return res

    def getHolograph(self):
        res = llIf()
        res.ann = deepcopy(self.ann)
        for c in self.conds:
            res.conds.append( deepcopy(c) )
        for b in self.bodys:
            res.bodys.append( b.getHolograph() )
        return res

    def getRealgraph(self):
        res = llIf()
        res.ann = deepcopy(self.ann)
        for c in self.conds:
            res.conds.append( deepcopy(c) )
        for b in self.bodys:
            res.bodys.append( b.getRealgraph() )
        return res

    def copySubs(self, dic):
        res = llIf()
        res.ann = deepcopy(self.ann)
        for c in self.conds:
            res.conds.append( deepcopy(c) )
        for b in self.bodys:
            res.bodys.append( b.copySubs(dic) )
        return res

    def get_ordered_choices(self, dic, choices_list):
        for b in self.bodys:
            b.get_ordered_choices(dic, choices_list)

    def __deepcopy__(self, memo):
        newIf = type(self)()
        newIf.ann = deepcopy(self.ann)
        newIf.bodys = deepcopy(self.bodys, memo)
        newIf.conds = deepcopy(self.conds, memo)

    def resetComputed(self):
        for b in self.bodys:
            b.resetComputed()

    def getOps(self):
        return max([ b.getOps() for b in self.bodys])

    def getFlops(self):
        return max([ b.getFlops() for b in self.bodys])

    def toLatex(self, context, ind=0, subs=None):
        subs = {} if subs is None else subs
        cond = self.conds[0].toLatex(context, ind, subs)
        res = ind*" " + "if ( $" + cond + "$ )\n"
        for sub in subs:
            res = res.replace(sub, subs[sub])
        res += self.bodys[0].toLatex(context, ind+2, subs)
        return res

    def toEG(self): 
        return "If {"+ str(self.conds) +"}"
        
    def toLL(self, tab=""):
        return tab + "If [" + str(self.conds[0])+ "] {\n\n" + self.bodys[0].toLL(tab) + "\n" + tab + "};\n"
        
    def __str__(self):
        return "If_{" + str(self.conds) + "} ( " + str(self.bodys) + " )"

##############################################
#------------- Conditions -------------------#
##############################################
            
class Condition(object):
    def __init__(self, condterms):
        self.condterms = condterms
    
    def __repr__(self):
        return str(self)
        
    def __str__(self):
        return " || ".join(["(" + str(c) + ")" for c in self.condterms])

    def toLatex(self, context, ind=0, subs=None):
        return " \\vee ".join(["\left(" + c.toLatex(context, ind, subs) + "\\right)" for c in self.condterms])

    def subs(self, idsDict):
        for ct in self.condterms:
            ct.subs(idsDict)

    def dependsOn(self, idx):
        return any(map(lambda ct: ct.dependsOn(idx), self.condterms))
    
    def getIslStr(self):
        return " or ".join(["(" + c.getIslStr() + ")" for c in self.condterms])
    
    def getSymAtoms(self):
        symAtoms = [ ct.getSymAtoms() for ct in self.condterms ]
        setSymAtoms = set()
        for sa in symAtoms:
            setSymAtoms.update(sa)
        return setSymAtoms
    
    def isSymbolic(self, bounds):
        return any(map(lambda ct: ct.isSymbolic(bounds), self.condterms))
    
    def isTrue(self, bounds):
        return any(map(lambda ct: ct.isTrue(bounds), self.condterms))
    
    def simplify(self, bounds):
        newCondterms = [ ct.simplify(bounds) for ct in self.condterms if not ct.isTrue(bounds) ]
        if not newCondterms:
            newCondterms = [CondTerm([CondFactor(2*[sympify(1)], '==')])]
        return Condition(newCondterms)
    
    def __deepcopy__(self, memo):
        return Condition( deepcopy(self.condterms, memo) )
        
class CondTerm(object):
    def __init__(self, condfactors):
        self.condfactors = condfactors
    
    def __repr__(self):
        return str(self)
        
    def __str__(self):
        return " && ".join(["(" + str(f) + ")" for f in self.condfactors])

    def subs(self, idsDict):
        for cf in self.condfactors:
            cf.subs(idsDict)

    def dependsOn(self, idx):
        return any(map(lambda cf: cf.dependsOn(idx), self.condfactors))

    def toLatex(self, context, ind=0, subs=None):
        return " \wedge ".join(["left(" + f.toLatex(context, ind, subs) + "\\right)" for f in self.condfactors])

    def getIslStr(self):
        return " and ".join(["(" + f.getIslStr() + ")" for f in self.condfactors])

    def getSymAtoms(self):
        symAtoms = [ cf.getSymAtoms() for cf in self.condfactors ]
        setSymAtoms = set()
        for sa in symAtoms:
            setSymAtoms.update(sa)
        return setSymAtoms

    def isSymbolic(self, bounds):
        return any(map(lambda cf: cf.isSymbolic(bounds), self.condfactors))

    def isTrue(self, bounds):
        return all(map(lambda cf: cf.isTrue(bounds), self.condfactors))

    def simplify(self, bounds):
        newCondfactors = [ cf.simplify(bounds) for cf in self.condfactors if not cf.isTrue(bounds) ]
        if not newCondfactors:
            newCondfactors = [CondFactor(2*[sympify(1)], '==')]
        return CondTerm(newCondfactors)

    def __deepcopy__(self, memo):
        return CondTerm( deepcopy(self.condfactors, memo) )
        
class CondFactor(object):
    def __init__(self, numexprs, sym):
        self.numexprs = numexprs
        self.sym = sym
    
    def __repr__(self):
        return str(self)
        
    def __str__(self):
        return self.sym.join([ str( n ) for n in self.numexprs])

    def subs(self, idsDict):
        self.numexprs = [ ne.subs(idsDict) for ne in self.numexprs ]

    def dependsOn(self, idx):
        return any(map(lambda numexpr: idx in numexpr, self.numexprs))

    def toLatex(self, context, ind=0, subs=None):
        subs = {} if subs is None else subs
        localsubs = {'==': '=', '>=': '\geq', '<=': '\leq', '!=': '\\neq'}
        localsubs.update(subs)
        res =  self.sym.join([ str(n) for n in self.numexprs])
        for sub in localsubs:
            res = res.replace(sub, localsubs[sub])
        return res

    def getIslStr(self):
        res = self.sym.join([ str(n) for n in self.numexprs])
        res = res.replace('==', '=')
        return res

    def getSymAtoms(self):
        symAtoms = [ e.atoms(Symbol) for e in self.numexprs ]
        setSymAtoms = set()
        for sa in symAtoms:
            setSymAtoms.update(sa)
        return setSymAtoms

    def isSymbolic(self, bounds):
        return any(map(lambda e: not e.subs(bounds).is_number, self.numexprs))

    def isTrue(self, bounds):
        if self.isSymbolic(bounds):
            return False
        subexprs = [ str(e.subs(bounds)) for e in self.numexprs ]
        res = sympify(self.sym.join(subexprs), locals=sym_locals)
        return res 

    def simplify(self, bounds):
        return CondFactor([ e.subs(bounds) for e in self.numexprs ], self.sym)

    def __deepcopy__(self, memo):
        return CondFactor( deepcopy(self.numexprs, memo), deepcopy(self.sym, memo))

##############################################
#--------------Expressions-------------------#
##############################################


class Expression(object):
    '''
    Expression base class.
    '''
    def __init__(self):
        self.computed = False
        #depSet is used to store the set of indeces the expression depends upon
        self.handle = getNextCount() # Used to identify subexpr within an expr - Not meant for equality check
        self.pred = [ (None,None) ]
        self.depSet = set()
        self.polyStmts = []
        self.accIds = []
        self.info = {}
        
    def set_info(self, label_list, info_list):
        for l,i in zip(label_list, info_list):
#             if isinstance(i, Set) and i.is_singleton():
#                 self.info[l] = i.copy()
#             else:
            self.info[l] = deepcopy(i)
        
    def __add__(self, other):
        if not isinstance(other, Expression):
            raise TypeError
        return Add(self, other)

    def __sub__(self, other):
        if not isinstance(other, Expression):
            raise TypeError
        return Sub(self, other)

    def __mul__(self, other):
        selfOut = self.getOut()
        otherOut = other.getOut()
        if selfOut.isScalar() or otherOut.isScalar():
            return Kro(self, other)
        return Mul(self, other)
    
    def getInexprMat(self, i):
        if isinstance(self, Quantity):
            return None
        return self.inexpr[i].getOut()
#         if isinstance(self.inexpr[i], Quantity):
#             return self.inexpr[i]
#         if isinstance(self.inexpr[i], list):
#             return [ inexpr.getOut() for inexpr in self.inexpr[i] ]  
#         return self.inexpr[i].out

    def getInexprNuMat(self, i):
        if isinstance(self, Quantity):
            return None
        return None if isinstance(self.inexpr[i], Quantity) else self.inexpr[i].nuout

    def getInexprMatNuMat(self, i):
        return self.getInexprMat(i), self.getInexprNuMat(i)
        
    def setPolyStmts(self, polyStmts):
        self.polyStmts = polyStmts

    def updatePolyStmts(self, polyStmts):
        self.polyStmts += polyStmts
    
    def getPolyStmts(self):
        return self.polyStmts
    
    def getOutNuOut(self):
        return self.getOut(), self.getNuOut()
    
    def getNuOut(self):
        if isinstance(self, Quantity):
            return None
        elif isinstance(self, Operator):
            return self.nuout
    
    def getOut(self):
        if isinstance(self, Quantity):
            return self
        elif isinstance(self, Operator):
            return self.out
    
    def getNonTileOut(self):
#         if isinstance(self, Quantity):
        return self
#         elif isinstance(self, Operator):
#             return self.out

    def getNonTileExpr(self):
        return self
    
    def setComputed(self, value):
        self.computed = value
#         self.computed = False

    def resetComputed(self):
        self.computed = False
        
    def setModified(self):
        self.computed = False
    
    def isComputed(self):
        return self.computed

    def is_func(self):
        return False
    
    def dependsOn(self, idx):
        mat = self.getOut()
        # indices may be contained within the origin of the matrix or within the index mapping functions expressions
        symExprs = [mat.o[0], mat.o[1], mat.fL.of(0), mat.fR.of(0)]
        return any(map(lambda symExpr: idx in symExpr, symExprs))
        
    def same(self, other):
        return id(self) == id(other)

    def setAsPredOfInExpr(self, i):
        if self.inexpr[i].pred[0][0] is None: self.inexpr[i].pred = [ (self, i) ] 
        elif not any(map(lambda pred: pred[0].same(self) and pred[1] == i, self.inexpr[i].pred)):
            self.inexpr[i].pred += [ (self, i) ]

    def setAsPred(self):
        i = 0
        for e in self.inexpr:
            if e.pred[0][0] is None: e.pred = [ (self, i) ]
            elif not any(map(lambda pred: pred[0].same(self) and pred[1] == i, e.pred)):
                e.pred += [ (self, i) ]
            i += 1
    
    def delPred(self, expr):
        pos = []
        i = 0
        for e in self.pred:
            if e[0] is not None and e[0].same(expr):
                pos.append(i)
            i += 1
        for i in pos:
            self.pred.pop(i)
        if len(self.pred) == 0:
            self.pred.append((None,None))
    
    def getHolograph(self, memo=None):
        h = Holonode(self)
        if memo is not None:
            memo[id(self)] = h
        return h
    
    def subs(self, idsDict):
        self.depSet = set([ s.subs(idsDict) for s in self.depSet if s.subs(idsDict).is_Symbol ])

    def deepUpdateDep(self, depSet):
        self.depSet.update(depSet)

##############################################
#           Block-Matrix Expression          #
##############################################

class ColPartition(object):
    '''
    For describing the layout of a (set of) col(s) in a RowPartition
    as a Block-Matrix
    '''
    def __new__(cls, nCols, block, info=None):
        if block is not None:
            return super(ColPartition, cls).__new__(cls, nCols, block, info)
            
    def __init__(self, nCols, block, info=None):

        nCols = sympify(nCols, locals=sym_locals)
        info = {} if info is None else info
        idcs, dom_info = info.get('indices', []), info.get('polytope', Set("{[]}"))
        cols_bounded = expr_is_bounded_over_domain(idcs, dom_info, nCols)

#         if isinstance(block, Empty):
#             print "Warning: ColPartition  has empty Block."
        if __VERBOSE__:
            if cols_bounded:
                cols_min = get_expr_bound_over_domain(idcs, dom_info, nCols, 'min')
                cols_max = get_expr_bound_over_domain(idcs, dom_info, nCols, 'max')
                if cols_min == 0:
                    if cols_max == 0:
                        print "Warning: ColPartition has zero columns."
                    else:
                        print "Warning: ColPartition also has zero columns."
            else:
                print "Warning: ColPartition has unbounded nCols: %s over domain %s." % (str(nCols), str(dom_info))
 
        self.nCols = nCols
        self.block = block
        self.info = {}
        self.set_info(info.keys(), info.values())

    def is_bounded(self):
        idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
        cols_bounded = expr_is_bounded_over_domain(idcs, dom_info, self.nCols)
        return cols_bounded

    def is_also_empty(self):
        if self.is_empty():
            return True
        idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
        cols_bounded = expr_is_bounded_over_domain(idcs, dom_info, self.nCols)
        if cols_bounded:
            cols_min = get_expr_bound_over_domain(idcs, dom_info, self.nCols, 'min')
            return cols_min == 0
        return False

    def is_empty(self):
        if self.block.is_empty():
            return True
        idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
        cols_bounded = expr_is_bounded_over_domain(idcs, dom_info, self.nCols)
        if cols_bounded:
            cols_min = get_expr_bound_over_domain(idcs, dom_info, self.nCols, 'min')
            cols_max = get_expr_bound_over_domain(idcs, dom_info, self.nCols, 'max')
            return cols_min == 0 and cols_max == 0
        return False
    
    def subs(self, idsDict):
        self.nCols = self.nCols.subs(idsDict)
        self.block.subs(idsDict)

    def set_info(self, label_list, info_list):
        for l,i in zip(label_list, info_list):
#             if isinstance(i, Set) and i.is_singleton():
#                 self.info[l] = i.copy()
#             else:
            self.info[l] = deepcopy(i)
        self.block.set_info(label_list, info_list)
    
    def getRowSize(self):
        return self.block.size[0]

    def getColSize(self):
        return self.block.size[1]

    def getFlatRowSize(self):
        return self.block.getFlatSize()[0]

    def getFlatColSize(self):
        return self.block.getFlatSize()[1]
    
    def getScalar(self):
        return self.block.getScalar()
    
    def duplicate(self, prefix=""):
        return ColPartition(self.nCols, self.block.duplicate(prefix), self.info) if self.block.level > 1 else ColPartition(self.nCols, self.block, self.info)
    
    def transposedBlock(self):
        return self.block.transpose()
    
    def __hash__(self):
        key = (self.nCols, hash(self.block))
        return hash(key)
    
    def __eq__(self, other):
        if not isinstance(other, ColPartition):
            return False
        idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
        cols_bounded = expr_is_bounded_over_domain(idcs, dom_info, self.nCols)
        o_idcs, o_dom_info = other.info.get('indices', []), other.info.get('polytope', Set("{[]}"))
        o_cols_bounded = expr_is_bounded_over_domain(o_idcs, o_dom_info, other.nCols)
        if cols_bounded and o_cols_bounded:
            cols_min = get_expr_bound_over_domain(idcs, dom_info, self.nCols, 'min')
            cols_max = get_expr_bound_over_domain(idcs, dom_info, self.nCols, 'max')
            o_cols_min = get_expr_bound_over_domain(o_idcs, o_dom_info, other.nCols, 'min')
            o_cols_max = get_expr_bound_over_domain(o_idcs, o_dom_info, other.nCols, 'max')
            if not ( cols_min == o_cols_min and cols_max == o_cols_max ):
                return False
        elif(self.nCols != other.nCols):
            return False
        return self.block == other.block
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "| " +  str(self.nCols) + ", " + str(self.block) + " |"
    

class RowPartition(object):
    '''
    For describing the layout of a (set of) row(s) in a block-matrix
    as a list of ColPartitions
    '''
#     def __new__(cls, nRows, info=None):
#         nRows = sympify(nRows)
#         info = {} if info is None else info
# #         dom_info = info.get('polytope', Set("{[]}"))
#         idcs, dom_info = info.get('indices', []), info.get('polytope', Set("{[]}"))
#         rows_bounded = expr_is_bounded_over_domain(idcs, dom_info, nRows)
#         if rows_bounded:
#             rows_min = get_expr_bound_over_domain(idcs, dom_info, nRows, 'min')
#             if rows_min > 0:
#                 return super(RowPartition, cls).__new__(cls, nRows, info)
#         elif not rows_bounded:
#             print "Warning: ColPartition has unbounded nCols: %s over domain %s" % (str(nRows), str(dom_info))
    
    def __init__(self, nRows=None, col_list=None, info=None):
        nRows = sympify(0) if nRows is None else sympify(nRows, locals=sym_locals)
        col_list = [] if col_list is None else [ c for c in col_list if not c.is_empty() ]
        info = {} if info is None else info
        if __VERBOSE__:
            idcs, dom_info = info.get('indices', []), info.get('polytope', Set("{[]}"))
            rows_bounded = expr_is_bounded_over_domain(idcs, dom_info, nRows)
            if rows_bounded:
                rows_min = get_expr_bound_over_domain(idcs, dom_info, nRows, 'min')
                rows_max = get_expr_bound_over_domain(idcs, dom_info, nRows, 'max')
                if rows_min == 0:
                    if rows_max == 0:
                        print "Warning: RowPartition has zero rows."
                    else:
                        print "Warning: RowPartition also has zero rows."
            elif not rows_bounded:
                print "Warning: RowPartition has unbounded nRows: %s over domain %s" % (str(nRows), str(dom_info))
        self.nRows = nRows
        self.cols = col_list
        self.checkPartition()
        self.info = {}
        self.set_info(info.keys(), info.values())

    def is_bounded(self):
        idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
        rows_bounded = expr_is_bounded_over_domain(idcs, dom_info, self.nRows)
        return rows_bounded

    def is_also_empty(self):
        if self.is_empty() or filter(lambda col: col.is_also_empty(), self.cols):
            return True
        idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
        rows_bounded = expr_is_bounded_over_domain(idcs, dom_info, self.nRows)
        if rows_bounded:
            rows_min = get_expr_bound_over_domain(idcs, dom_info, self.nRows, 'min')
            return rows_min == 0
        return False

    def is_empty(self):
        if not self.cols or filter(lambda col: col.is_empty(), self.cols):
            return True
        idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
        rows_bounded = expr_is_bounded_over_domain(idcs, dom_info, self.nRows)
        if rows_bounded:
            rows_min = get_expr_bound_over_domain(idcs, dom_info, self.nRows, 'min')
            rows_max = get_expr_bound_over_domain(idcs, dom_info, self.nRows, 'max')
            return rows_min == 0 and rows_max == 0
        return False
        
    def subs(self, idsDict):
        self.nRows = self.nRows.subs(idsDict)
        for col in self.cols:
            col.subs(idsDict)

    def set_info(self, label_list, info_list):
        for l,i in zip(label_list, info_list):
#             if isinstance(i, Set) and i.is_singleton():
#                 self.info[l] = i.copy()
#             else:
            self.info[l] = deepcopy(i)
        for col in self.cols:
            col.set_info(label_list, info_list)
    
    def isHomogeneous(self):
        return (len(self.cols) == 1)

    def getNumColPartitions(self):
        return sympify(len(self.cols), locals=sym_locals)
    
    def checkPartition(self):
        for i in range(len(self.cols)-1):
            if(self.cols[i].getRowSize() != self.cols[i+1].getRowSize()):
                exit("CheckPartition: cannot have blocks with different #Rows within the same partition.")
                
    def addCols(self, listCols):
        self.cols += [ c for c in listCols if not c.is_empty() ]
        self.checkPartition()
    
    def getRowSize(self):
        '''
        Number of rows in the blocks within the partition
        '''
        return self.cols[0].getRowSize()

    def getFlatRowSize(self):
        '''
        Number of rows of the completely expanded blocks within the partition
        '''
        return self.cols[0].getFlatRowSize()

    def getColSize(self, idx): #idx index of a column
#         n = 0
#         for partition in self.cols:
#             n += partition.nCols
#             if(idx < n):
#                 return partition.getColSize()
#         return 0
        if(idx < len(self.cols)):
            return self.cols[idx].getColSize()
        return 0
    
    def getScalar(self):
        return self.cols[0].getScalar()

#     def getPartitionIndexOfBlock(self, idx): #idx index of a column
#         n = 0
#         idxn = 0
#         for partition in self.cols:
#             n += partition.nCols
#             if(idx < n):
#                 return idxn
#             idxn += 1
#         return None
    
    def getBlock(self, idx): #idx index of a column
        n = 0
        idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
        for partition in self.cols:
#             n += partition.nCols.subs(self.info.get('min',{}))
            n += get_expr_bound_over_domain(idcs, dom_info, partition.nCols, 'min')
            if(idx < n):
                return partition.block
        return None

#     def getLocatedBlock(self, idx): #idx index of a column
#         n = 0
#         colflatcol = [0,0]
#         for partition in self.cols:
#             n += partition.nCols
#             if(idx < n):
#                 colflatcol[1] += (idx-colflatcol[0])*partition.getFlatColSize()
#                 return (partition.block, colflatcol[1])
#             else:
#                 colflatcol[0] += partition.nCols
#                 colflatcol[1] += colflatcol[0]*partition.getFlatColSize()
#         return (None, None)

    def getColsOfPartition(self, idx): #idx index of a partition
        if(idx < len(self.cols)):
            return self.cols[idx].nCols
        return sympify(0)

    def getBlockOfPartition(self, idx): #idx index of a partition
        if(idx < len(self.cols)):
            return self.cols[idx].block
        return None
    
    def transposedBlocksInCols(self):
        listTransposedBlocks = []
        for colPart in self.cols:
            listTransposedBlocks += [colPart.transposedBlock()]
        return listTransposedBlocks
         
    def duplicate(self, prefix=""):
        dup = RowPartition(self.nRows, info=self.info)
        listColParts = []
        for colPart in self.cols:
            listColParts += [colPart.duplicate(prefix)]
        dup.addCols(listColParts)

        return dup
    
    def __hash__(self):
        tcols = tuple(self.cols)
        key = (self.nRows, hash(tcols))
        
        return hash(key)
        
    def __eq__(self, other):
        if not isinstance(other, RowPartition):
            return False
        
        idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
        rows_bounded = expr_is_bounded_over_domain(idcs, dom_info, self.nRows)
        o_idcs, o_dom_info = other.info.get('indices', []), other.info.get('polytope', Set("{[]}"))
        o_rows_bounded = expr_is_bounded_over_domain(o_idcs, o_dom_info, other.nRows)

        if rows_bounded and o_rows_bounded:
            rows_min = get_expr_bound_over_domain(idcs, dom_info, self.nRows, 'min')
            rows_max = get_expr_bound_over_domain(idcs, dom_info, self.nRows, 'max')
            o_rows_min = get_expr_bound_over_domain(o_idcs, o_dom_info, other.nRows, 'min')
            o_rows_max = get_expr_bound_over_domain(o_idcs, o_dom_info, other.nRows, 'max')
            if not ( rows_min == o_rows_min and rows_max == o_rows_max ):
                return False
        elif(self.nRows != other.nRows):
            return False
        for myColPart, oColPart in zip(self.cols, other.cols):
            if(myColPart != oColPart):
                return False
        return True
    
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __repr__(self):
        return "{ " + str(self.nRows) + ", " + str(self.cols) + " }"
    
class Descriptor(object):
    '''
    For describing the layout of a block-matrix
    as a list of RowPartitions
    '''
    def __init__(self, level, o=None):
        if o is None:
            self.o = sympify([0,0])
        else:
            self.setOrigin(o)
        self.level = level
        self.rows = []
        self.info = {}

    def is_bounded(self):
        size = self.getSize()
        idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
        size_bounded = all( map(lambda s: expr_is_bounded_over_domain(idcs, dom_info, s), size) )
        return size_bounded

    def is_also_empty(self):
        if self.is_empty() or filter(lambda row: row.is_also_empty(), self.rows):
            return True
        size = self.getSize()
        idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
        size_bounded = all( map(lambda s: expr_is_bounded_over_domain(idcs, dom_info, s), size) )
        if size_bounded:
            size_min = map(lambda s: get_expr_bound_over_domain(idcs, dom_info, s, 'min'), size)
            return size_min[0] == 0 or size_min[1] == 0
        return False

    def is_empty(self):
        if not self.rows or filter(lambda row: row.is_empty(), self.rows):
            return True
        size = self.getSize()
        idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
        size_bounded = all( map(lambda s: expr_is_bounded_over_domain(idcs, dom_info, s), size) )
        if size_bounded:
            size_min = map(lambda s: get_expr_bound_over_domain(idcs, dom_info, s, 'min'), size)
            size_max = map(lambda s: get_expr_bound_over_domain(idcs, dom_info, s, 'max'), size)
            return (size_min[0] == 0 or size_min[1] == 0) and (size_max[0] == 0 or size_max[1] == 0)
        return False
        
    def setOrigin(self, o):
        self.o = sympify(o, locals=sym_locals) 

    def subs(self, idsDict):
        self.o = [ self.o[0].subs(idsDict), self.o[1].subs(idsDict) ]
        for row in self.rows:
            row.subs(idsDict)

    def set_info(self, label_list, info_list):
        for l,i in zip(label_list, info_list):
#             if isinstance(i, Set) and i.is_singleton():
#                 self.info[l] = i.copy()
#             else:
            self.info[l] = deepcopy(i)
        for row in self.rows:
            row.set_info(label_list, info_list)

    def sanityCheck(self):
        for i in range(len(self.rows)-1):
            if(self.rows[i].getNumColPartitions() != self.rows[i+1].getNumColPartitions()):
                exit("SanityCheck: cannot have RowPartitions with different number of ColParititons.")
        nColPart = 0 if not self.rows else self.rows[0].getNumColPartitions()
        for i in range(nColPart):
            for j in range(len(self.rows)-1):
                if(self.rows[j].getColSize(i) != self.rows[j+1].getColSize(i)):
                    exit("SanityCheck: cannot have Blocks in ColPartitions at index i in different RowPartitions with different #Cols.")
        for i in range(nColPart):
            for j in range(len(self.rows)-1):
                if(self.rows[j].getColsOfPartition(i) != self.rows[j+1].getColsOfPartition(i)):
                    exit("SanityCheck: cannot have ColPartitions at index i in different RowPartitions with different #Cols.")
    
    def addRows(self, listRows):
        self.rows += [ r for r in listRows if not r.is_empty() ]
        self.sanityCheck()

    def getNumColPartitions(self):
        return sympify(0) if not self.rows else self.rows[0].getNumColPartitions()
    
    def getNumRowPartitions(self):
        return len(self.rows)
    
    def getRowsOfPartition(self, idx):
        if(idx < len(self.rows)):
            return self.rows[idx].nRows
        return sympify(0)

    def getColsOfPartition(self, idx):
        if self.rows:
            return self.rows[0].getColsOfPartition(idx)
        return sympify(0)

    def getBlockOfPartition(self, i, j):
        if(i < len(self.rows)):
            return self.rows[i].getBlockOfPartition(j)
        return None
    
#     def getPartitionIndexOfBlock(self, i, j):
#         m = 0
#         idxm = 0
#         for partition in self.rows:
#             m += partition.nRows
#             if(i < m):
#                 idxn = partition.getPartitionIndexOfBlock(j)
#                 return (idxm,idxn)
#             idxm += 1
#         return None
                
#     def getRowSize(self, idx): # Provide the number of rows in a partition at position idx
#         m = 0
#         for partition in self.rows:
#             m += partition.nRows
#             if(idx < m):
#                 return partition.getRowSize()
#         return 0

    def getColSize(self, idx): # Provide the number of cols in a partition at position idx
        return sympify(0) if not self.rows else self.rows[0].getColSize(idx)
    
    def getSize(self):
        m = sympify(0)
        for partition in self.rows:
            m += partition.nRows
        n = sympify(0)
        if self.rows:
            part0 = self.rows[0]
            for colPart in part0.cols:
                n += colPart.nCols
        return (m, n)
    
    def getNumPartitions(self): #Size in terms of available partitions
        m = sympify(len(self.rows))
        n = sympify(0) if not self.rows else self.rows[0].getNumColPartitions()
        
        return (m,n)
        
    def getScalar(self):
        return None if not self.rows else self.rows[0].getScalar()
        
    def getBlock(self, i, j):
        m = 0
        idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
        for partition in self.rows:
#             m += partition.nRows.subs(self.info.get('min', {}))
            m += get_expr_bound_over_domain(idcs, dom_info, partition.nRows, 'min')
            if(i < m):
                return partition.getBlock(j)
        return None

#     def getSubMatrix(self, i, j):
#         isExpr = (isinstance(i, sympy.Expr) and isinstance(j, sympy.Expr))
#         if(isExpr):
#             return Matrix.fromBlock(self.getBlock(0, 0), [self.o[0] + i, self.o[1] + j])
#         else:
#             if isinstance(i, sympy.Expr):
#                 (blk, flatcol) = self.rows[0].getLocatedBlock(j)
#                 if blk is None:
#                     return None
#                 o = [self.o[0]+i, self.o[1]+flatcol]
#                 return Matrix.fromBlock(blk, o)
#             else:
#                 m = 0
#                 rowflatrow = [0, 0]
#                 for partition in self.rows:
#                     m += partition.nRows
#                     if(i < m):
#                         rowflatrow[1] += (i-rowflatrow[0])*partition.getFlatRowSize()
#                         if isinstance(j, sympy.Expr):
#                             (blk, flatcol) = partition.getLocatedBlock(0)
#                             flatcol = j
#                         else:
#                             (blk, flatcol) = partition.getLocatedBlock(j)
#                         if blk is None:
#                             return None
#                         o = [self.o[0]+rowflatrow[1], self.o[1]+flatcol]
#                         return Matrix.fromBlock(blk, o)
#                     else:
#                         rowflatrow[0] += partition.nRows
#                         rowflatrow[1] += rowflatrow[0]*partition.getFlatRowSize()
#         return None

#     def getListHomSubMatrices(self, name, attr):
#         matList = []
#         ox = self.o[0]
#         for row in self.rows:
#             oy = self.o[1]
#             for colpart in row.cols:
#                 dup = colpart.duplicate()
#                 newRow = RowPartition(row.nRows)
#                 newRow.addCols([dup])
#                 newDesc = Descriptor(self.level)
#                 newDesc.addRows([newRow])
#                 o = [ox,oy]
#                 matList += [ Matrix(name, newDesc, newDesc.getSize(), o, attr)]
#                 oy += dup.getFlatColSize()*dup.nCols
#             ox += row.getFlatRowSize()*row.nRows
#         return matList

    def isHomogeneous(self):
        if (len(self.rows) > 1):
            return False
        return self.rows[0].isHomogeneous()
    
    def duplicate(self, prefix=""):
        dup = Descriptor(self.level)
        dup.set_info(self.info.keys(), self.info.values())
        listRowParts = []
        for rowPart in self.rows:
            listRowParts += [rowPart.duplicate(prefix)]
        dup.addRows(listRowParts)

        return dup

    def transpose(self):
        tr = Descriptor(self.level)
        tr.set_info(self.info.keys(), self.info.values())
        listRowParts = []
        col_list = [] if not self.rows else self.rows[0].cols
        for colPart in col_list:
            listRowParts += [RowPartition(colPart.nCols, info=self.info)]

        listNewColumns = [] # List of new columns consisting of their transposed blocks 
        for rowPart in self.rows:
            listNewColumns += [rowPart.transposedBlocksInCols()]
        
        rowIdx = 0
        for blocksPerRow in zip(*listNewColumns):
            newColPartList = []
            for rowComp in zip(self.rows, blocksPerRow):
                newColPartList += [ ColPartition(rowComp[0].nRows, rowComp[1], self.info) ]
            listRowParts[rowIdx].addCols(newColPartList)
            rowIdx += 1
        
        tr.addRows(listRowParts)
        return tr
    
    def __hash__(self):
        trows = tuple(self.rows)
        return hash(trows)
        
    def __eq__(self, other):
        if not isinstance(other, Descriptor):
            return False
        if(self.getNumRowPartitions() != other.getNumRowPartitions()):
            return False
        for myRowPart,oRowPart in zip(self.rows, other.rows):
            if(myRowPart != oRowPart):
                return False
        return True
    
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __str__(self):
        return str(self.rows)
    
################################################

class Empty(Descriptor):
    
    def __init__(self):
        super(Empty, self).__init__(0)
        self.size = sympify((0,0))
    
    def subs(self, idsDict):
        pass
        
    def duplicate(self, prefix):
        e = Empty()
        e.set_info(self.info.keys(), self.info.values())
        return e 

    def __repr__(self):
        return self.__str__()
    
    def __hash__(self):
        return hash(None) # Used to have identical hash across different executions
    
    def __str__(self):
        return "[-]"

################################################

class Block(Expression):
    '''
    Fundamental datatype class for representing Block-Matrices.
    '''
    def __new__(cls, name, descriptor, size):
        if descriptor is not None:
            return super(Block, cls).__new__(cls)
                
    def __init__(self, name, descriptor, size):
        super(Block, self).__init__()

        self.name = getNextName() if name == '' else name 
        size = sympify(size, locals=sym_locals)
        if __VERBOSE__:
            idcs, dom_info = descriptor.info.get('indices', []), descriptor.info.get('polytope', Set("{[]}"))
            size_bounded = all( map(lambda s: expr_is_bounded_over_domain(idcs, dom_info, s), size) )
            if size_bounded:
                size_min = map(lambda s: get_expr_bound_over_domain(idcs, dom_info, s, 'min'), size)
                size_max = map(lambda s: get_expr_bound_over_domain(idcs, dom_info, s, 'max'), size)
                if (size_min[0] == 0 or size_min[1] == 0):
                    if (size_max[0] == 0 or size_max[1] == 0):
                        print "Warning: Block %s has zero size: %s over domain %s." % ( self.name, str(size), str(dom_info) )
                    else:
                        print "Warning: Block %s also has zero size: %s over domain %s." % ( self.name, str(size), str(dom_info) )
            else:
                print "Warning: Block %s has unbounded size: %s over domain %s" % ( self.name, str(size), str(dom_info) )

        self.set_info_no_desc(descriptor.info.keys(), descriptor.info.values())
        self.level = descriptor.level + 1
        self.size = size

        if(isinstance(descriptor, Block)):
            self.createBasicDescriptor(descriptor)
        else:
            #Either a descriptor or Empty
            self.descriptor = descriptor
        self.homogeneous = None
        if __VERBOSE__:
            if self.is_empty():
                print "Warning: Block %s is empty: %s over domain %s" % ( self.name, str(self.descriptor), str(dom_info) )
            elif self.is_also_empty():
                print "Warning: Block %s is also empty: %s over domain %s" % ( self.name, str(self.descriptor), str(dom_info) )

    def is_bounded(self):
        idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
        size_bounded = all( map(lambda s: expr_is_bounded_over_domain(idcs, dom_info, s), self.size) )
        return size_bounded

    def is_also_empty(self):
        if self.is_empty():
            return True
        idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
        size_bounded = all( map(lambda s: expr_is_bounded_over_domain(idcs, dom_info, s), self.size) )
        if size_bounded:
            size_min = map(lambda s: get_expr_bound_over_domain(idcs, dom_info, s, 'min'), self.size)
            return size_min[0] == 0 or size_min[1] == 0
        return False

    def is_empty(self):
        idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
        size_bounded = all( map(lambda s: expr_is_bounded_over_domain(idcs, dom_info, s), self.size) )
        if size_bounded:
            size_min = map(lambda s: get_expr_bound_over_domain(idcs, dom_info, s, 'min'), self.size)
            size_max = map(lambda s: get_expr_bound_over_domain(idcs, dom_info, s, 'max'), self.size)
            if self.descriptor.is_empty() and filter(lambda s: s != 1, size_min+size_max):
                return True
            return (size_min[0] == 0 or size_min[1] == 0) and (size_max[0] == 0 or size_max[1] == 0)
        return False

    def get_pot_zero_dims(self):
        idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
        size_bounded = all( map(lambda s: expr_is_bounded_over_domain(idcs, dom_info, s), self.size) )
        res = []
        if size_bounded:
            size_min = map(lambda s: get_expr_bound_over_domain(idcs, dom_info, s, 'min'), self.size)
            for s,smin in zip(self.size,size_min):
                if smin == 0:
                    res.append(s)
        return res
    
    def subs(self, idsDict):
        self.size = self.size.subs(idsDict)
        self.descriptor.subs(idsDict)
    
    def set_info(self, label_list, info_list):
        super(Block, self).set_info(label_list, info_list)
        self.descriptor.set_info(label_list, info_list)

    def set_info_no_desc(self, label_list, info_list):
        super(Block, self).set_info(label_list, info_list)
        
    def getPartitionSize(self,i,j):
        m = self.descriptor.getRowsOfPartition(i)
        n = sympify(0) if not self.descriptor.rows else self.descriptor.rows[i].getColsOfPartition(j)
        return [m,n]

    def getNumPartitions(self):
        return self.descriptor.getNumPartitions()

#     def getFirstBlockOfPartition(self, i, j):
#         return self.getBlock(i*(self.size[0]-1),j*(self.size[1]-1))

    def getFirstBlockOfPartition(self, i, j):
        return self.descriptor.getBlockOfPartition(i, j)
        
    def getPartitionCols(self):
        return sympify(0) if not self.descriptor.rows else len(self.descriptor.rows[0].cols)

    def getFlatPartitionSize(self,i,j):
        m = self.descriptor.getRowsOfPartition(i)
        n = sympify(0) if not self.descriptor.rows else self.descriptor.rows[i].getColsOfPartition(j)
        b = self.descriptor.getBlockOfPartition(i, j)
        bsize = (sympify(0),sympify(0)) if b is None else b.getFlatSize()
        return [m*bsize[0],n*bsize[1]]
    
    def getSignature(self):
        fsize = self.getFlatSize()
        return self.name + str(fsize[0]) + "s" + str(fsize[1])
    
    def createBasicDescriptor(self, block):
        info = dict(block.info)
        info.update(self.info) 
        CP = ColPartition(self.size[1], block, info)
        RP = RowPartition(self.size[0], info=info)
        RP.addCols([CP])
        self.descriptor = Descriptor(block.level)
        self.descriptor.set_info(self.info.keys(), self.info.values())
        self.descriptor.addRows([RP])
    
    def getFlatSize(self):
        
        if(self.level == 1):
            return sympify((1,1))
        
        m = n = sympify(0)
        
        for rowPart in self.descriptor.rows:
            m += rowPart.nRows*rowPart.getFlatRowSize()
        
        col_list = [] if not self.descriptor.rows else self.descriptor.rows[0].cols 
        for colPart in col_list:
            n += colPart.nCols*colPart.getFlatColSize()
        
        return (m, n)
    
    def isHomogeneous(self):
        if self.homogeneous is None:
            self.homogeneous = self.descriptor.isHomogeneous() 
        return self.homogeneous
    
    def getBlock(self, i, j):
        return self.descriptor.getBlock(i, j)
    
    def getScalar(self):
        if(self.level == 1):
            return self
        return self.descriptor.getScalar()
    
#     def getIndices(self):
#         if self.level == 1:
#             return [ [ Index('i', 0, 1, 1), Index('j', 0, 1, 1) ] ]
#         
#         blk0 = self.getBlock(0, 0)
#         myList = [ [Index('i', 0, self.getFlatSize()[0], blk0.getFlatSize()[0]), Index('j', 0, self.getFlatSize()[1], blk0.getFlatSize()[1])] ]
#         return myList + blk0.getIndices()
    
    def duplicate(self, prefix=""):
        return Block(prefix + self.name, self.descriptor.duplicate(prefix), copy(self.size))
    
    def transpose(self):
        if(self.level == 1):
            return self
        return Block("tr" + self.name, self.descriptor.transpose(), (self.size[1], self.size[0]))                
    
    def __hash__(self):
        
        return hash(self.descriptor) 
    
    def __eq__(self, other):
        if not isinstance(other, Block):
            return False
        if(self.level != other.level):
            return False
        if(self.level == 1):
            return self.name == other.name
        return self.descriptor == other.descriptor
    
    def __ne__(self, other):
        return not self.__eq__(other)
     
    def __repr__(self):
        return "Block[" + self.name + ", " + str(self.size) + ", " + str(self.descriptor) + "]"
            
    def __str__(self):
        if (self.level == 1):
            return ""
        res = "Layout of block " + self.name + " :\n"
        res += "Size:\t" + str(self.size) + "\n"
        res += "Level:\t" + str(self.level) + "\n"
        for rowPart in self.descriptor.rows:
            res += str(rowPart.nRows) + " x |\t"
            for colPart in rowPart.cols:
                res += "(" + str(colPart.nCols) + ", " + colPart.block.name + ")\t"
            res += "|\n"
        res += "\n"
        for rowPart in self.descriptor.rows:
            for colPart in rowPart.cols:
                res += str(colPart.block)
        return res

##############################################

# empty  = Empty()
# scalar = Block("scalar", empty, (1,1))
def scalar_block():
    return Block("real", Empty(), (1,1))

##############################################
#--------------Metaclasses-------------------#
##############################################

class MetaScalar(type):
    def __add__(self, other):
        return Scalar
 
    def __sub__(self, other):
        return Scalar
     
    def __mul__(self, other):
        return other
 
    def T(self):
        return Scalar

    def __repr__(self):
            return str(self)
            
    def __str__(self):
        return self.__name__
 
class MetaMatrix(type):
    def __add__(self, other):
        return Matrix

    def __sub__(self, other):
        return (self + other)
    
    def __mul__(self, other):
        return Matrix

    def rdiv(self, other):
        return Matrix

    def T(self):
        return Matrix
    
    def __repr__(self):
            return str(self)
            
    def __str__(self):
        return self.__name__

class MetaSquaredMatrix(MetaMatrix):
    def __add__(self, other):
        return SquaredMatrix

    def __mul__(self, other):
        if issubclass(other, SquaredMatrix):
            return SquaredMatrix
        return Matrix


    def rdiv(self, other):
        if other is LowerTriangular or other is UpperTriangular:
            return SquaredMatrix

    def T(self):
        return SquaredMatrix

class MetaSymmetric(MetaSquaredMatrix):
    def __add__(self, other):
        if other is Symmetric or other is IdentityMatrix:
            return Symmetric
        return SquaredMatrix
    
    def T(self):
        return Symmetric

class MetaLowerTriangular(MetaSquaredMatrix):
    def __add__(self, other):
        if other is LowerTriangular or other is IdentityMatrix:
            return LowerTriangular
        return SquaredMatrix

    def __mul__(self, other):
        if other is LowerTriangular:
            return LowerTriangular
        if issubclass(other, SquaredMatrix):
            return SquaredMatrix
        return Matrix

#     def ldiv(self, other):
#         if other is LowerTriangular:
#             return LowerTriangular
#         if issubclass(other, SquaredMatrix):
#             return SquaredMatrix
#         return Matrix
    def ldiv(self, other):
        return self * other

    def rdiv(self, other):
        if other is UpperTriangular:
            return SquaredMatrix
        if other is LowerTriangular:
            return LowerTriangular

    def T(self):
        return UpperTriangular

class MetaLowerUnitTriangular(MetaLowerTriangular):
    def T(self):
        return UpperUnitTriangular

class MetaUpperTriangular(MetaSquaredMatrix):
    def __add__(self, other):
        if other is UpperTriangular or other is IdentityMatrix:
            return UpperTriangular
        return SquaredMatrix
    
    def __mul__(self, other):
        if other is UpperTriangular:
            return UpperTriangular
        if issubclass(other, SquaredMatrix):
            return SquaredMatrix
        return Matrix

    def ldiv(self, other):
        return self * other

    def rdiv(self, other):
        if other is LowerTriangular:
            return SquaredMatrix
        if other is UpperTriangular:
            return UpperTriangular

    def T(self):
        return LowerTriangular

class MetaUpperUnitTriangular(MetaUpperTriangular):
    def T(self):
        return LowerUnitTriangular

# class MetaZeroMatrix(MetaMatrix):
#     def __add__(self, other):
#         return other
#     
#     def __mul__(self, other):
#         return ZeroMatrix
# 
#     def T(self):
#         return ZeroMatrix

class Singleton(type):
    _instances = {}

class MetaIdentityMatrix(MetaSquaredMatrix):

    def __add__(self, other):
        return other
    
    def __mul__(self, other):
        return self

    def T(self):
        return self

def _meta_constant_with_value(value):
    class MetaConstant(MetaMatrix):
        __metaclass__ = Singleton
        
        def __new__(cls, name, bases, attrs):
            if value in cls._instances:
                return cls._instances[value]
            ConstType = super(MetaConstant, cls).__new__(cls, name, bases, attrs)
            ConstType._const_value = value
            cls._instances[value] = ConstType
            return ConstType

        def T(self):
            return self

        def __str__(self):
            return super(MetaConstant, self).__str__() + "<%d>" % self._const_value
        
    return MetaConstant

class MetaZeroMatrix(MetaMatrix):
    __metaclass__ = Singleton
    
    def __new__(cls, name, bases, attrs):
        ConstType = super(MetaZeroMatrix, cls).__new__(cls, name, bases, attrs)
        ConstType._const_value = 0
        cls._instances[0] = ConstType
        return ConstType

    def __add__(self, other):
        return other
    
    def __mul__(self, other):
        return self

    def T(self):
        return self

##############################################
#--------------Accesses   -------------------#
##############################################


class MatAccess(object):
    def __init__(self, mat):
        super(MatAccess, self).__init__()
        self.mat = mat

    def buildNDMap(self, domIds, rangeIds, constr=None, dimPos=None, trail=None):
        mapping = ""
        trail = [] if trail is None else trail
        if dimPos is not None:
            k=0
            for p in dimPos:
                idx = 'k'+str(k)
                domIds.insert(p, idx) 
                rangeIds.insert(p, idx)
                k+=1
        mapping += "["+(",".join(domIds+trail))+"]->["+(",".join(rangeIds+trail))+"]" 
        constraints = "" if constr is None else (": " + constr)
        m = Map("{"+mapping+constraints+"}")
        return m

    def getFlatPolyAccessFromStructure(self):
        return self.getFlatPolyAccessFromStructureND()

    def __str__(self):
        return self.__class__.__name__
    
    def __repr__(self):
        return str(self)
    
class GenMatAccess(MatAccess):
    def __init__(self, mat):
        super(GenMatAccess, self).__init__(mat)

    def getPolyAccess(self, indices, fL, fR, imfList, orig, partFlatSize, blBlkFlatSize):
        a = (self.mat.name, tuple([tuple(i) for i in imfList]), (fL, fR), None)
        lims = (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1]))
        s = Set(("{["+(",".join(indices))+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<%s}") % lims)
        accessDict = { a : s }
        return accessDict

    def getFlatPolyAccessFromStructureND(self, dimPos=None, trail=None):
        return self.buildNDMap(['i','j'], ['i','j'], dimPos=dimPos, trail=trail)
    
#    def getFlatPolyAccessFromStructure(self):
#        m = Map("{[i,j]->[i,j]}")
#        return m
    
# class LTMatAccess(MatAccess):
#     def __init__(self, mat):
#         super(LTMatAccess, self).__init__(mat)
# 
#     def getPolyAccess(self, indices, fL, fR, imfList, orig, partFlatSize, blBlkFlatSize):
#         a = (self.mat.name, tuple([tuple(i) for i in imfList]), (fL, fR), None)
#         s = Set(("{["+(",".join(indices))+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<="+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1])))
#         accessDict = { a : s }
#         return accessDict
# 
#     def getFlatPolyAccessFromStructureND(self, dimPos=None, trail=None):
#         return self.buildNDMap(['i','j'], ['i','j'], constr="j<=i", dimPos=dimPos, trail=trail)

#    def getFlatPolyAccessFromStructure(self):
#        m = Map("{[i,j]->[i,j]: j<=i }")
#        return m

# class UTMatAccess(MatAccess):
#     def __init__(self, mat):
#         super(UTMatAccess, self).__init__(mat)
# 
#     def getPolyAccess(self, indices, fL, fR, imfList, orig, partFlatSize, blBlkFlatSize):
#         a = (self.mat.name, tuple([tuple(i) for i in imfList]), (fL, fR), None)
#         s = Set(("{["+(",".join(indices))+"]: %s<="+str(fL.of(0))+"<%s and "+str(fL.of(0))+"<="+str(fR.of(0))+"<%s}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]+partFlatSize[1])))
#         accessDict = { a : s }
#         return accessDict
# 
#     def getFlatPolyAccessFromStructureND(self, dimPos=None, trail=None):
#         return self.buildNDMap(['i','j'], ['i','j'], constr="j>=i", dimPos=dimPos, trail=trail)

#    def getFlatPolyAccessFromStructure(self):
#        m = Map("{[i,j]->[i,j]: j>=i}")
#        return m

class LSMatAccess(MatAccess):
    def __init__(self, mat):
        super(LSMatAccess, self).__init__(mat)

    def getPolyAccess(self, indices, fL, fR, imfList, orig, partFlatSize, blBlkFlatSize):
        sindices = ",".join(indices)
#         if blBlkFlatSize[0]*blBlkFlatSize[1] == 1:
#             al = (self.mat.name, tuple([tuple(i) for i in imfList]), (fL, fR), None)
#             sl = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<="+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1])))
#             au = (self.mat.name, tuple([ tuple(i[::-1]) for i in imfList ]), (fR, fL), None)
#             su = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fL.of(0))+"<"+str(fR.of(0))+"<%s}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]+partFlatSize[1])))
#             accessDict = { al: sl, au: su }
#         elif blBlkFlatSize[0]==blBlkFlatSize[1]:
        if blBlkFlatSize[0]==blBlkFlatSize[1]:
#             ad = (self.mat.name, fL, fL, None)
            ad = (self.mat.name, tuple([ tuple([i[0]]*2) for i in imfList ]), (fL, fL), None)
            sd = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fR.of(0))+"="+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0])))
#             al = (self.mat.name, fL, fR, None)
            al = (self.mat.name, tuple([tuple(i) for i in imfList]), (fL, fR), None)
            sl = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<"+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1])))
#             au = (self.mat.name, fR, fL, T)
            au = (self.mat.name, tuple([ tuple(i[::-1]) for i in imfList ]), (fR, fL), T)
            su = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fL.of(0))+"<"+str(fR.of(0))+"<%s}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]+partFlatSize[1])))
            accessDict = { al: sl, ad: sd, au: su }
        else: #Vert or Horiz partitions
            if blBlkFlatSize[0]>blBlkFlatSize[1]:
                a = (self.mat.name, tuple([ tuple(i[::-1]) for i in imfList ]), (fR, fL), T)
            else:
                a = (self.mat.name, tuple([tuple(i) for i in imfList]), (fL, fR), None)
            lims = (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1]))
            s = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<%s}") % lims)
            accessDict = { a: s }
#         accessOp = None if blBlkFlatSize[0]*blBlkFlatSize[1] == 1 else 'trans'
#         al = (self.mat.name, str(fL), str(fR), None)
#         sl = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<="+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1])))
#         au = (self.mat.name, str(fR), str(fL), accessOp)
#         su = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fL.of(0))+"<"+str(fR.of(0))+"<%s}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]+partFlatSize[1])))
#         accessDict = { al: sl, au: su }
        return accessDict

    def getFlatPolyAccessFromStructureND(self, dimPos=None, trail=None):
        ml = self.buildNDMap(['i','j'], ['i','j'], constr="j<=i", dimPos=dimPos, trail=trail)
        mu = self.buildNDMap(['i','j'], ['j','i'], constr="j>i", dimPos=dimPos, trail=trail)
        return ml.union(mu)
    
#    def getFlatPolyAccessFromStructure(self):
#        ml = Map("{[i,j]->[i,j]: j<=i}")
#        mu = Map("{[i,j]->[j,i]: j>i}")
#        return ml.union(mu)

class USMatAccess(MatAccess):
    def __init__(self, mat):
        super(USMatAccess, self).__init__(mat)

    def getPolyAccess(self, indices, fL, fR, imfList, orig, partFlatSize, blBlkFlatSize):
        sindices = ",".join(indices)
#         if blBlkFlatSize[0]*blBlkFlatSize[1] == 1:
#             al = (self.mat.name, tuple([ tuple(i[::-1]) for i in imfList ]), (fR, fL), None)
#             sl = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<="+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1])))
#             au = (self.mat.name, tuple([tuple(i) for i in imfList]), (fL, fR), None)
#             su = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fL.of(0))+"<"+str(fR.of(0))+"<%s}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]+partFlatSize[1])))
#             accessDict = { al: sl, au: su }
#         elif blBlkFlatSize[0]==blBlkFlatSize[1]:
        if blBlkFlatSize[0]==blBlkFlatSize[1]:
#             ad = (self.mat.name, fL, fL, None)
            ad = (self.mat.name, tuple([ tuple([i[0]]*2) for i in imfList ]), (fL, fL), None)
            sd = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fR.of(0))+"="+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0])))
#             al = (self.mat.name, fR, fL, T)
            al = (self.mat.name, tuple([ tuple(i[::-1]) for i in imfList ]), (fR, fL), T)
            sl = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<"+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1])))
#             au = (self.mat.name, fL, fR, None)
            au = (self.mat.name, tuple([tuple(i) for i in imfList]), (fL, fR), None)
            su = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fL.of(0))+"<"+str(fR.of(0))+"<%s}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]+partFlatSize[1])))
            accessDict = { al: sl, ad: sd, au: su }
        else: #Vert or Horiz partitions
            if blBlkFlatSize[0]>blBlkFlatSize[1]:
                a = (self.mat.name, tuple([tuple(i) for i in imfList]), (fL, fR), None)
            else:
                a = (self.mat.name, tuple([ tuple(i[::-1]) for i in imfList ]), (fR, fL), T)
            lims = (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1]))
            s = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<%s}") % lims)
            accessDict = { a: s }
#         sindices = ",".join(indices)
#         accessOp = None if blBlkFlatSize[0]*blBlkFlatSize[1] == 1 else 'trans'
#         al = (self.mat.name, str(fR), str(fL), accessOp)
#         sl = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<"+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1])))
#         au = (self.mat.name, str(fL), str(fR), None)
#         su = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fL.of(0))+"<="+str(fR.of(0))+"<%s}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]+partFlatSize[1])))
#         accessDict = { al: sl, au: su }
        return accessDict

    def getFlatPolyAccessFromStructureND(self, dimPos=None, trail=None):
        ml = self.buildNDMap(['i','j'], ['j','i'], constr="j<i", dimPos=dimPos, trail=trail)
        mu = self.buildNDMap(['i','j'], ['i','j'], constr="j>=i", dimPos=dimPos, trail=trail)
        return ml.union(mu)

#    def getFlatPolyAccessFromStructure(self):
#        ml = Map("{[i,j]->[j,i]: j<i}")
#        mu = Map("{[i,j]->[i,j]: j>=i}")
#        return ml.union(mu)
    
##############################################
#--------------Quantities -------------------#
##############################################

class Quantity(Block):
    def __init__(self, name, descriptor, size=None, o=None, attr=None, fL=None, fR=None):
        super(Quantity, self).__init__(name, descriptor, size)

        self.attr = {'i' : True, 'o' : False, 't' : False }
        if attr is not None:
            self.attr = dict(self.attr.items() + attr.items())
        #Set index mapping function from the Left and from the Right to Identity func
        if fL is None:
            self.fL = fI(self.size[0])
        else:
            self.fL = fL
        if fR is None:
            self.fR = fI(self.size[1])
        else:
            self.fR = fR

        if(isinstance(descriptor, Block)):
            self.matCreateBasicDescriptor(descriptor)
        else:
            #Either a descriptor or Empty
            self.descriptor = descriptor

        if o is not None:
            self.descriptor.setOrigin(o)
        
        self.o = self.descriptor.o
        self.reqAss = True

        self.spaceIdxNames = [[],[]]
        self.idxPosAndLevInfo = {} 
        self.genStruct = None
        self._genAccess = None
        
    def genAccess(self):
        if self._genAccess is None: 
            return self.access.getFlatPolyAccessFromStructure()
        return self._genAccess

    def setGenAccess(self, genAccess):
        self._genAccess = genAccess

    @classmethod
    def fromBlock(cls, block, o=None, name=None):
        dup_blk = block.duplicate()
        if o is None:
            o = [0,0]
        if name is None:
            name=dup_blk.name
        return cls(name, descriptor=dup_blk.descriptor, size=dup_blk.size, o=o)

    def matCreateBasicDescriptor(self, block):
        CP = ColPartition(self.size[1], block, self.info)
        RP = RowPartition(self.size[0], info=self.info)
        RP.addCols([CP])
        self.descriptor = Descriptor(block.level)
        self.descriptor.set_info(self.info.keys(), self.info.values())
        self.descriptor.addRows([RP])
    
    def transpose(self):
        trDescriptor = self.descriptor.transpose()
        trSize = (self.size[1], self.size[0])
        return (self.__class__.T())(name="tr"+self.name, descriptor=trDescriptor, size=trSize, o=deepcopy(self.descriptor.o), attr=deepcopy(self.attr)) # Should fL and fR be imposed?
        
    def setOrigin(self, o):
        self.descriptor.setOrigin(o)

    def getOrigin(self):
        return deepcopy(self.descriptor.o)
    
    def getPartitionOrigin(self, i, j):
        psize = self.getFlatPartitionSize(0, 0)
        return (self.descriptor.o[0]+psize[0]*i, self.descriptor.o[1]+psize[1]*j)
        
        
    def duplicate(self, prefix="", o=None, fL=None, fR=None, changeHandle=False):
        if o is None:
            o = deepcopy(self.o)
        if fL is None:
            fL = deepcopy(self.fL)
        if fR is None:
            fR = deepcopy(self.fR)
#         res = Matrix(prefix + self.name, self.descriptor.duplicate(prefix), deepcopy(self.size), o, deepcopy(self.attr), fL, fR)
        res = (self.__class__)(prefix + self.name, self.descriptor.duplicate(prefix), deepcopy(self.size), o, deepcopy(self.attr), fL, fR, access=self.access.__class__)
        if not changeHandle:
            res.handle = self.handle
        res.spaceIdxNames = deepcopy(self.spaceIdxNames)
        res.idxPosAndLevInfo = deepcopy(self.idxPosAndLevInfo)
        res.genStruct = deepcopy(self.genStruct)
        return res

    def duplicateUpToBoundaries(self, prefix="", boundaries=None, changeHandle=True):
        res = self.duplicate(prefix)
        if changeHandle:
            res.handle = getNextCount()
    
    def isScalar(self):
        fsize = self.getFlatSize()
        return fsize[0] == 1 and fsize[1] == 1  

    def subs(self, idsDict, explored=None):
        if explored is not None and self.handle in explored:
            return
        super(Quantity, self).subs(idsDict)
        self.fL = self.fL.subs(idsDict)
        self.fR = self.fR.subs(idsDict)

    def multByG(self, fL, fR, idsDict, explored, opts):
        return G(fL, self, fR)

    def __getitem__(self, key):
        return [ self, key ]
    
    def sameLayout(self, other):
        if(self.level != other.level) or self.descriptor != other.descriptor:
            return False
        
        idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
        size_bounded = all( map(lambda s: expr_is_bounded_over_domain(idcs, dom_info, s), self.size) )

        o_idcs, o_dom_info = other.info.get('indices', []), other.info.get('polytope', Set("{[]}"))
        o_size_bounded = all( map(lambda s: expr_is_bounded_over_domain(o_idcs, o_dom_info, s), other.size) )

        if size_bounded and o_size_bounded:
            size_min = map(lambda s: get_expr_bound_over_domain(idcs, dom_info, s, 'min'), self.size)
            size_max = map(lambda s: get_expr_bound_over_domain(idcs, dom_info, s, 'max'), self.size)
            o_size_max = map(lambda s: get_expr_bound_over_domain(o_idcs, o_dom_info, s, 'max'), other.size)
            o_size_min = map(lambda s: get_expr_bound_over_domain(o_idcs, o_dom_info, s, 'min'), other.size)
            return (size_min[0] == o_size_min[0] or size_min[1] == o_size_min[1]) and (size_max[0] == o_size_max[0] or size_max[1] == o_size_max[1])

        return self.size == other.size

    def computeSpaceIdxNames(self, i, j, ipfix, jpfix, opts, depth=1, baselevel=2):
        
        def _place_idx(part_size, pos):
#             return opts.get('idx_for_sca_dims', False) or part_size[pos].subs(self.info.get('max', {})) > 1
            idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
            return opts.get('idx_for_sca_dims', False) or get_expr_bound_over_domain(idcs, dom_info, part_size[pos], 'max') > 1
        
        part_size = self.getPartitionSize(0, 0)
        self.spaceIdxNames[0] = [i*depth+ipfix if _place_idx(part_size, 0) else None]
        self.spaceIdxNames[1] = [j*depth+jpfix if _place_idx(part_size, 1) else None]
#         self.spaceIdxNames[0] = [i*depth+ipfix]
#         self.spaceIdxNames[1] = [j*depth+jpfix]
        b = self
        while baselevel < b.level:
            b = b.getBlock(0,0)
            part_size = b.getPartitionSize(0, 0)
            depth += 1
            self.spaceIdxNames[0].append(i*depth+ipfix if _place_idx(part_size, 0) else None)
            self.spaceIdxNames[1].append(j*depth+jpfix if _place_idx(part_size, 1) else None)
#             self.spaceIdxNames[0].append(i*depth+ipfix)
#             self.spaceIdxNames[1].append(j*depth+jpfix)

    def cleanSpaceIdxNames(self):
        self.spaceIdxNames = [[],[]]

    def computeIdxPosAndLevInfo(self):
        maxlev = self.level
        idxInfo = {}
        for l in range(len(self.spaceIdxNames[0])): 
            wi,wj=self.spaceIdxNames[0][l],self.spaceIdxNames[1][l]
            if wi is not None:
                idxInfo[wi] = (maxlev, maxlev-l, 0)
            if wj is not None:
                idxInfo[wj] = (maxlev, maxlev-l, 1)
        self.idxPosAndLevInfo = idxInfo

    def getSpaceIdxSet(self):
        full_list = self.spaceIdxNames[0]+self.spaceIdxNames[1]
        return set([ i for i in full_list if i is not None ])

    def getFlatBoundingSet(self, ids):
        sIds = ",".join(ids)
        lims = (str(self.o[0]), str(self.o[0]+self.getFlatSize()[0]), str(self.o[1]), str(self.o[1]+self.getFlatSize()[1]))
        return Set(("{["+sIds+"]: %s<= "+ids[0]+" <%s and %s<= "+ids[1]+" <%s}")%lims)
    
#    def getFlatAccessSetND(self, newDimPos=None):
#        newDimPos = newDimPos if newDimPos is not None else []
#        mAcc = self.access.getFlatPolyAccessFromStructure()
#        accSet2D = mAcc.intersect_domain(self.getFlatBoundingSet(['i','j'])).range().coalesce()
#        accSetND = accSet2D
#        for p in newDimPos:
#            accSetND = accSetND.insert_dims(dim_type.set, p, 1)
#        return accSetND

    def getFlatAccessMapND(self, dimPos=None, trail=None):
        return self.access.getFlatPolyAccessFromStructureND(dimPos, trail)
        
    def getPolyInfo(self, indices, baselevel=2, extrainfo=None, directions=None):
        directions = ('f','f') if directions is None else directions
        extrainfo = [] if extrainfo is None else extrainfo
        polyinfo = []
        psize = self.getNumPartitions()
        for pr in range(psize[0]):
            piRow = []
            for pc in range(psize[1]):
                info = {}
                #Tiling info
                tileinfo = []
                partFlatSize = self.getFlatPartitionSize(pr,pc)
                partOrigin = self.getPartitionOrigin(pr, pc)
                fBoP = b = self.getFirstBlockOfPartition(pr,pc)
                flatSize = self.getFlatSize()
                bFlatSize = b.getFlatSize()
                ids = (self.spaceIdxNames[0][0],self.spaceIdxNames[1][0])
#                 wi,wj = (self.spaceIdxNames[0][0],self.spaceIdxNames[1][0]) if self.spaceIdxNames[0] else ('0','0')
#                 bases = [ sympify(wi),sympify(wj) ]
#                 for i in range(2):
#                     if directions[i]=='b':
#                         bases[i] = sympify('0') if sympify(wi) == sympify('0') else partOrigin[i]+partFlatSize[i] - bases[i] 
                cst_list = []
                imfs = []
                for pos in range(2):
                    base = partOrigin[pos] if ids[pos] is None else sympify(ids[pos], locals=sym_locals) 
                    if directions[pos]=='b':
                        base = partOrigin[pos]+partFlatSize[pos] - base 
                    if ids[pos]:
                        size = (str(partOrigin[pos]), str(partOrigin[pos]+partFlatSize[pos]), str(bFlatSize[pos]), str(partOrigin[pos]) )
                        cst_list.append( ("(exists a: %s<="+str(base)+"<%s and "+str(base)+"=%s*a+%s)") % size )
                    imfs.append(fHbs(bFlatSize[pos],flatSize[pos],base,1))                
                cstAtLev = " and ".join(cst_list)
#                 sizes = (str(partOrigin[0]), str(partOrigin[0]+partFlatSize[0]), str(partOrigin[1]), str(partOrigin[1]+partFlatSize[1]), str(bFlatSize[0]), str(partOrigin[0]), str(bFlatSize[1]), str(partOrigin[1]) )
#                 cstAtLev = ("(exists a,b: %s<="+str(bases[0])+"<%s and %s<="+str(bases[1])+"<%s and "+str(bases[0])+"=%s*a+%s and "+str(bases[1])+"=%s*b+%s)") % sizes 
#                 l,r = fHbs(bFlatSize[0],flatSize[0],bases[0],1), fHbs(bFlatSize[1],flatSize[1],bases[1],1)
                if cstAtLev:
                    tileinfo.append(cstAtLev)
                lev=1
                l,r = imfs
                imfList = [ imfs ]
#                 while b.level > baselevel-1 and (bFlatSize[0]*bFlatSize[1]).subs(self.info.get('min', {})) > 1:
                idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
                while b.level > baselevel-1 and get_expr_bound_over_domain(idcs, dom_info, bFlatSize[0]*bFlatSize[1], 'max') > 1:
                    ids = (self.spaceIdxNames[0][lev],self.spaceIdxNames[1][lev])
                    b = b.getBlock(0,0)
                    flatSize = bFlatSize 
                    if b.level > 1:
                        bFlatSize = b.getFlatSize()
                    else:
                        bFlatSize = [1,1]

                    cst_list = []
                    imfs = []
                    for pos in range(2):
                        base = sympify('0') if ids[pos] is None else sympify(ids[pos], locals=sym_locals) 
                        if directions[pos]=='b':
                            base = flatSize[pos] - base 
                        if ids[pos]:
                            size = (str(flatSize[pos]), str(bFlatSize[pos]) )
                            cst_list.append( ("(exists a: 0<="+str(base)+"<%s and "+str(base)+"=%s*a)") % size )
                        imfs.append(fHbs(bFlatSize[pos],flatSize[pos],base,1))                
                    cstAtLev = " and ".join(cst_list)

#                     bases = [ sympify(wi),sympify(wj) ]
#                     for i in range(2):
#                         if directions[i]=='b':
#                             bases[i] = sympify('0') if sympify(wi) == sympify('0') else flatSize[i] - bases[i] 
#                     sizes = ( str(flatSize[0]), str(flatSize[1]), str(bFlatSize[0]), str(bFlatSize[1]) )
#                     cstAtLev = ("(exists a,b: 0<="+str(bases[0])+"<%s and 0<="+str(bases[1])+"<%s and "+str(bases[0])+"=%s*a and "+str(bases[1])+"=%s*b)") % sizes
#                     tl, tr = fHbs(bFlatSize[0],flatSize[0],bases[0],1), fHbs(bFlatSize[1],flatSize[1],bases[1],1)
                    imfList.append(imfs) 
                    l,r = l.compose(imfs[0]), r.compose(imfs[1])
                    if cstAtLev:
                        tileinfo.append(cstAtLev)
                    lev+=1
                sIndices = ",".join(indices)
                sCst = " and ".join(tileinfo) 
#                 if sCst.strip() == "and":
#                     sCst = ""
                info['tiling'] = Set("{["+sIndices+"] : "+sCst+"}")
                # Struct + Access info
                info['struct'] = self.getPolyStructure(indices, l, r, partOrigin, partFlatSize, bFlatSize)
#                 info['flatstruct'] = self.getFlatMatrixPolyStructure(indices, l, r, partOrigin, partFlatSize)
                info['access'] = self.getPolyAccess(indices, l, r, imfList, partOrigin, partFlatSize, bFlatSize)
                info['topblk'] = fBoP
                for einfo in extrainfo:
                    funname = 'get'+einfo+'PolyStructure'
                    fun = getattr(self, funname, None)
                    if callable(fun):
                        info[einfo] = fun(indices, l, r, partOrigin, partFlatSize, bFlatSize, baselevel)
                piRow.append(info)
            polyinfo.append(piRow)
        return polyinfo

    
    def __eq__(self, other):
        if self.isScalar() and not other.isScalar() or not self.isScalar() and other.isScalar():
            return False
        if not isinstance(other, self.__class__) or not isinstance(self, other.__class__):
            return False
#         if not isinstance(other, self.__class__) and not isinstance(self, other.__class__) and not (self.isScalar() and other.isScalar()) :
#             return False
        return self.sameLayout(other)

    def sameUpToNames(self, other):
        return self == other and self.name == other.name

    def get_quantity(self):
        return self

    def getInOutOrder(self):
        return [ self.name ]

    def getFlops(self):
        return 0
        
    def getOps(self):
        return 0
    
    def __hash__(self):
        key = (hash(self.__class__.__name__), hash(self.name))
        return hash(key)

    def algo_signature(self):
        res = self.__class__.__name__
        return res
    
    def __repr__(self):
#         return self.__class__.__name__ + "[" + self.name + ", " + str(self.size) + ", " + str(self.descriptor) + "]"
        return self.__class__.__name__ + "[" + self.name + ", " + str(self.size) + ", " + str(self.access) + "]"

    def toLatex(self, context, ind=0, subs=None):
        res = self.name 
        return res

    @classmethod
    def test(cls, struct, access, M, N):
        return True

    def toLL(self, acc=False, accSign=None, sep=False):
        return self.name if not sep else [ self.name ]

    def to_algo(self, decl_map, dep_map, dims_map, expr_map, order, sizes_map, dims):
        if self not in dims_map:
            local_dims = []
            if any(map(lambda MatType: isinstance(self, MatType), (Triangular, Symmetric))):
                existing_dim = filter(lambda d: d is not None, dims)
                d = existing_dim[0] if existing_dim else getNextDim()
                local_dims.extend((d,d))
            else:
                local_dims.append(getNextDim())
                local_dims.append(getNextDim())
            for i,dim in enumerate(dims):
                if dim is None:
                    dims[i] = local_dims[i]
            dims_map[self] = [ d for d in dims ]
            for d,s in zip(dims, self.size):
                if d not in sizes_map:
                    sizes_map[d] = s
#         if self.name not in decl_map: 
            decl_map[self.name] = self
#         if self.name not in dep_map:
            dep_map[self] = None
            expr_map[self] = self
            order.append(self)
        else:
            for i,dim in enumerate(dims):
                if dim is None:
                    dims[i] = dims_map[self][i]
        return self.name
            
    def __str__(self):
        global drawing
        if drawing:
            return self.name + "[" + str(self.size[0]) + "," + str(self.size[1]) + "]"
        else:
            res = "Layout of " + self.__class__.__name__ + " " + self.name + " :\n"
            res += "Origin:\t" + str(self.descriptor.o) + "\n"
            res += "Size:\t" + str(self.size) + "\n"
            res += "Attributes:\t" + str(self.attr) + "\n"
            res += "Level:\t" + str(self.level) + "\n"
            if (self.level > 1):
                res += "fL = " + str(self.fL) + "\n"
                res += "fR = " + str(self.fR) + "\n"
                for rowPart in self.descriptor.rows:
                    res += str(rowPart.nRows) + " x |\t"
                    for colPart in rowPart.cols:
                        res += "(" + str(colPart.nCols) + ", " + colPart.block.name + ")\t"
                    res += "|\n"
                res += "\n"
                for rowPart in self.descriptor.rows:
                    for colPart in rowPart.cols:
                        res += str(colPart.block)
            return res

class QuantityCartesianProduct(Expression):
    def __init__(self, *args):
        super(QuantityCartesianProduct, self).__init__()
        self.qnt_list = args

    def duplicate(self, prefix="", changeHandle=False):
        res = CartesianProduct(*[ qnt.duplicate(prefix)  for qnt in self.qnt_list ])
        if not changeHandle:
            res.handle = self.handle
        return res

    def getOut(self):
        return self

    def sameLayout(self, other):
        if not isinstance(other, QuantityCartesianProduct):
            return False
        for s, o in zip(self.qnt_list, other.qnt_list):
            if not s.sameLayout(o):
                return False
        return True

    def set_info(self, label_list, info_list):
        super(QuantityCartesianProduct, self).set_info(label_list, info_list)
        for qnt in self.qnt_list:
            qnt.set_info(label_list, info_list)

    def subs(self, idsDict, explored=None):
        if explored is not None and self.handle in explored:
            return
        super(QuantityCartesianProduct, self).subs(idsDict)
        for qnt in self.qnt_list:
            qnt.subs(idsDict, explored)
        
    def is_empty(self):
        for qnt in self.qnt_list:
            if qnt.is_empty():
                return True
        return False
             
class Scalar(Quantity):
    __metaclass__ = MetaScalar

    def __new__(cls, name, descriptor, size=None, o=None, attr=None, fL=None, fR=None, access=None):
        return super(Scalar, cls).__new__(cls, name, descriptor, (1,1))
     
    def __init__(self, name, descriptor, size=None, o=None, attr=None, fL=None, fR=None, access=None):
        super(Scalar, self).__init__(name, descriptor, (1,1), o, attr, fL, fR)
        self.access = GenMatAccess(self) 
     
    @classmethod
    def fromBlock(cls, block, o=None, name=None):
        if block.size[0] == block.size[1] and block.size[0] == 1:
            return super(Scalar, Scalar).fromBlock(block, o, name) 
        return None
    
    def matCreateBasicDescriptor(self, block):
        if block.size[0] == block.size[1] and block.size[0] == 1:
            super(Scalar, self).matCreateBasicDescriptor(block) 
     
    def isScalar(self):
        return True

    def getFlatMatrixPolyStructure(self, indices, fL, fR, orig, partFlatSize):
        lims = (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1]))
        s = Set(("{["+(",".join(indices))+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<%s}") % lims)
        return s

    def getDiagPolyStructure(self, indices, fL, fR, orig, partFlatSize, blBlkFlatSize, baselevel):
        return self.getPolyStructure(indices, fL, fR, orig, partFlatSize, blBlkFlatSize)

    def getStrictLowerPolyStructure(self, indices, fL, fR, orig, partFlatSize, blBlkFlatSize, baselevel):
        return {}
    
    def getPolyStructure(self, indices, fL, fR, orig, partFlatSize, blBlkFlatSize):
        lims = (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1]))
        s = Set(("{["+(",".join(indices))+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<%s}") % lims)
        structDict = { Matrix: s }
        return structDict

    def getFlatPolyStructureFromIndices(self, indices, orig, partFlatSize):
        lims = (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1]))
        s = Set(("{["+(",".join(indices))+"]: %s<="+indices[0]+"<%s and %s<="+indices[1]+"<%s}") % lims)
        structDict = { Matrix: s }
        return structDict

    def getPolyAccess(self, indices, fL, fR, imfList, orig, partFlatSize, blBlkFlatSize):
        return self.access.getPolyAccess(indices, fL, fR, imfList, orig, partFlatSize, blBlkFlatSize)

    def toLatex(self, context, ind=0, subs=None):
        res = "\\" + self.name 
        return res
    
    def tile(self, nu):
        block = self.getBlock(0, 0).duplicate()
        B = Block(self.name + str(globalSSAIndex()), block, (1,1))
         
        BP = ColPartition(1, B, self.info)
         
        R0 = RowPartition(1, info=self.info)
        listRowParts = [R0]
        listColParts = [BP]
        R0.addCols(listColParts)

        desc = Descriptor(self.level)
        desc.set_info(self.info.keys(), self.info.values())
        desc.addRows(listRowParts)
        return Scalar("t" + str(globalSSAIndex()), desc, attr=self.attr)

    @classmethod
    def testGeneral(cls, struct, access, M, N):
        isSuper = super(Matrix, cls).test(struct, access, M, N)
        return isSuper and Matrix in struct and M == 1 and N == 1

class Matrix(Quantity):
    __metaclass__ = MetaMatrix
    
    '''Fundamental datatype class for representing Block-Matrices.'''
    def __new__(cls, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, access=None):
        if size[0] == size[1]:
#             if size[0] == 1:
#                 return Scalar(name, descriptor, o=o, attr=attr, fL=fL, fR=fR)
            if cls is Matrix:
                return super(Matrix, SquaredMatrix).__new__(SquaredMatrix, name, descriptor, size)
        return super(Matrix, cls).__new__(cls, name, descriptor, size)
    
    def __init__(self, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, access=None):
        super(Matrix, self).__init__(name, descriptor, size, o, attr, fL, fR)
        self.structDict = structDict
        self.access = GenMatAccess(self) if access is None else access(self) 

#     def _buildStructDict(self):
#         def replaceStructParams(strStruct, paramList):
#             for i in range(6):
#                 strStruct = strStruct.replace("@"+str(i), str(paramList[i]))
#             return strStruct
#         return { Matrix: ("@0<=@1<@2 and @3<=@4<@5}", replaceStructParams) }
        
    def getFlatMatrixPolyStructure(self, indices, fL, fR, orig, partFlatSize):
        lims = (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1]))
        s = Set(("{["+(",".join(indices))+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<%s}") % lims)
        return s
    
    def getPolyStructure(self, indices, fL, fR, orig, partFlatSize, blBlkFlatSize):
        lims = (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1]))
        s = Set(("{["+(",".join(indices))+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<%s}") % lims)
        structDict = { Matrix : s }
        return structDict

    def getLowerStripPolyStructure(self, indices, fL, fR, orig, partFlatSize, blBlkFlatSize, baselevel=None):
        lims = (str(orig[0]+partFlatSize[0]-blBlkFlatSize[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1]))
        s = Set(("{["+(",".join(indices))+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<%s}") % lims)
        structDict = { Matrix : s }
        return structDict

    def getDiagPolyStructure(self, indices, fL, fR, orig, partFlatSize, blBlkFlatSize, baselevel=None):
        lims = (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1]))
        s = Set(("{["+(",".join(indices))+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<%s and "+str(fL.of(0))+"="+str(fR.of(0))+"}") % lims)
        structDict = { Matrix : s }
        return structDict

    def getStrictLowerPolyStructure(self, indices, fL, fR, orig, partFlatSize, blBlkFlatSize, baselevel=None):
        sindices = ",".join(indices)
        sg = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<"+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1])))
        structDict = { Matrix : sg }
        return structDict

    def getFlatPolyStructureFromIndices(self, indices, orig, partFlatSize):
        lims = (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1]))
        s = Set(("{["+(",".join(indices))+"]: %s<="+indices[0]+"<%s and %s<="+indices[1]+"<%s}") % lims)
        structDict = { Matrix : s }
        return structDict

    def getPolyAccess(self, indices, fL, fR, imfList, orig, partFlatSize, blBlkFlatSize):
        return self.access.getPolyAccess(indices, fL, fR, imfList, orig, partFlatSize, blBlkFlatSize)
    
    def tile(self, nu):
        size = self.getPartitionSize(0,0)
#         idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
        min_info = self.info.get('min', {})
        hi, hj = Eq(self.size[0]-size[0], 0).subs(min_info), Eq(self.size[1]-size[1], 0).subs(min_info)
#         hi = Eq( get_expr_bound_over_domain(idcs, dom_info, self.size[0]-size[0], 'min'), 0)
#         hj = Eq( get_expr_bound_over_domain(idcs, dom_info, self.size[1]-size[1], 'min'), 0)
         
        mq = sympy.floor((self.size[0]/nu[0]).together()) if hi or not hi and nu[0] > 1 else size[0] # #rows in main RowPartition
        mr = (self.size[0]%nu[0]).subs(min_info) if hi else 1                                     # #rows of blocks of ColPartitions in leftover RowPartition
        mb = nu[0] if mq.subs(min_info) > 0 or not hi else 0                                   # #rows of blocks of ColPartitions in main RowPartition
#         mr = get_expr_bound_over_domain(idcs, dom_info, self.size[0]%nu[0], 'min') if hi else 1                                     # #rows of blocks of ColPartitions in leftover RowPartition
#         mb = nu[0] if get_expr_bound_over_domain(idcs, dom_info, mq, 'min') > 0 or not hi else 0                                   # #rows of blocks of ColPartitions in main RowPartition
            
        nq = sympy.floor((self.size[1]/nu[1]).together()) if hj or not hj and nu[1] > 1 else size[1] # #cols in main ColPartitions
        nr = (self.size[1]%nu[1]).subs(min_info) if hj else 1                                     # #cols in blocks of leftover ColPartitions
        nb = nu[1] if nq.subs(min_info) > 0 or not hj else 0                                   # #cols in blocks of main ColPartitions
#         nr = get_expr_bound_over_domain(idcs, dom_info, self.size[1]%nu[1], 'min') if hj else 1                                     # #cols in blocks of leftover ColPartitions
#         nb = nu[1] if get_expr_bound_over_domain(idcs, dom_info, nq, 'min') > 0 or not hj else 0                                   # #cols in blocks of main ColPartitions

        mhat = sympify(0) if self.size[0] == 0 else (mq*nu[0])%self.size[0]
        nhat = sympify(0) if self.size[1] == 0 else (nq*nu[1])%self.size[1]
#         mhat = sympify(0) if self.size[0] == 0 else get_expr_bound_over_domain(idcs, dom_info, (mq*nu[0])%self.size[0], 'min')
#         nhat = sympify(0) if self.size[1] == 0 else get_expr_bound_over_domain(idcs, dom_info, (nq*nu[1])%self.size[1], 'min')
        
        blockB = self.getBlock(0, 0).duplicate()
        blockH = self.getBlock(mhat.subs(min_info), 0).duplicate()
        blockV = self.getBlock(0, nhat.subs(min_info)).duplicate()
        blockC = self.getBlock(mhat.subs(min_info), nhat.subs(min_info)).duplicate()
#         blockH = self.getBlock(mhat, 0).duplicate()
#         blockV = self.getBlock(0, nhat).duplicate()
#         blockC = self.getBlock(mhat, nhat).duplicate()
         
        B = Block(self.name + str(globalSSAIndex()), blockB, (mb,nb))
        V = Block(self.name + str(globalSSAIndex()), blockV, (mb,nr))
        H = Block(self.name + str(globalSSAIndex()), blockH, (mr,nb))
        C = Block(self.name + str(globalSSAIndex()), blockC, (mr,nr))
         
        iv = 1 if (nr > 0) or not hj else 0
        ih = 1 if (mr > 0) or not hi else 0
        ic = 1 if ((mr > 0) or not hi) and ((nr > 0) or not hj) else 0
         
        BP = ColPartition(nq, B, self.info)
        VP = ColPartition(iv, V, self.info)
        HP = ColPartition(nq, H, self.info)
        CP = ColPartition(ic, C, self.info)
         
        listRowParts = []
        listColParts = []
         
        R0 = RowPartition(mq, info=self.info)
        if(R0 is not None):
            listRowParts += [R0]
            if(BP is not None):
                listColParts += [BP]
            if(VP is not None):
                listColParts += [VP]
            R0.addCols(listColParts)
 
        listColParts = []
        R1 = RowPartition(ih, info=self.info)
        if(R1 is not None):
            listRowParts += [R1]
            if(HP is not None):
                listColParts += [HP]
            if(CP is not None):
                listColParts += [CP]
            R1.addCols(listColParts)
             
#         if(len(listRowParts) > 0):
        desc = Descriptor(self.level)
        desc.set_info(self.info.keys(), self.info.values())
        desc.addRows(listRowParts)
        mat = Matrix("t" + str(globalSSAIndex()), desc, desc.getSize(), attr=self.attr)
        return mat

    @classmethod
    def testGeneral(cls, struct, access, M, N):
        isSuper = super(Matrix, cls).test(struct, access, M, N)
        if isSuper and Matrix in struct:
            isGeMat = struct[Matrix] == Set("{[i,j]: 0<=i<"+str(M)+" and 0<=j<"+str(N)+"}")
            isGeMat = isGeMat and access == Map("{[i,j]->[i,j]}")
            return isGeMat
        return False
    
class SquaredMatrix(Matrix):
    __metaclass__ = MetaSquaredMatrix
    
    def __new__(cls, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, access=None):
        if( not isinstance(size, tuple) and not isinstance(size, Tuple)):
            size = (size, size)
        return super(SquaredMatrix, cls).__new__(cls, name, descriptor, size, o, attr, fL, fR, structDict, access)

    def __init__(self, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, access=None):
        if( not isinstance(size, tuple) and not isinstance(size, Tuple)):
            size = (size, size)
        super(SquaredMatrix, self).__init__(name, descriptor, size, o, attr, fL, fR, structDict, access)

    @classmethod
    def test(cls, struct, access, M, N):
        return super(SquaredMatrix, cls).test(struct, access, M, N) and M==N

    def tile(self, nu):
        TT = super(SquaredMatrix, self).tile(nu)
        size = TT.size
        if size[0] == size[1]:
            TT = (self.__class__)(TT.name, TT.descriptor, size, attr=self.attr)
        return TT

class Triangular(SquaredMatrix):
    def __new__(cls, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, access=None):
        return super(Triangular, cls).__new__(cls, name, descriptor, size, o, attr, fL, fR, structDict, access)

    def __init__(self, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, access=None):
        super(Triangular, self).__init__(name, descriptor, size, o, attr, fL, fR, structDict, access)
    
    def getDiagPolyStructure(self, indices, fL, fR, orig, partFlatSize, blBlkFlatSize, baselevel=None):
        sindices = ",".join(indices)
        structDict = None
        s = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fL.of(0))+"="+str(fR.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0])))
#         if blBlkFlatSize[0]*blBlkFlatSize[1] == 1:
#             structDict = {Matrix: s }
        if blBlkFlatSize[0]==blBlkFlatSize[1]:
#             sd = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fR.of(0))+"="+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0])))
            structDict = {self.__class__ : s }
        else: #Vert or Horiz partitions
            structDict = {}
        return structDict

    def getTopLeftPolyStructure(self, indices, fL, fR, orig, partFlatSize, blBlkFlatSize, baselevel=None):
        sindices = ",".join(indices)
        structDict = None
        s = Set(("{["+sindices+"]: "+str(fL.of(0))+"=%s and "+str(fR.of(0))+"="+str(fL.of(0))+"}") % str(self.o[0]))
#         if blBlkFlatSize[0]*blBlkFlatSize[1] == 1:
#             structDict = {Matrix: s }
        if blBlkFlatSize[0]==blBlkFlatSize[1]:
#             sd = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fR.of(0))+"="+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0])))
            structDict = {self.__class__: s }
        else: #Vert or Horiz partitions
            structDict = {}
        return structDict

    def getBottomRightPolyStructure(self, indices, fL, fR, orig, partFlatSize, blBlkFlatSize, baselevel):
        sindices = ",".join(indices)
        structDict = None
        psize = self.getNumPartitions()
        bottom_part_orig = self.getPartitionOrigin(psize[0]-1, 0)[0]
        bottom_part_flatsize = self.getFlatPartitionSize(psize[0]-1, 0)[0]
        b = self.getFirstBlockOfPartition(psize[0]-1, 0)

        while b.level > baselevel-1:
            b = b.getBlock(0,0)
        if b.level > 1:
            b_flatsize = b.getFlatSize()[0]
        else:
            b_flatsize = 1

        s = Set(("{["+sindices+"]: "+str(fL.of(0))+"=%s and "+str(fR.of(0))+"="+str(fL.of(0))+"}") % str(bottom_part_orig+bottom_part_flatsize-b_flatsize))
#         if blBlkFlatSize[0]*blBlkFlatSize[1] == 1:
#             structDict = {Matrix: s }
        if blBlkFlatSize[0]==blBlkFlatSize[1]:
#             sd = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fR.of(0))+"="+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0])))
            structDict = {self.__class__: s }
        else: #Vert or Horiz partitions
            structDict = {}
        return structDict
        
class LowerTriangular(Triangular):
    __metaclass__ = MetaLowerTriangular
    
    def __new__(cls, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, access=None):
        return super(LowerTriangular, cls).__new__(cls, name, descriptor, size, o, attr, fL, fR, structDict, access)
    
    def __init__(self, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, access=None):
#         access = LTMatAccess if access is None else access 
        super(LowerTriangular, self).__init__(name, descriptor, size, o, attr, fL, fR, structDict, access)

    def getFlatMatrixPolyStructure(self, indices, fL, fR, orig, partFlatSize):
        s = Set(("{["+(",".join(indices))+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<="+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1])))
        return s

    def getStrictLowerPolyStructure(self, indices, fL, fR, orig, partFlatSize, blBlkFlatSize, baselevel=None):
        sindices = ",".join(indices)
        structDict = None
        if blBlkFlatSize[0]*blBlkFlatSize[1] == 1:
            sg = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<"+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1])))
            structDict = { Matrix: sg }
        elif blBlkFlatSize[0]==blBlkFlatSize[1]:
            sg = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<="+str(fL.of(0)-blBlkFlatSize[1])+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1])))
            structDict = {Matrix: sg }
        else: #Horiz partitions
            if blBlkFlatSize[0]<blBlkFlatSize[1]:
                lims = (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1]))
                s = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<%s}") % lims)
                structDict = { Matrix: s }
            else:
                structDict = {}
        return structDict

    def getPolyStructure(self, indices, fL, fR, orig, partFlatSize, blBlkFlatSize):
        sindices = ",".join(indices)
        structDict = None
        if blBlkFlatSize[0]*blBlkFlatSize[1] == 1:
            sg = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<="+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1])))
            s0 = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fL.of(0))+"<"+str(fR.of(0))+"<%s}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]+partFlatSize[1])))
            structDict = {ZeroMatrix: s0, Matrix: sg }
        elif partFlatSize[0]==partFlatSize[1] and blBlkFlatSize[0]==blBlkFlatSize[1]:
            sd = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fR.of(0))+"="+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0])))
            sg = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<="+str(fL.of(0)-blBlkFlatSize[1])+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1])))
            s0 = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fL.of(0)+blBlkFlatSize[1])+"<="+str(fR.of(0))+"<%s}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]+partFlatSize[1])))
            structDict = {ZeroMatrix: s0, Matrix: sg, LowerTriangular: sd }
        else: #Vert or Horiz partitions
            lims = (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1]))
            s = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<%s}") % lims)
            TypeStr = ZeroMatrix if blBlkFlatSize[0]>blBlkFlatSize[1] else Matrix
            structDict = { TypeStr: s }
        return structDict

    def getFlatPolyStructureFromIndices(self, indices, orig, partFlatSize):
        sindices = ",".join(indices)
        sg = Set(("{["+sindices+"]: %s<="+indices[0]+"<%s and %s<="+indices[1]+"<="+indices[0]+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1])))
        s0 = Set(("{["+sindices+"]: %s<="+indices[0]+"<%s and "+indices[0]+"<"+indices[1]+"<%s}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]+partFlatSize[1])))
        structDict = {ZeroMatrix: s0, Matrix: sg }
        return structDict

    @classmethod
    def test(cls, struct, access, M, N):
        isSuper = super(LowerTriangular, cls).test(struct, access, M, N)
        if isSuper and Matrix in struct:
            isLowTria = struct[Matrix] == Set("{[i,j]: 0<=i<"+str(M)+" and 0<=j<=i}")
            if M > 1:
                isLowTria = isLowTria and ZeroMatrix in struct and struct[ZeroMatrix] == Set("{[i,j]: 0<=i<"+str(M)+" and i<j<"+str(M)+"}")
            return isLowTria
        return False

class LowerUnitTriangular(LowerTriangular):
    __metaclass__ = MetaLowerUnitTriangular
    
    def __new__(cls, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, access=None):
        return super(LowerUnitTriangular, cls).__new__(cls, name, descriptor, size, o, attr, fL, fR, structDict, access)
    
    def __init__(self, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, access=None):
#         access = LTMatAccess if access is None else access 
        super(LowerUnitTriangular, self).__init__(name, descriptor, size, o, attr, fL, fR, structDict, access)

    def getPolyStructure(self, indices, fL, fR, orig, partFlatSize, blBlkFlatSize):
        sindices = ",".join(indices)
        structDict = None
        if blBlkFlatSize[0]*blBlkFlatSize[1] == 1:
            sg = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<"+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1])))
            s1 = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fL.of(0))+"="+str(fR.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0])) )
            s0 = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fL.of(0))+"<"+str(fR.of(0))+"<%s}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]+partFlatSize[1])))
            structDict = {ZeroMatrix: s0, constant_matrix_type_with_value(1): s1, Matrix: sg }
        elif partFlatSize[0]==partFlatSize[1] and blBlkFlatSize[0]==blBlkFlatSize[1]:
            sd = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fR.of(0))+"="+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0])))
            sg = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<="+str(fL.of(0)-blBlkFlatSize[1])+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1])))
            s0 = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fL.of(0)+blBlkFlatSize[1])+"<="+str(fR.of(0))+"<%s}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]+partFlatSize[1])))
            structDict = {ZeroMatrix: s0, Matrix: sg, LowerUnitTriangular: sd }
        else: #Vert or Horiz partitions
            lims = (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1]))
            s = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<%s}") % lims)
            TypeStr = ZeroMatrix if blBlkFlatSize[0]>blBlkFlatSize[1] else Matrix
            structDict = { TypeStr: s }
        return structDict

    def getFlatPolyStructureFromIndices(self, indices, orig, partFlatSize):
        sindices = ",".join(indices)
        sg = Set(("{["+sindices+"]: %s<="+indices[0]+"<%s and %s<="+indices[1]+"<"+indices[0]+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1])))
        s1 = Set(("{["+sindices+"]: %s<="+indices[0]+"<%s and "+indices[0]+"="+indices[1]+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0])))
        s0 = Set(("{["+sindices+"]: %s<="+indices[0]+"<%s and "+indices[0]+"<"+indices[1]+"<%s}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]+partFlatSize[1])))
        structDict = {ZeroMatrix: s0, constant_matrix_type_with_value(1): s1, Matrix: sg }
        return structDict

    @classmethod
    def test(cls, struct, access, M, N):
        isSuper = super(LowerTriangular, cls).test(struct, access, M, N)
        if isSuper and constant_matrix_type_with_value(1) in struct:
            isLowUnitTria = struct[constant_matrix_type_with_value(1)] == Set("{[i,j]: 0<=i<"+str(M)+" and i=j}")
            if M > 1:
                isLowUnitTria = isLowUnitTria and Matrix in struct and struct[Matrix] == Set("{[i,j]: 0<=i<"+str(M)+" and 0<=j<i}")
                isLowUnitTria = isLowUnitTria and ZeroMatrix in struct and struct[ZeroMatrix] == Set("{[i,j]: 0<=i<"+str(M)+" and i<j<"+str(M)+"}")
            return isLowUnitTria
        return False
    
class UpperTriangular(Triangular):
    __metaclass__ = MetaUpperTriangular

    def __new__(cls, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, access=None):
        return super(UpperTriangular, cls).__new__(cls, name, descriptor, size, o, attr, fL, fR, structDict, access)
    
    def __init__(self, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, access=None):
#         access = UTMatAccess if access is None else access 
        super(UpperTriangular, self).__init__(name, descriptor, size, o, attr, fL, fR, structDict, access)

    def getFlatMatrixPolyStructure(self, indices, fL, fR, orig, partFlatSize):
        s = Set(("{["+(",".join(indices))+"]: %s<="+str(fL.of(0))+"<%s and "+str(fL.of(0))+"<="+str(fR.of(0))+"<%s}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]+partFlatSize[1])))
        return s

    def getPolyStructure(self, indices, fL, fR, orig, partFlatSize, blBlkFlatSize):
        sindices = ",".join(indices)
        structDict = None
        if blBlkFlatSize[0]*blBlkFlatSize[1] == 1:
            sg = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fL.of(0))+"<="+str(fR.of(0))+"<%s}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]+partFlatSize[1])))
            s0 = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<"+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1])))
            structDict = {ZeroMatrix: s0, Matrix: sg }
        elif partFlatSize[0]==partFlatSize[1] and blBlkFlatSize[0]==blBlkFlatSize[1]:
            sd = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fR.of(0))+"="+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0])))
            sg = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fL.of(0)+blBlkFlatSize[1])+"<="+str(fR.of(0))+"<%s}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]+partFlatSize[1])))
            s0 = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<="+str(fL.of(0)-blBlkFlatSize[1])+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1])))
            structDict = {ZeroMatrix: s0, Matrix: sg, UpperTriangular: sd }
        else:
            lims = (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1]))
            s = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<%s}") % lims)
            TypeStr = Matrix if blBlkFlatSize[0]>blBlkFlatSize[1] else ZeroMatrix
            structDict = { TypeStr: s }
        return structDict

    def getFlatPolyStructureFromIndices(self, indices, orig, partFlatSize):
        sindices = ",".join(indices)
        sg = Set(("{["+sindices+"]: %s<="+indices[0]+"<%s and "+indices[0]+"<="+indices[1]+"<%s}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]+partFlatSize[1])))
        s0 = Set(("{["+sindices+"]: %s<="+indices[0]+"<%s and %s<="+indices[1]+"<"+indices[0]+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1])))
        structDict = {ZeroMatrix: s0, Matrix: sg }
        return structDict

    def getStrictUpperPolyStructure(self, indices, fL, fR, orig, partFlatSize, blBlkFlatSize, baselevel=None):
        sindices = ",".join(indices)
        structDict = None
        if blBlkFlatSize[0]*blBlkFlatSize[1] == 1:
            sg = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fL.of(0))+"<"+str(fR.of(0))+"<%s }") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]+partFlatSize[1])))
            structDict = { Matrix: sg }
        elif blBlkFlatSize[0]==blBlkFlatSize[1]:
            sg = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fL.of(0)+blBlkFlatSize[1])+"<="+str(fR.of(0))+"<%s}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]+partFlatSize[1])))
            structDict = {Matrix: sg }
        else: #Vert partitions
            if blBlkFlatSize[0]>blBlkFlatSize[1]:
                lims = (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1]))
                s = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<%s}") % lims)
                structDict = { Matrix: s }
            else:
                structDict = {}
        return structDict

    @classmethod
    def test(cls, struct, access, M, N):
        isSuper = super(UpperTriangular, cls).test(struct, access, M, N)
        if isSuper and Matrix in struct:
            isUpTria = struct[Matrix] == Set("{[i,j]: 0<=i<"+str(M)+" and i<=j<"+str(M)+"}")
            if M > 1:
                isUpTria = isUpTria and ZeroMatrix in struct and struct[ZeroMatrix] == Set("{[i,j]: 0<=i<"+str(M)+" and 0<=j<i}")
            return isUpTria
        return False

class UpperUnitTriangular(UpperTriangular):
    __metaclass__ = MetaUpperUnitTriangular
    #TBA
    @classmethod
    def test(cls, struct, access, M, N):
        isSuper = super(UpperTriangular, cls).test(struct, access, M, N)
        if isSuper and constant_matrix_type_with_value(1) in struct:
            isUpUnitTria = struct[constant_matrix_type_with_value(1)] == Set("{[i,j]: 0<=i<"+str(M)+" and i=j}")
            if M > 1:
                isUpUnitTria = isUpUnitTria and Matrix in struct and struct[Matrix] == Set("{[i,j]: 0<=i<"+str(M)+" and i<j<"+str(M)+"}")
                isUpUnitTria = isUpUnitTria and ZeroMatrix in struct and struct[ZeroMatrix] == Set("{[i,j]: 0<=i<"+str(M)+" and 0<=j<i}")
            return isUpUnitTria
        return False

class Symmetric(SquaredMatrix):
    __metaclass__ = MetaSymmetric

    def __new__(cls, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, access=None):
        return super(Symmetric, cls).__new__(cls, name, descriptor, size, o, attr, fL, fR, structDict, access)
    
    def __init__(self, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, access=None):
        access = USMatAccess if access is None else access 
        super(Symmetric, self).__init__(name, descriptor, size, o, attr, fL, fR, structDict, access)

    def transpose(self):
        return self.duplicate("tr")
    
    @classmethod
    def test(cls, struct, access, M, N):
        return cls.testLower(struct, access, M, N) or cls.testUpper(struct, access, M, N)
    
    @classmethod
    def testLower(cls, struct, access, M, N):
        isLowSymm = super(Symmetric, cls).test(struct, access, M, N)
        if Matrix in struct:
            isLowSymm = isLowSymm and struct[Matrix] == Set("{[i,j]: 0<=i<"+str(M)+" and 0<=j<"+str(N)+"}")
            isLowSymm = isLowSymm and access == Map("{[i,j]->[i,j]: j<=i}").union(Map("{[i,j]->[j,i]: j>i}"))
            return isLowSymm
        return False
    
    @classmethod
    def testUpper(cls, struct, access, M, N):
        isUpSymm = super(Symmetric, cls).test(struct, access, M, N)
        if Matrix in struct:
            isUpSymm = isUpSymm and struct[Matrix] == Set("{[i,j]: 0<=i<"+str(M)+" and 0<=j<"+str(N)+"}")
            isUpSymm = isUpSymm and access == Map("{[i,j]->[j,i]: j<i}").union(Map("{[i,j]->[i,j]: j>=i}"))
            return isUpSymm
        return False
    
    def tile(self, nu):
        TS = super(Symmetric, self).tile(nu)
        size = TS.size
        if size[0] == size[1]:
            TS = (self.__class__)(TS.name, TS.descriptor, size, access=self.access.__class__, attr=self.attr)
        return TS

class ConstantMatrix(Matrix):
    def __new__(cls, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, accessDict=None):
        return super(ConstantMatrix, cls).__new__(cls, name, descriptor, size, o, attr, fL, fR, structDict, accessDict)

    def __init__(self, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, accessDict=None):
        super(ConstantMatrix, self).__init__(name, descriptor, size, o, attr, fL, fR, structDict, accessDict)

class ConstantSquaredMatrix(SquaredMatrix):
    def __new__(cls, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, access=None):
        return super(ConstantSquaredMatrix, cls).__new__(cls, name, descriptor, size, o, attr, fL, fR, structDict, access)

    def __init__(self, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, access=None):
        super(ConstantSquaredMatrix, self).__init__(name, descriptor, size, o, attr, fL, fR, structDict, access)
    
class AllEntriesConstantMatrix(ConstantMatrix):
    _const_value = None

    def __new__(cls, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, accessDict=None):
        return super(AllEntriesConstantMatrix, cls).__new__(cls, name, descriptor, size, o, attr, fL, fR, structDict, accessDict)

    def __init__(self, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, accessDict=None):
        super(AllEntriesConstantMatrix, self).__init__(name, descriptor, size, o, attr, fL, fR, structDict, accessDict)
    
    def tile(self, nu):
        TC = super(AllEntriesConstantMatrix, self).tile(nu)
#         TC = super(self.__class__, self).tile(nu)
        TC = (self.__class__)(TC.name, TC.descriptor, TC.size)
        return TC

    def getPolyStructure(self, indices, fL, fR, orig, partFlatSize, blBlkFlatSize):
        lims = (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1]))
        s = Set(("{["+(",".join(indices))+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<%s}") % lims)
        structDict = { type(self) : s }
        return structDict

    def getLowerStripPolyStructure(self, indices, fL, fR, orig, partFlatSize, blBlkFlatSize, baselevel=None):
        lims = (str(orig[0]+partFlatSize[0]-blBlkFlatSize[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1]))
        s = Set(("{["+(",".join(indices))+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<%s}") % lims)
        structDict = { type(self) : s }
        return structDict

    def getDiagPolyStructure(self, indices, fL, fR, orig, partFlatSize, blBlkFlatSize, baselevel=None):
        lims = (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1]))
        s = Set(("{["+(",".join(indices))+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<%s and "+str(fL.of(0))+"="+str(fR.of(0))+"}") % lims)
        structDict = { type(self) : s }
        return structDict

    def getStrictLowerPolyStructure(self, indices, fL, fR, orig, partFlatSize, blBlkFlatSize, baselevel=None):
        sindices = ",".join(indices)
        sg = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<"+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1])))
        structDict = { type(self) : sg }
        return structDict

    def getFlatPolyStructureFromIndices(self, indices, orig, partFlatSize):
        lims = (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1]))
        s = Set(("{["+(",".join(indices))+"]: %s<="+indices[0]+"<%s and %s<="+indices[1]+"<%s}") % lims)
        structDict = { type(self) : s }
        return structDict

    @classmethod
    def test(cls, struct, access, M, N):
        isSuper = super(AllEntriesConstantMatrix, cls).test(struct, access, M, N)
        if isSuper and len(struct) == 1 and issubclass(struct.keys()[0], AllEntriesConstantMatrix):
            return struct[struct.keys()[0]] == Set("{[i,j]: 0<=i<"+str(M)+" and 0<=j<"+str(N)+"}")
        return False
    
class ZeroMatrix(AllEntriesConstantMatrix):
    __metaclass__ = MetaZeroMatrix
    
    def __new__(cls, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, accessDict=None):
        return super(ZeroMatrix, cls).__new__(cls, name, descriptor, size, o, attr, fL, fR, structDict, accessDict)
 
    def __init__(self, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, accessDict=None):
        super(ZeroMatrix, self).__init__(name, descriptor, size, o, attr, fL, fR, structDict, accessDict)
#     
#     def tile(self, nu):
#         TZ = super(ZeroMatrix, self).tile(nu)
#         TZ = (self.__class__)(TZ.name, TZ.descriptor, TZ.size)
#         return TZ
#         
#     @classmethod
#     def test(cls, struct, access, M, N):
#         isSuper = super(ZeroMatrix, cls).test(struct, access, M, N)
#         if isSuper and ZeroMatrix in struct:
#             return struct[ZeroMatrix] == Set("{[i,j]: 0<=i<"+str(M)+" and 0<=j<"+str(N)+"}")
#         return False


def constant_matrix_type_with_value(value):
    class AllEntriesConstantMatrixWithValue(AllEntriesConstantMatrix):
        __metaclass__ = _meta_constant_with_value(value)

        def __new__(cls, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, access=None):
            return super(AllEntriesConstantMatrixWithValue, cls).__new__(cls, name, descriptor, size, o, attr, fL, fR, structDict, access)
    
        def __init__(self, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, access=None):
            super(AllEntriesConstantMatrixWithValue, self).__init__(name, descriptor, size, o, attr, fL, fR, structDict, access)
        
    return AllEntriesConstantMatrixWithValue


class IdentityMatrix(ConstantSquaredMatrix):
    __metaclass__ = MetaIdentityMatrix
    
    def __new__(cls, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, access=None):
        return super(IdentityMatrix, cls).__new__(cls, name, descriptor, size, o, attr, fL, fR, structDict, access)

    def __init__(self, name, descriptor, size, o=None, attr=None, fL=None, fR=None, structDict=None, access=None):
        super(IdentityMatrix, self).__init__(name, descriptor, size, o, attr, fL, fR, structDict, access)
    

    def getPolyStructure(self, indices, fL, fR, orig, partFlatSize, blBlkFlatSize):
        sindices = ",".join(indices)
        structDict = None
        if blBlkFlatSize[0]*blBlkFlatSize[1] == 1:
            s1 = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fL.of(0))+"="+str(fR.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0])) )
            s0 = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<%s}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1])) )
            s0 = s0 - s1
            structDict = {ZeroMatrix: s0, constant_matrix_type_with_value(1): s1 }
        elif partFlatSize[0]==partFlatSize[1] and blBlkFlatSize[0]==blBlkFlatSize[1]:
            sd = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fR.of(0))+"="+str(fL.of(0))+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0])))
            s0l = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<="+str(fL.of(0)-blBlkFlatSize[1])+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1])))
            s0u = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and "+str(fL.of(0)+blBlkFlatSize[1])+"<="+str(fR.of(0))+"<%s}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]+partFlatSize[1])))
            structDict = {ZeroMatrix: s0l.union(s0u), IdentityMatrix: sd }
        else: #Vert or Horiz partitions
            lims = (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1]))
            s = Set(("{["+sindices+"]: %s<="+str(fL.of(0))+"<%s and %s<="+str(fR.of(0))+"<%s}") % lims)
            structDict = { ZeroMatrix: s }
        return structDict

    def getFlatPolyStructureFromIndices(self, indices, orig, partFlatSize):
        sindices = ",".join(indices)
        s1 = Set(("{["+sindices+"]: %s<="+indices[0]+"<%s and "+indices[0]+"="+indices[1]+"}") % (str(orig[0]), str(orig[0]+partFlatSize[0])))
        s0 = Set(("{["+sindices+"]: %s<="+indices[0]+"<%s and %s<="+indices[1]+"<%s}") % (str(orig[0]), str(orig[0]+partFlatSize[0]), str(orig[1]), str(orig[1]+partFlatSize[1])))
        s0 = s0 - s1
        structDict = {ZeroMatrix: s0, constant_matrix_type_with_value(1): s1 }
        return structDict

    @classmethod
    def test(cls, struct, access, M, N):
        isSuper = super(IdentityMatrix, cls).test(struct, access, M, N)
        if isSuper and constant_matrix_type_with_value(1) in struct:
            diag_set = Set("{[i,j]: 0<=i<"+str(M)+" and i=j}")
            isIdentity = struct[constant_matrix_type_with_value(1)] == diag_set
            if M > 1:
                isIdentity = isIdentity  and ZeroMatrix in struct and (struct[ZeroMatrix] == Set("{[i,j]: 0<=i<"+str(M)+" and 0<=j<"+str(M)+"}") - diag_set) 
            return isIdentity
        return False
##############################################
#-----------Operators------------------------#
##############################################

class Operator(Expression):
    def __init__(self):
        super(Operator, self).__init__()
        self.inexpr = []
        self.out = None
        self.nuout = None
        self.reqAss = False

    def dependsOn(self, idx):
        if self.out.dependsOn(idx):
            return True
        for s in self.inexpr:
            if s.dependsOn(idx):
                return True
        return False

    def is_bounded(self):
        for ie in self.inexpr:
            if not ie.is_bounded():
                return False
        return self.out.is_bounded()

    def is_also_empty(self):
        if self.is_empty():
            return True
        for ie in self.inexpr:
            if ie.is_also_empty():
                return True
        return self.out.is_also_empty()

    def is_empty(self):
        if not self.inexpr:
            return True
        for ie in self.inexpr:
            if ie.is_empty():
                return True
        return self.out.is_empty()
        
    def get_pot_zero_dims(self):
        res = []
        for ie in self.inexpr:
            res.extend( ie.get_pot_zero_dims() )
        res.extend( self.out.get_pot_zero_dims() )
        return res 
    
    def set_info(self, label_list, info_list):
        super(Operator, self).set_info(label_list, info_list)
        if self.out:
            self.out.set_info(label_list, info_list)
        for e in self.inexpr:
            e.set_info(label_list, info_list)

    def set_out_info(self, label_list, info_list):
        if self.out:
            self.out.set_info(label_list, info_list)
        
    def set_info_no_td(self, label_list, info_list):
        super(Operator, self).set_info(label_list, info_list)
        
    def getNonTileOut(self):
        return self.out
        
    def subs(self, idsDict, explored=None):
        if explored is not None:
            if self.handle in explored:
                return
            explored.append(self.handle)
        
        super(Operator, self).subs(idsDict)
        for e in self.inexpr:
            e.subs(idsDict, explored)
        self.out.subs(idsDict)
    
    def getLeavesWithDiffType(self):
        res = []
        for sub in self.inexpr:
            if isinstance(sub, self.__class__):
                res.extend(sub.getLeavesWithDiffType())
            else:
                res.append(sub)
        return res

    def setComputed(self, value):
        super(Operator, self).setComputed(value)
        #In case an  operator is computed so must be for its subexprs
        if value:
            for exp in self.inexpr:
                if not exp.isComputed():
                    exp.setComputed(True)

    def resetComputed(self):
        self.computed = False
        self.nuout = None
        for exp in self.inexpr:
            exp.resetComputed()
    
    def remove(self):
        if len(self.pred) == 1 and (self.pred[0][0] is None):
            for sub in self.inexpr:
                if isinstance(sub, Operator):
                    sub.delPred(self)
                    sub.remove()
            del self.inexpr[:]

    def computeIdxPosAndLevInfo(self):
        for i in self.inexpr:
            i.computeIdxPosAndLevInfo()
        self.out.computeIdxPosAndLevInfo()
            
    def computeIdxPriority(self, idxPriorityList, indices, order, baselevel):
        for i in self.inexpr:
            if isinstance(i, Operator):
                i.computeIdxPriority(idxPriorityList, indices, order, baselevel)
        idxInfoList = [ i.getOut().idxPosAndLevInfo for i in self.inexpr ] # See Quantity.computeIdxPosAndLevInfo for content
        iPriority = self.orderPolicy(idxInfoList, indices, order, baselevel)
        idxPriorityList.append(iPriority)

    def computeUnrolling(self, uFs, indices, baselevel):
        for i in self.inexpr:
            if isinstance(i, Operator):
                i.computeUnrolling(uFs, indices, baselevel)
        self.unrollingPolicy(uFs, indices, baselevel)

    def unrollingPolicy(self, uFs, indices, baselevel):
        pass

    def markProperties(self, propDict, propList, indices, baselevel):
        for i in self.inexpr:
            if isinstance(i, Operator):
                i.markProperties(propDict, propList, indices, baselevel)
        self.checkProperties(propDict, propList, indices, baselevel)

    def checkProperties(self, propDict, propList, indices, baselevel):
        idxInfoList = [ i.getOut().idxPosAndLevInfo for i in self.inexpr ] # See Quantity.computeIdxPosAndLevInfo for content
        for i in indices:
            idxInfo = filter(lambda idxInfo: i in idxInfo, idxInfoList)
            if len(idxInfo) > 0:
                for p in propList:
                    mark = p(self, i, idxInfoList, baselevel)
                    if mark:
                        propDict[i].update([mark])
    
    def computeSpaceIdxNames(self, i, j, ipfix, jpfix, opts, depth=1, baselevel=2):
        for inexpr in self.inexpr:
            inexpr.computeSpaceIdxNames(i, j, ipfix, jpfix, opts, depth, baselevel)
        inOut = self.inexpr[0].getOut()
        for c in range(len(inOut.spaceIdxNames)):
            self.out.spaceIdxNames[c] = [ idx for idx in inOut.spaceIdxNames[c] ]

    def cleanSpaceIdxNames(self):
        self.out.spaceIdxNames = [[],[]]
        for inexpr in self.inexpr:
            inexpr.cleanSpaceIdxNames()
        
    def getSpaceIdxSet(self):
        full_list = self.out.spaceIdxNames[0]+self.out.spaceIdxNames[1] 
        ret = set([i for i in full_list if i is not None])
        for inexpr in self.inexpr:
            ret = ret.union(inexpr.getSpaceIdxSet())
        return ret

    def sameUpToNames(self, other):
        if not isinstance(other, self.__class__):
            return False
        for e,o in zip(self.inexpr, other.inexpr):
            if not e.sameUpToNames(o):
                return False
        return True

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
#         if self.handle != other.handle:
#             return False
        for e,o in zip(self.inexpr, other.inexpr):
            if e != o:
                return False
        return True

    def __ne__(self, other):
        return not (self == other)

    def getHolograph(self, memo=None):
        if memo is None:
            memo = {}
        h = super(Operator, self).getHolograph()
        memo[id(self)] = h
        
        for i,ie in zip(range(len(self.inexpr)),self.inexpr):
            hie = memo[id(ie)] if id(ie) in memo else ie.getHolograph(memo)
            h.succ.append(hie)
            hie.pred.append((h,i))
            
        return h

    def getStructFromAbove(self):
        return self.pred[0][0].getStructFromAbove() 

    def getAccessFromAbove(self):
        return self.pred[0][0].getAccessFromAbove() 

    def deepUpdateDep(self, depSet):
        self.depSet.update(depSet)
        for sub in self.inexpr:
            sub.deepUpdateDep(depSet)

    def getInOutOrder(self):
        res = []
        for i in self.inexpr:
            res += i.getInOutOrder()
        return res

    def getFlops(self):
        c = 0
        for e in self.inexpr:
            c += e.getFlops()
        return c

    def getOps(self):
        c = 0
        for e in self.inexpr:
            c += e.getOps()
        return c

    def algo_signature(self):
        res = self.__class__.__name__ + "_"
        res += "_".join( [inexpr.algo_signature() for inexpr in self.inexpr] )
        return res

    def __hash__(self):
        tin = tuple(self.inexpr)
        key = (hash(self.__class__.__name__), hash(tin))
        return hash(key)

class CartesianProduct(Operator):
    def __init__(self, *args, **kwargs):
        super(CartesianProduct, self).__init__()
        self.inexpr.extend(args)
        self.buildout(kwargs.get('out', None))
        self.setAsPred()

    def buildout(self, out=None):
        src = self.getInexprMat(0)
        self.set_info_no_td(src.info.keys(), src.info.values())
        if out:
            self.out = out
        else:
            self.out = QuantityCartesianProduct(*[ expr.getOut().duplicate("cp" + str(globalSSAIndex())) for expr in self.inexpr ])
        self.set_out_info(src.info.keys(), src.info.values())

    def duplicate(self, prefix="", everything=True, changeOut=False, changeHandle=False):
        tIn = [ inexpr.duplicate() if isinstance(inexpr, Quantity) else inexpr.duplicate(prefix, everything, changeOut, changeHandle) for inexpr in self.inexpr ] if everything else self.inexpr
        if changeOut:
            out = None
            changeHandle = True
        else:
            out = self.out.duplicate(prefix)
        res = CartesianProduct(*tIn, out=out)
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res

    def subs(self, idsDict, explored=None):
        if explored is not None:
            if self.handle in explored:
                return
            explored.append(self.handle)        
        super(Operator, self).subs(idsDict)
        for expr in self.inexpr:
            expr.subs(idsDict, explored)
        self.out.subs(idsDict)

    def toLL(self, acc=False, accSign=None, sep=False):
        res = "[ " + ", ".join( [inexpr.toLL() for inexpr in self.inexpr] ) + " ]"
        return res

    def __str__(self):
        res = "[ " + ", ".join( [str(inexpr) for inexpr in self.inexpr] ) + " ]"
        return res
        
class SimpleOperator(Operator):
    '''
    An operator is simple when it accepts only subexpressions as an input
    '''
    def __init__(self):
        super(SimpleOperator, self).__init__()

class NewContextOperator(Operator):
    '''
    An operator that generates a new context
    '''
    def __init__(self):
        super(NewContextOperator, self).__init__()

class Function(Operator):
    '''
    Arbitrary Operator Expression.
    '''
    def __init__(self, name, domsize, sexprs, out=None, out_class=None, out_access=None):
        super(Function, self).__init__()
        self.name = name
        self.domsize = sympify(domsize, locals=sym_locals) # Can also be generalized to multiple range sizes. A single domsize is shared by all outs. 
        self.inexpr = list(sexprs)
        self.buildout(out, out_class, out_access)
        self.setAsPred()

    def duplicate(self, prefix="", everything=True, changeOut=False, changeHandle=False):
        tIn = [ inexpr.duplicate() if isinstance(inexpr, Quantity) else inexpr.duplicate(prefix, everything, changeOut, changeHandle) for inexpr in self.inexpr ] if everything else self.inexpr
        if changeOut:
            out = None
            changeHandle = True
#         elif isinstance(self.out, list):
#             out = []
#             for o in self.out:
#                 out.append( o.duplicate(prefix) )
        else:
            out = self.out.duplicate(prefix)
        res = Function(self.name, self.domsize, tIn, out)
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res

    def buildout(self, out, out_class, out_access, src=None):
        if src is None:
            src = self.getInexprMat(0)

        self.set_info_no_td(src.info.keys(), src.info.values())

        if(out):
            self.out = out
        else:
            def _buildout(out_cls, out_acc): 
                name = "fun"+ str(globalSSAIndex())
                desc = scalar_block()
                desc.set_info(src.info.keys(), src.info.values())
                return out_cls(name, desc, size=self.domsize, access=out_acc)
            
            if isinstance(out_class, list):
                multi_out = []
                for out_cls, out_acc in zip(out_class, out_access):
                    multi_out.append( _buildout(out_cls, out_acc) )
                self.out = QuantityCartesianProduct(*multi_out)
            else:
                self.out = _buildout(out_class, out_access)
        self.set_out_info(src.info.keys(), src.info.values())
            
#     def toLatex(self, context, ind=0, subs=None):
#         l, r = self.inexpr[0].toLatex(context, ind, subs), self.inexpr[1].toLatex(context, ind, subs)
#         res = l 
#         if context.bindingTable.isBound(self.out) and context.bindingTable.getPhysicalLayout(self.out) is None:
#             res += "$\n"
#             res += ind*" " + "$+$\n"
#             res += ind*" " + "$" + r
#         else:
#             res += " + " + r
#         return res

    def toLL(self, acc=False, accSign=None, sep=False):
        res = self.name + "( " + str(self.domsize[0]) + " , " + str(self.domsize[1]) + " ; "
        res += ", ".join( [inexpr.toLL() for inexpr in self.inexpr] )
        res += " )"
        return res

    def subs(self, idsDict, explored=None):
        if explored is not None:
            if self.handle in explored:
                return
            explored.append(self.handle)
        
        super(Operator, self).subs(idsDict)
        for e in self.inexpr:
            e.subs(idsDict, explored)
#         if isinstance(self.out, list):
#             for out in self.out:
#                 out.subs(idsDict)
#         else:
        self.out.subs(idsDict)
        self.domsize = self.domsize.subs(idsDict)

    def is_func(self):
        return True
    
    def __str__(self):
        res = self.name + "( " + str(self.domsize[0]) + " , " + str(self.domsize[1]) + " ; "
        res += ", ".join( [str(inexpr) for inexpr in self.inexpr] )
        res += " )"
        return res

    def algo_signature(self):
        res = self.name
        return res
    
    def __hash__(self):
        tin = tuple(self.inexpr)
        key = (hash(self.name), hash(tin))
        return hash(key)

class Add(SimpleOperator):
    '''
    Addition Expression.
    '''
    def __init__(self, sexpr0, sexpr1, out=None):
        super(Add, self).__init__()
        if isinstance(sexpr0, Holonode) and isinstance(sexpr1, Holonode):
            self.buildout(out, [sexpr0.node.getOut(), sexpr1.node.getOut()])
        else:
            self.inexpr = [ sexpr0, sexpr1 ]
            self.buildout(out)
            self.setAsPred()

    def duplicate(self, prefix="", everything=True, changeOut=False, changeHandle=False):
        tIn = [ inexpr.duplicate() if isinstance(inexpr, Quantity) else inexpr.duplicate(prefix, everything, changeOut, changeHandle) for inexpr in self.inexpr ] if everything else self.inexpr
        if changeOut:
            out = None
            changeHandle = True
        else:
            out = self.out.duplicate(prefix)
        res = Add(tIn[0], tIn[1], out)
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res

    def duplicateUpToBoundaries(self, prefix="", boundaries=None, changeHandle=True):
        if boundaries is None:
            boundaries = []
        tIn = [ inexpr if (inexpr in boundaries) else inexpr.duplicateUpToBoundaries(prefix, boundaries, changeHandle) for inexpr in self.inexpr ]
        res = Add(tIn[0], tIn[1], self.out.duplicate(prefix))
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res
    
    @staticmethod
    def orderPolicy(idxInfoList, indices, order, baselevel):
        iPriority = {}
        for i in indices:
            idxInfo = filter(lambda idxInfo: i in idxInfo, idxInfoList)
            if len(idxInfo) == 0:
                p = {'t': (0,0), 's': 0, 'i': 0}
            else:
                idxInfo = idxInfo[0]
                rowIdx = any(map(lambda idxInfo: i in idxInfo and idxInfo[i][2] == 0, idxInfoList))
                colIdx = any(map(lambda idxInfo: i in idxInfo and idxInfo[i][2] == 1, idxInfoList))
                lev = idxInfo[i][1]
                if rowIdx:
                    p = {'t': (idxInfo[i][0]-lev,0), 's': 0, 'i': 0}
                elif colIdx:
                    p = {'t': (idxInfo[i][0]-lev,0), 's': 1, 'i': 0}
            t = ( p[order[0]], p[order[1]], p[order[2]] )
            iPriority[i] = t
        return iPriority

    def unrollingPolicy(self, uFs, indices, baselevel):
        idxInfoList = [ i.getOut().idxPosAndLevInfo for i in self.inexpr ] # See Quantity.computeIdxPosAndLevInfo for content
        for i in indices:
            idxInfo = filter(lambda idxInfo: i in idxInfo, idxInfoList)
            if len(idxInfo) > 0:
#                idxInfo = idxInfo[0]
                colIdx = any(map(lambda idxInfo: i in idxInfo and idxInfo[i][2] == 1, idxInfoList))
                baseIdx = all(map(lambda idxInfo: idxInfo[i][1] == baselevel if i in idxInfo else True, idxInfoList))
                if colIdx and baseIdx:
                    uFs[i].append(1)

    def buildout(self, out, src=None):
        if src is None:
            src0 = self.getInexprMat(0)
            src1 = self.getInexprMat(1)
        else:
            src0, src1 = src[0], src[1]
#         if(src0.level != src1.level):
#             exit("Expression Tree Error > Add: subexpressions have mismatching levels.")
#         
        self.set_info_no_td(src0.info.keys(), src0.info.values())
        if not src0.sameLayout(src1):
            exit("Expression Tree Error > Add: Mismatching layout.")
        
        if(out):
            self.out = out
        else: 
#             self.out = src0.duplicate("d"+ str(globalSSAIndex()), o=[0,0], fL=fI(src0.size[0]), fR=fI(src0.size[1]))
            AddType = src0.__class__+src1.__class__
            name = "add"+ str(globalSSAIndex())
            self.out = AddType(name, src0.descriptor.duplicate(name), size=deepcopy(src0.size))
        self.set_out_info(src0.info.keys(), src0.info.values())
            
    def multByG(self, fL, fR, idsDict, explored, opts):
#         inexpr = [ e.multByG(fL, fR, idsDict, explored, opts) for e in self.inexpr ]
#         
#         res = Add(inexpr[0], inexpr[1])
#         
#         return res
        return None

    def getSignature(self):
        return self.inexpr[0].getSignature() + "_plus_" + self.inexpr[1].getSignature()

    @staticmethod
    def toPolySigma():
        return "+"

    def toEG(self): 
        return "+"
    
#     def getFlops(self):
#         c = 0
#         for e in self.inexpr:
#             c += e.getFlops()
#         outs = [ i.getOut() for i in self.inexpr ]
#         structs = [ o.getFlatPolyStructureFromIndices(['i', 'j'], o.getOrigin(), o.getFlatSize()) for o in outs ]
#         c += structs[0].get(Matrix, Set("{[i,j]:1=0}")).intersect(structs[1].get(Matrix, Set("{[i,j]:1=0}"))).count_val().to_python()
#         return c

#     def getOps(self):
#         c = 0
#         for e in self.inexpr:
#             c += e.getOps()
#         # TBA
# #         s = self.out.getFlatSize()
# #         outs = [ i.getOut() for i in self.inexpr ]
# #         structs = [ o.getFlatPolyStructureFromIndices(['i', 'j'], o.getOrigin(), o.getFlatSize()) for o in outs ]
# #         zeros = [ st.get(ZeroMatrix, Set("{[i,j]:1=0}")) for st in structs ]
# #         c += s[0]*s[1] - ( zeros[0].intersect(zeros[1]).count_val().to_python() )
#         return c

    def toLatex(self, context, ind=0, subs=None):
        l, r = self.inexpr[0].toLatex(context, ind, subs), self.inexpr[1].toLatex(context, ind, subs)
        res = l 
        if context.bindingTable.isBound(self.out) and context.bindingTable.getPhysicalLayout(self.out) is None:
            res += "$\n"
            res += ind*" " + "$+$\n"
            res += ind*" " + "$" + r
        else:
            res += " + " + r
        return res
        
    def __str__(self):
        return "( " + str(self.inexpr[0]) + " + " + str(self.inexpr[1]) + " )"

    def toLL(self, acc=False, accSign=None, sep=False):
        return "( " + self.inexpr[0].toLL() + " + " + self.inexpr[1].toLL() + " )"

    def to_algo(self, decl_map, dep_map, dims_map, expr_map, order, sizes_map, dims):
        in_list = []
        for inexpr in self.inexpr:
            in_list.append( inexpr.to_algo(decl_map, dep_map, dims_map, expr_map, order, sizes_map, dims) )
        res = "( " + in_list[0] + " + " + in_list[1] + " )"
        return res
    
    def __hash__(self):
        tin = tuple(self.inexpr)
        key = (hash('+'), hash(tin))
        return hash(key)

class Sub(SimpleOperator):
    '''
    Addition Expression.
    '''
    def __init__(self, sexpr0, sexpr1, out=None):
        super(Sub, self).__init__()
        if isinstance(sexpr0, Holonode) and isinstance(sexpr1, Holonode):
            self.buildout(out, [sexpr0.node.getOut(), sexpr1.node.getOut()])
        else:
            self.inexpr = [ sexpr0, sexpr1 ]
            self.buildout(out)
            self.setAsPred()

    def duplicate(self, prefix="", everything=True, changeOut=False, changeHandle=False):
        tIn = [ inexpr.duplicate() if isinstance(inexpr, Quantity) else inexpr.duplicate(prefix, everything, changeOut, changeHandle) for inexpr in self.inexpr ] if everything else self.inexpr
        if changeOut:
            out = None
            changeHandle = True
        else:
            out = self.out.duplicate(prefix)
        res = Sub(tIn[0], tIn[1], out)
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res

    @staticmethod
    def orderPolicy(idxInfoList, indices, order, baselevel):
        iPriority = {}
        for i in indices:
            idxInfo = filter(lambda idxInfo: i in idxInfo, idxInfoList)
            if len(idxInfo) == 0:
                p = {'t': (0,0), 's': 0, 'i': 0}
            else:
                idxInfo = idxInfo[0]
                rowIdx = any(map(lambda idxInfo: i in idxInfo and idxInfo[i][2] == 0, idxInfoList))
                colIdx = any(map(lambda idxInfo: i in idxInfo and idxInfo[i][2] == 1, idxInfoList))
                lev = idxInfo[i][1]
                if rowIdx:
                    p = {'t': (idxInfo[i][0]-lev,0), 's': 0, 'i': 0}
                elif colIdx:
                    p = {'t': (idxInfo[i][0]-lev,0), 's': 1, 'i': 0}
            t = ( p[order[0]], p[order[1]], p[order[2]] )
            iPriority[i] = t
        return iPriority

    def unrollingPolicy(self, uFs, indices, baselevel):
        idxInfoList = [ i.getOut().idxPosAndLevInfo for i in self.inexpr ] # See Quantity.computeIdxPosAndLevInfo for content
        for i in indices:
            idxInfo = filter(lambda idxInfo: i in idxInfo, idxInfoList)
            if len(idxInfo) > 0:
#                idxInfo = idxInfo[0]
                colIdx = any(map(lambda idxInfo: i in idxInfo and idxInfo[i][2] == 1, idxInfoList))
                baseIdx = all(map(lambda idxInfo: idxInfo[i][1] == baselevel if i in idxInfo else True, idxInfoList))
                if colIdx and baseIdx:
                    uFs[i].append(1)

    def buildout(self, out, src=None):
        if src is None:
            src0 = self.getInexprMat(0)
            src1 = self.getInexprMat(1)
        else:
            src0, src1 = src[0], src[1]

#         if(src0.level != src1.level):
#             exit("Expression Tree Error > Add: subexpressions have mismatching levels.")
#         
        self.set_info_no_td(src0.info.keys(), src0.info.values())
        if(not src0.sameLayout(src1)):
            exit("Expression Tree Error > Sub: Mismatching layout.")
        
        if(out):
            self.out = out
        else: 
#             self.out = src0.duplicate("d"+ str(globalSSAIndex()), o=[0,0], fL=fI(src0.size[0]), fR=fI(src0.size[1]))
            SubType = src0.__class__-src1.__class__
            name = "sub"+ str(globalSSAIndex())
            self.out = SubType(name, src0.descriptor.duplicate(name), size=deepcopy(src0.size))
        self.set_out_info(src0.info.keys(), src0.info.values())

    @staticmethod
    def toPolySigma():
        return "-"

    def toEG(self): 
        return "-"
    
#     def getOps(self):
#         c = 0
#         for e in self.inexpr:
#             c += e.getOps()
#         # TBA
# #         s = self.out.getFlatSize()
# #         outs = [ i.getOut() for i in self.inexpr ]
# #         structs = [ o.getFlatPolyStructureFromIndices(['i', 'j'], o.getOrigin(), o.getFlatSize()) for o in outs ]
# #         zeros = [ st.get(ZeroMatrix, Set("{[i,j]:1=0}")) for st in structs ]
# #         c += s[0]*s[1] - ( zeros[0].intersect(zeros[1]).count_val().to_python() )
#         return c

    def toLatex(self, context, ind=0, subs=None):
        l, r = self.inexpr[0].toLatex(context, ind, subs), self.inexpr[1].toLatex(context, ind, subs)
        res = l + " - " + r
        return res
        
    def __str__(self):
        return "( " + str(self.inexpr[0]) + " - " + str(self.inexpr[1]) + " )"

    def toLL(self, acc=False, accSign=None, sep=False):
        return "( " + self.inexpr[0].toLL() + " - " + self.inexpr[1].toLL() + " )"

    def to_algo(self, decl_map, dep_map, dims_map, expr_map, order, sizes_map, dims):
        in_list = []
        for inexpr in self.inexpr:
            in_list.append( inexpr.to_algo(decl_map, dep_map, dims_map, expr_map, order, sizes_map, dims) )
        res = "( " + in_list[0] + " - " + in_list[1] + " )"
        return res
        
    def __hash__(self):
        tin = tuple(self.inexpr)
        key = (hash('-'), hash(tin))
        return hash(key)
    
class Kro(SimpleOperator):
    '''
    Kronecker Product. (Only for sca-mat by now)
    '''
    def __init__(self, sexpr0, sexpr1, out=None):
        super(Kro, self).__init__()
        if isinstance(sexpr0, Holonode) and isinstance(sexpr1, Holonode):
            self.buildout(out, [sexpr0.node.getOut(), sexpr1.node.getOut()])
        else:
            self.inexpr = [ sexpr0, sexpr1 ]
            self.buildout(out)
            self.setAsPred()

    def duplicate(self, prefix="", everything=True, changeOut=False, changeHandle=False):
        tIn = [ inexpr.duplicate() if isinstance(inexpr, Quantity) else inexpr.duplicate(prefix, everything, changeOut, changeHandle) for inexpr in self.inexpr ] if everything else self.inexpr
        if changeOut:
            out = None
            changeHandle = True
        else:
            out = self.out.duplicate(prefix)
        res = Kro(tIn[0], tIn[1], out)
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res

    def duplicateUpToBoundaries(self, prefix="", boundaries=None, changeHandle=True):
        if boundaries is None:
            boundaries = []
        tIn = [ inexpr if (inexpr in boundaries) else inexpr.duplicateUpToBoundaries(prefix, boundaries, changeHandle) for inexpr in self.inexpr ]
        res = Kro(tIn[0], tIn[1], self.out.duplicate(prefix))
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res
            
    def buildout(self, out, src=None):
        if src is None:
            src0 = self.getInexprMat(0)
            src1 = self.getInexprMat(1)
        else:
            src0, src1 = src[0], src[1]

        self.set_info_no_td(src0.info.keys(), src0.info.values())
        if(src0.level != src1.level):
            exit("Expression Tree Error > Kro: subexpressions have mismatching levels.")
        
        if(out):
            self.out = out
        else: 
            self.out = self.__buildout(src0, src1)
        self.set_out_info(src0.info.keys(), src0.info.values())
    
    @staticmethod
    def orderPolicy(idxInfoList, indices, order, baselevel):
        iPriority = {}
        for i in indices:
            idxInfo = filter(lambda idxInfo: i in idxInfo, idxInfoList)
            if len(idxInfo) == 0:
                p = {'t': (0,0), 's': 0, 'i': 0}
            else:
                idxInfo = idxInfo[0]
                rowIdx = any(map(lambda idxInfo: i in idxInfo and idxInfo[i][2] == 0, idxInfoList))
                colIdx = any(map(lambda idxInfo: i in idxInfo and idxInfo[i][2] == 1, idxInfoList))
                lev = idxInfo[i][1]
                if rowIdx:
                    p = {'t': (idxInfo[i][0]-lev,0), 's': 0, 'i': 0}
                elif colIdx:
                    p = {'t': (idxInfo[i][0]-lev,0), 's': 1, 'i': 0}
            t = ( p[order[0]], p[order[1]], p[order[2]] )
            iPriority[i] = t
        return iPriority

    def unrollingPolicy(self, uFs, indices, baselevel):
        idxInfoList = [ i.getOut().idxPosAndLevInfo for i in self.inexpr ] # See Quantity.computeIdxPosAndLevInfo for content
        for i in indices:
            idxInfo = filter(lambda idxInfo: i in idxInfo, idxInfoList)
            if len(idxInfo) > 0:
#                idxInfo = idxInfo[0]
                colIdx = any(map(lambda idxInfo: i in idxInfo and idxInfo[i][2] == 1, idxInfoList))
                baseIdx = all(map(lambda idxInfo: idxInfo[i][1] == baselevel if i in idxInfo else True, idxInfoList))
                if colIdx and baseIdx:
                    uFs[i].append(1)

    def computeSpaceIdxNames(self, i, j, ipfix, jpfix, opts, depth=1, baselevel=2):
        p, q, ppfix, qpfix = 'p', 'q', str(globalSSAIndex()), str(globalSSAIndex())
        lin = self.inexpr[0]
        if lin.getOut().getFlatSize()[0]*lin.getOut().getFlatSize()[1] == 1:
            sca = lin
            mat = self.inexpr[1]
        else:
            sca = self.inexpr[1]
            mat = lin
        sca.computeSpaceIdxNames(p, q, ppfix, qpfix, opts, depth, baselevel)
        mat.computeSpaceIdxNames(i, j, ipfix, jpfix, opts, depth, baselevel)
        matOut = mat.getOut()
        for c in range(len(matOut.spaceIdxNames)):
            self.out.spaceIdxNames[c] = [ idx for idx in matOut.spaceIdxNames[c] ]

    def __buildout(self, src0, src1):
#         if not isinstance(src0.size[0], int) or not isinstance(src0.size[1], int) or src0.size[0]*src0.size[1] > 1:
        size = src0.getFlatSize()
        idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
#         if ((size[0]*size[1]).subs(self.info.get('min', {})) > 1 or (size[0]*size[1]).subs(self.info.get('max', {})) > 1):
        if get_expr_bound_over_domain(idcs, dom_info, size[0]*size[1], 'max') > 1:
            out = (src0.__class__).fromBlock(src0, name="kr" + str(globalSSAIndex()))
        else:
            out = (src1.__class__).fromBlock(src1, name="kr" + str(globalSSAIndex()))
        return out
#        size=(src0.size[0]*src1.size[0], src0.size[1]*src1.size[1])
#        return Matrix("k" + str(globalSSAIndex()), scalar, size)

#     def getOps(self):
#         c = 0
#         for e in self.inexpr:
#             c += e.getOps()
#         # TBA
# #         matOut = filter(lambda i: not i.getOut().isScalar(), self.inexpr)[0].getOut()
# #         struct = matOut.getFlatPolyStructureFromIndices(['i', 'j'], matOut.getOrigin(), matOut.getFlatSize())
# #         c += struct.get(Matrix, Set("{[i,j]:1=0}")).count_val().to_python()
#         return c
    
    def __repr__(self):
        return "Kro( " + repr(self.inexpr[0]) + ", " + repr(self.inexpr[1]) + " )"

    def __str__(self):
        return "( " + str(self.inexpr[0]) + " Kro " + str(self.inexpr[1]) + " )"

    def toLL(self, acc=False, accSign=None, sep=False):
        return "( " + self.inexpr[0].toLL() + " * " + self.inexpr[1].toLL() + " )"

    def to_algo(self, decl_map, dep_map, dims_map, expr_map, order, sizes_map, dims):
        in_list = []
        for inexpr in self.inexpr:
            in_list.append( inexpr.to_algo(decl_map, dep_map, dims_map, expr_map, order, sizes_map, dims) )
        res = "( " + in_list[0] + " * " + in_list[1] + " )"
        return res
    
    def toLatex(self, context, ind=0, subs=None):
        l, r = self.inexpr[0].toLatex(context, ind, subs), self.inexpr[1].toLatex(context, ind, subs)
        if not ( any( map(lambda cls: isinstance(self.inexpr[0], cls), [Quantity, NewContextOperator]) ) \
                 or isinstance(self.inexpr[0], Quantity) and self.inexpr[0].isScalar() ):
            l = "(" + l + ")"   
        if not ( any( map(lambda cls: isinstance(self.inexpr[1], cls), [Quantity, NewContextOperator]) ) \
                 or isinstance(self.inexpr[1], Quantity) and self.inexpr[1].isScalar() ):
            r = "(" + r + ")"   
        res = l + r
        return res

    @staticmethod
    def toPolySigma():
        return "*"

    def toEG(self): 
        return "*"

    def __hash__(self):
        tin = tuple(self.inexpr)
        key = (hash('kr*'), hash(tin))
        return hash(key)
    
#     def __eq__(self, other):
#         if not isinstance(other, Kro):
#             return False
# #         if self.handle != other.handle:
# #             return False
#         for e,o in zip(self.inexpr, other.inexpr):
#             if e != o:
#                 return False
#         return True
# 
#     def __ne__(self, other):
#         return not self.__eq__(other)
    

class Mul(SimpleOperator):
    '''
    Multiplication Expression.
    '''
    def __init__(self, sexpr0, sexpr1, out=None, setAsPred=True):
        super(Mul, self).__init__()
        if isinstance(sexpr0, Holonode) and isinstance(sexpr1, Holonode):
            self.buildout(out, [sexpr0.node.getOut(), sexpr1.node.getOut()])
        else:
            self.inexpr = [ sexpr0, sexpr1 ]
            self.buildout(out)
            if setAsPred:
                self.setAsPred()

    def duplicate(self, prefix="", everything=True, changeOut=False, changeHandle=False):
        tIn = [ inexpr.duplicate() if isinstance(inexpr, Quantity) else inexpr.duplicate(prefix, everything, changeOut, changeHandle) for inexpr in self.inexpr ] if everything else self.inexpr
        if changeOut:
            out = None
            changeHandle = True
        else:
            out = self.out.duplicate(prefix)
        res = Mul(tIn[0], tIn[1], out)
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res

    def duplicateUpToBoundaries(self, prefix="", boundaries=None, changeHandle=True):
        if boundaries is None:
            boundaries = []
        tIn = [ inexpr if (inexpr in boundaries) else inexpr.duplicateUpToBoundaries(prefix, boundaries, changeHandle) for inexpr in self.inexpr ]
        res = Mul(tIn[0], tIn[1], self.out.duplicate(prefix))
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res
    
    @staticmethod
    def orderPolicy(idxInfoList, indices, order, baselevel):
        kTlocPrior = lambda lev: 0 if lev == baselevel+1 else 2 
        jSlocPrior = lambda lev: 0 if lev == baselevel+1 else 2
        kSlocPrior = lambda lev: 0 if lev == baselevel+1 else 1
        ijIlpPrior = lambda lev: 1 if lev == baselevel+1 else 0
        iPriority = {}
        for i in indices:
            idxInfo = filter(lambda idxInfo: i in idxInfo, idxInfoList)
            if len(idxInfo) == 0:
                p = {'t': (0,0), 's': 0, 'i': 0}
            else:
                idxInfo = idxInfo[0]
                rowIdx = any(map(lambda idxInfo: i in idxInfo and idxInfo[i][2] == 0, idxInfoList))
                colIdx = any(map(lambda idxInfo: i in idxInfo and idxInfo[i][2] == 1, idxInfoList))
                lev = idxInfo[i][1]
                if rowIdx and colIdx:
                    p = {'t': (idxInfo[i][0]-lev, kTlocPrior(lev)), 's': kSlocPrior(lev), 'i': 0}
                elif rowIdx:
                    p = {'t': (idxInfo[i][0]-lev, 0), 's': 1, 'i': ijIlpPrior(lev)}
                elif colIdx:
                    p = {'t': (idxInfo[i][0]-lev, 1), 's': jSlocPrior(lev), 'i': ijIlpPrior(lev)}
            t = ( p[order[0]], p[order[1]], p[order[2]] )
            iPriority[i] = t
        return iPriority

    def unrollingPolicy(self, uFs, indices, baselevel):
        idxInfoList = [ i.getOut().idxPosAndLevInfo for i in self.inexpr ] # See Quantity.computeIdxPosAndLevInfo for content
        for i in indices:
            idxInfo = filter(lambda idxInfo: i in idxInfo, idxInfoList)
            if len(idxInfo) > 0:
#                idxInfo = idxInfo[0]
#                 rowIdx = any(map(lambda idxInfo: i in idxInfo and idxInfo[i][2] == 0, idxInfoList))
#                 colIdx = any(map(lambda idxInfo: i in idxInfo and idxInfo[i][2] == 1, idxInfoList))
                baseIdx = all(map(lambda idxInfo: idxInfo[i][1] == baselevel if i in idxInfo else True, idxInfoList))
#                 if rowIdx and colIdx and baseIdx:
                if baseIdx:
                    uFs[i].append(1)
#                 
#                 if idxInfo[i][1] == baselevel:
#                     uFs[i].append(sys.maxint)
#                 else:
#                     uFs[i].append(1)

    def buildout(self, out, src=None):
        if src is None:
            src0 = self.getInexprMat(0)
            src1 = self.getInexprMat(1)
        else:
            src0, src1 = src[0], src[1]
        
        self.set_info_no_td(src0.info.keys(), src0.info.values())
        if(src0.level != src1.level):
            exit("Expression Tree Error > Mul: subexpressions have mismatching levels.")
        
        if(not self.checkConformity(src0, src1)):
            #If it gets here it must be scalar mismatch
            exit("Expression Tree Error > Mul: checkConformity at level 1. Scalar mismatch.")
        
        if(out):
            self.out = out
        else: 
            self.out = self.__buildout(src0, src1)
        self.set_out_info(src0.info.keys(), src0.info.values())
    
    def checkConformity(self, src0, src1):
        if (src0 is None or src1 is None) and src0 != src1:
            return False
        elif src0 is None and src1 is None:
            return True
        if(src0.level == 1): # Scalar conformity
            return src0.name == src1.name
        
        desc0 = src0.descriptor
        desc1 = src1.descriptor
        
        if(desc0.getNumColPartitions() != desc1.getNumRowPartitions()):
            exit("Expression Tree Error > Mul: checkConformity at level " + str(src0.level) + ". ColParts in RowPart0 != RowParts in src1_desc.")
        
        for i in range(desc1.getNumRowPartitions()):
            if(desc0.getColsOfPartition(i) != desc1.getRowsOfPartition(i)):
                exit("Expression Tree Error > Mul: checkConformity at level " + str(src0.level) + ". ColsPerPart in RowPart0 != RowsPerPart in src1_desc.")
        
        for i in range(desc1.getNumRowPartitions()):
            if(not self.checkConformity(desc0.getBlockOfPartition(0,i), desc1.getBlockOfPartition(i, 0))):
                exit("Expression Tree Error > Mul: checkConformity at level " + str(src0.level) + ". Nonconforming Blocks at index " + str(i))
        
        return True
        
    def __buildout(self, src0, src1):
        
        if(src0.level == 1):
            return src0
        
        desc = self.__buildblock(src0, src1).descriptor
        matCls = src0.__class__*src1.__class__
#        if desc.getSize()[0] == desc.getSize()[1]:
#            if isinstance(self.inexpr[0], T):
#                matCls = Symmetric if self.inexpr[0].inexpr[0].sameUpToNames(self.inexpr[1]) else matCls
#            elif isinstance(self.inexpr[1], T):
#                matCls = Symmetric if self.inexpr[0].sameUpToNames(self.inexpr[1].inexpr[0]) else matCls
        return (matCls)("m" + str(globalSSAIndex()), desc, desc.getSize())

    def __buildblock(self, b0, b1):
        
        if(b0.level == 1):
            return b0
            
        desc0 = b0.descriptor
        desc1 = b1.descriptor
        desc = Descriptor(desc0.level)
        desc.set_info(self.info.keys(), self.info.values())
        
        listRowParts = []
        for rowPart_d0 in desc0.rows:
            newRowPart = RowPartition(rowPart_d0.nRows, info=self.info)
            B0 = rowPart_d0.getBlockOfPartition(0)
            listColParts = []
            for j in range(desc1.getNumColPartitions()):
                newColPart = ColPartition(desc1.getColsOfPartition(j), self.__buildblock(B0, desc1.getBlockOfPartition(0,j)), self.info)
                listColParts += [newColPart]
            newRowPart.addCols(listColParts)
            listRowParts += [newRowPart]
        
        desc.addRows(listRowParts)
        return Block("", desc, desc.getSize())

    def multByG(self, fL, fR, idsDict, explored, opts):
#         
#         n = self.getInexprMat(0).size[1]
#         innerf = fI(n)
#         
#         in0 = self.inexpr[0].multByG(fL, innerf, idsDict, explored, opts)
#         in1 = self.inexpr[1].multByG(innerf, fR, idsDict, explored, opts)
#         
# #         res = Mul(in0, in1)
#         res = (in0*in1)
#         
#         return res
        return None

    def computeSpaceIdxNames(self, i, j, ipfix, jpfix, opts, depth=1, baselevel=2):
        k, kpfix = 'k', str(globalSSAIndex())
        self.inexpr[0].computeSpaceIdxNames(i, k, ipfix, kpfix, opts, depth, baselevel)
        self.inexpr[1].computeSpaceIdxNames(k, j, kpfix, jpfix, opts, depth, baselevel)
        self.out.spaceIdxNames[0] = [ idx for idx in self.inexpr[0].getOut().spaceIdxNames[0] ]
        self.out.spaceIdxNames[1] = [ idx for idx in self.inexpr[1].getOut().spaceIdxNames[1] ]

#     def getSpaceIdxSet(self, i, j, ipfix, jpfix, depth, baselevel=2):
#         k, kpfix = 'k', str(globalSSAIndex())
#         ret = self.inexpr[0].getSpaceIdxSet(i, k, ipfix, kpfix, depth, baselevel).union(self.inexpr[1].getSpaceIdxSet(k, j, kpfix, jpfix, depth, baselevel))
#         return ret
            
    def getSignature(self):
        return self.inexpr[0].getSignature() + "_times_" + self.inexpr[1].getSignature()

    @staticmethod
    def toPolySigma():
        return "*"

    def toEG(self): 
        return "*"

#     def getOps(self):
#         c = 0
#         for e in self.inexpr:
#             c += e.getOps()
#         # TBA
# #         outs = [ i.getOut() for i in self.inexpr ]
# #         s0 = outs[0].getFlatPolyStructureFromIndices(['i', 'k'], outs[0].getOrigin(), outs[0].getFlatSize())
# #         s1 = outs[1].getFlatPolyStructureFromIndices(['k', 'j'], outs[1].getOrigin(), outs[1].getFlatSize())
# #         m0 = s0.get(Matrix, Set("{[i,k]: 1=0}"))
# #         m1 = s1.get(Matrix, Set("{[k,j]: 1=0}"))
# #         m0 = m0.insert_dims(dim_type.set, 2, 1).set_dim_name(dim_type.set, 2, 'j')
# #         m1 = m1.insert_dims(dim_type.set, 0, 1).set_dim_name(dim_type.set, 0, 'i')
# #         tot = m0.intersect(m1)
# #         init = tot.project_out(dim_type.set, 1, 1)
# #         c += (2*tot.count_val().to_python() - init.count_val().to_python())
#         return c
    
    def toLatex(self, context, ind=0, subs=None):
        l, r = self.inexpr[0].toLatex(context, ind, subs), self.inexpr[1].toLatex(context, ind, subs)
        if not isinstance(self.inexpr[0], Quantity):
            l = "(" + l + ")"
        if not isinstance(self.inexpr[1], Quantity):
            r = "(" + r + ")"
        res = l + r
        return res
    
    def __str__(self):
        return "( " + str(self.inexpr[0]) + " * " + str(self.inexpr[1]) + " )"

    def toLL(self, acc=False, accSign=None, sep=False):
        return "( " + self.inexpr[0].toLL() + " * " + self.inexpr[1].toLL() + " )"

    def to_algo(self, decl_map, dep_map, dims_map, expr_map, order, sizes_map, dims):
        in_list = []
        local_dims0 = [dims[0], None]
        in_list.append( self.inexpr[0].to_algo(decl_map, dep_map, dims_map, expr_map, order, sizes_map, local_dims0) )
        local_dims1 = [local_dims0[1], dims[1]]
        in_list.append( self.inexpr[1].to_algo(decl_map, dep_map, dims_map, expr_map, order, sizes_map, local_dims1) )
        dims[0] = local_dims0[0] 
        dims[1] = local_dims1[1] 
        res = "( " + in_list[0] + " * " + in_list[1] + " )"
        return res    

    def __hash__(self):
        tin = tuple(self.inexpr)
        key = (hash('*'), hash(tin))
        return hash(key)
    
#     def __eq__(self, other):
#         if not isinstance(other, Mul):
#             return False
# #         if self.handle != other.handle:
# #             return False
#         for e,o in zip(self.inexpr, other.inexpr):
#             if e != o:
#                 return False
#         return True
# 
#     def __ne__(self, other):
#         return not self.__eq__(other)

class LDivBase(SimpleOperator):
    '''
    LDiv Expression.
    '''
    def __init__(self, sexpr0, sexpr1, out=None):
        super(LDivBase, self).__init__()
        if isinstance(sexpr0, Holonode) and isinstance(sexpr1, Holonode):
            self.buildout(out, [sexpr0.node.getOut(), sexpr1.node.getOut()])
        else:
            self.inexpr = [ sexpr0, sexpr1 ]
            self.buildout(out)
            self.setAsPred()
        
    def buildout(self, out, src=None):
        if src is None:
            src0 = self.getInexprMat(0)
            src1 = self.getInexprMat(1)
        else:
            src0, src1 = src[0], src[1]
        
        self.set_info_no_td(src0.info.keys(), src0.info.values())
        if(src0.level != src1.level):
            exit("Expression Tree Error > LDiv: subexpressions have mismatching levels.")
        
        if(not self.checkConformity(src0, src1)):
            #If it gets here it must be scalar mismatch
            exit("Expression Tree Error > LDiv: checkConformity at level 1. Scalar mismatch.")
        
        if(out):
            self.out = out
        else: 
            self.out = self.__buildout(src0, src1)
        self.set_out_info(src0.info.keys(), src0.info.values())
        
    def duplicate(self, prefix="", everything=True, changeOut=False, changeHandle=False):
        tIn = [ inexpr.duplicate() if isinstance(inexpr, Quantity) else inexpr.duplicate(prefix, everything, changeOut, changeHandle) for inexpr in self.inexpr ] if everything else self.inexpr
        if changeOut:
            out = None
            changeHandle = True
        else:
            out = self.out.duplicate(prefix)
        res = self.__class__(tIn[0], tIn[1], out)
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res
        
    def checkConformity(self, src0, src1):
        if(src0.level == 1): # Scalar conformity
            return src0.name == src1.name
        
        desc0 = src0.descriptor
        desc1 = src1.descriptor
        
        if(desc0.getNumRowPartitions() != desc1.getNumRowPartitions()):
            exit("Expression Tree Error > LDiv: checkConformity at level " + str(src0.level) + ". RowParts don't match.")
        
        for i in range(desc1.getNumRowPartitions()):
            if(desc0.getRowsOfPartition(i) != desc1.getRowsOfPartition(i)):
                exit("Expression Tree Error > LDiv: checkConformity at level " + str(src0.level) + ". RowsPerPart don't match.")
        
        for i in range(desc1.getNumRowPartitions()):
            if(not self.checkConformity(desc0.getBlockOfPartition(i, 0), desc1.getBlockOfPartition(i, 0))):
                exit("Expression Tree Error > LDiv: checkConformity at level " + str(src0.level) + ". Nonconforming Blocks at index " + str(i))
        
        return True

    def __buildout(self, src0, src1):
        
        if(src0.level == 1):
            return src0
        
        desc = self.__buildblock(src0, src1).descriptor
#         return (src0.__class__.ldiv(src1.__class__))("ld" + str(globalSSAIndex()), desc, desc.getSize())
        return Matrix("ld" + str(globalSSAIndex()), desc, desc.getSize())

    def __buildblock(self, b0, b1):
        
        if(b0.level == 1):
            return b0
            
#         desc0 = b0.descriptor
#         desc1 = b1.descriptor
#         desc = Descriptor(desc0.level)
#         desc.set_info(self.info.keys(), self.info.values())
#         
#         listRowParts = []
#         rowPart0_d0 = desc0.rows[0]
#         rowPart0_d1 = desc1.rows[0]
#         for i in range(rowPart0_d0.getNumColPartitions()):
#             newRowPart = RowPartition(rowPart0_d0.getColsOfPartition(i), self.info)
#             B0 = rowPart0_d0.getBlockOfPartition(0)
#             
#         
#         for rowPart_d0 in desc0.rows:
#             newRowPart = RowPartition(rowPart_d0.nRows, self.info)
#             B0 = rowPart_d0.getBlockOfPartition(i)
#             listColParts = []
#             for j in range(rowPart0_d1.getNumColPartitions()):
#                 newColPart = ColPartition(rowPart0_d1.getColsOfPartition(j), self.__buildblock(B0, rowPart0_d1.getBlockOfPartition(j)), self.info)
#                 listColParts += [newColPart]
#             newRowPart.addCols(listColParts)
#             listRowParts += [newRowPart]
#         
#         desc.addRows(listRowParts)
#         return Block("", desc, desc.getSize())

        desc0 = b0.descriptor
        desc1 = b1.descriptor
        desc = Descriptor(desc0.level)
        desc.set_info(self.info.keys(), self.info.values())
        
        listRowParts = []
        col_list = [] if not desc0.rows else desc0.rows[0].cols
        for colPart_d0 in col_list:
            newRowPart = RowPartition(colPart_d0.nCols, info=self.info)
            B0 = colPart_d0.block
            listColParts = []
            for j in range(desc1.getNumColPartitions()):
                newColPart = ColPartition(desc1.getColsOfPartition(j), self.__buildblock(B0, desc1.getBlockOfPartition(0,j)), self.info)
                listColParts += [newColPart]
            newRowPart.addCols(listColParts)
            listRowParts += [newRowPart]
        
        desc.addRows(listRowParts)
        return Block("", desc, desc.getSize())

    def getSignature(self):
        return self.inexpr[0].getSignature() + "_ldiv_" + self.inexpr[1].getSignature()

    @staticmethod
    def toPolySigma():
        return "\\"

    def toEG(self): 
        return "\\"

    def toLL(self, acc=False, accSign=None, sep=False):
        return "( " + self.inexpr[0].toLL() + " \\ " + self.inexpr[1].toLL() + " )"

#     def getOps(self):
#         c = 0
#         for e in self.inexpr:
#             c += e.getOps()
#         # if B is L -> ops = M^3/3 + M^2/2 + M/6
#         # if B is Matrix -> ops = N*M^2
# 
#         # TBA
# #         s1 = self.inexpr[1].getOut().getFlatSize()
# #         if self.inexpr[0].getOut().__class__ == self.inexpr[1].getOut().__class__: 
# #             c += s1[0]*(2*s1[0]**2 + 3*s1[0] + 1)/6
# #         else:
# #             c += s1[1]*s1[0]**2
#         return c
    
    def toLatex(self, context, ind=0, subs=None):
        l, r = self.inexpr[0].toLatex(context, ind, subs), self.inexpr[1].toLatex(context, ind, subs)
        if not isinstance(self.inexpr[0], Quantity):
            l = "(" + l + ")"   
        if not isinstance(self.inexpr[1], Quantity):
            r = "(" + r + ")"   
        res = l + "\\backslash " + r
        return res
    
    def __str__(self):
        return "( " + str(self.inexpr[0]) + " \\ " + str(self.inexpr[1]) + " )"

    def __hash__(self):
        tin = tuple(self.inexpr)
        key = (hash('\\'), hash(tin))
        return hash(key)

    @staticmethod
    def orderPolicy(idxInfoList, indices, order, baselevel):
        iPriority = {}
        for i in indices:
            idxInfo = filter(lambda idxInfo: i in idxInfo, idxInfoList)
            if len(idxInfo) == 0:
                p = {'t': (0,0), 's': 0, 'i': 0}
            else:
                idxInfo = idxInfo[0]
                rowIdx = any(map(lambda idxInfo: i in idxInfo and idxInfo[i][2] == 0, idxInfoList))
                colIdx = any(map(lambda idxInfo: i in idxInfo and idxInfo[i][2] == 1, idxInfoList))
                lev = idxInfo[i][1]
                if rowIdx and not colIdx:
                    p = {'t': (idxInfo[i][0]-lev, 0), 's': 1, 'i': 1} # Triang matrix diagonal
                elif rowIdx and colIdx:
                    p = {'t': (idxInfo[i][0]-lev, 0), 's': 0, 'i': 0} 
                else:
                    p = {'t': (idxInfo[i][0]-lev, 0), 's': 2, 'i': 2}
            t = ( p[order[0]], p[order[1]], p[order[2]] )
            iPriority[i] = t
        return iPriority

    def unrollingPolicy(self, uFs, indices, baselevel):
        idxInfoList = [ i.getOut().idxPosAndLevInfo for i in self.inexpr ]# +  [ self.getOut().idxPosAndLevInfo ]# See Quantity.computeIdxPosAndLevInfo for content
        for i in indices:
            idxInfo = filter(lambda idxInfo: i in idxInfo, idxInfoList)
            if len(idxInfo) > 0:
#                idxInfo = idxInfo[0]
#                 rowIdx = any(map(lambda idxInfo: i in idxInfo and idxInfo[i][2] == 0, idxInfoList))
#                 colIdx = any(map(lambda idxInfo: i in idxInfo and idxInfo[i][2] == 1, idxInfoList))
                baseIdx = all(map(lambda idxInfo: idxInfo[i][1] == baselevel if i in idxInfo else True, idxInfoList))
                if baseIdx:
                    uFs[i].append(1)

class LDiv1(LDivBase):

    def __init__(self, sexpr0, sexpr1, out=None):
        super(LDiv1, self).__init__(sexpr0, sexpr1, out)

    def computeSpaceIdxNames(self, i, j, ipfix, jpfix, opts, depth=1, baselevel=2):
        k, kpfix = 'k', str(globalSSAIndex())
        self.inexpr[0].computeSpaceIdxNames(k, i, kpfix, ipfix, opts, depth, baselevel)
        self.inexpr[1].computeSpaceIdxNames(k, j, kpfix, jpfix, opts, depth, baselevel)
        opts['idsattr'][k] = 'f'
        self.out.spaceIdxNames[0] = [ idx for idx in self.inexpr[0].getOut().spaceIdxNames[1] ]
        self.out.spaceIdxNames[1] = [ idx for idx in self.inexpr[1].getOut().spaceIdxNames[1] ]

    def computeIdxPriority(self, idxPriorityList, indices, order, baselevel):
        for i in self.inexpr:
            if isinstance(i, Operator):
                i.computeIdxPriority(idxPriorityList, indices, order, baselevel)
        idxInfoList = [ i.getOut().idxPosAndLevInfo for i in self.inexpr ] + [ self.getOut().idxPosAndLevInfo ]# See Quantity.computeIdxPosAndLevInfo for content
        iPriority = self.orderPolicy(idxInfoList, indices, order, baselevel)
        idxPriorityList.append(iPriority)

class LDiv2(LDivBase):

    def __init__(self, sexpr0, sexpr1, out=None):
        super(LDiv2, self).__init__(sexpr0, sexpr1, out)

    def computeSpaceIdxNames(self, i, j, ipfix, jpfix, opts, depth=1, baselevel=2):
        k, kpfix = 'k', str(globalSSAIndex())
        self.inexpr[0].computeSpaceIdxNames(k, i, kpfix, ipfix, opts, depth, baselevel)
        self.inexpr[1].computeSpaceIdxNames(k, j, kpfix, jpfix, opts, depth, baselevel)
        opts['idsattr'][k] = 'f'
        self.out.spaceIdxNames[0] = [ idx for idx in self.inexpr[0].getOut().spaceIdxNames[1] ]
        self.out.spaceIdxNames[1] = [ idx for idx in self.inexpr[1].getOut().spaceIdxNames[1] ]

        self.suppExpr = self.inexpr[1].duplicate() - self.inexpr[0].duplicate()*self.out.duplicate()
        l, r, lpfix, rpfix = 'l', 'r', str(globalSSAIndex()), str(globalSSAIndex())
        mul = self.suppExpr.inexpr[1]
        self.suppExpr.inexpr[0].computeSpaceIdxNames(l, r, lpfix, rpfix, opts, depth, baselevel)
        mul.inexpr[0].computeSpaceIdxNames(l, i, lpfix, ipfix, opts, depth, baselevel)
        mul.inexpr[1].computeSpaceIdxNames(i, r, ipfix, rpfix, opts, depth, baselevel)
        self.suppExpr.out.spaceIdxNames[0] = [ idx for idx in self.suppExpr.inexpr[0].getOut().spaceIdxNames[0] ]
        self.suppExpr.out.spaceIdxNames[1] = [ idx for idx in self.suppExpr.inexpr[0].getOut().spaceIdxNames[1] ]
        

    def computeIdxPosAndLevInfo(self):
        super(LDiv2, self).computeIdxPosAndLevInfo()
        self.suppExpr.computeIdxPosAndLevInfo()
        
    def getSpaceIdxSet(self):
        ret = super(LDiv2, self).getSpaceIdxSet()
        ret = ret.union(self.suppExpr.getSpaceIdxSet())
        return ret
        
    def computeIdxPriority(self, idxPriorityList, indices, order, baselevel):
        for i in self.inexpr:
            if isinstance(i, Operator):
                i.computeIdxPriority(idxPriorityList, indices, order, baselevel)
        idxInfoList = [ i.getOut().idxPosAndLevInfo for i in self.inexpr ] + [ self.getOut().idxPosAndLevInfo ] # See Quantity.computeIdxPosAndLevInfo for content
        iPriority = self.orderPolicy(idxInfoList, indices, order, baselevel)
        idxPriorityList.append(iPriority)
        idxInfoList = [ i.getOut().idxPosAndLevInfo for i in self.suppExpr.inexpr ]
        iPriority = Mul.orderPolicy(idxInfoList, indices, order, baselevel)
        idxPriorityList.append(iPriority)

    def computeUnrolling(self, uFs, indices, baselevel):
        super(LDiv2, self).computeUnrolling(uFs, indices, baselevel)
        self.suppExpr.unrollingPolicy(uFs, indices, baselevel)

    def markProperties(self, propDict, propList, indices, baselevel):
        super(LDiv2, self).markProperties(propDict, propList, indices, baselevel)
        self.suppExpr.checkProperties(propDict, propList, indices, baselevel)

class LDiv(LDiv1):
# class LDiv(LDiv2):
    pass    

class RDiv(SimpleOperator):
    '''
    RDiv Expression.
    '''
    def __init__(self, sexpr0, sexpr1, out=None):
        super(RDiv, self).__init__()
        if isinstance(sexpr0, Holonode) and isinstance(sexpr1, Holonode):
            self.buildout(out, [sexpr0.node.getOut(), sexpr1.node.getOut()])
        else:
            self.inexpr = [ sexpr0, sexpr1 ]
            self.buildout(out)
            self.setAsPred()
        
    def buildout(self, out, src=None):
        if src is None:
            src0 = self.getInexprMat(0)
            src1 = self.getInexprMat(1)
        else:
            src0, src1 = src[0], src[1]
        
        self.set_info_no_td(src0.info.keys(), src0.info.values())
        if(src0.level != src1.level):
            exit("Expression Tree Error > "+self.__class__.__name__+": subexpressions have mismatching levels.")
        
        if(not self.checkConformity(src0, src1)):
            #If it gets here it must be scalar mismatch
            exit("Expression Tree Error > "+self.__class__.__name__+": checkConformity at level 1. Scalar mismatch.")
        
        if(out):
            self.out = out
        else: 
            self.out = self.__buildout(src0, src1)
        self.set_out_info(src0.info.keys(), src0.info.values())
        
    def duplicate(self, prefix="", everything=True, changeOut=False, changeHandle=False):
        tIn = [ inexpr.duplicate() if isinstance(inexpr, Quantity) else inexpr.duplicate(prefix, everything, changeOut, changeHandle) for inexpr in self.inexpr ] if everything else self.inexpr
        if changeOut:
            out = None
            changeHandle = True
        else:
            out = self.out.duplicate(prefix)
        res = self.__class__(tIn[0], tIn[1], out)
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res
        
    def checkConformity(self, src0, src1):
        if(src0.level == 1): # Scalar conformity
            return src0.name == src1.name
        
        desc0 = src0.descriptor
        desc1 = src1.descriptor
        
        idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
        f = lambda val: get_expr_bound_over_domain(idcs, dom_info, val, 'min')
        
        if(f(desc0.getNumColPartitions()) != f(desc1.getNumColPartitions())):
            exit("Expression Tree Error > "+self.__class__.__name__+": checkConformity at level " + str(src0.level) + ". ColParts don't match.")
        
        for i in range(desc0.getNumColPartitions()):
            if(f(desc0.getColsOfPartition(i)) != f(desc1.getColsOfPartition(i))):
                exit("Expression Tree Error > "+self.__class__.__name__+": checkConformity at level " + str(src0.level) + ". ColsPerPart don't match.")
        
        for i in range(desc0.getNumColPartitions()):
            if(not self.checkConformity(desc0.getBlockOfPartition(0, i), desc1.getBlockOfPartition(0, i))):
                exit("Expression Tree Error > "+self.__class__.__name__+": checkConformity at level " + str(src0.level) + ". Nonconforming Blocks at index " + str(i))
        
        return True

    def __buildout(self, src0, src1):
        
        if(src0.level == 1):
            return src0
        
        desc = self.__buildblock(src0, src1).descriptor
        if src0.isScalar() and src1.isScalar():
#             return (src0.__class__)("rd" + str(globalSSAIndex()), desc, desc.getSize())
            return Scalar("rd" + str(globalSSAIndex()), desc)
        return (src0.__class__.rdiv(src1.__class__))("rd" + str(globalSSAIndex()), desc, desc.getSize())

    def __buildblock(self, b0, b1):
        
        if(b0.level == 1):
            return b0
            
        desc0 = b0.descriptor
        desc1 = b1.descriptor
        desc = Descriptor(desc0.level)
        desc.set_info(self.info.keys(), self.info.values())
        
        listRowParts = []
        for i in range(desc0.getNumRowPartitions()):
            newRowPart = RowPartition(desc0.getRowsOfPartition(i), info=self.info)
            B0 = desc0.getBlockOfPartition(i,0)
            listColParts = []
            for j in range(desc1.getNumRowPartitions()):
                newColPart = ColPartition(desc1.getRowsOfPartition(j), self.__buildblock(B0, desc1.getBlockOfPartition(j,0)), self.info)
                listColParts += [newColPart]
            newRowPart.addCols(listColParts)
            listRowParts += [newRowPart]
        
        desc.addRows(listRowParts)
        return Block("", desc, desc.getSize())

    @staticmethod
    def orderPolicy(idxInfoList, indices, order, baselevel):
        iPriority = {}
        for i in indices:
#             idxInfo = filter(lambda idxInfo: i in idxInfo, idxInfoList)
#             if len(idxInfo) == 0:
            p = {'t': (0,0), 's': 0, 'i': 0}
#             else:
#                 idxInfo = idxInfo[0]
#                 lev = idxInfo[i][1]
#                 p = {'t': (idxInfo[i][0]-lev,0), 's': 0, 'i': 0}
            t = ( p[order[0]], p[order[1]], p[order[2]] )
            iPriority[i] = t
        return iPriority

    def computeSpaceIdxNames(self, i, j, ipfix, jpfix, opts, depth=1, baselevel=2):
        k, kpfix = 'k', str(globalSSAIndex())
        self.inexpr[0].computeSpaceIdxNames(i, k, ipfix, kpfix, opts, depth, baselevel)
        self.inexpr[1].computeSpaceIdxNames(j, k, jpfix, kpfix, opts, depth, baselevel)
        self.out.spaceIdxNames[0] = [ idx for idx in self.inexpr[0].getOut().spaceIdxNames[0] ]
        self.out.spaceIdxNames[1] = [ idx for idx in self.inexpr[1].getOut().spaceIdxNames[0] ]

    def getSignature(self):
        return self.inexpr[0].getSignature() + "_rdiv_" + self.inexpr[1].getSignature()

    @staticmethod
    def toPolySigma():
        return "/"

    def toEG(self): 
        return "/"

#     def getOps(self):
#         c = 0
#         for e in self.inexpr:
#             c += e.getOps()
#         # if B is L -> ops = M^3/3 + M^2/2 + M/6
#         # if B is Matrix -> ops = N*M^2
# 
#         # TBA
# #         s1 = self.inexpr[1].getOut().getFlatSize()
# #         if self.inexpr[0].getOut().__class__ == self.inexpr[1].getOut().__class__: 
# #             c += s1[0]*(2*s1[0]**2 + 3*s1[0] + 1)/6
# #         else:
# #             c += s1[1]*s1[0]**2
#         return c
    
    def toLatex(self, context, ind=0, subs=None):
        l, r = self.inexpr[0].toLatex(context, ind, subs), self.inexpr[1].toLatex(context, ind, subs)
        if not isinstance(self.inexpr[0], Quantity):
            l = "(" + l + ")"   
        if not isinstance(self.inexpr[1], Quantity):
            r = "(" + r + ")"   
        res = l + " / " + r
        return res
    
    def __str__(self):
        return "( " + str(self.inexpr[0]) + " / " + str(self.inexpr[1]) + " )"

    def toLL(self, acc=False, accSign=None, sep=False):
        return "( " + self.inexpr[0].toLL() + " / " + self.inexpr[1].toLL() + " )"

    def __hash__(self):
        tin = tuple(self.inexpr)
        key = (hash('/'), hash(tin))
        return hash(key)

# class Div(RDiv):
#     pass

class Div(SimpleOperator):
    '''
    Pointwise Division
    '''
    def __init__(self, sexpr0, sexpr1, out=None):
        super(Div, self).__init__()
        if isinstance(sexpr0, Holonode) and isinstance(sexpr1, Holonode):
            self.buildout(out, [sexpr0.node.getOut(), sexpr1.node.getOut()])
        else:
            self.inexpr = [ sexpr0, sexpr1 ]
            self.buildout(out)
            self.setAsPred()

    def duplicate(self, prefix="", everything=True, changeOut=False, changeHandle=False):
        tIn = [ inexpr.duplicate() if isinstance(inexpr, Quantity) else inexpr.duplicate(prefix, everything, changeOut, changeHandle) for inexpr in self.inexpr ] if everything else self.inexpr
        if changeOut:
            out = None
            changeHandle = True
        else:
            out = self.out.duplicate(prefix)
        res = Div(tIn[0], tIn[1], out)
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res

    def duplicateUpToBoundaries(self, prefix="", boundaries=None, changeHandle=True):
        if boundaries is None:
            boundaries = []
        tIn = [ inexpr if (inexpr in boundaries) else inexpr.duplicateUpToBoundaries(prefix, boundaries, changeHandle) for inexpr in self.inexpr ]
        res = Div(tIn[0], tIn[1], self.out.duplicate(prefix))
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res
            
    def buildout(self, out, src=None):
        if src is None:
            src0 = self.getInexprMat(0)
            src1 = self.getInexprMat(1)
        else:
            src0, src1 = src[0], src[1]

        self.set_info_no_td(src0.info.keys(), src0.info.values())
        if(src0.level != src1.level):
            exit("Expression Tree Error > PwDiv: subexpressions have mismatching levels.")
        
        if(out):
            self.out = out
        else: 
            self.out = self.__buildout(src0, src1)
        self.set_out_info(src0.info.keys(), src0.info.values())

    def __buildout(self, src0, src1):
        size = src0.getFlatSize()
        idcs, dom_info = self.info.get('indices', []), self.info.get('polytope', Set("{[]}"))
        if get_expr_bound_over_domain(idcs, dom_info, size[0]*size[1], 'max') > 1:
            out = (src0.__class__).fromBlock(src0, name="pwd" + str(globalSSAIndex()))
        else:
            out = (src1.__class__).fromBlock(src1, name="pwd" + str(globalSSAIndex()))
        return out
    
    def computeSpaceIdxNames(self, i, j, ipfix, jpfix, opts, depth=1, baselevel=2):
        p, q, ppfix, qpfix = 'p', 'q', str(globalSSAIndex()), str(globalSSAIndex())
        lin = self.inexpr[0]
        if lin.getOut().getFlatSize()[0]*lin.getOut().getFlatSize()[1] == 1:
            sca = lin
            mat = self.inexpr[1]
        else:
            sca = self.inexpr[1]
            mat = lin
        sca.computeSpaceIdxNames(p, q, ppfix, qpfix, opts, depth, baselevel)
        mat.computeSpaceIdxNames(i, j, ipfix, jpfix, opts, depth, baselevel)
        matOut = mat.getOut()
        for c in range(len(matOut.spaceIdxNames)):
            self.out.spaceIdxNames[c] = [ idx for idx in matOut.spaceIdxNames[c] ]

    @staticmethod
    def orderPolicy(idxInfoList, indices, order, baselevel): #Taken from RDiv
        iPriority = {}
        for i in indices:
            p = {'t': (0,0), 's': 0, 'i': 0}
            t = ( p[order[0]], p[order[1]], p[order[2]] )
            iPriority[i] = t
        return iPriority
    
    def __repr__(self):
        return "Div( " + repr(self.inexpr[0]) + ", " + repr(self.inexpr[1]) + " )"

    def __str__(self):
        return "( " + str(self.inexpr[0]) + " Div " + str(self.inexpr[1]) + " )"

    def toLL(self, acc=False, accSign=None, sep=False):
        return "( " + self.inexpr[0].toLL() + " / " + self.inexpr[1].toLL() + " )"

#     def toLatex(self, context, ind=0, subs=None):
#         l, r = self.inexpr[0].toLatex(context, ind, subs), self.inexpr[1].toLatex(context, ind, subs)
#         if not ( any( map(lambda cls: isinstance(self.inexpr[0], cls), [Quantity, NewContextOperator]) ) \
#                  or isinstance(self.inexpr[0], Quantity) and self.inexpr[0].isScalar() ):
#             l = "(" + l + ")"   
#         if not ( any( map(lambda cls: isinstance(self.inexpr[1], cls), [Quantity, NewContextOperator]) ) \
#                  or isinstance(self.inexpr[1], Quantity) and self.inexpr[1].isScalar() ):
#             r = "(" + r + ")"   
#         res = l + r
#         return res

    @staticmethod
    def toPolySigma():
        return "/"

    def toEG(self): 
        return "/"

    def __hash__(self):
        tin = tuple(self.inexpr)
        key = (hash('pw/'), hash(tin))
        return hash(key)

class Inverse(Operator):

    def __init__(self, sexpr, out=None):
        super(Inverse, self).__init__()
        self.inexpr = [ sexpr ]
        self.buildout(out)
        self.setAsPred()

    def duplicate(self, prefix="", everything=True, changeOut=False, changeHandle=False):
        tIn = [ inexpr.duplicate() if isinstance(inexpr, Quantity) else inexpr.duplicate(prefix, everything, changeOut, changeHandle) for inexpr in self.inexpr ] if everything else self.inexpr
        if changeOut:
            out = None
            changeHandle = True
        else:
            out = self.out.duplicate(prefix)
        res = Inverse(tIn[0], out)
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res

    def buildout(self, out, src=None):
        if src is None:
            src = self.getInexprMat(0)
        
        self.set_info_no_td(src.info.keys(), src.info.values())
        if(out):
            self.out = out
        else:
            self.out = (src.__class__).fromBlock(src, name="inv" + str(globalSSAIndex()))
        self.set_out_info(src.info.keys(), src.info.values())

    def __str__(self):
        return "Inv( " + str(self.inexpr[0]) + " )"

    def toLL(self, acc=False, accSign=None, sep=False):
        return "inv( " + self.inexpr[0].toLL() + " )"

    def to_algo(self, decl_map, dep_map, dims_map, expr_map, order, sizes_map, dims):
        in_list = self.inexpr[0].to_algo(decl_map, dep_map, dims_map, expr_map, order, sizes_map, dims)
        res = "inv( " + in_list + " )"
        return res
    
    def __hash__(self):
        tin = tuple(self.inexpr)
        key = (hash('inv'), hash(tin))
        return hash(key)

class PMul(SimpleOperator):
    '''
    Parallel Multiplication (first part of mvm).
    '''
    def __init__(self, sexpr0, sexpr1, nu, out=None):
        super(PMul, self).__init__()
        self.inexpr = [ sexpr0, sexpr1 ]
        self.nu = nu
        self.buildout(out)
        self.setAsPred()

    def duplicate(self, prefix="", everything=True, changeOut=False, changeHandle=False):
        tIn = [ inexpr.duplicate() if isinstance(inexpr, Quantity) else inexpr.duplicate(prefix, everything, changeOut, changeHandle) for inexpr in self.inexpr ] if everything else self.inexpr
        if changeOut:
            out = None
            changeHandle = True
        else:
            out = self.out.duplicate(prefix)
        res = PMul(tIn[0], tIn[1], self.nu, out)
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res

    def duplicateUpToBoundaries(self, prefix="", boundaries=None, changeHandle=True):
        if boundaries is None:
            boundaries = []
        tIn = [ inexpr if (inexpr in boundaries) else inexpr.duplicateUpToBoundaries(prefix, boundaries, changeHandle) for inexpr in self.inexpr ]
        res = PMul(tIn[0], tIn[1], self.nu, self.out.duplicate(prefix))
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res
            
    def buildout(self, out, src=None):
        src0 = self.getInexprMat(0)
        src1 = self.getInexprMat(1)
        
        if(src0.level != src1.level):
            exit("Expression Tree Error > PMul: subexpressions have mismatching levels.")
        
        if(not self.checkConformity(src0, src1)):
            #If it gets here it must be scalar mismatch
            exit("Expression Tree Error > PMul: checkConformity at level 1. Scalar mismatch.")
        
        if(out):
            self.out = out
        else: 
            self.out = self.__buildout(src0, src1)
    
    def checkConformity(self, src0, src1):
        if(src0.level == 1): # Scalar conformity
            return src0.name == src1.name
        
        desc0 = src0.descriptor
        desc1 = src1.descriptor
        
        if(desc0.rows[0].getNumColPartitions() != desc1.getNumRowPartitions()):
            exit("Expression Tree Error > PMul: checkConformity at level " + str(src0.level) + ". ColParts in RowPart0 != RowParts in src1_desc.")
        
        for i in range(desc1.getNumRowPartitions()):
            if(desc0.rows[0].getColsOfPartition(i) != desc1.getRowsOfPartition(i)):
                exit("Expression Tree Error > PMul: checkConformity at level " + str(src0.level) + ". ColsPerPart in RowPart0 != RowsPerPart in src1_desc.")
        
        for i in range(desc1.getNumRowPartitions()):
            if(not self.checkConformity(desc0.rows[0].getBlockOfPartition(i), desc1.getBlockOfPartition(i, 0))):
                exit("Expression Tree Error > PMul: checkConformity at level " + str(src0.level) + ". Nonconforming Blocks at index " + str(i))
        
        return True
        
    def __buildout(self, src0, src1):
        if(src0.level == 1):
            return src0
            
        desc0 = src0.descriptor
        desc1 = src1.descriptor
        desc = Descriptor(desc0.level)
        desc.set_info(self.info.keys(), self.info.values())
        
#         if desc0.level == 1:
#             return src0.duplicate("d"+ str(globalSSAIndex()), o=[0,0], fL=fI(src0.size[0]), fR=fI(src0.size[1]))
#         
        listRowParts = []
        rowPart0_d1 = desc1.rows[0]
        for rowPart_d0 in desc0.rows:
            newRowPart = RowPartition(rowPart_d0.nRows, info=self.info)
            B0 = rowPart_d0.getBlockOfPartition(0)
#             if desc0.level == 2:
#                 listColParts = [ColPartition(1, Matrix.fromBlock(B0, name="pm" + str(globalSSAIndex())))]
#             else:
#                 listColParts = [ColPartition(1, self.__buildout(B0, rowPart0_d1.getBlockOfPartition(0)))]
            if desc0.level == 1:
                listColParts = [ColPartition(self.nu, self.__buildout(B0, rowPart0_d1.getBlockOfPartition(0)), self.info)]
            else:
                listColParts = [ColPartition(1, self.__buildout(B0, rowPart0_d1.getBlockOfPartition(0)), self.info)]
            newRowPart.addCols(listColParts)
            listRowParts += [newRowPart]
        
        desc.addRows(listRowParts)
        return Matrix("pm" + str(globalSSAIndex()), desc, desc.getSize())

    def multByG(self, fL, fR, idsDict, explored, opts):
        return None
            
    def getSignature(self):
        return self.inexpr[0].getSignature() + "_pmul-times_" + self.inexpr[1].getSignature()

    def __str__(self):
        return "( " + str(self.inexpr[0]) + " % " + str(self.inexpr[1]) + " )"

    def __hash__(self):
        tin = tuple(self.inexpr)
        key = (hash('*!'), hash(tin))
        return hash(key)


class HRed(Operator):
    '''
    Horizontal reduction (second part of mvm)
    '''
    def __init__(self, sexpr, out=None):
        super(HRed, self).__init__()
        self.inexpr = [sexpr]
        self.buildout(out)
        self.setAsPred()

    def duplicate(self, prefix="", everything=True, changeOut=False, changeHandle=False):
        tIn = [ inexpr.duplicate() if isinstance(inexpr, Quantity) else inexpr.duplicate(prefix, everything, changeOut, changeHandle) for inexpr in self.inexpr ] if everything else self.inexpr
        if changeOut:
            out = None
            changeHandle = True
        else:
            out = self.out.duplicate(prefix)
        res = HRed(tIn[0], out)
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res

    def duplicateUpToBoundaries(self, prefix="", boundaries=None, changeHandle=True):
        if boundaries is None:
            boundaries = []
        tIn = [ inexpr if (inexpr in boundaries) else inexpr.duplicateUpToBoundaries(prefix, boundaries, changeHandle) for inexpr in self.inexpr ]
        res = HRed(tIn[0], self.out.duplicate(prefix))
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res
            
    def buildout(self, out, src=None):
        src = self.getInexprMat(0)
        
        if(out):
            self.out = out
        else:
            self.out = self.__buildout(src)

    def __buildout(self, src0):
        
        if(src0.level == 1):
            return src0
        
        desc0 = src0.descriptor
        desc = Descriptor(desc0.level)
        desc.set_info(self.info.keys(), self.info.values())
        
        listRowParts = []
        for rowPart_d0 in desc0.rows:
            newRowPart = RowPartition(rowPart_d0.nRows, info=self.info)
            B0 = rowPart_d0.getBlockOfPartition(0)
            newColPart = ColPartition(1, self.__buildout(B0), self.info)
            newRowPart.addCols([newColPart])
            listRowParts.append(newRowPart)
        
        desc.addRows(listRowParts)
        return Matrix("hr" + str(globalSSAIndex()), desc, desc.getSize())
    
    def multByG(self, fL, fR, idsDict, explored, opts):
        return None
            
    def __str__(self):
        return "HRed( " + str(self.inexpr[0]) + " )"

    def __hash__(self):
        tin = tuple(self.inexpr)
        key = (hash('hr'), hash(tin))
        return hash(key)
    
class Sqrt(Operator):
    '''
    Square root
    '''
    def __init__(self, sexpr, out=None):
        super(Sqrt, self).__init__()
        if isinstance(sexpr, Holonode):
            self.buildout(out, sexpr.node.getOut())
        else:
            self.inexpr = [sexpr]
            self.buildout(out)
            self.setAsPred()

    def duplicate(self, prefix="", everything=True, changeOut=False, changeHandle=False):
        tIn = [ inexpr.duplicate() if isinstance(inexpr, Quantity) else inexpr.duplicate(prefix, everything, changeOut, changeHandle) for inexpr in self.inexpr ] if everything else self.inexpr
        if changeOut:
            out = None
            changeHandle = True
        else:
            out = self.out.duplicate(prefix)
        res = Sqrt(tIn[0], out)
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res

    def duplicateUpToBoundaries(self, prefix="", boundaries=None, changeHandle=True):
        if boundaries is None:
            boundaries = []
        tIn = [ inexpr if (inexpr in boundaries) else inexpr.duplicateUpToBoundaries(prefix, boundaries, changeHandle) for inexpr in self.inexpr ]
        res = Sqrt(tIn[0], self.out.duplicate(prefix))
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res
    
    @staticmethod
    def orderPolicy(idxInfoList, indices, order, baselevel):
        iPriority = {}
        for i in indices:
            idxInfo = filter(lambda idxInfo: i in idxInfo, idxInfoList)
            if len(idxInfo) == 0:
                p = {'t': (0,0), 's': 0, 'i': 0}
            else:
                idxInfo = idxInfo[0]
                lev = idxInfo[i][1]
                p = {'t': (idxInfo[i][0]-lev,0), 's': 0, 'i': 0}
            t = ( p[order[0]], p[order[1]], p[order[2]] )
            iPriority[i] = t
        return iPriority

    def computeSpaceIdxNames(self, i, j, ipfix, jpfix, opts, depth=1, baselevel=2):
        self.inexpr[0].computeSpaceIdxNames(i, j, ipfix, jpfix, opts, depth, baselevel)
        self.out.spaceIdxNames[0] = [ idx for idx in self.inexpr[0].getOut().spaceIdxNames[0] ]
        self.out.spaceIdxNames[1] = [ idx for idx in self.inexpr[0].getOut().spaceIdxNames[1] ]
            
    def buildout(self, out, src=None):
        if src is None:
            src = self.getInexprMat(0)
        
        self.set_info_no_td(src.info.keys(), src.info.values())
        if(out):
            self.out = out
        else:
            self.out = self.__buildout(src)
        self.set_out_info(src.info.keys(), src.info.values())

    def __buildout(self, src):
        
        return src.duplicate("sr")
    
    @staticmethod
    def toPolySigma():
        return "sqrt"

    def toEG(self): 
        return "sqrt"
    
    def toLatex(self, context, ind=0, subs=None):
        res = self.inexpr[0].toLatex(context, ind, subs)
        res = "\sqrt{" + res + "}"   
        return res
        
    def __str__(self):
        return "Sqrt( " + str(self.inexpr[0]) + " )"

    def toLL(self, acc=False, accSign=None, sep=False):
        return "sqrt( " + self.inexpr[0].toLL() + " )"

    def __hash__(self):
        tin = tuple(self.inexpr)
        key = (hash('sqrt'), hash(tin))
        return hash(key)

class T(Operator):
    '''
    Transpose Matrix
    '''
    def __init__(self, sexpr, out=None):
        super(T, self).__init__()
        if isinstance(sexpr, Holonode):
            self.buildout(out, sexpr.node.getOut())
        else:
            self.inexpr = [sexpr]
            self.buildout(out)
            self.setAsPred()

    def duplicate(self, prefix="", everything=True, changeOut=False, changeHandle=False):
        tIn = [ inexpr.duplicate() if isinstance(inexpr, Quantity) else inexpr.duplicate(prefix, everything, changeOut, changeHandle) for inexpr in self.inexpr ] if everything else self.inexpr
        if changeOut:
            out = None
            changeHandle = True
        else:
            out = self.out.duplicate(prefix)
        res = T(tIn[0], out)
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res

    def duplicateUpToBoundaries(self, prefix="", boundaries=None, changeHandle=True):
        if boundaries is None:
            boundaries = []
        tIn = [ inexpr if (inexpr in boundaries) else inexpr.duplicateUpToBoundaries(prefix, boundaries, changeHandle) for inexpr in self.inexpr ]
        res = T(tIn[0], self.out.duplicate(prefix))
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res
    
    @staticmethod
    def orderPolicy(idxInfoList, indices, order, baselevel):
        iPriority = {}
        for i in indices:
            idxInfo = filter(lambda idxInfo: i in idxInfo, idxInfoList)
            if len(idxInfo) == 0:
                p = {'t': (0,0), 's': 0, 'i': 0}
            else:
                idxInfo = idxInfo[0]
                lev = idxInfo[i][1]
                p = {'t': (idxInfo[i][0]-lev,0), 's': 0, 'i': 0}
            t = ( p[order[0]], p[order[1]], p[order[2]] )
            iPriority[i] = t
        return iPriority

    def computeSpaceIdxNames(self, i, j, ipfix, jpfix, opts, depth=1, baselevel=2):
        self.inexpr[0].computeSpaceIdxNames(j, i, jpfix, ipfix, opts, depth, baselevel)
        self.out.spaceIdxNames[0] = [ idx for idx in self.inexpr[0].getOut().spaceIdxNames[1] ]
        self.out.spaceIdxNames[1] = [ idx for idx in self.inexpr[0].getOut().spaceIdxNames[0] ]
            
    def buildout(self, out, src=None):
        if src is None:
            src = self.getInexprMat(0)
        
        self.set_info_no_td(src.info.keys(), src.info.values())
        if(out):
            self.out = out
        else:
            self.out = self.__buildout(src)
        self.set_out_info(src.info.keys(), src.info.values())

    def __buildout(self, src):
        
        return src.transpose()
    
    def multByG(self, fL, fR, idsDict, explored, opts):
#         
#         indup = self.inexpr[0] 
#         indup.subs(idsDict, [])
#         
# #         newT = T(self.inexpr[0])
#         newT = T(indup)
#         return G(fL, newT, fR)
        return None
    
    @staticmethod
    def toPolySigma():
        return "trans"

    def toEG(self): 
        return "trans"
    
    @staticmethod
    def inverse():
        return T 

#     def getOps(self):
#         c = self.inexpr[0].getOps()
#         # TBA
# #         subOut = self.inexpr[0].getOut()
# #         subSize = subOut.getFlatSize()
# #         s = subOut.getFlatPolyStructureFromIndices(['x', 'y'], subOut.getOrigin(), subSize)
# #         d = subOut.getDiagPolyStructure(['x','y'], IMF(1, subSize[0], sympify('x+i')), IMF(1, subSize[1], sympify('y+i')), subOut.getOrigin(), subSize, (1,1))
# #         stype = filter(lambda struct: issubclass(struct, Matrix), d)[0]
# #         c += 2*(s.get(Matrix, Set("{[x,y]:1=0}")).count_val().to_python() - d.get(stype, Set("{[x,y]:1=0}")).count_val().to_python()) - s.get(ZeroMatrix, Set("{[x,y]:1=0}")).count_val().to_python()
#         return c
    
    def toLatex(self, context, ind=0, subs=None):
        sub = self.inexpr[0].toLatex(context, ind, subs)
        if not isinstance(self.inexpr[0], Quantity):
            sub = "(" + sub + ")"   
        res = sub + "^T"
        return res
        
    def __str__(self):
        return "T( " + str(self.inexpr[0]) + " )"

    def toLL(self, acc=False, accSign=None, sep=False):
        return "trans( " + self.inexpr[0].toLL() + " )"

    def to_algo(self, decl_map, dep_map, dims_map, expr_map, order, sizes_map, dims):
        local_dims = [dims[1], dims[0]] 
        in_list = self.inexpr[0].to_algo(decl_map, dep_map, dims_map, expr_map, order, sizes_map, local_dims)
        dims[0] = local_dims[1]
        dims[1] = local_dims[0]
        res = "trans( " + in_list + " )"
        return res
    

    def __hash__(self):
        tin = tuple(self.inexpr)
        key = (hash('t'), hash(tin))
        return hash(key)
    
#     def __eq__(self, other):
#         if not isinstance(other, T):
#             return False
# #         if self.handle != other.handle:
# #             return False
#         for e,o in zip(self.inexpr, other.inexpr):
#             if e != o:
#                 return False
#         return True
# 
#     def __ne__(self, other):
#         return not self.__eq__(other)

class Neg(Operator):
    '''
    Negative operator
    '''
    def __init__(self, sexpr, out=None):
        super(Neg, self).__init__()
        if isinstance(sexpr, Holonode):
            self.buildout(out, sexpr.node.getOut())
        else:
            self.inexpr = [sexpr]
            self.buildout(out)
            self.setAsPred()

    def duplicate(self, prefix="", everything=True, changeOut=False, changeHandle=False):
        tIn = [ inexpr.duplicate() if isinstance(inexpr, Quantity) else inexpr.duplicate(prefix, everything, changeOut, changeHandle) for inexpr in self.inexpr ] if everything else self.inexpr
        if changeOut:
            out = None
            changeHandle = True
        else:
            out = self.out.duplicate(prefix)
        res = Neg(tIn[0], out)
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res

    def duplicateUpToBoundaries(self, prefix="", boundaries=None, changeHandle=True):
        if boundaries is None:
            boundaries = []
        tIn = [ inexpr if (inexpr in boundaries) else inexpr.duplicateUpToBoundaries(prefix, boundaries, changeHandle) for inexpr in self.inexpr ]
        res = Neg(tIn[0], self.out.duplicate(prefix))
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res
    
    @staticmethod
    def orderPolicy(idxInfoList, indices, order, baselevel):
        iPriority = {}
        for i in indices:
            idxInfo = filter(lambda idxInfo: i in idxInfo, idxInfoList)
            if len(idxInfo) == 0:
                p = {'t': (0,0), 's': 0, 'i': 0}
            else:
                idxInfo = idxInfo[0]
                rowIdx = any(map(lambda idxInfo: i in idxInfo and idxInfo[i][2] == 0, idxInfoList))
                colIdx = any(map(lambda idxInfo: i in idxInfo and idxInfo[i][2] == 1, idxInfoList))
                lev = idxInfo[i][1]
                if rowIdx:
                    p = {'t': (idxInfo[i][0]-lev,0), 's': 0, 'i': 0}
                elif colIdx:
                    p = {'t': (idxInfo[i][0]-lev,0), 's': 1, 'i': 0}
            t = ( p[order[0]], p[order[1]], p[order[2]] )
            iPriority[i] = t
        return iPriority

#     def computeSpaceIdxNames(self, i, j, ipfix, jpfix, opts, depth=1, baselevel=2):
#         self.inexpr[0].computeSpaceIdxNames(i, j, ipfix, jpfix, opts, depth, baselevel)
#         self.out.spaceIdxNames[0] = [ idx for idx in self.inexpr[0].getOut().spaceIdxNames[0] ]
#         self.out.spaceIdxNames[1] = [ idx for idx in self.inexpr[0].getOut().spaceIdxNames[1] ]

    def buildout(self, out, src=None):
        if src is None:
            src = self.getInexprMat(0)
        
        self.set_info_no_td(src.info.keys(), src.info.values())
        if(out):
            self.out = out
        else:
            self.out = self.__buildout(src)
        self.set_out_info(src.info.keys(), src.info.values())

    def __buildout(self, src):
        
        return (src.__class__).fromBlock(src, name="neg" + str(globalSSAIndex()))
    
    @staticmethod
    def toPolySigma():
        return "-"

    def toEG(self): 
        return "-"
    
    def toLatex(self, context, ind=0, subs=None):
        sub = self.inexpr[0].toLatex(context, ind, subs)
        if not isinstance(self.inexpr[0], Quantity):
            sub = "(" + sub + ")"   
        res = "-" + sub
        return res
        
    def __str__(self):
        return "Neg( " + str(self.inexpr[0]) + " )"

    def toLL(self, acc=False, accSign=None, sep=False):
        return "-( " + self.inexpr[0].toLL() + " )"

    def to_algo(self, decl_map, dep_map, dims_map, expr_map, order, sizes_map, dims):
        in_list = []
        for inexpr in self.inexpr:
            in_list.append( inexpr.to_algo(decl_map, dep_map, dims_map, expr_map, order, sizes_map, dims) )
        res = "-( " + in_list[0] + " )"
        return res
    

    def __hash__(self):
        tin = tuple(self.inexpr)
        key = (hash('neg'), hash(tin))
        return hash(key)
    
class Tile(Operator):
    '''
    Tiling Expression.
    '''
    def __init__(self, nu, sexpr, out=None):
        super(Tile, self).__init__()

        if isinstance(nu, int):
            self.nu = (nu, nu)
        else:
            self.nu = nu

        if isinstance(sexpr, Holonode):
            self.buildout(out, sexpr.node.getOut())
        else:
            self.inexpr = [sexpr]
            self.buildout(out)
            self.setAsPred()

    def duplicate(self, prefix="", everything=True, changeOut=False, changeHandle=False):
        tIn = [ inexpr.duplicate() if isinstance(inexpr, Quantity) else inexpr.duplicate(prefix, everything, changeOut, changeHandle) for inexpr in self.inexpr ] if everything else self.inexpr
        if changeOut:
            out = None
            changeHandle = True
        else:
            out = self.out.duplicate(prefix)
        res = Tile(copy(self.nu), tIn[0], out)
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res

    def duplicateUpToBoundaries(self, prefix="", boundaries=None, changeHandle=True):
        if boundaries is None:
            boundaries = []
        tIn = [ inexpr if (inexpr in boundaries) else inexpr.duplicateUpToBoundaries(prefix, boundaries, changeHandle) for inexpr in self.inexpr ]
        res = Tile(copy(self.nu), tIn[0], self.out.duplicate(prefix))
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res
            
    def buildout(self, out, src=None):
        if src is None:
            src = self.getInexprMat(0)              
        
        self.set_info_no_td(src.info.keys(), src.info.values())
        min_info = self.info.get('min', {})
        homogeneous = src.isHomogeneous()
        if(not homogeneous):
            size = src.getPartitionSize(0,0)
#             hi, hj = src.size[0]-size[0] == 0, src.size[1]-size[1] == 0
            hi, hj = Eq(src.size[0]-size[0], 0), Eq(src.size[1]-size[1], 0)

            # if the matrix is heterogeneous, the heterogeneous dimensions must be divisible by the corresponding tile size,
            # so that we don't get more than 2 different block sizes per dimension
            if not hi.subs(min_info) and Gt(size[0]%self.nu[0], 0).subs(min_info):
                exit("Expression Tree Error > Tile: Cannot create \"loop-friendly\" rows.")
            if not hj.subs(min_info) and Gt(size[1]%self.nu[1], 0).subs(min_info):
                exit("Expression Tree Error > Tile: Cannot create \"loop-friendly\" columns.")

        if(out):
            self.out = out
        else:
#             self.out = self.__buildout(src, homogeneous)
            self.out = self.__buildout(src)
        self.set_out_info(src.info.keys(), src.info.values())


#     def __buildout(self, src, homogeneous):
    def __buildout(self, src):
        return src.tile(self.nu)

    def getSignature(self):
        return self.inexpr[0].getSignature()

    def computeSpaceIdxNames(self, i, j, ipfix, jpfix, opts, depth=1, baselevel=2):
        self.out.computeSpaceIdxNames(i, j, ipfix, jpfix, opts, depth, baselevel)
# #         part_size = self.out.getPartitionSize(0, 0)
# #         self.out.spaceIdxNames[0] = [i*depth+ipfix if part_size[0].subs(self.info.get('min', {})) > 1 else None]
# #         self.out.spaceIdxNames[1] = [j*depth+jpfix if part_size[1].subs(self.info.get('min', {})) > 1 else None]
#         self.out.spaceIdxNames[0] = [i*depth+ipfix]
#         self.out.spaceIdxNames[1] = [j*depth+jpfix]
#         osize = self.out.getFlatSize()
#         if baselevel < self.out.level and (osize[0]*osize[1]).subs(self.info.get('min', {})) > 1:
#             self.inexpr[0].computeSpaceIdxNames(i, j, ipfix, jpfix, opts, depth+1, baselevel)
#             for c in range(len(self.inexpr[0].getOut().spaceIdxNames)):
#                 for idx in self.inexpr[0].getOut().spaceIdxNames[c]:
#                     self.out.spaceIdxNames[c].append(idx)
#         else:
#             self.inexpr[0].cleanSpaceIdxNames()

    def computeIdxPriority(self, idxPriorityList, indices, order, baselevel):
        if isinstance(self.inexpr[0], Operator):
            self.inexpr[0].computeIdxPriority(idxPriorityList, indices, order, baselevel)
    
    def getNonTileOut(self):
        return self.inexpr[0].getNonTileOut()

    def getNonTileExpr(self):
        return self.inexpr[0].getNonTileExpr()
    
    def setPolyStmts(self, polyStmts):
        self.inexpr[0].setPolyStmts(polyStmts)

    def updatePolyStmts(self, polyStmts):
        self.inexpr[0].updatePolyStmts(polyStmts)

    def getPolyStmts(self):
        return self.inexpr[0].getPolyStmts()

    def __str__(self):
        return "Tile( " + str(self.nu) + ", " + str(self.inexpr[0]) + " )"

    def __hash__(self):
        tin = tuple(self.inexpr)
        key = (hash('tile'), self.nu[0], self.nu[1], hash(tin))
        return hash(key)

    def sameUpToNames(self, other):
        return super(Tile, self).sameUpToNames(other) and self.nu == other.nu
    
    def __eq__(self, other):
        return super(Tile, self).__eq__(other) and self.nu == other.nu


class Assign(SimpleOperator):
    '''
    Assignment Expression.
    '''
    def __init__(self, sexpr0, sexpr1, out=None):
        super(Assign, self).__init__()
        if isinstance(sexpr0, Holonode) and isinstance(sexpr1, Holonode):
            self.buildout(out, [sexpr0.node.getOut(), sexpr1.node.getOut()])
        else:
            self.inexpr = [sexpr0, sexpr1]
            self.buildout(out)
            self.setAsPred()

    def duplicate(self, prefix="", everything=True, changeOut=False, changeHandle=False):
        tIn = [ inexpr.duplicate() if isinstance(inexpr, Quantity) else inexpr.duplicate(prefix, everything, changeOut, changeHandle) for inexpr in self.inexpr ] if everything else self.inexpr
        if changeOut:
            out = None
            changeHandle = True
        else:
            out = self.out.duplicate(prefix)
        res = Assign(tIn[0], tIn[1], out)
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res

    def duplicateUpToBoundaries(self, prefix="", boundaries=None, changeHandle=True):
        if boundaries is None:
            boundaries = []
        tIn = [ inexpr if (inexpr in boundaries) else inexpr.duplicateUpToBoundaries(prefix, boundaries, changeHandle) for inexpr in self.inexpr ]
        res = Assign(tIn[0], tIn[1], self.out.duplicate(prefix))
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res
                    
    def buildout(self, out, src=None):
        if src is None:
            src0 = self.getInexprMat(0)
            src1 = self.getInexprMat(1)
        else:
            src0, src1 = src[0], src[1]
        
#         if(src0.level != src1.level):
#             exit("Expression Tree Error > Assign: subexpressions have mismatching levels.")
        
        self.set_info_no_td(src0.info.keys(), src0.info.values())
#         if(src0 != src1):
#         if  not src0.sameLayout(src1) or not isinstance(src1, src0.__class__):
        if  not src0.sameLayout(src1):
            exit("Expression Tree Error > Assign: Mismatching layout.")
        
#         if not src0.attr['o'] and not src1.attr['o']:
#             exit("Expression Tree Error > Assign: no input marked as destination.")
        
        if(out):
            self.out = out
        else:
            self.out = src0.duplicate("s" + str(globalSSAIndex()))
        self.set_out_info(src0.info.keys(), src0.info.values())
        

    def getStructFromAbove(self):
        return self.inexpr[0].genStruct 

    def getAccessFromAbove(self):
        return self.inexpr[0].genAccess() 

    def computeIdxPriority(self, idxPriorityList, indices, order, baselevel):
        if isinstance(self.inexpr[1], Operator):
            self.inexpr[1].computeIdxPriority(idxPriorityList, indices, order, baselevel)

    def getSignature(self):
        return self.inexpr[0].getSignature() + "_eq_" + self.inexpr[1].getSignature()
    
    def toEG(self): 
        return "="

    @staticmethod
    def toPolySigma():
        return "="

    def toLatex(self, context, ind=0, subs=None):
        res = self.inexpr[0].toLatex(context, ind, subs) + " = " + self.inexpr[1].toLatex(context, ind, subs) 
        return res

    def __str__(self):
        return str(self.inexpr[0]) + " = " + str(self.inexpr[1])

    def toLL(self):
        return self.inexpr[0].toLL() + " = " + self.inexpr[1].toLL() + ";\n"

    def to_algo(self, decl_map, dep_map, dims_map, expr_map, order, sizes_map, dims=None):
        in_list = []
        if dims is None:
            dims = [None]*2
        for inexpr in self.inexpr:
            in_list.append( inexpr.to_algo(decl_map, dep_map, dims_map, expr_map, order, sizes_map, dims) )
        res = in_list[0] + " = " + in_list[1] + ";\n"
        return res

    def algo_signature(self):
        if self.inexpr[1].is_func():
            return self.inexpr[1].algo_signature()
        res = super(Assign, self).algo_signature()
        return res

    def __hash__(self):
        tin = tuple(self.inexpr)
        key = (hash('='), hash(tin))
        return hash(key)
    
class ParamMat(Operator):
    '''
    Parametrized Matrix
    '''
    def __init__(self):
        super(ParamMat, self).__init__()
        self.fL, self.fR = None,None
        
    def subs(self, idsDict, explored=None):
        super(ParamMat, self).subs(idsDict, explored)
        self.fL = self.fL.subs(idsDict)
        self.fR = self.fR.subs(idsDict)
        
    def getSyms(self):
        #Returns a list of sets
        return [ self.fL.of(0).atoms(Symbol), self.fR.of(0).atoms(Symbol) ]

    def dependsOn(self, idx):
        return super(ParamMat, self).dependsOn(idx) or any(map(lambda symExpr: idx in symExpr, [ self.fL.of(0), self.fR.of(0)]))

    def __eq__(self, other):
        return super(ParamMat, self).__eq__(other) and self.fL == other.fL and self.fR == other.fR

    def sameUpToNames(self, other):
        return super(ParamMat, self).sameUpToNames(other) and self.fL == other.fL and self.fR == other.fR

    def computeIdxPriority(self, idxPriorityList, indices, order, baselevel):
        pass

    def getNonTileOut(self):
        return self
    
    def getCost(self):
        return self.inexpr[0].getCost()

    def getOps(self):
        return self.inexpr[0].getOps()
    
    def getFlops(self):
        return self.inexpr[0].getFlops()

class G(ParamMat):
    '''
    Gather Matrix
    '''
    def __init__(self, fL, sexpr, fR, out=None, setAsPred=True, ann=None):
        super(G, self).__init__()
        self.fL = fL
        self.fR = fR
        self.ann = ann
        
        if isinstance(sexpr, Holonode):
            self.buildout(out, sexpr.node.getOut())
        else:
            self.inexpr = [sexpr]
            self.buildout(out)
            if setAsPred:
                self.setAsPred()

    def duplicate(self, prefix="", everything=True, changeOut=False, changeHandle=False):
        tIn = [ inexpr.duplicate() if isinstance(inexpr, Quantity) else inexpr.duplicate(prefix, everything, changeOut, changeHandle) for inexpr in self.inexpr ] if everything else self.inexpr
        if changeOut:
            out = None
            changeHandle = True
        else:
            out = self.out.duplicate(prefix)
        res = G(deepcopy(self.fL), tIn[0], deepcopy(self.fR), out)
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res

    def duplicateUpToBoundaries(self, prefix="", boundaries=None, changeHandle=True):
        if boundaries is None:
            boundaries = []
        tIn = [ inexpr if (inexpr in boundaries) else inexpr.duplicateUpToBoundaries(prefix, boundaries, changeHandle) for inexpr in self.inexpr ]
        res = G(self.fL, tIn[0], self.fR, self.out.duplicate(prefix))
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res
            
    def buildout(self, out, src=None):
        if src is None:
            src = self.getInexprMat(0)
        
#        if(self.fL.N != src.size[0]) or (self.fR.N != src.size[1]):
#            exit("Expression Tree Error > G: IMF not conforming to subexpression.")
                     
        self.set_info_no_td(src.info.keys(), src.info.values())
        if(out):
            self.out = out
        else:
            self.out = self.__buildout(src)
        self.set_out_info(src.info.keys(), src.info.values())

    def __buildout(self, src):
        blk = src.getBlock(0,0)
#         return Matrix("g" + str(globalSSAIndex()), blk, (self.fL.n, self.fR.n), copy(src.o), attr={'i': src.attr['i'], 'o':src.attr['o']}, fL=self.fL, fR=self.fR)
        mtype,access = Matrix,None
        if self.ann is not None:
            mtype = eval(self.ann[0])
            access = eval(self.ann[1]) if len(self.ann) > 1 else None
        
        return mtype("g" + str(globalSSAIndex()), blk, (self.fL.n, self.fR.n), access=access)
        

    def multByG(self, fL, fR, idsDict, explored, opts):
#         
#         gfL = self.fL.subs(idsDict)
#         gfR = self.fR.subs(idsDict)
#         newfL = gfL.compose(fL)
#         newfR = gfR.compose(fR)
#         
#         res = self.inexpr[0].multByG(newfL, newfR, idsDict, explored, opts)
#         
#         return res
        return None

    def toEG(self): 
        return "G"

    def toLatex(self, context, ind=0, subs=None):
        sub = self.inexpr[0].toLatex(context, ind, subs)
        if not any( map(lambda cls: isinstance(self.inexpr[0], cls), [Quantity, ParamMat, NewContextOperator]) ):
            sub = "(" + sub + ")"   
        res = sub + "[" + self.fL.toLatex(context, ind, subs)+ "," + self.fR.toLatex(context, ind, subs)+ "]_{" + str(self.fL.n)+ ","+str(self.fR.n)+"}^{"  + str(self.fL.N)+ ","+str(self.fR.N)+ "}"
        return res
    
    def get_quantity(self):
        return self.inexpr[0].get_quantity()
    
    def toLL(self, acc=False, accSign=None, sep=False):
        if not sep:
            return self.inexpr[0].toLL(acc, accSign) + "[" + str(self.fL) + "," + str(self.fR) + "]"
        else:
            return self.inexpr[0].toLL(acc, accSign, sep) + ["[" + str(self.fL) + "," + str(self.fR) + "]"]

    def to_algo(self, decl_map, dep_map, dims_map, expr_map, order, sizes_map, dims):
        #Not in use yet - But might if gathers will appear in LA input progs
        #So far just replicating the logic of Quantity with the out matrix.  
        llstr = self.toLL()
        if llstr not in decl_map: 
            local_dims = []
            if any(map(lambda MatType: isinstance(self.out, MatType), (Triangular, Symmetric))):
                d = getNextDim()
                local_dims.extend((d,d))
            else:
                local_dims.append(getNextDim())
                local_dims.append(getNextDim())
            for i,dim in enumerate(dims):
                if dim is None:
                    dims[i] = local_dims[i]
            dims_map[self.out] = [ d for d in dims ]
            for d,s in zip(dims, self.out.size):
                if d not in sizes_map:
                    sizes_map[d] = s
            decl_map[llstr] = self.out
            dep_map[self.out] = self.get_quantity()
            expr_map[self.out] = self
            order.append(self.out)
#         for s in self.out.getFlatSize():
#             if s not in dims_map:
#                 dims_map[s] = getNextDim()
#         llstr = self.toLL()
#         if llstr not in decl_map: 
#             decl_map[llstr] = self.out
# #             if self.out not in dep_map:
#             dep_map[self.out] = self.get_quantity()
#             expr_map[self.out] = self
#             order.append(self.out)
        return decl_map[llstr][0].name

    def algo_signature(self):
        res = self.out.__class__.__name__
        return res

    def __str__(self):
        return "G(" + str(self.fL) + ", " + str(self.inexpr[0]) + "," + str(self.fR) + ")"

    def __hash__(self):
        tin = tuple(self.inexpr)
        key = (hash('Gat'), hash(tin), hash(self.fL), hash(self.fR))
        return hash(key)

class S(ParamMat):
    '''
    Scatter Matrix 
    '''
    def __init__(self, fL, sexpr, fR, out=None):
        super(S, self).__init__()

        self.fL = fL
        self.fR = fR

        if isinstance(sexpr, Holonode):
            self.buildout(out, sexpr.node.getOut())
        else:
            self.inexpr = [sexpr]
            self.buildout(out)
            self.setAsPred()

    def duplicate(self, prefix="", everything=True, changeOut=False, changeHandle=False):
        tIn = [ inexpr.duplicate() if isinstance(inexpr, Quantity) else inexpr.duplicate(prefix, everything, changeOut, changeHandle) for inexpr in self.inexpr ] if everything else self.inexpr
        if changeOut:
            out = None
            changeHandle = True
        else:
            out = self.out.duplicate(prefix)
        res = self.__class__(deepcopy(self.fL), tIn[0], deepcopy(self.fR), out)
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res

    def duplicateUpToBoundaries(self, prefix="", boundaries=None, changeHandle=True):
        if boundaries is None:
            boundaries = []
        tIn = [ inexpr if (inexpr in boundaries) else inexpr.duplicateUpToBoundaries(prefix, boundaries, changeHandle) for inexpr in self.inexpr ]
        res = S(self.fL, tIn[0], self.fR, self.out.duplicate(prefix))
        res.setComputed(self.computed)
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res
            
    def buildout(self, out, src=None):
        if src is None:
            src = self.getInexprMat(0)
        # TODO: Should think of checking whether the input has a pred already
        #       In case of multiple pred, the operator should refer to a copy 
#         src = self.getInexprMat(0)
        
#        if(self.fL.n != src.size[0]) or (self.fR.n != src.size[1]):
#            exit("Expression Tree Error > S: IMF not conforming to subexpression.")
                     
        self.set_info_no_td(src.info.keys(), src.info.values())
        if(out):
            self.out = out
        else:
            self.out = self.__buildout(src)
        self.set_out_info(src.info.keys(), src.info.values())

    def __buildout(self, src):
        
        #self.srcfL, self.srcfR = src.fL, src.fR 
#         src.fL = self.fL
#         src.fR = self.fR
        
        blk = src.getBlock(0,0)
        return Matrix("sc" + str(globalSSAIndex()), blk, (self.fL.N, self.fR.N))

    def multByG(self, caller, fL, fR, idsDict, explored, opts):
        
        sfL, sfR = self.fL.subs(idsDict), self.fR.subs(idsDict)
        
        # Under the assumption that fL and fR are fHbs
        x = Max(sympify(0), fL.i - sfL.i)
        y = Max(sympify(0), fR.i - sfR.i)
        
        m = Min(sfL.n, fL.i - sfL.i + fL.n) - x
        n = Min(sfR.n, fR.i - sfR.i + fR.n) - y
        
        newfL, newfR = fHbs(m, sfL.n, x, sympify(1)), fHbs(n, sfR.n, y, sympify(1)) 
        
        if newfL.isfI() and newfR.isfI():
            inner = self.inexpr[0]
            inner.subs(idsDict, [])

            del self.inexpr[:]
            inner.delPred(self)
            self.delPred(caller)
            inner.buildout(None)
#             for p in self.pred:
#                 p[0].inexpr[p[1]] = inner
#                 p[0].setAsPredOfInExpr(p[1])
            return inner
#             return G(newfL, inner, newfR)
        
        res = self.inexpr[0].multByG(newfL, newfR, idsDict, explored, opts)
        
        return res

    def toEG(self): 
        return "S"

    def toLatex(self, context, ind=0, subs=None):
        sub = self.inexpr[0].toLatex(context, ind, subs)
        if not any( map(lambda cls: isinstance(self.inexpr[0], cls), [Quantity, ParamMat, NewContextOperator]) ):
            sub = "(" + sub + ")"   
        res = "\leftidx{_{" + str(self.fL.n)+ ","+str(self.fR.n)+"}^{"  + str(self.fL.N)+ ","+str(self.fR.N)+ "}}{[}{}" + self.fL.toLatex(context, ind, subs)+ "," + self.fR.toLatex(context, ind, subs)+ "]" + sub
        return res

    def toLL(self, acc=False, accSign=None, sep=False):
        accSign = '' if not accSign else accSign
        accPrefix = ("$" + accSign) if acc else "" 
        if not sep:
            return accPrefix + "[" + str(self.fL) + "," + str(self.fR) + "]" + self.inexpr[0].toLL(acc, accSign)
        else:
            return [accPrefix + "[" + str(self.fL) + "," + str(self.fR) + "]"] + self.inexpr[0].toLL(acc, accSign, sep)
        
    def __str__(self):
        return "S(" + str(self.fL) + ", " + str(self.inexpr[0]) + "," + str(self.fR) + ")"

    def __hash__(self):
        tin = tuple(self.inexpr)
        key = (hash('Sca'), hash(tin), hash(self.fL), hash(self.fR))
        return hash(key)

class Sacc(S):
    def __init__(self, fL, sexpr, fR, out=None):
        super(Sacc, self).__init__(fL, sexpr, fR, out)
        self.neg = False

    def toEG(self): 
        return "\$"

    def __eq__(self, other):
        return super(Sacc, self).__eq__(other) and self.neg == other.neg

    def sameUpToNames(self, other):
        return super(Sacc, self).sameUpToNames(other) and self.neg == other.neg

    def duplicate(self, prefix="", everything=True, changeOut=False, changeHandle=False):
        res = super(Sacc, self).duplicate(prefix=prefix, everything=everything, changeOut=changeOut, changeHandle=changeHandle)
        res.neg = self.neg
        return res

    def duplicateUpToBoundaries(self, prefix="", boundaries=None, changeHandle=True):
        res = super(Sacc, self).duplicateUpToBoundaries(prefix=prefix, boundaries=boundaries, changeHandle=changeHandle)
        res.neg = self.neg
        return res

    def __str__(self):
        return ("-" if self.neg else "") + "$(" + str(self.fL) + ", " + str(self.inexpr[0]) + "," + str(self.fR) + ")"

    def toLatex(self, context, ind=0, subs=None):
        sub = self.inexpr[0].toLatex(context, ind, subs)
        if not any( map(lambda cls: isinstance(self.inexpr[0], cls), [Quantity, ParamMat, NewContextOperator]) ):
            sub = "(" + sub + ")"   
        res = ("-" if self.neg else "") + "\leftidx{_{" + str(self.fL.n)+ ","+str(self.fR.n)+"}^{"  + str(self.fL.N)+ ","+str(self.fR.N)+ "}}{[}{}" + self.fL.toLatex(context, ind, subs)+ "," + self.fR.toLatex(context, ind, subs)+ "]" + sub
        return res

    def __hash__(self):
        tin = tuple(self.inexpr)
        key = (hash('ScaAcc'), hash(tin), hash(self.fL), hash(self.fR), hash(self.neg))
        return hash(key)

    def getCost(self):
        c = self.inexpr[0].getCost()
        s = self.out.getFlatSize()
        c += s[0]*s[1]
        return c


class Iv(NewContextOperator):
    '''
    Iverson Brackets
    '''
    def __init__(self, sexpr, cond=True, out=None):
        super(Iv, self).__init__()
        self.cond = cond
        self.init = False
        if isinstance(sexpr, Holonode):
            self.buildout(out, sexpr.node.getOut())
        else:
            self.inexpr = [sexpr]
            self.buildout(out)
            self.setAsPred()

    def buildout(self, out, src=None):
        if src is None:
            src = self.getInexprMat(0)

        self.set_info_no_td(src.info.keys(), src.info.values())
        if(out):
            self.out = out
        else:
            self.out = self.__buildout(src)
        self.set_out_info(src.info.keys(), src.info.values())

    def subs(self, idsDict, explored=None):
        super(Iv, self).subs(idsDict, explored)
        self.cond.subs(idsDict)

    def duplicate(self, prefix="", everything=True, changeOut=False, changeHandle=False):
        tIn = [ inexpr.duplicate() if isinstance(inexpr, Quantity) else inexpr.duplicate(prefix, everything, changeOut, changeHandle) for inexpr in self.inexpr ] if everything else self.inexpr
        if changeOut:
            out = None
            changeHandle = True
        else:
            out = self.out.duplicate(prefix)
        res = Iv(tIn[0], deepcopy(self.cond), out)
        res.setComputed(self.computed)
        res.init = self.init
        res.depSet = deepcopy(self.depSet)
        if not changeHandle:
            res.handle = self.handle
        return res

    def dependsOn(self, idx):
        return super(Iv, self).dependsOn(idx) or self.cond.dependsOn(idx)

    def toLatex(self, context, ind=0, subs=None):
        subs = {} if subs is None else subs
        res = "($\n"
        res += ind*" " + "$" + self.inexpr[0].toLatex(context, ind+2, subs) + "$\n" 
        res += ind*" " + "$)\left[" + self.cond.toLatex(context, ind, subs) + "\\right]"
        return res
    

    def toEG(self): 
        return "Iv["+ str(self.cond) +"]"

    def __buildout(self, src):
        
        return src.duplicate("iv")

##############################################
#--------------IMFs--------------------------#
##############################################

class MappingException(Exception):
    pass

class Index(object):
    def __init__(self, i, b, e, s, isTop=False):
        name = i+str(globalSSAIndex())
        self.i = sympify(name)
        self.b = sympify(b)
        self.e = sympify(e)
        self.s = sympify(s)
        self.isTop = isTop
        self.beenReinit = False
    
    def getSyms(self):
        res = set()
        res.update(self.b.atoms(Symbol))
        res.update(self.e.atoms(Symbol))
        res.update(self.s.atoms(Symbol))
        return res
    
    def hasSym(self, sym):
        return self.i == sym
    
    def isPure(self):
        return not ( self.b.atoms(Symbol) or self.e.atoms(Symbol) or self.s.atoms(Symbol) )
    
    def equivalent(self, idx):
        return self.b == idx.b and self.e == idx.e and self.s == idx.s and self.isTop == idx.isTop 
    
    def subs(self, idsDict):
        self.i = self.i.subs(idsDict)
        self.b = self.b.subs(idsDict)
        self.e = self.e.subs(idsDict)
        self.s = self.s.subs(idsDict)
        
    def reinit(self, newb=None, newe=None, news=None):
        if newb is not None:
            self.b = sympify(newb)
        if newe is not None:
            self.e = sympify(newe)
        if news is not None:
            self.s = sympify(news)
        self.beenReinit = True
    
    def set(self, b, e, s):
        self.b = sympify(b)
        self.e = sympify(e)
        self.s = sympify(s)
        self.beenReinit = False
    
    def needsLoop(self, reqSubs=None):
        if reqSubs is None:
            reqSubs = [ {} ]
        v = self.e - self.b - self.s
        return any(map(lambda reqSub: v.subs(reqSub) > sympify(0), reqSubs)) 
    
    def assumesOneValue(self):
        return self.isPure() and (self.b + self.s - self.e >= 0)
    
    def __repr__(self):
        return str(self.i) + " < b=" + str(self.b) + ", e=" + str(self.e) + ", s=" + str(self.s) + (", Top" if self.isTop else "") + " >"
    
#     def __deepcopy__(self, memo):
#         res = Index('xxx', self.b, self.e, self.s, self.isTop)
#         res.i = self.i
#         res.beenReinit = self.beenReinit
#         return res
    
class IMF(object):
    def __init__(self, n, N,func=None,i=None):
        super(IMF, self).__init__()
        self.n,self.N = sympify(n, locals=sym_locals), sympify(N, locals=sym_locals)
        self.i = sympify('__i') if i is None else i
        self.func = func

    def subs(self, d):
        res = IMF(self.n.subs(d), self.N.subs(d))
        res.func = self.func.subs(d)
        return res

    def of(self, i):
        if self.func is None: return None
        res = self.func.subs(self.i, i)
        if res.is_Number and self.N.is_Number and res >= self.N:
            raise MappingException
        return res
    
    def getAtoms(self):
        return self.of(0).atoms(Symbol)
    
    def compose(self, f):
        if self.func is None or f.func is None: return None
        res = IMF(f.n, self.N)
        res.func = self.func.subs(self.i, f.func)
        res.i = f.i
        return res
    
    def isfI(self):
        return self.n == self.N and self.func == self.i
    
    def getConstraint(self, idx, bounds, lbs):
        if self.n == 1:
            res = idx + " = " + str(self.of(0)).subs(bounds).subs(lbs)
        else:
            s = self.of(1)-self.of(0)
            lb = self.of(0).subs(bounds).subs(lbs)
            ub = self.of(self.n-1).subs(bounds).subs(lbs)
            res = str(lb) + " <= " + idx + " <= " + str(ub) + " and exists a: " + idx + " = "+str(s)+"a"
        return res
            
    def __repr__(self):
        return str(self)

    def toLatex(self, context, ind=0, subs=None):
        subs = {} if subs is None else subs
        res = str(self.func.subs({self.i:0}))
        for sub in subs:
            res = res.replace(sub, subs[sub])
        return res
    
    def __str__(self):
#         return "IMF : I_" + str(self.n) + " -> I_" + str(self.N) + " ; " + str(self.i) + " |-> " + str(self.func)  
        return "f(" + str(self.n) + ", " + str(self.N) + ", " + str(self.func) + ", " + str(self.i) + ")"  
    
    def __eq__(self, other):
        return self.n == other.n and self.N == other.N and self.func == other.func
    
class fHbs(IMF):
    def __init__(self, n, N, b, s=1):
        super(fHbs, self).__init__(n, N)
        self.name = "h"
        self.b,self.s = sympify(b, locals=sym_locals), sympify(s, locals=sym_locals)
        self.func = b + self.i*s

    def subs(self, d):
        res = fHbs(self.n.subs(d), self.N.subs(d), self.b.subs(d), self.s.subs(d))
        return res

    def replace(self, new, old):
        res = fHbs(self.n.simplify().replace(new, old), self.N.simplify().replace(new, old), self.b.simplify().replace(new, old), self.s.simplify().replace(new, old))
        return res

    def replace_self(self, new, old):
        self.n = self.n.replace(new, old)
        self.N = self.N.replace(new, old)
        self.b = self.b.replace(new, old)
        self.s = self.s.replace(new, old)

    def compose(self, f):
        if isinstance(f, fHbs):
            return fHbs(f.n, self.N, self.b+self.s*f.b, self.s*f.s)
        return super(fHbs, self).compose(f)

    def match(self, sym_expr):
        res = []
        for e in [self.n, self.N, self.b, self.s]:
            res.append( e.match(sym_expr) )
        return res
    
    def use_floord_ceild(self):
        a,b = Wild('a'), Wild('b', exclude=[sympy.Add, sympy.Symbol], properties=[lambda f: f>0])
        floord = sympy.Function('floord')
        ceild = sympy.Function('ceild')
        self.replace_self(sympy.floor(a/b), lambda a,b: floord(a,b))
        self.replace_self(sympy.ceiling(a/b), lambda a,b: ceild(a,b))
        
    def use_floor_ceiling(self):
        a,b = Wild('a'), Wild('b', exclude=[sympy.Add, sympy.Symbol], properties=[lambda f: f>0])
        floord = sympy.Function('floord')
        ceild = sympy.Function('ceild')
        self.replace_self(floord(a,b), lambda a,b: sympy.floor((a.together()/b.together()).together()))
        self.replace_self(ceild(a,b), lambda a,b: sympy.ceiling((a.together()/b.together()).together()))
    
    def __str__(self):
#         return self.name + " : I_" + str(self.n) + " -> I_" + str(self.N) + " ; " + str(self.i) + " |-> " + str(self.func)
#         return str(self.b)

        a,b = Wild('a'), Wild('b', exclude=[sympy.Add, sympy.Symbol], properties=[lambda f: f>0])
        floord = sympy.Function('floord')
        ceild = sympy.Function('ceild')
        srep = self.replace(sympy.floor(a/b), lambda a,b: floord(a,b))
        srep = srep.replace(sympy.ceiling(a/b), lambda a,b: ceild(a,b))
            
        if self.s > sympify(1):
            sfhbs = "h(" + str(srep.n) + ", " + str(srep.N) + ", " + str(srep.b) + ", " + str(srep.s) + ")"
        else:  
            sfhbs = "h(" + str(srep.n) + ", " + str(srep.N) + ", " + str(srep.b) + ")"
        return sfhbs
        
class fI(fHbs):
    def __init__(self, n):
        super(fI, self).__init__(n, n, 0, 1)
        self.name = "i"

    def __str__(self):
        return "fI(" + str(self.n) + ")"  


if __name__ == "__main__":
    
#     T0 = constant_matrix_type_with_value(0)
#     print constant_matrix_type_with_value(1) == constant_matrix_type_with_value(2)
#     struct = {ZeroMatrix: Set("{[i,j]: 0<=i<4 and 0<=j<4}")}
#     print T0.test(struct, None, 4, 0) 
#     
#     h = fHbs(sympy.sympify("floord(floord(17-fi,4),4)"), sympy.sympify(4), 0, 1)
    if __VERBOSE__:
        m = Matrix('name', Empty(), (2,0))
        m1 = Matrix('name', Empty(), (2,0))
        print (m+m1).get_pot_zero_dims()
    
