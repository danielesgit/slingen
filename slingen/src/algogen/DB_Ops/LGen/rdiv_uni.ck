program rdiv_uni
    Matrix U(n,n) <Input, UpperTriangular, Non-singular, ImplicitUnitDiagonal>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output>;

    B * U = A;
