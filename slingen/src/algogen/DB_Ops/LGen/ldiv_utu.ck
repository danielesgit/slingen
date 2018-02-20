program ldiv_utu
    Matrix U(m,m) <Input, UpperTriangular, Non-singular, UnitDiagonal>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output>;

    trans(U) * B = A;
