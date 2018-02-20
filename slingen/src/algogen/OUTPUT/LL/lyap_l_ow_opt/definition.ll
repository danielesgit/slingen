L: triangular<@m, l, in>;
C: symmetric<@m, l, inout>;

C = lyap_l_ow_opt(@m, @m; L, C);
