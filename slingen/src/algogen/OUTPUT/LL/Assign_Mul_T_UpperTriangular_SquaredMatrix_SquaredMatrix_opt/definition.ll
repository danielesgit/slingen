U0: triangular<@m0, u, in>;
M5: matrix<@m0, @m2, inout>;

M5 = Assign_Mul_T_UpperTriangular_SquaredMatrix_SquaredMatrix_opt(@m0, @m2; U0, M5);
