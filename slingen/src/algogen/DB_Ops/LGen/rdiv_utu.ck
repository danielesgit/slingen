program rdiv_utu
    Matrix U(n,n) <Input, UpperTriangular, Non-singular, UnitDiagonal>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output>;

    B * trans(U) = A;
