L: triangular<@m0, l, in>;
C: symmetric<@m0, l, inout>;

C = Assign_Add_Mul_LowerTriangular_Symmetric_Mul_Symmetric_T_LowerTriangular_Symmetric_opt(@m0, @m0; L, C);
