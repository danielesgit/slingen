import copy
import itertools

from core.expression import Symbol, Matrix, Vector, Predicate, \
                            Equal, Plus, Minus, Times, Transpose, \
                            PatternDot, PatternStar
from core.functional import Constraint, Replacement, RewriteRule, replace_all, match
import core.TOS as TOS

from CoreExtension import isOperand
from BuildingBlocks import instruction_set

def tile_expr( _expr ):
    tiles = []
    expr = copy.deepcopy( _expr )
    lhs, rhs = expr.get_children()
    if isinstance( rhs, Predicate ):
        tiles_per_arg = []
        for i, arg in enumerate( rhs.get_children() ):
            if not isOperand( arg ):
                tiles_per_arg.append( list(all_tilings( arg )) )
            else:
                tiles_per_arg.append( [[arg]] )
        cross = itertools.product( *tiles_per_arg )
        for comb in cross:
            new_pred = copy.deepcopy( rhs )
            new_ch = [ t[-1] for t in comb ]
            for i,ch in enumerate( new_ch ):
                new_pred.set_children( i, ch )
            updates = list(itertools.chain.from_iterable( [t[:-1] for t in comb] ))
            tiles.append( updates + [Equal([lhs, new_pred])] )
    else:
        if isOperand(rhs):
            tiles.append( [_expr] )
        else:
            for tiling in all_tilings( rhs ):
                last = tiling.pop() # This is just a (temporary) symbol (output of one-to-last)
                one_to_last = tiling.pop()
                lhs, rhs = expr.get_children()
                one_to_last.set_children( 0, lhs ) # assign one-to-last to actual lhs of eq
                tiling.append( one_to_last )
                tiles.append( tiling )
    return tiles

def all_tilings( expr ):
    ongoing = [ [expr] ]
    while len( ongoing ) > 0:
        alg = ongoing.pop()
        to_tile = alg.pop()
        if isOperand( to_tile ):
            alg.append( to_tile )
            yield alg
            continue
        to_tile = replace_all( copy.deepcopy( to_tile), grouping_rules )
        for collection in reversed(instruction_set):
            matched_in_this_level = False ### These are just control vars
                                          ### to avoid redundancies
            for instr in collection:
                for node in to_tile.iterate_preorder():
                    # To avoid redundancies
                    matched_this_node = [] ###
                    if isinstance( instr, tuple ): # A way to deactivate some for quick development/debugging?
                        continue
                    for _m in instr.match( node ):
                        matched_in_this_level = True ###
                        #_T = TOS.new_temp()
                        new = copy.deepcopy( to_tile )
                        #tile, new = instr.tile( new, _m, _T )
                        tile, new = instr.tile( new, node, _m )
                        lhs, rhs = tile.get_children()
                        if rhs not in matched_this_node: ###
                            matched_this_node.append( rhs ) ###
                            ongoing.append( alg[:] + [tile, new] )
                            # Set size of new temporary
                            lhs.children[0].size = rhs.get_size()
                        else:
                            # Aestetic. Simply to avoid missing T? values.
                            TOS.push_back_temp( )
                            TOS._TOS.unset_operand( tile.children[0].children[0] )
            if matched_in_this_level: ###
                break


PD1 = PatternDot("PD1")
PD2 = PatternDot("PD2")
PS1 = PatternStar("PS1")
PS2 = PatternStar("PS2")

grouping_rules = [
    # A B + A C D -> A (B + C D)
    RewriteRule(
        Plus([ Times([ PD1, PS1 ]), Times([ PD1, PS2 ]) ]),
        Replacement(lambda d: Times([ d["PD1"], Plus([Times([d["PS1"]]), Times([d["PS2"]])]) ]))
    ),
    # A B - A C D -> A (B - C D)
    RewriteRule(
        Plus([ Times([ PD1, PS1 ]), Times([ Minus([PD1]), PD2, PS2 ]) ]),
        Replacement(lambda d: Times([ d["PD1"], Plus([ Times([d["PS1"]]), Times([Minus([d["PD2"]]), Times([d["PS2"]])])]) ]))
    ),
    # B A + C D A -> (B + C D) A
    RewriteRule(
        Plus([ Times([ PS1, PD1 ]), Times([ PS2, PD1 ]) ]),
        Replacement(lambda d: Times([ Plus([ Times([d["PS1"]]), Times([d["PS2"]]) ]), d["PD1"] ]))
    ),
    # B A - C D A -> (B - C D) A
    RewriteRule(
        Plus([ Times([ PS1, PD1 ]), Times([ Minus([PD2]), PS2, PD1 ]) ]),
        Replacement(lambda d: Times([ Plus([ Times([d["PS1"]]), Times([Minus([d["PD2"]]), d["PS2"]])]), d["PD1"] ]))
    )
]
 
