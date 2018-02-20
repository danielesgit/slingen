program Scal
    Scalar alpha <Input>;
    Vector x(n)  <Input>;
    Vector y(n)  <Output, overwrites(x)>;

    y = alpha * x;
