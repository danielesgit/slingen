program ldiv_unn
    Matrix U(m,m) <Input, UpperTriangular, Non-singular>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output>;

    U * B = A;
