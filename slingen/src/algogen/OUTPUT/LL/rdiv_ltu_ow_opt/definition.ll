L: triangular<@n, l, in>;
A: matrix<@m, @n, inout>;

A = rdiv_ltu_ow_opt(@m, @n; L, A);
