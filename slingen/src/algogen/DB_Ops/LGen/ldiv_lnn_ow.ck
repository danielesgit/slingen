program ldiv_lnn_ow
    Matrix L(m,m) <Input, LowerTriangular, Non-singular>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output, overwrites(A)>;

    L * B = A;
