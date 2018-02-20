from core.properties import *
from core.InferenceOfProperties import *

prop_to_func = {
    INPUT  : isInput,
    OUTPUT : isOutput,
    #
    #SCALAR = isScalar,
    #VECTOR = isVector,
    #MATRIX = isMatrix,
    #
    #SQUARE       : isSquare,
    #
    ZERO : isZero,
    IDENTITY : isIdentity,
    DIAGONAL : isDiagonal,
    #TRIANGULAR : isTriangular,
    LOWER_TRIANGULAR : isLowerTriangular,
    UPPER_TRIANGULAR : isUpperTriangular,
    UNIT_DIAGONAL : isUnitDiagonal,
    IMPLICIT_UNIT_DIAGONAL : isImplicitUnitDiagonal,
    #
    SYMMETRIC : isSymmetric,
    SPD : isSPD,
    #LOWER_STORAGE : isLowerStorage,
    #UPPER_STORAGE : isUpperStorage,
    #
    NON_SINGULAR : isNonSingular,
}

def symbol_props_to_constraints( symbol ):
    props = [ ("%s(%s)" % (query.__name__, symbol.name)) for prop, query in prop_to_func.items() if query(symbol) ]
    return " and ".join( props )

def symbol_props_to_constraints_no_io( symbol ):
    query_no_io = [ query for prop, query in prop_to_func.items() if (query(symbol) and prop not in (INPUT, OUTPUT)) ]
    props = [ ("%s(%s)" % (query.__name__, symbol.name)) for query in query_no_io ]
    return " and ".join( props )


def propagate_properties( inp, out ):
    for prop, f in prop_to_func.items():
        if prop in (INPUT, OUTPUT, TEMPORARY):
            continue
        if f( inp ):
            out.set_property( prop )
