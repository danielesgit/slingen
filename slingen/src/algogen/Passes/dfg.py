import copy

from core.expression import BaseExpression, Equal, Symbol, Predicate
from core.functional import contains, replace, RewriteRule, Replacement
import PredicateMetadata as pm

from Passes import lpla
from Passes.alg_passes import _checkPredicateOverwrite

class dfg_node( object ):
    def __init__( self, statements, leader_idx ):
        self.statements = statements
        self.leader = leader_idx
        self.successors = []
        self.next_use = None
        #
        self.visited = False

    def add_successor( self, node ):
        self.successors.append( node )

    def checkPredicateOverwrite( self ):
        new_sts = []
        for st in self.statements:
            if not isinstance( st, Equal ):
                new_sts.append( st )
                continue
            new_sts.extend( _checkPredicateOverwrite( st ) )
        self.statements = new_sts

    def opt_remove_self_assignments( self ):
        new_st = []
        for st in self.statements:
            if isinstance( st, Equal ):
                lhs, rhs = st.children
                lhs = lhs.children
                if len(lhs) == 1 and isinstance( st.rhs(), Symbol ):
                    try: # [CHECK] Temporaries. All of them?
                        if lhs[0].st_info == rhs.st_info:
                            continue
                        if lhs[0].name == rhs.st_info[1].name:
                            continue
                        if lhs[0].st_info[1].name == rhs.name:
                            continue
                    except AttributeError:
                        print(" [WARNING] No storage info:", lhs[0], rhs )
                        pass
            new_st.append( st )
        self.statements = new_st

    def opt_copy_propagation( self ):
        for i,st in enumerate(self.statements):
            if isinstance( st, Equal ):
                lhs, rhs = st.children
                lhs = lhs.children
                if len(lhs) == 1 and lhs[0].isTemporary() and isinstance( st.rhs(), Symbol ):
                    for oth_st in self.statements[i+1:]:
                        if not isinstance( oth_st, Equal ): #[CHECK] Careful. Not the case, but generally speaking could be some part/repart
                            continue
                        oth_lhs, oth_rhs = oth_st.lhs(), oth_st.rhs()
                        if contains( oth_rhs, lhs[0] ):
                        #\ and not (isinstance( oth_rhs, Predicate ) and pm.DB[oth_rhs.name].overwrite): #[FIXME] Can be less restrictive
                            new_rhs = replace( oth_rhs, [RewriteRule( lhs[0], Replacement(rhs) )] )
                            oth_st.children[1] = new_rhs
                        if oth_lhs.children[0] == lhs[0] or oth_lhs == rhs:
                            break

    def opt_backward_copy_propagation( self ):
        for i,st in enumerate(self.statements):
            if isinstance( st, Equal ):
                lhs, rhs = st.children
                lhs = lhs.children
                if len(lhs) == 1 and isinstance( lhs[0], Symbol ) and rhs.isTemporary():
                    killed = []
                    for oth_st in self.statements[i-1::-1]:
                        if not isinstance( oth_st, Equal ):
                            break # declare, part, repart, ... no more assignments towards the beginning of the block
                        oth_lhs, oth_rhs = oth_st.lhs(), oth_st.rhs()
                        if contains( oth_lhs, rhs ):
                            if len( oth_lhs.children ) > 1:
                                break
                            if any([ contains( oth_rhs, k ) for k in killed ]):
                                break
                            #if isinstance( oth_rhs, Predicate ) and pm.DB[oth_rhs.name].overwrite:
                                #print( "Overwrites" )
                                #break
                            if contains( oth_rhs, oth_lhs.children[0] ):
                                break
                            st.children[1] = oth_rhs
                            break
                        killed.extend( oth_lhs.children )
                        killed.extend( [ch.st_info[1] for ch in oth_lhs.children] )

    def opt_dead_code_elimination( self ):
        new_st = []
        for st, next_use in zip(self.statements, self.next_use):
            if isinstance( st, Equal ):
                if next_use == [] and not any([l.isOutput() for l in st.lhs()]):
                    #print(" Dead:", st )
                    continue
            new_st.append( st )
        self.statements = new_st

    def analysis_next_use( self ):
        self.next_use = []
        for i, cur_st in enumerate(self.statements):
            self.next_use.append( [] )
            if isinstance( cur_st, lpla.declare ):
                continue
            dead = False
            for j, oth_st in enumerate(self.statements[i+1:], start=i+1):
                if isinstance( oth_st, lpla.declare ):
                    continue
                for op in cur_st.lhs():
                    if isinstance( oth_st.rhs(), BaseExpression ):
                        if contains( oth_st.rhs(), op ):
                            self.next_use[-1].append( (self, j) )
                            break
                    else:
                        #if op in oth_st.rhs():
                        try:
                            _ = op.st_info
                            if any([ op.st_info[1] == other for other in oth_st.rhs()]):
                                self.next_use[-1].append( (self, j) )
                                break
                        except AttributeError:
                            if op in oth_st.rhs():
                                self.next_use[-1].append( (self, j) )
                                break

                #[FIXME] For now, one single output
                for op in cur_st.lhs():
                    if op in oth_st.lhs():
                        dead = True
                        break
                if dead:
                    break
            if not dead and self.successors:
                for op in cur_st.lhs():
                    self.graph.clear_visited()
                    for n in self.successors:
                        for occurrence in n.analysis_next_use_var( op ):
                            self.next_use[-1].append( occurrence )       

    def analysis_next_use_var( self, var ):
        if self.visited:
            return
        self.visited = True
        #
        dead = False
        for i, st in enumerate(self.statements):
            if isinstance( st, lpla.declare ):
                continue
            if isinstance( st.rhs(), BaseExpression ):
                #rhs_symbols = [n for n in st.rhs().iterate_preorder() if isinstance(n, Symbol)]
                #if any([ var.st_info[1] == n.st_info[1] for n in rhs_symbols ]):
                if contains( st.rhs(), var ):
                    yield (self, i)
            else:
                if var in st.rhs():
                    yield (self, i)
            #[FIXME] For now, one single output
            if isinstance( st.lhs(), BaseExpression ):
                if contains( st.lhs(), var ):
                    dead = True
                    #yield None
                    return
            else:
                for l in st.lhs():
                    if var == l:
                        dead = True
                        #yield None
                        return
        if not dead:
            for n in self.successors:
                for occurrence in n.analysis_next_use_var( var ):
                    yield occurrence


    def __repr__( self ):
        if self.visited: 
            return ""
        self.visited = True
        succ = [str(s) for s in self.successors]
        this = ["[%d] Successors: %s" % (self.leader, ", ".join([str(s.leader) for s in self.successors]))]
        return "\n".join(succ+this)

    def __eq__( self, other ):
        return len(self.statements) == len(other.statements) and \
                all([ s1 == s2 for s1,s2 in zip(self.statements, other.statements) ])

class dfg( object ):
    def __init__( self ):
        self.nodes = []
        self.root = None

    def clear_visited( self ):
        for node in self.nodes:
            node.visited = False

    def checkPredicateOverwrite( self ):
        for node in self.nodes:
            node.checkPredicateOverwrite()

    def opt_remove_self_assignments( self ):
        for node in self.nodes:
            node.opt_remove_self_assignments()

    def opt_copy_propagation( self ):
        for node in self.nodes:
            node.opt_copy_propagation()

    def opt_backward_copy_propagation( self ):
        for node in self.nodes:
            node.opt_backward_copy_propagation()

    def opt_dead_code_elimination( self ):
        for node in self.nodes:
            node.opt_dead_code_elimination()

    def analysis_next_use( self ):
        for node in self.nodes:
            node.analysis_next_use()

    def __repr__( self ):
        ret = ["nodes: " + str(len(self.nodes))]
        ret.append("")
        for n in self.nodes:
            for st in n.statements:
                ret.append( str(st) )
            ret.append("")
        return "\n".join(ret)

    def __eq__( self, other ): # just for the sake of code generation, not general "eq"
        if len(self.nodes) != len(other.nodes):
            return False
        for n1, n2 in zip(self.nodes, other.nodes):
            if len(n1.statements) != len(n2.statements):
                return False
            for st1, st2 in zip(n1.statements, n2.statements):
                if st1 != st2:
                    return False
        return True
