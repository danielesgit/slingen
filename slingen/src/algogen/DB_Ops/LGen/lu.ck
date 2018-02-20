program LU
    Matrix A(m,m) <Input>;
    Matrix L(m,m) <Output, LowerTriangular, UnitDiagonal, Non-singular>;
    Matrix U(m,m) <Output, UpperTriangular, Non-singular>;

    L * U = A;
