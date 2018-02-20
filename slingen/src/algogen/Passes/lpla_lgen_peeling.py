import copy

from core.expression import Symbol, sONE, sZERO, Equal, Predicate
from core.algebraic_manipulation import to_canonical, simplify
from core.builtin_operands import Zero
from core.functional import replace, RewriteRule, Replacement

import Passes.lpla as lpla

def peel_loop( alg, lpla_alg, force_tail_peeling=True ):
    # Grab while loop
    line, lpla_loop = [ (i,st) for i,st in enumerate(lpla_alg.body) if isinstance( st, lpla._while ) ][0]
    # Get bounds for top and bottom (repart, cont_with)
    loop_top_bounds = [0]
    for i,st in enumerate(lpla_loop.body):
        if isinstance( st, Equal ):
            loop_top_bounds.append( i )
            break
    loop_bottom_bounds = []
    start = loop_top_bounds[1]
    for i,st in enumerate(lpla_loop.body[start:], start=start):
        if isinstance( st, Equal ):
            continue
        loop_bottom_bounds.append( i )
        break
    loop_bottom_bounds.append( len(lpla_loop.body) )
    # Calculate peelings
    initial_rules = initial_rewrite_rules( alg )
    final_rules = final_rewrite_rules( alg )
    pre  = rewrite_computation( alg, initial_rules )
    post = rewrite_computation( alg, final_rules )
    #
    # Build peeling pre and post loop
    # Same length as well, otherwise zip truncates and may lead to errors
    if len(pre) == len(alg.updates) and  all( [p == u for p,u in zip( pre, alg.updates )] ):
        peeling_pre = []
        alg.peel_first_it = False
    else:
        peeling_pre = []
        for i in range( loop_top_bounds[0], loop_top_bounds[1] ):
            peeling_pre.append( copy.deepcopy( lpla_loop.body[i] ) )
        peeling_pre.extend( pre )
        for i in range( loop_bottom_bounds[0], loop_bottom_bounds[1] ):
            peeling_pre.append( copy.deepcopy( lpla_loop.body[i] ) )
        alg.peel_first_it = True
    # Same length as well, otherwise zip truncates and may lead to errors
    if len(post) == len(alg.updates) and  all( [p == u for p,u in zip( post, alg.updates )] ):
        alg.needs_tail_peeling = False 
    else:
        alg.needs_tail_peeling = True # Peeling is needed to avoid if statements within 
                                      # the loop (access to empty flame objects)
    if not alg.needs_tail_peeling and not force_tail_peeling:
        peeling_post = []
        alg.peel_last_it = False
    else:
        peeling_post = []
        for i in range( loop_top_bounds[0], loop_top_bounds[1] ):
            peeling_post.append( copy.deepcopy( lpla_loop.body[i] ) )
        peeling_post.extend( post )
        for i in range( loop_bottom_bounds[0], loop_bottom_bounds[1] ):
            peeling_post.append( copy.deepcopy( lpla_loop.body[i] ) )
        alg.peel_last_it = True
    # Attach
    lpla_alg.body[line+1:line+1] = peeling_post
    lpla_alg.body[line:line] = peeling_pre

    return lpla_alg

def rewrite_computation( alg, rules ):
    computation = []
    for u in alg.updates:
        new = copy.deepcopy( u )
        new_replaced = simplify( to_canonical( replace( new, rules ) ) )
        lhs, rhs = new_replaced.get_children()
        # [FIXME] Not necessarily enough if any arg in predicate is zero!!!
        #if not ( all( op.isZero() for op in lhs ) or rhs.isZero() ):
        if not ( all( op.isZero() for op in lhs ) or rhs.isZero() or \
                isinstance(rhs, Predicate) and any([ch.isZero() for ch in rhs.children])):
            computation.append( new_replaced )
    return computation

def initial_rewrite_rules( alg ):
    rules = []
    for op in alg.linv.linv_operands:
        rules.extend( initial_rewrite_rules_per_op( alg, op ) )
    return rules

def initial_rewrite_rules_per_op( alg, op ):
    opname = op.name
    try:
        shape, repart_flat, _ = alg.repartition[ opname ]
        trav = alg.linv.traversals[0][0][opname]
    except KeyError: # Temporary from tiling updates, never empty itself
        #shape = (1,1)
        #repart_flat = [[op]]
        #trav = None
        return []
    return peeling_rewrite_rules( shape, repart_flat, trav )

def final_rewrite_rules( alg ):
    rules = []
    for op in alg.linv.linv_operands:
        rules.extend( final_rewrite_rules_per_op( alg, op ) )
    return rules

def final_rewrite_rules_per_op( alg, op ):
    opname = op.name
    try:
        shape, repart_flat, _ = alg.repartition[ opname ]
        trav = alg.linv.traversals[0][0][opname]
    except KeyError:
        #shape = (1,1)
        #repart_flat = [[op]]
        #trav = None
        return []

    # swap trav and reuse initial_rewrite
    swap_dict = {1:-1, 0:0,  -1:1}
    r, c = trav
    trav = swap_dict[r], swap_dict[c]
    # could do r*=-1, c*=-1. Less readable
    return peeling_rewrite_rules( shape, repart_flat, trav )


def peeling_rewrite_rules( shape, repart_flat, trav ):
    zero = Zero( (sZERO, sZERO) ) # Why can I simply use sZERO? It is not registered in the TOS ???
    if shape == (1, 1):
        return []
    elif shape == (1, 3): # [0|1|2]
        [A0, A1, A2] = repart_flat
        if trav == (0, 1): # Left to Right, initially Left is empty, Right is the full operand
            rewrite = [ zero, A1, A2 ]
        elif trav == (0, -1): # Right to Left
            rewrite = [ A0, A1, zero ]
    elif shape == (3, 1): # [0/1/2]
        [A0, A1, A2] = repart_flat
        if trav == (1, 0): # Top to Bottom
            rewrite = [ zero, A1, A2 ]
        elif trav == (-1, 0): # Bottom to Top
            rewrite = [ A0, A1, zero ]
    elif shape == (3, 3): # [TL TR; BL BR]
        [A00, A01, A02,
         A10, A11, A12,
         A20, A21, A22] = repart_flat
        if trav == (1, 1): # Top Left to Bottom Right
            rewrite = [ zero, zero, zero,
                        zero, A11,   A12,
                        zero, A21,   A22 ]
        elif trav == (1, -1): # Top Right to Bottom Left
            rewrite = [ zero, zero, zero,
                        A10,   A11,   zero,
                        A20,   A21,   zero ]
        elif trav == (-1, 1): # Bottom Left to Top Right
            rewrite = [ zero, A01,   A02,
                        zero, A11,   A12,
                        zero, zero, zero ]
        elif trav == (-1, -1): # Bottom Right to Top Left
            rewrite = [ A00,   A01,   zero,
                        A10,   A11,   zero,
                        zero, zero, zero ]

    return [ RewriteRule( p, Replacement( rew ) ) for p, rew in zip (repart_flat, rewrite) if p != rew ]
