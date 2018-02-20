program ldiv_un_ow
    Matrix U(m,m) <Input, UpperTriangular, Non-singular>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output, overwrites(A)>;

    U * B = A;
