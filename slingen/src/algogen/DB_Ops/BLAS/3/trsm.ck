program Trsm
    Matrix A(m,m) <Input, LowerTriangular, Non-singular>;
    Matrix B(m,n) <Input>;
    Matrix X(m,n) <Output, overwrites(B)>;

    A * X = B;
