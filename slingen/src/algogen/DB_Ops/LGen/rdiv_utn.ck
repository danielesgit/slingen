program rdiv_utn
    Matrix U(n,n) <Input, UpperTriangular, Non-singular>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output>;

    B * trans(U) = A;
