U: triangular<@n, u, in>;
A: matrix<@m, @n, inout>;

A = rdiv_utu_ow_opt(@m, @n; U, A);
