program ldiv_unu_ow
    Matrix U(m,m) <Input, UpperTriangular, Non-singular, UnitDiagonal>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output, overwrites(A)>;

    U * B = A;
