program ldiv_unu
    Matrix U(m,m) <Input, UpperTriangular, Non-singular, UnitDiagonal>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output>;

    U * B = A;
