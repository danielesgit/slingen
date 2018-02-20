program ldiv_lti_ow
    Matrix L(m,m) <Input, LowerTriangular, Non-singular, ImplicitUnitDiagonal>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output, overwrites(A)>;

    trans(L) * B = A;
