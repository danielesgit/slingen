import itertools

from core.expression import Symbol
from core.functional import contains
from CoreExtension import WrapOutBef, WrapOutAft

# Takes a list of assignments ( such as a PME )
# and builds a dependency graph so that
# if there is a dependency from i to j (j depends on i) -> graph(i,j) == 1
def build_dep_graph( ass_list ):
    neqs = len(ass_list)
    dep_graph = [[0 for i in range(neqs)] for j in range(neqs)]
    for i, this_eq in enumerate( ass_list ):
        lhs, _ = this_eq.get_children()
        for op in lhs:
            for j, other_eq in enumerate( ass_list ):
                if i == j: # no deps with self
                    continue
                _, rhs = other_eq.get_children()
                deps = dependency_type( op, rhs )
                for dep in deps:
                    if dep == 1: # Flow dependence
                        dep_graph[i][j] = 1
                    else: # Anti-dependence
                        dep_graph[j][i] = 1
    return dep_graph

# -1: anti
#  0: output [Cannot happen in here. Only looking at rhs]
#  1: flow
#
# op is the lhs of the statement under consideration
# rhs is the ocurrence of op in the other statements
# Case updates:
#    - occurrence in rhs is WrapOutBef, anti dependence (other assigment needs the op before overwriting it)
#    - occurrence in rhs is WrapOutAft, flow dependence (other assigment needs the final value computed here)
# Case pme/tiling:
#    - occurrence in rhs, flow dependence (other assigment needs the final value computed here)
# If st_info is a different operand:
#    - occurrence of the other operand in rhs, anti dependence (other assigment needs the op before overwriting it)
def dependency_type( op, rhs ):
    if op.__class__ in (WrapOutBef, WrapOutAft):
        op = op.children[0]
    try:
        st_op = op.st_info[1]
    except AttributeError:
        st_op = op

    deps = []
    it = rhs.iterate_preorder()
    node = next(it)
    while node:
        if node.__class__ in (WrapOutBef, WrapOutAft):
            child = next(it)
            if child == op:
                wrap_class = node.__class__
                if wrap_class == WrapOutBef:
                    deps.append( -1 ) # Anti dep (other assigment needs the op before overwriting it)
                elif wrap_class == WrapOutAft:
                    #deps.append( -1 ) # Anti dep (other assigment needs the op before overwriting it)
                    deps.append( 1 ) # Flow dep (other assigment needs the final value computed here)
            elif child == st_op:
                deps.append( -1 ) # Anti dep (other assigment needs the op before overwriting it)
        elif isinstance(node, Symbol):
            if node == op:
                deps.append( 1 ) # Flow dep (other assigment needs the final value computed here)
            elif node == st_op:
                deps.append( -1 ) # Anti dep (other assigment needs the op before overwriting it)
        try:
            node = next(it)
        except StopIteration:
            node = None
    return deps

def zero_out_lower( graph ):
    for row in range(len(graph)):
        for col in range(row):
            graph[row][col] = 0

def graphRoots( g ):
    subgraphs = []
    n_nodes = len(g)
    for col in range( n_nodes ):
        is_root = True
        for row in range( n_nodes ): 
            if g[row][col] == 1:
                is_root = False
                break
        if is_root:
            subgraphs.append( col )
    return subgraphs

def graphNextOf( g, n ):
    n_nodes = len( g )
    nextNodes = []
    for col in range( n_nodes ):
        if g[n][col]:
            nextNodes.append( col )
    return nextNodes

def sortDAGByLevels( g ):
    n_nodes = len( g )
    nodesLevel = [0] * n_nodes
    cur_level_nodes  = graphRoots( g )
    next_level_nodes = []
    while cur_level_nodes:
        for c_n in cur_level_nodes:
            nextOfN = graphNextOf( g, c_n )
            for n_n in nextOfN:
                nodesLevel[n_n] = nodesLevel[c_n] + 1
                next_level_nodes.append(n_n)
        cur_level_nodes = next_level_nodes
        next_level_nodes = []
    return nodesLevel

def dependenciesSatisfied( g, node, sg ):
    n_nodes = len(g)
    satisfied = True
    for dep in range(n_nodes):
        if g[dep][node] and dep not in sg:
            satisfied = False
    return satisfied

def nonEmptySubsets( l ):
    return itertools.chain.from_iterable( 
                itertools.combinations( l, n ) for n in range(1, len(l) + 1)
           )

def subgraphs( g ):
    subg_list = [[]] # initialize with the empty graph
    n_nodes = len( g )
    gSorted = sortDAGByLevels( g ) 
    for level in range( max( gSorted ) + 1 ):
        newSubgList = []
        for subg in subg_list:
            nodes_in_level = [n for n in range(n_nodes) if gSorted[n] == level]
            acc = []
            for n in nodes_in_level:
                if dependenciesSatisfied( g, n, subg ):
                    acc.append( n )
            subsets = nonEmptySubsets( acc )
            for subset in subsets:
                newSubgList.append( subg + list(subset) )
        subg_list.extend(newSubgList)

    for l in range(len(subg_list)):
        for i in range(len(subg_list[l])):
            subg_list[l][i] += 1
    return subg_list

#if __name__ == "__main__":
    ## Dependecy from 1 to 2 -> set to 1 cell (1,2) (well, start from 0)
    ## Root nodes, those whose column is 0
    #g_LU = [
            #[0, 1, 1, 0, 0],
            #[0, 0, 0, 1, 0],
            #[0, 0, 0, 1, 0],
            #[0, 0, 0, 0, 1],
            #[0, 0, 0, 0, 0]
        #]

    #g_CoupSylv = [
            #[ 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0],
            #[ 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            #[ 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            #[ 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0], # 4
            #[ 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            #[ 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            #[ 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
            #[ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], # 8
            #[ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            #[ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            #[ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            #[ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        #]

    #print "Roots of LU's graph:", graphRoots( g_LU )
    #for i in range( len ( g_LU ) ):
        #print "Depend on Task %d: " % (i+1),
        #print [t+1 for t in graphNextOf( g_LU, i )]
    #print "Task 4 satisfied with subgraph [1,3]:", dependenciesSatisfied( g_LU, 3, [0,2] )
    #print "Task 4 satisfied with subgraph [1,2]:", dependenciesSatisfied( g_LU, 3, [0,1] )
    #print "Task 4 satisfied with subgraph [1,2,3]:", dependenciesSatisfied( g_LU, 3, [0,1,2] )
    #print "Sorted:", sortDAGByLevels( g_LU )
    #print "Subgraphs:", subgraphs( g_LU )
    #print
    #print "Roots of Coupled Sylvester's graph:", graphRoots( g_CoupSylv )
    #for i in range( len ( g_CoupSylv ) ):
        #print "Depend on Task %d: " % (i+1),
        #print [t+1 for t in graphNextOf( g_CoupSylv, i )]
    #print "Task 4 satisfied with subgraph [1,3]:", dependenciesSatisfied( g_CoupSylv, 3, [0,2] )
    #print "Task 4 satisfied with subgraph [1,2]:", dependenciesSatisfied( g_CoupSylv, 3, [0,1] )
    #print "Task 4 satisfied with subgraph [1,2,3]:", dependenciesSatisfied( g_CoupSylv, 3, [0,1,2] )
    #print "Sorted:", sortDAGByLevels( g_CoupSylv )
    #print "Subgraphs:"
    #for sg in subgraphs( g_CoupSylv ):
        #print "   ", sg
    #print "# Subgraphs:", len(subgraphs( g_CoupSylv ))
