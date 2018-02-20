program sylv_lup_ow
    Matrix L(m,m) <Input, LowerTriangular>;
    Matrix U(n,n) <Input, UpperTriangular>;
    Matrix C(m,n) <Input>;
    Matrix X(m,n) <Output, overwrites(C)>;

    L * X + X * U = C;
