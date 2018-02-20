#!/usr/bin/env python

from core.expression import Symbol, Scalar, Vector, Matrix, \
                            Equal, Plus, Minus, Times, Transpose, Inverse
import core.properties as properties
from core.InferenceOfProperties import *

def bindDimensions( equation, operands ):
    def bindDimensionsRec( node, bindings ):
        if isinstance( node, Equal ):
            (rows_lhs, cols_lhs) = bindDimensionsRec( node.get_children()[0], bindings ) # lhs
            (rows_rhs, cols_rhs) = bindDimensionsRec( node.get_children()[1], bindings ) # rhs
            merge( bindings, rows_lhs, rows_rhs ) # merge sets including rows(lhs) and rows(rhs)
            merge( bindings, cols_lhs, cols_rhs ) # merge sets including rows(lhs) and rows(rhs)
            return (rows_lhs, cols_lhs)
        if isinstance( node, Plus ):
            dims = [ bindDimensionsRec( ch, bindings ) for ch in node.get_children() ]
            # Plus imposes a binding of all rows and of all columns
            for i in range(len(dims)-1):
                merge( bindings, dims[i][0], dims[i+1][0] ) # rows of first and rows of second
                merge( bindings, dims[i][1], dims[i+1][1] ) # cols of first and rows of second
            return ( dims[0] )
        if isinstance( node, Times ): # [TODO] subgroups of 1x1 expressions
            full_dims = [ bindDimensionsRec( ch, bindings ) for ch in node.get_children() ]
            # Drop "scalar" subtrees, be it a scalar operand or a 1x1 expression (e.g. inner product)
            dims = [ dim for dim in full_dims if not (dim[0] in bindings[0] and dim[1] in bindings[0]) ]
            # Times imposes a binding of the "inner dimensions"
            for i in range(len(dims)-1):
                merge( bindings, dims[i][1], dims[i+1][0] ) # cols of first and rows of second
            if dims: return ( dims[0][0], dims[-1][1] ) 
            else:    return full_dims[0] # in case all scalars
        if isinstance( node, Minus ):
            return bindDimensionsRec( node.get_children()[0], bindings )
        if isinstance( node, Transpose ):
            (r,c) = bindDimensionsRec( node.get_children()[0], bindings )
            return (c,r)
        if isinstance( node, Inverse ):
            (r,c) = bindDimensionsRec( node.get_children()[0], bindings )
            # assume inverse of square -> binding
            merge( bindings, r, c )
            return (r,c)
        if isinstance( node, Symbol ):
            dims = ( node.name + "_r", node.name + "_c" )
            if isinstance(node, Matrix):
                if isIdentity( node ) or \
                        isDiagonal( node ) or \
                        isLowerTriangular( node ) or \
                        isUpperTriangular( node ) or \
                        isSymmetric( node ):
                    merge( bindings, dims[0], dims[1] )
            return dims

    def merge( bindings, dim1, dim2 ):
        idxs = []
        for idx in range(1, len(bindings)): # 1st entry corresponds to scalars
            if dim1 in bindings[idx] or \
               dim2 in bindings[idx]:
                idxs.append(idx)
        if len(idxs) > 1: # dim1 and dim2 not in the same set
            idx1 = idxs[0]
            idx2 = idxs[1]
            bindings[idx1].extend( bindings[idx2] )
            bindings[idx2:idx2+1] = []

    bindings = [ [] ] # one set for scalars
    for op in operands: # ... and one per operand dimension
        if isinstance( op, Scalar ): # both dims = 1
            bindings[0].append( op.name+"_r" )
            bindings[0].append( op.name+"_c" )
        elif isinstance( op, Vector ): # 1 col
            bindings.append( [op.name+"_r"] )
            bindings[0].append( op.name+"_c" )
        elif isinstance( op, Matrix ): # Matrix
            bindings.append( [op.name+"_r"] )
            bindings.append( [op.name+"_c"] )
        else:
            raise Exception # [TODO] improve
    
    for eq in equation:
        bindDimensionsRec( eq, bindings )
    return bindings


# Should write proper unit testing

#if __name__ == "__main__":
    ## Scalars
    #alpha = Operand("alpha")
    #alpha.setProperty(Properties.SCALAR)
    ## Vectors
    #x = Operand("x")
    #x.setProperty(Properties.VECTOR)
    #y = Operand("y")
    #y.setProperty(Properties.VECTOR)
    ## Matrices
    #A = Operand("A")
    #C = Operand("C")
    #X = Operand("X")
    #L = Operand("L")
    #L.setProperty(Properties.LOWER_TRIANGULAR)
    #L.setProperty(Properties.TRIANGULAR)
    #U = Operand("U")
    #U.setProperty(Properties.UPPER_TRIANGULAR)
    #U.setProperty(Properties.TRIANGULAR)

    #print bindDimensions( Plus([A, C]), [A, C] )
    #print bindDimensions( Plus([A, L]), [A, L] )
    #print bindDimensions( Minus([A]), [A] )
    #print bindDimensions( Transpose([A]), [A] )
    #print bindDimensions( Inverse([A]), [A] )

    #sylv = Equal([
                  #Plus([
                        #Times([ L, X ]),
                        #Times([ X, U ])
                       #]),
                  #C
                 #])
    #print bindDimensions( sylv, [L, X, U, C] )

    #chol = Equal([ Times([ L, Transpose([L]) ]), A ])
    #print bindDimensions( chol, [L, A] )

    #dot = Equal([ alpha, Times([ Transpose([x]), y ]) ])
