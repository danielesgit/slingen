U0: triangular<@m0, u, in>;
v3: matrix<@m0, @m2, inout>;

v3 = Assign_Mul_UpperTriangular_Matrix_Matrix_opt(@m0, @m2; U0, v3);
