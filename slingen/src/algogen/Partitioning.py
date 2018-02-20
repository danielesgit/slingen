import itertools

from core.expression import Symbol, BlockedExpression, Matrix, Plus, Times, Minus, Transpose, Inverse
import core.properties as properties

from core.TOS import _TOE as TOE
import storage

def partition( operand, shape, properties ):
    part = partition_shape( operand, shape )
    for prop in properties:
        inherit_properties( operand, part, shape, prop, tri=operand.isTriangular() ) # needed for non-singular
    # storage
    other_part = partition_shape( operand.st_info[1], shape )
    inherit_storage( operand, part, other_part )
    return part

def partition_shape_with_storage( operand, shape ):
    part = partition_shape( operand, shape )
    # storage
    other_part = partition_shape( operand.st_info[1], shape )
    inherit_storage( operand, part, other_part )
    return part


def repartition( operand, initial_part, trav ):
    map_part_repart = {
                        (1, 1): (1, 1),
                        (1, 2): (1, 3),
                        (2, 1): (3, 1),
                        (2, 2): (3, 3)
                      }
    shape = map_part_repart[ initial_part ]
    properties = operand.get_properties()

    repart = repartition_shape( operand, shape )
    for prop in properties:
        inherit_properties( operand, repart, shape, prop, tri=operand.isTriangular() ) # needed for non-singular
    # storage
    other_repart = repartition_shape( operand.st_info[1], shape )
    inherit_storage( operand, repart, other_repart )
    #
    repart = repart_group( repart, shape, trav )
    return repart

def repartition_shape( operand, repart_shape ):
    parts_type = operand.get_head()
    # [TODO] Will ignore the reparts' sizes for now
    size = operand.get_size()
    if repart_shape == (1, 1):
        exts = [[ "" ]]
    elif repart_shape == (1, 3):
        exts = [[  "_0", "_1", "_2" ]]
    elif repart_shape == (3, 1):
        exts = [[ "_0"], 
                [ "_1"], 
                [ "_2"]]
    elif repart_shape == (3, 3):
        exts = [ [ "_00", "_01", "_02"], 
                 [ "_10", "_11", "_12"], 
                 [ "_20", "_21", "_22"] ]
    else:
        raise WrongPartitioningShape

    repart = BlockedExpression(
              [[ parts_type(operand.get_name() + ext, size) 
                  for ext in row_ext ] 
                      for row_ext in exts ], 
              operand.get_size(), repart_shape)
    return repart

def repart_group( repart, shape, traversal ):
    # [TODO] Fix
    m,n = repart[0][0].get_size()
    #
    repart = repart.get_children() # repart is a blocked expression
    if shape == (1, 1):
        grouped = [[ repart ]]
    elif shape == (1, 3):
        [[ A0, A1, A2 ]] = repart
        if traversal == (0, 1): # Left to Right
            grouped = [[  [[A0]], [[A1, A2]]  ]]
        if traversal == (0, -1): # Right to Left
            grouped = [[  [[A0, A1]], [[A2]]  ]]
    elif shape == (3, 1):
        [ [A0], [A1], [A2] ] = repart
        if traversal == (1, 0): # Top to Bottom
            grouped = [[ [[A0]] ],
                       [ [[A1],
                          [A2]] ]]
        if traversal == (-1, 0): # Bottom to Top
            grouped = [[ [[A0],
                          [A1]], ],
                       [ [[A2]] ]]
    elif shape == (3, 3):
        [ [A00, A01, A02], 
          [A10, A11, A12], 
          [A20, A21, A22] ] = repart
        if traversal == (1, 1): # TL to TR
            grouped = [ [ [[A00]], 
                          [[A01, A02]] ],
                        [ [[A10], [A20]], 
                          [[A11, A12], [A21, A22]] ] ]
        elif traversal == (1, -1): # TR to BL
            grouped = [ [ [[A00, A01]], 
                          [[A02]] ],
                        [ [[A10, A11], [A20, A21]], 
                          [[A12], [A22]] ] ]
        elif traversal == (-1, 1): # BL to TR
            matrix = repart
            TL = [ row[ :1] for row in matrix[ :2] ] # col  0   of rows 0-1
            BL = [ row[ :1] for row in matrix[2: ] ] # col  0   of row    2
            TR = [ row[1: ] for row in matrix[ :2] ] # cols 1-2 of rows 0-1
            BR = [ row[1: ] for row in matrix[2: ] ] # cols 1-2 of row    2
            grouped = [ [TL, TR], [BL, BR] ]
        elif traversal == (-1, -1): # BR to TL
            matrix = repart
            TL = [ row[ :2] for row in matrix[ :2] ] # cols 0-1 of rows 0-1
            BL = [ row[ :2] for row in matrix[2: ] ] # cols 0-1 of row    2
            TR = [ row[2: ] for row in matrix[ :2] ] # col    2 of rows 0-1
            BR = [ row[2: ] for row in matrix[2: ] ] # col    2 of row    2
            grouped = [ [TL, TR], [BL, BR] ]

    final_repart = []
    for row in grouped:
        final_repart.append([])
        for cell in row:
            final_repart[-1].append( BlockedExpression( cell, (m,n), (len(cell), len(cell[0])) ) )
    return final_repart

# [TODO] I guess we can beautify the sizes later on
# I will think about it when using them for loopinvs, updates, code generation, etc.
def partition_shape( operand, shape ):
    parts_type = operand.get_head()
    m, n = operand.get_size()
    i, j = Symbol("s"+str(m)), Symbol("s"+str(n))
    #if m == n: # [TODO] better check if they're bound
        #j = i
    if shape == (1, 1):
        exts, sizes = [[""]], [[(m, n)]]
    elif shape == (1, 2):
        exts, sizes = [["_L", "_R"]], [[ (m,j), (m, Plus([n, Minus([j])])) ]]
    elif shape == (2, 1):
        exts, sizes = [["_T"], ["_B"]], [ [(i,n)], [(Plus([m, Minus([i])]), n)] ]
    elif shape == (2, 2):
        exts, sizes = [["_TL", "_TR"], ["_BL", "_BR"]], [ [ (i,j), (i, Plus([n, Minus([j])])) ],
                                                   [ (Plus([m, Minus([i])]), j), (Plus([m, Minus([i])]), Plus([n, Minus([j])])) ] ]
    else:
        print( operand, shape )
        raise WrongPartitioningShape

    part = BlockedExpression(
            [[ parts_type(operand.get_name() + ext, size) 
                for ext, size in zip(row_ext, row_size)] 
                    for row_ext, row_size in zip(exts, sizes)], 
            operand.get_size(), shape)
    # Pointers to fix temporaries in loop invariants
    ch = part.get_children()
    for i, row in enumerate(ch):
        for j, quad in enumerate(row):
            quad.parent_op = operand
            quad.quadrant = (i, j)
    #
    return part

def inherit_properties( operand, part, shape, prop, **kwargs ):
    if prop == properties.INPUT:
        inherit_input( part, shape )
    elif prop == properties.OUTPUT:
        inherit_output( part, shape )
    elif prop == properties.TEMPORARY:
        inherit_temporary( part, shape )
    elif prop == properties.IDENTITY:
        inherit_identity( part, shape )
    elif prop == properties.LOWER_TRIANGULAR:
        inherit_lower_triangular( part, shape )
    elif prop == properties.UPPER_TRIANGULAR:
        inherit_upper_triangular( part, shape )
    elif prop == properties.UNIT_DIAGONAL:
        inherit_unit_diagonal( part, shape )
    elif prop == properties.IMPLICIT_UNIT_DIAGONAL:
        inherit_implicit_unit_diagonal( part, shape )
    elif prop == properties.SYMMETRIC:
        inherit_symmetric( operand, part, shape )
    elif prop == properties.SPD:
        inherit_spd( operand, part, shape )
    elif prop == properties.NON_SINGULAR:
        inherit_non_singular( part, shape, kwargs )
    else:
        print( "\n[WARNING] Inheritance of property %s not implemented!\n" % prop )

def inherit_input( part, shape ):
    if shape in ( (1,1), (1,2), (1,3), (2,1), (3,1), (2,2), (3,3) ):
        for row in part:
            for suboperand in row:
                suboperand.set_property( properties.INPUT )
    else:
        raise WrongPartitioningShape

def inherit_output( part, shape ):
    if shape in ( (1,1), (1,2), (1,3), (2,1), (3,1), (2,2), (3,3) ):
        for row in part:
            for suboperand in row:
                suboperand.set_property( properties.OUTPUT )
    else:
        raise WrongPartitioningShape

def inherit_inout( part, shape ):
    if shape in ( (1,1), (1,2), (1,3), (2,1), (3,1), (2,2), (3,3) ):
        for row in part:
            for suboperand in row:
                suboperand.set_property( properties.INOUT )
    else:
        raise WrongPartitioningShape

def inherit_temporary( part, shape ):
    if shape in ( (1,1), (1,2), (1,3), (2,1), (3,1), (2,2), (3,3) ):
        for row in part:
            for suboperand in row:
                suboperand.set_property( properties.TEMPORARY )
    else:
        raise WrongPartitioningShape

def inherit_identity( part, shape ):
    m, n = shape
    if m == n:
        for row in range(m):
            for col in range(n):
                if row == col: # Diagonal
                    part[row][col].set_property( properties.IDENTITY )
                else: # Off-diagonal
                    part[row][col].set_property( properties.ZERO )
    else:
        raise WrongPartitioningShape

def inherit_lower_triangular( part, shape ):
    m, n = shape
    if m == n:
        for row in range(m):
            for col in range(n):
                if row == col: # Quadrants in the diagonal
                    part[row][col].set_property( properties.LOWER_TRIANGULAR )
                elif row < col: # upper triangle
                    part[row][col].set_property( properties.ZERO )
    else:
        raise WrongPartitioningShape

def inherit_upper_triangular( part, shape ):
    m, n = shape
    if m == n:
        for row in range(m):
            for col in range(n):
                if row == col: # Quadrants in the diagonal
                    part[row][col].set_property( properties.UPPER_TRIANGULAR )
                elif row > col: # Lower triangle
                    part[row][col].set_property( properties.ZERO )
    else:
        raise WrongPartitioningShape

def inherit_unit_diagonal( part, shape ):
    m, n = shape
    if m == n:
        for i in range(m):
            part[i][i].set_property( properties.UNIT_DIAGONAL )
    else:
        raise WrongPartitioningShape

def inherit_implicit_unit_diagonal( part, shape ):
    m, n = shape
    if m == n:
        for i in range(m):
            part[i][i].set_property( properties.IMPLICIT_UNIT_DIAGONAL )
    else:
        raise WrongPartitioningShape

def inherit_symmetric( operand, part, shape ):
    m, n = shape
    st = operand.st_info[0]
    if m == n:
        for row in range(m):
            for col in range(row, n):
                if row == col: # Diagonal
                    part[row][col].set_property( properties.SYMMETRIC )
                else: # Off-diagonal
                    if st == storage.ST_LOWER:
                        part[row][col] = Transpose([ part[col][row] ])
                    else:
                        part[col][row] = Transpose([ part[row][col] ])
    else:
        raise WrongPartitioningShape

def inherit_spd( operand, part, shape ):
    m, n = shape
    if m == n:
        for i in range(m):
            part[i][i].set_property( properties.SPD )
        if shape == (2,2): # For 3,3 repart not really needed
            # Schur complements of A_TL and A_BR are also SPD
            TL, TR, BL, BR = part.flatten_children()
            if operand.st_info[0] == storage.ST_LOWER:
                TOE.set_property( properties.SPD, Plus([ TL, Times([ Minus([ Transpose([ BL ]) ]), Inverse([ BR ]), BL ]) ]) )
                TOE.set_property( properties.SPD, Plus([ BR, Times([ Minus([ BL ]), Inverse([ TL ]), Transpose([ BL ]) ]) ]) )
            else:
                TOE.set_property( properties.SPD, Plus([ TL, Times([ Minus([ TR ]), Inverse([ BR ]), Transpose([ TR ]) ]) ]) )
                TOE.set_property( properties.SPD, Plus([ BR, Times([ Minus([ Transpose([ TR ]) ]), Inverse([ TL ]), TR ]) ]) )
    else:
        raise WrongPartitioningShape

def inherit_non_singular( part, shape, tri ):
    m, n = shape
    if m == n:
        if shape == (1,1):
            part[0][0].set_property( properties.NON_SINGULAR )
        elif tri: # square part > 1 and triangular
            for i in range(m):
                part[i][i].set_property( properties.NON_SINGULAR )
    else:
        raise WrongPartitioningShape

def inherit_storage( operand, this_part, other_part ):
    st, other_op = operand.st_info
    if st == storage.ST_FULL:
        inherit_st_full( this_part, other_part )
    elif st == storage.ST_LOWER:
        inherit_st_lower( this_part, other_part )
    elif st == storage.ST_UPPER:
        inherit_st_upper( this_part, other_part )
    else:
        print( "\n[WARNING] Inheritance of property %s not implemented!\n" % prop )

def inherit_st_full( this_part, other_part ):
    for this, other in zip( itertools.chain(*this_part), itertools.chain(*other_part) ):
        this.st_info = (storage.ST_FULL, other)

#[FIXME] Do row != col as for lower and upper
def inherit_st_diagonal( this_part, other_part ):
    m, n = this_part.shape
    if m == n:
        for i in range(m):
            this = this_part[i][i]
            other = other_part[i][i]
            this.st_info = (storage.ST_DIAG, other)
    else:
        raise WrongPartitioningShape

def inherit_st_lower( this_part, other_part ):
    m, n = this_part.shape
    if m == n:
        for row in range(m):
            for col in range(n):
                this = this_part[row][col]
                other = other_part[row][col]
                if row == col: # Quadrants in the diagonal
                    this.st_info = (storage.ST_LOWER, other)
                #elif row > col: # lower triangle, storage full
                elif row != col: # just for code generation. harmless for the upper block is not referenced in derivation
                    this.st_info = (storage.ST_FULL, other)
    else:
        raise WrongPartitioningShape

def inherit_st_upper( this_part, other_part ):
    m, n = this_part.shape
    if m == n:
        for row in range(m):
            for col in range(n):
                this = this_part[row][col]
                other = other_part[row][col]
                if row == col: # Quadrants in the diagonal
                    this.st_info = (storage.ST_UPPER, other)
                #elif row < col: # upper triangle, storage full
                elif row != col: # just for code generation. harmless for the lower block is not referenced in derivation
                    this.st_info = (storage.ST_FULL, other)
    else:
        raise WrongPartitioningShape

#[FIXME] Do row != col as for lower and upper
def inherit_st_strict_lower( this_part, other_part ):
    m, n = this_part.shape
    if m == n:
        for row in range(m):
            for col in range(n):
                this = this_part[row][col]
                other = other_part[row][col]
                if row == col: # Quadrants in the diagonal
                    this.st_info = (storage.ST_STRICT_LOWER, other)
                elif row > col: # lower triangle, storage full
                    this.st_info = (storage.ST_FULL, other)
    else:
        raise WrongPartitioningShape

#[FIXME] Do row != col as for lower and upper
def inherit_st_strict_upper( this_part, other_part ):
    m, n = this_part.shape
    if m == n:
        for row in range(m):
            for col in range(n):
                this = this_part[row][col]
                other = other_part[row][col]
                if row == col: # Quadrants in the diagonal
                    this.st_info = (storage.ST_STRICT_UPPER, other)
                elif row > col: # lower triangle, storage full
                    this.st_info = (storage.ST_FULL, other)
    else:
        raise WrongPartitioningShape


if __name__ == "__main__":
    A = Matrix("A", ("m", "n"))
    A.st_info = (storage.ST_FULL, A)
    print( partition(A, (1,1), {}) )
    print( partition(A, (1,2), {}) )
    print( partition(A, (2,1), {}) )
    print( partition(A, (2,2), {}) )
