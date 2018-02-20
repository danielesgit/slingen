U0: triangular<@m0, u, in>;
M7: matrix<@m0, @m2, inout>;

M7 = Assign_Mul_UpperTriangular_SquaredMatrix_SquaredMatrix_opt(@m0, @m2; U0, M7);
