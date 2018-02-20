program ldiv_lni_ow
    Matrix L(m,m) <Input, LowerTriangular, Non-singular, ImplicitUnitDiagonal>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output, overwrites(A)>;

    L * B = A;
