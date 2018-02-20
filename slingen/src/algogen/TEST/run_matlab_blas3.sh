#!/usr/bin/env bash
for op_def in `ls DB_Ops/BLAS/3/*.ck`
do
    #./Cl1ck --matlab --opt DB_Ops/BLAS/3/$op_def || exit
    ./Cl1ck --matlab --opt $op_def || exit
done
