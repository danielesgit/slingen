L: triangular<@m, l, in>;
A: matrix<@m, @n, inout>;

A = ldiv_lnu_ow_opt(@m, @n; L, A);
