program ldiv_lnu
    Matrix L(m,m) <Input, LowerTriangular, Non-singular, UnitDiagonal>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output>;

    L * B = A;
