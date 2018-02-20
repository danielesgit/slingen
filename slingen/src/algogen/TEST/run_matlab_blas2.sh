#!/usr/bin/env bash
for op_def in `ls DB_Ops/BLAS/2/`
do
    ./Cl1ck --matlab --opt DB_Ops/BLAS/2/$op_def || exit
done
