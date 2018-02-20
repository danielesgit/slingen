'''
Created on May 9, 2014

@author: danieles
'''

import sympy
from copy import deepcopy
from itertools import ifilter
import sys
import importlib
from ConfigParser import ConfigParser

from src.dsls.ll import Quantity, Operator, Tile, ParamMat, Iv, llLoop, llGuard,\
    llBlock

def parse_config_file(conf_file, ignore_non_existent_file=False, opts=None):
    ''' Parse the given configuration file and return a dict with its contents.
    
    opts and curr are configurations that can be accessed from within the [code] section of conf_file.
    curr is the current processed file, opts the current complete set of options (curr excluded).
    '''
    opts = {} if opts is None else opts
    curr = {}
    parser = ConfigParser()
    found = parser.read(conf_file)
    if len(found) > 0:
        if parser.has_section('string'):
            # Load string options
            for item in parser.items('string'):
                curr[item[0]] = item[1].replace("\n", " ")
        if parser.has_section('code'):
            # Load code options
            for item in parser.items('code'):
                curr[item[0]] = eval(item[1]) if item[1] else ''
        if parser.has_section('loadmod'):
            for item in parser.items('loadmod'):
                modpair = eval(item[1])
                mod = importlib.import_module(modpair[0])
                curr[item[0]] = getattr(mod, modpair[1])
        if parser.has_section('withopts'):
            for item in parser.items('withopts'):
#                 res[item[0]] = eval(item[1])(opts).getOpt() if item[1] else ''
                modpair = eval(item[1])
                mod = importlib.import_module(modpair[0])
                if isinstance(modpair[1], list):
                    curr[item[0]] = []
                    for Cls in modpair[1]:
                        curr[item[0]].append( getattr(mod, Cls)(opts).getOpt() )
                else:
                    curr[item[0]] = getattr(mod, modpair[1])(opts).getOpt()
#         if 'vectorize' in res:
#             if not res['vectorize'] or res['nu'] == 1:
#                 res['nu'] = 1
#                 res['vectorize'] = False
        if 'useintrinsics' in curr:
            if not curr['useintrinsics']:
                curr['nu'] = 1
    else:
        if not ignore_non_existent_file:
            print "Configuration file " + conf_file + " not available."
            sys.exit(1)
    return curr
        

# def markInnermostSums(sllprog):
#     for s in sllprog.stmtList:
#         applyMarking(s.eq)
# 
# def applyMarking(sexpr):
#     '''
#     Mark the innermost loop and in that case report it was found
#     '''
#     if isinstance(sexpr, Operator):
#         found = False
#         if isinstance(sexpr, NewSum):
#             found = applyMarking(sexpr.inexpr[0])
#             if not found:
#                 found = sexpr.ann['innermost'] = True
#         else:
#             for sub in sexpr.inexpr:
#                 found = found or applyMarking(sub)
#     return found

# def applyUnrollingPolicies(sllprog, opts):
#     for s in sllprog.stmtList:
#         baseUFs = { i : 1 for i in s.ann['indices'] }
#         opts['baseufs'] = baseUFs
#         opts['ufslist'] = [ ]
#         uFs = { i : [1] for i in s.ann['indices'] }
#         s.eq.computeUnrolling(uFs, s.ann['indices'], 3 if opts['vectorize'] else 2)
#         uFs = { i : max(uFs[i]) for i in s.ann['indices'] }
#         if uFs != baseUFs:
#             opts['ufslist'].append(uFs)
        
#########################################
#----------- Graph Processing -----------
#########################################

def searchHandle(handle, expr):
    if expr.handle == handle: return expr
    if isinstance(expr, Quantity): return None 
    for e in expr.inexpr:
            res = searchHandle(handle, e)
            if res is not None: return res
    return None

def searchGenHandle(handle, expr, getHandle, succFunc):
    if getHandle(expr) == handle: return expr
    for e in succFunc(expr):
            res = searchGenHandle(handle, e, getHandle, succFunc)
            if res is not None: return res
    return None

def duplicateEG(expr):
    if expr.pred[0][0] is None:
        return expr.duplicate()
    return duplicateEG(expr.pred[0][0])

def duplicateHG(holo):
    if len(holo.pred) == 0:
        return deepcopy(holo)
    return duplicateHG(holo.pred[0][0])

def getToRoot(expr):
    if expr.pred[0][0] is None:
        return expr
    return getToRoot(expr.pred[0][0])

def duplicateAtHandle(expr):
    newRoot = duplicateEG(expr)
    return (newRoot, searchHandle(expr.handle, newRoot))    

def duplicateAtHandleHolo(holo):
    newRoot = duplicateHG(holo)
    return (newRoot, searchGenHandle(id(holo.node), newRoot, lambda h: id(h.node), lambda h: h.succ))    

def trackTiling(expr, ttDict, explored=None):
    if explored is None:
        explored = []
    
    if str(expr) in explored:
        return (False, None)
    else: 
        explored.append(str(expr))
        if isinstance(expr, Operator):
            for sub in expr.inexpr:
                tt = trackTiling(sub, ttDict, explored)
                if tt[0] and isinstance(expr, Tile):
                    dm, dn = tt[1] + "_M", tt[1] + "_N" 
                    ttDict[dm][-1].append(expr.nu[0])
                    ttDict[dn][-1].append(expr.nu[1])
                    return tt
            return (False, None)
        if 'tt' in expr.attr and expr.attr['tt']:
            dm, dn = expr.name + "_M", expr.name + "_N" 
            if dm not in ttDict:
                ttDict[dm], ttDict[dn] = [[]], [[]]
            else:
                ttDict[dm].append([]) # In case of multiple different tilings the matrix is associated to multiple lists
                ttDict[dn].append([]) # of tiling choices
            return (True, expr.name)
        return (False, None)
    
#################################################
#----------- Dependencies Processing -----------
#################################################

def resetDependencies(expr, opts, explored):
    expr.depSet.clear()

    if isinstance(expr, Operator) and not expr in explored:
        explored.append(expr)
        for sub in expr.inexpr:
            resetDependencies(sub, opts, explored)

def replaceWith(expr, oldSub, newSub, explored):
    
    if expr.same(oldSub):
        for p in expr.pred:
            p[0].inexpr[p[1]] = newSub
            p[0].setAsPredOfInExpr(p[1])
            return

    if isinstance(expr, Operator) and not expr in explored:
        explored.append(expr)
        for inexpr in expr.inexpr:
            replaceWith(inexpr, oldSub, newSub, explored)

    
# def computeDependencies(expr, opts, explored):
def computeDependenciesEquation(expr, opts):
    mat = expr.getOut()
    
    if isinstance(expr, Operator):
        for sub in expr.inexpr:
            computeDependenciesEquation(sub, opts)
    
    # indices may be contained within the origin of the matrix or within the index mapping functions expressions
    atomSrc = [mat.o[0], mat.o[1], mat.fL.of(0), mat.fR.of(0)]
    if isinstance(expr, ParamMat):
        atomSrc += [ expr.fL.of(0), expr.fR.of(0) ]
    if isinstance(expr, Iv):
        expr.deepUpdateDep(expr.cond.getSymAtoms())
    for e in atomSrc:
        if isinstance(e, sympy.Expr):
            expr.depSet.update(e.atoms(sympy.Symbol))
    if isinstance(expr, Operator):
        for sub in expr.inexpr:
            expr.depSet.update(sub.depSet)
    
    return expr

def _computeDependencies(expr, opts):
    if isinstance(expr, llBlock):
        for s in expr:
            _computeDependencies(s, opts)
    elif isinstance(expr, llLoop):
        _computeDependencies(expr.body, opts)
    elif isinstance(expr, llGuard):
        for b in expr.bodys:
            _computeDependencies(b, opts)
    else:
        computeDependenciesEquation(expr.eq, opts)

def computeDependencies(sllprog, opts):
    _computeDependencies(sllprog.stmtList, opts)

def substituteIndices(expr, subsDict, opts, explored):
    mat = expr.getOut()
    
    if isinstance(expr, Operator) and not expr in explored:
        explored.append(expr)
        for sub in expr.inexpr:
            substituteIndices(sub, subsDict, opts, explored)
    
    # indices may be contained within the origin of the matrix or within the index mapping functions expressions
    # We take size into account because we should replace outer indices (I,J,..) too.
    mat.o = (mat.o[0].subs(subsDict), mat.o[1].subs(subsDict))
    mat.fL, mat.fR = mat.fL.subs(subsDict), mat.fR.subs(subsDict)
    if isinstance(expr, ParamMat):
        expr.fL, expr.fR = expr.fL.subs(subsDict), expr.fR.subs(subsDict)

def printDependencies(expr, opts, explored):
    print expr.__class__.__name__ + ": " + str(expr.depSet)

    if isinstance(expr, Operator) and not expr in explored:
        explored.append(expr)
        for sub in expr.inexpr:
            printDependencies(sub, opts, explored)

# def computeIndependentSubexprWithBounds(expr, idxList, bounds, explored, opts):
def computeIndependentSubexprWithBounds(expr, idxList, bounds, genopts, opts):
    '''
    Determine the first subexprs that don't depend upon the list of indices
    '''
    res = []
#     if not any(map(lambda idx: idx in expr.depSet and opts['unroll'][str(idx)] == 0, idxList)):
    if not any(map(lambda idx: idx in expr.depSet, idxList)):
        res += [(expr, genopts)]
        return res
    
    if isinstance(expr, Operator):
        for sub in expr.inexpr:
            res += computeIndependentSubexprWithBounds(sub, idxList, bounds, genopts, opts)
    return res

def computeIndependentSubexpr(expr, idxList, explored, opts):
    '''
    Determine all the subexpressions of expr that don't depend upon the list of indices in idxList.
    '''
    res = []
    if not any(map(lambda idx: idx.i in expr.depSet, idxList)):
        res += [expr]
        return res
    
    if isinstance(expr, Operator) and not expr in explored:
        explored.append(expr)
        for sub in expr.inexpr:
            res += computeIndependentSubexpr(sub, idxList, explored, opts)
    return res

def computeDependentSubexprOfType(expr, idxList, explored, opts, vtype=None):
    '''
    Determine the list of subexprs that depend upon any of the indices in the list.
    If a type is given, only expressions of that type are considered.
    '''
    res = []
    if not any(map(lambda idx: idx.i in expr.depSet, idxList)):
        return res
    
    if vtype is not None:
        if isinstance(expr, vtype):
            res += [expr]
    else:
        res += [expr]
        
    if isinstance(expr, Operator) and not expr in explored:
        explored.append(expr)
        for sub in expr.inexpr:
            res += computeDependentSubexprOfType(sub, idxList, explored, opts, vtype)
    
    return res

#------------------ Indices Processing -------------------

def reorderIdxList(idxList, iPriority, opts):
    order = opts['indexorder']
    for idx in iPriority:
        p = iPriority[idx]
        t = ( p[order[0]], p[order[1]], p[order[2]] )
        iPriority[idx] = t
    ordPrioList = sorted(iPriority.items(), key=lambda idxp: idxp[1])
    ordSym = [ idxp[0] for idxp in ordPrioList ]
    ordIdxList = [None]*len(idxList)
    for idx in idxList:
        ordIdxList[ordSym.index(idx.i)] = idx
    return ordIdxList

def separateLeftRight(l):
    #((l1,r1), (l2,r2), ...) -> ((l1, l2, ...), (r1, r2, ...)) where li and ri are sets
    left = []
    right = []
    for t in l:
        left.append(t[0])
        right.append(t[1])
    return tuple(left), tuple(right)

def separatePureIds(idsSet):
    pure = set()
    impure = set()
    
    for idx in idsSet:
        pure.update( [idx] ) if idx.isPure() else impure.update( [idx] )
    
    return pure, impure

def checkAndStore(set1, set2, d):
    temp = set()
    while set1:
        idx1 = deepcopy(set1.pop())
        idx1.subs(d)
        idx2 = next(ifilter(lambda i: i.equivalent(idx1), set2), None)
        if idx2 is not None:
            d[idx1.i] = idx2.i
            temp.update( [idx2] )
            set2.remove(idx2)
    set2.update(temp)
        
def createSubsDict(list1, list2):
    # Compare the two lists (see applyMerge for the matrix )
    # and create a dictionary for substitution of the following form: {item_from_1: item_from_2} 
    res = {}
    
    left1, right1 = separateLeftRight(list1)
    left2, right2 = separateLeftRight(list2)
    
    pure2, impure2 = separatePureIds(left2[0])
    for s in left1:
        pure1,impure1 = separatePureIds(s)
        checkAndStore(pure1, pure2, res)
        checkAndStore(impure1, impure2, res)
        
    pure2, impure2 = separatePureIds(right2[0])
    for s in right1:
        pure1,impure1 = separatePureIds(s)
        checkAndStore(pure1, pure2, res)
        checkAndStore(impure1, impure2, res)
        
    return res
