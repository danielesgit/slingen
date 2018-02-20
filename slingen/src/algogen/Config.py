# Command-line options
options = None

# FLAME LAB directory
#flame_lab_dir = "set/path/to/.../Cl1ck/TEST/FLAME_LAB"

# Directories for code generation
matlab_dir = "OUTPUT/MATLAB/"
ll_dir = "OUTPUT/LL/"
#latex_dir  = "OUTPUT/TEX/"

def unparse_args():
    args = []
    if options.latex:
        args.append("--latex")
    if options.matlab:
        args.append("--matlab")
    if options.ll:
        args.append("--ll")
    if options.opt:
        args.append("--opt")
    args.append("--sizes %s" % options.sizes)
    return " ".join(args)
