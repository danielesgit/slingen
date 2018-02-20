#!/usr/bin/env bash
for op_def in `ls DB_Ops/BLAS/1/*.ck`
do
    echo $op_def
    base=`basename $op_def .ck`
    base="$(tr '[:lower:]' '[:upper:]' <<< ${base:0:1})${base:1}"
    #echo $base
    cd OUTPUT/MATLAB/$base
    /mnt/MATLAB/R2016a/bin/matlab -nodesktop -nodisplay -r test
    cd -
done
