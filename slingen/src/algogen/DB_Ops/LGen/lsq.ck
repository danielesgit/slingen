program lsq
  Matrix L(m,m) <Input, LowerTriangular, Non-singular>;
  Matrix X(n,m) <Input>;
  Vector v(n) <Input>;
  Vector w(m) <Output>;

  w = inv(L) * trans(X) * v;
