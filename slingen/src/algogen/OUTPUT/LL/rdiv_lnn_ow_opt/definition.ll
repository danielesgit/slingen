L: triangular<@n, l, in>;
A: matrix<@m, @n, inout>;

A = rdiv_lnn_ow_opt(@m, @n; L, A);
