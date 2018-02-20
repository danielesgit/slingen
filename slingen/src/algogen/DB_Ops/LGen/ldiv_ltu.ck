program ldiv_ltu
    Matrix L(m,m) <Input, LowerTriangular, Non-singular, UnitDiagonal>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output>;

    trans(L) * B = A;
