program Gemv
    Scalar alpha  <Input>;
    Matrix A(m,n) <Input>;
    Vector x(n)   <Input>;
    Scalar beta   <Input>;
    Vector y(m)   <Input>;
    Vector z(m)   <Output, overwrites(y)>;

    z = alpha * A * x + beta * y;
