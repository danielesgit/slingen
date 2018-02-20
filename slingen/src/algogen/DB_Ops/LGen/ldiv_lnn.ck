program ldiv_lnn
    Matrix L(m,m) <Input, LowerTriangular, Non-singular>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output>;

    L * B = A;
