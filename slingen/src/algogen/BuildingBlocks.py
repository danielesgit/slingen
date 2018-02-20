import copy

from core.expression import Equal, Plus, Times, Minus, Transpose, Inverse, \
                            Symbol, PatternDot, PatternStar, NList, Predicate
from core.functional import Constraint, Replacement, RewriteRule, match, replace
import core.properties as properties
from core.InferenceOfProperties import isUpperTriangular
from core.prop_to_queryfunc import propagate_properties

from CoreExtension import isOperand
import storage

import core.TOS as TOS

alpha = PatternDot( "alpha" )
beta = PatternDot( "beta" )
A = PatternDot( "A" )
B = PatternDot( "B" )
C = PatternDot( "C" )
D_PS = PatternStar( "D_PS")
left = PatternStar( "left" )
middle = PatternStar( "middle" )
right = PatternStar( "right" )


class Instruction( object ):
    def __init__( self, pattern, create_rewrite_rule, create_tile ):
        self.pattern = pattern
        self.create_rewrite_rule = create_rewrite_rule
        self.create_tile = create_tile

    def match( self, expr ):
        yield from match( expr, self.pattern )

    def tile( self, tree, node, match_dict ):
        _T = TOS.new_temp()
        temp = Symbol("T" + str(_T))
        temp.set_property( properties.TEMPORARY )
        #
        if isinstance( node, Predicate ):
            if node == tree:
                print( "[Warning] If predicate has multiple outputs, may break if not careful from caller" )
            return Equal([ NList([ temp ]), copy.deepcopy( node ) ]), \
                    replace( tree, [RewriteRule( copy.deepcopy( node ), Replacement(temp) )] )
        else:
            tile_expr = self.create_tile( match_dict )
            propagate_properties( tile_expr, temp )
            propagate_st_info( tile_expr, temp )
            ## [FIXME] Quick and dirty test
            #if isUpperTriangular( tile_expr ):
                #print( temp, "is upper triangular" )
                #temp.set_property( properties.UPPER_TRIANGULAR )
            return Equal([ NList([ temp ]), self.create_tile( match_dict ) ]), \
                    replace( tree, [self.create_rewrite_rule( match_dict, temp )] )

    def __repr__( self ):
        return str(self.pattern)

def propagate_st_info( inp, out ):
    out.st_info = (storage.ST_FULL, out) # default
    if out.isLowerTriangular():
        out.st_info = (storage.ST_LOWER, out)
    elif out.isUpperTriangular():
        out.st_info = (storage.ST_UPPER, out)
    elif out.isSymmetric():
        symm_ops = [ ch for ch in inp.children if ch.isSymmetric() and isinstance( ch, Symbol ) ]
        if symm_ops:
            print( "Propagating st info from:", symm_ops )
            out.st_info = (symm_ops[0].st_info[0], out )
        else:
            pass
            # [FIXME] Default?


# [TODO] Complete
instruction_set = [
    # Basic Ops - Completeness of the instruction set
    #
    [
        # Inverse
        Instruction(
            ( Inverse([ A ]), Constraint("isOperand(A)") ),
            lambda d, t: \
                    RewriteRule(
                        Inverse([ d["A"] ]),
                        Replacement( "%s" % t )
                    ),
            lambda d: Inverse([ d["A"] ])
        ),
        # Transpose
        Instruction(
            ( Transpose([ A ]), Constraint("isOperand(A)") ),
            lambda d, t: \
                    RewriteRule(
                        Transpose([ d["A"] ]),
                        Replacement( "%s" % t )
                    ),
            lambda d: Transpose([ d["A"] ])
        ),
        # Minus
        #( Minus([ A ]), Constraint("isOperand(A, Symbol)") ),
        Instruction(
            ( Minus([ A ]), Constraint("isOperand(A)") ),
            lambda d, t: \
                    RewriteRule(
                        Minus([ d["A"] ]),
                        Replacement( "%s" % t )
                    ),
            lambda d: Minus([ d["A"] ])
        ),
        # Times
        ( Times([ left, A, B, right ]), Constraint("isOperand(A) and isOperand(B)") ),
        # Plus
        ( Plus([ left, A, B, right ]), Constraint("isOperand(A) and isOperand(B)") )
    ],
    #
    # Optimizations
    #
    # A B
    [
        Instruction(
            ( Times([ left, A, B, right ]), Constraint("isOperand(A) and isOperand(B)") ),
            lambda d, t: \
                    RewriteRule(
                        Times([ left, d["A"], d["B"], right ]),
                        Replacement( "Times([ left, %s, right ])" % t )
                    ),
            lambda d: Times([ d["A"], d["B"] ])
        ),
    # A' B
        #Instruction(
            #( Times([ left, Transpose([A]), B, right ]), Constraint("isOperand(A) and isOperand(B)") ),
            #lambda d, t: \
                    #RewriteRule(
                        #Times([ left, Transpose([d["A"]]), d["B"], right ]),
                        #Replacement( "Times([ left, %s, right ])" % t )
                    #),
            #lambda d: Times([ d["A"], d["B"] ])
        #),
    ],
    [
        # TRSM
        # A \ B
        Instruction(
            ( Times([ left, Inverse([ A ]), B, right ]), 
              Constraint("isOperand(A) and isOperand(B)") ),
            lambda d, t: \
                    RewriteRule(
                        Times([ left, Inverse([ d["A"] ]), d["B"], right ]), 
                        Replacement( "Times([ left, %s, right ])" % t )
                    ),
            lambda d: Times([ Inverse([ d["A"] ]), d["B"] ])
        ),
        # A' \ B
        Instruction(
            ( Times([ left, Transpose([ Inverse([ A ]) ]), B, right ]), 
              Constraint("isOperand(A) and isOperand(B)") ),
            lambda d, t: \
                    RewriteRule(
                        Times([ left, Transpose([ Inverse([ d["A"] ]) ]), d["B"], right ]), 
                        Replacement( "Times([ left, %s, right ])" % t )
                    ),
            lambda d: Times([ Transpose([ Inverse([ d["A"] ]) ]), d["B"] ])
        ),
        # - A \ B
        Instruction(
            ( Times([ Minus([ Inverse([ A ]) ]), B, right ]), Constraint("isOperand(A) and isOperand(B)") ),
            lambda d, t: \
                    RewriteRule(
                        Times([ Minus([ Inverse([ d["A"] ]) ]), d["B"], right ]), 
                        Replacement( "Times([ %s, right ])" % t )
                    ),
            lambda d: Times([ Minus([ Inverse([ d["A"] ]) ]), d["B"] ])
        ),
        # B / A
        Instruction(
            ( Times([ left, B, Inverse([ A ]), right ]), Constraint("isOperand(A) and isOperand(B)") ),
            lambda d, t: \
                    RewriteRule(
                        Times([ left, d["B"], Inverse([ d["A"] ]), right ]), 
                        Replacement( "Times([ left, %s, right ])" % t )
                    ),
            lambda d: Times([ d["B"], Inverse([ d["A"] ]) ])
        ),
        # B / A'
        Instruction(
            ( Times([ left, B, Transpose([ Inverse([ A ]) ]), right ]), Constraint("isOperand(A) and isOperand(B)") ),
            lambda d, t: \
                    RewriteRule(
                        Times([ left, d["B"], Transpose([ Inverse([ d["A"] ]) ]), right ]), 
                        Replacement( "Times([ left, %s, right ])" % t )
                    ),
            lambda d: Times([ d["B"], Transpose([ Inverse([ d["A"] ]) ]) ])
        ),
        # GEMM
        #
        # alpha A B
        Instruction(
            ( Times([ left, alpha, A, B, right ]), Constraint("isOperand(alpha) and isOperand(A) and isOperand(B)") ),
            lambda d, t: \
                    RewriteRule(
                        Times([ left, d["alpha"], d["A"], d["B"], right ]),
                        Replacement( "Times([ left, %s, right ])" % t )
                    ),
            lambda d: Times([ d["alpha"], d["A"], d["B"] ])
        ),
        # - AB
        Instruction(
            ( Times([ Minus([A]), B, right ]), Constraint("isOperand(A) and isOperand(B)") ),
            lambda d, t: \
                    RewriteRule(
                        Times([ Minus([d["A"]]), d["B"], right ]),
                        Replacement( "Times([ %s, right ])" % t )
                    ),
            lambda d: Times([ Minus([d["A"]]), d["B"] ])
        ),
    ],
    [
        # alpha A B + beta C
        Instruction(
            ( Plus([ Times([ alpha, A, B ]), Times([ beta, C ]), right ]), \
                     Constraint("isOperand(alpha) and isOperand(A) and isOperand(B) and isOperand(beta) and isOperand(C)") ),
            lambda d, t: \
                    RewriteRule(
                        Plus([ Times([ d["alpha"], d["A"], d["B"] ]), Times([ d["beta"], d["C"] ]), right ]),
                        Replacement( "Plus([ %s, right ])" % t )
                    ),
            lambda d: Plus([ Times([ d["alpha"], d["A"], d["B"] ]), Times([ d["beta"], d["C"] ]) ])
        ),
        # alpha A' B + beta C
        Instruction(
            ( Plus([ Times([ alpha, Transpose([A]), B ]), Times([ beta, C ]), right ]), \
                     Constraint("isOperand(alpha) and isOperand(A) and isOperand(B) and isOperand(beta) and isOperand(C)") ),
            lambda d, t: \
                    RewriteRule(
                        Plus([ Times([ d["alpha"], Transpose([d["A"]]), d["B"] ]), Times([ d["beta"], d["C"] ]), right ]),
                        Replacement( "Plus([ %s, right ])" % t )
                    ),
            lambda d: Plus([ Times([ d["alpha"], Transpose([d["A"]]), d["B"] ]), Times([ d["beta"], d["C"] ]) ])
        ),
        # alpha A B' + beta C
        Instruction(
            ( Plus([ Times([ alpha, A, Transpose([B]) ]), Times([ beta, C ]), right ]), \
                     Constraint("isOperand(alpha) and isOperand(A) and isOperand(B) and isOperand(beta) and isOperand(C)") ),
            lambda d, t: \
                    RewriteRule(
                        Plus([ Times([ d["alpha"], d["A"], Transpose([d["B"]]) ]), Times([ d["beta"], d["C"] ]), right ]),
                        Replacement( "Plus([ %s, right ])" % t )
                    ),
            lambda d: Plus([ Times([ d["alpha"], d["A"], Transpose([d["B"]]) ]), Times([ d["beta"], d["C"] ]) ])
        ),
        # alpha A B + C
        Instruction(
            ( Plus([ Times([ alpha, A, B ]), C, right ]), \
                     Constraint("isOperand(alpha) and isOperand(A) and isOperand(B) and isOperand(C)") ),
            lambda d, t: \
                    RewriteRule(
                        Plus([ Times([ d["alpha"], d["A"], d["B"] ]), d["C"], right ]),
                        Replacement( "Plus([ %s, right ])" % t )
                    ),
            lambda d: Plus([ Times([ d["alpha"], d["A"], d["B"] ]), d["C"] ])
        ),
        # alpha A' B + C
        Instruction(
            ( Plus([ Times([ alpha, Transpose([A]), B ]), C, right ]), \
                     Constraint("isOperand(alpha) and isOperand(A) and isOperand(B) and isOperand(C)") ),
            lambda d, t: \
                    RewriteRule(
                        Plus([ Times([ d["alpha"], Transpose([d["A"]]), d["B"] ]), d["C"], right ]),
                        Replacement( "Plus([ %s, right ])" % t )
                    ),
            lambda d: Plus([ Times([ d["alpha"], Transpose([d["A"]]), d["B"] ]), d["C"] ])
        ),
        # alpha A B' + C
        Instruction(
            ( Plus([ Times([ alpha, A, Transpose([B]) ]), C, right ]), \
                     Constraint("isOperand(alpha) and isOperand(A) and isOperand(B) and isOperand(C)") ),
            lambda d, t: \
                    RewriteRule(
                        Plus([ Times([ d["alpha"], d["A"], Transpose([d["B"]]) ]), d["C"], right ]),
                        Replacement( "Plus([ %s, right ])" % t )
                    ),
            lambda d: Plus([ Times([ d["alpha"], d["A"], Transpose([d["B"]]) ]), d["C"] ])
        ),
        # A B + C
        Instruction(
            ( Plus([ Times([ A, B ]), C, right ]), Constraint("isOperand(A) and isOperand(B) and isOperand(C)") ),
            lambda d, t: \
                    RewriteRule(
                        Plus([ Times([ d["A"], d["B"] ]), d["C"], right ]),
                        Replacement( "Plus([ %s, right ])" % t )
                    ),
            lambda d: Plus([ Times([ d["A"], d["B"] ]), d["C"] ])
        ),
        # - A B + C
        Instruction(
            ( Plus([ Times([ Minus([A]), B ]), C, right ]), Constraint("isOperand(A) and isOperand(B) and isOperand(C)") ),
            lambda d, t: \
                    RewriteRule(
                        Plus([ Times([ Minus([d["A"]]), d["B"] ]), d["C"], right ]),
                        Replacement( "Plus([ %s, right ])" % t )
                    ),
            lambda d: Plus([ Times([ Minus([d["A"]]), d["B"] ]), d["C"] ])
        ),
        # - A B' + C
        Instruction(
            ( Plus([ Times([ Minus([A]), Transpose([ B ]) ]), C, right ]), Constraint("isOperand(A) and isOperand(B) and isOperand(C)") ),
            lambda d, t: \
                    RewriteRule(
                        Plus([ Times([ Minus([d["A"]]), Transpose([ d["B"] ]) ]), d["C"], right ]),
                        Replacement( "Plus([ %s, right ])" % t )
                    ),
            lambda d: Plus([ Times([ Minus([d["A"]]), Transpose([ d["B"] ]) ]), d["C"] ])
        ),
        # - A' B + C
        Instruction(
            ( Plus([ Times([ Minus([ Transpose([ A ]) ]), B ]), C, right ]), 
              Constraint("isOperand(A) and isOperand(B) and isOperand(C)") ),
            lambda d, t: \
                    RewriteRule(
                        Plus([ Times([ Minus([ Transpose([ d["A"]]) ]), d["B"] ]), d["C"], right ]),
                        Replacement( "Plus([ %s, right ])" % t )
                    ),
            lambda d: Plus([ Times([ Minus([Transpose([d["A"]])]), d["B"] ]), d["C"] ])
        ),
        # A' B + C
        Instruction(
            ( Plus([ Times([ Transpose([ A ]), B ]), C, right ]), 
              Constraint("isOperand(A) and isOperand(B) and isOperand(C)") ),
            lambda d, t: \
                    RewriteRule(
                        Plus([ Times([ Transpose([ d["A"]]), d["B"] ]), d["C"], right ]),
                        Replacement( "Plus([ %s, right ])" % t )
                    ),
            lambda d: Plus([ Times([ Transpose([d["A"]]), d["B"] ]), d["C"] ])
        )
    ],
    [
        # SYR2K
        # 
        # alpha A B' + alpha B A' + beta C
        Instruction(
            ( Plus([ Times([ alpha, A, Transpose([ B ]) ]), 
                     Times([ alpha, B, Transpose([ A ]) ]),
                     Times([ beta, C ]), right ]), 
                     Constraint("isOperand(alpha) and isOperand(A) and isOperand(B) and isOperand(beta) and isOperand(C)") ),
            lambda d, t: \
                    RewriteRule(
                        Plus([ Times([ d["alpha"], d["A"], Transpose([ d["B"] ]) ]), 
                               Times([ d["alpha"], d["B"], Transpose([ d["A"] ]) ]), 
                               Times([ d["beta"], d["C"] ]), right ]),
                        Replacement( "Plus([ %s, right ])" % t )
                    ),
            lambda d: Plus([ Times([ d["alpha"], d["A"], Transpose([ d["B"] ]) ]), 
                             Times([ d["alpha"], d["B"], Transpose([ d["A"] ]) ]), 
                             Times([ d["beta"], d["C"] ]) ])
        ),
        # - A B' - B A' + C
        Instruction(
            ( Plus([ Times([ Minus([A]), Transpose([ B ]) ]), 
                     Times([ Minus([B]), Transpose([ A ]) ]), C, right ]), Constraint("isOperand(A) and isOperand(B) and isOperand(C)") ),
            lambda d, t: \
                    RewriteRule(
                        Plus([ Times([ Minus([ d["A"] ]), Transpose([ d["B"] ]) ]), 
                               Times([ Minus([ d["B"] ]), Transpose([ d["A"] ]) ]), d["C"], right ]),
                        Replacement( "Plus([ %s, right ])" % t )
                    ),
            lambda d: Plus([ Times([ Minus([ d["A"] ]), Transpose([ d["B"] ]) ]), 
                             Times([ Minus([ d["B"] ]), Transpose([ d["A"] ]) ]), d["C"] ])
        ),
    ],
    # Predicates
    [
        Instruction(
            ( A, Constraint("isinstance(A, Predicate) and all([ isOperand(ch) for ch in A.get_children() ])") ),
            None, None
        )
    ]
]
