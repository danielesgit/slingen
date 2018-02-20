program Ger
    Scalar alpha  <Input>;
    Vector x(m)   <Input>;
    Vector y(n)   <Input>;
    Scalar beta   <Input>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output, overwrites(A)>;

    B = alpha * x * trans(y) + beta * A;
