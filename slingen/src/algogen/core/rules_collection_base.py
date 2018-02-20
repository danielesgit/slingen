from core.expression import Symbol, Matrix, \
                            Equal, Plus, Minus, Times, Transpose, Inverse, \
                            PatternDot, PatternStar

from core.functional import Constraint, Replacement, RewriteRule, replace_all
#from core.builtin_operands import Zero

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

# TODO: where do we place A*inv(A) -> I?

canonical_rules = [
    # a * ( b + c ) * e -> a*b*e + a*c*e
    RewriteRule(
        Times([ PSLeft, Plus([ PS1 ]), PSRight ]),
        Replacement( lambda d: Plus([ Times([ d["PSLeft"], term, d["PSRight"]]) for term in d["PS1"] ]) )
    ),
    # -( a + b) -> (-a)+(-b)
    RewriteRule(
        Minus([ Plus([ PS1 ]) ]),
        Replacement( lambda d: Plus([ Minus([term]) for term in d["PS1"] ]) )
    ),
    # -( a * b) -> (-a) * b
    RewriteRule(
        Minus([ Times([ PD1, PS1 ]) ]),
        Replacement( lambda d: Times([ Minus([ d["PD1"] ]), d["PS1"] ]) )
    ),
    # a * b * (-c) -> (-a) * b * c
    RewriteRule(
        Times([ PD1, PS1, Minus([ PD2 ]), PS2 ]),
        Replacement( lambda d: Times([ Minus([ d["PD1"] ]), d["PS1"], d["PD2"], d["PS2"] ]) )
    ),
    # Transpose( A + B + C ) -> A^T + B^T + C^T
    RewriteRule(
        Transpose([ Plus([ PS1 ]) ]),
        Replacement( lambda d: Plus([ Transpose([term]) for term in d["PS1"] ])),
    ),
    # Transpose( A * B * C ) -> C^T + B^T + A^T
    RewriteRule(
        Transpose([ Times([ PS1 ]) ]),
        Replacement( lambda d: Times([ Transpose([term]) for term in reversed(list(d["PS1"])) ]) ),
    ),
    # Transpose( -A ) -> -(A^T)
    RewriteRule(
        Transpose([ Minus([ PD1 ]) ]),
        Replacement( lambda d: Minus([ Transpose([ d["PD1"] ]) ]) ),
    ),
    # Inverse( -A ) -> -(Inverse(A))
    RewriteRule(
        Inverse([ Minus([ PD1 ]) ]),
        Replacement( lambda d: Minus([ Inverse([ d["PD1"] ]) ]) ),
    ),
    # Inverse( A^T ) -> (Inverse(A))^T
    RewriteRule(
        Inverse([ Transpose([ PD1 ]) ]),
        Replacement( lambda d: Transpose([ Inverse([ d["PD1"] ]) ]) ),
    ),
    # Inverse( A * B * C ) -> inv(C) + inv(B) + inv(A)
    RewriteRule(
        Inverse([ Times([ PS1 ]) ]),
        Replacement( lambda d: Times([ Inverse([term]) for term in reversed(list(d["PS1"])) ]) ),
    )
]

simplify_rules_base = [
    # Transpose
    # T(T(expr)) -> expr
    RewriteRule(
        Transpose([ Transpose([ subexpr ]) ]),
        Replacement( lambda d: d["subexpr"] )
    ),
    RewriteRule(
        (
            Transpose([ subexpr ]),
            Constraint(lambda d: isinstance(d["subexpr"], Symbol) and d["subexpr"].isSymmetric())
        ),
        Replacement(lambda d: d["subexpr"])
    )
]
