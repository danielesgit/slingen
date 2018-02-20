U: triangular<@m, u, in>;
A: matrix<@m, @n, inout>;

A = ldiv_uni_ow_opt(@m, @n; U, A);
