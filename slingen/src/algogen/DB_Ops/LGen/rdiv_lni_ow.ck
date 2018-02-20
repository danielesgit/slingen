program rdiv_lni_ow
    Matrix L(n,n) <Input, LowerTriangular, Non-singular, ImplicitUnitDiagonal>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output, overwrites(A)>;

    B * L = A;
