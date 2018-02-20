import copy

from core.expression import Symbol, Matrix, \
                            Equal, Plus, Minus, Times, Transpose, Inverse, \
                            BlockedExpression, Sequence, Predicate, \
                            PatternDot
from core.builtin_operands import Zero
from core.functional import replace, replace_all, RewriteRule, Replacement, Constraint

from core.rules_collection_base import canonical_rules, \
                                       simplify_rules_base

import core.properties as properties
from core.TOS import _TOE as TOE

def to_canonical( expr ):
    return replace_all( expr, canonical_rules+simplify_rules_base )

# 
# An expression is an input expression if:
#   - is an input symbol.
#   - a sum or product of input expressions.
#   - the transpose of an input expression.
#   - the inverse of an input expression.
#   - is an operation like trsm, ...
#
# [TODO] node.isInput -> only when changing a property
#                        will trigger re-inference up the tree
def isInput( node ):
    # isinstance?
    #if node.isInput():
    if isinstance( node, Symbol ) and node.isInput():
        return True
    if isinstance( node, Plus ):
        return all( [ isInput(term) for term in node.get_children() ] )
    if isinstance( node, Times ):
        return all( [ isInput(factor) for factor in node.get_children() ] )
    if isinstance( node, Minus ):
        return isInput(node.get_children()[0])
    if isinstance( node, Transpose ):
        return isInput(node.get_children()[0])
    if isinstance( node, Inverse ):
        return isInput(node.get_children()[0])
    # [TODO] Double check!!!
    if isinstance( node, Predicate ) and node.isInput():
        return True
    return False

# 
# An expression is an input expression if:
#   - is an output symbol.
#   - a sum or product where at least one output expression appears.
#   - the transpose of an output expression.
#   - the inverse of an output expression.
#
# [TODO] node.isOutput -> only when changing a property
#                        will trigger re-inference up the tree
def isOutput( node ):
    # isinstance?
    #if node.isOutput():
    if isinstance( node, Symbol ) and node.isOutput():
        return True
    if isinstance( node, Plus ):
        return any( [ isOutput(term) for term in node.get_children() ] )
    if isinstance( node, Times ):
        return any( [ isOutput(factor) for factor in node.get_children() ] )
    if isinstance( node, Minus ):
        return isOutput(node.get_children()[0])
    if isinstance( node, Transpose ):
        return isOutput(node.get_children()[0])
    if isinstance( node, Inverse ):
        return isOutput(node.get_children()[0])
    return False

def isZero( node ):
    return node.isZero()

def isIdentity( node ):
    if node.isIdentity():
        return True
    if isinstance( node, Plus ):
        return False
    if isinstance( node, Times ):
        return all( [ isIdentity(factor) for factor in node.get_children() ] )
    if isinstance( node, Minus ):
        return False
    if isinstance( node, Transpose ):
        return isIdentity(node.get_children()[0])
    if isinstance( node, Inverse ):
        return isIdentity(node.get_children()[0])
    #if isinstance( node, Operand ):
        #if node.type == "Scalar": ONE!
            #return True
    return False

def isDiagonal( node ):
    # isinstance?
    if node.isDiagonal():
        return True
    if isinstance( node, Plus ):
        return all( [ isDiagonal(term) for term in node.get_children() ] )
    if isinstance( node, Times ):
        return all( [ isDiagonal(factor) for factor in node.get_children() ] )
    if isinstance( node, Minus ):
        return isDiagonal(node.get_children()[0])
    if isinstance( node, Transpose ):
        return isDiagonal(node.get_children()[0])
    if isinstance( node, Inverse ):
        return isDiagonal(node.get_children()[0])
    #if isinstance( node, Operand ): # Should be inferred once at the beginning and enter the first "if"
        if node.type == "Scalar":
            return True
    return False

def isTriangular( node ):
    return isLowerTriangular( node ) or isUpperTriangular( node )

def isLowerTriangular( node ):
    # isinstance?
    if node.isLowerTriangular():
        return True
    if isinstance( node, Plus ):
        return all( [ isLowerTriangular(term) for term in node.get_children() ] )
    if isinstance( node, Times ):
        return all( [ isLowerTriangular(factor) for factor in node.get_children() ] )
    if isinstance( node, Minus ):
        return isLowerTriangular(node.get_children()[0])
    if isinstance( node, Transpose ):
        return isUpperTriangular(node.get_children()[0])
    if isinstance( node, Inverse ):
        return isLowerTriangular(node.get_children()[0])
    #if isinstance( node, Operand ):
        #if node.type == "Scalar":
            #return True
    return False

def isUpperTriangular( node ):
    # isinstance?
    if node.isUpperTriangular():
        return True
    if isinstance( node, Plus ):
        return all( [ isUpperTriangular(term) for term in node.get_children() ] )
    if isinstance( node, Times ):
        return all( [ isUpperTriangular(factor) for factor in node.get_children() ] )
    if isinstance( node, Minus ):
        return isUpperTriangular(node.get_children()[0])
    if isinstance( node, Transpose ):
        return isLowerTriangular(node.get_children()[0])
    if isinstance( node, Inverse ):
        return isUpperTriangular(node.get_children()[0])
    #if isinstance( node, Operand ):
        #if node.type == "Scalar":
            #return True
    return False

def isUnitDiagonal( node ):
    # isinstance?
    if node.isUnitDiagonal():
        return True
    if isinstance( node, Plus ):
        return False
    if isinstance( node, Times ): # Should check triangular as well?
        return all( [ isUnitDiagonal(factor) for factor in node.get_children() ] )
    if isinstance( node, Minus ):
        return False
    if isinstance( node, Transpose ):
        return isUnitDiagonal(node.get_children()[0])
    if isinstance( node, Inverse ): # triangular?
        return isUnitDiagonal(node.get_children()[0])
    #if isinstance( node, Operand ):
        #if node.type == "Scalar": ONE!
            #return True
    return False

def isImplicitUnitDiagonal( node ):
    if node.isImplicitUnitDiagonal():
        return True
    return False

def isSymmetric( node ):
    # isinstance?
    if node.isSymmetric():
        return True
    # node == trans( node )
    alt1 = copy.deepcopy( node )
    alt1 = to_canonical(alt1)._cleanup()
    alt2 = copy.deepcopy( node )
    alt2 = to_canonical(Transpose([alt2]))._cleanup()
    if alt1 == alt2:
        return True
    # more ...
    if isinstance( node, Plus ):
        return all( [ isSymmetric(term) for term in node.get_children() ] )
    if isinstance( node, Times ): # iif they commute ...
        return False
    if isinstance( node, Minus ):
        return isSymmetric(node.get_children()[0])
    if isinstance( node, Transpose ):
        return isSymmetric(node.get_children()[0])
    if isinstance( node, Inverse ):
        return isSymmetric(node.get_children()[0])
    #if isinstance( node, Operand ):
        #if node.type == "Scalar":
            #return True
    return False

def isSPD( node ):
    # isinstance?
    if node.isSPD():
        return True
    if TOE.get_property( properties.SPD, node ):
        return True
    if isinstance( node, Plus ): # ?
        #return reduce( lambda x,y: x and y, [ isSPD(term) for term in node.get_children() ], True )
        return False
    if isinstance( node, Times ): # related to "iif they commute" ... ?
        return False
    if isinstance( node, Minus ):
        return False
    if isinstance( node, Transpose ):
        return isSPD(node.get_children()[0])
    if isinstance( node, Inverse ):
        return isSPD(node.get_children()[0])
    #if isinstance( node, Operand ):
        #if node.type == "Scalar": > 0 !
            #return True
    return False

def isNonSingular( node ):
    # isinstance?
    if node.isNonSingular():
        return True
    if isinstance( node, Plus ): # ?
        return False
    if isinstance( node, Times ): # related to "iif they commute" ... ?
        return all( [ isNonSingular(factor) for factor in node.get_children() ] )
    if isinstance( node, Minus ):
        return isNonSingular(node.get_children()[0])
    if isinstance( node, Transpose ):
        return isNonSingular(node.get_children()[0])
    if isinstance( node, Inverse ):
        return isNonSingular(node.get_children()[0])
    #if isinstance( node, Operand ):
        #if node.type == "Scalar": != 0 !
            #return True
    return False
