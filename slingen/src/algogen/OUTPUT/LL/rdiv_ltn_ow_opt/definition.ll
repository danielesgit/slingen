L: triangular<@n, l, in>;
A: matrix<@m, @n, inout>;

A = rdiv_ltn_ow_opt(@m, @n; L, A);
