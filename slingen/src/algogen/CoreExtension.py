from core.expression import Operator, Symbol
from core.attributes import UNARY
from core.properties import TOE_properties
from core.prop_to_queryfunc import prop_to_func


class WrapOutBef( Operator ):
    def __init__( self, arg ):
        Operator.__init__( self, [arg], [], UNARY )
        self.size = arg.get_size()

    def isOutput( self ):
        return False

    def isInput( self ):
        return True

    def __repr__( self ):
        return "^%s" % self.children[0]

class WrapOutAft( Operator ):
    def __init__( self, arg ):
        Operator.__init__( self, [arg], [], UNARY )
        self.size = arg.get_size()

    def __repr__( self ):
        return "AO(%s)" % self.children[0]

def isOperand( expr ):
    return isinstance( expr, Symbol ) or \
            isinstance( expr, WrapOutBef ) or \
            isinstance( expr, WrapOutAft )

def infer_properties( update ):
    lhs, rhs = update.children
    for op in lhs:
        for p in TOE_properties:
            try:
                if prop_to_func[p]( rhs ):
                    op.set_property( p )
            except KeyError: # e.g., TRIANGULAR
                pass
