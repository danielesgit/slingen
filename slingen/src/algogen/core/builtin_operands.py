from core.expression import Symbol
from core.properties import ZERO, IDENTITY, INPUT

class Zero( Symbol ):
    def __init__( self, size ):
        Symbol.__init__( self, "zero", size )
        self.set_property( ZERO )

    def __repr__( self ):
        return "0"

class Identity( Symbol ):
    def __init__( self, size ):
        Symbol.__init__( self, "identity", size )
        self.set_property( IDENTITY )

    def __repr__( self ):
        return "I"
