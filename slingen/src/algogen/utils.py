from core.expression import Symbol, Equal, Plus, Minus, Times, Transpose, Inverse
from graph import build_dep_graph                            

def size_as_func_of_operands( expr ):
    # R, C -> rows of, cols of
    if isinstance( expr, Symbol ):
        return ( (expr, "R"), (expr, "C") )
    if isinstance( expr, Plus ):
        return size_as_func_of_operands( expr.get_children()[0] )
    if isinstance( expr, Minus ):
        return size_as_func_of_operands( expr.get_children()[0] )
    if isinstance( expr, Times ): # ignore scalars for now
        left = size_as_func_of_operands( expr.get_children()[0] )[0]
        right = size_as_func_of_operands( expr.get_children()[-1] )[1]
        return ( left, right )
    if isinstance( expr, Transpose ):
        return list( reversed( size_as_func_of_operands( expr.get_children()[0] ) ) )
    if isinstance( expr, Inverse ):
        return size_as_func_of_operands( expr.get_children()[0] )


# Find one possible valid sequence to compute 
# the equations/assignments in the PME/updates
# that respects the data dependencies
def sort( statements ): # rename this function
    sorted = []
    dep_graph = build_dep_graph( statements )
    while len( sorted ) != len( statements ):
        new = []
        for cur_eq in range( len( dep_graph ) ):
            # if not in sorted and no antecesor I depend upon...
            if cur_eq not in sorted and \
               not any( [ dep_graph[antecesor][cur_eq] for antecesor in range(len(dep_graph)) ] ):
                sorted.append( cur_eq )
                new.append( cur_eq )
        for eq_idx in new:
            for col in range(len(dep_graph[0])):
                dep_graph[eq_idx][col] = 0
    return [statements[index] for index in sorted]

