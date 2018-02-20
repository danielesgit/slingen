program Sapdot
    Scalar beta  <Output>;
    Scalar alpha <Input>;
    Vector x(n)  <Input>;
    Vector y(n)  <Input>;

    beta = alpha + trans(x) * y;
