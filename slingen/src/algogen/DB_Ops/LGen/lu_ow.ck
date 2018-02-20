program LU_ow
    Matrix A(m,m) <Input>;
    Matrix L(m,m) <Output, LowerTriangular, ImplicitUnitDiagonal, Non-singular, overwrites(A)>;
    Matrix U(m,m) <Output, UpperTriangular, Non-singular, overwrites(A)>;

    L * U = A;
