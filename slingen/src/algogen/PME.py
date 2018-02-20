import os
import pickle
import copy
import itertools
import functools

import sympy

from core.expression import Symbol, Predicate, BlockedExpression, NList, \
                            PatternDot, PatternPlus, PatternStar
from core.BlockedExpression_utils import flatten_blocked_operation
# [TODO] This stars I don't like. Needed for pattern matching to work :( 
from core.properties import *
from core.InferenceOfProperties import *

from core.functional import RewriteRule, Replacement, replace, map_thread
from core.algebraic_manipulation import to_canonical, to_canonicalIO, simplify

from core.TOS import _TOS as TOS, _TOE as TOE

from Partitioning import partition, partition_shape_with_storage
from graph import build_dep_graph

from RewritingExtension import equation2replacement
import PredicateMetadata as pm

class PME( object ):
    # operands and postcondition as in input to the operation
    # part_shape is a dict: part_shape[Op.get_name()] = ([1|2], [1|2])
    def __init__( self, name, operands, equation, known_ops, known_pmes, part_tuple, part_shape ):
        self.name = name
        self.operands = operands
        self.equation = equation
        self.known_ops = known_ops
        self.known_pmes = known_pmes
        self.part_tuple = part_tuple
        self.part_shape = part_shape
        # Will be created later on
        self.basic_partitionings = None
        self.partitionings = None
        self.partitioned_postcondition = None
        self.distributed_partitioned_postcondition = None
        self.solved_subequations = None
        self.sorted = None
        self.scalar_solution = None
        #
        self.overwrite_rules = []

    def partition( self ):
        self.basic_partitionings = dict()
        self.partitionings = dict()
        rewrite_rules = []
        for operand in self.operands:
            op_name = operand.get_name()
            # For code generation
            #part = partition_shape( operand, self.part_shape[op_name] )
            part = partition_shape_with_storage( operand, self.part_shape[op_name] )
            self.basic_partitionings[op_name] = part
            #
            part = partition( operand, self.part_shape[op_name], operand.get_properties() )
            self.partitionings[op_name] = part
            #
            rewrite_rules.append( RewriteRule(operand, Replacement(part)) )

        self.partitioned_postcondition = \
            [replace( copy.deepcopy(eq), rewrite_rules ) for eq in self.equation]
        
        print( "* Partitioned postcondition" )
        for eq in self.partitioned_postcondition:
            print( "*    ", eq )
        #print( )

    def distribute_partitioned_postcondition( self ):
        dist = [simplify(to_canonical(flatten_blocked_operation( eq )))._cleanup() \
                for eq in self.partitioned_postcondition]
        size = dist[0].size
        shape = dist[0].shape
        self.distributed_partitioned_postcondition = \
            BlockedExpression( map_thread( NList, dist, 2 ), size, shape )
        #for eq in self.distributed_partitioned_postcondition:
            #print( eq )
        
    def solve_equations( self ):
        dist = self.distributed_partitioned_postcondition
        # Update TOE
        for eq in dist.flatten_children():
            for subeq in eq:
                lhs, rhs = subeq.get_children()
                update_TOE( RewriteRule( lhs, Replacement( rhs ) ) )
                update_TOE( RewriteRule( rhs, Replacement( lhs ) ) )
        # Collect all output parts to be computed
        basic_part = self.basic_partitionings
        basic_part = self.partitionings #[TODO] Ok?
        all_outputs = []
        for op in self.operands:
            if op.isOutput():
                all_outputs.extend(
                    [ node for node in basic_part[op.get_name()].iterate_preorder() if isinstance(node, Symbol) ]
                )

        # Iterate until PME is solved
        subeqs_to_solve = dist.flatten_children()
        subeqs_to_solve = filter_zero_zero( subeqs_to_solve )
        subeqs_solved = []
        solved_outputs = set([""]) # any initialization that cannot render the equality below true
        solved = False
        #
        while not solved:
            for eq in subeqs_to_solve:
                new = replace( copy.deepcopy(eq), self.known_ops )
                if isinstance( new, Equal ):
                    lhs, rhs = new.get_children()
                    # Set input property
                    if all( [isinstance( elem, Symbol ) for elem in lhs] ):
                        if isinstance(rhs, Predicate):
                            rhs.set_property( INPUT ) # SOLVED?
                        for op in lhs:
                            op.set_property( INPUT ) # SOLVED?
                        subeqs_solved.append( new )
                    else:
                        #print( "Can it be?" )
                        # Yes, e.g., trans(X_BL) in lyapunov
                        #raise Exception
                        pass
            cur_solved_outputs = set([ op.get_name() for op in all_outputs if isInput(op) ])
            #print( "SOLVED:", cur_solved_outputs )
            if solved_outputs == cur_solved_outputs:
                print( "" )
                print( "[WARNING] PME Generation is stuck - Trying recursive instance" )
                print( "" )
                minimum = (100000, 100000)
                subeq = None
                for eq in subeqs_to_solve:
                    unks = []
                    cnt = 0
                    for node in eq.iterate_preorder():
                        cnt += 1
                        if isinstance(node, Symbol) and node.isOutput() and node not in unks:
                            unks.append(node)
                    if (len(unks), cnt) < minimum:
                        subeq = eq
                        minimum = (len(unks), cnt)
                from NestedInstance import rec_instance
                ((md_name, md_data), new_patts, new_pmes) = rec_instance( subeq.children[0] )
                self.known_pmes.extend(new_pmes)
                print("NPMES:", len(new_pmes))
                for patt in new_patts:
                    self.known_ops.append(patt)
                pm.DB[md_name] = md_data
                #raise Exception
            solved_outputs = cur_solved_outputs
            if all( [isInput(op) or op.isZero() for op in all_outputs] ):
                solved = True
            else:
                new_to_solve = []
                for eq in subeqs_to_solve:
                    if not isinstance( eq, Equal ) and \
                            len([op for op in eq.iterate_preorder() if isinstance(op, Symbol) and isOutput(op)]) != 0:
                        new_to_solve.append(eq)
                subeqs_to_solve = [simplify(to_canonicalIO( eq ))._cleanup() for eq in new_to_solve]
        self.solved_subequations = subeqs_solved
        # Replace rhs with lhs if they appear as subexpressions of other rhss
        #
        # Create replacements when suited
        reuse_rules = []
        for i, eq in enumerate( subeqs_solved ):
            eq_rules = []
            lhs, rhs = eq.children
            if not isinstance(rhs, Predicate) and rhs.get_head() not in (Minus, Transpose, Inverse):
                lhs_sym = lhs.children[0]
                t = PatternStar("t")
                l = PatternStar("l")
                r = PatternStar("r")
                repl_f = (lambda lhs_sym: lambda d: Plus([ d["t"], Times([ d["l"], lhs_sym, d["r"] ]) ]))(lhs_sym)
                eq_rules.append( RewriteRule( Plus([ t, Times([ l, rhs, r]) ]), 
                                              Replacement( repl_f ) ) )
                # A - B C in  -L B C R + L A R  (minus pushed all the way to the left)
                if len(rhs.children) > 1:
                    repl_f = (lambda lhs_sym: lambda d: Times([Minus([lhs_sym])] + d["r"].children))(lhs_sym)
                    eq_rules.append( RewriteRule( Times([ Minus([ rhs.children[0] ]), *rhs.children[1:], r]),
                                                  Replacement(repl_f) ) ) 
            reuse_rules.append( (i, eq_rules) )

        # Replace
        self.solved_subequations = []
        for i, eq in enumerate(subeqs_solved):
            rules = [ r for j,r in reuse_rules if i != j ]
            self.solved_subequations.append( replace_all( eq, list(itertools.chain(*rules)) ) )

        # [TODO] Add T to operands and bind dimensions
        #self.bind_temporaries( )
        # Reset outputs
        for op in solved_outputs:
            TOS[op][0].set_property( OUTPUT )

        print( "* PME " )
        for eq in self.solved_subequations:
            print( "*    ", eq )
        #print( )

    def learn_pattern( self ):
        inops = [ op for op in self.operands if op.isInput() ]
        outops = [ op for op in self.operands if op.isOutput() ]
        # pattern
        predicate_inops = []
        predicate_outops = []
        for op in self.operands:
            rewrite_predicate_ops = []
            basic_part = self.basic_partitionings[op.get_name()]
            for part_op in itertools.chain( *basic_part ):
                rewrite_predicate_ops.append( RewriteRule( part_op, Replacement( PatternDot(part_op.get_name()) ) ) )
            new = BlockedExpression(
                    copy.deepcopy(self.basic_partitionings[op.get_name()]),
                    op.get_size(),
                    basic_part.shape
                  )
            if op.isInput():
                predicate_inops.append( replace( new, rewrite_predicate_ops ) )
            else:
                predicate_outops.append( replace( new, rewrite_predicate_ops ) )
        pattern = Equal([
                    NList( predicate_outops ),
                    Predicate( self.name, predicate_inops, [op.get_size() for op in outops] )
                  ])
        # replacement
        # [TODO] Tuple for get_size
        #basic_parts = self.basic_partitionings
        basic_parts = self.partitionings
        lhss = map_thread( NList, [basic_parts[op.get_name()] for op in outops], 2 )

        # [TODO] This is a fix for lu (maybe coup sylv as well).
        #        Generalize and clean up
        for i,row in enumerate(lhss):
            for j,cell in enumerate(row):
                cell = replace( cell, [
                                RewriteRule(
                                    (
                                        NList([ PatternPlus("PP"), PatternDot("PD") ]),
                                        Constraint( lambda d: isZero(d["PD"]) )
                                    ),
                                    Replacement( lambda d: NList( d["PP"].get_children() ) )
                                ),
                                RewriteRule(
                                    (
                                        NList([ PatternDot("PD"), PatternPlus("PP") ]),
                                        Constraint( lambda d: isZero(d["PD"]) )
                                    ),
                                    Replacement( lambda d: NList( d["PP"].get_children() ) )
                                )
                              ] )
                lhss[i][j] = cell
        #
                
        # [CHECK] parts = self.partitionings
        #parts = self.basic_partitionings
        parts = self.partitionings
        eqs = map_thread( Equal, [ lhss, parts[outops[0].get_name()] ], 2 )

        output_shape = self.basic_partitionings[ outops[0].get_name() ].shape
        r,c = output_shape
        for eq in self.solved_subequations:
            lhs, rhs = eq.get_children()
            for row in range(r):
                for col in range(c):
                    this_lhs, this_rhs = eqs[row][col].get_children()
                    if lhs == this_lhs:
                        eqs[row][col].set_children( 1, rhs )

        #for row in range(r):
            #for col in range(c):
                #eqs[row][col] = equation2replacement( eqs[row][col].get_children()[1] )
        
        replacement_str = equation2replacement(
                              BlockedExpression( eqs, (0,0), output_shape )
                          )
                                #", ".join([
                                      #"[ " + ", ".join( [ eq for eq in row ] ) + " ]"
                                    #for row in eqs ]) + " ]" + \
                                #", (0,0), (%d, %d) )" % (r, c) + \
                                #"]), " + \
                          #"BlockedExpression([ " + \
                            #", ".join([
                                  #"[ " + ", ".join( [ eq for eq in row ] ) + " ]"
                                #for row in eqs ]) + " ]" + \
                            #", (0,0), (%d, %d) )" % (r, c) + \
                            #"])" # size does not matter
        print( "* Learnt PME pattern" )
        print( "*     ", RewriteRule( pattern, Replacement( replacement_str ) ) )
        self.known_pmes.append( RewriteRule( pattern, Replacement( replacement_str ) ) )
        with open(os.path.join("OUTPUT", self.name+"_pmes"), "ab+") as pmes_f:
            pickle.dump( self.known_pmes[-1], pmes_f )

    def solve_base_case( self ):
        unk = [sympy.var(op.get_name()) for op in self.operands if op.isOutput()]
        # [TODO] With new operations, this will get more complex/complete
        solved = dict( [ (sympy.var(v.get_name()), 1) for v in self.operands if v.isOutput() and \
                (v.isUnitDiagonal() or v.isImplicitUnitDiagonal()) ] )
        sols = sympy.solve([click2sympy(eq) for eq in self.equation], unk, dict=True)

        #elif isinstance( sol, list ) and len(unk) == 1: 
        # ex. chol: sol = [ (sqrt(a),), (-sqrt(a),) ]; what if more than one?
        if isinstance( sols, list ):
            if len( sols ) > 1:
                print( "[WARNING] Multiple solutions to the scalar case\n" )
            # trick for chol (the only one with multiple sols so far) to get the positive sqrt
            # [TODO] Can I find a way to avoid tricks and select the rigt one? Can I use l>0 in sympy.solve?
            sol = sols[-1]
            sol.update( solved )
            self.scalar_solution = [ "%s = %s" % (x, sol[x]) for x in unk ]
            # [CHECK] Here or elsewhere?
            #self.scalar_solution = []
            #for x in unk:
                #scalar_solution = "%s = %s" % (x, sol[x])
                #if self.operation.overwrite:
                    #for inp, out in self.operation.overwrite:
                       #scalar_solution = scalar_solution.replace(out.get_name(), inp.get_name())
                #self.scalar_solution.append( scalar_solution )
            #
        else:
            print( sols )
            raise Exception

    # Find one possible valid sequence to compute 
    # the equations/assignments in the PME
    def sort( self ):
        sorted = []
        dep_graph = build_dep_graph( self.solved_subequations )
        while len( sorted ) != len( self.solved_subequations ):
            new = []
            for cur_eq in range( len( dep_graph ) ):
                # if not in sorted and no antecesor I depend upon...
                if cur_eq not in sorted and \
                   not any( [ dep_graph[antecesor][cur_eq] for antecesor in range(len(dep_graph)) ] ):
                    sorted.append( cur_eq )
                    new.append( cur_eq )
            for eq_idx in new:
                for col in range(len(dep_graph[0])):
                    dep_graph[eq_idx][col] = 0
        self.sorted = [self.solved_subequations[index] for index in sorted]

#############
# Auxiliary
#############

# [TODO] Careful with precedence
from core.properties import TOE_properties
def update_TOE( rule ):
    for prop in TOE_properties:
        for _expr in TOE[prop]:
            #for rule in rewrite_rules:
            expr = copy.deepcopy( _expr )
            expr = replace( expr, [rule] )
            new = copy.deepcopy( expr )
            new = simplify( to_canonical( new ) )
            TOE.set_property( prop, new )

# [TODO] Note the eq[0]
# [TODO] Note .children (instead of get_children())
def filter_zero_zero( eqs ):
    return [ eq for eq in eqs if not (isZero( eq.children[0].lhs() ) and isZero( eq.children[0].rhs() )) ]

def click2sympy( node ):
    if isinstance( node, Symbol ):
        if node.isUnitDiagonal() or node.isImplicitUnitDiagonal():
            return 1
        return sympy.var( node.get_name() )
    elif isinstance( node, Plus ):
        return functools.reduce( lambda x,y: x+y, [ click2sympy(ch) for ch in node.get_children()] )
    elif isinstance( node, Times ):
        return functools.reduce( lambda x,y: x*y, [ click2sympy(ch) for ch in node.get_children()] )
    elif isinstance( node, Minus ):
        return -(click2sympy(node.get_children()[0]))
    elif isinstance( node, Transpose ):
        #return sympy.Transpose(click2sympy(node.get_children()[0]))
        return click2sympy(node.get_children()[0])
    elif isinstance( node, Inverse ):
        return 1/(click2sympy(node.get_children()[0]))
    elif isinstance( node, Equal ):
        lhs, rhs = node.get_children()
        return sympy.Eq( click2sympy(lhs), click2sympy(rhs) )
