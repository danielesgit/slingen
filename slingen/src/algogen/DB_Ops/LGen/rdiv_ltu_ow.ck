program rdiv_ltu_ow
    Matrix L(n,n) <Input, LowerTriangular, Non-singular, UnitDiagonal>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output, overwrites(A)>;

    B * trans(L) = A;
