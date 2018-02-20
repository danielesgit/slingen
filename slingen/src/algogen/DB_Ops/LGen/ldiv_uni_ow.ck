program ldiv_uni_ow
    Matrix U(m,m) <Input, UpperTriangular, Non-singular, ImplicitUnitDiagonal>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output, overwrites(A)>;

    U * B = A;
