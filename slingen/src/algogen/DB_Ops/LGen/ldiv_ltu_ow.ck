program ldiv_ltu_ow
    Matrix L(m,m) <Input, LowerTriangular, Non-singular, UnitDiagonal>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output, overwrites(A)>;

    trans(L) * B = A;
