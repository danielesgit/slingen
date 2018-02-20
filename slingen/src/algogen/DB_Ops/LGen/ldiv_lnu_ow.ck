program ldiv_lnu_ow
    Matrix L(m,m) <Input, LowerTriangular, Non-singular, UnitDiagonal>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output, overwrites(A)>;

    L * B = A;
