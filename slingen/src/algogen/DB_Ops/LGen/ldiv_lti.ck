program ldiv_lti
    Matrix L(m,m) <Input, LowerTriangular, Non-singular, ImplicitUnitDiagonal>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output>;

    trans(L) * B = A;
