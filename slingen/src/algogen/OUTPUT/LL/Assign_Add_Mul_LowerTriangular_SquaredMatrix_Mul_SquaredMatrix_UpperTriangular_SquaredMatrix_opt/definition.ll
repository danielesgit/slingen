L: triangular<@m0, l, in>;
C: matrix<@m0, @m2, inout>;
U: triangular<@m2, u, in>;

C = Assign_Add_Mul_LowerTriangular_SquaredMatrix_Mul_SquaredMatrix_UpperTriangular_SquaredMatrix_opt(@m0, @m2; L, C, U);
