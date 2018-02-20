program ldiv_uti
    Matrix U(m,m) <Input, UpperTriangular, Non-singular, ImplicitUnitDiagonal>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output>;

    trans(U) * B = A;
