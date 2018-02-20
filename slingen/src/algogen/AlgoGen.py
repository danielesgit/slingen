#!/usr/bin/env python3

import sys, os
import argparse

from FrontEnd.syntax import cl1ckParser
from FrontEnd.semantics import cl1ckSemantics

import core.TOS as TOS
import Config

# Parse arguments
parser = argparse.ArgumentParser(description="Generation of loop-based algorithms.")
parser.add_argument("operations", nargs='+', help="Relative path to the definition of the input operation")
parser.add_argument("--latex", default=False, action="store_true", \
                    help="Generates LaTeX code to document the generated algorithms in FLAME notation")
parser.add_argument("--matlab", default=False, action="store_true", \
                    help="Generates Matlab code for each algorithm and test drivers")
parser.add_argument("--ll", default=False, action="store_true", \
                    help="Generates LL code")
parser.add_argument("--sizes", type=str, choices=["multiple-of-nu", "non-multiple-of-nu"], default="non-multiple-of-nu",
                    help="Specifies whether to assume sizes as multiples of vector size or not")
#parser.add_argument("--flamec", default=False, action="store_true", \
                    #help="Generates FLAME C code")
parser.add_argument("--opt", default=False, action="store_true", \
                    help="Generates optimized code (copy propagation, ...)")
Config.options = parser.parse_args()

from Operation import Operation

# Proceed to generate algorithms/code
for operation in Config.options.operations:
    TOS._TOS.clear()
    TOS._TOE.reset()
    with open( operation, "r" ) as f:
        parser = cl1ckParser()
        try:
            ast = parser.parse( f.read(),
                                filename = operation,
                                rule_name = "program",
                                semantics = cl1ckSemantics() )
        except Exception as e:
            print('Error while parsing "{}":'.format(operation))
            #lninfo = parser._buffer.line_info()
            #print('Line {0.line}:\t{0.text}'.format(lninfo))
            #print('              \t' + ' ' * lninfo.col + '^')
            print(e)
            sys.exit(1)

        op_name = ast.header.name
        decls = ast.declarations
        eqs = ast.equations
        #
        op_syms = decls
        overwrite = [(op.st_info[1], op) for op in op_syms if op.st_info[1] != op]
        operation = Operation( op_name, op_syms, eqs, overwrite )
        operation.run()
