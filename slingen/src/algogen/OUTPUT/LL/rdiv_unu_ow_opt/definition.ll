U: triangular<@n, u, in>;
A: matrix<@m, @n, inout>;

A = rdiv_unu_ow_opt(@m, @n; U, A);
