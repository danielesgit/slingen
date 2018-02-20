program rdiv_lnn
    Matrix L(n,n) <Input, LowerTriangular, Non-singular>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output>;

    B * L = A;
