from core.exceptions import OperandNotRegistered

class TOS( dict ):
    def __init__(self):
        dict.__init__(self)

    def register( self, operand ):
        if not operand.get_name() in self:
            self[operand.get_name()] = (operand, set())

    def get_operands( self ):
        return dict([ (k,v[0]) for k,v in self.items() ])

    def get_properties( self, symbol_name ):
        if not symbol_name in self:
            #self[symbol_name] = set()
            raise OperandNotRegistered( symbol_name )
        return self[symbol_name][1]

    def set_property( self, symbol_name, prop ):
        #print( "Setting property ", prop, " to ", symbol_name )
        props = self.get_properties( symbol_name )
        props.add( prop )

    def unset_property( self, symbol_name, prop ):
        props = self.get_properties( symbol_name )
        props.remove( prop )

    def unset_operand( self, operand ):
        del self[operand.get_name()]

_TOS = TOS()

from core.properties import TOE_properties
#from core.algebraic_manipulation import to_canonical, simplify

class TOE( dict ):
    def __init__( self ):
        dict.__init__(self)
        self.reset( )

    def reset( self ):
        for prop in TOE_properties:
            self[prop] = []

    def set_property( self, prop, expr ):
        if not expr in self[prop]:
            #print( "Setting:", prop, expr )
            self[prop].append( expr )

    def get_property( self, prop, expr ):
        return expr in self[prop]

    #def update( self, rewrite_rules ):
        #for prop in TOE_properties:
            #for _expr in self[prop]:
                #for rule in rewrite_rules:
                    #expr = copy.deepcopy( _expr )
                    #new = simplify( to_canonical( replace( expr, [rule] ) ) )
                    #self.set_property( prop, new )

_TOE = TOE()


_T = 0
def new_temp( ):
    global _T
    _T += 1
    return _T

def reset_temp( ):
    global _T
    _T = 0

def push_back_temp( ):
    global _T
    _T -= 1
