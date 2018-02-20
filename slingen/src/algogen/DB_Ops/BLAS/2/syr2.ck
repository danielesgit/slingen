program Syr2
    Scalar alpha  <Input>;
    Vector x(m)   <Input>;
    Vector y(m)   <Input>;
    Scalar beta   <Input>;
    Matrix A(m,m) <Input, Symmetric, LowerStorage>;
    Matrix B(m,m) <Output, Symmetric, LowerStorage, overwrites(A)>;

    B = alpha * x * trans(y) + alpha * y * trans(x) + beta * A;
