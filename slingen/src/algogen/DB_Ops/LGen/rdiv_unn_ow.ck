program rdiv_unn_ow
    Matrix U(n,n) <Input, UpperTriangular, Non-singular>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output, overwrites(A)>;

    B * U = A;
