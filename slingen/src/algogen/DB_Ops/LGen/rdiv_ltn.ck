program rdiv_ltn
    Matrix L(n,n) <Input, LowerTriangular, Non-singular>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output>;

    B * trans(L) = A;
