program Trmv
    Scalar alpha  <Input>;
    Matrix A(m,m) <Input, LowerTriangular>;
    Vector x(m)   <Input>;
    Scalar beta   <Input>;
    Vector y(m)   <Input>;
    Vector z(m)   <Output, overwrites(y)>;

    z = alpha * A * x + beta * y;
