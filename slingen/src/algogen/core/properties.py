INPUT  = "Input"
OUTPUT = "Output"
TEMPORARY = "Temporary"
#
SCALAR = "Scalar"
VECTOR = "Vector"
MATRIX = "Matrix"
#
SQUARE       = "Square"
#
ZERO = "Zero"
IDENTITY = "Identity"
DIAGONAL = "Diagonal"
TRIANGULAR = "Triangular"
LOWER_TRIANGULAR = "LowerTriangular"
UPPER_TRIANGULAR = "UpperTriangular"
UNIT_DIAGONAL = "UnitDiagonal"
IMPLICIT_UNIT_DIAGONAL = "ImplicitUnitDiagonal"
#
SYMMETRIC = "Symmetric"
SPD = "SPD"
LOWER_STORAGE = "LowerStorage"
UPPER_STORAGE = "UpperStorage"
#
NON_SINGULAR = "Non-singular"

TOE_properties = [
    ZERO,
    IDENTITY,
    DIAGONAL,
    TRIANGULAR,
    LOWER_TRIANGULAR,
    UPPER_TRIANGULAR,
    UNIT_DIAGONAL,
    IMPLICIT_UNIT_DIAGONAL,
    #
    SYMMETRIC,
    SPD,
    LOWER_STORAGE,
    UPPER_STORAGE,
    #
    NON_SINGULAR
]

# Add dictionary implies (prop) -> props
#   e.g., SPD -> Symmetric
#         Diagonal -> Triangular
