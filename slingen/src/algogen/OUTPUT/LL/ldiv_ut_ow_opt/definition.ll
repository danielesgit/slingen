A: matrix<@m, @n, inout>;
U: triangular<@m, u, in>;

A = ldiv_ut_ow_opt(@m, @n; A, U);
