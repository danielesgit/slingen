program rdiv_ltu
    Matrix L(n,n) <Input, LowerTriangular, Non-singular, UnitDiagonal>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output>;

    B * trans(L) = A;
