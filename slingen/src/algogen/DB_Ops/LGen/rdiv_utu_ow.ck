program rdiv_utu_ow
    Matrix U(n,n) <Input, UpperTriangular, Non-singular, UnitDiagonal>;
    Matrix A(m,n) <Input>;
    Matrix B(m,n) <Output, overwrites(A)>;

    B * trans(U) = A;
