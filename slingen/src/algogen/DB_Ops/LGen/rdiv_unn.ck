program rdiv_unn
    Matrix U(n,n) <Input, UpperTriangular, Non-singular>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output>;

    B * U = A;
