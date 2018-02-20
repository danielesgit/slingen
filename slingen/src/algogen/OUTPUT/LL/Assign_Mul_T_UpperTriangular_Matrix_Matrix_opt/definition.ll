U0: triangular<@m0, u, in>;
v1: matrix<@m0, @m2, inout>;

v1 = Assign_Mul_T_UpperTriangular_Matrix_Matrix_opt(@m0, @m2; U0, v1);
