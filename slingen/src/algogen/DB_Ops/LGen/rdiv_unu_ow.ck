program rdiv_unu_ow
    Matrix U(n,n) <Input, UpperTriangular, Non-singular, UnitDiagonal>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output, overwrites(A)>;

    B * U = A;
