class WrongArityError( Exception ):
    pass

class OperandNotRegistered( Exception ):
    pass

MAX_REPLACEMENT_ITERATIONS = 100
class MaxReplacementIterationsExceeded( Exception ):
    pass
