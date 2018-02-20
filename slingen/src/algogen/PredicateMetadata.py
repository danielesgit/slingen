class PredicateMetadata( object ):
    def __init__( self, name, output_size ):
        self.name = name
        self.output_size = output_size

    def lgen_size( self, input_sizes ):
        pass

DB = dict()
