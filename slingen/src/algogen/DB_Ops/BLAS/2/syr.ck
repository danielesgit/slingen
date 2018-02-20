program Syr
    Scalar alpha  <Input>;
    Vector x(m)   <Input>;
    Scalar beta   <Input>;
    Matrix A(m,m) <Input, Symmetric, LowerStorage>;
    Matrix B(m,m) <Output, Symmetric, LowerStorage, overwrites(A)>;

    B = alpha * x * trans(x) + beta * A;
