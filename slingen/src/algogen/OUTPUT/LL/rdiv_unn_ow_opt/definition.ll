U: triangular<@n, u, in>;
A: matrix<@m, @n, inout>;

A = rdiv_unn_ow_opt(@m, @n; U, A);
