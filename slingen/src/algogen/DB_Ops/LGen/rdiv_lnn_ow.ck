program rdiv_lnn_ow
    Matrix L(n,n) <Input, LowerTriangular, Non-singular>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output, overwrites(A)>;

    B * L = A;
