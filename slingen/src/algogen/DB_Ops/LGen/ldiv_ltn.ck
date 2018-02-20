program ldiv_ltn
    Matrix L(m,m) <Input, LowerTriangular, Non-singular>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output>;

    trans(L) * B = A;
