import copy
import functools

from core.expression import Symbol, Matrix, Vector, Scalar, NumericConstant, \
                            Equal, Plus, Minus, Times, Transpose, Inverse, \
                            BlockedExpression, NList, Predicate, \
                            PatternDot, sZERO
from core.functional import map_thread

def multiply_blocked_expressions( a, b ):
    b_trans = list(zip(*b.get_children()))
    product = \
        [ [ Plus([Times([copy.deepcopy(za), copy.deepcopy(zb)]) for za, zb in zip(rowa, rowb)]) for rowb in b_trans ] for rowa in a ]
    return BlockedExpression( product, (a.get_size()[0], b.get_size()[1]), (a.shape[0], b.shape[1]) )

def flatten_blocked_operation( expr ):
    if isinstance( expr, BlockedExpression ):
        return expr
    if isinstance( expr, Equal ):
        flat_ch = [flatten_blocked_operation( ch ) for ch in expr.get_children()] 
        return BlockedExpression( map_thread( Equal, flat_ch, 2 ), flat_ch[0].size, flat_ch[0].shape )
    if isinstance( expr, Plus ):
        flat_ch = [flatten_blocked_operation( ch ) for ch in expr.get_children()] 
        return BlockedExpression( map_thread( Plus, flat_ch, 2 ), flat_ch[0].size, flat_ch[0].shape )
    # [TODO] will ignore the inner scalar expressions for now
    # Also the plain scalars: I guess it will suffice to check size of blocked == (1,1)
    if isinstance( expr, Times ):
        non_scalar_idx = 0
        while expr.children[non_scalar_idx].isScalar():
            non_scalar_idx += 1
        scalars = [ s.children[0][0] for s in expr.get_children()[:non_scalar_idx] ]
        non_scalars = expr.get_children()[non_scalar_idx:]
        if non_scalars:
            prod = flatten_blocked_operation( copy.deepcopy(non_scalars[0]) )
            for ch in non_scalars[1:]:
                prod = multiply_blocked_expressions( prod, flatten_blocked_operation(ch) )
            prod.children = [ [ Times(scalars + [cell]) for cell in row ] for row in prod.children ]
            return prod
        else:
            return [[ Times(scalars) ]]
        #non_scalar_prod = functools.reduce( 
                #multiply_blocked_expressions, 
                #[flatten_blocked_operation( ch ) for ch in expr.get_children()[non_scalar_idx:]] 
            #)
        #non_scalar_prod.children = [ [ Times(scalars + [cell]) for cell in row ] for row in non_scalar_prod.children ]
        #return non_scalar_prod
    if isinstance( expr, Minus ):
        flat_ch = [flatten_blocked_operation( ch ) for ch in expr.get_children()] 
        return BlockedExpression( map_thread( Minus, flat_ch, 2 ), flat_ch[0].size, flat_ch[0].shape )
    if isinstance( expr, Transpose ):
        flat_ch = [flatten_blocked_operation( ch ) for ch in expr.get_children()]
        new = BlockedExpression( map_thread( Transpose, flat_ch, 2 ), flat_ch[0].size, flat_ch[0].shape )
        new.transpose()
        return new
    if isinstance( expr, Inverse ): # [TODO] Only triangular
        flat_ch = [flatten_blocked_operation( ch ) for ch in expr.get_children()]
        if len( flat_ch[0].get_children() ) == 1: # 1x1 inverse
            return BlockedExpression( map_thread( Inverse, flat_ch, 2 ), flat_ch[0].size, flat_ch[0].shape )
        if len( flat_ch[0].get_children() ) == 2: # 2x2 inverse
            children = flat_ch[0].get_children()
            TL = children[0][0]
            TR = children[0][1]
            BL = children[1][0]
            BR = children[1][1]
            return BlockedExpression( [[ Inverse([ TL ]), 
                                         Times([ Minus([ Inverse([ TL ]) ]), TR, Inverse([ BR ]) ]) ], 
                                       [ Times([ Minus([ Inverse([ BR ]) ]), BL, Inverse([ TL ]) ]), 
                                         Inverse([children[1][1]]) ]], flat_ch[0].size, flat_ch[0].shape )

