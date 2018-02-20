program rdiv_lnu
    Matrix L(n,n) <Input, LowerTriangular, Non-singular, UnitDiagonal>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output>;

    B * L = A;
