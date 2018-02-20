#!/usr/bin/env bash

for dir in Cholesky tril_inv sylv_lup lyap_l
do
    cd OUTPUT/MATLAB/$dir
    /mnt/MATLAB/R2016a/bin/matlab -nodesktop -nodisplay -r test
    cd -
done
