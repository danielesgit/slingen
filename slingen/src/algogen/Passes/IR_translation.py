import copy

from Passes import lpla
from Passes import dfg

def alg2lpla( operation, pme, linv, alg, variant ):
    # function
    inop  = [op for op in operation.operands if op.isInput()]
    outop = [op for op in operation.operands if op.isOutput()]
    f = lpla.function( operation.name, variant, inop, outop )
    # temporary operands
    tempop = [op for op in linv.linv_operands if op not in inop and op not in outop]
    for op in tempop:
        f.add_statement( lpla.declare( op ) )
    # Basic initialization (if any)
    if alg.init:
        f.add_statement( alg.init )
    # Partitioning
    for op in linv.linv_operands:
        if op.st_info[1].name != op.name:
            continue
        try:
            shape, flat, quad = alg.partition[ op.get_name() ]
            if not op.isTemporary():
                flat = pme.basic_partitionings[ op.get_name() ].flatten_children() # [FIX] Clarify
            size = alg.partition_size[ op.get_name() ]
        except KeyError:
            continue
        part = lpla.partition( op, shape, flat, quad, size )
        f.add_statement( part )

    # Loop
    guard = alg.guard
    loop = lpla._while( guard )
    # Repart
    repartitionings = []
    for op in linv.linv_operands:
        if op.st_info[1].name != op.name:
            continue
        try:
            part_size, part_flat, part_quad = alg.partition[ op.get_name() ]
            if not op.isTemporary():
                part_flat = pme.basic_partitionings[ op.get_name() ].flatten_children() # [FIX] Clarify
            repart_size, repart_flat, repart_quad = alg.repartition[ op.get_name() ]
            repart_flat = alg.basic_repart[ op.get_name() ].flatten_children() # [FIX] Clarify
        except:
            continue
        r,c = op.get_size()
        if part_size == (1, 2):
            middle_quad_size = (r, "%sb" % c)
        elif part_size == (2, 1):
            middle_quad_size = ("%sb" % r, c)
        elif part_size == (2, 2):
            middle_quad_size = ("%sb" % r, "%sb" % c)
        repart = lpla.repartition( part_flat, repart_size, repart_flat, repart_quad, middle_quad_size )
        loop.add_statement( repart )
    # Body
    for u in alg.updates:
        loop.add_statement( u )
    # Progress
    for op in linv.linv_operands:
        if op.st_info[1].name != op.name:
            continue
        try:
            part_size, part_flat, part_quad = alg.partition[ op.get_name() ]
            if not op.isTemporary():
                part_flat = pme.basic_partitionings[ op.get_name() ].flatten_children() # [FIX] Clarify
            repart_size, repart_flat, repart_quad = alg.repartition[ op.get_name() ]
            repart_flat = alg.basic_repart[ op.get_name() ].flatten_children() # [FIX] Clarify
            cont_with_quad = alg.cont_with[ op.get_name() ]
        except:
            continue
        progress = lpla.progress( repart_flat, repart_size, part_flat, cont_with_quad )
        loop.add_statement( progress )
    # Attach loop
    f.add_statement( loop )
    # Combine/aggregate
    for op in outop: # Input operands do not need to be reconstructed
        try:
            part_size, part_flat, part_quad = alg.partition[ op.get_name() ] #[FIXME] no part_flat from pme.basic...?
            part_flat = pme.basic_partitionings[ op.get_name() ].flatten_children() # [FIX] Clarify
            comb = lpla.combine( part_flat,
                                 part_size, # shape from partitioned object?
                                 op )
        except KeyError:
            continue
        f.add_statement( comb )
    return f

def lpla2dfg( code ):
    graph = dfg.dfg()

    def lpla2dfg_( code, offset_idx = 0 ):
        idx = 0
        while idx < len(code):
            if isinstance( code[idx], lpla._while ):
                break
            idx += 1
        #
        if idx == len(code):
            node = dfg.dfg_node( copy.deepcopy(code), offset_idx )
            graph.nodes.append( node )
        else:
            node = dfg.dfg_node( copy.deepcopy( code[:idx]), offset_idx )
            graph.nodes.append( node )
            loop_node = lpla2dfg_( code[ idx ].body, offset_idx+idx )
            loop_node.lpla_node = code[idx]
            loop_node.add_successor( loop_node )
            node.add_successor( loop_node )
            if idx < len(code) - 1: # There is more code after the loop
                after_loop_node = lpla2dfg_( code[idx+1:], offset_idx+idx+1 )
                loop_node.add_successor( after_loop_node )
                node.add_successor( after_loop_node )
        return node

    graph.root = lpla2dfg_( code )
    for node in graph.nodes:
        node.graph = graph
    return graph

def dfg2lpla( dfg ):
    dfg.clear_visited()
    body = []

    stack = [dfg.root]
    while( stack ):
        node = stack.pop()
        if node.visited:
            continue
        node.visited= True
        #
        node_body = node.statements
        try:
            lpla_node = node.lpla_node
            lpla_node.body = node.statements
            node_body = [lpla_node]
        except AttributeError:
            pass
        body.extend( node_body )
        stack.extend( reversed(node.successors) )
    return body
