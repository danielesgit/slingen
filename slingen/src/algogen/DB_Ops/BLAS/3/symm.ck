program Symm
    Scalar alpha  <Input>;
    Matrix A(m,m) <Input, Symmetric, LowerStorage>;
    Matrix B(m,n) <Input>;
    Scalar beta   <Input>;
    Matrix C(m,n) <Input>;
    Matrix D(m,n) <Output, overwrites(C)>;

    D = alpha * A * B + beta * C;
