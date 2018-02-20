import os
import subprocess
import pickle
import tempfile
import copy

import Config
import core.TOS as TOS
from core.expression import Symbol
from core.prop_to_queryfunc import prop_to_func as p2f
from core.prop_to_queryfunc import propagate_properties
import core.properties as properties

sizes = ["m", "n", "p", "q", "r"]
opnames = ["A", "B", "C", "D", "E" "F"]

def rec_instance( equation ):
    lhs, rhs = equation.get_children()
    ops_in_lhs = [node for node in lhs.iterate_preorder() if isinstance(node, Symbol)]
    ops_in_rhs = [node for node in rhs.iterate_preorder() if isinstance(node, Symbol)]
    # Temporary to replace entire input expression on rhs
    temp = Symbol("T" + str(TOS.new_temp()))
    temp.set_property(properties.INPUT)
    propagate_properties(rhs, temp)
    temp.size = rhs.get_size()
    temp.st_info = ("", temp)

    # all operands (including temp)
    operands = [ node for node in equation.iterate_preorder() if isinstance(node, Symbol) ] + [temp]

    # rename sizes
    orig_sizes = []
    for op in operands:
        m,n = op.get_size()
        if m not in orig_sizes: orig_sizes.append(m)
        if n not in orig_sizes: orig_sizes.append(n)
    map_sizes = dict((str(orig),new) for orig,new in zip(orig_sizes, sizes))

    # prepare declaration of operands: first declare inputs, then outputs
    to_declare_inp = []
    to_declare_out = []
    for op in operands:
        if op in to_declare_inp or op in to_declare_out or (op in ops_in_rhs and op not in ops_in_lhs):
            continue
        if op.isInput():
            to_declare_inp.append(op)
        else:
            to_declare_out.append(op)
    to_declare = to_declare_inp + to_declare_out

    # rename operands
    map_opnames = dict([(op.name, new) for op,new in zip(to_declare,opnames)])

    # Generate Cl1ck program
    tmp_id, tmp_path = tempfile.mkstemp(text=True, dir="OUTPUT/")
    os.close(tmp_id)
    tmp_name = os.path.basename(tmp_path)
    program_name = "f" + tmp_name
    with open(tmp_path, "w") as tmp_file:
        print("program %s" % program_name, file=tmp_file)
        for op in to_declare:
            t = "Matrix" # [FIXME] Assumes matrices
            m, n = op.get_size()
            m = map_sizes[str(m)]
            n = map_sizes[str(n)]
            io = "Input" if op.isInput() else "Output"
            props = [p for p in op.get_properties() if p not in ["Input", "Output"]]
            if props:
                props = ", " + ", ".join(props)
            else:
                props = ""
            if op.st_info[1] == op or io == "Input":
                st = ""
            else:
                ow = op.st_info[1]
                if ow in ops_in_rhs and ow.get_size() == op.get_size():
                    st = ", overwrites(%s)" % map_opnames[temp.name]
                else:
                    raise Exception

            print("\t%s %s(%s,%s) <%s%s%s>;" % (t, map_opnames[str(op)], m,n, io, props, st), file=tmp_file)

        new_eq = copy.deepcopy(equation)
        new_eq.children[1] = temp
        new_eq_str = new_eq.to_math()
        for op in ops_in_lhs+[temp]:
            new_eq_str = new_eq_str.replace(op.name, map_opnames[op.name])
        print("\n\t" + new_eq_str + ";", file=tmp_file)

    # temp name can be reused
    TOS.push_back_temp( )

    # Run the new instance of click
    subprocess.call("./AlgoGen %s %s" % (tmp_path, Config.unparse_args()), shell=True)

    patterns = list(load("OUTPUT/%s_patterns" % program_name))
    pmes = list(load("OUTPUT/%s_pmes" % program_name))
    md = list(load("OUTPUT/%s_metadata" % program_name))

    # Remove input program file
    os.remove(tmp_path)

    return (md[0], patterns, pmes)

def load(path):
    with open(path, "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break
