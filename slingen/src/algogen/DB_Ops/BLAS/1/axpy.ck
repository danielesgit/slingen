program Axpy
    Scalar alpha <Input>;
    Vector x(n)  <Input>;
    Vector y(n)  <Input>;
    Vector z(n)  <Output, overwrites(y)>;

    z = alpha * x + y;
