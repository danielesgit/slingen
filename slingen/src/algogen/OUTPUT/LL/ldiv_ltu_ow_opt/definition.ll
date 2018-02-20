L: triangular<@m, l, in>;
A: matrix<@m, @n, inout>;

A = ldiv_ltu_ow_opt(@m, @n; L, A);
