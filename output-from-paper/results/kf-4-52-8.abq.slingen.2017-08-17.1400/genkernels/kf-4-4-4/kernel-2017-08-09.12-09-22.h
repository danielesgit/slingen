/*
 * kf_kernel.h
 *
Decl { {'T649': Matrix[T649, (1, 4), GenMatAccess], u'F': SquaredMatrix[F, (4, 4), GenMatAccess], u'H': SquaredMatrix[H, (4, 4), GenMatAccess], 'T660': Matrix[T660, (1, 4), GenMatAccess], u'U0': UpperTriangular[U0, (4, 4), GenMatAccess], u'M5': SquaredMatrix[M5, (4, 4), GenMatAccess], u'P': Symmetric[P, (4, 4), USMatAccess], u'M7': SquaredMatrix[M7, (4, 4), GenMatAccess], u'M6': SquaredMatrix[M6, (4, 4), GenMatAccess], u'v4': Matrix[v4, (4, 1), GenMatAccess], u'M0': SquaredMatrix[M0, (4, 4), GenMatAccess], u'M3': Symmetric[M3, (4, 4), USMatAccess], u'M2': SquaredMatrix[M2, (4, 4), GenMatAccess], u'Y': Symmetric[Y, (4, 4), USMatAccess], u'R': Symmetric[R, (4, 4), USMatAccess], u'U': UpperTriangular[U, (4, 4), GenMatAccess], u'M8': SquaredMatrix[M8, (4, 4), GenMatAccess], u'v0': Matrix[v0, (4, 1), GenMatAccess], u'u': Matrix[u, (4, 1), GenMatAccess], u'M4': Symmetric[M4, (4, 4), USMatAccess], u'v2': Matrix[v2, (4, 1), GenMatAccess], u'v1': Matrix[v1, (4, 1), GenMatAccess], u'v3': Matrix[v3, (4, 1), GenMatAccess], u'Q': Symmetric[Q, (4, 4), USMatAccess], u'x': Matrix[x, (4, 1), GenMatAccess], u'y': Matrix[y, (4, 1), GenMatAccess], u'M1': SquaredMatrix[M1, (4, 4), GenMatAccess], u'B': SquaredMatrix[B, (4, 4), GenMatAccess], u'z': Matrix[z, (4, 1), GenMatAccess]} }
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ann: {'part_schemes': {'Assign_Mul_UpperTriangular_Matrix_Matrix_opt': {'m0': 'm04.ll', 'm2': 'm21.ll'}, 'Assign_Mul_T_UpperTriangular_UpperTriangular_Symmetric_opt': {'m0': 'm03.ll'}, 'ldiv_utn_ow_opt': {'m': 'm4.ll', 'n': 'n1.ll'}, 'Assign_Mul_T_UpperTriangular_Matrix_Matrix_opt': {'m0': 'm04.ll', 'm2': 'm21.ll'}, 'Assign_Mul_T_UpperTriangular_SquaredMatrix_SquaredMatrix_opt': {'m0': 'm04.ll', 'm2': 'm21.ll'}, 'Assign_Mul_UpperTriangular_SquaredMatrix_SquaredMatrix_opt': {'m0': 'm04.ll', 'm2': 'm21.ll'}}, 'cl1ck_v': 0, 'variant_tag': 'Assign_Mul_T_UpperTriangular_Matrix_Matrix_opt_m04_m21_Assign_Mul_T_UpperTriangular_SquaredMatrix_SquaredMatrix_opt_m04_m21_Assign_Mul_T_UpperTriangular_UpperTriangular_Symmetric_opt_m03_Assign_Mul_UpperTriangular_Matrix_Matrix_opt_m04_m21_Assign_Mul_UpperTriangular_SquaredMatrix_SquaredMatrix_opt_m04_m21_ldiv_utn_ow_opt_m4_n1'}

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Entry 0:
Eq: Tile( (1, 1), Tile( (4, 4), y[4,1] ) ) = ( ( Tile( (1, 1), Tile( (4, 4), F[4,4] ) ) * Tile( (1, 1), Tile( (4, 4), x[4,1] ) ) ) + ( Tile( (1, 1), Tile( (4, 4), B[4,4] ) ) * Tile( (1, 1), Tile( (4, 4), u[4,1] ) ) ) )
Eq.ann: {}
Entry 1:
Eq: Tile( (1, 1), Tile( (4, 4), M0[4,4] ) ) = ( Tile( (1, 1), Tile( (4, 4), F[4,4] ) ) * Tile( (1, 1), Tile( (4, 4), P[4,4] ) ) )
Eq.ann: {}
Entry 2:
Eq: Tile( (1, 1), Tile( (4, 4), Y[4,4] ) ) = ( ( Tile( (1, 1), Tile( (4, 4), M0[4,4] ) ) * T( Tile( (1, 1), Tile( (4, 4), F[4,4] ) ) ) ) + Tile( (1, 1), Tile( (4, 4), Q[4,4] ) ) )
Eq.ann: {}
Entry 3:
Eq: Tile( (1, 1), Tile( (4, 4), v0[4,1] ) ) = ( Tile( (1, 1), Tile( (4, 4), z[4,1] ) ) - ( Tile( (1, 1), Tile( (4, 4), H[4,4] ) ) * Tile( (1, 1), Tile( (4, 4), y[4,1] ) ) ) )
Eq.ann: {}
Entry 4:
Eq: Tile( (1, 1), Tile( (4, 4), M1[4,4] ) ) = ( Tile( (1, 1), Tile( (4, 4), H[4,4] ) ) * Tile( (1, 1), Tile( (4, 4), Y[4,4] ) ) )
Eq.ann: {}
Entry 5:
Eq: Tile( (1, 1), Tile( (4, 4), M2[4,4] ) ) = ( Tile( (1, 1), Tile( (4, 4), Y[4,4] ) ) * T( Tile( (1, 1), Tile( (4, 4), H[4,4] ) ) ) )
Eq.ann: {}
Entry 6:
Eq: Tile( (1, 1), Tile( (4, 4), M3[4,4] ) ) = ( ( Tile( (1, 1), Tile( (4, 4), M1[4,4] ) ) * T( Tile( (1, 1), Tile( (4, 4), H[4,4] ) ) ) ) + Tile( (1, 1), Tile( (4, 4), R[4,4] ) ) )
Eq.ann: {}
Entry 7:
Eq: Tile( (1, 1), G(h(1, 4, 0), U[4,4],h(1, 4, 0)) ) = Sqrt( Tile( (1, 1), G(h(1, 4, 0), U[4,4],h(1, 4, 0)) ) )
Eq.ann: {}
Entry 8:
Eq: Tile( (1, 1), G(h(1, 1, 0), T649[1,4],h(1, 4, 0)) ) = ( Tile( (1, 1), 1[1,1] ) Div Tile( (1, 1), G(h(1, 4, 0), U[4,4],h(1, 4, 0)) ) )
Eq.ann: {}
Entry 9:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), U[4,4],h(3, 4, 1)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 1, 0), T649[1,4],h(1, 4, 0)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), U[4,4],h(3, 4, 1)) ) ) )
Eq.ann: {}
Entry 10:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 1), U[4,4],h(3, 4, 1)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 1), U[4,4],h(3, 4, 1)) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), U[4,4],h(3, 4, 1)) ) ) ) * Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), U[4,4],h(3, 4, 1)) ) ) ) )
Eq.ann: {}
Entry 11:
Eq: Tile( (1, 1), G(h(1, 4, 1), U[4,4],h(1, 4, 1)) ) = Sqrt( Tile( (1, 1), G(h(1, 4, 1), U[4,4],h(1, 4, 1)) ) )
Eq.ann: {}
Entry 12:
Eq: Tile( (1, 1), G(h(1, 1, 0), T649[1,4],h(1, 4, 1)) ) = ( Tile( (1, 1), 1[1,1] ) Div Tile( (1, 1), G(h(1, 4, 1), U[4,4],h(1, 4, 1)) ) )
Eq.ann: {}
Entry 13:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), U[4,4],h(2, 4, 2)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 1, 0), T649[1,4],h(1, 4, 1)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), U[4,4],h(2, 4, 2)) ) ) )
Eq.ann: {}
Entry 14:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 2), U[4,4],h(2, 4, 2)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 2), U[4,4],h(2, 4, 2)) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), U[4,4],h(2, 4, 2)) ) ) ) * Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), U[4,4],h(2, 4, 2)) ) ) ) )
Eq.ann: {}
Entry 15:
Eq: Tile( (1, 1), G(h(1, 4, 2), U[4,4],h(1, 4, 2)) ) = Sqrt( Tile( (1, 1), G(h(1, 4, 2), U[4,4],h(1, 4, 2)) ) )
Eq.ann: {}
Entry 16:
Eq: Tile( (1, 1), G(h(1, 4, 2), U[4,4],h(1, 4, 3)) ) = ( Tile( (1, 1), G(h(1, 4, 2), U[4,4],h(1, 4, 3)) ) Div Tile( (1, 1), G(h(1, 4, 2), U[4,4],h(1, 4, 2)) ) )
Eq.ann: {}
Entry 17:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), U[4,4],h(1, 4, 3)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), U[4,4],h(1, 4, 3)) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), U[4,4],h(1, 4, 3)) ) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), U[4,4],h(1, 4, 3)) ) ) ) )
Eq.ann: {}
Entry 18:
Eq: Tile( (1, 1), G(h(1, 4, 3), U[4,4],h(1, 4, 3)) ) = Sqrt( Tile( (1, 1), G(h(1, 4, 3), U[4,4],h(1, 4, 3)) ) )
Eq.ann: {}
Entry 19:
Eq: Tile( (1, 1), G(h(1, 4, 0), v2[4,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 0), v2[4,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 4, 0), U0[4,4],h(1, 4, 0)) ) )
Eq.ann: {}
Entry 20:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 1), v2[4,1],h(1, 1, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 1), v2[4,1],h(1, 1, 0)) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), U0[4,4],h(3, 4, 1)) ) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), v2[4,1],h(1, 1, 0)) ) ) ) )
Eq.ann: {}
Entry 21:
Eq: Tile( (1, 1), G(h(1, 4, 1), v2[4,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 1), v2[4,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 4, 1), U0[4,4],h(1, 4, 1)) ) )
Eq.ann: {}
Entry 22:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 2), v2[4,1],h(1, 1, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 2), v2[4,1],h(1, 1, 0)) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), U0[4,4],h(2, 4, 2)) ) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), v2[4,1],h(1, 1, 0)) ) ) ) )
Eq.ann: {}
Entry 23:
Eq: Tile( (1, 1), G(h(1, 4, 2), v2[4,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 2), v2[4,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 4, 2), U0[4,4],h(1, 4, 2)) ) )
Eq.ann: {}
Entry 24:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), v2[4,1],h(1, 1, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), v2[4,1],h(1, 1, 0)) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), U0[4,4],h(1, 4, 3)) ) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), v2[4,1],h(1, 1, 0)) ) ) ) )
Eq.ann: {}
Entry 25:
Eq: Tile( (1, 1), G(h(1, 4, 3), v2[4,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 3), v2[4,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 4, 3), U0[4,4],h(1, 4, 3)) ) )
Eq.ann: {}
Entry 26:
Eq: Tile( (1, 1), G(h(1, 4, 3), v4[4,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 3), v4[4,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 4, 3), U0[4,4],h(1, 4, 3)) ) )
Eq.ann: {}
Entry 27:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 0), v4[4,1],h(1, 1, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 0), v4[4,1],h(1, 1, 0)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 0), U0[4,4],h(1, 4, 3)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), v4[4,1],h(1, 1, 0)) ) ) ) )
Eq.ann: {}
Entry 28:
Eq: Tile( (1, 1), G(h(1, 4, 2), v4[4,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 2), v4[4,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 4, 2), U0[4,4],h(1, 4, 2)) ) )
Eq.ann: {}
Entry 29:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 0), v4[4,1],h(1, 1, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 0), v4[4,1],h(1, 1, 0)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 0), U0[4,4],h(1, 4, 2)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), v4[4,1],h(1, 1, 0)) ) ) ) )
Eq.ann: {}
Entry 30:
Eq: Tile( (1, 1), G(h(1, 4, 1), v4[4,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 1), v4[4,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 4, 1), U0[4,4],h(1, 4, 1)) ) )
Eq.ann: {}
Entry 31:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), v4[4,1],h(1, 1, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), v4[4,1],h(1, 1, 0)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), U0[4,4],h(1, 4, 1)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), v4[4,1],h(1, 1, 0)) ) ) ) )
Eq.ann: {}
Entry 32:
Eq: Tile( (1, 1), G(h(1, 4, 0), v4[4,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 0), v4[4,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 4, 0), U0[4,4],h(1, 4, 0)) ) )
Eq.ann: {}
Entry 33:
Eq: Tile( (1, 1), G(h(1, 1, 0), T660[1,4],h(1, 4, 0)) ) = ( Tile( (1, 1), 1[1,1] ) Div Tile( (1, 1), G(h(1, 4, 0), U0[4,4],h(1, 4, 0)) ) )
Eq.ann: {}
Entry 34:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), M6[4,4],h(4, 4, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 1, 0), T660[1,4],h(1, 4, 0)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), M6[4,4],h(4, 4, 0)) ) ) )
Eq.ann: {}
Entry 35:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 1), M6[4,4],h(4, 4, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 1), M6[4,4],h(4, 4, 0)) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), U0[4,4],h(3, 4, 1)) ) ) ) * Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), M6[4,4],h(4, 4, 0)) ) ) ) )
Eq.ann: {}
Entry 36:
Eq: Tile( (1, 1), G(h(1, 1, 0), T660[1,4],h(1, 4, 1)) ) = ( Tile( (1, 1), 1[1,1] ) Div Tile( (1, 1), G(h(1, 4, 1), U0[4,4],h(1, 4, 1)) ) )
Eq.ann: {}
Entry 37:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), M6[4,4],h(4, 4, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 1, 0), T660[1,4],h(1, 4, 1)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), M6[4,4],h(4, 4, 0)) ) ) )
Eq.ann: {}
Entry 38:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 2), M6[4,4],h(4, 4, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 2), M6[4,4],h(4, 4, 0)) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), U0[4,4],h(2, 4, 2)) ) ) ) * Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), M6[4,4],h(4, 4, 0)) ) ) ) )
Eq.ann: {}
Entry 39:
Eq: Tile( (1, 1), G(h(1, 1, 0), T660[1,4],h(1, 4, 2)) ) = ( Tile( (1, 1), 1[1,1] ) Div Tile( (1, 1), G(h(1, 4, 2), U0[4,4],h(1, 4, 2)) ) )
Eq.ann: {}
Entry 40:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), M6[4,4],h(4, 4, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 1, 0), T660[1,4],h(1, 4, 2)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), M6[4,4],h(4, 4, 0)) ) ) )
Eq.ann: {}
Entry 41:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), M6[4,4],h(4, 4, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), M6[4,4],h(4, 4, 0)) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), U0[4,4],h(1, 4, 3)) ) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), M6[4,4],h(4, 4, 0)) ) ) ) )
Eq.ann: {}
Entry 42:
Eq: Tile( (1, 1), G(h(1, 1, 0), T660[1,4],h(1, 4, 3)) ) = ( Tile( (1, 1), 1[1,1] ) Div Tile( (1, 1), G(h(1, 4, 3), U0[4,4],h(1, 4, 3)) ) )
Eq.ann: {}
Entry 43:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), M6[4,4],h(4, 4, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 1, 0), T660[1,4],h(1, 4, 3)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), M6[4,4],h(4, 4, 0)) ) ) )
Eq.ann: {}
Entry 44:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), M8[4,4],h(4, 4, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 1, 0), T660[1,4],h(1, 4, 3)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), M8[4,4],h(4, 4, 0)) ) ) )
Eq.ann: {}
Entry 45:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 0), M8[4,4],h(4, 4, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 0), M8[4,4],h(4, 4, 0)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 0), U0[4,4],h(1, 4, 3)) ) ) * Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), M8[4,4],h(4, 4, 0)) ) ) ) )
Eq.ann: {}
Entry 46:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), M8[4,4],h(4, 4, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 1, 0), T660[1,4],h(1, 4, 2)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), M8[4,4],h(4, 4, 0)) ) ) )
Eq.ann: {}
Entry 47:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 0), M8[4,4],h(4, 4, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 0), M8[4,4],h(4, 4, 0)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 0), U0[4,4],h(1, 4, 2)) ) ) * Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), M8[4,4],h(4, 4, 0)) ) ) ) )
Eq.ann: {}
Entry 48:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), M8[4,4],h(4, 4, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 1, 0), T660[1,4],h(1, 4, 1)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), M8[4,4],h(4, 4, 0)) ) ) )
Eq.ann: {}
Entry 49:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), M8[4,4],h(4, 4, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), M8[4,4],h(4, 4, 0)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), U0[4,4],h(1, 4, 1)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), M8[4,4],h(4, 4, 0)) ) ) ) )
Eq.ann: {}
Entry 50:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), M8[4,4],h(4, 4, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 1, 0), T660[1,4],h(1, 4, 0)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), M8[4,4],h(4, 4, 0)) ) ) )
Eq.ann: {}
Entry 51:
Eq: Tile( (1, 1), Tile( (4, 4), x[4,1] ) ) = ( Tile( (1, 1), Tile( (4, 4), y[4,1] ) ) + ( Tile( (1, 1), Tile( (4, 4), M2[4,4] ) ) * Tile( (1, 1), Tile( (4, 4), v0[4,1] ) ) ) )
Eq.ann: {}
Entry 52:
Eq: Tile( (1, 1), Tile( (4, 4), P[4,4] ) ) = ( Tile( (1, 1), Tile( (4, 4), Y[4,4] ) ) - ( Tile( (1, 1), Tile( (4, 4), M2[4,4] ) ) * Tile( (1, 1), Tile( (4, 4), M1[4,4] ) ) ) )
Eq.ann: {}
 *
 * Created on: 2017-08-09
 * Author: danieles
 */

#pragma once

#include <x86intrin.h>


static __inline__ __m256d _asm256_loadu_pd(const double* p) {
  __m256d v;
  __asm__("vmovupd %1, %0" : "=x" (v) : "m" (*p));
  return v;
}

static __inline__ void _asm256_storeu_pd(double* p, const __m256d& v) {
  __asm__("vmovupd %1, %0" : "=rm" (*p) : "x" (v));
}

#define PARAM0 4
#define PARAM1 4
#define PARAM2 4

#define ERRTHRESH 1e-7

#define NUMREP 30

#define floord(n,d) (((n)<0) ? -((-(n)+(d)-1)/(d)) : (n)/(d))
#define ceild(n,d)  (((n)<0) ? -((-(n))/(d)) : ((n)+(d)-1)/(d))
#define max(x,y)    ((x) > (y) ? (x) : (y))
#define min(x,y)    ((x) < (y) ? (x) : (y))
#define Max(x,y)    ((x) > (y) ? (x) : (y))
#define Min(x,y)    ((x) < (y) ? (x) : (y))


static __attribute__((noinline)) void kernel(double const * F, double const * B, double const * u, double const * Q, double const * z, double const * H, double const * R, double * y, double * x, double * M0, double * P, double * Y, double * v0, double * M1, double * M2, double * M3)
{
  __m256d _t0_0, _t0_1, _t0_2, _t0_3, _t0_4, _t0_5, _t0_6, _t0_7,
	_t0_8, _t0_9, _t0_10, _t0_11, _t0_12, _t0_13, _t0_14, _t0_15,
	_t0_16, _t0_17, _t0_18, _t0_19, _t0_20, _t0_21, _t0_22, _t0_23,
	_t0_24, _t0_25, _t0_26, _t0_27, _t0_28, _t0_29, _t0_30, _t0_31,
	_t0_32, _t0_33, _t0_34, _t0_35, _t0_36, _t0_37, _t0_38, _t0_39,
	_t0_40, _t0_41, _t0_42, _t0_43, _t0_44, _t0_45, _t0_46, _t0_47,
	_t0_48, _t0_49, _t0_50, _t0_51, _t0_52, _t0_53, _t0_54, _t0_55,
	_t0_56, _t0_57, _t0_58, _t0_59, _t0_60, _t0_61, _t0_62, _t0_63,
	_t0_64, _t0_65, _t0_66, _t0_67, _t0_68, _t0_69, _t0_70, _t0_71,
	_t0_72, _t0_73, _t0_74, _t0_75, _t0_76, _t0_77, _t0_78, _t0_79,
	_t0_80, _t0_81, _t0_82, _t0_83, _t0_84, _t0_85, _t0_86, _t0_87,
	_t0_88, _t0_89, _t0_90, _t0_91, _t0_92, _t0_93, _t0_94, _t0_95,
	_t0_96, _t0_97, _t0_98, _t0_99, _t0_100, _t0_101, _t0_102, _t0_103,
	_t0_104, _t0_105, _t0_106, _t0_107, _t0_108, _t0_109, _t0_110, _t0_111,
	_t0_112, _t0_113, _t0_114, _t0_115, _t0_116, _t0_117, _t0_118, _t0_119,
	_t0_120, _t0_121, _t0_122, _t0_123, _t0_124, _t0_125, _t0_126, _t0_127,
	_t0_128, _t0_129, _t0_130, _t0_131, _t0_132, _t0_133, _t0_134, _t0_135,
	_t0_136, _t0_137, _t0_138, _t0_139, _t0_140, _t0_141, _t0_142, _t0_143,
	_t0_144, _t0_145, _t0_146, _t0_147, _t0_148, _t0_149, _t0_150, _t0_151,
	_t0_152, _t0_153, _t0_154, _t0_155, _t0_156, _t0_157, _t0_158, _t0_159,
	_t0_160, _t0_161, _t0_162, _t0_163, _t0_164, _t0_165, _t0_166, _t0_167,
	_t0_168, _t0_169, _t0_170, _t0_171, _t0_172, _t0_173, _t0_174, _t0_175,
	_t0_176, _t0_177, _t0_178, _t0_179, _t0_180, _t0_181, _t0_182, _t0_183,
	_t0_184, _t0_185, _t0_186, _t0_187, _t0_188, _t0_189, _t0_190, _t0_191,
	_t0_192, _t0_193, _t0_194, _t0_195, _t0_196, _t0_197, _t0_198, _t0_199,
	_t0_200, _t0_201, _t0_202, _t0_203, _t0_204, _t0_205, _t0_206, _t0_207,
	_t0_208, _t0_209, _t0_210, _t0_211, _t0_212, _t0_213, _t0_214, _t0_215,
	_t0_216, _t0_217, _t0_218, _t0_219, _t0_220, _t0_221, _t0_222, _t0_223,
	_t0_224, _t0_225, _t0_226, _t0_227, _t0_228, _t0_229, _t0_230, _t0_231,
	_t0_232, _t0_233, _t0_234, _t0_235, _t0_236, _t0_237, _t0_238, _t0_239,
	_t0_240, _t0_241, _t0_242, _t0_243, _t0_244, _t0_245, _t0_246, _t0_247,
	_t0_248, _t0_249, _t0_250, _t0_251, _t0_252, _t0_253, _t0_254, _t0_255,
	_t0_256, _t0_257, _t0_258, _t0_259, _t0_260, _t0_261, _t0_262, _t0_263,
	_t0_264, _t0_265, _t0_266, _t0_267, _t0_268, _t0_269, _t0_270, _t0_271,
	_t0_272, _t0_273, _t0_274, _t0_275, _t0_276, _t0_277, _t0_278, _t0_279,
	_t0_280, _t0_281, _t0_282, _t0_283, _t0_284, _t0_285, _t0_286, _t0_287,
	_t0_288, _t0_289, _t0_290, _t0_291, _t0_292, _t0_293, _t0_294, _t0_295,
	_t0_296, _t0_297, _t0_298, _t0_299, _t0_300, _t0_301, _t0_302, _t0_303,
	_t0_304, _t0_305, _t0_306, _t0_307, _t0_308, _t0_309, _t0_310, _t0_311,
	_t0_312, _t0_313, _t0_314, _t0_315, _t0_316, _t0_317, _t0_318, _t0_319,
	_t0_320, _t0_321, _t0_322, _t0_323, _t0_324, _t0_325, _t0_326, _t0_327,
	_t0_328, _t0_329, _t0_330, _t0_331, _t0_332, _t0_333, _t0_334, _t0_335,
	_t0_336, _t0_337, _t0_338, _t0_339, _t0_340, _t0_341, _t0_342, _t0_343,
	_t0_344, _t0_345, _t0_346, _t0_347, _t0_348, _t0_349, _t0_350, _t0_351,
	_t0_352, _t0_353, _t0_354, _t0_355, _t0_356, _t0_357, _t0_358, _t0_359,
	_t0_360, _t0_361, _t0_362, _t0_363, _t0_364, _t0_365;

  _t0_53 = _asm256_loadu_pd(F);
  _t0_52 = _asm256_loadu_pd(F + 4);
  _t0_51 = _asm256_loadu_pd(F + 8);
  _t0_50 = _asm256_loadu_pd(F + 12);
  _t0_63 = _asm256_loadu_pd(x);
  _t0_49 = _asm256_loadu_pd(B);
  _t0_48 = _asm256_loadu_pd(B + 4);
  _t0_47 = _asm256_loadu_pd(B + 8);
  _t0_46 = _asm256_loadu_pd(B + 12);
  _t0_45 = _asm256_loadu_pd(u);
  _t0_44 = _mm256_broadcast_sd(F);
  _t0_43 = _mm256_broadcast_sd(F + 1);
  _t0_42 = _mm256_broadcast_sd(F + 2);
  _t0_41 = _mm256_broadcast_sd(F + 3);
  _t0_40 = _mm256_broadcast_sd(F + 4);
  _t0_39 = _mm256_broadcast_sd(F + 5);
  _t0_38 = _mm256_broadcast_sd(F + 6);
  _t0_37 = _mm256_broadcast_sd(F + 7);
  _t0_36 = _mm256_broadcast_sd(F + 8);
  _t0_35 = _mm256_broadcast_sd(F + 9);
  _t0_34 = _mm256_broadcast_sd(F + 10);
  _t0_33 = _mm256_broadcast_sd(F + 11);
  _t0_32 = _mm256_broadcast_sd(F + 12);
  _t0_31 = _mm256_broadcast_sd(F + 13);
  _t0_30 = _mm256_broadcast_sd(F + 14);
  _t0_29 = _mm256_broadcast_sd(F + 15);
  _t0_98 = _asm256_loadu_pd(P);
  _t0_99 = _mm256_maskload_pd(P + 4, _mm256_setr_epi64x(0, (__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63));
  _t0_100 = _mm256_maskload_pd(P + 8, _mm256_setr_epi64x(0, 0, (__int64)1 << 63, (__int64)1 << 63));
  _t0_101 = _mm256_maskload_pd(P + 12, _mm256_setr_epi64x(0, 0, 0, (__int64)1 << 63));
  _t0_28 = _asm256_loadu_pd(Q);
  _t0_27 = _mm256_maskload_pd(Q + 4, _mm256_setr_epi64x(0, (__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63));
  _t0_26 = _mm256_maskload_pd(Q + 8, _mm256_setr_epi64x(0, 0, (__int64)1 << 63, (__int64)1 << 63));
  _t0_25 = _mm256_maskload_pd(Q + 12, _mm256_setr_epi64x(0, 0, 0, (__int64)1 << 63));
  _t0_24 = _asm256_loadu_pd(z);
  _t0_23 = _asm256_loadu_pd(H);
  _t0_22 = _asm256_loadu_pd(H + 4);
  _t0_21 = _asm256_loadu_pd(H + 8);
  _t0_20 = _asm256_loadu_pd(H + 12);
  _t0_19 = _mm256_broadcast_sd(H);
  _t0_18 = _mm256_broadcast_sd(H + 1);
  _t0_17 = _mm256_broadcast_sd(H + 2);
  _t0_16 = _mm256_broadcast_sd(H + 3);
  _t0_15 = _mm256_broadcast_sd(H + 4);
  _t0_14 = _mm256_broadcast_sd(H + 5);
  _t0_13 = _mm256_broadcast_sd(H + 6);
  _t0_12 = _mm256_broadcast_sd(H + 7);
  _t0_11 = _mm256_broadcast_sd(H + 8);
  _t0_10 = _mm256_broadcast_sd(H + 9);
  _t0_9 = _mm256_broadcast_sd(H + 10);
  _t0_8 = _mm256_broadcast_sd(H + 11);
  _t0_7 = _mm256_broadcast_sd(H + 12);
  _t0_6 = _mm256_broadcast_sd(H + 13);
  _t0_5 = _mm256_broadcast_sd(H + 14);
  _t0_4 = _mm256_broadcast_sd(H + 15);
  _t0_3 = _asm256_loadu_pd(R);
  _t0_2 = _mm256_maskload_pd(R + 4, _mm256_setr_epi64x(0, (__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63));
  _t0_1 = _mm256_maskload_pd(R + 8, _mm256_setr_epi64x(0, 0, (__int64)1 << 63, (__int64)1 << 63));
  _t0_0 = _mm256_maskload_pd(R + 12, _mm256_setr_epi64x(0, 0, 0, (__int64)1 << 63));

  // Generating : y[4,1] = S(h(4, 4, 0), ( ( G(h(4, 4, 0), F[4,4],h(4, 4, 0)) * G(h(4, 4, 0), x[4,1],h(1, 1, 0)) ) + ( G(h(4, 4, 0), B[4,4],h(4, 4, 0)) * G(h(4, 4, 0), u[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // AVX Loader:

  // 4-BLAC: 4x4 * 4x1
  _t0_104 = _mm256_add_pd(_mm256_permute2f128_pd(_mm256_hadd_pd(_mm256_mul_pd(_t0_53, _t0_63), _mm256_mul_pd(_t0_52, _t0_63)), _mm256_hadd_pd(_mm256_mul_pd(_t0_51, _t0_63), _mm256_mul_pd(_t0_50, _t0_63)), 33), _mm256_blend_pd(_mm256_hadd_pd(_mm256_mul_pd(_t0_53, _t0_63), _mm256_mul_pd(_t0_52, _t0_63)), _mm256_hadd_pd(_mm256_mul_pd(_t0_51, _t0_63), _mm256_mul_pd(_t0_50, _t0_63)), 12));

  // AVX Loader:

  // AVX Loader:

  // 4-BLAC: 4x4 * 4x1
  _t0_105 = _mm256_add_pd(_mm256_permute2f128_pd(_mm256_hadd_pd(_mm256_mul_pd(_t0_49, _t0_45), _mm256_mul_pd(_t0_48, _t0_45)), _mm256_hadd_pd(_mm256_mul_pd(_t0_47, _t0_45), _mm256_mul_pd(_t0_46, _t0_45)), 33), _mm256_blend_pd(_mm256_hadd_pd(_mm256_mul_pd(_t0_49, _t0_45), _mm256_mul_pd(_t0_48, _t0_45)), _mm256_hadd_pd(_mm256_mul_pd(_t0_47, _t0_45), _mm256_mul_pd(_t0_46, _t0_45)), 12));

  // 4-BLAC: 4x1 + 4x1
  _t0_54 = _mm256_add_pd(_t0_104, _t0_105);

  // AVX Storer:

  // Generating : M0[4,4] = S(h(4, 4, 0), ( G(h(4, 4, 0), F[4,4],h(4, 4, 0)) * G(h(4, 4, 0), P[4,4],h(4, 4, 0)) ),h(4, 4, 0))

  // AVX Loader:

  // AVX Loader:

  // 4x4 -> 4x4 - UpSymm
  _t0_164 = _t0_98;
  _t0_165 = _mm256_blend_pd(_mm256_shuffle_pd(_t0_98, _t0_99, 3), _t0_99, 12);
  _t0_166 = _mm256_permute2f128_pd(_mm256_shuffle_pd(_t0_98, _t0_99, 0), _t0_100, 49);
  _t0_167 = _mm256_permute2f128_pd(_mm256_shuffle_pd(_t0_98, _t0_99, 12), _mm256_shuffle_pd(_t0_100, _t0_101, 12), 49);

  // 4-BLAC: 4x4 * 4x4
  _t0_106 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_t0_44, _t0_164), _mm256_mul_pd(_t0_43, _t0_165)), _mm256_add_pd(_mm256_mul_pd(_t0_42, _t0_166), _mm256_mul_pd(_t0_41, _t0_167)));
  _t0_107 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_t0_40, _t0_164), _mm256_mul_pd(_t0_39, _t0_165)), _mm256_add_pd(_mm256_mul_pd(_t0_38, _t0_166), _mm256_mul_pd(_t0_37, _t0_167)));
  _t0_108 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_t0_36, _t0_164), _mm256_mul_pd(_t0_35, _t0_165)), _mm256_add_pd(_mm256_mul_pd(_t0_34, _t0_166), _mm256_mul_pd(_t0_33, _t0_167)));
  _t0_109 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_t0_32, _t0_164), _mm256_mul_pd(_t0_31, _t0_165)), _mm256_add_pd(_mm256_mul_pd(_t0_30, _t0_166), _mm256_mul_pd(_t0_29, _t0_167)));

  // AVX Storer:

  // Generating : Y[4,4] = S(h(4, 4, 0), ( ( G(h(4, 4, 0), M0[4,4],h(4, 4, 0)) * T( G(h(4, 4, 0), F[4,4],h(4, 4, 0)) ) ) + G(h(4, 4, 0), Q[4,4],h(4, 4, 0)) ),h(4, 4, 0))

  // AVX Loader:

  // AVX Loader:

  // 4-BLAC: (4x4)^T
  _t0_354 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_53, _t0_52), _mm256_unpacklo_pd(_t0_51, _t0_50), 32);
  _t0_355 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t0_53, _t0_52), _mm256_unpackhi_pd(_t0_51, _t0_50), 32);
  _t0_356 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_53, _t0_52), _mm256_unpacklo_pd(_t0_51, _t0_50), 49);
  _t0_357 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t0_53, _t0_52), _mm256_unpackhi_pd(_t0_51, _t0_50), 49);

  // 4-BLAC: 4x4 * 4x4
  _t0_110 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_106, _t0_106, 32), _mm256_permute2f128_pd(_t0_106, _t0_106, 32), 0), _t0_354), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_106, _t0_106, 32), _mm256_permute2f128_pd(_t0_106, _t0_106, 32), 15), _t0_355)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_106, _t0_106, 49), _mm256_permute2f128_pd(_t0_106, _t0_106, 49), 0), _t0_356), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_106, _t0_106, 49), _mm256_permute2f128_pd(_t0_106, _t0_106, 49), 15), _t0_357)));
  _t0_111 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_107, _t0_107, 32), _mm256_permute2f128_pd(_t0_107, _t0_107, 32), 0), _t0_354), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_107, _t0_107, 32), _mm256_permute2f128_pd(_t0_107, _t0_107, 32), 15), _t0_355)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_107, _t0_107, 49), _mm256_permute2f128_pd(_t0_107, _t0_107, 49), 0), _t0_356), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_107, _t0_107, 49), _mm256_permute2f128_pd(_t0_107, _t0_107, 49), 15), _t0_357)));
  _t0_112 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_108, _t0_108, 32), _mm256_permute2f128_pd(_t0_108, _t0_108, 32), 0), _t0_354), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_108, _t0_108, 32), _mm256_permute2f128_pd(_t0_108, _t0_108, 32), 15), _t0_355)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_108, _t0_108, 49), _mm256_permute2f128_pd(_t0_108, _t0_108, 49), 0), _t0_356), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_108, _t0_108, 49), _mm256_permute2f128_pd(_t0_108, _t0_108, 49), 15), _t0_357)));
  _t0_113 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_109, _t0_109, 32), _mm256_permute2f128_pd(_t0_109, _t0_109, 32), 0), _t0_354), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_109, _t0_109, 32), _mm256_permute2f128_pd(_t0_109, _t0_109, 32), 15), _t0_355)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_109, _t0_109, 49), _mm256_permute2f128_pd(_t0_109, _t0_109, 49), 0), _t0_356), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_109, _t0_109, 49), _mm256_permute2f128_pd(_t0_109, _t0_109, 49), 15), _t0_357)));

  // AVX Loader:

  // 4x4 -> 4x4 - UpSymm
  _t0_181 = _t0_28;
  _t0_182 = _mm256_blend_pd(_mm256_shuffle_pd(_t0_28, _t0_27, 3), _t0_27, 12);
  _t0_183 = _mm256_permute2f128_pd(_mm256_shuffle_pd(_t0_28, _t0_27, 0), _t0_26, 49);
  _t0_184 = _mm256_permute2f128_pd(_mm256_shuffle_pd(_t0_28, _t0_27, 12), _mm256_shuffle_pd(_t0_26, _t0_25, 12), 49);

  // 4-BLAC: 4x4 + 4x4
  _t0_55 = _mm256_add_pd(_t0_110, _t0_181);
  _t0_56 = _mm256_add_pd(_t0_111, _t0_182);
  _t0_57 = _mm256_add_pd(_t0_112, _t0_183);
  _t0_58 = _mm256_add_pd(_t0_113, _t0_184);

  // AVX Storer:

  // 4x4 -> 4x4 - UpSymm
  _t0_64 = _t0_55;
  _t0_65 = _t0_56;
  _t0_66 = _t0_57;
  _t0_67 = _t0_58;

  // Generating : v0[4,1] = S(h(4, 4, 0), ( G(h(4, 4, 0), z[4,1],h(1, 1, 0)) - ( G(h(4, 4, 0), H[4,4],h(4, 4, 0)) * G(h(4, 4, 0), y[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // AVX Loader:

  // AVX Loader:

  // 4-BLAC: 4x4 * 4x1
  _t0_114 = _mm256_add_pd(_mm256_permute2f128_pd(_mm256_hadd_pd(_mm256_mul_pd(_t0_23, _t0_54), _mm256_mul_pd(_t0_22, _t0_54)), _mm256_hadd_pd(_mm256_mul_pd(_t0_21, _t0_54), _mm256_mul_pd(_t0_20, _t0_54)), 33), _mm256_blend_pd(_mm256_hadd_pd(_mm256_mul_pd(_t0_23, _t0_54), _mm256_mul_pd(_t0_22, _t0_54)), _mm256_hadd_pd(_mm256_mul_pd(_t0_21, _t0_54), _mm256_mul_pd(_t0_20, _t0_54)), 12));

  // 4-BLAC: 4x1 - 4x1
  _t0_132 = _mm256_sub_pd(_t0_24, _t0_114);

  // AVX Storer:

  // Generating : M1[4,4] = S(h(4, 4, 0), ( G(h(4, 4, 0), H[4,4],h(4, 4, 0)) * G(h(4, 4, 0), Y[4,4],h(4, 4, 0)) ),h(4, 4, 0))

  // AVX Loader:

  // AVX Loader:

  // 4x4 -> 4x4 - UpSymm
  _t0_194 = _t0_64;
  _t0_195 = _mm256_blend_pd(_mm256_shuffle_pd(_t0_64, _t0_65, 3), _t0_65, 12);
  _t0_196 = _mm256_permute2f128_pd(_mm256_shuffle_pd(_t0_64, _t0_65, 0), _t0_66, 49);
  _t0_197 = _mm256_permute2f128_pd(_mm256_shuffle_pd(_t0_64, _t0_65, 12), _mm256_shuffle_pd(_t0_66, _t0_67, 12), 49);

  // 4-BLAC: 4x4 * 4x4
  _t0_115 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_t0_19, _t0_194), _mm256_mul_pd(_t0_18, _t0_195)), _mm256_add_pd(_mm256_mul_pd(_t0_17, _t0_196), _mm256_mul_pd(_t0_16, _t0_197)));
  _t0_116 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_t0_15, _t0_194), _mm256_mul_pd(_t0_14, _t0_195)), _mm256_add_pd(_mm256_mul_pd(_t0_13, _t0_196), _mm256_mul_pd(_t0_12, _t0_197)));
  _t0_117 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_t0_11, _t0_194), _mm256_mul_pd(_t0_10, _t0_195)), _mm256_add_pd(_mm256_mul_pd(_t0_9, _t0_196), _mm256_mul_pd(_t0_8, _t0_197)));
  _t0_118 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_t0_7, _t0_194), _mm256_mul_pd(_t0_6, _t0_195)), _mm256_add_pd(_mm256_mul_pd(_t0_5, _t0_196), _mm256_mul_pd(_t0_4, _t0_197)));

  // AVX Storer:

  // Generating : M2[4,4] = S(h(4, 4, 0), ( G(h(4, 4, 0), Y[4,4],h(4, 4, 0)) * T( G(h(4, 4, 0), H[4,4],h(4, 4, 0)) ) ),h(4, 4, 0))

  // AVX Loader:

  // 4x4 -> 4x4 - UpSymm
  _t0_207 = _t0_64;
  _t0_208 = _mm256_blend_pd(_mm256_shuffle_pd(_t0_64, _t0_65, 3), _t0_65, 12);
  _t0_209 = _mm256_permute2f128_pd(_mm256_shuffle_pd(_t0_64, _t0_65, 0), _t0_66, 49);
  _t0_210 = _mm256_permute2f128_pd(_mm256_shuffle_pd(_t0_64, _t0_65, 12), _mm256_shuffle_pd(_t0_66, _t0_67, 12), 49);

  // AVX Loader:

  // 4-BLAC: (4x4)^T
  _t0_358 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_23, _t0_22), _mm256_unpacklo_pd(_t0_21, _t0_20), 32);
  _t0_359 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t0_23, _t0_22), _mm256_unpackhi_pd(_t0_21, _t0_20), 32);
  _t0_360 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_23, _t0_22), _mm256_unpacklo_pd(_t0_21, _t0_20), 49);
  _t0_361 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t0_23, _t0_22), _mm256_unpackhi_pd(_t0_21, _t0_20), 49);

  // 4-BLAC: 4x4 * 4x4
  _t0_119 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_207, _t0_207, 32), _mm256_permute2f128_pd(_t0_207, _t0_207, 32), 0), _t0_358), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_207, _t0_207, 32), _mm256_permute2f128_pd(_t0_207, _t0_207, 32), 15), _t0_359)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_207, _t0_207, 49), _mm256_permute2f128_pd(_t0_207, _t0_207, 49), 0), _t0_360), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_207, _t0_207, 49), _mm256_permute2f128_pd(_t0_207, _t0_207, 49), 15), _t0_361)));
  _t0_120 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_208, _t0_208, 32), _mm256_permute2f128_pd(_t0_208, _t0_208, 32), 0), _t0_358), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_208, _t0_208, 32), _mm256_permute2f128_pd(_t0_208, _t0_208, 32), 15), _t0_359)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_208, _t0_208, 49), _mm256_permute2f128_pd(_t0_208, _t0_208, 49), 0), _t0_360), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_208, _t0_208, 49), _mm256_permute2f128_pd(_t0_208, _t0_208, 49), 15), _t0_361)));
  _t0_121 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_209, _t0_209, 32), _mm256_permute2f128_pd(_t0_209, _t0_209, 32), 0), _t0_358), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_209, _t0_209, 32), _mm256_permute2f128_pd(_t0_209, _t0_209, 32), 15), _t0_359)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_209, _t0_209, 49), _mm256_permute2f128_pd(_t0_209, _t0_209, 49), 0), _t0_360), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_209, _t0_209, 49), _mm256_permute2f128_pd(_t0_209, _t0_209, 49), 15), _t0_361)));
  _t0_122 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_210, _t0_210, 32), _mm256_permute2f128_pd(_t0_210, _t0_210, 32), 0), _t0_358), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_210, _t0_210, 32), _mm256_permute2f128_pd(_t0_210, _t0_210, 32), 15), _t0_359)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_210, _t0_210, 49), _mm256_permute2f128_pd(_t0_210, _t0_210, 49), 0), _t0_360), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_210, _t0_210, 49), _mm256_permute2f128_pd(_t0_210, _t0_210, 49), 15), _t0_361)));

  // AVX Storer:

  // Generating : M3[4,4] = S(h(4, 4, 0), ( ( G(h(4, 4, 0), M1[4,4],h(4, 4, 0)) * T( G(h(4, 4, 0), H[4,4],h(4, 4, 0)) ) ) + G(h(4, 4, 0), R[4,4],h(4, 4, 0)) ),h(4, 4, 0))

  // AVX Loader:

  // AVX Loader:

  // 4-BLAC: (4x4)^T
  _t0_362 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_23, _t0_22), _mm256_unpacklo_pd(_t0_21, _t0_20), 32);
  _t0_363 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t0_23, _t0_22), _mm256_unpackhi_pd(_t0_21, _t0_20), 32);
  _t0_364 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_23, _t0_22), _mm256_unpacklo_pd(_t0_21, _t0_20), 49);
  _t0_365 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t0_23, _t0_22), _mm256_unpackhi_pd(_t0_21, _t0_20), 49);

  // 4-BLAC: 4x4 * 4x4
  _t0_123 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_115, _t0_115, 32), _mm256_permute2f128_pd(_t0_115, _t0_115, 32), 0), _t0_362), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_115, _t0_115, 32), _mm256_permute2f128_pd(_t0_115, _t0_115, 32), 15), _t0_363)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_115, _t0_115, 49), _mm256_permute2f128_pd(_t0_115, _t0_115, 49), 0), _t0_364), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_115, _t0_115, 49), _mm256_permute2f128_pd(_t0_115, _t0_115, 49), 15), _t0_365)));
  _t0_124 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_116, _t0_116, 32), _mm256_permute2f128_pd(_t0_116, _t0_116, 32), 0), _t0_362), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_116, _t0_116, 32), _mm256_permute2f128_pd(_t0_116, _t0_116, 32), 15), _t0_363)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_116, _t0_116, 49), _mm256_permute2f128_pd(_t0_116, _t0_116, 49), 0), _t0_364), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_116, _t0_116, 49), _mm256_permute2f128_pd(_t0_116, _t0_116, 49), 15), _t0_365)));
  _t0_125 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_117, _t0_117, 32), _mm256_permute2f128_pd(_t0_117, _t0_117, 32), 0), _t0_362), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_117, _t0_117, 32), _mm256_permute2f128_pd(_t0_117, _t0_117, 32), 15), _t0_363)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_117, _t0_117, 49), _mm256_permute2f128_pd(_t0_117, _t0_117, 49), 0), _t0_364), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_117, _t0_117, 49), _mm256_permute2f128_pd(_t0_117, _t0_117, 49), 15), _t0_365)));
  _t0_126 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_118, _t0_118, 32), _mm256_permute2f128_pd(_t0_118, _t0_118, 32), 0), _t0_362), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_118, _t0_118, 32), _mm256_permute2f128_pd(_t0_118, _t0_118, 32), 15), _t0_363)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_118, _t0_118, 49), _mm256_permute2f128_pd(_t0_118, _t0_118, 49), 0), _t0_364), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_118, _t0_118, 49), _mm256_permute2f128_pd(_t0_118, _t0_118, 49), 15), _t0_365)));

  // AVX Loader:

  // 4x4 -> 4x4 - UpSymm
  _t0_224 = _t0_3;
  _t0_225 = _mm256_blend_pd(_mm256_shuffle_pd(_t0_3, _t0_2, 3), _t0_2, 12);
  _t0_226 = _mm256_permute2f128_pd(_mm256_shuffle_pd(_t0_3, _t0_2, 0), _t0_1, 49);
  _t0_227 = _mm256_permute2f128_pd(_mm256_shuffle_pd(_t0_3, _t0_2, 12), _mm256_shuffle_pd(_t0_1, _t0_0, 12), 49);

  // 4-BLAC: 4x4 + 4x4
  _t0_59 = _mm256_add_pd(_t0_123, _t0_224);
  _t0_60 = _mm256_add_pd(_t0_124, _t0_225);
  _t0_61 = _mm256_add_pd(_t0_125, _t0_226);
  _t0_62 = _mm256_add_pd(_t0_126, _t0_227);

  // AVX Storer:

  // 4x4 -> 4x4 - UpSymm
  _t0_68 = _t0_59;
  _t0_69 = _t0_60;
  _t0_70 = _t0_61;
  _t0_71 = _t0_62;

  // Generating : U[4,4] = S(h(1, 4, 0), Sqrt( G(h(1, 4, 0), U[4,4],h(1, 4, 0)) ),h(1, 4, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_265 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_68, 1);

  // 4-BLAC: sqrt(1x4)
  _t0_281 = _mm256_castpd128_pd256(_mm_sqrt_pd(_mm256_castpd256_pd128(_t0_265)));

  // AVX Storer:
  _t0_72 = _t0_281;

  // Generating : T649[1,4] = S(h(1, 1, 0), ( G(h(1, 1, 0), 1[1,1],h(1, 1, 0)) Div G(h(1, 4, 0), U[4,4],h(1, 4, 0)) ),h(1, 4, 0))

  // AVX Loader:

  // Constant 1x1 -> 1x4
  _t0_307 = _mm256_set_pd(0, 0, 0, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_308 = _t0_72;

  // 4-BLAC: 1x4 / 1x4
  _t0_309 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_307), _mm256_castpd256_pd128(_t0_308)));

  // AVX Storer:
  _t0_73 = _t0_309;

  // Generating : U[4,4] = S(h(1, 4, 0), ( G(h(1, 1, 0), T649[1,4],h(1, 4, 0)) Kro G(h(1, 4, 0), U[4,4],h(3, 4, 1)) ),h(3, 4, 1))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_310 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_73, _t0_73, 32), _mm256_permute2f128_pd(_t0_73, _t0_73, 32), 0);

  // AVX Loader:

  // 1x3 -> 1x4
  _t0_311 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_68, 14), _mm256_permute2f128_pd(_t0_68, _t0_68, 129), 5);

  // 4-BLAC: 1x4 Kro 1x4
  _t0_312 = _mm256_mul_pd(_t0_310, _t0_311);

  // AVX Storer:
  _t0_74 = _t0_312;

  // Generating : U[4,4] = S(h(3, 4, 1), ( G(h(3, 4, 1), U[4,4],h(3, 4, 1)) - ( T( G(h(1, 4, 0), U[4,4],h(3, 4, 1)) ) * G(h(1, 4, 0), U[4,4],h(3, 4, 1)) ) ),h(3, 4, 1))

  // AVX Loader:

  // 3x3 -> 4x4 - UpperTriang
  _t0_313 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_69, 14), _mm256_permute2f128_pd(_t0_69, _t0_69, 129), 5);
  _t0_314 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_70, 12), _mm256_permute2f128_pd(_t0_70, _t0_70, 129), 5);
  _t0_315 = _mm256_unpackhi_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_71, 8), _mm256_setzero_pd());
  _t0_316 = _mm256_setzero_pd();

  // AVX Loader:

  // 1x3 -> 1x4
  _t0_317 = _t0_74;

  // 4-BLAC: (1x4)^T
  _t0_318 = _t0_317;

  // AVX Loader:

  // 1x3 -> 1x4
  _t0_319 = _t0_74;

  // 4-BLAC: 4x1 * 1x4
  _t0_320 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_318, _t0_318, 32), _mm256_permute2f128_pd(_t0_318, _t0_318, 32), 0), _t0_319);
  _t0_321 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_318, _t0_318, 32), _mm256_permute2f128_pd(_t0_318, _t0_318, 32), 15), _t0_319);
  _t0_322 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_318, _t0_318, 49), _mm256_permute2f128_pd(_t0_318, _t0_318, 49), 0), _t0_319);
  _t0_323 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_318, _t0_318, 49), _mm256_permute2f128_pd(_t0_318, _t0_318, 49), 15), _t0_319);

  // 4-BLAC: 4x4 - 4x4
  _t0_324 = _mm256_sub_pd(_t0_313, _t0_320);
  _t0_325 = _mm256_sub_pd(_t0_314, _t0_321);
  _t0_326 = _mm256_sub_pd(_t0_315, _t0_322);
  _t0_327 = _mm256_sub_pd(_t0_316, _t0_323);

  // AVX Storer:

  // 4x4 -> 3x3 - UpTriang
  _t0_75 = _t0_324;
  _t0_76 = _t0_325;
  _t0_77 = _t0_326;

  // Generating : U[4,4] = S(h(1, 4, 1), Sqrt( G(h(1, 4, 1), U[4,4],h(1, 4, 1)) ),h(1, 4, 1))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_328 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_75, 1);

  // 4-BLAC: sqrt(1x4)
  _t0_329 = _mm256_castpd128_pd256(_mm_sqrt_pd(_mm256_castpd256_pd128(_t0_328)));

  // AVX Storer:
  _t0_78 = _t0_329;

  // Generating : T649[1,4] = S(h(1, 1, 0), ( G(h(1, 1, 0), 1[1,1],h(1, 1, 0)) Div G(h(1, 4, 1), U[4,4],h(1, 4, 1)) ),h(1, 4, 1))

  // AVX Loader:

  // Constant 1x1 -> 1x4
  _t0_330 = _mm256_set_pd(0, 0, 0, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_331 = _t0_78;

  // 4-BLAC: 1x4 / 1x4
  _t0_332 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_330), _mm256_castpd256_pd128(_t0_331)));

  // AVX Storer:
  _t0_79 = _t0_332;

  // Generating : U[4,4] = S(h(1, 4, 1), ( G(h(1, 1, 0), T649[1,4],h(1, 4, 1)) Kro G(h(1, 4, 1), U[4,4],h(2, 4, 2)) ),h(2, 4, 2))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_333 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_79, _t0_79, 32), _mm256_permute2f128_pd(_t0_79, _t0_79, 32), 0);

  // AVX Loader:

  // 1x2 -> 1x4
  _t0_334 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_75, 6), _mm256_permute2f128_pd(_t0_75, _t0_75, 129), 5);

  // 4-BLAC: 1x4 Kro 1x4
  _t0_335 = _mm256_mul_pd(_t0_333, _t0_334);

  // AVX Storer:
  _t0_80 = _t0_335;

  // Generating : U[4,4] = S(h(2, 4, 2), ( G(h(2, 4, 2), U[4,4],h(2, 4, 2)) - ( T( G(h(1, 4, 1), U[4,4],h(2, 4, 2)) ) * G(h(1, 4, 1), U[4,4],h(2, 4, 2)) ) ),h(2, 4, 2))

  // AVX Loader:

  // 2x2 -> 4x4 - UpperTriang
  _t0_336 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_76, 6), _mm256_permute2f128_pd(_t0_76, _t0_76, 129), 5);
  _t0_337 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_77, 4), _mm256_permute2f128_pd(_t0_77, _t0_77, 129), 5);
  _t0_338 = _mm256_setzero_pd();
  _t0_339 = _mm256_setzero_pd();

  // AVX Loader:

  // 1x2 -> 1x4
  _t0_340 = _t0_80;

  // 4-BLAC: (1x4)^T
  _t0_341 = _t0_340;

  // AVX Loader:

  // 1x2 -> 1x4
  _t0_342 = _t0_80;

  // 4-BLAC: 4x1 * 1x4
  _t0_343 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_341, _t0_341, 32), _mm256_permute2f128_pd(_t0_341, _t0_341, 32), 0), _t0_342);
  _t0_344 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_341, _t0_341, 32), _mm256_permute2f128_pd(_t0_341, _t0_341, 32), 15), _t0_342);
  _t0_345 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_341, _t0_341, 49), _mm256_permute2f128_pd(_t0_341, _t0_341, 49), 0), _t0_342);
  _t0_346 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_341, _t0_341, 49), _mm256_permute2f128_pd(_t0_341, _t0_341, 49), 15), _t0_342);

  // 4-BLAC: 4x4 - 4x4
  _t0_347 = _mm256_sub_pd(_t0_336, _t0_343);
  _t0_348 = _mm256_sub_pd(_t0_337, _t0_344);
  _t0_349 = _mm256_sub_pd(_t0_338, _t0_345);
  _t0_350 = _mm256_sub_pd(_t0_339, _t0_346);

  // AVX Storer:

  // 4x4 -> 2x2 - UpTriang
  _t0_81 = _t0_347;
  _t0_82 = _t0_348;

  // Generating : U[4,4] = S(h(1, 4, 2), Sqrt( G(h(1, 4, 2), U[4,4],h(1, 4, 2)) ),h(1, 4, 2))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_351 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_81, 1);

  // 4-BLAC: sqrt(1x4)
  _t0_352 = _mm256_castpd128_pd256(_mm_sqrt_pd(_mm256_castpd256_pd128(_t0_351)));

  // AVX Storer:
  _t0_83 = _t0_352;

  // Generating : U[4,4] = S(h(1, 4, 2), ( G(h(1, 4, 2), U[4,4],h(1, 4, 3)) Div G(h(1, 4, 2), U[4,4],h(1, 4, 2)) ),h(1, 4, 3))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_353 = _mm256_unpackhi_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_81, 2), _mm256_setzero_pd());

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_137 = _t0_83;

  // 4-BLAC: 1x4 / 1x4
  _t0_138 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_353), _mm256_castpd256_pd128(_t0_137)));

  // AVX Storer:
  _t0_84 = _t0_138;

  // Generating : U[4,4] = S(h(1, 4, 3), ( G(h(1, 4, 3), U[4,4],h(1, 4, 3)) - ( T( G(h(1, 4, 2), U[4,4],h(1, 4, 3)) ) Kro G(h(1, 4, 2), U[4,4],h(1, 4, 3)) ) ),h(1, 4, 3))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_139 = _mm256_unpackhi_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_82, 2), _mm256_setzero_pd());

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_140 = _t0_84;

  // 4-BLAC: (4x1)^T
  _t0_141 = _t0_140;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_142 = _t0_84;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_143 = _mm256_mul_pd(_t0_141, _t0_142);

  // 4-BLAC: 1x4 - 1x4
  _t0_144 = _mm256_sub_pd(_t0_139, _t0_143);

  // AVX Storer:
  _t0_85 = _t0_144;

  // Generating : U[4,4] = S(h(1, 4, 3), Sqrt( G(h(1, 4, 3), U[4,4],h(1, 4, 3)) ),h(1, 4, 3))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_145 = _t0_85;

  // 4-BLAC: sqrt(1x4)
  _t0_146 = _mm256_castpd128_pd256(_mm_sqrt_pd(_mm256_castpd256_pd128(_t0_145)));

  // AVX Storer:
  _t0_85 = _t0_146;

  // Generating : v2[4,1] = S(h(1, 4, 0), ( G(h(1, 4, 0), v2[4,1],h(1, 1, 0)) Div G(h(1, 4, 0), U0[4,4],h(1, 4, 0)) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_147 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_132, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_148 = _t0_72;

  // 4-BLAC: 1x4 / 1x4
  _t0_149 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_147), _mm256_castpd256_pd128(_t0_148)));

  // AVX Storer:
  _t0_86 = _t0_149;

  // Generating : v2[4,1] = S(h(3, 4, 1), ( G(h(3, 4, 1), v2[4,1],h(1, 1, 0)) - ( T( G(h(1, 4, 0), U0[4,4],h(3, 4, 1)) ) Kro G(h(1, 4, 0), v2[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // 3x1 -> 4x1
  _t0_150 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_132, 14), _mm256_permute2f128_pd(_t0_132, _t0_132, 129), 5);

  // AVX Loader:

  // 1x3 -> 1x4
  _t0_151 = _t0_74;

  // 4-BLAC: (1x4)^T
  _t0_152 = _t0_151;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_153 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_86, _t0_86, 32), _mm256_permute2f128_pd(_t0_86, _t0_86, 32), 0);

  // 4-BLAC: 4x1 Kro 1x4
  _t0_154 = _mm256_mul_pd(_t0_152, _t0_153);

  // 4-BLAC: 4x1 - 4x1
  _t0_155 = _mm256_sub_pd(_t0_150, _t0_154);

  // AVX Storer:
  _t0_87 = _t0_155;

  // Generating : v2[4,1] = S(h(1, 4, 1), ( G(h(1, 4, 1), v2[4,1],h(1, 1, 0)) Div G(h(1, 4, 1), U0[4,4],h(1, 4, 1)) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_156 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_87, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_157 = _t0_78;

  // 4-BLAC: 1x4 / 1x4
  _t0_158 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_156), _mm256_castpd256_pd128(_t0_157)));

  // AVX Storer:
  _t0_88 = _t0_158;

  // Generating : v2[4,1] = S(h(2, 4, 2), ( G(h(2, 4, 2), v2[4,1],h(1, 1, 0)) - ( T( G(h(1, 4, 1), U0[4,4],h(2, 4, 2)) ) Kro G(h(1, 4, 1), v2[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // 2x1 -> 4x1
  _t0_159 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_87, 6), _mm256_permute2f128_pd(_t0_87, _t0_87, 129), 5);

  // AVX Loader:

  // 1x2 -> 1x4
  _t0_160 = _t0_80;

  // 4-BLAC: (1x4)^T
  _t0_161 = _t0_160;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_162 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_88, _t0_88, 32), _mm256_permute2f128_pd(_t0_88, _t0_88, 32), 0);

  // 4-BLAC: 4x1 Kro 1x4
  _t0_163 = _mm256_mul_pd(_t0_161, _t0_162);

  // 4-BLAC: 4x1 - 4x1
  _t0_168 = _mm256_sub_pd(_t0_159, _t0_163);

  // AVX Storer:
  _t0_89 = _t0_168;

  // Generating : v2[4,1] = S(h(1, 4, 2), ( G(h(1, 4, 2), v2[4,1],h(1, 1, 0)) Div G(h(1, 4, 2), U0[4,4],h(1, 4, 2)) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_169 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_89, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_170 = _t0_83;

  // 4-BLAC: 1x4 / 1x4
  _t0_171 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_169), _mm256_castpd256_pd128(_t0_170)));

  // AVX Storer:
  _t0_90 = _t0_171;

  // Generating : v2[4,1] = S(h(1, 4, 3), ( G(h(1, 4, 3), v2[4,1],h(1, 1, 0)) - ( T( G(h(1, 4, 2), U0[4,4],h(1, 4, 3)) ) Kro G(h(1, 4, 2), v2[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_172 = _mm256_unpackhi_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_89, 2), _mm256_setzero_pd());

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_173 = _t0_84;

  // 4-BLAC: (4x1)^T
  _t0_174 = _t0_173;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_175 = _t0_90;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_176 = _mm256_mul_pd(_t0_174, _t0_175);

  // 4-BLAC: 1x4 - 1x4
  _t0_177 = _mm256_sub_pd(_t0_172, _t0_176);

  // AVX Storer:
  _t0_91 = _t0_177;

  // Generating : v2[4,1] = S(h(1, 4, 3), ( G(h(1, 4, 3), v2[4,1],h(1, 1, 0)) Div G(h(1, 4, 3), U0[4,4],h(1, 4, 3)) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_178 = _t0_91;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_179 = _t0_85;

  // 4-BLAC: 1x4 / 1x4
  _t0_180 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_178), _mm256_castpd256_pd128(_t0_179)));

  // AVX Storer:
  _t0_91 = _t0_180;

  // Generating : v4[4,1] = S(h(1, 4, 3), ( G(h(1, 4, 3), v4[4,1],h(1, 1, 0)) Div G(h(1, 4, 3), U0[4,4],h(1, 4, 3)) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_185 = _t0_91;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_186 = _t0_85;

  // 4-BLAC: 1x4 / 1x4
  _t0_187 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_185), _mm256_castpd256_pd128(_t0_186)));

  // AVX Storer:
  _t0_91 = _t0_187;

  // Generating : v4[4,1] = S(h(3, 4, 0), ( G(h(3, 4, 0), v4[4,1],h(1, 1, 0)) - ( G(h(3, 4, 0), U0[4,4],h(1, 4, 3)) Kro G(h(1, 4, 3), v4[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // 3x1 -> 4x1
  _t0_188 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_86, _t0_88), _mm256_unpacklo_pd(_t0_90, _mm256_setzero_pd()), 32);

  // AVX Loader:

  // 3x1 -> 4x1
  _t0_189 = _mm256_blend_pd(_mm256_permute2f128_pd(_t0_74, _t0_84, 33), _mm256_blend_pd(_mm256_setzero_pd(), _t0_80, 2), 10);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_190 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_91, _t0_91, 32), _mm256_permute2f128_pd(_t0_91, _t0_91, 32), 0);

  // 4-BLAC: 4x1 Kro 1x4
  _t0_191 = _mm256_mul_pd(_t0_189, _t0_190);

  // 4-BLAC: 4x1 - 4x1
  _t0_192 = _mm256_sub_pd(_t0_188, _t0_191);

  // AVX Storer:
  _t0_92 = _t0_192;

  // Generating : v4[4,1] = S(h(1, 4, 2), ( G(h(1, 4, 2), v4[4,1],h(1, 1, 0)) Div G(h(1, 4, 2), U0[4,4],h(1, 4, 2)) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_193 = _mm256_permute2f128_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_92, 4), _mm256_blend_pd(_mm256_setzero_pd(), _t0_92, 4), 129);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_198 = _t0_83;

  // 4-BLAC: 1x4 / 1x4
  _t0_199 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_193), _mm256_castpd256_pd128(_t0_198)));

  // AVX Storer:
  _t0_90 = _t0_199;

  // Generating : v4[4,1] = S(h(2, 4, 0), ( G(h(2, 4, 0), v4[4,1],h(1, 1, 0)) - ( G(h(2, 4, 0), U0[4,4],h(1, 4, 2)) Kro G(h(1, 4, 2), v4[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // 2x1 -> 4x1
  _t0_200 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_92, 3);

  // AVX Loader:

  // 2x1 -> 4x1
  _t0_201 = _mm256_shuffle_pd(_mm256_blend_pd(_t0_74, _mm256_setzero_pd(), 12), _mm256_blend_pd(_t0_80, _mm256_setzero_pd(), 12), 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_202 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_90, _t0_90, 32), _mm256_permute2f128_pd(_t0_90, _t0_90, 32), 0);

  // 4-BLAC: 4x1 Kro 1x4
  _t0_203 = _mm256_mul_pd(_t0_201, _t0_202);

  // 4-BLAC: 4x1 - 4x1
  _t0_204 = _mm256_sub_pd(_t0_200, _t0_203);

  // AVX Storer:
  _t0_93 = _t0_204;

  // Generating : v4[4,1] = S(h(1, 4, 1), ( G(h(1, 4, 1), v4[4,1],h(1, 1, 0)) Div G(h(1, 4, 1), U0[4,4],h(1, 4, 1)) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_205 = _mm256_unpackhi_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_93, 2), _mm256_setzero_pd());

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_206 = _t0_78;

  // 4-BLAC: 1x4 / 1x4
  _t0_211 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_205), _mm256_castpd256_pd128(_t0_206)));

  // AVX Storer:
  _t0_88 = _t0_211;

  // Generating : v4[4,1] = S(h(1, 4, 0), ( G(h(1, 4, 0), v4[4,1],h(1, 1, 0)) - ( G(h(1, 4, 0), U0[4,4],h(1, 4, 1)) Kro G(h(1, 4, 1), v4[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_212 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_93, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_213 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_74, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_214 = _t0_88;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_215 = _mm256_mul_pd(_t0_213, _t0_214);

  // 4-BLAC: 1x4 - 1x4
  _t0_216 = _mm256_sub_pd(_t0_212, _t0_215);

  // AVX Storer:
  _t0_86 = _t0_216;

  // Generating : v4[4,1] = S(h(1, 4, 0), ( G(h(1, 4, 0), v4[4,1],h(1, 1, 0)) Div G(h(1, 4, 0), U0[4,4],h(1, 4, 0)) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_217 = _t0_86;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_218 = _t0_72;

  // 4-BLAC: 1x4 / 1x4
  _t0_219 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_217), _mm256_castpd256_pd128(_t0_218)));

  // AVX Storer:
  _t0_86 = _t0_219;

  // Generating : T660[1,4] = S(h(1, 1, 0), ( G(h(1, 1, 0), 1[1,1],h(1, 1, 0)) Div G(h(1, 4, 0), U0[4,4],h(1, 4, 0)) ),h(1, 4, 0))

  // AVX Loader:

  // Constant 1x1 -> 1x4
  _t0_220 = _mm256_set_pd(0, 0, 0, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_221 = _t0_72;

  // 4-BLAC: 1x4 / 1x4
  _t0_222 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_220), _mm256_castpd256_pd128(_t0_221)));

  // AVX Storer:
  _t0_94 = _t0_222;

  // Generating : M6[4,4] = S(h(1, 4, 0), ( G(h(1, 1, 0), T660[1,4],h(1, 4, 0)) Kro G(h(1, 4, 0), M6[4,4],h(4, 4, 0)) ),h(4, 4, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_223 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_94, _t0_94, 32), _mm256_permute2f128_pd(_t0_94, _t0_94, 32), 0);

  // AVX Loader:

  // 4-BLAC: 1x4 Kro 1x4
  _t0_115 = _mm256_mul_pd(_t0_223, _t0_115);

  // AVX Storer:

  // Generating : M6[4,4] = S(h(3, 4, 1), ( G(h(3, 4, 1), M6[4,4],h(4, 4, 0)) - ( T( G(h(1, 4, 0), U0[4,4],h(3, 4, 1)) ) * G(h(1, 4, 0), M6[4,4],h(4, 4, 0)) ) ),h(4, 4, 0))

  // AVX Loader:

  // 3x4 -> 4x4
  _t0_228 = _t0_116;
  _t0_229 = _t0_117;
  _t0_230 = _t0_118;
  _t0_231 = _mm256_setzero_pd();

  // AVX Loader:

  // 1x3 -> 1x4
  _t0_232 = _t0_74;

  // 4-BLAC: (1x4)^T
  _t0_233 = _t0_232;

  // AVX Loader:

  // 4-BLAC: 4x1 * 1x4
  _t0_234 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_233, _t0_233, 32), _mm256_permute2f128_pd(_t0_233, _t0_233, 32), 0), _t0_115);
  _t0_235 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_233, _t0_233, 32), _mm256_permute2f128_pd(_t0_233, _t0_233, 32), 15), _t0_115);
  _t0_236 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_233, _t0_233, 49), _mm256_permute2f128_pd(_t0_233, _t0_233, 49), 0), _t0_115);
  _t0_237 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_233, _t0_233, 49), _mm256_permute2f128_pd(_t0_233, _t0_233, 49), 15), _t0_115);

  // 4-BLAC: 4x4 - 4x4
  _t0_238 = _mm256_sub_pd(_t0_228, _t0_234);
  _t0_239 = _mm256_sub_pd(_t0_229, _t0_235);
  _t0_240 = _mm256_sub_pd(_t0_230, _t0_236);
  _t0_241 = _mm256_sub_pd(_t0_231, _t0_237);

  // AVX Storer:
  _t0_116 = _t0_238;
  _t0_117 = _t0_239;
  _t0_118 = _t0_240;

  // Generating : T660[1,4] = S(h(1, 1, 0), ( G(h(1, 1, 0), 1[1,1],h(1, 1, 0)) Div G(h(1, 4, 1), U0[4,4],h(1, 4, 1)) ),h(1, 4, 1))

  // AVX Loader:

  // Constant 1x1 -> 1x4
  _t0_242 = _mm256_set_pd(0, 0, 0, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_243 = _t0_78;

  // 4-BLAC: 1x4 / 1x4
  _t0_244 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_242), _mm256_castpd256_pd128(_t0_243)));

  // AVX Storer:
  _t0_95 = _t0_244;

  // Generating : M6[4,4] = S(h(1, 4, 1), ( G(h(1, 1, 0), T660[1,4],h(1, 4, 1)) Kro G(h(1, 4, 1), M6[4,4],h(4, 4, 0)) ),h(4, 4, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_245 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_95, _t0_95, 32), _mm256_permute2f128_pd(_t0_95, _t0_95, 32), 0);

  // AVX Loader:

  // 4-BLAC: 1x4 Kro 1x4
  _t0_116 = _mm256_mul_pd(_t0_245, _t0_116);

  // AVX Storer:

  // Generating : M6[4,4] = S(h(2, 4, 2), ( G(h(2, 4, 2), M6[4,4],h(4, 4, 0)) - ( T( G(h(1, 4, 1), U0[4,4],h(2, 4, 2)) ) * G(h(1, 4, 1), M6[4,4],h(4, 4, 0)) ) ),h(4, 4, 0))

  // AVX Loader:

  // 2x4 -> 4x4
  _t0_246 = _t0_117;
  _t0_247 = _t0_118;
  _t0_248 = _mm256_setzero_pd();
  _t0_249 = _mm256_setzero_pd();

  // AVX Loader:

  // 1x2 -> 1x4
  _t0_250 = _t0_80;

  // 4-BLAC: (1x4)^T
  _t0_251 = _t0_250;

  // AVX Loader:

  // 4-BLAC: 4x1 * 1x4
  _t0_252 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_251, _t0_251, 32), _mm256_permute2f128_pd(_t0_251, _t0_251, 32), 0), _t0_116);
  _t0_253 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_251, _t0_251, 32), _mm256_permute2f128_pd(_t0_251, _t0_251, 32), 15), _t0_116);
  _t0_254 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_251, _t0_251, 49), _mm256_permute2f128_pd(_t0_251, _t0_251, 49), 0), _t0_116);
  _t0_255 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_251, _t0_251, 49), _mm256_permute2f128_pd(_t0_251, _t0_251, 49), 15), _t0_116);

  // 4-BLAC: 4x4 - 4x4
  _t0_256 = _mm256_sub_pd(_t0_246, _t0_252);
  _t0_257 = _mm256_sub_pd(_t0_247, _t0_253);
  _t0_258 = _mm256_sub_pd(_t0_248, _t0_254);
  _t0_259 = _mm256_sub_pd(_t0_249, _t0_255);

  // AVX Storer:
  _t0_117 = _t0_256;
  _t0_118 = _t0_257;

  // Generating : T660[1,4] = S(h(1, 1, 0), ( G(h(1, 1, 0), 1[1,1],h(1, 1, 0)) Div G(h(1, 4, 2), U0[4,4],h(1, 4, 2)) ),h(1, 4, 2))

  // AVX Loader:

  // Constant 1x1 -> 1x4
  _t0_260 = _mm256_set_pd(0, 0, 0, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_261 = _t0_83;

  // 4-BLAC: 1x4 / 1x4
  _t0_262 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_260), _mm256_castpd256_pd128(_t0_261)));

  // AVX Storer:
  _t0_96 = _t0_262;

  // Generating : M6[4,4] = S(h(1, 4, 2), ( G(h(1, 1, 0), T660[1,4],h(1, 4, 2)) Kro G(h(1, 4, 2), M6[4,4],h(4, 4, 0)) ),h(4, 4, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_263 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_96, _t0_96, 32), _mm256_permute2f128_pd(_t0_96, _t0_96, 32), 0);

  // AVX Loader:

  // 4-BLAC: 1x4 Kro 1x4
  _t0_117 = _mm256_mul_pd(_t0_263, _t0_117);

  // AVX Storer:

  // Generating : M6[4,4] = S(h(1, 4, 3), ( G(h(1, 4, 3), M6[4,4],h(4, 4, 0)) - ( T( G(h(1, 4, 2), U0[4,4],h(1, 4, 3)) ) Kro G(h(1, 4, 2), M6[4,4],h(4, 4, 0)) ) ),h(4, 4, 0))

  // AVX Loader:

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_264 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_84, _t0_84, 32), _mm256_permute2f128_pd(_t0_84, _t0_84, 32), 0);

  // 4-BLAC: (4x1)^T
  _t0_266 = _t0_264;

  // AVX Loader:

  // 4-BLAC: 1x4 Kro 1x4
  _t0_102 = _mm256_mul_pd(_t0_266, _t0_117);

  // 4-BLAC: 1x4 - 1x4
  _t0_118 = _mm256_sub_pd(_t0_118, _t0_102);

  // AVX Storer:

  // Generating : T660[1,4] = S(h(1, 1, 0), ( G(h(1, 1, 0), 1[1,1],h(1, 1, 0)) Div G(h(1, 4, 3), U0[4,4],h(1, 4, 3)) ),h(1, 4, 3))

  // AVX Loader:

  // Constant 1x1 -> 1x4
  _t0_267 = _mm256_set_pd(0, 0, 0, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_268 = _t0_85;

  // 4-BLAC: 1x4 / 1x4
  _t0_269 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_267), _mm256_castpd256_pd128(_t0_268)));

  // AVX Storer:
  _t0_97 = _t0_269;

  // Generating : M6[4,4] = S(h(1, 4, 3), ( G(h(1, 1, 0), T660[1,4],h(1, 4, 3)) Kro G(h(1, 4, 3), M6[4,4],h(4, 4, 0)) ),h(4, 4, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_270 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_97, _t0_97, 32), _mm256_permute2f128_pd(_t0_97, _t0_97, 32), 0);

  // AVX Loader:

  // 4-BLAC: 1x4 Kro 1x4
  _t0_118 = _mm256_mul_pd(_t0_270, _t0_118);

  // AVX Storer:

  // Generating : M8[4,4] = S(h(1, 4, 3), ( G(h(1, 1, 0), T660[1,4],h(1, 4, 3)) Kro G(h(1, 4, 3), M8[4,4],h(4, 4, 0)) ),h(4, 4, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_271 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_97, _t0_97, 32), _mm256_permute2f128_pd(_t0_97, _t0_97, 32), 0);

  // AVX Loader:

  // 4-BLAC: 1x4 Kro 1x4
  _t0_118 = _mm256_mul_pd(_t0_271, _t0_118);

  // AVX Storer:

  // Generating : M8[4,4] = S(h(3, 4, 0), ( G(h(3, 4, 0), M8[4,4],h(4, 4, 0)) - ( G(h(3, 4, 0), U0[4,4],h(1, 4, 3)) * G(h(1, 4, 3), M8[4,4],h(4, 4, 0)) ) ),h(4, 4, 0))

  // AVX Loader:

  // 3x4 -> 4x4
  _t0_272 = _t0_115;
  _t0_273 = _t0_116;
  _t0_274 = _t0_117;
  _t0_275 = _mm256_setzero_pd();

  // AVX Loader:

  // 3x1 -> 4x1
  _t0_276 = _mm256_blend_pd(_mm256_permute2f128_pd(_t0_74, _t0_84, 33), _mm256_blend_pd(_mm256_setzero_pd(), _t0_80, 2), 10);

  // AVX Loader:

  // 4-BLAC: 4x1 * 1x4
  _t0_277 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_276, _t0_276, 32), _mm256_permute2f128_pd(_t0_276, _t0_276, 32), 0), _t0_118);
  _t0_278 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_276, _t0_276, 32), _mm256_permute2f128_pd(_t0_276, _t0_276, 32), 15), _t0_118);
  _t0_279 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_276, _t0_276, 49), _mm256_permute2f128_pd(_t0_276, _t0_276, 49), 0), _t0_118);
  _t0_280 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_276, _t0_276, 49), _mm256_permute2f128_pd(_t0_276, _t0_276, 49), 15), _t0_118);

  // 4-BLAC: 4x4 - 4x4
  _t0_282 = _mm256_sub_pd(_t0_272, _t0_277);
  _t0_283 = _mm256_sub_pd(_t0_273, _t0_278);
  _t0_284 = _mm256_sub_pd(_t0_274, _t0_279);
  _t0_285 = _mm256_sub_pd(_t0_275, _t0_280);

  // AVX Storer:
  _t0_115 = _t0_282;
  _t0_116 = _t0_283;
  _t0_117 = _t0_284;

  // Generating : M8[4,4] = S(h(1, 4, 2), ( G(h(1, 1, 0), T660[1,4],h(1, 4, 2)) Kro G(h(1, 4, 2), M8[4,4],h(4, 4, 0)) ),h(4, 4, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_286 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_96, _t0_96, 32), _mm256_permute2f128_pd(_t0_96, _t0_96, 32), 0);

  // AVX Loader:

  // 4-BLAC: 1x4 Kro 1x4
  _t0_117 = _mm256_mul_pd(_t0_286, _t0_117);

  // AVX Storer:

  // Generating : M8[4,4] = S(h(2, 4, 0), ( G(h(2, 4, 0), M8[4,4],h(4, 4, 0)) - ( G(h(2, 4, 0), U0[4,4],h(1, 4, 2)) * G(h(1, 4, 2), M8[4,4],h(4, 4, 0)) ) ),h(4, 4, 0))

  // AVX Loader:

  // 2x4 -> 4x4
  _t0_287 = _t0_115;
  _t0_288 = _t0_116;
  _t0_289 = _mm256_setzero_pd();
  _t0_290 = _mm256_setzero_pd();

  // AVX Loader:

  // 2x1 -> 4x1
  _t0_291 = _mm256_shuffle_pd(_mm256_blend_pd(_t0_74, _mm256_setzero_pd(), 12), _mm256_blend_pd(_t0_80, _mm256_setzero_pd(), 12), 1);

  // AVX Loader:

  // 4-BLAC: 4x1 * 1x4
  _t0_292 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_291, _t0_291, 32), _mm256_permute2f128_pd(_t0_291, _t0_291, 32), 0), _t0_117);
  _t0_293 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_291, _t0_291, 32), _mm256_permute2f128_pd(_t0_291, _t0_291, 32), 15), _t0_117);
  _t0_294 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_291, _t0_291, 49), _mm256_permute2f128_pd(_t0_291, _t0_291, 49), 0), _t0_117);
  _t0_295 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_291, _t0_291, 49), _mm256_permute2f128_pd(_t0_291, _t0_291, 49), 15), _t0_117);

  // 4-BLAC: 4x4 - 4x4
  _t0_296 = _mm256_sub_pd(_t0_287, _t0_292);
  _t0_297 = _mm256_sub_pd(_t0_288, _t0_293);
  _t0_298 = _mm256_sub_pd(_t0_289, _t0_294);
  _t0_299 = _mm256_sub_pd(_t0_290, _t0_295);

  // AVX Storer:
  _t0_115 = _t0_296;
  _t0_116 = _t0_297;

  // Generating : M8[4,4] = S(h(1, 4, 1), ( G(h(1, 1, 0), T660[1,4],h(1, 4, 1)) Kro G(h(1, 4, 1), M8[4,4],h(4, 4, 0)) ),h(4, 4, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_300 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_95, _t0_95, 32), _mm256_permute2f128_pd(_t0_95, _t0_95, 32), 0);

  // AVX Loader:

  // 4-BLAC: 1x4 Kro 1x4
  _t0_116 = _mm256_mul_pd(_t0_300, _t0_116);

  // AVX Storer:

  // Generating : M8[4,4] = S(h(1, 4, 0), ( G(h(1, 4, 0), M8[4,4],h(4, 4, 0)) - ( G(h(1, 4, 0), U0[4,4],h(1, 4, 1)) Kro G(h(1, 4, 1), M8[4,4],h(4, 4, 0)) ) ),h(4, 4, 0))

  // AVX Loader:

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_301 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_74, _t0_74, 32), _mm256_permute2f128_pd(_t0_74, _t0_74, 32), 0);

  // AVX Loader:

  // 4-BLAC: 1x4 Kro 1x4
  _t0_103 = _mm256_mul_pd(_t0_301, _t0_116);

  // 4-BLAC: 1x4 - 1x4
  _t0_115 = _mm256_sub_pd(_t0_115, _t0_103);

  // AVX Storer:

  // Generating : M8[4,4] = S(h(1, 4, 0), ( G(h(1, 1, 0), T660[1,4],h(1, 4, 0)) Kro G(h(1, 4, 0), M8[4,4],h(4, 4, 0)) ),h(4, 4, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_302 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_94, _t0_94, 32), _mm256_permute2f128_pd(_t0_94, _t0_94, 32), 0);

  // AVX Loader:

  // 4-BLAC: 1x4 Kro 1x4
  _t0_115 = _mm256_mul_pd(_t0_302, _t0_115);

  // AVX Storer:

  // Generating : x[4,1] = S(h(4, 4, 0), ( G(h(4, 4, 0), y[4,1],h(1, 1, 0)) + ( G(h(4, 4, 0), M2[4,4],h(4, 4, 0)) * G(h(4, 4, 0), v0[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // AVX Loader:

  // AVX Loader:

  // 4-BLAC: 4x4 * 4x1
  _t0_127 = _mm256_add_pd(_mm256_permute2f128_pd(_mm256_hadd_pd(_mm256_mul_pd(_t0_119, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_86, _t0_88), _mm256_unpacklo_pd(_t0_90, _t0_91), 32)), _mm256_mul_pd(_t0_120, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_86, _t0_88), _mm256_unpacklo_pd(_t0_90, _t0_91), 32))), _mm256_hadd_pd(_mm256_mul_pd(_t0_121, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_86, _t0_88), _mm256_unpacklo_pd(_t0_90, _t0_91), 32)), _mm256_mul_pd(_t0_122, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_86, _t0_88), _mm256_unpacklo_pd(_t0_90, _t0_91), 32))), 33), _mm256_blend_pd(_mm256_hadd_pd(_mm256_mul_pd(_t0_119, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_86, _t0_88), _mm256_unpacklo_pd(_t0_90, _t0_91), 32)), _mm256_mul_pd(_t0_120, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_86, _t0_88), _mm256_unpacklo_pd(_t0_90, _t0_91), 32))), _mm256_hadd_pd(_mm256_mul_pd(_t0_121, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_86, _t0_88), _mm256_unpacklo_pd(_t0_90, _t0_91), 32)), _mm256_mul_pd(_t0_122, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_86, _t0_88), _mm256_unpacklo_pd(_t0_90, _t0_91), 32))), 12));

  // 4-BLAC: 4x1 + 4x1
  _t0_63 = _mm256_add_pd(_t0_54, _t0_127);

  // AVX Storer:

  // Generating : P[4,4] = S(h(4, 4, 0), ( G(h(4, 4, 0), Y[4,4],h(4, 4, 0)) - ( G(h(4, 4, 0), M2[4,4],h(4, 4, 0)) * G(h(4, 4, 0), M1[4,4],h(4, 4, 0)) ) ),h(4, 4, 0))

  // AVX Loader:

  // 4x4 -> 4x4 - UpSymm
  _t0_303 = _t0_64;
  _t0_304 = _mm256_blend_pd(_mm256_shuffle_pd(_t0_64, _t0_65, 3), _t0_65, 12);
  _t0_305 = _mm256_permute2f128_pd(_mm256_shuffle_pd(_t0_64, _t0_65, 0), _t0_66, 49);
  _t0_306 = _mm256_permute2f128_pd(_mm256_shuffle_pd(_t0_64, _t0_65, 12), _mm256_shuffle_pd(_t0_66, _t0_67, 12), 49);

  // AVX Loader:

  // AVX Loader:

  // 4-BLAC: 4x4 * 4x4
  _t0_128 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_119, _t0_119, 32), _mm256_permute2f128_pd(_t0_119, _t0_119, 32), 0), _t0_115), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_119, _t0_119, 32), _mm256_permute2f128_pd(_t0_119, _t0_119, 32), 15), _t0_116)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_119, _t0_119, 49), _mm256_permute2f128_pd(_t0_119, _t0_119, 49), 0), _t0_117), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_119, _t0_119, 49), _mm256_permute2f128_pd(_t0_119, _t0_119, 49), 15), _t0_118)));
  _t0_129 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_120, _t0_120, 32), _mm256_permute2f128_pd(_t0_120, _t0_120, 32), 0), _t0_115), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_120, _t0_120, 32), _mm256_permute2f128_pd(_t0_120, _t0_120, 32), 15), _t0_116)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_120, _t0_120, 49), _mm256_permute2f128_pd(_t0_120, _t0_120, 49), 0), _t0_117), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_120, _t0_120, 49), _mm256_permute2f128_pd(_t0_120, _t0_120, 49), 15), _t0_118)));
  _t0_130 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_121, _t0_121, 32), _mm256_permute2f128_pd(_t0_121, _t0_121, 32), 0), _t0_115), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_121, _t0_121, 32), _mm256_permute2f128_pd(_t0_121, _t0_121, 32), 15), _t0_116)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_121, _t0_121, 49), _mm256_permute2f128_pd(_t0_121, _t0_121, 49), 0), _t0_117), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_121, _t0_121, 49), _mm256_permute2f128_pd(_t0_121, _t0_121, 49), 15), _t0_118)));
  _t0_131 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_122, _t0_122, 32), _mm256_permute2f128_pd(_t0_122, _t0_122, 32), 0), _t0_115), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_122, _t0_122, 32), _mm256_permute2f128_pd(_t0_122, _t0_122, 32), 15), _t0_116)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_122, _t0_122, 49), _mm256_permute2f128_pd(_t0_122, _t0_122, 49), 0), _t0_117), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_122, _t0_122, 49), _mm256_permute2f128_pd(_t0_122, _t0_122, 49), 15), _t0_118)));

  // 4-BLAC: 4x4 - 4x4
  _t0_133 = _mm256_sub_pd(_t0_303, _t0_128);
  _t0_134 = _mm256_sub_pd(_t0_304, _t0_129);
  _t0_135 = _mm256_sub_pd(_t0_305, _t0_130);
  _t0_136 = _mm256_sub_pd(_t0_306, _t0_131);

  // AVX Storer:

  // 4x4 -> 4x4 - UpSymm
  _t0_98 = _t0_133;
  _t0_99 = _t0_134;
  _t0_100 = _t0_135;
  _t0_101 = _t0_136;

  _asm256_storeu_pd(y, _t0_54);
  _asm256_storeu_pd(M0, _t0_106);
  _asm256_storeu_pd(M0 + 4, _t0_107);
  _asm256_storeu_pd(M0 + 8, _t0_108);
  _asm256_storeu_pd(M0 + 12, _t0_109);
  _asm256_storeu_pd(Y, _t0_64);
  _mm256_maskstore_pd(Y + 4, _mm256_setr_epi64x(0, (__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63), _t0_65);
  _mm256_maskstore_pd(Y + 8, _mm256_setr_epi64x(0, 0, (__int64)1 << 63, (__int64)1 << 63), _t0_66);
  _mm256_maskstore_pd(Y + 12, _mm256_setr_epi64x(0, 0, 0, (__int64)1 << 63), _t0_67);
  _asm256_storeu_pd(M2, _t0_119);
  _asm256_storeu_pd(M2 + 4, _t0_120);
  _asm256_storeu_pd(M2 + 8, _t0_121);
  _asm256_storeu_pd(M2 + 12, _t0_122);
  _mm_store_sd(&(M3[0]), _mm256_castpd256_pd128(_t0_72));
  _mm256_maskstore_pd(M3 + 1, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63, 0), _t0_74);
  _mm_store_sd(&(M3[5]), _mm256_castpd256_pd128(_t0_78));
  _mm256_maskstore_pd(M3 + 6, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, 0, 0), _t0_80);
  _mm_store_sd(&(M3[10]), _mm256_castpd256_pd128(_t0_83));
  _mm_store_sd(&(M3[11]), _mm256_castpd256_pd128(_t0_84));
  _mm_store_sd(&(M3[15]), _mm256_castpd256_pd128(_t0_85));
  _mm_store_sd(&(v0[3]), _mm256_castpd256_pd128(_t0_91));
  _mm_store_sd(&(v0[2]), _mm256_castpd256_pd128(_t0_90));
  _mm_store_sd(&(v0[1]), _mm256_castpd256_pd128(_t0_88));
  _mm_store_sd(&(v0[0]), _mm256_castpd256_pd128(_t0_86));
  _asm256_storeu_pd(M1 + 12, _t0_118);
  _asm256_storeu_pd(M1 + 8, _t0_117);
  _asm256_storeu_pd(M1 + 4, _t0_116);
  _asm256_storeu_pd(M1, _t0_115);
  _asm256_storeu_pd(x, _t0_63);
  _asm256_storeu_pd(P, _t0_98);
  _mm256_maskstore_pd(P + 4, _mm256_setr_epi64x(0, (__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63), _t0_99);
  _mm256_maskstore_pd(P + 8, _mm256_setr_epi64x(0, 0, (__int64)1 << 63, (__int64)1 << 63), _t0_100);
  _mm256_maskstore_pd(P + 12, _mm256_setr_epi64x(0, 0, 0, (__int64)1 << 63), _t0_101);

}
