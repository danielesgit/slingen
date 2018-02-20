L: triangular<@m, l, in>;
A: matrix<@m, @n, inout>;

A = ldiv_lti_ow_opt(@m, @n; L, A);
