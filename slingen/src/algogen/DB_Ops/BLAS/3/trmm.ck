program Trmm
    Scalar alpha  <Input>;
    Matrix A(m,m) <Input, LowerTriangular>;
    Matrix B(m,n) <Input>;
    Matrix D(m,n) <Output, overwrites(B)>;

    D = alpha * A * B;
