import sys, os
import copy

import Config
from core.attributes import UNARY, BINARY
from core.expression import Symbol, Matrix, Vector, Scalar, \
                            Equal, Plus, Minus, Times, \
                            Transpose, Inverse, Predicate, \
                            PatternDot, Operator
from core.functional import RewriteRule, Constraint, Replacement, replace
from core.InferenceOfProperties import *

from storage import ST_LOWER, ST_UPPER, ST_FULL

from core.TOS import _TOS as TOS

from Passes import lpla
from Passes import dfg
from Passes.IR_translation import alg2lpla, lpla2dfg, dfg2lpla
from Passes.alg_passes import PassCheckPredicateOverwrite
from Passes.lpla_passes import PassRemoveAssZeroToTemp, PassStorage, \
                               PassBlockSizes, PassPartRepartObjects, \
                               PassSpacings_MATLAB, tril, triu

# Dealing with product times inverse -> ldiv, rdiv
class mldiv( Operator ):
    def __init__( self, args ): # args[1] is the rhs of the linear system
        Operator.__init__( self, args, [], BINARY )
        self.size = args[1].get_size()

class mrdiv( Operator ):
    def __init__( self, args ): # args[1] is the rhs of the linear system
        Operator.__init__( self, args, [], BINARY )
        self.size = args[1].get_size()

class tril( Operator ):
    def __init__( self, arg ):
        Operator.__init__( self, [arg], [], UNARY )
        self.size = arg.get_size()

class triu( Operator ):
    def __init__( self, arg ):
        Operator.__init__( self, [arg], [], UNARY )
        self.size = arg.get_size()

# Patterns for inv to trsm
A = PatternDot("A")
B = PatternDot("B")
C = PatternDot("C")
# [TODO] Complete the set of patterns
trsm_patterns = [
    #RewriteRule( (Equal([ C, Times([ B, Transpose([Inverse([A])]) ]) ]), Constraint("A.st_info[0] == ST_LOWER")), \
    RewriteRule( Equal([ C, Times([ B, Transpose([Inverse([A])]) ]) ]), \
            Replacement( lambda d: Equal([ d["C"], mrdiv([ Transpose([tril(d["A"])]), d["B"] ]) ]) ) ),
]

#
# Produces Matlab code for:
# - Loop-based code
#
def generate_matlab_code( operation, matlab_dir ):
    # Recursive code
    out_path = os.path.join( matlab_dir, operation.name + ".m" ) # [FIX] At some this should be opname_rec.m
    with open( out_path, "w" ) as out:
        generate_matlab_recursive_code( operation, operation.pmes[-1], out ) # pmes[-1] should be the 2x2 one
    # Loop based code
    # Produce one algorithm per dimension slicing
    var = 1
    for pme, pme_linv, pme_alg in zip( operation.pmes, operation.linvs, operation.algs ):
        if all( [ part==1 for part in pme.part_tuple] ): # 1x1 partitioning, skip
            continue
        #if len( [ psize for psize in pme.part_tuple if psize != 1 ] ) > 1: # multidimensional partitioning, skip
            #continue
        # Identify the dimension "name" to identify the output file
        idx_sliced = pme.part_tuple.index( 2 )
        dim_sliced = str(opdim2problemdim( operation, operation.bound_dimensions[idx_sliced][0] ))
        # Create "dimension directory"
        try:
            #os.mkdir( os.path.join( matlab_dir, dim_sliced ) )
            os.mkdir( matlab_dir )
        except OSError:
            pass
        for linv, alg in zip( pme_linv, pme_alg ):
            #[TODO] This is ugly as hell. FIX!
            alg.operation = operation

            #
            # Pass overwrite
            #
            PassCheckPredicateOverwrite( alg )

            lpla_alg = alg2lpla( operation, pme, linv, alg, var )
            #print( lpla_alg )
            PassRemoveAssZeroToTemp( lpla_alg )
            #print( lpla_alg )
            if Config.options.opt:
                # OPTIMIZATIONS
                #mydfg = dfg.lpla2dfg( lpla_alg.body )
                ##
                #mydfg.opt_copy_propagation()
                #mydfg.opt_backward_copy_propagation()
                #mydfg.opt_remove_self_assignments()
                ##
                #mydfg.analysis_next_use()
                #mydfg.opt_dead_code_elimination()
                #lpla_alg.body = dfg.dfg2lpla( mydfg )
                #
                mydfg = lpla2dfg( lpla_alg.body )
                prev_dfg = copy.deepcopy( mydfg )
                done = False
                while not done:
                    mydfg.checkPredicateOverwrite()
                    mydfg.opt_backward_copy_propagation()
                    mydfg.opt_copy_propagation()
                    mydfg.opt_remove_self_assignments()
                    mydfg.analysis_next_use()
                    mydfg.opt_dead_code_elimination()

                    done = prev_dfg == mydfg
                    if not done:
                        #print( "Not done" )
                        #print( prev_dfg )
                        #print( mydfg )
                        prev_dfg = copy.deepcopy( mydfg )
                lpla_alg.body = dfg2lpla( mydfg )
                #
                # Passes to synthesize/gather required additional data
                PassStorage( lpla_alg )
                PassBlockSizes( lpla_alg )
                PassPartRepartObjects( lpla_alg )
                PassSpacings_MATLAB( lpla_alg )
                #
            out_path = os.path.join( matlab_dir, operation.name + "_blk_var%d.m" % var )
            with open( out_path, "w" ) as out:
                generate_loop_based_matlab_code( lpla_alg, out )
            var += 1
    # Test driver
    out_path = os.path.join( matlab_dir, "test.m" )
    with open( out_path, "w" ) as out:
        generate_matlab_test( operation, out )

indent_level = 0
indent_char = "    "
def generate_loop_based_matlab_code( lpla_f, out=sys.stderr ):
    global indent_level
    indent_level = 0
    code_dispatcher( lpla_f, out )

def code_dispatcher( node, out ):
    global indent_level, indent_char
    indent = indent_level * indent_char

    if isinstance( node, lpla.function ):
        code_function( node, out )
    elif isinstance( node, lpla.declare ):
        code_declare( node, out )
    elif isinstance( node, Equal ):
        node = replace( node, trsm_patterns )
        if isinstance( node, str ):
            print( indent + node + ";", file=out )
        else:
            print( indent + click2matlab( node ) + ";", file=out )
    elif isinstance( node, lpla.partition ):
        code_partition( node, out )
    elif isinstance( node, lpla.repartition ):
        code_repartition( node, out )
    elif isinstance( node, lpla.progress ):
        code_progress( node, out )
    elif isinstance( node, lpla.combine ):
        code_combine( node, out )
    elif isinstance( node, lpla._while ):
        code_while( node, out )
    elif isinstance( node, lpla.spacing ):
        code_spacing( node, out )
    #raise Exception

def code_function( node, out ):
    global indent_level, indent_char

    f = node
    # Header
    inargs_str = ["%s" % op.name for op in f.inargs]
    outargs = [op for op in f.outargs if op.st_info[1].name == op.name]
    outargs_str = ["%s" % op.st_info[1].name for op in f.outargs] # All, because needed as output of the function in Matlab
    bsizes = ["%s" % bs for bs in f.block_sizes]
    # Problem dimensions
    dims = []
    for op in f.inargs:
        for i, dim in enumerate(op.get_size()):
            if dim.get_name() not in [d[0] for d in dims] and str(dim) != "1":
                dims.append( (dim.get_name(), op.get_name(), i) )
    #
    if len(outargs_str) == 1:
        output = outargs_str[0]
    else:
        output = "[%s]" % ", ".join(outargs_str)
    # To have an homogeneous interface and the generation of tests
    header = "function %s = %s( %s, %s )" % (output, f.name, ", ".join( inargs_str ), \
             ", ".join(["%sb" % d for (d,_,_) in dims]))
    print( header, file=out )

    print( "%s%% Problem dimensions" % indent_char, file=out )
    for dim, op, idx in dims:
        if dim == "1":
            continue
        print( "%s%s = size(%s, %s);" % (indent_char, dim, op, idx+1), file=out ) # matlab starts counting at 1
    print( file=out)

    # "Allocate" output
    #
    if len( outargs ): # if any non overwritting output
        print( "%s%% Storage for output" % indent_char, file=out )
        for op in outargs:
            r,c = op.get_size()
            print( "%s%s = zeros(%s, %s);" % (indent_char, op.get_name(), r, c), file=out )
        print( file=out)

    # Body
    indent_level += 1
    indent = indent_level * indent_char
    for statement in f.body:
        code_dispatcher( statement, out )
    print( "end", file=out )

def code_declare( node, out ):
    global indent_level, indent_char
    indent = indent_level * indent_char

    name = node.operand.name
    size = [str(s) for s in node.operand.size]
    print( "%s%s = zeros(%s, %s);" % (indent, node.operand.get_name(), size[0], size[1]), file=out )

    #print( "\t% Storage for output", file=out )
    print( file=out)

def code_partition( node, out ):
    global indent_level, indent_char
    indent = indent_level * indent_char

    name = node.operand.name
    shape = [str(s) for s in node.shape]
    part_op = ["%s"%p for p in node.part_operand]
    which = quadrant2str( node.which )
    size = [str(s) for s in node.size]
    print( pretty_print_part( shape, name, part_op, size, which, indent ), file=out )

def code_repartition( node, out ):
    global indent_level, indent_char
    indent = indent_level * indent_char

    repart_to_part_shape_map = { (1,1):(1,1), (1,3):(1,2), (3,1):(2,1), (3,3):(2,2) }
    #
    part_op = ["%s"%p for p in node.part_operand]
    repart_op = ["%s"%p for p in node.repart_operand]
    shape_repart = [str(s) for s in node.shape]
    shape_part = repart_to_part_shape_map[ tuple(node.shape) ]
    shape_part = [str(s) for s in shape_part]
    which = quadrant2str( node.which )
    size = [str(s) for s in node.size]
    print( pretty_print_repart( "REPART", shape_part, part_op, repart_op, size, which, indent ), file=out )

def code_progress( node, out ):
    global indent_level, indent_char
    indent = indent_level * indent_char

    repart_to_part_shape_map = { (1,1):(1,1), (1,3):(1,2), (3,1):(2,1), (3,3):(2,2) }
    #
    part_op = ["%s"%p for p in node.part_operand]
    repart_op = ["%s"%p for p in node.repart_operand]
    shape_repart = [str(s) for s in node.shape]
    shape_part = repart_to_part_shape_map[ tuple(node.shape) ]
    shape_part = [str(s) for s in shape_part]
    which = quadrant2str( node.which )
    print( pretty_print_cont( shape_part, part_op, repart_op, which, indent ), file=out )

def code_combine( node, out ):
    global indent_level, indent_char
    indent = indent_level * indent_char
    #
    op = node.operand
    op_name = op.st_info[1]
    part_op = []
    for p in node.part_operand:
        try:
            sp = "%s" % p.st_info[1]
        except AttributeError:
            print( "ERROR IN COMBINE", p )
            sp = "%s" % p
        part_op.append( sp )
    shape = [str(s) for s in node.shape]

    print("%s%% Assemble output" % indent, file=out )
    if node.shape == (1, 2):
        print( "%s%s = [ %s, %s ];" % (indent, op_name, *part_op), file=out )
    elif node.shape == (2, 1):
        print( "%s%s = [ %s; %s ];" % (indent, op_name, *part_op), file=out )
    else:
        print( "%s%s = [ %s, %s; ..." % (indent, op_name, part_op[0], part_op[1] ), file=out )
        print( "%s      %s, %s    ];" % (indent, part_op[2], part_op[3]), file=out )

def code_while( node, out ):
    global indent_level, indent_char
    indent = indent_level * indent_char

    # [TODO] Can be improved: can use specific dimensions and avoid the use of "any"
    #guard = " && ".join([guard2flame(g) for g in node.guard])
    guard = " && ".join([ "any(size(%s_%s) < size(%s))" % (op, quad, op) for (dim, (quad, op)) in node.guard ])
    print( "%swhile( %s )" % (indent, guard), file=out )

    indent_level += 1
    for g in node.guard:
        dim, (quad, op) = g
        print( indent + indent_char + "%sb_ = min( %s, %sb );" % (str(dim), bsize2flame(g), str(dim)), file=out)
    for statement in node.body:
        code_dispatcher( statement, out )
    indent_level -= 1

    print( "%send" % indent, file=out )

def code_spacing( node, out ):
    global indent_level, indent_char
    indent = indent_level * indent_char
    print( indent + node.string, file=out )

def click2matlab( node ):
    if isinstance( node, Symbol ):
        return str(node)
        #return str(node.st_info[1])
        try:
            return str(node.st_info[1])
        except AttributeError:
            return str(node)
    elif isinstance( node, Plus ):
        return " + ".join( [ click2matlab(ch) for ch in node.get_children()] )
    elif isinstance( node, Times ):
        return " * ".join( [ click2matlab(ch) for ch in node.get_children()] )
    elif isinstance( node, Minus ):
        return "-" + click2matlab(node.get_children()[0])
    elif isinstance( node, Transpose ):
        return click2matlab(node.get_children()[0]) + "'"
    elif isinstance( node, Inverse ):
        return "inv(" + (click2matlab(node.get_children()[0])) + ")"
    elif isinstance( node, mrdiv ):
        A, B = node.get_children()
        return "%s / %s" % (click2matlab(B), click2matlab(A))
    elif isinstance( node, tril ):
        return "tril(" + (click2matlab(node.get_children()[0])) + ")"
    elif isinstance( node, triu ):
        return "triu(" + (click2matlab(node.get_children()[0])) + ")"
    elif isinstance( node, Equal ):
        lhs, rhs = node.get_children()
        if len( lhs.get_children() ) > 1:
            return "[" + ", ".join( click2matlab(elem) for elem in lhs ) + "] = " + click2matlab(rhs) 
        else:
            if isinstance( rhs, Predicate ):
                return click2matlab( lhs.get_children()[0] ) + " = " + click2matlab(rhs) 
            else:
                return click2matlab( lhs.get_children()[0] ) + " = " + click2matlab(rhs) 
    elif isinstance( node, Predicate ):
        return node.get_name() + "(" + ", ".join( click2matlab(arg) for arg in node.get_children() ) + ")"
    else:
        raise Exception

# 
# Auxiliary routines for code generation
#
def sort_args( part_op, repart_op, shape_part ):
    if tuple(shape_part) == (1,2):
        return part_op + repart_op
    elif tuple(shape_part) == (2,1):
        AT, AB = part_op
        A0, A1, A2 = repart_op
        return [AT, A0, A1, AB, A2]
    else:
        ATL, ATR, ABL, ABR = part_op
        A00, A01, A02, A10, A11, A12, A20, A21, A22 = repart_op
        return [ATL, ATR, A00, A01, A02,
                          A10, A11, A12,
                ABL, ABR, A20, A21, A22]

def quadrant2str( quad ):
    sanitizer_map = {
        "T" : "FLA_TOP",
        "B" : "FLA_BOTTOM",
        "L" : "FLA_LEFT",
        "R" : "FLA_RIGHT",
        "TL" : "FLA_TL",
        "TR" : "FLA_TR",
        "BL" : "FLA_BL",
        "BR" : "FLA_BR"
    }
    return sanitizer_map[ quad ]

def opdim2problemdim( operation, opdim ):
    opname, dim = opdim.split("_") # e.g., L_r
    op = [op for op in operation.operands if op.name == opname][0]
    r,c = op.size
    if dim == "r":
        return r
    else:
        return c

def guard2flame( guard ):
    (dim, (quad, op)) = guard
    if quad in ("L", "R"):
        direction = "width"
    elif quad in ("T", "B"):
        direction = "length"
    else:
        if dim == op.get_size()[0]:
            direction = "length"
        else:
            direction = "width"
    return "FLA_%s( %s_%s ) < FLA_%s( %s )" % (direction, op.name, quad, direction, op.name)

def bsize2flame( guard ):
    opposite_quad = { "L":"R", "R":"L", "T":"B", "B":"T",
                      "TL":"BR", "TR":"BL", "BL":"TR", "BR":"TL" }
    (dim, (quad, op)) = guard
    if quad in ("L", "R"):
        idx = 2
    elif quad in ("T", "B"):
        idx = 1
    else:
        if dim == op.get_size()[0]:
            idx = 1
        else:
            idx = 2
    return "size( %s_%s, %s )" % (op.name, opposite_quad[quad], idx)

def generate_matlab_recursive_code( operation, pme, out=sys.stdout ):
    inop  = [op for op in operation.operands if op.isInput()]
    outop = [op for op in operation.operands if op.isOutput()]
    inop_str  = [op.get_name() for op in inop]
    outop_str = [op.get_name() for op in outop]
    dims = []
    for op in inop: #operation.operands:
        for i, dim in enumerate(op.get_size()):
            if dim.get_name() not in [d[0] for d in dims]:
                dims.append( (dim.get_name(), op.get_name(), i) )
    output_dims = []
    for op in outop:
        for dim in op.get_size():
            if dim.get_name() not in output_dims:
                output_dims.append( dim.get_name() )

    print( "function [%s] = %s( %s )" % (", ".join(outop_str), operation.name, ", ".join(inop_str)), file=out )
    print( "\t% Problem dimensions", file=out )
    for dim, op, idx in dims:
        if dim == "1":
            continue
        print( "\t%s = size(%s, %s);" % (dim, op, idx+1), file=out ) # matlab starts counting at 1
    # if guard (any of dims of output are 0 -> nothing to compute)
    print( file=out)
    print( "\t% If output is empty, no need to compute", file=out )
    print( "\tif %s" % " || ".join(["%s == 0" % dim for dim in output_dims]), file=out )
    for op in outop:
        r,c = op.get_size()
        print( "\t\t%s = zeros(%s, %s);" % (op.get_name(), r, c), file=out )
    print( "\t% All operands are scalars, base case of recursion", file=out )
    print( "\telseif %s" % " && ".join(["%s == 1" % dim[0] for dim in dims]), file=out )
    for statement in pme.scalar_solution:
        print( "\t\t%s;" % str(statement), file=out )
    print( "\t% Otherwise, proceed recursively", file=out )
    print( "\telse", file=out )
    print( "\t\t% Partition input", file=out )
    for op in inop:
        size = op.get_size()
        if isinstance( op, Matrix ):
            part = pme.basic_partitionings[op.get_name()] # basic, to avoid, for instance, Transpose() for symm.
            part_flat = [str(ch) for ch in part.flatten_children()]
            print( "\t\t[ %s, %s, ..." % (part_flat[0], part_flat[1]), file=out )
            print( "\t\t  %s, %s     ] = FLA_Part_2x2( %s, floor(%s/2), floor(%s/2), 'FLA_TL' );" % (part_flat[2], part_flat[3], op.get_name(), size[0], size[1]), file=out )
        elif isinstance( op, Vector ):
            part = pme.basic_partitionings[op.get_name()] # basic, to avoid, for instance, Transpose() for symm.
            part_flat = [str(ch) for ch in part.flatten_children()]
            print( "\t\t[ %s, %s ] = FLA_Part_2x1( %s, floor(%s/2), 'FLA_TOP' );" % (*part_flat, op, str(op.get_size()[0])), file=out )
    print( file=out)
    print( "\t\t% Compute each subproblem", file=out )
    #for op in operation.rec_algs[-1]:
    for op in pme.sorted:
        print( "\t\t%s;" % click2matlab(op), file=out )
    print( file=out)
    print( "\t\t% Build output", file=out )
    for op in outop:
        # -1 is 2x2
        part = pme.partitionings[op.get_name()] # not basic, to benefit from Transpose(), etc
        part_flat = [ch for ch in part.flatten_children()]
        if isinstance( op, Matrix ):
            TL = part_flat[0]
            TR = part_flat[1]
            if TR.isZero():
                r,c = op.get_size()
                print( "\t\t%s = zeros( floor(%s/2), %s-floor(%s/2) );" % (TR, r, c, c), file=out )
            BL = part_flat[2]
            if BL.isZero():
                r,c = op.get_size()
                print( "\t\t%s = zeros( %s-floor(%s/2), floor(%s/2) );" % (BL, r, r, c), file=out )
            BR = part_flat[3]
            #
            TL = click2matlab( TL )
            TR = click2matlab( TR )
            BL = click2matlab( BL )
            BR = click2matlab( BR )
            print( "\t\t%s = [ %s, %s; ..." % (op, TL, TR ), file=out )
            print( "\t\t       %s, %s    ];" % (BL, BR), file=out )
        elif isinstance( op, Vector ):
            T = part_flat[0]
            B = part_flat[1]
            #
            T = click2matlab( T )
            B = click2matlab( B )
            print( "\t\t%s = [ %s; ..." % (op, T ), file=out )
            print( "\t\t       %s    ];" % B, file=out )
        elif isinstance( op, Scalar ):
            pass
        else:
            raise Exception
    print( "\tend", file=out )
    print( "end", file=out )


def generate_matlab_test( operation, out=sys.stdout ):
    inop  = [op for op in operation.operands if op.isInput()]
    outop = [op for op in operation.operands if op.isOutput()]
    inop_str  = [op.get_name() for op in inop]
    outop_str = [op.get_name() for op in outop]
    dims = []
    for op in operation.operands:
        for dim in op.get_size():
            if dim.get_name() not in dims:
                dims.append( dim.get_name() )

    # FLAME in path
    print( "% Set path for FLAME auxiliary routines", file=out )
    print( "path(path, '%s');" % Config.flame_lab_dir, file=out )
    print( file=out)

    # Set problem dimensions
    print( "% Problem dimensions", file=out )
    for dim in dims:
        #if dim == "one":
        if dim == "1":
            pass
            #print( "%s = 1;" % dim, file=out )
        else:
            print( "%s = %d;" % (dim, 537), file=out ) # Could be randomized
    print( file=out)

    # Initialize operands (with structure if needed)
    print( "% Initialize operands", file=out )
    for operand in inop:
        name = operand.get_name()
        r, c = operand.get_size()
        if isLowerTriangular( operand ):
            print( "%% %s is lower triangular" % name, file=out )
            #print( "%s = tril(rand(%s, %s));" % (name, r, c), file=out )
            # [FIX] Just for conditioning purposes
            print( "%s = tril(rand(%s, %s)) + %s * eye(%s);" % (name, r, c, r, r), file=out )
        elif isUpperTriangular( operand ):
            print( "%% %s is upper triangular" % name, file=out )
            #print( "%s = triu(rand(%s, %s));" % (name, r, c), file=out )
            # [FIX] Just for conditioning purposes
            print( "%s = triu(rand(%s, %s)) + %s * eye(%s);" % (name, r, c, r, r), file=out )
        elif isSPD( operand ):
            print( "%% %s is SPD" % name, file=out )
            print( "%s = rand(%s, %s);" % (name, r, c), file=out )
            print( "%s = %s + %s' + %s*eye(%s);" % (name, name, name, r, r), file=out )
        elif isSymmetric( operand ):
            print( "%% %s is symmetric" % name, file=out )
            print( "%s = rand(%s, %s);" % (name, r, c), file=out )
            print( "%s = %s + %s';" % (name, name, name), file=out )
        else:
            print( "%% %s is general" % name, file=out )
            print( "%s = rand(%s, %s);" % (name, r, c), file=out )
    print( file=out)

    ## Test recursive implementation
    #print( "% Test recursive implementation", file=out )
    #print( "[%s] = %s( %s );" % (", ".join(outop_str), operation.name, ", ".join(inop_str)), file=out )
    #for eq in operation.equation:
        #lhs, rhs = eq.get_children()
        ##print( "fprintf('Norm: %%.15e\\n', norm( (%s) - (%s) ));" % (click2matlab(lhs), click2matlab(rhs)), file=out )
        #print( "fprintf('Norm: %%.15e\\n', norm( (%s) - (%s) ));" % (lhs, click2matlab(rhs)), file=out )
    #print( file=out)

    # Test loop-based implementations
    print( "% Test loop-based implementations", file=out )
    for dim in dims:
        if dim == "1":
            continue
        print("%sb = %d;" % (dim, 160), file=out)
    print( file=out )
    for algs_per_pme in operation.algs[1:]: # [FIXME] Not the first pme 1x1, copy actually produces an empty alg here
        for alg in algs_per_pme:
            alg_output = ", ".join(outop_str)
            alg_input = ", ".join(inop_str)
            alg_blks = ", ".join([ "%sb" % dim for dim in dims if dim != "1" ])
            print( "[%s] = %s( %s, %s );" % (alg_output, alg.name, alg_input, alg_blks), file=out )
            for op in outop:
                #op_name = op.st_info[1].get_name()
                op_name = op.get_name()
                if isSymmetric(op):
                    if op.st_info[0] == ST_LOWER:
                        print("%s = tril(%s) + tril(%s,-1)';" % (op_name, op_name, op_name), file=out)
                    else: # ST_UPPER
                        print("%s = triu(%s) + triu(%s,1)';" % (op_name, op_name, op_name), file=out)
                elif isLowerTriangular(op):
                    print("%s = tril(%s);" % (op_name, op_name), file=out)
                elif isUpperTriangular(op):
                    print("%s = triu(%s);" % (op_name, op_name), file=out)
            for eq in operation.equation:
                lhs, rhs = eq.get_children()
                print( "fprintf('Norm: %%.15e\\n', norm( (%s) - (%s) ));" % (click2matlab(lhs), click2matlab(rhs)), file=out )
                #print( "fprintf('Norm: %%.15e\\n', norm( (%s) - (%s) ));" % (lhs, click2matlab(rhs)), file=out )
            print( file=out )
    print( "quit", file=out )

#
# Pretty printing a la FLAME
#
def pretty_print_fla_obj_decl( shape, part, repart, indent ):
    if tuple(shape) == (3, 3):
        return pretty_print_fla_obj_decl_2x2( part, repart, indent )
    elif tuple(shape) == (1, 3):
        return pretty_print_fla_obj_decl_1x2( part, repart, indent )
    elif tuple(shape) == (3, 1):
        return pretty_print_fla_obj_decl_2x1( part, repart, indent )
    print( shape )
    raise Exception

def pretty_print_fla_obj_decl_2x2( part, repart, indent ):
    # To string!
    ATL, ATR, \
    ABL, ABR = part

    ATL = str(ATL)
    ATR = str(ATR)
    ABL = str(ABL)
    ABR = str(ABR)

    A00, A01, A02, \
    A10, A11, A12, \
    A20, A21, A22 = repart

    A00 = str(A00)
    A01 = str(A01)
    A02 = str(A02)
    A10 = str(A10)
    A11 = str(A11)
    A12 = str(A12)
    A20 = str(A20)
    A21 = str(A21)
    A22 = str(A22)

    # Type
    type = "FLA_Obj "
    # spacing
    spacing = "   "
    secondary_indent = indent + " "*len(type)
    ternary_indent = secondary_indent + " "*(2*len(ATL)) + spacing + "   " # 2 ","s, 1 space
    # Some ascii documentation
    """
    """
    #
    line1 = indent + type + ATL + ", " + ATR + "," + spacing + A00 + ", " + A01 + ", " + A02 + ","
    line2 = secondary_indent + ABL + ", " + ABR + "," + spacing + A10 + ", " + A11 + ", " + A12 + ","
    line3 = ternary_indent + A20 + ", " + A21 + ", " + A22 + ";"
    return "\n".join([ line1, line2, line3 ])

def pretty_print_fla_obj_decl_1x2( part, repart, indent ):
    # To string!
    AL, AR = part

    AL = str(AL)
    AR = str(AR)

    A0, A1, A2 = repart

    A0 = str(A0)
    A1 = str(A1)
    A2 = str(A2)

    # Type
    type = "FLA_Obj "
    # spacing
    spacing = "   "
    # Some ascii documentation
    """
    """
    #
    line1 = indent + type + AL + ", " + AR + "," + spacing + A0 + ", " + A1 + ", " + A2 + ","
    return line1

def pretty_print_fla_obj_decl_2x1( part, repart, indent ):
    # To string!
    AT, \
    AB  = part

    AT = str(AT)
    AB = str(AB)

    A0, \
    A1, \
    A2  = repart

    A0 = str(A0)
    A1 = str(A1)
    A2 = str(A2)

    # Type
    type = "FLA_Obj "
    # spacing
    spacing = "   "
    secondary_indent = indent + " "*len(type)
    ternary_indent = secondary_indent + " "*len(AT) + spacing + " " # 1 ","
    # Some ascii documentation
    """
    """
    #
    line1 = indent + type + AT + "," + spacing + A0 + ","
    line2 = secondary_indent + AB + "," + spacing + A1 + ","
    line3 = ternary_indent + A2 + ";"
    return "\n".join([ line1, line2, line3 ])

def pretty_print_part( shape, op, part_op, size, which, indent ):
    if tuple(shape) == ('2','2'):
        return pretty_print_part_2x2( shape, op, part_op, size, which, indent )
    elif tuple(shape) == ('1','2'):
        return pretty_print_part_1x2( shape, op, part_op, size, which, indent )
    elif tuple(shape) == ('2','1'):
        return pretty_print_part_2x1( shape, op, part_op, size, which, indent )
    print( shape )
    raise Exception

def pretty_print_part_2x2( shape, op, part_op, size, which, indent ):
    A = op
    ATL, ATR, \
    ABL, ABR = part_op

    fcall = "FLA_Part_2x2( "
    which = "'%s'" % which
    # Some ascii documentation
    """
    """
    #
    line1 = indent + "[%s, %s, ..." % (ATL, ATR)
    line2 = indent + " %s, %s]  = " % (ABL, ABR) + fcall + A + ", " + ", ".join(size) + ", " + which + " );"
    return "\n".join([ line1, line2 ])

def pretty_print_part_1x2( shape, op, part_op, size, which, indent ):
    A = op
    AL, AR, = part_op

    fcall = "FLA_Part_1x2( "
    which = "'%s'" % which
    # Some ascii documentation
    """
    """
    #
    line1 = indent + "[%s, %s] = " % (AL, AR) + fcall + A + ", " + size[1] + ", " + which + " );"
    return line1

def pretty_print_part_2x1( shape, op, part_op, size, which, indent ):
    A = op
    AT, \
    AB  = part_op

    fcall = "FLA_Part_2x1( "
    which = "'%s'" % which
    # Some ascii documentation
    """
    """
    #
    line1 = indent + "[%s, ..." % (AT)
    line2 = indent + " %s]  = " % (AB) + fcall + A + ", " + size[0] + ", " + which + " );"
    return "\n".join([ line1, line2 ])

def pretty_print_repart( repart_or_cont, shape, part, repart, size, which, indent ):
    if tuple(shape) == ('2','2'):
        return pretty_print_repart_2x2( repart_or_cont, part, repart, size, which, indent )
    elif tuple(shape) == ('1','2'):
        return pretty_print_repart_1x2( repart_or_cont, part, repart, size, which, indent )
    elif tuple(shape) == ('2','1'):
        return pretty_print_repart_2x1( repart_or_cont, part, repart, size, which, indent )
    print( shape )
    raise Exception

def pretty_print_repart_2x2( repart_or_cont, part, repart, size, which, indent ):
    ATL, ATR, \
    ABL, ABR = part
    
    A00, A01, A02, \
    A10, A11, A12, \
    A20, A21, A22 = repart

    """
    [A00, A01, A02, ...
     A10, A11, A12, ...
     A20, A21, A22]  =  FLA_Repart_2x2_to_3x3( A_TL, A_TR, ...
                                               A_BL, A_BR, ...
                                               mb, mb, "which" );
    """
    
    fcall = "FLA_Repart_2x2_to_3x3( "
    size = ["%s_" % s for s in size]
    which = "'%s'" % which
   
    line1 = indent + "[%s, %s, %s, ..." % (A00, A01, A02)
    line2 = indent + " %s, %s, %s, ..." % (A10, A11, A12)
    line3 = indent + " %s, %s, %s]  = " % (A20, A21, A22) + " " + \
                                          fcall + ATL + ", " + ATR + ", ..."
    secondary_indent = " " * (len(line1) + 1 + len(fcall))
    line4 = secondary_indent + ABL + ", " + ABR + ", ..."
    line5 = secondary_indent + ", ".join(size) + ", " + which + " );"

    return "\n".join([ line1, line2, line3, line4, line5 ])

def pretty_print_repart_1x2( repart_or_cont, part, repart, size, which, indent ):
    AL, AR = part
    
    A0, A1, A2 = repart

    fcall = "FLA_Repart_1x2_to_1x3( "
    _size = []
    for s in size:
        try:
            _ = int(s) # s == 1 -> no underscore
            _size.append(s)
        except:
            _size.append("%s_" % s)
    size = _size
    #size = ["_%s" % s for s in size]
    which = "'%s'" % which
    
    line1 = indent + "[%s, %s, %s] = " % (A0, A1, A2) + \
                                         fcall + AL + ", " + AR + ", " + \
                                         size[1] + ", " + which + " );"
    return line1
    #return "\n".join([ line1, line2 ])

def pretty_print_repart_2x1( repart_or_cont, part, repart, size, which, indent ):
    AT, \
    AB  = part
    
    A0, \
    A1, \
    A2  = repart

    fcall = "FLA_Repart_2x1_to_3x1( "
    _size = []
    for s in size:
        try:
            _ = int(s)
            _size.append(s)
        except:
            _size.append("%s_" % s)
    size = _size
    #size = ["_%s" % s for s in size]
    which = "'%s'" % which

    line1 = indent + "[%s, ..." % (A0)
    line2 = indent + " %s, ..." % (A1)
    line3 = indent + " %s]  = " % (A2) + " " + \
                                  fcall + AT + ", ..."
    secondary_indent = " " * (len(line1) + 1 + len(fcall))
    line4 = secondary_indent + AB + ", " + size[0] + ", " + which + " );"

    return "\n".join([ line1, line2, line3, line4 ])

def pretty_print_cont( shape, part, cont, which, indent ):
    if tuple(shape) == ('2','2'):
        return pretty_print_cont_2x2( part, cont, which, indent )
    elif tuple(shape) == ('1','2'):
        return pretty_print_cont_1x2( part, cont, which, indent )
    elif tuple(shape) == ('2','1'):
        return pretty_print_cont_2x1( part, cont, which, indent )
    print( shape )
    raise Exception

def pretty_print_cont_2x2( part, cont, which, indent ):
    ATL, ATR, \
    ABL, ABR = part
    
    A00, A01, A02, \
    A10, A11, A12, \
    A20, A21, A22 = cont

    """
    [ATL, ATR, ...
     ABL, ABR]  =  FLA_Cont_with_3x3_to_2x2( A00, A01, A02, ...
                                             A10, A11, A12, ...
                                             A20, A21, A22, "which" );
    """
    
    fcall = "FLA_Cont_with_3x3_to_2x2( "
    which = "'%s'" % which

    line1 = indent + "[%s, %s, ..." % (ATL, ATR)
    line2 = indent + " %s, %s]  = " % (ABL, ABR) + " " + \
                                      fcall + ", ".join([A00, A01, A02]) + ", ..."
    secondary_indent = " " * (len(line1) + 1 + len(fcall))
    line3 = secondary_indent + ", ".join([A10, A11, A12]) + ", ..."
    line4 = secondary_indent + ", ".join([A20, A21, A22]) + ", " + which + " );"

    lines = [ line1, line2, line3, line4 ]
    ATL_sym = TOS[ATL][0]
    if ATL_sym.isSymmetric():
        if ATL_sym.parent_op.st_info[0] == ST_LOWER:
            line5 = indent + "%s = %s';" % (ATR, ABL)
            line6 = indent + "%s = tril(%s) + tril(%s,-1)';" % (ATL, ATL, ATL)
            line7 = indent + "%s = tril(%s) + tril(%s,-1)';" % (ABR, ABR, ABR)
        else: # Upper storage
            line5 = indent + "%s = %s';" % (ABL, ATR)
            line6 = indent + "%s = triu(%s) + triu(%s,1)';" % (ATL, ATL, ATL)
            line7 = indent + "%s = triu(%s) + triu(%s,1)';" % (ABR, ABR, ABR)
        lines.extend([line5, line6, line7])

    return "\n".join(lines)

def pretty_print_cont_1x2( part, cont, which, indent ):
    AL, AR = part
    A0, A1, A2 = cont

    fcall = "FLA_Cont_with_1x3_to_1x2( "
    which = "'%s'" % which

    line1 = indent + "[%s, %s] = " % (AL, AR) + \
                                     fcall + ", ".join([A0, A1, A2]) + \
                                     ", " + which + " );"
    return line1

def pretty_print_cont_2x1( part, cont, which, indent ):
    AT, \
    AB  = part
    
    A0, \
    A1, \
    A2  = cont

    fcall = "FLA_Cont_with_3x1_to_2x1( "
    which = "'%s'" % which

    line1 = indent + "[%s, ..." % (AT)
    line2 = indent + " %s]  = " % (AB) + " " + \
                                  fcall + A0 + ", ..."
    secondary_indent = " " * (len(line1) + 1 + len(fcall))
    line3 = secondary_indent + A1 + ", ..."
    line4 = secondary_indent + A2 + ", " + which + " );"

    return "\n".join([ line1, line2, line3, line4 ])
