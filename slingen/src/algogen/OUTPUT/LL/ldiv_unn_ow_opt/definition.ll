U: triangular<@m, u, in>;
A: matrix<@m, @n, inout>;

A = ldiv_unn_ow_opt(@m, @n; U, A);
