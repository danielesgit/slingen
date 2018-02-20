L: triangular<@m, l, in>;
A: matrix<@m, @n, inout>;

A = ldiv_lni_ow_opt(@m, @n; L, A);
