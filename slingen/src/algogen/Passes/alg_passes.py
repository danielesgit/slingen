import copy

from core.expression import Equal, Predicate, NList, Symbol
from core.functional import replace, RewriteRule, Replacement

import core.TOS as TOS
import PredicateMetadata as pm

# Needed:
#   Metadata/DB for each operation:
#     - overwrite  (posin, posout)
#     - if overwrite to be fixed: register temp as linv temp + sizes/properties
#     

def PassCheckPredicateOverwrite( algorithm ):
    try:
        new_init = []
        for statement in algorithm.init:
            new_init.extend( _checkPredicateOverwrite( statement ) )
        algorithm.init = new_init
    except TypeError:
        pass

    new_updates = []
    for statement in algorithm.updates:
        new_updates.extend( _checkPredicateOverwrite( statement ) )
    algorithm.updates = new_updates

def _checkPredicateOverwrite( statement ):
    lhs = statement.lhs()
    rhs = statement.rhs()
    if not isinstance( rhs, Predicate ):
        rhs_ops = [ node for node in rhs.iterate_preorder() if isinstance( node, Symbol ) ]
        tmp_ops = [ op for op in rhs_ops if op.isTemporary() ]
        if len(tmp_ops) == 1: # [FIXME] Quick and dirty to play with temporaries
            tmp = tmp_ops[0]
            if lhs.children[0].size == tmp.size:
                if not lhs.children[0].isTemporary():
                    overwrites = False
                    for op in rhs_ops:
                        try:
                            overwrites = lhs.children[0].st_info[1]==op.st_info[1]
                        except AttributeError:
                            pass
                        if overwrites: break
                    if not overwrites:
                        statements = []
                        statements.append( Equal([NList(lhs.children), tmp]) )
                        statement.children[1] = replace( copy.deepcopy(rhs), [RewriteRule( tmp, Replacement(lhs.children[0]))] )
                        statements.append( statement )
                        return statements
        else:
            # TRSM 2x2 ...
            pass
        return [statement]
    if not pm.DB[rhs.name].overwrite: # []
        return [statement]

    statements = []
    # [FIXME] Assumes one single operands get overwritten. Will break in the future
    already_copied = []
    for inp, out in pm.DB[rhs.name].overwrite:
        if inp in already_copied:
            continue
        already_copied.append(inp)
        #
        if rhs.children[inp] != lhs.children[out]: # [FIXME] All should have st_into
            try:
                overwrites = lhs.children[out].st_info[1] == rhs.children[inp].st_info[1]
            except AttributeError:
                overwrites = False
            if overwrites:
                statements.append( statement ) #[FIXME] Gosh...
                continue
            inpop = rhs.children[inp]
            outop = lhs.children[out]
            if inpop.isTemporary() or inpop.isInput():
                # if multiple outputs overwrite input (e.g., LU)
                if len([ o for i,o in pm.DB[rhs.name].overwrite if i == inp ]) > 1:
                    try:
                        outop = TOS._TOS[outop.st_info[1].name][0] # LU  (ABR = T3; [LBR,UBR] = LU(ABR))
                    except:
                        pass
                    outop.st_info = (None, outop)
                #
                statements.append( Equal([NList([outop]), inpop]) )
                rhs.children[inp] = outop
                statements.append( statement )
            else:
                lhs.children[out] = rhs.children[inp]
                statements.append( statement )
                statements.append( Equal([NList([inpop]), outop]) )
        else:
            statements.append( statement )
    return statements
