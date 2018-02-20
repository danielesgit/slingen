import itertools
import Partitioning

class Algorithm( object ):
    def __init__( self, linv, variant, init, repart, contwith, before, after, updates ):
        self.linv = linv
        self.variant = variant
        if init:
            #assert( len(init) == 1 )
            self.init = init[0]
        else:
            self.init = None
        self.repart = repart
        self.contwith = contwith
        self.before = before
        self.after = after
        self.updates = updates
        # To be filled up for code generation
        self.name = None
        self.partition = None
        self.partition_size = None
        self.guard = None
        self.repartition = None
        self.repartition_size = None
        self.basic_repart = None
        self.cont_with = None

    def prepare_for_code_generation( self ):
        self.set_name()
        self.set_partition()
        self.set_partition_size()
        self.set_guard()
        self.set_repartition()
        self.set_repartition_size()
        self.set_basic_repart()
        self.set_cont_with()

    def set_name( self ):
        self.name = "%s_blk_var%d" % (self.linv.operation.name, self.variant)

    def set_partition( self ):
        self.partition = dict()
        traversals = self.linv.traversals[0][0]
        #for op in self.linv.operation.operands: # [FIX] linv_operands?
        for op in self.linv.linv_operands: # [FIX] linv_operands?
            #part_size = self.linv.pme.part_shape[ op.get_name() ]
            part_size = self.linv.linv_operands_part_shape[ op.get_name() ]
            #part_flat = list(itertools.chain( *self.linv.pme.partitionings[ op.get_name() ] ))
            part_flat = list(itertools.chain( *self.linv.linv_operands_basic_part[ op.get_name() ] ))
            trav = traversals[op.get_name()]
            if part_size == (1, 1):
                continue
            elif part_size == (1, 2):
                if trav == (0, 1):
                    part_quad = "L"
                else: # (0, -1)
                    part_quad = "R"
            elif part_size == (2, 1):
                if trav == (1, 0):
                    part_quad = "T"
                else: # (-1, 0)
                    part_quad = "B"
            elif part_size == (2, 2):
                if trav == (1, 1):
                    part_quad = "TL"
                elif trav == (1, -1):
                    part_quad = "TR"
                elif trav == (-1, 1):
                    part_quad = "BL"
                else: #(-1, -1):
                    part_quad = "BR"
            else:
                raise Exception
            self.partition[ op.get_name() ] = (part_size, part_flat, part_quad)

    def set_partition_size( self ):
        self.partition_size = dict()
        traversals = self.linv.traversals[0][0]
        #for op in self.linv.operation.operands:
        for op in self.linv.linv_operands:
            name = op.get_name()
            traversal = traversals[op.get_name()]
            if traversal == (0, 0):
                continue
            elif traversal in ( (0, 1), (0, -1) ): # L|R  (the specific quadrant can be retrieved from self.partition)
                self.partition_size[ name ] = ( op.size[0], 0 )
            elif traversal in ( (1, 0), (-1, 0) ): # T/B
                self.partition_size[ name ] = ( 0, op.size[1] )
            elif traversal in ( (1, 1), (1, -1), (-1, 1), (-1, -1) ): # 2x2
                self.partition_size[ name ] = ( 0, 0 )
            else:
                print( name, traversal )
                raise Exception

    def set_guard( self ):
        self.guard = []
        traversals = self.linv.traversals[0][0]
        #guard_dims = [bd[0] for bd in self.linv.linv_bound_dimensions[1:]]
        guard_dims = []
        #for bd in self.linv.linv_bound_dimensions[1:]:
        for bd in self.linv.operation.bound_dimensions[1:]:
            for d in bd:
                op_name, dim = d.split("_")
                op = [ o for o in self.linv.operation.operands if o.name == op_name ][0]
                if op.st_info[1] != op:
                    continue
                if dim == "r":
                    idx = 0
                else:
                    idx = 1
                if ( traversals[op_name][idx] == 0 ):
                    continue
                self.guard.append( (op.get_size()[idx], guard(op, traversals[op_name])) )
                break

    def set_repartition( self ):
        self.repartition = dict()
        traversals = self.linv.traversals[0][0]
        #for op in self.linv.operation.operands:
        for op in self.linv.linv_operands:
            part_size = self.linv.linv_operands_part_shape[ op.get_name() ]
            #part_size = self.linv.pme.part_shape[ op.get_name() ]
            repart = self.repart[ op.get_name() ]
            traversal = traversals[op.get_name()]
            if part_size == (1, 1):
                continue
            elif part_size == (1, 2):
                repart_size = (1, 3)
                if traversal == (0, 1): # ( 0 || 1 | 2 )
                    repart_quadrant = "R"
                else: # ( 0 | 1 || 2 )
                    repart_quadrant = "L"
            elif part_size == (2, 1):
                repart_size = (3, 1)
                if traversal == (1, 0): # ( 0 // 1 / 2 )
                    repart_quadrant = "B"
                else: # ( 0 / 1 // 2 )
                    repart_quadrant = "T"
            elif part_size == (2, 2):
                repart_size = (3, 3)
                if traversal == (1, 1): # BR becomes 2x2
                    repart_quadrant = "BR"
                elif traversal == (1, -1): # BL becomes 2x2
                    repart_quadrant = "BL"
                elif traversal == (-1, 1): # TR becomes 2x2
                    repart_quadrant = "TR"
                else: #if traversal == (-1, -1): # TL becomes 2x2
                    repart_quadrant = "TL"
            else:
                raise Exception
            repart_flat = list(flatten_repart(repart))
            self.repartition[ op.get_name() ] = (repart_size, repart_flat, repart_quadrant)

    def set_repartition_size( self ):
        self.repartition_size = dict()
        traversals = self.linv.traversals[0][0]
        #for op in self.linv.operation.operands:
        for op in self.linv.linv_operands:
            name = op.get_name()
            traversal = traversals[op.get_name()]
            if traversal == (0, 0):
                continue
            elif traversal in ( (0, 1), (0, -1) ): # Quadrant is 1
                self.repartition_size[ name ] = ( "1", op.size[0], "bs" )
            elif traversal in ( (1, 0), (-1, 0) ): # Quadrant is 1
                self.repartition_size[ name ] = ( "1", "bs", op.size[1] )
            elif traversal in ( (1, 1), (1, -1), (-1, 1), (-1, -1) ): # Quadrant is 11
                self.repartition_size[ name ] = ( "11", "bs", "bs" )
            else:
                print( name, traversal )
                raise Exception

    def set_basic_repart( self ):
        self.basic_repart = dict()
        traversals = self.linv.traversals[0][0]
        for op in self.linv.linv_operands:
            part_size = self.linv.linv_operands_part_shape[ op.get_name() ]
            if part_size == (1, 1):
                repart_size = (1, 1)
            elif part_size == (1, 2):
                repart_size = (1, 3)
            elif part_size == (2, 1):
                repart_size = (3, 1)
            elif part_size == (2, 2):
                repart_size = (3, 3)
            else:
                raise Exception
            self.basic_repart[ op.get_name() ] = Partitioning.repartition_shape( op, repart_size )

    def set_repartition_size( self ):
        self.repartition_size = dict()
        traversals = self.linv.traversals[0][0]
        #for op in self.linv.operation.operands:
        for op in self.linv.linv_operands:
            name = op.get_name()
            traversal = traversals[op.get_name()]
            if traversal == (0, 0):
                continue

    def set_cont_with( self ):
        self.cont_with = dict()
        traversals = self.linv.traversals[0][0]
        #for op in self.linv.operation.operands:
        for op in self.linv.linv_operands:
            part_size = self.linv.linv_operands_part_shape[ op.get_name() ]
            #part_size = self.linv.pme.part_shape[ op.get_name() ]
            traversal = traversals[op.get_name()]
            if part_size == (1, 1):
                continue
            elif part_size == (1, 2):
                if traversal == (0, 1): # ( 0 | 1 || 2 )  1 appended to L
                    cont_with_quadrant = "L"
                else: # ( 0 || 1 | 2 ) 1 appended to R
                    cont_with_quadrant = "R"
            elif part_size == (2, 1):
                if traversal == (1, 0): # ( 0 / 1 // 2 )  1 appended to T
                    cont_with_quadrant = "T"
                else: # ( 0 // 1 / 2 ) 1 appended to B
                    cont_with_quadrant = "B"
            elif part_size == (2, 2):
                if traversal == (1, 1): # TL grows
                    cont_with_quadrant = "TL"
                elif traversal == (1, -1): # TR grows
                    cont_with_quadrant = "TR"
                elif traversal == (-1, 1): # BL grows
                    cont_with_quadrant = "BL"
                else: #if traversal == (-1, -1): # BR grows
                    cont_with_quadrant = "BR"
            else:
                raise Exception
            self.cont_with[ op.get_name() ] = cont_with_quadrant

def guard( op, traversal ):
    name = op.get_name()
    #op = [ o for o in self.operations.operands if o.name == op_name ][0]
    if traversal == (0, 1): # L -> R
        return ("L", op)
    elif traversal == (0, -1): # R -> L
        return ("R", op)
    elif traversal == (1, 0): # T -> B
        return ("T", op)
    elif traversal == (-1, 0): # B -> T
        return ("B", op)
    elif traversal == (1, 1): # TL -> BR
        return ("TL", op)
    elif traversal == (1, -1): # TR -> BL
        return ("TR", op)
    elif traversal == (-1, 1): # BL -> TR
        return ("BL", op)
    elif traversal == (-1, -1): # BR -> TL
        return ("BR", op)
    else:
        print( op_name, traversal )
        raise Exception

# Flattens a matrix of matrices resulting from a repartitioning
def flatten_repart( repart ):
    r, c = 0, 0
    chained = []
    for row in repart:
        for cell in row:
            _r = r
            _c = c
            for _row in cell:
                _c = c
                for _cell in _row:
                    chained.append( (_r, _c, _cell) )
                    _c += 1
                _r += 1
            c += len( cell.children[0] )
        r = len( cell.children )
        c = 0
    chained.sort()
    for _, _, quadrant in chained:
        yield quadrant

