from core.attributes import UNARY
from core.expression import Symbol, Equal, Operator
from core.functional import RewriteRule, Replacement, replace
from core.InferenceOfProperties import Zero

import Passes.lpla as lpla

_MATLAB_line_separator = "% "  + "-" * 50
_C_line_separator      = "/* " + "-" * 50 + " */"

class tril( Operator ):
    def __init__( self, arg ):
        Operator.__init__( self, [arg], [], UNARY )
        self.size = arg.get_size()

    def isLowerTriangular( self ):
        return True

    def __repr__( self ):
        return "tril(%s)" % self.children[0]

class triu( Operator ):
    def __init__( self, arg ):
        Operator.__init__( self, [arg], [], UNARY )
        self.size = arg.get_size()

    def isUpperTriangular( self ):
        return True

    def __repr__( self ):
        return "triu(%s)" % self.children[0]

#
# Passes over the lpla IR
#
def PassBlockSizes( alg ):
    f = alg
    loop = [st for st in f.body if isinstance(st, lpla._while)][0]
    f.block_sizes = ["%sb" % d for (d,(quad,op)) in loop.guard]

def PassPartRepartObjects( alg ):
    f = alg
    loop = [st for st in f.body if isinstance(st, lpla._while)][0]
    repart_sts = [st for st in loop.body if isinstance(st, lpla.repartition)]
    #
    f.part_repart_objs = []
    f.part_repart_objs_shape = []
    for st in repart_sts:
        f.part_repart_objs.append( (st.part_operand, st.repart_operand) )
        f.part_repart_objs_shape.append( st.shape )

def PassSpacings_MATLAB( alg ):
    PassSpacings( alg, _MATLAB_line_separator )

def PassSpacings_C( alg ):
    PassSpacings( alg, _C_line_separator )

def PassSpacings( alg, line_separator ):
    f = alg
    part_idx = [i for i,st in enumerate(f.body) if isinstance(st, lpla.partition)][0]
    loop_idx = [i for i,st in enumerate(f.body) if isinstance(st, lpla._while)][0]
    loop = f.body[loop_idx]

    repart_idx = [i for i,st in enumerate(loop.body) if isinstance(st, lpla.repartition)]
    first_repart_idx = repart_idx[0]
    last_repart_idx = repart_idx[-1]
    cont_idx = [i for i,st in enumerate(loop.body) if isinstance(st, lpla.progress)]
    first_cont_idx = cont_idx[0]

    # Adding spaces bottom up
    loop.body.insert( first_cont_idx, lpla.spacing("") )
    loop.body.insert( first_cont_idx, lpla.spacing(line_separator) )
    loop.body.insert( first_cont_idx, lpla.spacing("") )

    loop.body.insert( last_repart_idx+1, lpla.spacing("") )
    loop.body.insert( last_repart_idx+1, lpla.spacing(line_separator) )
    loop.body.insert( last_repart_idx+1, lpla.spacing("") )

    loop.body.insert( first_repart_idx, lpla.spacing("") )

    f.body.insert( loop_idx, lpla.spacing("") )
    f.body.insert( part_idx, lpla.spacing("") )

def PassStorage( alg ):
    def _PassStorage( st ):
        if isinstance( st, lpla._while ):
            for s in st.body:
                _PassStorage( s )
        elif isinstance( st, Equal ):
            symbols = []
            for n in st.iterate_preorder():
                # Zero has no st_info...
                if isinstance(n, Zero):
                    pass
                elif isinstance( n, Symbol ) and n.st_info[1] != n:
                    n_st = n.st_info[1]
                    n_st.st_info = n.st_info
                    # E.g., in Cholesky, n is L_11, and n_st is A_11
                    #if n.isLowerTriangular() and not n_st.isLowerTriangular(): 
                        #symbols.append( RewriteRule( n, Replacement(tril(n_st)) ) )
                    #elif n.isUpperTriangular() and not n_st.isUpperTriangular(): 
                        #symbols.append( RewriteRule( n, Replacement(triu(n_st)) ) )
                    #else:
                    symbols.append( RewriteRule( n, Replacement(n_st) ) )
            replace( st, symbols )
    for st in alg.body:
        _PassStorage( st )

def PassRemoveAssZeroToTemp( alg ):
    def _PassRemoveAssZeroToTemp( st ):
        if isinstance( st, lpla._while ):
            st.body = [ _PassRemoveAssZeroToTemp( s ) for s in st.body ]
            st.body = [ s for s in st.body if s is not None ]
            return st
        elif isinstance( st, Equal ):
            lhs, rhs = st.get_children()
            if len( lhs.children ) == 1 and lhs.children[0].isTemporary() and\
                    isinstance( rhs, Symbol ) and rhs.isZero():
                return None
            return st
        else: return st
    alg.body = [ _PassRemoveAssZeroToTemp( st ) for st in alg.body ]
    alg.body = [ st for st in alg.body if st is not None ]

