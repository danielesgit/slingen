program tril_inv_ow
    Matrix L(m,m) <Input, LowerTriangular, Non-singular>;
    Matrix X(m,m) <Output, LowerTriangular, Non-singular, overwrites(L)>;

    X = inv(L);
