program Dot
    Scalar alpha <Output>;
    Vector x(n)  <Input>;
    Vector y(n)  <Input>;

    alpha = trans(x) * y;
