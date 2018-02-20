#!/bin/bash

# Path to python2.7 and python3.5. E.g., 
#export PYTHON2BIN=/usr/bin/python2.7
#export PYTHON3BIN=/usr/bin/python3.5
export PYTHON2BIN=
export PYTHON3BIN=

# Path to python2.7 include folder. E.g., 
#export PYTHON2INC=/usr/include/python2.7
export PYTHON2INC=

# Uncomment and add path to libpython2.7 in case it's not available in (LD_)LIBRARY_PATH
#export PYTHON2LIB=

export LIBRARY_PATH=$LIBRARY_PATH:$(readlink -f libs/lib):$PYTHON2LIB
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(readlink -f libs/lib):$PYTHON2LIB

# Uncomment and add paths to:
#Intel MKL (in case the variable is not already defined). E.g.,
#export MKLROOT=/opt/intel/compilers_and_libraries_2016.2.181/linux/mkl

#Eigen 3.3.4. Available at eigen.tuxfamily.org
#E.g., assuming Eigen folder is in /opt/include/eigen
#export EIGENROOT=/opt/include/eigen

#RECSY (also requires SLICOT). Available at www8.cs.umu.se/~isak/recsy/#Download
#E.g., Assuming both librecsy.a and slicot.a are /opt/lib
#export RECSYROOT=/opt/lib
#export SLICOTROOT=/opt/lib

#ReLAPACK. Available at github.com/HPAC/ReLAPACK.
#E.g., assuming librelapack.a is available in /opt/lib
#export RELAPACKROOT=/opt/lib

#clang++ + Polly. Polly is available at polly.llvm.org/get_started.html.
#E.g.,
#export POLLYROOT=/opt/polly/llvm_build/bin
