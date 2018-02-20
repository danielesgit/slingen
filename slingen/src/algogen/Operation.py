import sys
import os
import copy
import pickle
import itertools

from core.expression import Symbol, Matrix, Vector, Scalar, NumericConstant, \
                            Equal, Plus, Minus, Times, Transpose, \
                            BlockedExpression, NList, Predicate, \
                            PatternDot, PatternStar, sZERO
from core.builtin_operands import Zero
from core.properties import *
from core.InferenceOfProperties import *
from core.prop_to_queryfunc import symbol_props_to_constraints, prop_to_func, symbol_props_to_constraints_no_io

from core.functional import replace, replace_all, RewriteRule, Replacement, Constraint, \
                            map_thread, contains, match, matchq

from core.rules_collection import simplify_rules, canonicalIO_rules
from core.rules_collection_base import canonical_rules
from core.algebraic_manipulation import to_canonical, to_canonicalIO, simplify

import core.TOS as TOS
# DEBUGGING
from core.TOS import _TOS

from CoreExtension import WrapOutBef, WrapOutAft, isOperand, infer_properties
import PredicateMetadata as pm

import Config

from PME import PME
from LoopInvariant import LoopInvariant, initial_rewrite, final_rewrite
from Algorithm import Algorithm

from BindDimensions import bindDimensions
from graph import build_dep_graph, subgraphs, zero_out_lower
from Partitioning import partition_shape, repartition, repartition_shape, repart_group
from Tiling import tile_expr
from utils import sort
from RewritingExtension import *

from BackEnd.MatlabCode import generate_matlab_code, click2matlab
#from BackEnd.LatexCode import generate_latex_code
from BackEnd.LGenCode import generate_lgen_files
#from BackEnd.CCode import generate_c_code

known_ops = [
    # Straight assignment
    RewriteRule(
        (
            NList([ Equal([ PatternDot("LHS"), PatternDot("RHS") ]) ]),
            Constraint( "isinstance(LHS, Symbol) and isOutput(LHS) and isInput(RHS)" )
        ),
        Replacement( "Equal([ NList([LHS]), RHS ])" )
    )
]
known_ops_single = []
known_pmes = []
op_to_implicit = []

# Add a verbose option
# For now it would help to illustrate the process
class Operation( object ):
    def __init__( self, name, operands, equation, overwrite ):
        self.name = name
        self.operands = operands
        self.equation = equation # list because it may be a coupled equation
        self.overwrite = overwrite
        
    def run( self ):
        print("**********************************")
        print("* Generating code for %s " % self.name)
        for eq in self.equation:
            print("*   - %s " % str(eq))
        print("**********************************")
        self.initial_setup()
        self.generate_PMEs()
        self.generate_loop_invariants()
        self.generate_loop_based_algorithms()
        self.generate_code()

    #
    # Initialization step:
    #   
    def initial_setup( self ):
        self.to_canonical_IO()
        self.learn_pattern()
        
    def to_canonical_IO( self ):
        self.equation = [
            replace_all( eq, canonical_rules + canonicalIO_rules + simplify_rules ) \
                for eq in self.equation
        ]
        # Minimize number of nodes among:
        #   1) as is, 
        #   2) applying minus to both sides, and 
        #   3) applying transpose to both sides
        minimal = []
        for eq in self.equation:
            alternative_forms= [ eq, 
                                 simplify( to_canonical( Equal([ Minus([ eq.lhs() ]), Minus([ eq.rhs()]) ]) ) ),
                                 simplify( to_canonical( Equal([ Transpose([ eq.lhs() ]), Transpose([ eq.rhs()]) ]) ) )
                               ]
            _, new = min( [ (alt.num_nodes(), alt) for alt in alternative_forms ] )
            minimal.append(new)
        # Set minimal forms
        self.equation = NList( minimal )
        #
        nodes = list( itertools.chain( *[[ node for node in eq.iterate_preorder() ] for eq in self.equation ] ) )
        self.operands = [ op for op in self.operands if op in nodes ]

    def learn_pattern( self ):
        inops = [ op for op in self.operands if op.isInput() ]
        outops = [ op for op in self.operands if op.isOutput() ]
        #
        single_assignment = len( self.equation.children ) == 1 and \
                            isinstance(self.equation.children[0].children[0], Symbol) # eq.lhs.single_entry_in_NL
        #
        op_to_pattern = [ RewriteRule( op, Replacement("PatternDot(%s.name)" % op.name) ) for op in self.operands ]
        pattern = NList([ replace_all( copy.deepcopy(eq), op_to_pattern ) for eq in self.equation ])
        if single_assignment:
            props_str = [symbol_props_to_constraints_no_io(op) for op in self.operands]
            constraint = Constraint(" and ".join( [prop for prop in props_str if prop] ))
        else:
            constraint = Constraint(" and ".join( [symbol_props_to_constraints(op) for op in self.operands] ))
        # [TODO] Tuple for get_size
        replacement = Replacement("Equal([ NList([%s]), Predicate( \"%s\", [%s], [%s] ) ])" % (
                        ", ".join( [op.name for op in outops] ), 
                        self.name, 
                        ", ".join( [op.name for op in inops] ), 
                        ", ".join( ["%s.get_size()" % op.get_name() for op in outops]))
                      )
        # [TODO] This should be part of the verbose option
        print( "* Learnt pattern" )
        print( "*   ", pattern, end="" )
        if constraint.to_eval:
            print( "with        ", constraint.to_eval )
        print(" --> ")
        print( "*          ", replacement.to_eval )
        print("**********************************")
        # [TODO] Maybe sort known ops by specificity (a la mathematica)
        #known_ops.insert( 0, RewriteRule( (pattern, constraint), replacement ) )

        if single_assignment:
            expr = pattern.children[0]
            expr.children[0] = NList([ expr.children[0] ])
            known_ops_single.insert( 0, RewriteRule( (expr, constraint), replacement ) )
            # With minus
            replacement = Replacement("Equal([ NList([%s]), Minus([ Predicate( \"%s\", [%s], [%s] ) ]) ])" % (
                            ", ".join( [op.name for op in outops] ), 
                            self.name, 
                            ", ".join( [op.name for op in inops] ), 
                            ", ".join( ["%s.get_size()" % op.get_name() for op in outops]))
                          )
            expr = copy.deepcopy( expr )
            expr.children[1] = Minus([ expr.children[1] ])
            expr.children[1] = normalize_minus( copy.deepcopy(expr.children[1]) )
            known_ops_single.insert( 0, RewriteRule( (expr, constraint), replacement ) )
            #with open(os.path.join("OUTPUT", self.name+"_patterns"), "wb") as patt_f:
                #pickle.dump( known_ops_single[1], patt_f )
                #pickle.dump( known_ops_single[0], patt_f )
        else:
            known_ops.insert( 0, RewriteRule( (pattern, constraint), replacement ) )
            with open(os.path.join("OUTPUT", self.name+"_patterns"), "wb") as patt_f:
                pickle.dump( known_ops[0], patt_f )

        pattern = Equal([ NList([ PatternDot(op.get_name()) for op in outops ]), 
                          Predicate( self.name, [PatternDot(op.get_name()) for op in inops], [op.get_size() for op in outops] ) ])
        replacement = Replacement( equation2replacement( self.equation ) )
        op_to_implicit.append( RewriteRule( pattern, replacement ) )

    def generate_PMEs( self ):
        print("* Generating PMEs...")
        self.bind_dimensions()
        self.predicate_metadata()
        #
        self.pmes = []
        for part_tuple in itertools.product([1,2], repeat=len(self.bound_dimensions)-1):
            print("* ")
            # If multidimensional partitioning and --ll: skip
            multidim_part = len( [ psize for psize in part_tuple if psize != 1 ] ) > 1
            if multidim_part and Config.options.ll:
                continue
            # Build dict such as part_shape[op.get_name()] = (1,2), ...
            part_tuple = [1] + list(part_tuple)
            dims_to_part_shape = dict()
            for dims, shape in zip( self.bound_dimensions, part_tuple ):
                for dim in dims:
                    dims_to_part_shape[dim] = shape
            part_shape = dict()
            for operand in self.operands:
                op_name = operand.get_name()
                part_shape[ op_name ] = \
                    (
                       dims_to_part_shape[op_name + "_r"],
                       dims_to_part_shape[op_name + "_c"]
                    )
            # Initialize PME and generate
            pme = PME( self.name, self.operands, self.equation, known_ops, known_pmes, part_tuple, part_shape )
            # [TODO] UGLY AS HELL!!!
            pme.operation = self
            #
            pme.partition()
            pme.distribute_partitioned_postcondition()
            pme.solve_equations()
            pme.learn_pattern()
            pme.solve_base_case()
            self.pmes.append( pme )
        #
        for pme in self.pmes:
            pme.sort()
        print("**********************************")

    def bind_dimensions( self ):
        self.bound_dimensions = bindDimensions( self.equation, self.operands )

    def predicate_metadata( self ):
        inops = [ op for op in self.operands if op.isInput() ]
        outops = [ op for op in self.operands if op.isOutput() ]
        output_size = []
        for op in outops:
            row_str = op.get_name() + "_r"
            row_set = [ s for s in self.bound_dimensions if row_str in s ][0]
            col_str = op.get_name() + "_c"
            col_set = [ s for s in self.bound_dimensions if col_str in s ][0]
            for dim in row_set:
                op_name, dim_label = dim.split("_")
                try:
                    idx = [ op.get_name() for op in inops ].index( op_name )
                except ValueError:
                    continue
                row_size = (idx, inops[idx], dim_label) 
            for dim in col_set:
                op_name, dim_label = dim.split("_")
                try:
                    idx = [ op.get_name() for op in inops ].index( op_name )
                except ValueError:
                    continue
                col_size = (idx, inops[idx], dim_label) 
            output_size.append( (row_size, col_size) )
        pm.DB[self.name] = pm.PredicateMetadata( self.name, output_size )
        pm.DB[self.name].overwrite = [ (inops.index(inp), outops.index(out)) for inp, out in self.overwrite ]
        with open(os.path.join("OUTPUT", self.name+"_metadata"), "wb") as md_f:
            pickle.dump( (self.name, pm.DB[self.name]), md_f )

    def generate_loop_invariants( self ):
        print("* Generating Loop invariants...")
        self.linvs = [] 
        self.travs = [] # traversal of the operands
        for pme in self.pmes:
            print("* ")
            loop_invariants = [] # This PME's loop invariants
            travs = [] # Traversals for this PME's loop invariants
            for tiling in self.tile_pme( pme ):
                tiling = self.pme_tiling_eliminate_temporaries( tiling )
                linear_tiling = list(itertools.chain( *tiling ))
                ##
                print( "* Tiling PME" )
                for t in linear_tiling:
                    print("* ", t)
                print("* ")
                ##
                dep_graph = build_dep_graph( linear_tiling )
                #for g in dep_graph:
                    #print(g)
                zero_out_lower( dep_graph ) # since ops are sorted, there are no deps backwards
                                            # occurs, e.g., in sylvester L,U 2x2 at the BR 
                                            # with 3 statements writing to BR
                # Check feasibility of the subgraph
                for subgraph in subgraphs( dep_graph ):
                    linv_candidate = LoopInvariant( self, op_to_implicit, known_pmes, pme, tiling, dep_graph, subgraph )
                    linv_candidate.build()
                    if linv_candidate.is_feasible() and \
                       not any( [linv_candidate.same_up_to_temporaries( linv ) \
                                       for linv in loop_invariants] ):
                        loop_invariants.append( linv_candidate )
                        print( "*   Loop invariant %d" % len( loop_invariants ) )
                        for expr in itertools.chain( *linv_candidate.expressions ):
                            print("*     ",  expr )
                        print("* ")
                    #else:
                        #print(" Unfeasiable linv ")
                        #print( linv_candidate.expressions )
            self.linvs.append( loop_invariants )
        print("**********************************")

    def tile_pme( self, pme ):
        #TOS.reset_temp() # Start again from T1
        #
        # Per equation, list of possible tilings, 
        #   which will then be "cross-producted"
        pme.tilings = []
        tiles_per_eq = []
        for _eq in pme.sorted:
            tiles_per_eq.append( tile_expr( _eq ) )

        for cross in itertools.product( *tiles_per_eq ):
            pme.tilings.append( list(cross) )

        return pme.tilings

    def pme_tiling_eliminate_temporaries( self, tiling ):
        # Tiling is a list of tilings, one per quadrant
        #  The traversal of the quadrants is based on data dependencies already :)
        from Passes import dfg
        from Passes import alg_passes
        #
        new_pme_tiling = []
        for quad_tiling in tiling:
            opt_quad_tiling = []
            for st in quad_tiling:
                opt_quad_tiling.extend( alg_passes._checkPredicateOverwrite( copy.deepcopy(st) ) )
            pme_dfg = dfg.dfg_node( opt_quad_tiling, 0 )
            #
            prev_tiling = [copy.deepcopy(t) for t in opt_quad_tiling]
            done = False
            while not done:
                old_sts = pme_dfg.statements
                pme_dfg.statements = []
                for st in old_sts:
                    pme_dfg.statements.extend( alg_passes._checkPredicateOverwrite(st) )
                pme_dfg.opt_backward_copy_propagation()
                pme_dfg.opt_copy_propagation()
                pme_dfg.opt_remove_self_assignments()
                pme_dfg.analysis_next_use()
                pme_dfg.opt_dead_code_elimination()
                cur_tiling = [copy.deepcopy(t) for t in pme_dfg.statements]
                done = len( prev_tiling ) == len( cur_tiling ) and \
                        all([ t1 == t2 for t1, t2 in zip( prev_tiling, cur_tiling ) ])
                if not done:
                    prev_tiling = []
                    for t in cur_tiling:
                        #prev_tiling.extend( pass_check_ow._checkPredicateOverwrite( t ) )
                        prev_tiling.extend( [t] )
            #
            new_pme_tiling.append( pme_dfg.statements )
        return new_pme_tiling

    def generate_loop_based_algorithms( self ):
        print( "* Generating Loop-based algorithms..." )
        self.algs = []
        variant = 1
        for pme, linvs in zip( self.pmes, self.linvs ):
            algs = []
            for linv in linvs:
                print("* ")
                print( "* Loop invariant", variant )
                for expr in linv.expressions:
                    print("*     ",  expr )
                print("* ")
                trav, init_state, _ = linv.traversals[0] # this would be another for loop
                init = self.algorithm_initialization( init_state )
                print( "* Init" )
                #print( init_state )
                print( "*   ", init )
                s = PatternDot("s")
                init = [ replace_all( i, [RewriteRule( WrapOutBef(s), Replacement(lambda d: d["s"]) )] ) for i in init ]
                print( "* Before" )
                repart, before = self.generate_predicate_before( pme, trav, linv.expressions, linv )
                print( "* After" )
                reversed_trav = dict( [(k, (r*-1, c*-1)) for k, (r,c) in trav.items() ] )
                cont_with, after = self.generate_predicate_before( pme, reversed_trav, linv.expressions, linv )
                # find updates
                print( "* Updates" )
                updates = self.find_updates( before, after )
                if updates is None:
                    #variant += 1
                    continue
                # Tile updates
                for u in updates:
                    infer_properties( u )
                final_updates = []
                # [DIEGO] Fixing some output pieces being labeled as input
                outputs = []
                for u in updates:
                    lhs, rhs = u.children
                    for l in lhs:
                        if not l.isTemporary():
                            outputs.append( l )
                            l.set_property( OUTPUT )
                #
                for u in updates:
                    #[DIEGO] u.children[0].children[0].set_property( OUTPUT )
                    for node in u.children[1].iterate_preorder():
                        #if isinstance(node, Symbol):
                        if isinstance(node, Symbol) and node not in outputs:
                            node.set_property( INPUT )
                    #
                    #copy_u = replace( copy.deepcopy(u), known_ops_single )
                    copy_u = copy.deepcopy(u)
                    copy_u = tile_expr(copy.deepcopy(copy_u))[0] # One tiling
                    final_updates.extend( copy_u )
                if len(updates) == 0:
                    print("No updates!! Should only happen in copy")
                    continue

                algs.append( Algorithm( linv, variant, init, repart, cont_with, before, after, final_updates) )
                algs[-1].prepare_for_code_generation()
                variant += 1
            self.algs.append( algs )

    def express_in_terms_of_input( self, assignments ):
        # In LU, there may be (overwritable) inputs as lhs
        for a in assignments:
            if a.children[0].children[0].isInput():
                raise Exception
        assignments = [ a for a in assignments if not a.children[0].children[0].isInput() ] 
        expand_rules = list(itertools.chain(*self.expr_to_rule_lhs_rhs( assignments )))
        new_ass = []
        for expr in assignments:
            new = copy.deepcopy(expr)
            new.children[1] = simplify(to_canonical(replace_all(new.children[1], expand_rules)))
            new_ass.append(new)
        return new_ass

    def find_updates( self, before, after ):
        # If a part is (partially) computed in the before and
        #   does not appear in the after or
        # going from before to after requires undoing some computation
        # it is potentially unstable, and more expensive: ignore
        try:
            before_finputs = self.express_in_terms_of_input( before )
            after_finputs = self.express_in_terms_of_input( after )
        except:
            # [TODO] In LU's variant 5, parts of A appear as lhs's
            return None
        #
        dict_bef = dict([ (str(u.get_children()[0]), u) for u in before_finputs ])
        dict_aft = dict([ (str(u.get_children()[0]), u) for u in after_finputs ])
        same = []
        ignore = False
        for k,v in dict_bef.items():
            if k in dict_aft and matchq(v, dict_aft[k]):
                same.extend(v.children[0].children)
            if k not in dict_aft:
                ignore = True
                reason = "%s not in %s" % (k, dict_aft.keys())
                break
            else:
                rules = self.expr_to_rule_rhs_lhs( [v] )
                rules = list(itertools.chain(*rules))
                expr_copy = copy.deepcopy( dict_aft[k] )
                t = replace( expr_copy, rules )
                #if v == replace( expr_copy, rules ):
                if dict_aft[k] == t:
                    ignore = True
                    reason = "%s would require undoing job" % k
                    break
        if ignore:
            print( "[INFO] Skipping invariant: %s" % reason )
            return None
        #
        # Wrap outputs for before and after
        WrapBefOut = WrapOutBef
        lhss = []
        for u in before:
            lhss.extend( u.children[0] )
            u.children[0] = NList([WrapBefOut(l) for l in u.children[0]])
        for u in before:
            u.children[1] = replace( u.children[1], [RewriteRule(l, Replacement(WrapBefOut(l))) for l in lhss] )
        #
        lhss = []
        for u in after:
            lhss.extend( u.children[0] )
            u.children[0] = NList([WrapOutAft(l) for l in u.children[0]])
        wrap_rules_after = \
                [
                    RewriteRule(l, Replacement(WrapBefOut(l))) if l in same else
                    RewriteRule(l, Replacement(WrapOutAft(l))) for l in lhss
                ]
        for u in after:
            u.children[1] = replace( u.children[1], wrap_rules_after )
        # replace before in before
        wrap_rules_before = []
        for u in before:
            lhs, rhs = u.get_children()
            #if len(lhs.children) > 1: 
                #wrap_rules_before.append([])
                #continue
            rules = self.expr_to_rule_rhs_lhs( [u] )
            wrap_rules_before.append(list(itertools.chain(*rules)))
        #
        new_rules = []
        for i,rules in enumerate(wrap_rules_before):
            new_rules.append([])
            for rule in rules:
                new_r = copy.deepcopy(rule)
                new_r.pattern = replace_all(new_r.pattern, list(itertools.chain.from_iterable(wrap_rules_before[:i] + wrap_rules_before[i+1:])))
                if new_r.pattern != rule.pattern:
                    new_rules[-1].append(new_r)
        for r1, r2 in zip(new_rules, wrap_rules_before):
            r2.extend(r1)
        # 
        wrap_rules_before = list(itertools.chain(*wrap_rules_before))
        done = False
        while not done:
            after_top = [copy.deepcopy(u) for u in after]
            for i,u in enumerate(after):
                _, rhs = u.get_children()
                u.children[1] = simplify(to_canonical(replace_all(copy.deepcopy(rhs), wrap_rules_before)))
            done = True
            for top, bot in zip(after_top, after):
                if top != bot:
                    done = False
                    break
        # replace after in after
        done = False
        while not done:
            # replace after in after
            wrap_rules_after = []
            for u in after:
                lhs, rhs = u.get_children()
                #if len(lhs.children) > 1: 
                    #wrap_rules_after.append([])
                    #continue
                rules = self.expr_to_rule_rhs_lhs( [u] )
                wrap_rules_after.append(list(itertools.chain(*rules)))
            #
            after_top = [copy.deepcopy(u) for u in after]
            for i,u in enumerate(after):
                _, rhs = u.get_children()
                rules = list(itertools.chain.from_iterable(wrap_rules_after[:i] + wrap_rules_after[i+1:]))
                u.children[1] = simplify(to_canonical(replace_all(copy.deepcopy(rhs), rules)))
            done = True
            for top, bot in zip(after_top, after):
                if top != bot:
                    done = False
                    break
        # [TODO] Multiple lhss, won't work
        updates = []
        for u in after:
            lhs, rhs = u.get_children()
            if len(lhs.children) == 1:
                lhs = lhs.children[0] # NList[op] -> op
                if isinstance(rhs, WrapBefOut) and isinstance(lhs, WrapOutAft) and \
                        matchq(lhs.children[0], rhs.children[0]):
                    continue
            elif not isinstance(rhs, NList): # multiple outputs/predicate in rhs, 
                                             # but not complete (otherwise it would be NList)
                pass
            else:
                to_skip = True
                for l,r in zip(lhs.children, rhs.children):
                    if not( isinstance(r, WrapBefOut) and isinstance(l, WrapOutAft) and \
                            matchq(l.children[0], r.children[0]) ):
                        to_skip = False
                        break
                if to_skip:
                    continue
            updates.append(u)
        #
        tiled_updates = []
        for u in updates:
            print( "*   ", u )
            tilings = list( tile_expr(u) ) 
            if len(tilings) > 1:
                print( "[WARNING] Multiple (%d) tilings for expression %s" % (len(tilings), u) )
                print( "          Discarding all but one" )
            tiled_updates.extend( tilings[0] )
        tiled_updates = sort( tiled_updates )
        print( "* Tiled update" )
        for t in tiled_updates:
            print("*   ", t)

        # Drop WrapOutBef's
        # Drop WrapOutAft's
        s = PatternDot("s")
        updates = []
        for u in tiled_updates:
            u = replace_all( u, [RewriteRule( WrapOutAft(s), Replacement(lambda d: d["s"]) )] )
            u = replace_all( u, [RewriteRule( WrapOutBef(s), Replacement(lambda d: d["s"]) )] )
            updates.append( u )

        return updates

    def find_updates_v2( self, before, after ):
        # If a part is (partially) computed in the before and
        #   does not appear in the after or
        # going from before to after requires undoing some computation
        # it is potentially unstable, and more expensive: ignore
        dict_bef = dict([ (str(u.get_children()[0]), u) for u in before ])
        dict_aft = dict([ (str(u.get_children()[0]), u) for u in after ])
        ignore = False
        quadrant = None
        for k,v in dict_bef.items():
            if k not in dict_aft:
                ignore = True
                break
            else:
                rules = self.expr_to_rule_rhs_lhs( [v] )
                rules = list(itertools.chain(*rules))
                expr_copy = copy.deepcopy( dict_aft[k] )
                t = replace( expr_copy, rules )
                #if v == replace( expr_copy, rules ):
                if dict_aft[k] == t:
                    ignore = True
                    break
        if ignore:
            print( "[INFO] Skipping invariant: %s" % reason )
            return None
        #
        # Wrap outputs for before and after
        WrapBefOut = WrapOutBef
        for u in before:
            u.children[0] = NList([WrapBefOut(l) for l in u.children[0]])
        #
        wrap_rules_after = []
        for u in after:
            u.children[0] = NList([WrapOutAft(l) for l in u.children[0]])
        # replace before in after
        wrap_rules_before = []
        for u in before:
            print( u )
            lhs, rhs = u.get_children()
            if len(lhs.children) > 1: 
                continue
            rules = self.expr_to_rule_rhs_lhs( [u] )
            wrap_rules_before.append(list(itertools.chain(*rules)))
        #
        for i,rule in enumerate(reversed(wrap_rules_before)):
            idx = len(wrap_rules_before) - i - 1
            for j in range(idx-1,-1,-1):
                for _rule in rule:
                    _rule.pattern = replace_all(_rule.pattern, wrap_rules_before[j])
        wrap_rules_before = list(itertools.chain(*wrap_rules_before))
        # 
        for u in after:
            _, rhs = u.get_children()
            u.children[1] = simplify(to_canonical(replace_all(copy.deepcopy(rhs), wrap_rules_before)))
        # replace after in after
        done = False
        while not done:
            # replace after in after
            wrap_rules_after = []
            for u in after:
                lhs, rhs = u.get_children()
                if len(lhs.children) > 1: 
                    wrap_rules_after.append([])
                    continue
                rules = self.expr_to_rule_rhs_lhs( [u] )
                wrap_rules_after.append(list(itertools.chain(*rules)))
            #
            after_top = [copy.deepcopy(u) for u in after]
            for i,u in enumerate(after):
                _, rhs = u.get_children()
                rules = list(itertools.chain.from_iterable(wrap_rules_after[:i] + wrap_rules_after[i+1:]))
                u.children[1] = simplify(to_canonical(replace_all(copy.deepcopy(rhs), rules)))
            done = True
            for top, bot in zip(after_top, after):
                if top != bot:
                    done = False
                    break
        # [TODO] Multiple lhss, won't work
        updates = []
        for u in after:
            lhs, rhs = u.get_children()
            lhs = lhs.children[0] # NList[op] -> op
            if isinstance(rhs, WrapBefOut) and isinstance(lhs, WrapOutAft) and \
                    matchq(lhs.children[0], rhs.children[0]):
                continue
            updates.append(u)
        #
        tiled_updates = []
        for u in updates:
            print( "*   ", u )
            tilings = list( tile_expr(u) ) 
            if len(tilings) > 1:
                print( "[WARNING] Multiple (%d) tilings for expression %s" % (len(tilings), u) )
                print( "          Discarding all but one" )
            tiled_updates.extend( tilings[0] )
        tiled_updates = sort( tiled_updates )
        print( "* Tiled update" )
        for t in tiled_updates:
            print("*   ", t)

        # Drop WrapOutBef's
        # Drop WrapOutAft's
        s = PatternDot("s")
        updates = []
        for u in tiled_updates:
            u = replace_all( u, [RewriteRule( WrapOutAft(s), Replacement(lambda d: d["s"]) )] )
            u = replace_all( u, [RewriteRule( WrapOutBef(s), Replacement(lambda d: d["s"]) )] )
            updates.append( u )

        return updates

    def expr_to_rule_lhs_rhs( self, predicates ):
        rules = []
        for p in predicates:
            lhs, rhs = p.children
            if len(lhs.children) == 1:
                rules.append( [RewriteRule( lhs.children[0], Replacement(rhs) )] )
        return rules

    # [TODO] This is quite messy. Needs a serious cleanup
    def expr_to_rule_rhs_lhs( self, predicates ):
        rules = []
        t = PatternStar("t")
        l = PatternStar("l")
        ld = PatternDot("ld")
        r = PatternStar("r")
        for p in predicates:
            pr = []
            lhs, rhs = p.children
            if len(lhs.children) == 1:
                #lhs_sym = WrapOutBef( lhs.children[0] )
                lhs_sym = lhs.children[0]
                if isinstance( rhs, Plus ):
                    # t___ + rhs -> t + lhs
                    repl_f = (lambda lhs: lambda d: Plus(d["t"].children + [lhs]))(lhs_sym)
                    pr.append( RewriteRule( Plus([t] + rhs.children), 
                                    Replacement(repl_f) ) )
                    # t___ + l___ rhs_i r___ + ... -> t + l lhs r
                    repl_f = (lambda lhs: lambda d: Plus(d["t"].children + [Times(d["l"].children + [lhs] + d["r"].children)]))(lhs_sym)
                    pr.append( RewriteRule( Plus([t] + [ Times([l] + [ch] + [r]) for ch in rhs.children ]),
                                    Replacement(repl_f) ) )
                    repl_f = (lambda lhs: lambda d: Plus(d["t"].children + [Times([simplify(to_canonical(Minus([lhs])))] + d["r"].children)]))(lhs_sym)
                    pr.append( RewriteRule( Plus([t] + [ Times( [simplify(to_canonical(Minus([ch])))] + [r]) for ch in rhs.children ]),
                                    Replacement(repl_f) ) )
                    # A - B C in  L B C R + -L A R  (minus pushed all the way to the left, and whole thing negated)
                    repl_f = (lambda lhs: lambda d: normalize_minus(Plus(d["t"].children + [Times([d["ld"]] + d["l"].children + [Minus([lhs])] + d["r"].children)])))(lhs_sym)
                    pr.append( RewriteRule( Plus([t] + [ normalize_minus( Times([ld, l, Minus([ch]), r]) ) for ch in rhs.children ]),
                                            Replacement(repl_f) ) )
                    # A - B C in  -L B C R + L A R  (minus pushed all the way to the left)
                    repl_f = (lambda lhs: lambda d: Plus(d["t"].children + [Times([d["ld"]] + d["l"].children + [lhs] + d["r"].children)]))(lhs_sym)
                    pr.append( RewriteRule( Plus([t] + [ normalize_minus( Times([ld, l, ch, r]) ) for ch in rhs.children ]),
                                            Replacement(repl_f) ) )
                    #repl_f = (lambda lhs: lambda d: Plus(d["t"].children + [Times([simplify(to_canonical(Minus(lhs.children)))] + d["r"].children)]))(lhs_sym)
                    #pr.append( RewriteRule( Plus([t] + [ 
                                #Times([ Minus([ld]), l, ch, r]) if not isinstance(ch, Minus) \
                                        #else Times([ l, ch.children[0], r]) \
                                        #for ch in rhs.children ]),
                                    #Replacement(repl_f) ) )
                    repl_f = (lambda lhs: lambda d: Plus(d["t"].children + [Times([simplify(to_canonical(Minus([Transpose([lhs])])))] + d["r"].children)]))(lhs_sym)
                    pr.append( RewriteRule( Plus([t] + [
                                Times([ Minus([ld]), l, simplify(to_canonical(Transpose([ch]))), r]) if not isinstance(ch, Minus) \
                                        else Times([ l, simplify(to_canonical(Transpose([ch]))), r]) \
                                        for ch in rhs.children ]),
                                    Replacement(repl_f) ) )
                elif isinstance( rhs, Times ):
                    repl_f = (lambda lhs: lambda d: Times(d["l"].children + [lhs] + d["r"].children))(lhs_sym)
                    pr.append( RewriteRule( Times([l] + rhs.children + [r] ), 
                                    Replacement(repl_f) ) )
                    repl_f = (lambda lhs: lambda d: Times(d["l"].children + [Transpose([lhs])] + d["r"].children))(lhs_sym)
                    pr.append( RewriteRule( Times([l, simplify(to_canonical(Transpose([rhs]))), r]), 
                                    Replacement(repl_f) ) )
                    # [TODO] Minus is a b*tch. Should go for -1 and remove the operator internally?
                    repl_f = (lambda lhs: lambda d: Times([simplify(to_canonical(Minus([Times([lhs])])))] + d["r"].children) )(lhs_sym)
                    pr.append( RewriteRule( Times([simplify(to_canonical(Minus([Times(rhs.get_children())])))] + [r] ),
                                    Replacement(repl_f) ) )
                    repl_f = (lambda lhs: lambda d: Times([simplify(to_canonical(Minus([Transpose([Times([lhs])])])))] + d["r"].children) )(lhs_sym)
                    pr.append( RewriteRule( Times([simplify(to_canonical(Minus([Transpose([Times(rhs.get_children())])])))] + [r] ),
                                    Replacement(repl_f) ) )
                else:
                    pr.append( RewriteRule( rhs, Replacement(lhs_sym) ) )
                    new_rhs = simplify(to_canonical(Transpose([rhs])))
                    if not isOperand( new_rhs ):
                        pr.append( RewriteRule( simplify(to_canonical(Transpose([rhs]))), Replacement(Transpose([lhs_sym])) ) )
            else:
                pr.append(RewriteRule(rhs, Replacement(lhs)))
            rules.append(pr)
        return rules

    def before_to_rule( self, before ):
        lhs, rhs = before.get_children()
        if isinstance( rhs, Plus ):
            rules = [ RewriteRule( Plus( [PatternStar("rest")] + rhs.get_children() ),
                                Replacement( lambda d: Plus(d["rest"].get_children() + lhs.get_children()) ) ),
                                #Replacement("Plus(rest+lhs.get_children())") )
                      RewriteRule( Plus([ Times([PatternStar("l")] + [ch] + [PatternStar("r")]) for ch in rhs.get_children() ]),
                                Replacement( lambda d: Times(d["l"].get_children() + lhs.get_children() + d["r"].get_children()) ) ),
                      RewriteRule( to_canonical( Plus([ Times([PatternStar("l")] + [ch] + [PatternStar("r")]) for ch in rhs.get_children() ]) ),
                                Replacement( lambda d: Times(d["l"].get_children() + lhs.get_children() + d["r"].get_children()) ) ) ]
        elif isinstance( rhs, Times ):
            rules = [ RewriteRule( Times( [PatternStar("l")] + rhs.get_children() + [PatternStar("r")] ),
                                Replacement( lambda d: Times(d["l"].get_children() + lhs.get_children() + d["r"].get_children()) ) ),
                      # [TODO] For chol loop invariants 2 and 3, should fix elsewhere (maybe -1 instead of minus operator)
                      RewriteRule( Times( [PatternStar("l")] + [to_canonical(Minus([Times(rhs.get_children())]))] + [PatternStar("r")] ),
                                Replacement( lambda d: Times(d["l"].get_children() + [to_canonical(Minus([Times(lhs.get_children())]))] + d["r"].get_children()) ) ) ]
        else: # [FIX] what if multiple outputs?
            #rules = [ RewriteRule( rhs, Replacement( lhs ) ) ]
            rules = [ RewriteRule( rhs, Replacement( lhs.children[0] ) ) ]
        return rules


    # [TODO] With coupled sylvester, will have to double check a few things here and above
    def algorithm_initialization( self, init_state ):
        init = []
        for expr in init_state:
            lhs, rhs = expr.get_children()
            lhs_ch = lhs.get_children()
            #init.extend([ Equal([ NList([lch]), rhs ]) for lch in lhs_ch if not isZero(lch) and not isZero(rhs) ])
            init.extend([ Equal([ NList([lch]), rhs ]) for lch in lhs_ch if not isZero(lch) ])
        return init

    def generate_predicate_before( self, pme, trav, linv, linv_obj ): # [TODO] Cleanup, no need for linv AND linv_obj
        new = [ copy.deepcopy(expr) for expr in itertools.chain(*linv) ]
        # Repartition
        reparts = dict()
        repart_rules = []
        for op in linv_obj.linv_operands:
            part = linv_obj.linv_operands_basic_part[op.get_name()]
            # [CHECK] _shape or not? Regular one needed for inheritance
            repart = repartition( op, part.shape, trav[op.get_name()] )
            #
            #repart_shape = {(1,1):(1,1), (1,2):(1,3), (2,1):(3,1), (2,2):(3,3)}[part.shape]
            #repart = repartition_shape( op, repart_shape )
            #repart = repart_group( repart, repart_shape, trav[op.get_name()] )
            #
            for part_op, repart_op in zip( itertools.chain(*part), itertools.chain(*repart) ):
                repart_rules.append( RewriteRule( part_op, Replacement( repart_op ) ) )
            reparts[op.get_name()] = repart
        # Apply repartitionings
        new = [ replace( expr, repart_rules ) for expr in new ]

        # Explicit functions to BlockedExpression
        #  First flatten args, then replace
        for expr in new:
            lhs, rhs = expr.get_children()
            if isinstance( rhs, Predicate ):
                for i, arg in enumerate( rhs.get_children() ):
                    #rhs.set_children( i, flatten_blocked_operation(arg) )
                    rhs.set_children( i, flatten_blocked_operation_click(arg) )
        new = [ replace( expr, known_pmes ) for expr in new ]

        # Operators applied to BlockedExpression, into BlockedExpressions
        for expr in new:
            if isinstance( expr, BlockedExpression ):
                continue
            _, rhs = expr.get_children()
            #print( rhs ) # [TODO] Maybe "Sylv(...)"!!!
            #rhs = flatten_blocked_operation( rhs )
            rhs = flatten_blocked_operation_click( rhs )
            expr.set_children( 1, rhs )

        # Flatten left-hand sides of the previous type of expressions
        for expr in new:
            if isinstance( expr, BlockedExpression ):
                continue
            lhs, rhs = expr.get_children()
            new_lhs = []
            for out in lhs:
                if isinstance( out, Symbol ): # this is a temporary one
                    out.size = rhs.get_size()
                    #part = partition_shape( out, rhs.shape )
                    part = partition_shape( out, tuple(rhs.shape) )
                    new_lhs.append( part )
                else:
                    new_lhs.append( out )
            lhs = BlockedExpression( map_thread( NList, new_lhs, 2 ), (0,0), rhs.shape )
            expr.set_children( 0, lhs )
        # Flatten the last type of expressions
        final = []
        for expr in new:
            if isinstance( expr, BlockedExpression ):
                final.extend( [ simplify( to_canonical( eq ) ) for eq in itertools.chain( *expr ) ] )
            else:
                lhs, rhs = expr.get_children()
                final.extend( [ simplify( to_canonical( eq ) ) for eq in itertools.chain.from_iterable( map_thread( Equal, [lhs, rhs], 2 ) ) ] )
        final = filter_zero_zero( final )
        # remove expressions of the type " B_10^T = ..." (e.g., in symv)"
        _final = final
        final = []
        for expr in _final:
            lhs, rhs = expr.children
            lhs = lhs.children
            # [FIXME] == 1 only to make sure it does not affect other cases. 
            # Just want to let them break and study them in the future 
            if len( lhs ) == 1 and (not isOperand( lhs[0] ) or lhs[0].isZero()):
                continue
            final.append( expr )
        #
        # expand in terms of input parts
        #
        #expand_rules = list(itertools.chain(*self.expr_to_rule_lhs_rhs( final )))
        #for expr in final:
            #expr.children[1] = simplify(to_canonical(replace_all(copy.deepcopy(expr.children[1]), expand_rules)))
        #
        # Print and return
        #
        for expr in final:
            print( "*   ", expr )

        return (reparts, final)

    def generate_code( self ):
        ## [LATEX] Algorithms in pdf
        #if Config.options.latex:
            #latex_dir = os.path.join(Config.latex_dir, self.name)
            #try:
                #os.makedirs( latex_dir )
            #except OSError as err:
                #pass
            #generate_latex_code( self, latex_dir )
        
        # [MATLAB] Recursive, loop-based and test driver code
        if Config.options.matlab:
            matlab_dir = os.path.join(Config.matlab_dir, self.name)
            try:
                os.makedirs( matlab_dir )
            except OSError as err:
                pass
            generate_matlab_code( self, matlab_dir )
            return 

        ## [LGEN] Loop based algorithms/code
        if Config.options.ll:
            if Config.options.opt:
                lgen_dir = os.path.join(Config.lgen_dir, self.name + "_opt")
            else:
                lgen_dir = os.path.join(Config.lgen_dir, self.name)
            try:
                os.makedirs( lgen_dir )
            except OSError as err:
                pass
            generate_lgen_files( self, lgen_dir, known_ops_single )
        ## [FLAMEC] Loop based algorithms/code
        #if Config.options.flamec:
            #c_dir = os.path.join(Config.c_dir, self.name)
            #try:
                #os.makedirs( c_dir )
            #except OSError as err:
                #pass
            #generate_c_code( self, c_dir )
