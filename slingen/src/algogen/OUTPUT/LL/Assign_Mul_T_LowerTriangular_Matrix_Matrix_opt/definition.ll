L0: triangular<@m0, l, in>;
t1: matrix<@m0, @m2, inout>;

t1 = Assign_Mul_T_LowerTriangular_Matrix_Matrix_opt(@m0, @m2; L0, t1);
