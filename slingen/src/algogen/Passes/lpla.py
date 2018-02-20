class function( object ):
    def __init__( self, name, variant, inargs, outargs ):
        self.name = "%s_blk_var%s" % (name, variant)
        self.inargs = inargs
        self.outargs = outargs
        self.body = []
        # block sizes!!!

    def add_statement( self, statement ):
        self.body.append( statement )

    def __repr__( self ):
        head = "%s( %s, %s )" % ( self.name,
                                  ", ".join([arg.name for arg in self.inargs]),
                                  ", ".join([arg.name for arg in self.outargs]) )
        body = "\t" + "\n\t".join( str(st) for st in self.body )
        return "%s\n{\n%s\n}\n" % (head, body)

class declare( object ):
    def __init__( self, operand ):
        self.operand = operand

    def __repr__( self ):
        return "declare %s" % self.operand.name

    def __eq__( self, other ):
        return isinstance(other, declare) and self.operand == other.operand

class partition( object ):
    def __init__( self, operand, shape, part_operand, which, size ):
        self.operand = operand
        self.shape = shape
        self.part_operand = part_operand
        self.which = which
        self.size = size

    def lhs( self ):
        return self.part_operand

    def rhs( self ):
        return self.operand

    def __repr__( self ):
        return "%s = part( %s, %s, %s, %s )" % \
                    ( self.part_operand, self.operand, self.shape,
                      self.which, self.size )

    def __eq__( self, other ):
        return isinstance(other, partition) and \
                self.operand == other.operand and \
                self.part_operand == other.part_operand

class repartition( object ):
    def __init__( self, part_operand, shape, repart_operand, which, size ):
        self.part_operand = part_operand
        self.repart_operand = repart_operand
        self.shape = shape
        self.which = which
        self.size = size

    def __repr__( self ):
        return "%s = repart( %s, %s, %s, %s )" % \
                    ( self.repart_operand, self.part_operand, self.shape,
                      self.which, self.size )

    def lhs( self ):
        return self.repart_operand

    def rhs( self ):
        return self.part_operand

    def __eq__( self, other ):
        return isinstance(other, repartition) and \
                self.part_operand == other.part_operand and \
                self.repart_operand == other.repart_operand

class progress( object ):
    def __init__( self, repart_operand, shape, part_operand, which ):
        self.repart_operand = repart_operand
        self.part_operand = part_operand
        self.shape = shape
        self.which = which

    def lhs( self ):
        return self.part_operand

    def rhs( self ):
        return self.repart_operand

    def __repr__( self ):
        return "%s = progress( %s, %s )" % \
                    ( self.part_operand, self.repart_operand, self.which )

    def __eq__( self, other ):
        return isinstance(other, progress) and \
                self.part_operand == other.part_operand and \
                self.repart_operand == other.repart_operand

class combine( object ):
    def __init__( self, part_operand, shape, operand ):
        self.part_operand = part_operand
        self.shape = shape
        self.operand = operand

    def lhs( self ):
        return self.part_operand

    def rhs( self ):
        return self.operand

    def __repr__( self ):
        return "%s = combine( %s )" % \
                    ( self.operand, self.part_operand )

    def __eq__( self, other ):
        return isinstance(other, combine) and \
                self.operand == other.operand and \
                self.part_operand == other.part_operand

class _while( object ):
    def __init__( self, guard ):
        self.guard = guard
        self.body = []

    def add_statement( self, statement ):
        self.body.append( statement )

    def __repr__( self ):
        head = "while( %s ) // bsizes %s" % ( " and ".join([ "%s_%s < %s" % (op.name, quad, op.name) for (dim, (quad,op)) in self.guard ]), ", ".join([str(dim) for dim,(quad,op) in self.guard]) )
        body = "\t\t" + "\n\t\t".join( str(st) for st in self.body )
        return "%s\n\t{\n%s\n\t}" % (head, body)

    def __eq__( self, other ):
        return isinstance(other, _while) and \
                all([ st1 == st2 for st1, st2 in zip(self.body, other.body) ])

class spacing( object ):
    def __init__( self, string ):
        self.string = string

    def __repr__( self ):
        return self.string

    def __eq__( self, other ):
        return isinstance(other, spacing) and \
                self.string == other.string
