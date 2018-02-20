import inspect # This might get nasty. 
               # Hope my future me does not have to regret this xD
import copy
import itertools

from core.expression import BaseExpression, Sequence
import core.exceptions as myexc

from core.TOS import _TOS as TOS

class _Eval( object ):
    def __init__( self, to_eval ):
        self.to_eval = to_eval

    def _eval( self, match_dict, _globals, _locals ):
        # [TODO] CAREFUL!!! strings are deprecated
        if isinstance( self.to_eval, str ):
            if self.to_eval == "":
                return True
            #print( "Usage of strings as constraints/replacements is deprecated", self.to_eval )
            env_locals = dict( [(k,v) for k,v in _locals.items()] )
            env_locals.update(match_dict)
            env_globals = dict( [(k,v) for k,v in _globals.items()] )
            try:
                return eval( self.to_eval, env_globals, env_locals )
            # Comprehension lists and eval break things...
            except NameError as e:
                env_globals.update(match_dict)
                #var = e.message.split("'")[1]
                #var = str(e).split("'")[1]
                #if var in TOS:
                    #env_locals[ var ] = TOS.get_operands()[ var ]
                env_locals.update( dict([ (k,v[0]) for k,v in TOS.items() if k not in env_locals ]) )
                return eval( self.to_eval, env_globals, env_locals)
            except TypeError as e:
                print(e)
                print( self.to_eval )
                raise e
        elif isinstance( self.to_eval, BaseExpression ):
            return self.to_eval
        elif inspect.isfunction( self.to_eval ):
            return self.to_eval( match_dict )
        else:
            print(self.to_eval.__class__)
            raise TypeError #, self.to_eval.__class__

class Constraint( _Eval ):
    pass

class Replacement( _Eval ):
    pass

class RewriteRule( object ):
    def __init__( self, pattern, replacement ):
        self.pattern = pattern
        self.replacement = replacement

    def __iter__( self ):
        yield self.pattern
        yield self.replacement

    def __repr__( self ):
        if isinstance( self.pattern, BaseExpression ):
            pattern = self.pattern
            constraint = ""
        else:
            pattern, constraint = self.pattern
            constraint = constraint.to_eval
        return "%s /; %s -> %s" % (pattern, constraint, self.replacement.to_eval)

# Pattern matching context
class PM_context( object ):
    def __init__( self ):
        self.stack_patt = []
        self.stack_expr = []
        self.match = {}

    def __copy__( self ):
        cls = self.__class__
        new = cls.__new__(cls)
        #new = PM_context()
        new.stack_patt = self.stack_patt[:]
        new.stack_expr = self.stack_expr[:]
        new.match = self.match.copy()
        return new

def match( expr, pattern, caller_globals=None, caller_locals=None ):
    if isinstance( pattern, BaseExpression ):
        patt_expr = pattern
        #constraint = Constraint("True")
        constraint = Constraint( lambda d: True )
    else:
        patt_expr, constraint = pattern

    ctx = PM_context()
    expr_seq = Sequence( [expr] )
    patt_seq = Sequence( [patt_expr] )
    #ctx.stack_expr.append( expr )
    #patt.match( ctx )
    ctx.stack_expr.append( expr_seq )
    # needed for eval to succeed
    if caller_globals == None:
        caller_globals = inspect.stack()[1][0].f_globals
        #caller_globals = {}
    if caller_locals == None:
        caller_locals = inspect.stack()[1][0].f_locals
        #caller_locals = {}
    for match in patt_seq.match( ctx ):
        if constraint._eval( match, caller_globals, caller_locals ):
            yield match
        #else:
            #print( "Match %s failed" % match )

def matchq( expr, patt ):
    caller_globals = inspect.stack()[1][0].f_globals
    caller_locals = inspect.stack()[1][0].f_locals
    for m in match( expr, patt, caller_globals, caller_locals ):
        return True
    return False

# [TODO] Try to write replace_all in terms of replace
def replace( expr, rewrite_rules ):
    # needed for eval to succeed
    caller_globals = inspect.stack()[1][0].f_globals
    caller_locals = inspect.stack()[1][0].f_locals
    #caller_globals = {}
    #caller_locals = {}
    #
    stack = [expr._postorder_stack()] # ( node, (parent,pos), ((node, ()), ...) )
    #stack = [expr._postorder_stack()] # ( node, (node, ()) )
    #positions = dict( [(node, pos) for node, pos in expr._preorder_position()] )
    while len(stack) > 0:
        #node, children = stack.pop()
        node, (parent,pos), children = stack.pop()
        any_rule_applied = False
        for pattern, replacement in rewrite_rules:
            for _m in match( node, pattern, caller_globals, caller_locals ):
                #parent, pos = positions[ id(node) ]
                evaled_repl = replacement._eval( _m, caller_globals, caller_locals )
                if parent:
                    parent.set_children( pos, evaled_repl )
                else:
                    expr = evaled_repl
                any_rule_applied = True
                #expr._cleanup()
                break
            if any_rule_applied:
                break
        if not any_rule_applied:
            stack.extend( reversed(children) )
        #print( stack )
    expr = expr._cleanup()
    return expr

class dummy():
    def get_head(self):
        return ""

def replace_all( expr, rewrite_rules ):
    # needed for eval to succeed
    caller_globals = inspect.stack()[1][0].f_globals
    caller_locals = inspect.stack()[1][0].f_locals
    #caller_globals = {}
    #caller_locals = {}
    # "Fixed point"
    niters = 0
    keep_replacing = True
    # [TODO] Fixed point
    #last_expr = dummy()
    while keep_replacing:
    #while expr != last_expr:
        #last_expr = expr
        #
        niters += 1
        if niters > myexc.MAX_REPLACEMENT_ITERATIONS:
            raise myexc.MaxReplacementIterationsExceeded
        keep_replacing = False
        stack = [expr._postorder_stack()] # ( node, (parent,pos), ((node, ()), ...) )
        #positions = dict( [(node, pos) for node, pos in expr._preorder_position()] )
        while len(stack) > 0:
            #node, children = stack.pop()
            node, (parent, pos), children = stack.pop()
            any_rule_applied = False
            for pattern, replacement in rewrite_rules:
                for _m in match( node, pattern, caller_globals, caller_locals ):
                    evaled_repl = replacement._eval( _m, caller_globals, caller_locals )
                    if parent:
                        parent.set_children( pos, evaled_repl )
                    else:
                        expr = evaled_repl
                    any_rule_applied = True
                    keep_replacing = True
                    #expr._cleanup()
                    break
                if any_rule_applied:
                    break
            if not any_rule_applied:
                stack.extend( reversed(children) )
        expr = expr._cleanup() # [CHECK] was unindented one level (for chol after/updates to move a minus in times to first argument
    return expr

# depth >= 0
def map_thread( f, iterables, depth ):
    if depth == 0:
        return f(Sequence(iterables))
    else:
        return [ map_thread(f, z, depth-1) for z in zip(*iterables) ]

def contains( expr, subexpr ):
    # needed for eval to succeed
    #caller_globals = inspect.stack()[1][0].f_globals
    #caller_locals = inspect.stack()[1][0].f_locals
    caller_globals = {}
    caller_locals = {}
    for node in expr.iterate_preorder():
        for _ in match( node, subexpr, caller_locals, caller_globals ):
            return True
    return False
