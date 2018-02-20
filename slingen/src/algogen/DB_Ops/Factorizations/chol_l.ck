program Cholesky
    Matrix A(m,m) <Input, Symmetric, SPD, LowerStorage>;
    Matrix L(m,m) <Output, LowerTriangular, Non-singular, overwrites(A)>;

    L * trans(L) = A;
