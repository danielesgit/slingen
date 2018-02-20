program lyap_l
    Matrix L(m,m) <Input, LowerTriangular>;
    Matrix C(m,m) <Input, Symmetric, LowerStorage>;
    Matrix X(m,m) <Output, Symmetric, LowerStorage, overwrites(C)>;

    L * X + X * trans(L) = C;
