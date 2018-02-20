import copy
import itertools

from core.expression import Symbol, Matrix, Vector, Scalar, NumericConstant, \
                            Equal, Plus, Minus, Times, Transpose, Inverse, \
                            BlockedExpression, NList, Predicate, sZERO
from core.builtin_operands import Zero
from core.functional import RewriteRule, Replacement, replace, contains
from core.InferenceOfProperties import *
from core.algebraic_manipulation import to_canonical, simplify
from core.TOS import _TOS as TOS

from CoreExtension import isOperand

from Partitioning import partition_shape
import utils


class LoopInvariant( object ):
    def __init__( self, operation, op_to_implicit, known_pmes, pme, tiling, dep_graph, subgraph ):
        self.operation = operation
        self.op_to_implicit = op_to_implicit
        self.known_pmes = known_pmes
        self.pme = pme
        self.tiling = tiling
        self.dep_graph = dep_graph
        self.subgraph = subgraph
        # To be created
        self.expressions = None
        self.traversals = None
        self.linv_operands = self.pme.operands[:]
        self.linv_operands_part_shape = copy.deepcopy(self.pme.part_shape)
        #self.linv_operands_basic_part = dict( (k,v) for k,v in self.pme.basic_partitionings.items() )
        self.linv_operands_basic_part = dict( (k,v) for k,v in self.pme.partitionings.items() )
        self.linv_bound_dimensions = copy.deepcopy(self.operation.bound_dimensions)

    def build( self ):
        subg_filter = [ 1 if (i+1) in self.subgraph \
                          else 0 for i in range( len( self.dep_graph ) ) ]
        unchained_subg = list( unchain_graph( self.tiling, subg_filter ) )
        filtered_tiling = filter_tiling( self.tiling, unchained_subg )
        #print("++++")
        #for t in filtered_tiling:
            #print(t)
        #print("++++")
        self.expressions = compress_tiles( filtered_tiling )
        self.fix_temporaries()

    def fix_temporaries( self ):
        temp_exprs = []
        for expr in itertools.chain( *self.expressions ):
            lhs, rhs = expr.get_children()
            for out in lhs:
                if not out.isInput() and not out.isOutput(): # [FIXME] Temporaries are not labeled. Now they are, fix.
                    self.linv_operands.append( out )
                    temp_exprs.append( expr )
        for expr in temp_exprs:
            #print( expr )
            lhs, rhs = expr.get_children()
            lhs = lhs.get_children()[0]
            # Determine to which operands in the temporary bound
            # Also, which quadrant of the full temporary should be used
            (rows_op, r_dim), (cols_op, c_dim) = utils.size_as_func_of_operands( rhs )

            # set in bound_dimensions
            r = rows_op.parent_op.get_name() + "_" + r_dim.lower()
            for s in self.linv_bound_dimensions:
                if r in s:
                    s.append( lhs.get_name() + "_r" )
            c = cols_op.parent_op.get_name() + "_" + c_dim.lower()
            for s in self.linv_bound_dimensions:
                if c in s:
                    s.append( lhs.get_name() + "_c" )

            # partition temporary
            rows_parent = rows_op.parent_op.get_name()
            cols_parent = cols_op.parent_op.get_name()
            shape_rows = self.pme.part_shape[ rows_parent ][ {"R":0, "C":1}[r_dim] ]
            shape_cols = self.pme.part_shape[ cols_parent ][ {"R":0, "C":1}[c_dim] ]
            
            size_rows = rows_op.parent_op.get_size()[ {"R":0, "C":1}[r_dim] ]
            size_cols = cols_op.parent_op.get_size()[ {"R":0, "C":1}[c_dim] ]
            lhs.size = (size_rows, size_cols)

            part = partition_shape( lhs, (shape_rows, shape_cols) )
            self.linv_operands_basic_part[ lhs.get_name() ] = part
            part_shape = (len(part.children), len(part.children[0]))
            self.linv_operands_part_shape[ lhs.get_name() ] = part_shape

            part_rows = rows_op.quadrant[ {"R":0, "C":1}[r_dim] ]
            part_cols = cols_op.quadrant[ {"R":0, "C":1}[c_dim] ]
            quadrant = part[ part_rows ][ part_cols ]

            # replace the temporary with the proper quadrant in every expression of the linv
            # [TODO] why is loop invariant a list of lists?
            expressions = []
            for expr_l in self.expressions:
                expressions.append([ replace( copy.deepcopy(expr), [RewriteRule( lhs, Replacement(quadrant) )] ) for expr in expr_l ])
            self.expressions = expressions

    def is_feasible( self ):
        pme = self.pme
        linv = self.expressions

        traversal_tuples = [ [0] if shape == 1 else [1,-1] for shape in pme.part_tuple ]
        feasible_traversals = []
        # For peeling in slingen mode
        #self.iteration_rules = []

        for traversal_dirs in itertools.product( *traversal_tuples ):
            dims_to_part_shape = {}
            #for dims, shape in zip( self.operation.bound_dimensions, traversal_dirs ):
            for dims, shape in zip( self.linv_bound_dimensions, traversal_dirs ):
                for dim in dims:
                    dims_to_part_shape[dim] = shape
            initial_rules = []
            final_rules = []
            trav_shape = dict()
            #for operand in self.operation.operands:
            for operand in self.linv_operands:
                trav_shape[operand.get_name()] = (
                   dims_to_part_shape[operand.get_name()+"_r"],
                   dims_to_part_shape[operand.get_name()+"_c"]
                )
                initial_rules.extend(
                    #initial_rewrite(operand, pme.basic_partitionings[operand.get_name()], trav_shape[operand.get_name()])
                    initial_rewrite(operand, self.linv_operands_basic_part[operand.get_name()], trav_shape[operand.get_name()])
                )
                final_rules.extend(
                    #final_rewrite(operand, pme.basic_partitionings[operand.get_name()], trav_shape[operand.get_name()])
                    final_rewrite(operand, self.linv_operands_basic_part[operand.get_name()], trav_shape[operand.get_name()])
                )
            pre = []
            post = []

            for expr in itertools.chain( *linv ):
                new = copy.deepcopy( expr )
                pre.append( simplify( to_canonical( replace( new, initial_rules ) ) ) )
                new = copy.deepcopy( expr )
                post.append( simplify( to_canonical( replace( new, final_rules ) ) ) )
            # check if basic init
            basic_init = True
            for expr in pre:
                lhs, rhs = expr.get_children()
                if not all( op.isZero() for op in lhs ) and not \
                        isOperand( rhs ):
                    basic_init = False
                    break
            if not basic_init:
                continue
            # check if linv and not guard -> post
            #final_status = [ replace( copy.deepcopy(expr), self.op_to_implicit ) for expr in post ]
            final_status = post
            #rules1 = []
            #rules2 = []
            #neweq = replace( copy.deepcopy(self.operation.equation), [self.pme.known_ops[-1]] )
            neweq = replace( copy.deepcopy(self.operation.equation), self.pme.known_ops )
            # [FIXME] Generalize
            implies_post = True
            if not neweq in final_status:
                implies_post = False
                continue
            feasible_traversals.append( (trav_shape, pre, post) )
            # Store these states for use in loop peeling (LGenCode)
            #self.iteration_rules.append( (initial_rules, final_rules) )

        if len( feasible_traversals ) > 1:
            print( "* More than one traversal for this LoopInvariant: %d" % len(feasible_traversals) )
        self.traversals = feasible_traversals
        return bool( feasible_traversals )

    # [TODO] Polish: predicates, temporaries, etc
    def same_up_to_temporaries( self, other ):
        linv1 = self.expressions
        linv2 = other.expressions
        if len( linv1 ) != len( linv2 ):
            return False
        if [ len(quadrant) for quadrant in (linv1) ] != \
            [ len(quadrant) for quadrant in (linv2) ]:
            return False
        for q1, q2 in zip( linv1, linv2 ):
            for t1, t2 in zip( q1, q2 ):
                lhs1, rhs1 = t1.get_children()
                lhs2, rhs2 = t2.get_children()
                if not rhs1 == rhs2:
                    return False
        return True


def unchain_graph( tiled_pme, graph ):
    start = 0
    for expr_tiling in tiled_pme:
        end = start + len(expr_tiling)
        yield( graph[start:end] )
        start = end

def filter_tiling( tiled_pme, subg_filter ):
    return [
        [
          tile for j, tile in enumerate( expr_tiling ) if subg_filter[i][j]
        ] for i, expr_tiling in enumerate( tiled_pme )
    ]

def compress_tiles( tiled_subpme ):
    compressed = []
    for tiles in tiled_subpme:
        compressed.append( [] )
        i = 0
        while i < len( tiles ):
        #for i, tile in enumerate( tiles ):
            tile = tiles[i]
            lhs, rhs = tile.get_children()
            if isinstance( rhs, Predicate ):
                compressed[-1].append( copy.deepcopy( tile ) )
                i += 1
                continue
            replaced = False
            for j, other_tile in enumerate( tiles[i+1:], start=i+1 ):
                olhs, orhs = other_tile.get_children()
                lhs_ch = lhs.get_children()[0]
                if contains( orhs, lhs_ch ):
                    new_other = copy.deepcopy( other_tile )
                    #new_other = replace( new_other, [RewriteRule(lhs_ch, Replacement(rhs))] )
                    new_other.children[1] = replace( new_other.rhs(), [RewriteRule(lhs_ch, Replacement(rhs))] )
                    tiles[j] = new_other
                    replaced = True
                # if tile lhs = f(rhs) and other_tile overwrites lhs (lhs = f(lhs))
                # stop replacing with "old" lhs
                if lhs_ch in olhs.children:
                    break
            if not replaced:
                compressed[-1].append( copy.deepcopy( tile ) )
            i += 1
    return compressed


def initial_rewrite(operand, part, trav_shape):
    part_ch = part.get_children()
    part_shape = (len(part_ch), len(part_ch[0]))
    zero = Zero( (sZERO, sZERO) )
    if part_shape == (1, 1):
        #rewrite = [[operand]]
        return []
    elif part_shape == (1, 2): # [L|R]
        if trav_shape == (0, 1): # Left to Right, initially Left is empty, Right is the full operand
            rewrite = [[ zero, operand ]]
        elif trav_shape == (0, -1): # Right to Left
            rewrite = [[ operand, zero ]]
    elif part_shape == (2, 1): # [T;B]
        if trav_shape == (1, 0): # Top to Bottom
            rewrite = [ [zero], [operand] ]
        elif trav_shape == (-1, 0): # Bottom to Top
            rewrite = [ [operand], [zero] ]
    elif part_shape == (2, 2): # [TL TR; BL BR]
        if trav_shape == (1, 1): # Top Left to Bottom Right
            rewrite = [ [zero,    zero],
                        [zero, operand] ]
        elif trav_shape == (1, -1): # Top Right to Bottom Left
            rewrite = [ [zero,    zero],
                        [operand, zero] ]
        elif trav_shape == (-1, 1): # Bottom Left to Top Right
            rewrite = [ [zero, operand],
                        [zero,    zero] ]
        elif trav_shape == (-1, -1): # Bottom Right to Top Left
            rewrite = [ [operand, zero],
                        [zero,    zero] ]

    return list(itertools.chain( *[
                [
                    RewriteRule( p, Replacement( rew ) )
                        for p, rew in zip( p_row, rew_row )
                ] for p_row, rew_row in zip (part, rewrite) 
            ] ))

def final_rewrite(operand, part, trav_shape):
    # swap trav_shape and reuse initial_rewrite
    r,c = trav_shape
    if r == 1:
        r = -1
    elif r == -1:
        r = 1
    if c == 1:
        c = -1
    elif c == -1:
        c = 1
    # could do r*=-1, c*=-1. Less readable
    return initial_rewrite( operand, part, (r,c) )

