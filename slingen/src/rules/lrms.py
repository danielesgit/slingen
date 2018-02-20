'''
Created on Jan 23, 2015

@author: danieles
'''

import shlex
import subprocess
import re
import string
import sys
import os
import itertools
import math
import importlib

from copy import deepcopy
from random import sample
from itertools import product
from sympy import sympify

from islpy import Set

from src.dsls.ll import Quantity, Matrix, G, Kro, Div, llProgram, llBlock, llIf, llFor, llStmt, constant_matrix_type_with_value,\
    Assign, scalar_block, fHbs, globalSSAIndex, get_expr_bound_over_domain,\
    CartesianProduct, QuantityCartesianProduct
from src.dsls.processing import duplicateAtHandle, duplicateAtHandleHolo


class LRM(object):
    '''
    LRM - L-Rules Manager
    '''
    def __init__(self, measMgr, opts):
        super(LRM, self).__init__()
        self.opts = opts
        self.rank = {}
        self.current = None
        self.measManager = measMgr

    def insertMeasurement(self, meas):
        if self.current is not None:
            if self.rank[self.current][0] is not None:
                if self.measManager.compare(meas, self.rank[self.current]) > 0:
                    self.rank[self.current] =  meas
            else:
                self.rank[self.current] =  meas  

    def getBestMeasurement(self):
#         return max(self.rank.iteritems(), key=itemgetter(1))
        return self.measManager.getBestMeasurement(self.rank)

    def getRankItems(self):
        rItems = [ i for i in self.rank.items() if i[1][0] is not None ]
        return rItems

    def count(self):
        rItems = [ i for i in self.rank.items() if i[1][0] is not None ]
        return len(rItems)

    def dumpRank(self, fname):
        self.measManager.dumpRank(fname, self.rank)
# 
#     def count(self):
#         return len(self.rank)
    

class SimpleLRM(LRM):
    def __init__(self, expr, measMgr, opts):
        super(SimpleLRM, self).__init__(measMgr, opts)
#         self.opts = opts
        self.roots = [expr]
        self.initIterator()

    def initIterator(self):
        self.iter = ( e for e in self.roots ) # Create a generator for the expressions
    
    def next(self):
        try:
            _next = self.iter.next()
        except StopIteration:
            _next = None
        self.current = _next
        return _next
    
    def __str__(self):
        return "SimpleLRM"
    
class OfflineLRM(LRM):
    def __init__(self, expr, measMgr, opts):
        super(OfflineLRM, self).__init__(measMgr, opts)
#         self.opts = opts
        self.roots = [expr]
        self.generated = []
        self.newRoots = [] 
        self.links = {}
        self.populate()
        self.initRank()
        self.random = opts['random']
        self.limit = opts['limit']
        self.initIterator()

    def initIterator(self):
        if self.random:
            k = self.limit if (self.limit > 0 and self.limit < len(self.rank)) else len(self.rank)
            samp = sample(self.rank, k)
        else:
            samp = self.rank
        self.iter = ( e for e in samp ) # Create a generator for the expressions
        
    def next(self):
        try:
            _next = self.iter.next()
        except StopIteration:
            _next = None
        self.current = _next
        return _next
    
    def initRank(self):
        for e in self.links:
            if self.links[e] == []:
                self.rank[e] = [ None ]
        
    def populate(self): 
        self.apply()
        while(self.newRoots):
            self.roots = self.newRoots
            self.newRoots = []
            self.generated = []
            self.apply()
            
    def apply(self): 
        for root in self.roots:
            self.actualRoot = root
            self.links[self.actualRoot] = []
            self._apply(root)
#         self.newRoots = [ e for e in self.generated if self.links[e] == [] ]
        self.newRoots = [ e for e in self.links if not self.links[e] and e in self.generated ] # Condition filters out leaves in the link connections that are not from current apply

    def _apply(self, expr):
        rs = self.opts['lrs']
        ruleList = filter(lambda rr: rr.applicable(expr), rs[expr.__class__.__name__]) if expr.__class__.__name__ in rs else []

        if ruleList:
            for r in ruleList:
                choices = r.genChoices(expr)
                for c in choices:
                    rootHandle = duplicateAtHandle(expr) #returns tuple (newroot, exprHandle)
                    newExpr = r.apply(rootHandle[1], c)
                    newRoot = newExpr if newExpr.pred[0][0] is None else rootHandle[0] 
                    self.links[self.actualRoot].append((r, c, newRoot))
                    self.generated.append(newRoot)
                    tempRoot = self.actualRoot
                    self.actualRoot = newRoot
                    self.links[self.actualRoot] = []
                    self._apply(newExpr)
                    self.actualRoot = tempRoot 
        else:
            if not isinstance(expr, Quantity):
                for inexpr in expr.inexpr:
                    self._apply(inexpr)
    
    def __str__(self):
        limit = (" with limit = " + str(self.limit) if self.limit > 0 else " exhaustive")
        rand = (" random" + limit if self.random else " exhaustive")
        return "OfflineLRM" + rand + " - Gen Expr count: " + str(len(self.rank))

class HOfflineLRM(LRM):
    """
    LRM processing holographs. Mind: there cannot be two realgraphs at once as they are created combining same real nodes.
    """
    def __init__(self, init_llprog, rs_list, measMgr, opts):
        super(HOfflineLRM, self).__init__(measMgr, opts)
#         self.roots = [expr.getHolograph()]
        self.rank_by_variants = {}
        
        self.nublac = opts['isaman'].getNuBLAC(opts['precision'], opts['nu'])
        self.rs_sca = rs_list[0]

        self.random = opts['random']
        self.limit = opts['limit']

        if opts['useintrinsics']:
            self.rs_nu = rs_list[1]
        else:
            self.rs_nu = self.rs_sca 
        
        print "\nSynthesis of basic linear algebra LL programs...\n"
        llprogs = self.algogen(init_llprog)   
        print "All variants are now available.\n"
        
#TODO: This part should be made rule-based.        
        for i,llprog in enumerate(llprogs):
            print "Processing variant %d with non-iterative rules...\n" % (i)
            self._reduce_divs(llprog)

        fixedchoices_fname = opts.get('fixedchoices', None)
        if fixedchoices_fname:
            print "\nUsing fixed choices in: %s\n" % fixedchoices_fname
            with open(fixedchoices_fname, 'r') as f:
                self.fixedchoices = eval(''.join(f.readlines()))
        else:
            self.fixedchoices = None 
        
        self.holoLLProgTrack = {}
        for i,llprog in enumerate(llprogs):
            print "Processing variant %d...\n" % (i)
            if 'variant_tag' in llprog.ann:
                self.rank_by_variants[llprog.ann['variant_tag']] = [None]
            self.holoLlProg = llprog.getHolograph()
#             self.holoEqs = self.holoLlProg.getEqsList()
            self.holoStmts = self.holoLlProg.getStmtList()
            if opts['useintrinsics']:
                print "  - Computing can-vec list...\n"
                self.can_vec_list = llprog.get_can_vec_with_nublac_list(self.nublac)
            else:
                self.can_vec_list = [False]*len(self.holoStmts)
            self.candidateEqs = {}
            print "  - Populating...\n"
            self.populate()
            print "  - Initializing rank...\n"
            self.initRank()
            print "Done processing %d.\n" % (i)
        print "Initializing iterator...\n"
        self.initIterator()
        print "Done.\n"

#     def _getHoloEqs(self, expr):
#         res = []
#         if isinstance(expr, llBlock):
#             for s in expr:
#                 res.extend( self._getHoloEqs(s) )
#         elif isinstance(expr, llLoop):
#             res.extend( self._getHoloEqs(expr.body) )
#         elif isinstance(expr, llGuard):
#             for b in expr.bodys:
#                 res.extend( self._getHoloEqs(b) )
#         else:
#             res.append(expr.eq)
#         return res

#     def _group_divs(self, llprog):
#         fusible_stmts = []
#         self._filter_fusible_stmts(llprog.stmtList, fusible_stmts)
#         prep_stmts = [self._prep_fuse_stmts(fss) for fss in fusible_stmts]
#         self._replace_stmts(llprog, fusible_stmts, prep_stmts)
#         self._hoist_divs(llprog)
#         llprog.update_info()
    
    def _reduce_divs(self, llprog):
        fusible_stmts, directions = [], []
        self._filter_fusible_stmts(llprog.stmtList, fusible_stmts, directions)
        prep_stmts = [self._prep_fuse_stmts(fss, direction) for fss, direction in zip(fusible_stmts, directions)]
        self._replace_stmts(llprog, fusible_stmts, prep_stmts)
        self._hoist_divs(llprog)
        llprog.update_info()
        
#         with open('/tmp/llprog.ll', 'w') as f:
#             f.write(llprog.toLL())

    def _hoist_divs(self, expr, ctx=None, cur_blk=None):
        res = []
        if isinstance(expr, llProgram):
            self._hoist_divs(expr.stmtList, ctx, cur_blk)
        elif isinstance(expr, llBlock):
            for s in expr:
                res.extend( self._hoist_divs(s, ctx, expr) )
        elif isinstance(expr, llFor):
            tmp = self._hoist_divs(expr.body, expr, cur_blk)
            for llstmt in tmp:
                if ctx is None or llstmt.eq.dependsOn(ctx.idx):
                    cur_blk.insert(cur_blk.index(expr), llstmt)
                else:
                    res.append(llstmt)
        elif isinstance(expr, llIf):
            for b in expr.bodys:
                res.extend( self._hoist_divs(b, ctx, cur_blk) )
        elif isinstance(expr, llStmt):
            if ctx is not None and not expr.eq.dependsOn(ctx.idx):
                cur_blk.remove(expr)
                res.append(expr)
        return res

    def _replace_stmts(self, llprog, fusible_stmts, prep_stmts):
        one_type = constant_matrix_type_with_value( sympify(1) )
        divmats_dict = {}
        divlhs_dict = {}
        for fss,prep in zip(fusible_stmts, prep_stmts):
            if prep is not None:
                lhs, rhs, divisor = prep
                div_out = divisor.inexpr[0].getOut()
                if div_out.name not in divmats_dict: 
                    tname = 'T'+str(globalSSAIndex())
                    llprog.mDict[tname] = tmat = Matrix(tname, scalar_block(), (1,divisor.inexpr[0].getOut().size[1]), attr={ 't':True, 'o':True })
                    divmats_dict[div_out.name] = tmat
                
                blk = fss[0][0] 
                one = one_type('1', scalar_block(), (1,1))
                division = Div(one, divisor)
                prev_div = filter(lambda div: div.sameUpToNames(division), divlhs_dict)
                if not prev_div:
                    div_lhs = G(fHbs(1,1,0), divmats_dict[div_out.name], deepcopy(divisor.fR))
                    div_stmt = llStmt(Assign(div_lhs, division))
                    blk.insert(blk.index(fss[0][1]), div_stmt)
                    divlhs_dict[division] = div_lhs
                else:
                    div_lhs = divlhs_dict[prev_div[0]]
                
                rcp_mul_stmt = llStmt( Assign(lhs, Kro(div_lhs.duplicate(), rhs)) )
                blk.insert(blk.index(fss[0][1]), rcp_mul_stmt)
                for fs in fss:
                    blk.remove(fs[1])
            
    def _prep_fuse_stmts(self, fusible_stmts, direction):
        if len(fusible_stmts) <= 1:
            return None
#         mat_type = constant_matrix_type_with_value( sympify(1) )
#         one = mat_type('1', scalar_block(), (1,1))
        leq = fusible_stmts[0][1].eq
        sub_gatl = leq.inexpr[0].inexpr[0].duplicate()
        sub_gatr = leq.inexpr[1].inexpr[0].inexpr[0].duplicate()
        divisor = leq.inexpr[1].inexpr[1].duplicate()
        if direction == 'hor':
            l_fL, l_fR = deepcopy(leq.inexpr[0].fL), fHbs(len(fusible_stmts), leq.inexpr[0].fR.N, leq.inexpr[0].fR.b)
            r_fL, r_fR = deepcopy(leq.inexpr[1].inexpr[0].fL), fHbs(len(fusible_stmts), leq.inexpr[1].inexpr[0].fR.N, leq.inexpr[1].inexpr[0].fR.b)
        elif direction == 'ver':
            l_fL, l_fR = fHbs(len(fusible_stmts), leq.inexpr[0].fL.N, leq.inexpr[0].fL.b), deepcopy(leq.inexpr[0].fR)
            r_fL, r_fR = fHbs(len(fusible_stmts), leq.inexpr[1].inexpr[0].fL.N, leq.inexpr[1].inexpr[0].fL.b), deepcopy(leq.inexpr[1].inexpr[0].fR)
        lhs = G(l_fL, sub_gatl, l_fR)
        dividend = G(r_fL, sub_gatr, r_fR)
        res = (lhs, dividend, divisor)
        return res
    
    def _filter_fusible_stmts(self, expr, fus_stmts, directions, cur_blk=None):
        if isinstance(expr, llBlock):
            for s in expr:
                self._filter_fusible_stmts(s, fus_stmts, directions, expr)
        elif isinstance(expr, llFor):
            if fus_stmts and fus_stmts[-1]:
                fus_stmts.append([])
            self._filter_fusible_stmts(expr.body, fus_stmts, directions)
        elif isinstance(expr, llIf):
            if fus_stmts and fus_stmts[-1]:
                fus_stmts.append([])
            for b in expr.bodys:
                self._filter_fusible_stmts(b, fus_stmts, directions)
        elif isinstance(expr, llStmt):
            if isinstance(expr.eq.inexpr[1], Div) and all([ isinstance(e, G) for e in expr.eq.inexpr[:1]+expr.eq.inexpr[1].inexpr]):
                if not fus_stmts:
                    fus_stmts.append([]) #New matrix of stmts
                if not fus_stmts[-1]:
                    fus_stmts[-1].append( (cur_blk, expr) )
                    directions.append(None)
                else:
                    add_new = True
                    any_prev = fus_stmts[-1][0] #first elem of last list of stmts
                    prev_gat_subs = [ g.inexpr[0] for g in any_prev[1].eq.inexpr[:1]+any_prev[1].eq.inexpr[1].inexpr ]
                    curr_gat_subs = [ g.inexpr[0] for g in expr.eq.inexpr[:1]+expr.eq.inexpr[1].inexpr ]
                    if cur_blk == any_prev[0] and all([ csub.sameUpToNames(psub) for csub,psub in zip(curr_gat_subs, prev_gat_subs)])\
                        and any_prev[1].eq.inexpr[1].inexpr[1].sameUpToNames(expr.eq.inexpr[1].inexpr[1]): #same divisor
                        leq, req = fus_stmts[-1][0][1].eq, fus_stmts[-1][-1][1].eq
                        subs_to_test = [(leq.inexpr[0], req.inexpr[0], expr.eq.inexpr[0])]
                        subs_to_test.append( (leq.inexpr[1].inexpr[0], req.inexpr[1].inexpr[0], expr.eq.inexpr[1].inexpr[0]) )
                        add_l, add_r = [], []
                        # Check horizontally 
                        direction = 'hor'
                        for l,r,e in subs_to_test:
                            add_l.append(False)
                            add_r.append(False)
                            if l.fR.of(0)-1 == e.fR.of(0) and l.fL.of(0) == e.fL.of(0):
                                add_l[-1] = True
                            elif r.fR.of(0)+1 == e.fR.of(0) and r.fL.of(0) == e.fL.of(0):
                                add_r[-1] = True
                        if not (all(add_l) or all(add_r)):
                            # Check vertically
                            direction = 'ver'
                            del add_l[:] 
                            del add_r[:] 
                            for l,r,e in subs_to_test:
                                add_l.append(False)
                                add_r.append(False)
                                if l.fL.of(0)-1 == e.fL.of(0) and l.fR.of(0) == e.fR.of(0):
                                    add_l[-1] = True
                                elif r.fL.of(0)+1 == e.fL.of(0) and r.fR.of(0) == e.fR.of(0):
                                    add_r[-1] = True
                        
                        if all(add_l):
                                directions[-1] = direction
                                fus_stmts[-1].insert(0, (cur_blk, expr) )
                                add_new = False
                        elif all(add_r):
                                directions[-1] = direction
                                fus_stmts[-1].append( (cur_blk, expr) )
                                add_new = False
                        
                    if add_new:
                        fus_stmts.append([])
                        fus_stmts[-1].append( (cur_blk, expr) )
                        directions.append(None)
                        
    
    def insertMeasurement(self, meas, variant_tag=None):
        super(HOfflineLRM, self).insertMeasurement(meas)
        if variant_tag is not None and self.current is not None:
            if self.measManager.compare(meas, self.rank_by_variants[variant_tag]) > 0:
                self.rank_by_variants[variant_tag] =  meas #???
#             else:
#                 self.rank_by_variants[variant_tag] =  meas  
            
    
    def to_tuples_of_tuples(self, it):
        final = []
        for t in it:
            if type(t[0]) is tuple:
                final.extend(t)
            else:
                final.append(t)
        return tuple(final)
    
    def _algogen_setup_func(self, eq_info):
        signature = eq_info[0]
        stmt = eq_info[1][ eq_info[2] ]
        algo_db = self.opts['algodb']+'/' + signature + "_opt"
        ck_prog, dims_map, in_expr_list, out_expr_list = stmt.to_algo()
        if not os.path.exists(algo_db):
            in_name = "%s/results/%s/alg/%s.ck" % (self.opts['logroot'], self.opts['testname'], signature)
            with open(in_name, 'w') as f:
                f.write(ck_prog)
            
            algogen_cmd = "bash -c \"source ..\py35env/bin/activate && "
            algogen_cmd += "cd src/algogen && ./AlgoGen %s %s" % ('--ll --size multiple-of-nu --opt', in_name)
            algogen_cmd += " && deactivate\""
            args = shlex.split(algogen_cmd)
            print algogen_cmd
            ret = subprocess.call(args)
            if ret>0:
                sys.exit("Algorithmic synthesis Error.")
        return dims_map, in_expr_list, out_expr_list
            
        
    def algogen(self, init_llprog):
        nublac = self.opts['isaman'].getNuBLAC(self.opts['precision'], self.opts['nu'])
        v, vv = 0, 0
        llprogs = []
        llprog = None
        partitionings, obtained_funcs = [None], []
        tmp_re = re.compile(r"@T\d*@")
        
        while (llprog is None) or partitionings: 
            llprog = deepcopy(init_llprog)
#             prev_func = func = None
            prev_signature = signature = None
#             eq_info = llprog.get_first_func_nongen_with_nublac(nublac)
            eq_info = llprog.get_first_eq_nongen_with_nublac(nublac)
            if eq_info:
                params = '-'.join(str(p) for p in self.opts['static_params'])
                destfilebase = '%s/results/%s/alg/%s/%d' % (self.opts['logroot'], self.opts['testname'], params, v)
                args = shlex.split('mkdir -p %s' % (destfilebase))
                subprocess.call(args)

                list_current_tags, current_tags = [], {}
                func = eq_info[3]
                signature = eq_info[0] + ("_opt" if func is None else "")  
                eq = eq_info[1][ eq_info[2] ].eq
                while eq_info:
#                     prev_func = func
                    prev_signature = signature
                    print "\nHLAC: " + signature + "..."
#################### Updating current_tags and keeping further options in partitionings
                    if func is None:
                        sizes_map, in_expr_list, out_expr_list = self._algogen_setup_func(eq_info)
#                     if func.name not in current_tags:
                    if signature not in current_tags:
#                         if not func.name in obtained_funcs:
                        if not signature in obtained_funcs:
                            fun_base = self.opts['algodb']+'/'+signature
                            partitioning_dims = [ (fname, os.listdir(fun_base+'/'+fname)) for fname in os.listdir(fun_base) if not fname.startswith('.') and not fname.endswith('~') and os.path.isdir(fun_base+'/'+fname) ]
                            partitioning_dims = [ [(list_parts[0],p) for p in list_parts[1] if not p.startswith('.') and not p.endswith('~') and not os.path.isdir(fun_base+'/'+list_parts[0]+'/'+p) ] for list_parts in partitioning_dims ]
        
                            parts_prod = list(itertools.product(*partitioning_dims))
#                             parts_prod = [((func.name, part_tuple),) for part_tuple in parts_prod ]
                            parts_prod = [((signature, part_tuple),) for part_tuple in parts_prod ]
        
                            if partitionings and partitionings[0] is None:
                                partitionings = parts_prod
                            else:
                                partitionings = list(itertools.product(partitionings, parts_prod))
        
                            partitionings = [ self.to_tuples_of_tuples(p) for p in partitionings ]
#                             obtained_funcs.append(func.name)
                            obtained_funcs.append(signature)
    
                        if not list_current_tags:
                            list_current_tags.append( partitionings.pop() )
                            current_tags = dict(*list_current_tags)
                            current_tags = { k:dict(current_tags[k]) for k in current_tags }
                        else:
                            extra_partitionings = list(itertools.product(list_current_tags, parts_prod))
                            extra_partitionings = [ self.to_tuples_of_tuples(p) for p in extra_partitionings ]
                            list_current_tags = [ extra_partitionings.pop() ]
                            current_tags = dict(*list_current_tags)
                            current_tags = { k:dict(current_tags[k]) for k in current_tags }
                            partitionings.extend(extra_partitionings)
                        
#                     print list_current_tags
#                     print current_tags
#                     sys.exit()
#################### 
                    if func is None:
                        dimtag_dict = sizes_map
                    else:
                        with open(self.opts['algodb']+'/'+func.name+'/dimtags.txt') as f:
                            dimtags = f.read().splitlines()
                        dimtag_dict = {}
                        for dimtag,expr in zip(dimtags, func.inexpr+[func]):
                            l,r = dimtag.split(' ')
                            expr_out = expr.getOut()
                            qnt_list = expr_out.qnt_list if isinstance(expr_out, QuantityCartesianProduct) else [ expr_out ]
                            for qnt in qnt_list:  
                                dimtag_dict[l] = qnt.size[0]
                                dimtag_dict[r] = qnt.size[1]
                    
                    for nb,unroll in [ (sympify(self.opts['nu']), False), (sympify(1), True) ]:
                        if prev_signature and prev_signature == signature:
                            for tag in dimtag_dict:
                                if prev_signature and prev_signature == signature:
                                    idcs, dom_info = eq.info.get('indices', []), eq.info.get('polytope', Set("{[]}"))
                                    if get_expr_bound_over_domain(idcs, dom_info, dimtag_dict[tag], 'max') > nb:
                                        print str(nb) + "-partitioning " + signature + " dimension: " + tag
                                        part_fname = self.opts['algodb']+'/'+signature+'/'+tag+'/'+current_tags[signature][tag]
                                        print "Using " + part_fname
                                        with open(part_fname) as f:
                                            text = f.read()
                                        tmat_patterns = list(set(tmp_re.findall(text)))
                    
                                        for tmat in tmat_patterns:
                                            tname = 'T'+str(globalSSAIndex())
                                            text = text.replace(tmat, tname )
        #                                     text = self.max_tmp_size(text, tname, dimtag_dict, eq)
                                         
                                        for t in dimtag_dict:
                                            text = text.replace('@'+t+'@', str(dimtag_dict[t]) )

                                        if func is None:
                                            for i, in_expr in enumerate(in_expr_list):
                                                text = text.replace('@op'+str(i)+'@', in_expr.toLL() )
                                            for i, out_expr in enumerate(out_expr_list):
                                                text = text.replace('@out'+str(i)+'@', out_expr.toLL() )
                                        else:
                                            for i, inexpr in enumerate(func.inexpr):
                                                text = text.replace('@op'+str(i)+'@', inexpr.toLL() )
#                                             text = text.replace('@out0@', eq.inexpr[0].toLL())
                                            out_expr_list = eq.inexpr[0].inexpr if isinstance(eq.inexpr[0], CartesianProduct) else [eq.inexpr[0]]  
                                            for i, out_expr in enumerate(out_expr_list):
                                                text = text.replace('@out'+str(i)+'@', out_expr.toLL() )
                                        
                                        text = text.replace('@it@', 'fi'+str(globalSSAIndex()) )
                                        
                                        text = text.replace('@nb@', str(nb) )
                                        
                                        parser = self.opts['ll_parser'](parseinfo=False, comments_re="%%.*")
                                        sem = self.opts['ll_sem'](mDict=dict(llprog.mDict), opts={'tag_unroll': unroll, 'fuse_gat':True, 'init_info': eq.info} )
                                        parser.parse(text, rule_name="program", whitespace=string.whitespace, semantics=sem)
                                        subs_ll = llProgram(sem)
                                        
                                        llprog.mDict.update(subs_ll.mDict)
                                        dimtag_dict[tag] = nb
                                        eq_info[1][ eq_info[2] ] = subs_ll.stmtList[0]
                
        #                                 print " storing partitioning result in " + destfilebase +"/"+ str(vv) + ".txt"
        #                                 with open(destfilebase +"/"+ str(vv) + ".txt", 'w') as f:
        #                                     llprog.flatten()
        #                                     f.write("Using part. schemes: " + str(current_tags)+"\n\n")
        #                                     f.write("="*80+"\n\n")
        #                                     f.write(llprog.toLL())
        #                                     vv+=1

#                                         eq_info = llprog.get_first_func_nongen_with_nublac(nublac)
                                        eq_info = llprog.get_first_eq_nongen_with_nublac(nublac)
                                        if eq_info:
#                                             prev_func = func
#                                             func = eq_info[0]
                                            prev_signature = signature
                                            func = eq_info[3]
                                            signature = eq_info[0] + ("_opt" if func is None else "")  
                                            eq = eq_info[1][ eq_info[2] ].eq
                                        
                    if prev_signature and prev_signature == signature:
                        part_fname = self.opts['algodb']+'/'+signature+'/1x1.ll'
                        print "Using " + part_fname
                        with open(part_fname) as f:
                            text = f.read()
                        
                        if func is None:
                            for i, in_expr in enumerate(in_expr_list):
                                text = text.replace('@op'+str(i)+'@', in_expr.toLL() )
                            for i, out_expr in enumerate(out_expr_list):
                                text = text.replace('@out'+str(i)+'@', out_expr.toLL() )
                        else:
                            for i, inexpr in enumerate(func.inexpr):
                                text = text.replace('@op'+str(i)+'@', inexpr.toLL() )
#                             text = text.replace('@out0@', eq.inexpr[0].toLL())
                            out_expr_list = eq.inexpr[0].inexpr if isinstance(eq.inexpr[0], CartesianProduct) else [eq.inexpr[0]]  
                            for i, out_expr in enumerate(out_expr_list):
                                text = text.replace('@out'+str(i)+'@', out_expr.toLL() )
                
                        parser = self.opts['ll_parser'](parseinfo=False, comments_re="%%.*")
                        sem = self.opts['ll_sem'](mDict=dict(llprog.mDict), opts={'init_info': eq.info} )
                        parser.parse(text, rule_name="program", whitespace=string.whitespace, semantics=sem)
                        subs_ll = llProgram(sem)
                        
                        eq_info[1][ eq_info[2] ] = subs_ll.stmtList[0]
                        print "Synthesis completed.\n"
                        eq_info = llprog.get_first_eq_nongen_with_nublac(nublac)
                        if eq_info:
                            func = eq_info[3]
                            signature = eq_info[0] + ("_opt" if func is None else "")  
                            eq = eq_info[1][ eq_info[2] ].eq
                
                llprog.unroll()
                llprog.flatten()
                llprog.remove_empty_eqs()
                llprog.update_info()
                llprog.ann['part_schemes'] = deepcopy(current_tags)

                def compute_variant_tag_(d):
                    slist = sorted( [ (k,sorted(v.items())) for k,v in d.items() ], key=lambda t: t[0] )
                    taglist = [ '_'.join([tag]+[var[1].replace('.ll','') for var in varlist]) for tag,varlist in slist ]
                    return '_'.join(taglist)
                
                llprog.ann['variant_tag'] = compute_variant_tag_(current_tags)
                llprog.ann['algo_v'] = v
                print "Storing final version "+str(v)+" in " + destfilebase +"/final.txt"
                with open(destfilebase +"/final.txt", 'w') as f:
                    f.write("Using part. schemes: " + llprog.ann['variant_tag']+"\n\n")
                    f.write("="*80+"\n\n")
                    f.write(llprog.toLL())
                
                v,vv = v+1,0
    #         sys.exit()
            elif partitionings[0] is None:
                partitionings.pop()
            llprogs.append(llprog)
        return llprogs

    def initIterator(self):
#         if self.random:
#             k = self.limit if (self.limit > 0 and self.limit < len(self.rank)) else len(self.rank)
#             samp = sample(self.rank, k)
#         else:
#             samp = self.rank
#         self.samp = samp
#         self.iter = ( e for e in samp ) # Create a generator for the expressions
        self.iter = ( e for e in self.rank ) # Create a generator for the expressions
        
    def next(self):
        try:
            _next = self.iter.next()
        except StopIteration:
            _next = None
        self.current = _next
#         return None if _next is None else _next.getRealgraph() 
#         llprog = None
#         if _next is not None:
#             eqs = [ holoeq.getRealgraph() for holoeq in _next ]
#             llprog = llProgram(self.llprog)
#             for lls, eq in zip(llprog.stmtList, eqs): # In order to preserve eqs' original annotations
#                 lls.eq = eq

        llprog = None
        if _next is not None:
            holoLlProg = self.holoLLProgTrack[_next]
            llprog = holoLlProg.copySubs(dict(_next))
#             llprog = self.holoLlProg.copySubs(dict(_next))
            llprog = llprog.getRealgraph()

        return llprog 
    
    def initRank(self):
#         maxLength = 0
#         candList = []
#         for cands in self.candidateEqs:
#             if self.random:
#                 k = self.limit if (self.limit > 0 and self.limit < len(cands)) else len(cands)
#                 samp = sample(cands, k)
#             else:
#                 samp = cands
#             if len(samp) > maxLength:
#                 maxLength = len(samp) 
#             candList.append(samp)
#         for i in range(maxLength):
#             eqs = [ cands[i%len(cands)] for cands in candList ]
#             self.rank[tuple(eqs)] = [None]
        print "      Computing full_list..."
#         full_list = [ tuple(zip(self.candidateEqs.keys(), cp)) for cp in product(*self.candidateEqs.values()) ]
        list_of_cands = self.candidateEqs.values()
        max_len = max( map(len, list_of_cands) )
        for cands in list_of_cands:
            r = int(math.ceil(float(max_len)/len(cands))) 
            ext = cands*r
            cands.extend( ext[:max_len-len(cands)] )
        full_list = [ tuple(zip(self.candidateEqs.keys(), cp)) for cp in zip(*list_of_cands) ]
        print "      full_list computed."
        if self.random and (self.limit > 0 and self.limit < len(full_list)):
            samp = sample(full_list, self.limit)
        else:
            limit = self.limit if self.limit > 0 else len(full_list)
            samp = full_list[:limit]
        for t in samp:
            self.rank[t] = [None]
            self.holoLLProgTrack[t] = self.holoLlProg

#     def groupCandidateEqs(self):
#         cands = [ e for e in self.links if self.links[e] == [] ]
#         self.candidateEqs.append(cands)

    def groupCandidateEqs(self, origEq):
        cands = [ e for e in self.links if self.links[e] == [] ]
        self.candidateEqs[origEq] = cands

    def populate(self):
        for can_vec,stmt in zip(self.can_vec_list, self.holoStmts):
            self.rs = self.rs_nu if can_vec else self.rs_sca
            self.generated = []
            self.newRoots = [] 
            self.links = {}
            self.roots = [stmt.eq]
            self.add_rs = self._get_add_rs_in_ann(stmt.ann)
            self.rem_rs = self._get_rem_rs_in_ann(stmt.ann)
            self.apply()
            while(self.newRoots):
                self.roots = self.newRoots
                self.newRoots = []
                self.generated = []
                self.apply()
#             self.groupCandidateEqs()
            self.groupCandidateEqs(stmt.eq)
    
    def _get_add_rs_in_ann(self, ann):
        res = {}
        for a in ann:
            if '+' in a:
                l = a.split('+') # ['Op', 'modname rulename [plist]' ]
                mod_rule_params = l[1].split()
                mod = importlib.import_module(mod_rule_params[0])
                rule = getattr(mod, mod_rule_params[1])(*eval(mod_rule_params[2]))
                if l[0] in res:
                    res[l[0]].append(rule)
                else:
                    res[l[0]] = [rule]
        return res

    def _get_rem_rs_in_ann(self, ann):
        res = {}
        for a in ann:
            if '-' in a:
                l = a.split('-') # ['Op', 'rulename0 ..rulenamek' ]
                if l[0] in res:
                    res[l[0]].extend(l[1].split())
                else:
                    res[l[0]] = l[1].split()
        return res
            
    def print_choices(self):
        filename = self.opts['logroot'] + '/results/' + self.opts['testname'] + '/choices.txt'
        holoLlProg = self.holoLLProgTrack[self.current]
        choices_list = []
        holoLlProg.get_ordered_choices(dict(self.current), choices_list)
        choices = deepcopy(choices_list[-1])
        for c in choices_list[-2::-1]: 
            for k,v in c.iteritems():
                if k not in choices:
                    choices[k] = deepcopy(v)
                else:
                    choices[k].extend(v)
        with open(filename, 'w') as f:
            f.write("{\n" + ",\n".join(( '\'{}\': {}'.format(k.__name__, v) for k,v in choices.iteritems() ) ) + "\n}")
#             f.write("\n\n============\n\n")

    def apply(self): # This should disappear and the logic transferred one level up (populate)
        for root in self.roots:
            self.actualRoot = root
            self.links[self.actualRoot] = []
            self._apply(root)
        self.newRoots = [ e for e in self.links if not self.links[e] and e in self.generated ]

    def _apply(self, holo, mask=None):
        ruleList = filter(lambda rr: rr.applicable(holo), self.rs[holo.node.__class__.__name__]) if holo.node.__class__.__name__ in self.rs else []
        if holo.node.__class__.__name__ in self.rem_rs:
            ruleList = [ rule for rule in ruleList if rule.__class__.__name__ not in self.rem_rs[holo.node.__class__.__name__] ]
        ruleList.extend( filter(lambda rr: rr.applicable(holo), self.add_rs[holo.node.__class__.__name__]) if holo.node.__class__.__name__ in self.add_rs else [] )
        
        if ruleList:
#             for r in ruleList:
            ruleList.sort(key=lambda r: r.priority)
            rule = ruleList.pop()
            if self.fixedchoices:
                choices = [ self.fixedchoices[rule.__class__.__name__].pop() ]
            else:
                choices = rule.genChoices(holo)
            for c in choices:
                rootHandle = duplicateAtHandleHolo(holo) #returns tuple (newroot, exprHandle)
                newHolo = rule.apply(rootHandle[1], c)
                newRoot = newHolo if len(newHolo.pred) == 0 else rootHandle[0] 
                self.links[self.actualRoot].append((rule, c, newRoot))
                if self.opts['printchoices']:
                    newRoot.choices = deepcopy(self.actualRoot.choices)
                    if rule.__class__ in newRoot.choices:
                        newRoot.choices[rule.__class__].append(c)
                    else:
                        newRoot.choices[rule.__class__] = [c]
                self.generated.append(newRoot)
                tempRoot = self.actualRoot
                self.actualRoot = newRoot
                self.links[self.actualRoot] = []
                self._apply(newHolo, rule.mask(holo))
                self.actualRoot = tempRoot
            return True # If any rule was applied notify it.
        else:
            if mask is None:
                mask = [True]*len(holo.succ)
#             tempRoot = self.actualRoot
            for s,m in zip(holo.succ, mask):
#                 if tempRoot != self.actualRoot:
#                     s = searchGenHandle(id(s.node), self.actualRoot, lambda h: id(h.node), lambda h: h.succ)
                if m: 
                    generated = self._apply(s)
                    if generated: return True
            return False # No rule applied starting from this node

    def getBestMeasurement(self):
#         return max(self.rank.iteritems(), key=itemgetter(1))
        t = self.measManager.getBestMeasurement(self.rank)

        llprog = self.holoLlProg.copySubs(dict(t[0]))
        llprog = llprog.getRealgraph()

#         eqs = [ holoeq.getRealgraph() for holoeq in t[0] ]
#         llprog = llProgram(self.llprog)
#         for lls, eq in zip(llprog.stmtList, eqs): # In order to preserve eqs' original annotations
#             lls.eq = eq
            
        return (llprog, t[1])
    
    def __str__(self):
        limit = (" with limit = " + str(self.limit) if self.limit > 0 else " exhaustive")
        rand = (" random" + limit if self.random else " exhaustive")
        return "HOfflineLRM" + rand + " - Gen Expr count: " + str(len(self.rank))

class HSimpleLRM(LRM):
    """
    LRM processing holographs. Mind: there cannot be two realgraphs at once as they are created combining same real nodes.
    """
    def __init__(self, llprog, measMgr, opts):
        super(HSimpleLRM, self).__init__(measMgr, opts)
#         self.roots = [expr.getHolograph()]
        self.llprog = llprog
        self.holoEqs = [ s.eq.getHolograph() for s in llprog.stmtList ]
        self.initRank()
        self.initIterator()

    def initIterator(self):
        self.iter = ( e for e in self.rank ) # Create a generator for the expressions
        
    def next(self):
        try:
            _next = self.iter.next()
        except StopIteration:
            _next = None
        self.current = _next
#         return None if _next is None else _next.getRealgraph() 
        llprog = None
        if _next is not None:
            eqs = [ eq.getRealgraph() for eq in _next ]
            llprog = llProgram(self.llprog)
            llprog.stmtList = [ llStmt(eq) for eq in eqs ]
            
        return llprog 
    
    def initRank(self):
        self.rank[tuple(self.holoEqs)] = [None]
            
    def getBestMeasurement(self):
#         return max(self.rank.iteritems(), key=itemgetter(1))
        t = self.measManager.getBestMeasurement(self.rank)
        eqs = [ eq.getRealgraph() for eq in t[0] ]
        llprog = llProgram(self.llprog)
        llprog.stmtList = [ llStmt(eq) for eq in eqs ]
            
        return (llprog, t[1])
    
    def __str__(self):
        return "HSimpleLRM - Gen Expr count: " + str(len(self.rank))

class OnlineLRM(LRM):
    def __init__(self, expr, measMgr, opts):
        super(OnlineLRM, self).__init__(measMgr, opts)
#         self.opts = opts
        self.initExpr = [expr]
        
        self.rootStack = []
        self.exprStack = []
        self.ruleListStack = []
        self.ruleStack = []
        self.choiceListStack = []
        self.links = {}
        self.populate()
        
    def count(self):
        return len(self.rank)
            
    def populate(self):
        rs = self.opts['lrs']
        root = self.initExpr[-1]
        expr = root
        ruleList = []
        if expr.__class__.__name__ in rs:
            for r in rs[expr.__class__.__name__]:
                if r.applicable(expr):
                    ruleList += [r]
        if ruleList:
            self.rootStack.append(root)
            self.exprStack.append(expr)
            self.ruleListStack.append(ruleList)
            rule = ruleList.pop()
            self.ruleStack.append(rule)
            choices = rule.genChoices(expr)
            self.choiceListStack.append(choices)
            self.links[root] = []

    def next(self):
        if not self.exprStack:
            return None
        # If you're here there's still at least one rule and one choice
        root = self.rootStack[-1]
        expr = self.exprStack[-1]
        rule = self.ruleStack[-1]
        c = self.choiceListStack[-1].pop()
        rootHandle = duplicateAtHandle(expr)
        newExpr = rule.apply(rootHandle[1], c)
        newRoot = newExpr if newExpr.pred[0][0] is None else rootHandle[0]
        self.links[root].append((rule, c, newRoot)) 
        self.links[newRoot] = []
        self.current = newRoot
        self._next(newExpr, newRoot)
        
#        self.rank[self.current] = [ None ]
        
        peel = True
        while(peel):
            if not self.choiceListStack[-1]:
                self.choiceListStack.pop()
                self.ruleStack.pop()
                if not self.ruleListStack[-1]:
                    self.ruleListStack.pop()
                    self.exprStack.pop()
                    self.rootStack.pop()
                    if not self.rootStack:
                        peel = False
                else:
                    rule = self.ruleListStack[-1].pop()
                    self.ruleStack.append(rule)
                    choices = rule.genChoices(self.exprStack[-1])
                    self.choiceListStack.append(choices)
                    peel = False
            else:
                peel = False    
            
        return self.current
    
    def _next(self, expr, root):
        rs = self.opts['lrs']
        ruleList = []
        if expr.__class__.__name__ in rs:
            for r in rs[expr.__class__.__name__]:
                if r.applicable(expr):
                    ruleList += [r]
        if ruleList:
            self.rootStack.append(root)
            self.exprStack.append(expr)
            self.ruleListStack.append(ruleList)
            rule = ruleList.pop()
            self.ruleStack.append(rule)
            choices = rule.genChoices(expr)
            self.choiceListStack.append(choices)
            c = choices.pop()

            rootHandle = duplicateAtHandle(expr)
            newExpr = rule.apply(rootHandle[1], c)
            newRoot = newExpr if newExpr.pred[0][0] is None else rootHandle[0]
            self.links[root].append((rule, c, newRoot)) 
            self.links[newRoot] = []
            self.current = newRoot
            self._next(newExpr, newRoot)
        else:
            if not isinstance(expr, Quantity):
                for inexpr in expr.inexpr:
                    self._next(inexpr, root)
    
    def __str__(self):
        return "OnlineLRM exhaustive"
