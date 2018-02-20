program rdiv_uti
    Matrix U(n,n) <Input, UpperTriangular, Non-singular, ImplicitUnitDiagonal>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output>;

    B * trans(U) = A;
