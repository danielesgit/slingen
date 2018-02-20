from core.expression import Symbol, Matrix, Vector, \
                            Equal, Plus, Minus, Times, Transpose, Inverse, \
                            BlockedExpression, Sequence, Predicate, \
                            PatternDot
from core.properties import *
from core.InferenceOfProperties import *
from core.builtin_operands import Zero, Identity

from core.functional import replace_all
from core.rules_collection import simplify_rules, canonicalIO_rules
from core.rules_collection_base import canonical_rules

def to_canonical( expr ):
    return replace_all( expr, canonical_rules )

def to_canonicalIO( expr ):
    return replace_all( expr, canonical_rules+canonicalIO_rules )

def simplify( expr ):
    return replace_all( expr, simplify_rules )

