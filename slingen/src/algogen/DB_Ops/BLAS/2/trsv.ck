program Trsv
    Matrix A(m,m) <Input, LowerTriangular, Non-singular>;
    Vector y(m)   <Input>;
    Vector x(m)   <Output, overwrites(y)>;

    A * x = y;
