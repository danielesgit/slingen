from core.expression import Symbol, Equal, Plus, Minus, Times, Transpose, Inverse, \
                            Predicate, NList, BlockedExpression, PatternDot, PatternStar
from core.properties import *
from core.InferenceOfProperties import *
from core.functional import replace, replace_all, RewriteRule, Replacement, map_thread
from core.BlockedExpression_utils import flatten_blocked_operation

from CoreExtension import WrapOutBef

def flatten_blocked_operation_click( expr ):
    PD = PatternDot("PD")
    rule = RewriteRule( WrapOutBef( PD ), \
                        Replacement(lambda d: BlockedExpression( map_thread( WrapOutBef, [d["PD"]], 2 ), d["PD"].size, d["PD"].shape)) )
    expr = replace( copy.deepcopy(expr), [rule] )
    return flatten_blocked_operation( expr ) 

def normalize_minus( expr ):
    ld = PatternDot("ld")
    md = PatternDot("md")
    l = PatternStar("l")
    r = PatternStar("r")
    return replace_all( expr, [RewriteRule( Times([ ld, l, Minus([md]), r ]),
                                            Replacement( lambda d: Times([ Minus([d["ld"]]), d["l"], d["md"], d["r"]]) )),
                               RewriteRule( Times([ Minus([Minus([ld])]), l ]),
                                            Replacement( lambda d: Times([ d["ld"], d["l"]]) )),
                               RewriteRule( Minus([ Times([ ld, l ]) ]),
                                            Replacement( lambda d: Times([ Minus([d["ld"]]), d["l"]]) )) ] )

def filter_zero_zero( eqs ):
    return [ eq for eq in eqs if not ( all([ isZero(op) for op in eq.get_children()[0] ]) and isZero( eq.get_children()[1] ) ) ]

def equation2replacement( eq ):
    if isinstance( eq, Symbol ):
        return str(eq)
    if isinstance( eq, Equal ):
        return "Equal([ %s ])" % ( ", ".join([ equation2replacement(ch) for ch in eq.get_children() ]) )
    if isinstance( eq, Plus ):
        return "Plus([ %s ])" % ( ", ".join([ equation2replacement(ch) for ch in eq.get_children() ]) )
    if isinstance( eq, Times ):
        return "Times([ %s ])" % ( ", ".join([ equation2replacement(ch) for ch in eq.get_children() ]) )
    if isinstance( eq, Minus ):
        return "Minus([ %s ])" % ( equation2replacement(eq.get_children()[0]) )
    if isinstance( eq, Transpose ):
        return "Transpose([ %s ])" % ( equation2replacement(eq.get_children()[0]) )
    if isinstance( eq, Inverse ):
        return "Inverse([ %s ])" % ( equation2replacement(eq.get_children()[0]) )
    if isinstance( eq, NList ):
        return "NList([ %s ])" % ( ", ".join([ equation2replacement(ch) for ch in eq.get_children() ]) )
    if isinstance( eq, BlockedExpression ):
        repl = "["
        rows = []
        for row in eq.get_children():
            r = "["
            r += ", ".join([ equation2replacement(expr) for expr in row ])
            r += "]"
            rows.append( r )
        repl += ", ".join( rows )
        repl += "]"
        return "BlockedExpression( %s, %s, %s )" % ( repl, eq.size, eq.shape )
    if isinstance( eq, Predicate ):
        return "Predicate( \"%s\", %s, %s )" % ( 
                eq.name, 
                "[ " + ", ".join([ equation2replacement(ch) for ch in eq.get_children() ]) + " ]",
                "[ " + ", ".join([ 
                                str((equation2replacement(s[0]),
                                     equation2replacement(s[1]))) for s in eq.size ]) + " ]"
                )
    else:
        print( "Error:", eq.__class__ )
        raise TypeError

