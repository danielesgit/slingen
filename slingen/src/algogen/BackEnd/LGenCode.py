import sys, os
import random
import sympy

import Config

from core.expression import Symbol, sONE, sZERO, \
                            Equal, Plus, Minus, Times, Transpose, \
                            PatternDot, \
                            NList
from core.functional import matchq, match
from core.InferenceOfProperties import *
import core.properties as properties
from core.algebraic_manipulation import to_canonical, simplify
from core.builtin_operands import Zero
import storage

import PredicateMetadata as pm

from Passes.IR_translation import alg2lpla, lpla2dfg, dfg2lpla
from Passes import lpla
from Passes import dfg
from Passes.alg_passes import PassCheckPredicateOverwrite
from Passes import lpla_lgen_peeling as peeling

from BackEnd.trsm2lgen import trsm2lgen_rules


#
# Produces the files required for the interaction with LGEN:
# - definition.ll: definition of the operation in ll language
# - dimtags.txt: mapping from operand to problem dimensions
# - _slice*.ll: one algorithm per dimension slicing
# - _1x1.ll: base case (scalar code)
#
def generate_lgen_files( operation, lgen_dir, known_ops_single ):
    overwritten = [ outop for inop, outop in operation.overwrite ]
    inops = [ op for op in operation.operands if op.isInput() ]
    outops = [ op for op in operation.operands if op.isOutput() ]
    inouts = [ op.st_info[1] for op in outops if op.st_info[1] != op ]
    # Operation definition
    out_path = os.path.join( os.path.join( lgen_dir, "definition.ll" ) )
    with open( out_path, "w" ) as out:
        # needed when multiple output operands overwrite one same input (e.g., lu)
        declared = []
        # Declaration of operands
        #for op in inouts:
            #if op.st_info[1].name in declared:
                #continue
            #declared.append( op.st_info[1].name )
            ##
            #print( declaration(op, "inout"), file=out )
        for op in inops:
            if op.st_info[1].name in declared:
                continue
            declared.append( op.st_info[1].name )
            #
            if op not in inouts:
                print( declaration(op, "in"), file=out )
            else:
                print( declaration(op, "inout"), file=out )
        for op in outops:
            if op.st_info[1].name in declared:
                continue
            declared.append( op.st_info[1].name )
            #
            if op.st_info[1] == op:
                print( declaration(op, "out"), file=out )
        print( file=out )
        # Operation in implicit form: out = f(in)
        if len( outops ) == 1:
            output = outops[0].st_info[1].name
            #out_dims = ", ".join([ "@%s" % str(s) for s in outops[0].size ])
            out_dims = ", ".join([ "@%s" % str(s) for s in outops[0].st_info[1].size ])
        else:
            output = "[%s]" % ", ".join([ o.st_info[1].name for o in outops ])
            #out_dims = "?"
            out_dims = ", ".join([ "@%s" % str(s) for s in outops[0].st_info[1].size ])
            #raise Exception
        inp = ", ".join([i.name for i in inops])
        name = operation.name
        if Config.options.opt:
            name += "_opt"
        print( "%s = %s(%s; %s);" % (output, name, out_dims, inp), file=out )

    # Dimensions file
    out_path = os.path.join( os.path.join( lgen_dir, "dimtags.txt" ) )
    # Issues 1/2: Dimtags for in and out separately irrespective of overwriting
    with open( out_path, "w" ) as out:
        #for op in inouts:
            #print( "%s %s" % op.size, file=out )
        for op in inops:
            #if op not in inouts:
            print( "%s %s" % op.size, file=out )
        for op in outops:
            #if op.st_info[1] == op:
            print( "%s %s" % op.size, file=out )

    # Produce one algorithm per dimension slicing
    var = 1
    for pme, pme_linv, pme_alg in zip( operation.pmes, operation.linvs, operation.algs ):
        if all( [ part==1 for part in pme.part_tuple] ): # 1x1 partitioning, skip
            continue
        if len( [ psize for psize in pme.part_tuple if psize != 1 ] ) > 1: # multidimensional partitioning, skip
            continue
        # Identify the dimension "name" to identify the output file
        idx_sliced = pme.part_tuple.index( 2 )
        dim_sliced = str(opdim2problemdim( operation, operation.bound_dimensions[idx_sliced][0] ))
        # Create "dimension directory"
        try:
            os.mkdir( os.path.join( lgen_dir, dim_sliced ) )
        except OSError:
            pass
        for linv, alg in zip( pme_linv, pme_alg ):
            print( "+++++ VAR", var )
            #[TODO] This is ugly as hell. FIX!
            alg.operation = operation

            alg.updates = [ replace(u, known_ops_single) for u in alg.updates ]

            #
            # Pass overwrite
            #
            PassCheckPredicateOverwrite( alg )


            #if Config.options.opt:
                ## OPTIMIZATIONS
                ##print( alg.updates )
                #lpla_alg = alg2lpla.alg2lpla( operation, pme, linv, alg, var )
                #print( lpla_alg )
                #mydfg = dfg.lpla2dfg( lpla_alg.body )
                #mydfg.opt_copy_propagation()
                #mydfg.opt_backward_copy_propagation()
                #mydfg.opt_remove_self_assignments()
                ##
                #mydfg.analysis_next_use()
                #mydfg.opt_dead_code_elimination()
                #lpla_alg.body = dfg.dfg2lpla( mydfg )
                #print( lpla_alg )
                #lpla_loop = [ st for st in lpla_alg.body if isinstance( st, lpla._while ) ][0] #[TODO] Ok?
                #new_updates = [ st for st in lpla_loop.body if isinstance(st, Equal) ] 
                #print( new_updates )
                #alg.updates = new_updates

                #lpla_alg = peeling.peel_loop( alg, lpla_alg )
                #mydfg = dfg.lpla2dfg( lpla_alg.body )
                #mydfg.opt_copy_propagation()
                #mydfg.opt_backward_copy_propagation()
                #mydfg.opt_remove_self_assignments()
                ##
                #print( lpla_alg )
                #mydfg.analysis_next_use()
                #mydfg.opt_dead_code_elimination()
                #lpla_alg.body = dfg.dfg2lpla( mydfg )
                #print( lpla_alg )

            lpla_alg = alg2lpla( operation, pme, linv, alg, var )
            # trsm2lgen
            #lpla_loop = [ st for st in lpla_alg.body if isinstance( st, lpla._while ) ][0] #[TODO] Ok?
            #lpla_loop.body = [ replace(u, trsm2lgen_rules) if isinstance(u,Equal) else u for u in lpla_loop.body ]
            #alg.updates = [ replace(u, trsm2lgen_rules) for u in alg.updates ]
            #
            lpla_alg = peeling.peel_loop( alg, lpla_alg, force_tail_peeling=Config.options.sizes=="non-multiple-of-nu" )
            if Config.options.opt:
                # OPTIMIZATIONS
                #
                mydfg = lpla2dfg( lpla_alg.body )
                prev_dfg = copy.deepcopy( mydfg )
                done = False
                print( lpla_alg )
                while not done:
                    mydfg.checkPredicateOverwrite()
                    mydfg.opt_backward_copy_propagation()
                    mydfg.opt_copy_propagation()
                    mydfg.opt_remove_self_assignments()
                    mydfg.analysis_next_use()
                    mydfg.opt_dead_code_elimination()

                    tmp_alg = dfg2lpla( mydfg )
                    print( tmp_alg )

                    done = prev_dfg == mydfg
                    if not done:
                        print( "Not done" )
                        prev_dfg = copy.deepcopy( mydfg )
                lpla_alg.body = dfg2lpla( mydfg )
                #
                lpla_loop = [ st for st in lpla_alg.body if isinstance( st, lpla._while ) ][0] #[TODO] Ok?
                new_updates = [ st for st in lpla_loop.body if isinstance(st, Equal) ] 
                alg.updates = new_updates

            replace_trsm2lgen( lpla_alg )

            #out_path = os.path.join( os.path.join( lgen_dir, dim_sliced + ".ll" ) )
            out_path = os.path.join( lgen_dir, dim_sliced, dim_sliced + "%d.ll" % var )
            with open( out_path, "w" ) as out:
                generate_lgen_algorithm( operation, pme, linv, alg, var, lpla_alg, out )

            var += 1

    # Produce base case algorithm
    scalar_sols = []
    # mapping: operand -> @op_i
    opname2macro = dict()
    for i, op in enumerate(outops):
        opname2macro[ op.name ] = "@out%d@" % i
    for i, op in enumerate(inops):
        opname2macro[ op.name ] = "@op%d@" % i
    #
    scalar_solutions = operation.pmes[0].scalar_solution # [CHECK] this should probably be in operation, not in pme
    for scalar_sol in scalar_solutions:
        lhs, rhs = scalar_sol.split("=")
        lhs = lhs.strip()
        lhs_op = [op for op in outops if op.name == lhs][0]
        if lhs_op.isImplicitUnitDiagonal(): # avoid assigning the implicit value 1
            continue
        #
        for operand in operation.operands:
            scalar_sol = scalar_sol.replace( operand.name, opname2macro[operand.name] )
        scalar_sols.append( scalar_sol )
    out_path = os.path.join( os.path.join( lgen_dir, "1x1.ll" ) )
    with open( out_path, "w" ) as out:
        print( ";\n".join(scalar_sols) + ";", file=out)

def generate_lgen_algorithm( operation, pme, linv, alg, variant, lpla_alg, fout=sys.stdout ):
    inop  = [op for op in operation.operands if op.isInput()]
    outop = [op for op in operation.operands if op.isOutput()]
    tempop = [op for op in linv.linv_operands if op not in inop and op not in outop]
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

    # mapping: operand -> @op_i
    alg.map_opname2macro = dict()
    for i, op in enumerate(outop):
        alg.map_opname2macro[ op.name ] = "@out%d@" % i
    for i, op in enumerate(inop):
        alg.map_opname2macro[ op.name ] = "@op%d@" % i
    # Temporaries should be declared within the function

    alg.indices = dict()

    for op in alg.linv.linv_operands:
        set_loop_indices( op.name, alg )

    temp_size = dict()
    for u in alg.updates:
        lhs, rhs = u.children
        for op in lhs:
            #if not op.isInput() and not op.isOutput():
            if op.isTemporary() and "_" not in op.name: # "_" means part of a whole temporary
                (r,c), (indr, indc) =  lgen_size( rhs, alg )
                temp_size[ op.name ] = op, r, c
                #alg.indices[ op.name ] = ((r,r,"0"), (c,c,"0")) # The middle ones would be problem dimensions, but we don't care for this
                r0, r1, r2 = indr
                c0, c1, c2 = indc
                alg.indices[ op.name ] = ((r0, r, "0"), (c0, c, "0"))

    #
    # Declare temporaries (from tiling updates)
    #
    for op in alg.linv.linv_operands: # [TODO] Refactor, this is just a copy paste of below
        if not op.isTemporary():
            continue
        mat_type = "matrix"
        rows, cols = op.get_size()
        rows, cols = "@"+str(rows)+"@", "@"+str(cols)+"@"
        if op.isLowerTriangular():
            mat_type = "triangular"
            cols = "l"
        elif op.isUpperTriangular():
            mat_type = "triangular"
            cols = "u"
        elif op.isSymmetric():
            mat_type = "symmetric"
            # [FIX] Might need additional code at propagation of properties time
            #if properties.LOWER_STORAGE in op.get_properties():
            if op.st_info[0] == storage.ST_LOWER:
                cols = "l"
            else: # [FIX] Should I consider this the default or is there always a specified storage?
                cols = "u"
        #print( "@%s@: %s<@%s@, @%s@, tinout>;" % (op.name, mat_type, rows, cols), file=fout )
        print( "@%s@: %s<%s, %s, tinout>;" % (op.name, mat_type, rows, cols), file=fout )
        
    for opname, (op, r, c) in temp_size.items():
        mat_type = "matrix"
        rows, cols = str(r), str(c)
        if op.isLowerTriangular():
            mat_type = "triangular"
            cols = "l"
        elif op.isUpperTriangular():
            mat_type = "triangular"
            cols = "u"
        elif op.isSymmetric():
            mat_type = "symmetric"
            #if properties.LOWER_STORAGE in op.get_properties():
            if op.st_info[0] == storage.ST_LOWER:
                cols = "l"
            else: # [FIX] Should I consider this the default or is there always a specified storage?
                cols = "u"
        print( "@%s@: %s<%s, %s, tinout>;" % (op.name, mat_type, rows, cols), file=fout )
    print( file=fout )

    #
    # Basic initialization (if any)
    #
    if alg.init:
        # Set alg.indices
        #for i in alg.init:
        lhs, rhs = alg.init.children
        lhs = lhs.children[0]
        r, c = lhs.get_size()
        r = "@%s@" % r
        c = "@%s@" % c
        alg.indices[ lhs.name ] = ( (r, r, "0"), (c, c, "0") )
        # [FIXME] rhs might be Zero()
        alg.indices[ rhs.name ] = ( (r, r, "0"), (c, c, "0") )
        #
        #print( click2lgen(alg.init, alg) + ";", file=fout)
    #
    # loop header
    if len( alg.guard ) > 1:
        print( "[WARNING] Traversing two dimensions" )
        sys.exit(-1)
    quadrant, op = alg.guard[0]
    # dim needed to the replacement of iterators in peeling
    (it, start, end, step), dim = traversal2loop( alg, op, quadrant, alg.peel_first_it, alg.peel_last_it ) # (..., peel_first?, peel_last?)
    #
    # Get bounds for top and bottom (repart, cont_with)
    #
    loop_pre_bounds = [0]
    for i,st in enumerate(lpla_alg.body):
        if isinstance( st, lpla._while ):
            loop_pre_bounds.append( i )
            break
    loop_post_bounds = [ loop_pre_bounds[1] + 1 ]
    loop_post_bounds.append( len(lpla_alg.body) )
    #
    # Peel first iteration
    for i in range(loop_pre_bounds[0], loop_pre_bounds[1]):
        update = lpla_alg.body[i]
        if not isinstance( update, Equal ):
            continue
        print( "%%%% %s" % update, file=fout )
        indices_backup = copy.deepcopy(alg.indices)
        alg.indices = replace_iterator_in_indices( alg.indices, it, "0" )
        alg.indices = replace_iterator_in_indices( alg.indices, "@nb@", "min(@nb@,@%s@)"%dim )
        print( "" + click2lgen(update, alg) + ";", file=fout )
        alg.indices = indices_backup
    # body
    print( "For[ %s; %s; %s; %s ]" % (it, start, end, step), file=fout )
    print( "{", file=fout )
    loop = lpla_alg.body[ loop_pre_bounds[1] ]
    #for u in alg.updates:
    for update in loop.body:
        if not isinstance( update, Equal ):
            continue
        print( "\t%%%% %s" % update, file=fout )
        print( "\t" + click2lgen(update, alg) + ";", file=fout )
    print( "};", file=fout )
    # Peel last iteration
    for i in range(loop_post_bounds[0], loop_post_bounds[1]):
        update = lpla_alg.body[i]
        if not isinstance( update, Equal ):
            continue
        indices_backup = copy.deepcopy(alg.indices)
        #alg.indices = replace_iterator_in_indices( alg.indices, it, "(@%s@-@nb@)" % dim )
        # Still, some zero op may remain, if rhs is predicate and lhs is temporary
        # [FIXME] What if multiple outputs. Not supported yet by LGEN.
        lhs, rhs = update.children
        lhs = lhs.children[0]
        ((r, _, _), (c, _, _)) = alg.indices[lhs.get_name()]
        r = r.replace("@", "")
        c = c.replace("@", "")
        r_sympy = sympy.sympify(r)
        c_sympy = sympy.sympify(c)
        # [CHECK] Think about and/or?
        #iszero = r_sympy is sympy.S.Zero and c_sympy is sympy.S.Zero
        iszero = r_sympy is sympy.S.Zero or c_sympy is sympy.S.Zero
        if iszero:
            continue
        #
        if alg.peel_first_it:
            post_min_start = "min(@%s@,@nb@)" % dim
        else:
            post_min_start = "0"
        #if alg.needs_tail_peeling:
        if not alg.needs_tail_peeling: # enforced
            print("If[(@%s@ %% @%s@) == 0] {" % (dim, "nb"), file=fout)
            # print("If[mod(@%s@, @%s@) == 0] {" % (dim, "nb"), file=fout)
            # start
            alg.indices = replace_iterator_in_indices( alg.indices, it, "max(@%s@-@nb@, %s)" % (dim, post_min_start) )
            # size
            #alg.indices = replace_iterator_in_indices( alg.indices, "@nb@", "min(@nb@, @%s@-@%s@%%@nb@)" % (dim, dim) )
            print( "\t%%%% %s" % update, file=fout )
            print( "\t" + click2lgen(update, alg) + ";", file=fout )
            print("};", file=fout)
            alg.indices = indices_backup
            #
            print("If[(@%s@ %% @%s@) != 0] {" % (dim, "nb"), file=fout)
            # print("If[mod(@%s@, @%s@) != 0] {" % (dim, "nb"), file=fout)
            # start
            alg.indices = replace_iterator_in_indices( alg.indices, it, "max(@%s@-(@%s@%%@nb@), %s)" % (dim, dim, post_min_start) )
            # alg.indices = replace_iterator_in_indices( alg.indices, it, "max(@%s@-mod(@%s@,@nb@), %s)" % (dim, dim, post_min_start) )
            # size
            alg.indices = replace_iterator_in_indices( alg.indices, "@nb@", "min(@nb@, @%s@%%@nb@)" % dim )
            # alg.indices = replace_iterator_in_indices( alg.indices, "@nb@", "min(@nb@, mod(@%s@,@nb@))" % dim )
            print( "\t%%%% %s" % update, file=fout )
            print( "\t" + click2lgen(update, alg) + ";", file=fout )
            print("};", file=fout)
            alg.indices = indices_backup
        else:
            # size
            #alg.indices = replace_iterator_in_indices( alg.indices, "@nb@", "min(@nb@, @%s@%%@nb@)" % dim )
            #alg.indices = replace_iterator_in_indices( alg.indices, "@nb@", "min(@nb@, mod(@%s@,@nb@))" % dim )
            # start
            #alg.indices = replace_iterator_in_indices( alg.indices, it, "max(@%s@-@%s@%%@nb@, %s)" % (dim, dim, post_min_start) )
            #alg.indices = replace_iterator_in_indices( alg.indices, it, "max(@%s@-mod(@%s@,@nb@), %s)" % (dim, dim, post_min_start) )
            alg.indices = replace_iterator_in_indices( alg.indices, it, "max(@%s@-@nb@, %s)" % (dim, post_min_start) )
            print( "%%%% %s" % update, file=fout )
            print( "" + click2lgen(update, alg) + ";", file=fout )
            alg.indices = indices_backup
        #print( "%% %s" % update, file=fout )
        #print( "" + click2lgen(update, alg) + ";", file=fout )
        #alg.indices = indices_backup
    print( "", file=fout )

def click2lgen( node, alg ):
    def _click2lgen( node ):
        if isinstance( node, Symbol ):
            #return str(node)
            # indices
            try:
                indices = alg.indices[ str(node) ]
                ind_str = "[h(%s), h(%s)]" % (",".join(indices[0]), ",".join(indices[1]))
            except Exception as e: # temporary in update tiling (not partitioned, repartitioned, ...)
                ind_str = ""
            # properties
            all_props = node.get_properties()
            props = [] # properties of interest
            for p in all_props:
                if p == properties.LOWER_TRIANGULAR:
                    props.append( str( p ) )
                elif p == properties.UPPER_TRIANGULAR:
                    props.append( str( p ) )
                elif p == properties.SYMMETRIC or p == properties.SPD:
                    if "Symmetric" not in props:
                        props.append( "Symmetric" )
                        #if properties.LOWER_STORAGE in node.get_properties():
                        if node.st_info[0] == storage.ST_LOWER:
                            props.append( "LSMatAccess" )
                        else:
                            props.append( "USMatAccess" )
            if props:
                props_str = "#" + ",".join(props) + "#"
            else:
                props_str = ""
            # remove subscript
            try:
                opname, part = node.name.split("_")
            except ValueError:
                opname = node.name
            try:
                opname = map_opname2macro[ opname ]
            except KeyError: # temporary from update tiling
                opname = "@"+opname+"@" #[TODO] Back to setting it here for everyone, no need to spread @s all over
            return opname + ind_str + props_str
        elif isinstance( node, Plus ):
            # [FIX] Quick & dirty to print in a more convenient way for lgen
            sorted_ch = [ ch for ch in node.get_children() if not isinstance(ch, Times) ]
            sorted_ch += [ ch for ch in node.get_children() if isinstance(ch, Times) ]
            for c in sorted_ch:
                print(c)
            return " + ".join( [ _click2lgen(ch) for ch in sorted_ch ] )
            #return " + ".join( [ _click2lgen(ch) for ch in node.get_children()] )
        elif isinstance( node, Times ):
            return " * ".join( [ _click2lgen(ch) for ch in node.get_children()] )
        elif isinstance( node, Minus ):
            return "-" + _click2lgen(node.get_children()[0])
        elif isinstance( node, Transpose ):
            return "trans(" + _click2lgen(node.get_children()[0]) + ")"
        elif isinstance( node, Inverse ):
            return "inv(" + _click2lgen(node.get_children()[0]) + ")"
        elif isinstance( node, Equal ):
            lhs, rhs = node.get_children()
            if isinstance( rhs, Predicate ): # [FIX] Not clean. Should be taken care of somewhere else
                # [FIX] assumes one single output
                lhs_op = lhs.children[0]
                lhs_idxs = alg.indices[ lhs_op.name ]
                rhs.size = [(lhs_idxs[0][0], lhs_idxs[1][0])]
            #
            if len( lhs.get_children() ) > 1:
                return "[" + ", ".join( _click2lgen(elem) for elem in lhs ) + "] = " + _click2lgen(rhs) 
            else:
                return _click2lgen( lhs.get_children()[0] ) + " = " + _click2lgen(rhs) 
        elif isinstance( node, Predicate ):
            name = node.get_name()
            #sizes = ", ".join(node.size)
            sizes = node.get_size()
            if isinstance( sizes[0], Symbol ):
                sizes = [ "@%s@" % s for s in sizes ]
            sizes = ", ".join(sizes)
            #
            in_args = ", ".join( _click2lgen(arg) for arg in node.get_children() )
            # [CHECK] Is it reasonable to do it this way?
            if Config.options.opt:
                name += "_opt"
            return "%s(%s; %s)" % (name, sizes, in_args)
    #map_opname2macro = dict()
    #for i, op in enumerate(alg.linv.linv_operands):
        #map_opname2macro[ op.name ] = i
    map_opname2macro = alg.map_opname2macro
    return _click2lgen( node )

def traversal2loop( alg, opname, quadrant, peel_first, peel_last ):
    quadrant, op = opname #[TODO] Cleanup (due to some changes for the generation of flamec)
    #op = [ op for op in alg.linv.linv_operands if op.name == opname ][0]
    # dims
    if quadrant in ("L", "R"): # partitioning the operands' column dimension
        dim = op.size[1]
    elif quadrant in ("T", "B"): # partitioning the operands' row dimension
        dim = op.size[0]
    else:
        dim = op.size[0]
    # iterator
    it = "@it@"
    # step
    step = "@%s@" % "nb"
    # start
    start = "0"
    if peel_first:
        start = step
    # end
    # if peeled to avoid ops with empty objects
    if alg.needs_tail_peeling:
        end = "@%s@-(@nb@+1)" % dim
    # if instead peeled enforced due to sizes non-multiple of nu
    elif Config.options.sizes == "non-multiple-of-nu":
        end = "@%s@-((@%s@%%@nb@)+1)" % (dim, dim)
        # end = "@%s@-(mod(@%s@,@nb@)+1)" % (dim, dim)
    # otherwise, for multiples of nu, no peeling, thus this suffices
    else:
        end = "@%s@-(@nb@)" % dim
    return ( it, start, end, step ), dim

def set_loop_indices( opname, alg ):
    op = [op for op in alg.linv.linv_operands if op.name == opname ][0]
    try:
        shape, repart_flat, _ = alg.repartition[ opname ]
        trav = alg.linv.traversals[0][0][opname]
    except KeyError:
        shape = (1,1)
        repart_flat = [[op]]
        trav = None
    #
    it = "@it@"
    vlen = "@nb@"
    if shape == (1,1):
        m,n = op.size
        if m == sONE:
            dim_m = "1"
        else:
            dim_m = "@%s@" % m
        if n == sONE:
            dim_n = "1"
        else:
            dim_n = "@%s@" % n
        alg.indices[str(op)] = ((dim_m, dim_m, "0"), (dim_n, dim_n, "0"))
    elif shape == (1,3):
        m,n = op.size
        dim_m = "@%s@" % m
        dim_n = "@%s@" % n
        [A0, A1, A2] = repart_flat
        if trav == (0,1):
            # rows
            rows0 = dim_m
            start_r0 = "0"
            # cols
            start_c0 = "0"
            cols0 = "%s" % it
            start_c1 = cols0
            cols1 = "%s" % vlen
            start_c2 = "%s+%s" % (it, vlen)
            cols2 = "%s-(%s)" % (dim_n, start_c2)
            alg.indices[str(A0)] = ((rows0, dim_m, start_r0), (cols0, dim_n, start_c0))
            alg.indices[str(A1)] = ((rows0, dim_m, start_r0), (cols1, dim_n, start_c1))
            alg.indices[str(A2)] = ((rows0, dim_m, start_r0), (cols2, dim_n, start_c2))
        else:
            cols1 = vlen
            start1 = "%s-(%s+1)*%s)" % (dim_n, it, vlen)
            cols2 = "%s*%s" % (it, vlen)
            start2 = "%s-(%s)" % (dim_n, cols2)
            cols0 = start1
            start0 = "0"
            A0.indices = ((dim_m, dim_m, "0"), (cols0, dim_n, start0))
            A1.indices = ((dim_m, dim_m, "0"), (cols1, dim_n, start1))
            A2.indices = ((dim_m, dim_m, "0"), (cols2, dim_n, start2))
            # rows
            rows0 = dim_m
            start_r0 = "0"
            # cols
            start_c2 = "%s-%s" % (dim_n, it)
            cols2 = "%s" % it
            start_c1 = "%s-(%s+%s)" % (dim_n, it, vlen)
            cols1 = "%s" % vlen
            start_c0 = "0"
            cols0 = start_c1
            #
            alg.indices[str(A0)] = ((rows0, dim_m, start_r0), (cols0, dim_n, start_c0))
            alg.indices[str(A1)] = ((rows0, dim_m, start_r0), (cols1, dim_n, start_c1))
            alg.indices[str(A2)] = ((rows0, dim_m, start_r0), (cols2, dim_n, start_c2))
    elif shape == (3,1):
        m,n = op.size
        dim_m = "@%s@" % m
        dim_n = "@%s@" % n
        [A0, A1, A2] = repart_flat
        if trav == (1,0):
            # rows
            start_r0 = "0"
            rows0 = "%s" % it
            start_r1 = rows0
            rows1 = "%s" % vlen
            start_r2 = "%s+%s" % (it, vlen)
            rows2 = "%s-(%s)" % (dim_m, start_r2)
            # cols
            cols0 = dim_n
            start_c0 = "0"
            #
            alg.indices[str(A0)] = ((rows0, dim_m, start_r0), (cols0, dim_n, start_c0))
            alg.indices[str(A1)] = ((rows1, dim_m, start_r1), (cols0, dim_n, start_c0))
            alg.indices[str(A2)] = ((rows2, dim_m, start_r2), (cols0, dim_n, start_c0))
        elif trav == (-1,0):
            # rows
            start_r2 = "%s-%s" % (dim_m, it)
            rows2 = it
            start_r1 = "%s-(%s+%s)" % (dim_m, it, vlen)
            rows1 = "%s" % vlen
            start_r0 = "0"
            rows0 = start_r1
            # cols
            cols0 = dim_n
            start_c0 = "0"
            #
            alg.indices[str(A0)] = ((rows0, dim_m, start_r0), (cols0, dim_n, start_c0))
            alg.indices[str(A1)] = ((rows1, dim_m, start_r1), (cols0, dim_n, start_c0))
            alg.indices[str(A2)] = ((rows2, dim_m, start_r2), (cols0, dim_n, start_c0))
    elif shape == (3,3):
        m,n = op.size
        dim_m = "@%s@" % m
        dim_n = "@%s@" % n
        [A00, A01, A02,
         A10, A11, A12,
         A20, A21, A22] = repart_flat
        if trav == (1,1): # TL to BR
            # rows
            start_r0 = "0"
            rows0 = "%s" % it
            start_r1 = rows0
            rows1 = "%s" % vlen
            start_r2 = "%s+%s" % (it, vlen)
            rows2 = "%s-(%s)" % (dim_m, start_r2)
            # cols
            start_c0 = "0"
            cols0 = "%s" % it
            start_c1 = cols0
            cols1 = "%s" % vlen
            start_c2 = "%s+%s" % (it, vlen)
            cols2 = "%s-(%s)" % (dim_n, start_c2)
            # indices
            alg.indices[str(A00)] = ((rows0, dim_m, start_r0), (cols0, dim_n, start_c0))
            alg.indices[str(A01)] = ((rows0, dim_m, start_r0), (cols1, dim_n, start_c1))
            alg.indices[str(A02)] = ((rows0, dim_m, start_r0), (cols2, dim_n, start_c2))
            alg.indices[str(A10)] = ((rows1, dim_m, start_r1), (cols0, dim_n, start_c0))
            alg.indices[str(A11)] = ((rows1, dim_m, start_r1), (cols1, dim_n, start_c1))
            alg.indices[str(A12)] = ((rows1, dim_m, start_r1), (cols2, dim_n, start_c2))
            alg.indices[str(A20)] = ((rows2, dim_m, start_r2), (cols0, dim_n, start_c0))
            alg.indices[str(A21)] = ((rows2, dim_m, start_r2), (cols1, dim_n, start_c1))
            alg.indices[str(A22)] = ((rows2, dim_m, start_r2), (cols2, dim_n, start_c2))
        elif trav == (-1,-1): # BR to TL
            # rows
            start_r2 = "%s-%s" % (dim_m, it)
            rows2 = it
            start_r1 = "%s-(%s+%s)" % (dim_m, it, vlen)
            rows1 = "%s" % vlen
            start_r0 = "0"
            rows0 = start_r1
            # cols
            start_c2 = "%s-%s" % (dim_n, it)
            cols2 = "%s" % it
            start_c1 = "%s-(%s+%s)" % (dim_n, it, vlen)
            cols1 = "%s" % vlen
            start_c0 = "0"
            cols0 = start_c1
            # indices
            alg.indices[str(A00)] = ((rows0, dim_m, start_r0), (cols0, dim_n, start_c0))
            alg.indices[str(A01)] = ((rows0, dim_m, start_r0), (cols1, dim_n, start_c1))
            alg.indices[str(A02)] = ((rows0, dim_m, start_r0), (cols2, dim_n, start_c2))
            alg.indices[str(A10)] = ((rows1, dim_m, start_r1), (cols0, dim_n, start_c0))
            alg.indices[str(A11)] = ((rows1, dim_m, start_r1), (cols1, dim_n, start_c1))
            alg.indices[str(A12)] = ((rows1, dim_m, start_r1), (cols2, dim_n, start_c2))
            alg.indices[str(A20)] = ((rows2, dim_m, start_r2), (cols0, dim_n, start_c0))
            alg.indices[str(A21)] = ((rows2, dim_m, start_r2), (cols1, dim_n, start_c1))
            alg.indices[str(A22)] = ((rows2, dim_m, start_r2), (cols2, dim_n, start_c2))
        else:
            print( opname, shape )
            raise Exception

# This is for temporaries from update tiling
def lgen_size( node, alg ):
    def _lgen_size( node ):
        if isinstance( node, Symbol ):
            # if one of the sizes is @it@, replace with full dimension
            # this is because it will grow (or shrink) from 0 -> dim (or dim -> 0)
            #   so we allocate once before the loop with the large size
            r0, r1, r2 = alg.indices[ str(node) ][0]
            c0, c1, c2 = alg.indices[ str(node) ][1]
            r = r0
            #if r == "@it@":
            if "@it@" in r:
                r = r1 # the actual dimension from the h() notation
                #r0 = r1
            c = c0
            #if c == "@it@":
            if "@it@" in c:
                c = c1 # the actual dimension from the h() notation
                #c0 = c1
            #alg.indices[ str(node) ] = ((r0, r1, r2), (c0, c1, c2))
            return (r,c), ((r0, r1, r2), (c0, c1, c2))
        elif isinstance( node, Plus ):
            return _lgen_size( node.children[0] )
        elif isinstance( node, Times ): # [FIX] lets assume no scalars for now...
            #r = _lgen_size( node.children[0] )[0]
            #c = _lgen_size( node.children[-1] )[1]
            first = _lgen_size( node.children[0] )
            last  = _lgen_size( node.children[-1] )
            r,c  = first[0][0], last[0][1]
            indr, indc = first[1][0], last[1][1]
            return (r,c), (indr, indc)
        elif isinstance( node, Minus ):
            return _lgen_size( node.children[0] )
        elif isinstance( node, Transpose ):
            rc, inds = _lgen_size( node.children[0] )
            #return tuple( reversed( _lgen_size( node.children[0] ) ) )
            return tuple(reversed(rc)), tuple(reversed(inds))
        elif isinstance( node, Inverse ):
            return _lgen_size( node.children[0] )
        elif isinstance( node, Predicate ):
            pred_name = node.name
            [((row_idx, row_op, row_dim), (col_idx, col_op, col_dim))] =  pm.DB[pred_name].output_size
            # row sizes
            (r,c), ((r0, r1, r2), (c0, c1, c2)) = _lgen_size( node.children[row_idx] )
            if row_dim == "r":
                pred_r = r
                pred_r012 = (r0, r1, r2)
            else:
                pred_r = c
                pred_r012 = (c0, c1, c2)
            # col sizes
            (r,c), ((r0, r1, r2), (c0, c1, c2)) = _lgen_size( node.children[col_idx] )
            if col_dim == "r":
                pred_c = r
                pred_c012 = (r0, r1, r2)
            else:
                pred_c = c
                pred_c012 = (c0, c1, c2)
            return (pred_r, pred_c), (pred_r012, pred_c012)
    return _lgen_size( node )

def replace_iterator_in_indices( indices, old_it_value, new_it_value ):
    new_indices = dict()
    for k,v in indices.items():
        new_v = [ [ i.replace( old_it_value, new_it_value ) for i in idx ] for idx in v ]
        new_indices[ k ] = new_v
    return new_indices

def opdim2problemdim( operation, opdim ):
    opname, dim = opdim.split("_") # e.g., L_r
    op = [op for op in operation.operands if op.name == opname][0]
    r,c = op.size
    if dim == "r":
        return r
    else:
        return c

def declaration( op, iotype ):
    mat_type = "matrix" #[FIXME] Generalize
    rows, cols = "@"+str(op.size[0]), "@"+str(op.size[1])
    if op.isLowerTriangular():
        mat_type = "triangular"
        cols = "l"
    elif op.isUpperTriangular():
        mat_type = "triangular"
        cols = "u"
    elif op.isSymmetric():
        mat_type = "symmetric"
        if op.st_info[0] == storage.ST_LOWER:
            cols = "l"
        else: # [THINK] Should I consider this the default or is there always a specified storage?
            cols = "u"
    return "%s: %s<%s, %s, %s>;" % (op.name, mat_type, rows, cols, iotype)

def replace_trsm2lgen( node ):
    if isinstance( node, lpla.function ) or isinstance( node, lpla._while):
        node.body = [ replace_trsm2lgen( st ) for st in node.body ]
        return node
    elif isinstance( node, Equal ):
        return replace(node, trsm2lgen_rules)
    else:
        return node
