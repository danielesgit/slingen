from core.expression import Symbol, Matrix, Vector, \
                            Equal, Plus, Minus, Times, Transpose, \
                            PatternDot, PatternStar
from core.properties import *
from core.InferenceOfProperties import *

from core.functional import Constraint, Replacement, RewriteRule, replace_all

from core.builtin_operands import Zero, Identity

LHS = PatternDot("LHS")
RHS = PatternDot("RHS")
subexpr = PatternDot("subexpr")
PD1 = PatternDot("PD1")
PD2 = PatternDot("PD2")
PS1 = PatternStar("PS1")
PS2 = PatternStar("PS2")
PS3 = PatternStar("PS3")
PSLeft = PatternStar("PSLeft")
PSRight = PatternStar("PSRight")

simplify_rules = [
    # Minus
    # --expr -> expr
    RewriteRule(
        Minus([ Minus([ subexpr ]) ]),
        Replacement(lambda d: d["subexpr"])
    ),
    # -0 -> 0
    RewriteRule(
        (
            Minus([ subexpr ]),
            Constraint(lambda d: isZero(d["subexpr"]))
        ),
        Replacement(lambda d: d["subexpr"])
    ),
    # Plus
    # Plus(a) -> a
    RewriteRule(
        Plus([ subexpr ]),
        Replacement(lambda d: d["subexpr"])
    ),
    # Plus( a___, 0, b___ ) -> Plus( a, b )
    RewriteRule(
        (
            Plus([ PS1, subexpr, PS2 ]),
            Constraint(lambda d: isZero(d["subexpr"]))
        ),
        Replacement(lambda d: Plus([d["PS1"], d["PS2"]]))
    ),
    # a - a -> 0
    RewriteRule(
        Plus([ PS1, subexpr, PS2, Minus([subexpr]), PS3 ]),
        Replacement(lambda d: Plus([d["PS1"], Zero(d["subexpr"].get_size()), d["PS2"], d["PS3"]]))
    ),
    # Times
    # Times(a) -> a
    RewriteRule(
        Times([ subexpr ]),
        Replacement(lambda d: d["subexpr"])
    ),
    # Times( a___, 0, b___ ) -> 0
    RewriteRule(
        (
            Times([ PS1, subexpr, PS2 ]),
            Constraint(lambda d: isZero(d["subexpr"]))
        ),
        Replacement(lambda d: Zero( Times([ d["PS1"], d["subexpr"], d["PS2"] ]).get_size() ))
    ),
    # Times( a___, A, B, b___ ) /; A == Inv(B) -> Times( a, I, b )
    RewriteRule(
        (
            Times([ PS1, PD1, PD2, PS2 ]),
            Constraint(lambda d: to_canonical(Inverse([d["PD1"]])) == d["PD2"])
            #Constraint(lambda d: simplify(to_canonical(Inverse([d["PD1"]]))) == d["PD2"])
        ),
        Replacement(lambda d: Times([ d["PS1"], Identity( d["PD1"].get_size() ), d["PS2"] ]))
    ),
    # cannot simplify, need this one as well
    RewriteRule(
        (
            Times([ PS1, PD1, PD2, PS2 ]),
            Constraint(lambda d: to_canonical(Inverse([d["PD2"]])) == d["PD1"])
        ),
        Replacement(lambda d: Times([ d["PS1"], Identity( d["PD1"].get_size() ), d["PS2"] ]))
    ),
    ## Times( a___, A, Inverse(A), b___ ) -> Times( a, I, b )
    #RewriteRule(
        #Times([ PS1, PD1, Inverse([ PD1 ]), PS2 ]),
        #Replacement("Times([ PS1, Identity(PD1.get_size()), PS2 ])")
    #),
    ## Times( a___, Inverse(A), A, b___ ) -> Times( a, I, b )
    #RewriteRule(
        #Times([ PS1, Inverse([ PD1 ]), PD1, PS2 ]),
        #Replacement("Times([ PS1, Identity( PD1.get_size() ), PS2 ])")
    #),
    # Transpose
    # T(T(expr)) -> expr
    RewriteRule(
        Transpose([ Transpose([ subexpr ]) ]),
        Replacement(lambda d: d["subexpr"])
    ),
    # T(0) -> 0
    RewriteRule(
        (
            Transpose([ subexpr ]),
            Constraint(lambda d: isZero(d["subexpr"]))
        ),
        Replacement(lambda d: Zero(Transpose([d["subexpr"]]).get_size()))
    ),
    # Inverse
    # Inv(Inv(expr)) -> expr
    RewriteRule(
        Inverse([ Inverse([ subexpr ]) ]),
        Replacement(lambda d: d["subexpr"])
    ),
    # Identity
    # A * I (not scalar A) -> A
    RewriteRule(
        (
            Times([ PS1, PD1, PD2, PS2 ]),
            Constraint(lambda d: (d["PD1"].isMatrix() or d["PD1"].isVector()) and isIdentity(d["PD2"]))
        ),
        Replacement(lambda d: Times([ d["PS1"], d["PD1"], d["PS2"] ]))
    ),
    # I * A (not scalar A) -> A
    RewriteRule(
        (
            Times([ PS1, PD2, PD1, PS2 ]),
            Constraint(lambda d: (d["PD1"].isMatrix() or d["PD1"].isVector()) and isIdentity(d["PD2"]))
        ),
        Replacement(lambda d: Times([ d["PS1"], d["PD1"], d["PS2"] ]))
    )
]

#canonical_rules = [
    ## a * ( b + c ) * e -> a*b*e + a*c*e
    #RewriteRule(
        #Times([ PSLeft, Plus([ PS1 ]), PSRight ]),
        #Replacement( "Plus([ Times([ PSLeft, term, PSRight]) for term in PS1 ])" )
    #),
    ## -( a + b) -> (-a)+(-b)
    #RewriteRule(
        #Minus([ Plus([ PS1 ]) ]),
        #Replacement( "Plus([ Minus([term]) for term in PS1 ])" )
    #),
    ## -( a * b) -> (-a) * b
    #RewriteRule(
        #Minus([ Times([ PD1, PS1 ]) ]),
        #Replacement( "Times([ Minus([PD1]), PS1 ])" )
    #),
    ## Transpose( A + B + C ) -> A^T + B^T + C^T
    #RewriteRule(
        #Transpose([ Plus([ PS1 ]) ]),
        #Replacement( "Plus([ Transpose([term]) for term in PS1 ])"),
    #),
    ## Transpose( A * B * C ) -> C^T + B^T + A^T
    #RewriteRule(
        #Transpose([ Times([ PS1 ]) ]),
        #Replacement( "Times([ Transpose([term]) for term in reversed(list(PS1)) ])"),
    #),
    ## Transpose( -A ) -> -(A^T)
    #RewriteRule(
        #Transpose([ Minus([ PD1 ]) ]),
        #Replacement( "Minus([ Transpose([ PD1 ]) ])"),
    #),
    ## Inverse( -A ) -> -(Inverse(A))
    #RewriteRule(
        #Inverse([ Minus([ PD1 ]) ]),
        #Replacement( "Minus([ Inverse([ PD1 ]) ])"),
    #),
    ## Inverse( A^T ) -> (Inverse(A))^T
    #RewriteRule(
        #Inverse([ Transpose([ PD1 ]) ]),
        #Replacement( "Transpose([ Inverse([ PD1 ]) ])"),
    #)
#]

canonicalIO_rules = [
    ## Equal[Minus, Minus] -> remove minuses
    ## add support for head_[_]
    #RewriteRule(
        #(
            #Equal([ Minus([LHS]), Minus([RHS]) ]),
            #Constraint("True")
        #),
        #Replacement("Equal([ LHS, RHS ])")
    #),
    # Input to the right
    # Plus
    RewriteRule(
        (
            Equal([ Plus([PS1, subexpr, PS2]), RHS ]),
            Constraint(lambda d: isInput(d["subexpr"]))
        ),
        Replacement(lambda d: Equal([ Plus([ d["PS1"], d["PS2"] ]), \
                                      Plus([ d["RHS"], Minus([d["subexpr"]])]) ]))
    ),
    # Minus
    RewriteRule(
        (
            Equal([ Minus([subexpr]), RHS ]),
            Constraint(lambda d: isInput(d["subexpr"]))
        ),
        Replacement(lambda d: Equal([ Zero(d["subexpr"].get_size()), \
                                      Plus([d["RHS"], d["subexpr"]]) ]))
    ),
    # Transpose
    RewriteRule(
        (
            Equal([ Transpose([subexpr]), RHS ]),
            Constraint(lambda d: isInput(d["subexpr"]))
        ),
        Replacement(lambda d: Equal([ Zero(d["RHS"].get_size()), \
                                      Plus([d["RHS"], Minus([Transpose([d["subexpr"]])])]) ]))
    ),
    # Any expression
    RewriteRule(
        (
            Equal([ subexpr, RHS ]),
            Constraint(lambda d: isInput(d["subexpr"]))
        ),
        Replacement(lambda d: Equal([ Zero(d["subexpr"].get_size()), \
                                      Plus([d["RHS"], Minus([d["subexpr"]])]) ]))
    ),
    # Non-singular input A \times ... -> to the right as A^-1 ...
    RewriteRule(
        (
            Equal([ Times([ PD1, PS1 ]), RHS ]),
            Constraint(lambda d: isInput(d["PD1"]) and isNonSingular(d["PD1"]))
        ),
        Replacement(lambda d: Equal([ Times([ d["PS1"] ]), \
                                      Times([ Inverse([ d["PD1"] ]), d["RHS"] ]) ]))
    ),
    # X * L = A -> X = A * Inv(L)
    RewriteRule(
        (
            Equal([ Times([ PS1, PD1 ]), RHS ]),
            Constraint(lambda d: isInput(d["PD1"]) and isNonSingular(d["PD1"]))
        ),
        Replacement(lambda d: Equal([ Times([ d["PS1"] ]), \
                                      Times([ d["RHS"], Inverse([ d["PD1"] ]) ]) ]))
    ),
    # Output to the left
    # Plus
    RewriteRule(
        (
            Equal([ LHS, Plus([PS1, subexpr, PS2]) ]),
            Constraint(lambda d: isOutput(d["subexpr"]))
        ),
        Replacement(lambda d: Equal([ Plus([ d["LHS"], Minus([d["subexpr"]])]), \
                                      Plus([ d["PS1"], d["PS2"] ]) ]))
    ),
    # Minus
    RewriteRule(
        (
            Equal([ LHS, Minus([subexpr]) ]),
            Constraint(lambda d: isOutput(d["subexpr"]))
        ),
        Replacement(lambda d: Equal([ Plus([ d["LHS"], d["subexpr"]]), \
                                      Zero( d["LHS"].get_size()) ]))
    )
]

