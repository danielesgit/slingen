L: triangular<@m, l, in>;
A: matrix<@m, @n, inout>;

A = ldiv_lnn_ow_opt(@m, @n; L, A);
