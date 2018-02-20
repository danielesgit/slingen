L0: triangular<@m0, l, in>;
y: matrix<@m0, @m2, inout>;

y = Assign_Mul_LowerTriangular_Matrix_Matrix_opt(@m0, @m2; L0, y);
