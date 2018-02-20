L: triangular<@n, l, in>;
A: matrix<@m, @n, inout>;

A = rdiv_lti_ow_opt(@m, @n; L, A);
