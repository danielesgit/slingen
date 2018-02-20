L: triangular<@m, l, in>;
C: matrix<@m, @n, inout>;
U: triangular<@n, u, in>;

C = sylv_lup_ow_opt(@m, @n; L, C, U);
