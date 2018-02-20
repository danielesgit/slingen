import copy
import collections
import itertools

import core.attributes as attributes
import core.properties as properties

from core.exceptions import WrongArityError
from core.TOS import _TOS

class BaseExpression( object ):
    def __init__( self, children = [], line = -1 ):
        self.head = self.__class__
        # For a simple use of patterns after matching
        # asumming only two levels of nestedness, that is,
        # children may have iterables (sequences or lists) but
        # not iterables containing more iterables
        self.children = []
        for ch in children:
            #if isinstance( ch, collections.Iterable ):
            if isinstance( ch, Sequence ):
                self.children.extend( ch )
            else:
                self.children.append( ch )
        self.properties = set()
        self.size = None

    def get_head( self ):
        return self.head

    def get_children( self ):
        return self.children

    def set_children( self, i, expr ):
        self.children[i] = expr

    def get_size( self ):
        return self.size

    def num_nodes( self ):
        return len(list(self.iterate_preorder()))

    def _cleanup( self ):
        raise NotImplementedError

    def match( self, ctx ):
        raise NotImplementedError

    def iterate_preorder( self ):
        yield self
        for child in self.get_children():
            yield from child.iterate_preorder()

    def _preorder_position( self, parent=(None, None) ):
        yield (id(self), parent)
        for i, child in enumerate(self.get_children()):
            yield from child._preorder_position( (self, i) )

    def _postorder_stack( self, parent=(None, None) ):
        if len( self.get_children() ) == 0:
            return [ self, parent, [] ]
        else:
            return [ self, parent, [ch._postorder_stack((self, i)) for i, ch in enumerate(self.get_children())] ]

    def __eq__( self, other ):
        return self.get_head() == other.get_head() and \
                len(self.get_children()) == len(other.get_children()) and \
                all( [ x == y for x,y in zip(self.get_children(), other.get_children()) ] )

    #
    # Property handling
    #
    def set_property( self, prop ):
        self.properties.add( prop )

    def get_properties( self ):
        return self.properties

    def isInput( self ):
        return properties.INPUT in self.properties

    def isOutput( self ):
        return properties.OUTPUT in self.properties

    def isTemporary( self ):
        return properties.TEMPORARY in self.properties

    def isScalar( self ):
        size = self.get_size()
        return len( [dim for dim in size if dim != sONE] ) == 0
        #return properties.SCALAR in self.properties

    def isVector( self ):
        size = self.get_size()
        return len( [dim for dim in size if dim != sONE] ) == 1
        #return properties.VECTOR in self.properties

    def isMatrix( self ):
        size = self.get_size()
        return len( [dim for dim in size if dim != sONE] ) == 2
        #return properties.MATRIX in self.properties

    def isSquare( self ):
        return properties.SQUARE in self.properties

    def isZero( self ):
        return properties.ZERO in self.properties

    def isIdentity( self ):
        return properties.IDENTITY in self.properties

    def isDiagonal( self ):
        return properties.DIAGONAL in self.properties

    def isTriangular( self ):
        return properties.TRIANGULAR in self.properties

    def isLowerTriangular( self ):
        return properties.LOWER_TRIANGULAR in self.properties

    def isUpperTriangular( self ):
        return properties.UPPER_TRIANGULAR in self.properties

    def isUnitDiagonal( self ):
        return properties.UNIT_DIAGONAL in self.properties

    def isImplicitUnitDiagonal( self ):
        return properties.IMPLICIT_UNIT_DIAGONAL in self.properties

    def isSymmetric( self ):
        return properties.SYMMETRIC in self.properties

    def isSPD( self ):
        return properties.SPD in self.properties

    def isNonSingular( self ):
        return properties.NON_SINGULAR in self.properties

    def isOrthogonal( self ):
        return properties.ORTHOGONAL in self.properties

    def isFullRank( self ):
        return properties.FULL_RANK in self.properties

    #
    # Printing
    #
    def __repr__( self ):
        raise NotImplementedError

class Atom( BaseExpression ):
    def __init__( self ):
        BaseExpression.__init__( self, [] )

    def match( self, ctx ):
        # nothing to match, failure
        if len( ctx.stack_expr ) == 0:
            return None
        # pop the expression to match
        expr = ctx.stack_expr.pop()
        if self == expr:
            patt = ctx.stack_patt.pop()
            for m in patt.match( ctx ):
                yield m

    def _cleanup( self ):
        return self

    def __eq__( self, other ):
        raise NotImplementedError

class Expression( BaseExpression ):
    pass

class Sequence( Expression ):
    def __init__( self, children ):
        Expression.__init__( self, children )

    def __iter__( self ):
        yield from self.get_children()

    def _cleanup( self ):
        self.children = [ch._cleanup() for ch in self.get_children()]
        return self

    def match( self, ctx ):
        # Both are Sequences
        patt_ch = self.get_children()
        expr = ctx.stack_expr.pop()
        expr_ch = expr.get_children()
        while len( patt_ch ) == 0 and len( expr_ch ) == 0 and \
                len( ctx.stack_patt ) > 0:
            patt = ctx.stack_patt.pop()
            patt_ch = patt.get_children()
            expr = ctx.stack_expr.pop()
            expr_ch = expr.get_children()
        # Exited loop because no more patterns in the stack
        # and current sequence is also complete: yield match and done
        if len( patt_ch ) == 0 and len( expr_ch ) == 0:
            yield ctx.match
            return None

        # if both empty, match complete, yield
        #if len( patt_ch ) == 0 and len( expr_ch ) == 0:
            #yield ctx.match

        # No pattern to match the expression, failure
        if len( patt_ch ) == 0 and len( expr_ch ) > 0:
            return None

        patt_leaf, patt_next = patt_ch[0], Sequence(patt_ch[1:])
        if isinstance( patt_leaf, Pattern ):
            ctx.stack_patt.append( patt_next )
            # Push full expr back
            # The pattern itself will decide what it may match what is left for next
            ctx.stack_expr.append( expr )
            for m in patt_leaf.match( ctx ):
                yield m
        else: # Atom or Operator
            # nothing to match, failure
            if len( expr_ch ) == 0:
                return None
            else:
                expr_leaf, expr_next = expr_ch[0], Sequence(expr_ch[1:])
                ctx.stack_patt.append( patt_next )
                ctx.stack_expr.append( expr_next )
                ctx.stack_expr.append( expr_leaf )
                for m in patt_leaf.match( ctx ):
                    yield m
            
    def __repr__( self ):
        return "[ " + ", ".join( [ str(ch) for ch in self.get_children() ] ) + " ]"

class NList( Expression ):
    def __init__( self, children ):
        Expression.__init__( self, children )

    def __iter__( self ):
        yield from self.get_children()

    def _cleanup( self ):
        self.children = [ch._cleanup() for ch in self.get_children()]
        return self

    def match( self, ctx ):
        # nothing to match, failure
        if len( ctx.stack_expr ) == 0:
            return None
        # pop the expression to match
        expr = ctx.stack_expr.pop()
        if self.get_head() == expr.get_head():
            patt_seq = Sequence(self.get_children())
            expr_seq = Sequence(expr.get_children())
            ctx.stack_expr.append( expr_seq )
            for m in patt_seq.match( ctx ):
                yield m

    def __repr__( self ):
        return "NL[ " + ", ".join( [ str(ch) for ch in self.get_children() ] ) + " ]"

#
# Operators
#
class Operator( Expression ):
    def __init__( self, children, attr, arity ):
        Expression.__init__( self, children )
        self.attributes = attr
        self.flatten_associative()
        # Apply identity if so (e.g., Plus(a) -> a) (not here, at most in __new__)
        self.arity = arity
        self.check_arity()

    def flatten_associative( self ):
        if attributes.ASSOCIATIVE in self.attributes:
            children = []
            for ch in self.get_children():
                if isinstance( ch, self.__class__ ):
                    children.extend( ch.get_children() )
                else:
                    children.append( ch )
            self.children = children

    def check_arity( self ):
        if self.arity == attributes.UNARY and \
                len( self.children ) != 1:
            raise WrongArityError
        if self.arity == attributes.BINARY and \
                len( self.children ) != 2:
            raise WrongArityError

    def set_children( self, i, expr ):
        Expression.set_children( self, i, expr )
        #self.flatten_associative() # [TODO] DOUBLE-CHECK if it can stay commented!!!!
        # Also identity

    def _cleanup( self ):
        self.children = [ch._cleanup() for ch in self.get_children()]
        self.flatten_associative()
        if attributes.IDENTITY in self.attributes and \
                len(self.children) == 1:
            return self.children[0]
        #return self.__class__( self.children, self.attributes, self.arity )
        #return self.__class__( self.children )
        return self

    def match( self, ctx ):
        # nothing to match, failure
        if len( ctx.stack_expr ) == 0:
            return None
        # pop the expression to match
        expr = ctx.stack_expr.pop()
        if self.get_head() == expr.get_head():
            patt_seq = Sequence(self.get_children())
            if attributes.COMMUTATIVE not in self.attributes:
                expr_seq = Sequence(expr.get_children())
                ctx.stack_expr.append( expr_seq )
                for m in patt_seq.match( ctx ):
                    yield m
            else:
                #_ctx = copy.deepcopy( ctx )
                _ctx = copy.copy( ctx )
                expr_ch = expr.get_children()
                for ch_permutation in itertools.permutations( expr_ch ):
                    #ctx = copy.deepcopy( _ctx )
                    ctx = copy.copy( _ctx )
                    ctx.stack_expr.append( Sequence( list(ch_permutation) ) )
                    for m in patt_seq.match( ctx ):
                        yield m

    def __eq__( self, other ):
        if self.get_head() == other.get_head() and \
           len(self.get_children()) == len(other.get_children()):
            if attributes.COMMUTATIVE in self.attributes:
                return sorted( [ str(ch) for ch in self.get_children() ] ) == \
                       sorted( [ str(ch) for ch in other.get_children() ] )
            else:
                return all( [ x == y for x,y in zip(self.get_children(), other.get_children()) ] )
        return False

class Equal( Operator ):
    def __init__( self, children ):
        Operator.__init__( self, children, [], attributes.BINARY )

    def lhs( self ):
        return self.get_children()[0]
            
    def rhs( self ):
        return self.get_children()[1]
            
    def __repr__(self ):
        return "Equal( " + ", ".join( [ str(ch) for ch in self.get_children() ] ) + " )"

    def to_math( self ):
        lhs, rhs = self.children
        return "%s = %s" % (lhs.to_math(), rhs.to_math())

class Plus( Operator ):
    def __init__( self, children ):
        Operator.__init__( self, children, \
                           [attributes.COMMUTATIVE, attributes.ASSOCIATIVE, attributes.IDENTITY], \
                           attributes.NARY )

    def get_size( self ):
        if self.size == None:
            self.size = self.get_children()[0].get_size()
        return self.size
            
    def __repr__(self ):
        return "Plus( " + ", ".join( [ str(ch) for ch in self.get_children() ] ) + " )"

    def to_math( self ):
        return "(%s)" % " + ".join([ch.to_math() for ch in self.children])

class Minus( Operator ):
    def __init__( self, children ):
        Operator.__init__( self, children, [], attributes.UNARY )
            
    def get_size( self ):
        if self.size == None:
            self.size = self.get_children()[0].get_size()
        return self.size

    def __repr__(self ):
        return "Minus( " + ", ".join( [ str(ch) for ch in self.get_children() ] ) + " )"

    def to_math( self ):
        return "-%s" % self.children[0].to_math()

class Times( Operator ):
    def __init__( self, children ):
        Operator.__init__( self, children, \
                           [attributes.ASSOCIATIVE, attributes.IDENTITY], \
                           attributes.NARY )

    def get_size( self ):
        if self.size == None:
            self.size = self._calc_size()
        return self.size

    def _calc_size( self ):
        non_scalars = list(filter( lambda x: x.get_size() != (sONE, sONE), self.get_children() ))
        if len(non_scalars) == 0:
            return (1, 1)
        rows = non_scalars[0].get_size()[0]
        i = 0
        while rows == sONE and i < len(non_scalars) - 1:
            if non_scalars[i].size[1] == sONE:
                rows = non_scalars[i+1].size[0]
            i += 1
        cols = non_scalars[-1].size[1]
        i = len(non_scalars) - 1
        while cols == sONE and i > 0:
            #if non_scalars[i].size[0] == 1: # [CHECK]
            if non_scalars[i].size[0] == sONE:
                cols = non_scalars[i-1].size[1]
            i -= 1
        return (rows, cols)

    def __repr__(self ):
        return "Times( " + ", ".join( [ str(ch) for ch in self.get_children() ] ) + " )"

    def to_math( self ):
        return " * ".join([ch.to_math() for ch in self.children])

class Transpose( Operator ):
    def __init__(self, children ):
        Operator.__init__( self, children, [], attributes.UNARY )

    def get_size( self ):
        if self.size == None:
            self.size = list(reversed(self.get_children()[0].get_size()))
        return self.size

    def __repr__(self ):
        return "Transpose( " + ", ".join( [ str(ch) for ch in self.get_children() ] ) + " )"

    def to_math( self ):
        return "trans(%s)" % self.children[0].to_math()


class Inverse( Operator ):
    def __init__(self, children ):
        Operator.__init__( self, children, [], attributes.UNARY )

    def get_size( self ):
        if self.size == None:
            self.size = self.get_children()[0].get_size()
        return self.size

    def __repr__(self ):
        return "Inverse( " + ", ".join( [ str(ch) for ch in self.get_children() ] ) + " )"

    def to_math( self ):
        return "inverse(%s)" % self.children[0].to_math()

class BlockedExpression( Expression ):
    def __init__( self, nd_array, size, shape ):
        Expression.__init__( self, nd_array )
        self.size = size
        #self.shape = shape
        self.shape = tuple(shape) # [TODO] Any problem with this?

    def set_children( self, i, expr ):
        #pointer = self.get_children()
        #for pos_i in range( len(i)-1 ):
            #pointer = pointer[ i[pos_i] ]
        #pointer[i[-1]] = expr
        row, col = i // len( self.children[0] ), i % len( self.children[0] )
        self.children[row][col] = expr

    # only works for flattening matrices
    def flatten_children( self ):
        return list(itertools.chain.from_iterable( self.get_children() ))

    def transpose( self ):
        self.children = [list(row) for row in zip(*self.children)]
        self.size = list(reversed(self.size))
        self.shape = tuple(reversed(self.shape))

    def _cleanup( self ):
        # TODO: should reassign back to children
        for ch in self.flatten_children():
            ch._cleanup()
        return self

    def __iter__( self ):
        yield from self.get_children()

    def match( self, ctx ):
        # nothing to match, failure
        if len( ctx.stack_expr ) == 0:
            return None
        # pop the expression to match
        expr = ctx.stack_expr.pop()
        if self.get_head() == expr.get_head() and \
                self.shape == expr.shape:
            # This allows the use of PatternPlus and PatternStar for rows or full blocked expressions
            # In principle, no BlockedExpression would appear in a pattern, would it?
            patt_seq = Sequence(self.flatten_children())
            expr_seq = Sequence(expr.flatten_children())
            ctx.stack_expr.append( expr_seq )
            for m in patt_seq.match( ctx ):
                yield m

    def iterate_preorder( self ):
        yield self
        for child in self.flatten_children():
            yield from child.iterate_preorder()

    # only for matrices (2D blocked expressions)
    def _preorder_position( self, parent=(None, None) ):
        yield (id(self), parent)
        for i in range(len(self.children)):
            for j in range(len(self.children[0])):
                yield from self.children[i][j]._preorder_position( (self, (i,j)) )

    def _postorder_stack( self, parent=(None,None) ):
        return [ self, parent, [ch._postorder_stack((self, i)) for i, ch in enumerate(self.flatten_children())] ]

    def __getitem__( self, i ):
        if i > len(self.get_children()):
            raise TypeError
        return self.get_children()[i]

    def __eq__( self, other ):
        return self.get_head() == other.get_head() and \
                self.shape == self.shape and \
                self.get_children() == self.get_children()

    def __repr__( self ):
        #return "[ %s ]" % ( "; ".join([ ", ".join([ cell for cell in row ]) for row in self.get_children() ]) )
        return str(self.get_children())

class Predicate( Expression ):
    def __init__( self, name, args, size ):
        Expression.__init__( self, args )
        self.name = name
        self.size = []
        for s in size:
            this_s = []
            for dim in s:
                if isinstance(dim, str):
                    this_s.append( Symbol(dim) )
                else:
                    this_s.append( dim )
            self.size.append( tuple(this_s) )

    def get_name( self ):
        return self.name

    def set_children( self, i, expr ):
        self.children[i] = expr

    def _cleanup( self ):
        self.children = [ ch._cleanup() for ch in self.get_children()]
        return self

    def match( self, ctx ):
        # nothing to match, failure
        if len( ctx.stack_expr ) == 0:
            return None
        # pop the expression to match
        expr = ctx.stack_expr.pop()
        if self.get_head() == expr.get_head() and \
                self.name == expr.name:
            patt_seq = Sequence(self.get_children())
            expr_seq = Sequence(expr.get_children())
            ctx.stack_expr.append( expr_seq )
            for m in patt_seq.match( ctx ):
                yield m

    def get_size( self ):
        return self.size[0]

    def __eq__( self, other ):
        return self.get_head() == other.get_head() and \
                self.name == other.name and \
                self.get_children() == other.get_children()

    def __repr__( self ):
        return "%s( %s )" % (self.name, ", ".join([str(ch) for ch in self.get_children()]))

class Function( Predicate ):
    pass

#
# Symbols
#
class Symbol( Atom ):
    def __init__( self, name, size=() ):
        Atom.__init__( self )
        self.name = name
        self.size = size
        _TOS.register( self ) ###

    def get_name( self ):
        return self.name

    def __eq__( self, other ):
        return self.get_head() == other.get_head() and \
               self.get_name() == other.get_name()

    def __lt__( self, other ):
        return self.name < other.name

    def set_property( self, prop ):
        # TODO improve
        if prop == properties.INPUT:
            try:
                _TOS.unset_property( self.get_name(), properties.OUTPUT )
            except KeyError:
                pass
        elif prop == properties.OUTPUT:
            try:
                _TOS.unset_property( self.get_name(), properties.INPUT )
            except KeyError:
                pass
        _TOS.set_property( self.get_name(), prop )

    def get_properties( self ):
        return _TOS.get_properties( self.get_name() )

    def isInput( self ):
        return properties.INPUT in _TOS.get_properties(self.get_name())

    def isOutput( self ):
        return properties.OUTPUT in _TOS.get_properties(self.get_name())

    def isTemporary( self ):
        return properties.TEMPORARY in _TOS.get_properties(self.get_name())

    def isScalar( self ):
        return properties.SCALAR in _TOS.get_properties(self.get_name())

    def isVector( self ):
        return properties.VECTOR in _TOS.get_properties(self.get_name())

    def isMatrix( self ):
        return properties.MATRIX in _TOS.get_properties(self.get_name())

    def isSquare( self ):
        return properties.SQUARE in _TOS.get_properties(self.get_name())

    def isZero( self ):
        return properties.ZERO in _TOS.get_properties(self.get_name())

    def isIdentity( self ):
        return properties.IDENTITY in _TOS.get_properties(self.get_name())

    def isDiagonal( self ):
        return properties.DIAGONAL in _TOS.get_properties(self.get_name())

    def isTriangular( self ):
        return properties.TRIANGULAR in _TOS.get_properties(self.get_name())

    def isLowerTriangular( self ):
        return properties.LOWER_TRIANGULAR in _TOS.get_properties(self.get_name())

    def isUpperTriangular( self ):
        return properties.UPPER_TRIANGULAR in _TOS.get_properties(self.get_name())

    def isUnitDiagonal( self ):
        return properties.UNIT_DIAGONAL in _TOS.get_properties(self.get_name())

    def isImplicitUnitDiagonal( self ):
        return properties.IMPLICIT_UNIT_DIAGONAL in _TOS.get_properties(self.get_name())

    def isSymmetric( self ):
        return properties.SYMMETRIC in _TOS.get_properties(self.get_name())

    def isSPD( self ):
        return properties.SPD in _TOS.get_properties(self.get_name())

    def isNonSingular( self ):
        return properties.NON_SINGULAR in _TOS.get_properties(self.get_name())

    def isOrthogonal( self ):
        return properties.ORTHOGONAL in _TOS.get_properties(self.get_name())

    def isFullRank( self ):
        return properties.FULL_RANK in _TOS.get_properties(self.get_name())

    def __repr__( self ):
        return self.name

    def to_math( self ):
        return self.name

sONE = Symbol('1')
sZERO = Symbol('0')

class Scalar( Symbol ):
    def __init__( self, name, size=None ):
        Symbol.__init__( self, name, (sONE, sONE) )

class Vector( Symbol ):
    def __init__( self, name, size ):
        Symbol.__init__( self, name, (size[0], sONE) ) # ColumnVector

class Matrix( Symbol ):
    def __init__( self, name, size ):
        Symbol.__init__( self, name, size )

class Tensor( Symbol ): # will need indices as well
    def __init__( self, name, size ):
        Symbol.__init__( self, name, size )

# This inherits from atom (not a symbol)
class NumericConstant( Atom ):
    def __init__( self, value ):
        Atom.__init__( self )
        self.value = value
        self.size = (1, 1)

    def get_value( self ):
        return self.value

    def __eq__( self, other ):
        return self.get_head() == other.get_head() and \
               self.get_value() == other.get_value()

    def __repr__( self ):
        return str(self.value)

#
# Patterns
#
# Check validity of a pattern by asserting
# that do not exist two patterns with same name and different length (underscores)
#
# Add the __eq__ to everyone
# If needed, I could have a "same" function for pointer equality
class Pattern( Atom ):
    def __init__( self, name ):
        Atom.__init__( self )
        self.name = name

    def get_name( self ):
        return self.name

    def match( self, ctx ):
        # nothing to match, failure
        if len( ctx.stack_expr ) == 0:
            return None
        # pop the expression to match
        expr = ctx.stack_expr.pop()
        # expr is a Sequence
        expr_ch = expr.get_children()
        e,o = self.range_in_seq( expr_ch )
        #_ctx = copy.deepcopy( ctx )
        _ctx = copy.copy( ctx )
        for i in range(e,o+1):
            expr_leaf, expr_next = Sequence(expr_ch[:i]), Sequence(expr_ch[i:])
            #ctx = copy.deepcopy( _ctx )
            ctx = copy.copy( _ctx )
            ctx.stack_expr.append( expr_next )
            patt_name = self.get_name()
            #### if PatternDot, then the match is not a sequence but a single element
            if isinstance( self, PatternDot ):
                expr_leaf = expr_leaf.get_children()[0]
            ####
            if patt_name not in ctx.match or \
                    patt_name in ctx.match and expr_leaf == ctx.match[patt_name]:
                ctx.match[patt_name] = expr_leaf
                # unstack and keep going
                next_patt = ctx.stack_patt.pop()
                for m in next_patt.match( ctx ):
                    yield m

    def __eq__( self, other ):
        return self.get_head() == other.get_head() and \
               self.get_name() == other.get_name()

    def __repr__( self ):
        raise NotImplementedError( "Pattern.__repr__ not overloaded!" )
            
class PatternDot( Pattern ):
    def __init__( self, name ):
        Pattern.__init__( self, name )

    # can match one and only one element
    def range_in_seq( self, seq ):
        return (1, min(1, len(seq)))

    def __repr__( self ):
        return self.name + "_"
            
class PatternPlus( Pattern ):
    def __init__( self, name ):
        Pattern.__init__( self, name )

    # can match one or more elements
    def range_in_seq( self, seq ):
        return (1, len(seq))

    def __repr__( self ):
        return self.name + "__"
            
class PatternStar( Pattern ):
    def __init__( self, name ):
        Pattern.__init__( self, name )

    # can match zero, one or more elements
    def range_in_seq( self, seq ):
        return (0, len(seq))

    def __repr__( self ):
        return self.name + "___"

class PatternOr( Expression ):
    def __init__( self, children ):
        Expression.__init__( self, children )

    def match( self, ctx ):
        # nothing to match, failure
        #if len( ctx.stack_expr ) == 0:
            #return None
        # pop the expression to match
        #expr = ctx.stack_expr.pop()
        # expr is a Sequence
        #expr_ch = expr.get_children()
        #
        _ctx = copy.copy( ctx )
        for ch in self.get_children():
            #print( ch )
            #print( ctx.stack_expr[-1] )
            ctx = copy.copy( _ctx )
            #ctx.stack_expr.append( expr_next )
            #patt_name = self.get_name()
            ##### if PatternDot, then the match is not a sequence but a single element
            #if isinstance( self, PatternDot ):
                #expr_leaf = expr_leaf.get_children()[0]
            #####
            #patt_seq = Sequence([ ch ])
            #yield from patt_seq.match( ctx )
            for m in ch.match( ctx ):
            #for m in patt_seq.match( ctx ):
                yield m

    def __eq__( self, other ):
        return self.get_head() == other.get_head() and \
           len(self.get_children()) == len(other.get_children())

    def __repr__( self ):
        return "( " + " | ".join( [ str(ch) for ch in self.get_children() ] ) + " )"

