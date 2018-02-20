/*
 * gpr_kernel.h
 *
Decl { {u'K': Symmetric[K, (4, 4), LSMatAccess], u'L': LowerTriangular[L, (4, 4), GenMatAccess], u'var': Scalar[var, (1, 1), GenMatAccess], u'L0': LowerTriangular[L0, (4, 4), GenMatAccess], u'x': Matrix[x, (4, 1), GenMatAccess], u'X': SquaredMatrix[X, (4, 4), GenMatAccess], u'a': Matrix[a, (4, 1), GenMatAccess], u'f': Scalar[f, (1, 1), GenMatAccess], u't2': Matrix[t2, (4, 1), GenMatAccess], u't0': Matrix[t0, (4, 1), GenMatAccess], u't1': Matrix[t1, (4, 1), GenMatAccess], u'lp': Scalar[lp, (1, 1), GenMatAccess], u'v': Matrix[v, (4, 1), GenMatAccess], u'y': Matrix[y, (4, 1), GenMatAccess], 'T470': Matrix[T470, (1, 4), GenMatAccess], u'kx': Matrix[kx, (4, 1), GenMatAccess]} }
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ann: {'part_schemes': {'Assign_Mul_T_LowerTriangular_Matrix_Matrix_opt': {'m0': 'm04.ll', 'm2': 'm21.ll'}, 'Assign_Mul_LowerTriangular_Matrix_Matrix_opt': {'m0': 'm04.ll', 'm2': 'm21.ll'}, 'rdiv_ltn_ow_opt': {'m': 'm1.ll', 'n': 'n4.ll'}, 'Assign_Mul_LowerTriangular_T_LowerTriangular_Symmetric_opt': {'m0': 'm01.ll'}}, 'cl1ck_v': 1, 'variant_tag': 'Assign_Mul_LowerTriangular_Matrix_Matrix_opt_m04_m21_Assign_Mul_LowerTriangular_T_LowerTriangular_Symmetric_opt_m01_Assign_Mul_T_LowerTriangular_Matrix_Matrix_opt_m04_m21_rdiv_ltn_ow_opt_m1_n4'}

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Entry 0:
Eq: Tile( (1, 1), G(h(1, 4, 0), L[4,4],h(1, 4, 0)) ) = Sqrt( Tile( (1, 1), G(h(1, 4, 0), L[4,4],h(1, 4, 0)) ) )
Eq.ann: {}
Entry 1:
Eq: Tile( (1, 1), G(h(1, 1, 0), T470[1,4],h(1, 4, 0)) ) = ( Tile( (1, 1), 1[1,1] ) Div Tile( (1, 1), G(h(1, 4, 0), L[4,4],h(1, 4, 0)) ) )
Eq.ann: {}
Entry 2:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 1), L[4,4],h(1, 4, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 1, 0), T470[1,4],h(1, 4, 0)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 1), L[4,4],h(1, 4, 0)) ) ) )
Eq.ann: {}
Entry 3:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), L[4,4],h(1, 4, 1)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), K[4,4],h(1, 4, 1)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), L[4,4],h(1, 4, 0)) ) ) Kro T( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), L[4,4],h(1, 4, 0)) ) ) ) ) )
Eq.ann: {}
Entry 4:
Eq: Tile( (1, 1), G(h(1, 4, 1), L[4,4],h(1, 4, 1)) ) = Sqrt( Tile( (1, 1), G(h(1, 4, 1), L[4,4],h(1, 4, 1)) ) )
Eq.ann: {}
Entry 5:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), L[4,4],h(1, 4, 1)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), L[4,4],h(1, 4, 1)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), L[4,4],h(1, 4, 0)) ) ) Kro T( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), L[4,4],h(1, 4, 0)) ) ) ) ) )
Eq.ann: {}
Entry 6:
Eq: Tile( (1, 1), G(h(1, 4, 2), L[4,4],h(1, 4, 1)) ) = ( Tile( (1, 1), G(h(1, 4, 2), L[4,4],h(1, 4, 1)) ) Div Tile( (1, 1), G(h(1, 4, 1), L[4,4],h(1, 4, 1)) ) )
Eq.ann: {}
Entry 7:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), L[4,4],h(1, 4, 2)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), K[4,4],h(1, 4, 2)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), L[4,4],h(2, 4, 0)) ) ) * T( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), L[4,4],h(2, 4, 0)) ) ) ) ) )
Eq.ann: {}
Entry 8:
Eq: Tile( (1, 1), G(h(1, 4, 2), L[4,4],h(1, 4, 2)) ) = Sqrt( Tile( (1, 1), G(h(1, 4, 2), L[4,4],h(1, 4, 2)) ) )
Eq.ann: {}
Entry 9:
Eq: Tile( (1, 1), G(h(1, 4, 3), L[4,4],h(1, 4, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 3), L[4,4],h(1, 4, 0)) ) Div Tile( (1, 1), G(h(1, 4, 0), L[4,4],h(1, 4, 0)) ) )
Eq.ann: {}
Entry 10:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), L[4,4],h(2, 4, 1)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), L[4,4],h(2, 4, 1)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), L[4,4],h(1, 4, 0)) ) ) Kro T( Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 1), L[4,4],h(1, 4, 0)) ) ) ) ) )
Eq.ann: {}
Entry 11:
Eq: Tile( (1, 1), G(h(1, 4, 3), L[4,4],h(1, 4, 1)) ) = ( Tile( (1, 1), G(h(1, 4, 3), L[4,4],h(1, 4, 1)) ) Div Tile( (1, 1), G(h(1, 4, 1), L[4,4],h(1, 4, 1)) ) )
Eq.ann: {}
Entry 12:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), L[4,4],h(1, 4, 2)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), L[4,4],h(1, 4, 2)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), L[4,4],h(1, 4, 1)) ) ) Kro T( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), L[4,4],h(1, 4, 1)) ) ) ) ) )
Eq.ann: {}
Entry 13:
Eq: Tile( (1, 1), G(h(1, 4, 3), L[4,4],h(1, 4, 2)) ) = ( Tile( (1, 1), G(h(1, 4, 3), L[4,4],h(1, 4, 2)) ) Div Tile( (1, 1), G(h(1, 4, 2), L[4,4],h(1, 4, 2)) ) )
Eq.ann: {}
Entry 14:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), L[4,4],h(1, 4, 3)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), K[4,4],h(1, 4, 3)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), L[4,4],h(3, 4, 0)) ) ) * T( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), L[4,4],h(3, 4, 0)) ) ) ) ) )
Eq.ann: {}
Entry 15:
Eq: Tile( (1, 1), G(h(1, 4, 3), L[4,4],h(1, 4, 3)) ) = Sqrt( Tile( (1, 1), G(h(1, 4, 3), L[4,4],h(1, 4, 3)) ) )
Eq.ann: {}
Entry 16:
Eq: Tile( (1, 1), G(h(1, 4, 0), t0[4,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 0), t0[4,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 4, 0), L0[4,4],h(1, 4, 0)) ) )
Eq.ann: {}
Entry 17:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 1), t0[4,1],h(1, 1, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 1), t0[4,1],h(1, 1, 0)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 1), L0[4,4],h(1, 4, 0)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), t0[4,1],h(1, 1, 0)) ) ) ) )
Eq.ann: {}
Entry 18:
Eq: Tile( (1, 1), G(h(1, 4, 1), t0[4,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 1), t0[4,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 4, 1), L0[4,4],h(1, 4, 1)) ) )
Eq.ann: {}
Entry 19:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 2), t0[4,1],h(1, 1, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 2), t0[4,1],h(1, 1, 0)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 2), L0[4,4],h(1, 4, 1)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), t0[4,1],h(1, 1, 0)) ) ) ) )
Eq.ann: {}
Entry 20:
Eq: Tile( (1, 1), G(h(1, 4, 2), t0[4,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 2), t0[4,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 4, 2), L0[4,4],h(1, 4, 2)) ) )
Eq.ann: {}
Entry 21:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), t0[4,1],h(1, 1, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), t0[4,1],h(1, 1, 0)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), L0[4,4],h(1, 4, 2)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), t0[4,1],h(1, 1, 0)) ) ) ) )
Eq.ann: {}
Entry 22:
Eq: Tile( (1, 1), G(h(1, 4, 3), t0[4,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 3), t0[4,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 4, 3), L0[4,4],h(1, 4, 3)) ) )
Eq.ann: {}
Entry 23:
Eq: Tile( (1, 1), G(h(1, 4, 3), a[4,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 3), a[4,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 4, 3), L0[4,4],h(1, 4, 3)) ) )
Eq.ann: {}
Entry 24:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 0), a[4,1],h(1, 1, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 0), a[4,1],h(1, 1, 0)) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), L0[4,4],h(3, 4, 0)) ) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), a[4,1],h(1, 1, 0)) ) ) ) )
Eq.ann: {}
Entry 25:
Eq: Tile( (1, 1), G(h(1, 4, 2), a[4,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 2), a[4,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 4, 2), L0[4,4],h(1, 4, 2)) ) )
Eq.ann: {}
Entry 26:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 0), a[4,1],h(1, 1, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 0), a[4,1],h(1, 1, 0)) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), L0[4,4],h(2, 4, 0)) ) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), a[4,1],h(1, 1, 0)) ) ) ) )
Eq.ann: {}
Entry 27:
Eq: Tile( (1, 1), G(h(1, 4, 1), a[4,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 1), a[4,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 4, 1), L0[4,4],h(1, 4, 1)) ) )
Eq.ann: {}
Entry 28:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), a[4,1],h(1, 1, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), a[4,1],h(1, 1, 0)) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), L0[4,4],h(1, 4, 0)) ) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), a[4,1],h(1, 1, 0)) ) ) ) )
Eq.ann: {}
Entry 29:
Eq: Tile( (1, 1), G(h(1, 4, 0), a[4,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 0), a[4,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 4, 0), L0[4,4],h(1, 4, 0)) ) )
Eq.ann: {}
Entry 30:
Eq: Tile( (1, 1), Tile( (4, 4), kx[4,1] ) ) = ( Tile( (1, 1), Tile( (4, 4), X[4,4] ) ) * Tile( (1, 1), Tile( (4, 4), x[4,1] ) ) )
Eq.ann: {}
Entry 31:
Eq: Tile( (1, 1), Tile( (4, 4), f[1,1] ) ) = ( T( Tile( (1, 1), Tile( (4, 4), kx[4,1] ) ) ) * Tile( (1, 1), Tile( (4, 4), y[4,1] ) ) )
Eq.ann: {}
Entry 32:
Eq: Tile( (1, 1), G(h(1, 4, 0), v[4,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 0), v[4,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 4, 0), L0[4,4],h(1, 4, 0)) ) )
Eq.ann: {}
Entry 33:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 1), v[4,1],h(1, 1, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 1), v[4,1],h(1, 1, 0)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 1), L0[4,4],h(1, 4, 0)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), v[4,1],h(1, 1, 0)) ) ) ) )
Eq.ann: {}
Entry 34:
Eq: Tile( (1, 1), G(h(1, 4, 1), v[4,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 1), v[4,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 4, 1), L0[4,4],h(1, 4, 1)) ) )
Eq.ann: {}
Entry 35:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 2), v[4,1],h(1, 1, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 2), v[4,1],h(1, 1, 0)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 2), L0[4,4],h(1, 4, 1)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), v[4,1],h(1, 1, 0)) ) ) ) )
Eq.ann: {}
Entry 36:
Eq: Tile( (1, 1), G(h(1, 4, 2), v[4,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 2), v[4,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 4, 2), L0[4,4],h(1, 4, 2)) ) )
Eq.ann: {}
Entry 37:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), v[4,1],h(1, 1, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), v[4,1],h(1, 1, 0)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), L0[4,4],h(1, 4, 2)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), v[4,1],h(1, 1, 0)) ) ) ) )
Eq.ann: {}
Entry 38:
Eq: Tile( (1, 1), G(h(1, 4, 3), v[4,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 3), v[4,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 4, 3), L0[4,4],h(1, 4, 3)) ) )
Eq.ann: {}
Entry 39:
Eq: Tile( (1, 1), Tile( (4, 4), var[1,1] ) ) = ( ( T( Tile( (1, 1), Tile( (4, 4), x[4,1] ) ) ) * Tile( (1, 1), Tile( (4, 4), x[4,1] ) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), kx[4,1] ) ) ) * Tile( (1, 1), Tile( (4, 4), kx[4,1] ) ) ) )
Eq.ann: {}
Entry 40:
Eq: Tile( (1, 1), Tile( (4, 4), lp[1,1] ) ) = ( T( Tile( (1, 1), Tile( (4, 4), y[4,1] ) ) ) * Tile( (1, 1), Tile( (4, 4), y[4,1] ) ) )
Eq.ann: {}
 *
 * Created on: 2017-09-02
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

#define ERRTHRESH 1e-5

#define SOFTERRTHRESH 1e-7

#define NUMREP 30

#define floord(n,d) (((n)<0) ? -((-(n)+(d)-1)/(d)) : (n)/(d))
#define ceild(n,d)  (((n)<0) ? -((-(n))/(d)) : ((n)+(d)-1)/(d))
#define max(x,y)    ((x) > (y) ? (x) : (y))
#define min(x,y)    ((x) < (y) ? (x) : (y))
#define Max(x,y)    ((x) > (y) ? (x) : (y))
#define Min(x,y)    ((x) < (y) ? (x) : (y))


static __attribute__((noinline)) void kernel(double const * X, double const * x, double * K, double * y, double * kx, double * f, double * var, double * lp)
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
	_t0_184, _t0_185, _t0_186, _t0_187, _t0_188;

  _t0_5 = _mm256_castpd128_pd256(_mm_load_sd(&(K[0])));
  _t0_7 = _mm256_shuffle_pd(_mm256_castpd128_pd256(_mm_load_sd(K + 4)), _mm256_castpd128_pd256(_mm_load_sd(K + 8)), 0);
  _t0_8 = _mm256_castpd128_pd256(_mm_load_sd(&(K[5])));
  _t0_9 = _mm256_castpd128_pd256(_mm_load_sd(&(K[9])));
  _t0_10 = _mm256_castpd128_pd256(_mm_load_sd(&(K[10])));
  _t0_11 = _mm256_castpd128_pd256(_mm_load_sd(&(K[12])));
  _t0_12 = _mm256_maskload_pd(K + 13, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, 0, 0));
  _t0_15 = _mm256_castpd128_pd256(_mm_load_sd(&(K[15])));
  _t0_16 = _mm256_castpd128_pd256(_mm_load_sd(&(y[0])));
  _t0_17 = _mm256_maskload_pd(y + 1, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63, 0));
  _t0_4 = _mm256_loadu_pd(X);
  _t0_3 = _mm256_loadu_pd(X + 4);
  _t0_2 = _mm256_loadu_pd(X + 8);
  _t0_1 = _mm256_loadu_pd(X + 12);
  _t0_0 = _mm256_loadu_pd(x);

  // Generating : L[4,4] = S(h(1, 4, 0), Sqrt( G(h(1, 4, 0), L[4,4],h(1, 4, 0)) ),h(1, 4, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_179 = _t0_5;

  // 4-BLAC: sqrt(1x4)
  _t0_38 = _mm256_castpd128_pd256(_mm_sqrt_pd(_mm256_castpd256_pd128(_t0_179)));

  // AVX Storer:
  _t0_5 = _t0_38;

  // Generating : T470[1,4] = S(h(1, 1, 0), ( G(h(1, 1, 0), 1[1,1],h(1, 1, 0)) Div G(h(1, 4, 0), L[4,4],h(1, 4, 0)) ),h(1, 4, 0))

  // AVX Loader:

  // Constant 1x1 -> 1x4
  _t0_53 = _mm256_set_pd(0, 0, 0, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_58 = _t0_5;

  // 4-BLAC: 1x4 / 1x4
  _t0_73 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_53), _mm256_castpd256_pd128(_t0_58)));

  // AVX Storer:
  _t0_6 = _t0_73;

  // Generating : L[4,4] = S(h(2, 4, 1), ( G(h(1, 1, 0), T470[1,4],h(1, 4, 0)) Kro G(h(2, 4, 1), L[4,4],h(1, 4, 0)) ),h(1, 4, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_86 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_6, _t0_6, 32), _mm256_permute2f128_pd(_t0_6, _t0_6, 32), 0);

  // AVX Loader:

  // 2x1 -> 4x1
  _t0_92 = _t0_7;

  // 4-BLAC: 1x4 Kro 4x1
  _t0_106 = _mm256_mul_pd(_t0_86, _t0_92);

  // AVX Storer:
  _t0_7 = _t0_106;

  // Generating : L[4,4] = S(h(1, 4, 1), ( G(h(1, 4, 1), K[4,4],h(1, 4, 1)) - ( G(h(1, 4, 1), L[4,4],h(1, 4, 0)) Kro T( G(h(1, 4, 1), L[4,4],h(1, 4, 0)) ) ) ),h(1, 4, 1))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_120 = _t0_8;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_127 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_7, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_132 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_7, 1);

  // 4-BLAC: (4x1)^T
  _t0_141 = _t0_132;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_155 = _mm256_mul_pd(_t0_127, _t0_141);

  // 4-BLAC: 1x4 - 1x4
  _t0_156 = _mm256_sub_pd(_t0_120, _t0_155);

  // AVX Storer:
  _t0_8 = _t0_156;

  // Generating : L[4,4] = S(h(1, 4, 1), Sqrt( G(h(1, 4, 1), L[4,4],h(1, 4, 1)) ),h(1, 4, 1))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_157 = _t0_8;

  // 4-BLAC: sqrt(1x4)
  _t0_158 = _mm256_castpd128_pd256(_mm_sqrt_pd(_mm256_castpd256_pd128(_t0_157)));

  // AVX Storer:
  _t0_8 = _t0_158;

  // Generating : L[4,4] = S(h(1, 4, 2), ( G(h(1, 4, 2), L[4,4],h(1, 4, 1)) - ( G(h(1, 4, 2), L[4,4],h(1, 4, 0)) Kro T( G(h(1, 4, 1), L[4,4],h(1, 4, 0)) ) ) ),h(1, 4, 1))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_159 = _t0_9;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_160 = _mm256_unpackhi_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_7, 2), _mm256_setzero_pd());

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_161 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_7, 1);

  // 4-BLAC: (4x1)^T
  _t0_162 = _t0_161;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_163 = _mm256_mul_pd(_t0_160, _t0_162);

  // 4-BLAC: 1x4 - 1x4
  _t0_164 = _mm256_sub_pd(_t0_159, _t0_163);

  // AVX Storer:
  _t0_9 = _t0_164;

  // Generating : L[4,4] = S(h(1, 4, 2), ( G(h(1, 4, 2), L[4,4],h(1, 4, 1)) Div G(h(1, 4, 1), L[4,4],h(1, 4, 1)) ),h(1, 4, 1))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_165 = _t0_9;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_166 = _t0_8;

  // 4-BLAC: 1x4 / 1x4
  _t0_167 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_165), _mm256_castpd256_pd128(_t0_166)));

  // AVX Storer:
  _t0_9 = _t0_167;

  // Generating : L[4,4] = S(h(1, 4, 2), ( G(h(1, 4, 2), K[4,4],h(1, 4, 2)) - ( G(h(1, 4, 2), L[4,4],h(2, 4, 0)) * T( G(h(1, 4, 2), L[4,4],h(2, 4, 0)) ) ) ),h(1, 4, 2))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_168 = _t0_10;

  // AVX Loader:

  // 1x2 -> 1x4
  _t0_169 = _mm256_shuffle_pd(_mm256_blend_pd(_t0_7, _mm256_setzero_pd(), 12), _mm256_blend_pd(_t0_9, _mm256_setzero_pd(), 12), 1);

  // AVX Loader:

  // 1x2 -> 1x4
  _t0_170 = _mm256_shuffle_pd(_mm256_blend_pd(_t0_7, _mm256_setzero_pd(), 12), _mm256_blend_pd(_t0_9, _mm256_setzero_pd(), 12), 1);

  // 4-BLAC: (1x4)^T
  _t0_171 = _t0_170;

  // 4-BLAC: 1x4 * 4x1
  _t0_172 = _mm256_add_pd(_mm256_blend_pd(_mm256_add_pd(_mm256_mul_pd(_t0_169, _t0_171), _mm256_permute2f128_pd(_mm256_mul_pd(_t0_169, _t0_171), _mm256_mul_pd(_t0_169, _t0_171), 129)), _mm256_setzero_pd(), 14), _mm256_shuffle_pd(_mm256_add_pd(_mm256_mul_pd(_t0_169, _t0_171), _mm256_permute2f128_pd(_mm256_mul_pd(_t0_169, _t0_171), _mm256_mul_pd(_t0_169, _t0_171), 129)), _mm256_add_pd(_mm256_mul_pd(_t0_169, _t0_171), _mm256_permute2f128_pd(_mm256_mul_pd(_t0_169, _t0_171), _mm256_mul_pd(_t0_169, _t0_171), 129)), 1));

  // 4-BLAC: 1x4 - 1x4
  _t0_173 = _mm256_sub_pd(_t0_168, _t0_172);

  // AVX Storer:
  _t0_10 = _t0_173;

  // Generating : L[4,4] = S(h(1, 4, 2), Sqrt( G(h(1, 4, 2), L[4,4],h(1, 4, 2)) ),h(1, 4, 2))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_174 = _t0_10;

  // 4-BLAC: sqrt(1x4)
  _t0_175 = _mm256_castpd128_pd256(_mm_sqrt_pd(_mm256_castpd256_pd128(_t0_174)));

  // AVX Storer:
  _t0_10 = _t0_175;

  // Generating : L[4,4] = S(h(1, 4, 3), ( G(h(1, 4, 3), L[4,4],h(1, 4, 0)) Div G(h(1, 4, 0), L[4,4],h(1, 4, 0)) ),h(1, 4, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_176 = _t0_11;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_177 = _t0_5;

  // 4-BLAC: 1x4 / 1x4
  _t0_178 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_176), _mm256_castpd256_pd128(_t0_177)));

  // AVX Storer:
  _t0_11 = _t0_178;

  // Generating : L[4,4] = S(h(1, 4, 3), ( G(h(1, 4, 3), L[4,4],h(2, 4, 1)) - ( G(h(1, 4, 3), L[4,4],h(1, 4, 0)) Kro T( G(h(2, 4, 1), L[4,4],h(1, 4, 0)) ) ) ),h(2, 4, 1))

  // AVX Loader:

  // 1x2 -> 1x4
  _t0_180 = _t0_12;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_181 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_11, _t0_11, 32), _mm256_permute2f128_pd(_t0_11, _t0_11, 32), 0);

  // AVX Loader:

  // 2x1 -> 4x1
  _t0_182 = _t0_7;

  // 4-BLAC: (4x1)^T
  _t0_183 = _t0_182;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_184 = _mm256_mul_pd(_t0_181, _t0_183);

  // 4-BLAC: 1x4 - 1x4
  _t0_34 = _mm256_sub_pd(_t0_180, _t0_184);

  // AVX Storer:
  _t0_12 = _t0_34;

  // Generating : L[4,4] = S(h(1, 4, 3), ( G(h(1, 4, 3), L[4,4],h(1, 4, 1)) Div G(h(1, 4, 1), L[4,4],h(1, 4, 1)) ),h(1, 4, 1))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_35 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_12, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_36 = _t0_8;

  // 4-BLAC: 1x4 / 1x4
  _t0_37 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_35), _mm256_castpd256_pd128(_t0_36)));

  // AVX Storer:
  _t0_13 = _t0_37;

  // Generating : L[4,4] = S(h(1, 4, 3), ( G(h(1, 4, 3), L[4,4],h(1, 4, 2)) - ( G(h(1, 4, 3), L[4,4],h(1, 4, 1)) Kro T( G(h(1, 4, 2), L[4,4],h(1, 4, 1)) ) ) ),h(1, 4, 2))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_39 = _mm256_unpackhi_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_12, 2), _mm256_setzero_pd());

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_40 = _t0_13;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_41 = _t0_9;

  // 4-BLAC: (4x1)^T
  _t0_42 = _t0_41;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_43 = _mm256_mul_pd(_t0_40, _t0_42);

  // 4-BLAC: 1x4 - 1x4
  _t0_44 = _mm256_sub_pd(_t0_39, _t0_43);

  // AVX Storer:
  _t0_14 = _t0_44;

  // Generating : L[4,4] = S(h(1, 4, 3), ( G(h(1, 4, 3), L[4,4],h(1, 4, 2)) Div G(h(1, 4, 2), L[4,4],h(1, 4, 2)) ),h(1, 4, 2))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_45 = _t0_14;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_46 = _t0_10;

  // 4-BLAC: 1x4 / 1x4
  _t0_47 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_45), _mm256_castpd256_pd128(_t0_46)));

  // AVX Storer:
  _t0_14 = _t0_47;

  // Generating : L[4,4] = S(h(1, 4, 3), ( G(h(1, 4, 3), K[4,4],h(1, 4, 3)) - ( G(h(1, 4, 3), L[4,4],h(3, 4, 0)) * T( G(h(1, 4, 3), L[4,4],h(3, 4, 0)) ) ) ),h(1, 4, 3))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_48 = _t0_15;

  // AVX Loader:

  // 1x3 -> 1x4
  _t0_49 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_11, _t0_13), _mm256_unpacklo_pd(_t0_14, _mm256_setzero_pd()), 32);

  // AVX Loader:

  // 1x3 -> 1x4
  _t0_50 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_11, _t0_13), _mm256_unpacklo_pd(_t0_14, _mm256_setzero_pd()), 32);

  // 4-BLAC: (1x4)^T
  _t0_51 = _t0_50;

  // 4-BLAC: 1x4 * 4x1
  _t0_52 = _mm256_add_pd(_mm256_blend_pd(_mm256_add_pd(_mm256_mul_pd(_t0_49, _t0_51), _mm256_permute2f128_pd(_mm256_mul_pd(_t0_49, _t0_51), _mm256_mul_pd(_t0_49, _t0_51), 129)), _mm256_setzero_pd(), 14), _mm256_shuffle_pd(_mm256_add_pd(_mm256_mul_pd(_t0_49, _t0_51), _mm256_permute2f128_pd(_mm256_mul_pd(_t0_49, _t0_51), _mm256_mul_pd(_t0_49, _t0_51), 129)), _mm256_add_pd(_mm256_mul_pd(_t0_49, _t0_51), _mm256_permute2f128_pd(_mm256_mul_pd(_t0_49, _t0_51), _mm256_mul_pd(_t0_49, _t0_51), 129)), 1));

  // 4-BLAC: 1x4 - 1x4
  _t0_54 = _mm256_sub_pd(_t0_48, _t0_52);

  // AVX Storer:
  _t0_15 = _t0_54;

  // Generating : L[4,4] = S(h(1, 4, 3), Sqrt( G(h(1, 4, 3), L[4,4],h(1, 4, 3)) ),h(1, 4, 3))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_55 = _t0_15;

  // 4-BLAC: sqrt(1x4)
  _t0_56 = _mm256_castpd128_pd256(_mm_sqrt_pd(_mm256_castpd256_pd128(_t0_55)));

  // AVX Storer:
  _t0_15 = _t0_56;

  // Generating : t0[4,1] = S(h(1, 4, 0), ( G(h(1, 4, 0), t0[4,1],h(1, 1, 0)) Div G(h(1, 4, 0), L0[4,4],h(1, 4, 0)) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_57 = _t0_16;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_59 = _t0_5;

  // 4-BLAC: 1x4 / 1x4
  _t0_60 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_57), _mm256_castpd256_pd128(_t0_59)));

  // AVX Storer:
  _t0_16 = _t0_60;

  // Generating : t0[4,1] = S(h(3, 4, 1), ( G(h(3, 4, 1), t0[4,1],h(1, 1, 0)) - ( G(h(3, 4, 1), L0[4,4],h(1, 4, 0)) Kro G(h(1, 4, 0), t0[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // 3x1 -> 4x1
  _t0_61 = _t0_17;

  // AVX Loader:

  // 3x1 -> 4x1
  _t0_62 = _mm256_blend_pd(_mm256_permute2f128_pd(_mm256_blend_pd(_t0_7, _t0_7, 2), _t0_11, 32), _mm256_setzero_pd(), 8);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_63 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_16, _t0_16, 32), _mm256_permute2f128_pd(_t0_16, _t0_16, 32), 0);

  // 4-BLAC: 4x1 Kro 1x4
  _t0_64 = _mm256_mul_pd(_t0_62, _t0_63);

  // 4-BLAC: 4x1 - 4x1
  _t0_65 = _mm256_sub_pd(_t0_61, _t0_64);

  // AVX Storer:
  _t0_17 = _t0_65;

  // Generating : t0[4,1] = S(h(1, 4, 1), ( G(h(1, 4, 1), t0[4,1],h(1, 1, 0)) Div G(h(1, 4, 1), L0[4,4],h(1, 4, 1)) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_66 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_17, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_67 = _t0_8;

  // 4-BLAC: 1x4 / 1x4
  _t0_68 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_66), _mm256_castpd256_pd128(_t0_67)));

  // AVX Storer:
  _t0_18 = _t0_68;

  // Generating : t0[4,1] = S(h(2, 4, 2), ( G(h(2, 4, 2), t0[4,1],h(1, 1, 0)) - ( G(h(2, 4, 2), L0[4,4],h(1, 4, 1)) Kro G(h(1, 4, 1), t0[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // 2x1 -> 4x1
  _t0_69 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_17, 6), _mm256_permute2f128_pd(_t0_17, _t0_17, 129), 5);

  // AVX Loader:

  // 2x1 -> 4x1
  _t0_70 = _mm256_blend_pd(_mm256_unpacklo_pd(_t0_9, _t0_13), _mm256_setzero_pd(), 12);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_71 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_18, _t0_18, 32), _mm256_permute2f128_pd(_t0_18, _t0_18, 32), 0);

  // 4-BLAC: 4x1 Kro 1x4
  _t0_72 = _mm256_mul_pd(_t0_70, _t0_71);

  // 4-BLAC: 4x1 - 4x1
  _t0_74 = _mm256_sub_pd(_t0_69, _t0_72);

  // AVX Storer:
  _t0_19 = _t0_74;

  // Generating : t0[4,1] = S(h(1, 4, 2), ( G(h(1, 4, 2), t0[4,1],h(1, 1, 0)) Div G(h(1, 4, 2), L0[4,4],h(1, 4, 2)) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_75 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_19, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_76 = _t0_10;

  // 4-BLAC: 1x4 / 1x4
  _t0_77 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_75), _mm256_castpd256_pd128(_t0_76)));

  // AVX Storer:
  _t0_20 = _t0_77;

  // Generating : t0[4,1] = S(h(1, 4, 3), ( G(h(1, 4, 3), t0[4,1],h(1, 1, 0)) - ( G(h(1, 4, 3), L0[4,4],h(1, 4, 2)) Kro G(h(1, 4, 2), t0[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_78 = _mm256_unpackhi_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_19, 2), _mm256_setzero_pd());

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_79 = _t0_14;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_80 = _t0_20;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_81 = _mm256_mul_pd(_t0_79, _t0_80);

  // 4-BLAC: 1x4 - 1x4
  _t0_82 = _mm256_sub_pd(_t0_78, _t0_81);

  // AVX Storer:
  _t0_21 = _t0_82;

  // Generating : t0[4,1] = S(h(1, 4, 3), ( G(h(1, 4, 3), t0[4,1],h(1, 1, 0)) Div G(h(1, 4, 3), L0[4,4],h(1, 4, 3)) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_83 = _t0_21;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_84 = _t0_15;

  // 4-BLAC: 1x4 / 1x4
  _t0_85 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_83), _mm256_castpd256_pd128(_t0_84)));

  // AVX Storer:
  _t0_21 = _t0_85;

  // Generating : a[4,1] = S(h(1, 4, 3), ( G(h(1, 4, 3), a[4,1],h(1, 1, 0)) Div G(h(1, 4, 3), L0[4,4],h(1, 4, 3)) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_87 = _t0_21;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_88 = _t0_15;

  // 4-BLAC: 1x4 / 1x4
  _t0_89 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_87), _mm256_castpd256_pd128(_t0_88)));

  // AVX Storer:
  _t0_21 = _t0_89;

  // Generating : a[4,1] = S(h(3, 4, 0), ( G(h(3, 4, 0), a[4,1],h(1, 1, 0)) - ( T( G(h(1, 4, 3), L0[4,4],h(3, 4, 0)) ) Kro G(h(1, 4, 3), a[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // 3x1 -> 4x1
  _t0_90 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_16, _t0_18), _mm256_unpacklo_pd(_t0_20, _mm256_setzero_pd()), 32);

  // AVX Loader:

  // 1x3 -> 1x4
  _t0_91 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_11, _t0_13), _mm256_unpacklo_pd(_t0_14, _mm256_setzero_pd()), 32);

  // 4-BLAC: (1x4)^T
  _t0_93 = _t0_91;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_94 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_21, _t0_21, 32), _mm256_permute2f128_pd(_t0_21, _t0_21, 32), 0);

  // 4-BLAC: 4x1 Kro 1x4
  _t0_95 = _mm256_mul_pd(_t0_93, _t0_94);

  // 4-BLAC: 4x1 - 4x1
  _t0_96 = _mm256_sub_pd(_t0_90, _t0_95);

  // AVX Storer:
  _t0_22 = _t0_96;

  // Generating : a[4,1] = S(h(1, 4, 2), ( G(h(1, 4, 2), a[4,1],h(1, 1, 0)) Div G(h(1, 4, 2), L0[4,4],h(1, 4, 2)) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_97 = _mm256_permute2f128_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_22, 4), _mm256_blend_pd(_mm256_setzero_pd(), _t0_22, 4), 129);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_98 = _t0_10;

  // 4-BLAC: 1x4 / 1x4
  _t0_99 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_97), _mm256_castpd256_pd128(_t0_98)));

  // AVX Storer:
  _t0_20 = _t0_99;

  // Generating : a[4,1] = S(h(2, 4, 0), ( G(h(2, 4, 0), a[4,1],h(1, 1, 0)) - ( T( G(h(1, 4, 2), L0[4,4],h(2, 4, 0)) ) Kro G(h(1, 4, 2), a[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // 2x1 -> 4x1
  _t0_100 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_22, 3);

  // AVX Loader:

  // 1x2 -> 1x4
  _t0_101 = _mm256_shuffle_pd(_mm256_blend_pd(_t0_7, _mm256_setzero_pd(), 12), _mm256_blend_pd(_t0_9, _mm256_setzero_pd(), 12), 1);

  // 4-BLAC: (1x4)^T
  _t0_102 = _t0_101;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_103 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_20, _t0_20, 32), _mm256_permute2f128_pd(_t0_20, _t0_20, 32), 0);

  // 4-BLAC: 4x1 Kro 1x4
  _t0_104 = _mm256_mul_pd(_t0_102, _t0_103);

  // 4-BLAC: 4x1 - 4x1
  _t0_105 = _mm256_sub_pd(_t0_100, _t0_104);

  // AVX Storer:
  _t0_23 = _t0_105;

  // Generating : a[4,1] = S(h(1, 4, 1), ( G(h(1, 4, 1), a[4,1],h(1, 1, 0)) Div G(h(1, 4, 1), L0[4,4],h(1, 4, 1)) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_107 = _mm256_unpackhi_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_23, 2), _mm256_setzero_pd());

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_108 = _t0_8;

  // 4-BLAC: 1x4 / 1x4
  _t0_109 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_107), _mm256_castpd256_pd128(_t0_108)));

  // AVX Storer:
  _t0_18 = _t0_109;

  // Generating : a[4,1] = S(h(1, 4, 0), ( G(h(1, 4, 0), a[4,1],h(1, 1, 0)) - ( T( G(h(1, 4, 1), L0[4,4],h(1, 4, 0)) ) Kro G(h(1, 4, 1), a[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_110 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_23, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_111 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_7, 1);

  // 4-BLAC: (4x1)^T
  _t0_112 = _t0_111;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_113 = _t0_18;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_114 = _mm256_mul_pd(_t0_112, _t0_113);

  // 4-BLAC: 1x4 - 1x4
  _t0_115 = _mm256_sub_pd(_t0_110, _t0_114);

  // AVX Storer:
  _t0_16 = _t0_115;

  // Generating : a[4,1] = S(h(1, 4, 0), ( G(h(1, 4, 0), a[4,1],h(1, 1, 0)) Div G(h(1, 4, 0), L0[4,4],h(1, 4, 0)) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_116 = _t0_16;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_117 = _t0_5;

  // 4-BLAC: 1x4 / 1x4
  _t0_118 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_116), _mm256_castpd256_pd128(_t0_117)));

  // AVX Storer:
  _t0_16 = _t0_118;

  // Generating : kx[4,1] = S(h(4, 4, 0), ( G(h(4, 4, 0), X[4,4],h(4, 4, 0)) * G(h(4, 4, 0), x[4,1],h(1, 1, 0)) ),h(1, 1, 0))

  // AVX Loader:

  // AVX Loader:

  // 4-BLAC: 4x4 * 4x1
  _t0_33 = _mm256_add_pd(_mm256_permute2f128_pd(_mm256_hadd_pd(_mm256_mul_pd(_t0_4, _t0_0), _mm256_mul_pd(_t0_3, _t0_0)), _mm256_hadd_pd(_mm256_mul_pd(_t0_2, _t0_0), _mm256_mul_pd(_t0_1, _t0_0)), 33), _mm256_blend_pd(_mm256_hadd_pd(_mm256_mul_pd(_t0_4, _t0_0), _mm256_mul_pd(_t0_3, _t0_0)), _mm256_hadd_pd(_mm256_mul_pd(_t0_2, _t0_0), _mm256_mul_pd(_t0_1, _t0_0)), 12));

  // AVX Storer:

  // Generating : f[1,1] = S(h(1, 1, 0), ( T( G(h(4, 4, 0), kx[4,1],h(1, 1, 0)) ) * G(h(4, 4, 0), y[4,1],h(1, 1, 0)) ),h(1, 1, 0))

  // AVX Loader:

  // 4-BLAC: (4x1)^T
  _t0_185 = _t0_33;

  // AVX Loader:

  // 4-BLAC: 1x4 * 4x1
  _t0_119 = _mm256_add_pd(_mm256_blend_pd(_mm256_add_pd(_mm256_mul_pd(_t0_185, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_16, _t0_18), _mm256_unpacklo_pd(_t0_20, _t0_21), 32)), _mm256_permute2f128_pd(_mm256_mul_pd(_t0_185, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_16, _t0_18), _mm256_unpacklo_pd(_t0_20, _t0_21), 32)), _mm256_mul_pd(_t0_185, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_16, _t0_18), _mm256_unpacklo_pd(_t0_20, _t0_21), 32)), 129)), _mm256_setzero_pd(), 14), _mm256_shuffle_pd(_mm256_add_pd(_mm256_mul_pd(_t0_185, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_16, _t0_18), _mm256_unpacklo_pd(_t0_20, _t0_21), 32)), _mm256_permute2f128_pd(_mm256_mul_pd(_t0_185, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_16, _t0_18), _mm256_unpacklo_pd(_t0_20, _t0_21), 32)), _mm256_mul_pd(_t0_185, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_16, _t0_18), _mm256_unpacklo_pd(_t0_20, _t0_21), 32)), 129)), _mm256_add_pd(_mm256_mul_pd(_t0_185, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_16, _t0_18), _mm256_unpacklo_pd(_t0_20, _t0_21), 32)), _mm256_permute2f128_pd(_mm256_mul_pd(_t0_185, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_16, _t0_18), _mm256_unpacklo_pd(_t0_20, _t0_21), 32)), _mm256_mul_pd(_t0_185, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_16, _t0_18), _mm256_unpacklo_pd(_t0_20, _t0_21), 32)), 129)), 1));

  // AVX Storer:
  _t0_24 = _t0_119;

  // Generating : v[4,1] = S(h(1, 4, 0), ( G(h(1, 4, 0), v[4,1],h(1, 1, 0)) Div G(h(1, 4, 0), L0[4,4],h(1, 4, 0)) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_121 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_33, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_122 = _t0_5;

  // 4-BLAC: 1x4 / 1x4
  _t0_123 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_121), _mm256_castpd256_pd128(_t0_122)));

  // AVX Storer:
  _t0_25 = _t0_123;

  // Generating : v[4,1] = S(h(3, 4, 1), ( G(h(3, 4, 1), v[4,1],h(1, 1, 0)) - ( G(h(3, 4, 1), L0[4,4],h(1, 4, 0)) Kro G(h(1, 4, 0), v[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // 3x1 -> 4x1
  _t0_124 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_33, 14), _mm256_permute2f128_pd(_t0_33, _t0_33, 129), 5);

  // AVX Loader:

  // 3x1 -> 4x1
  _t0_125 = _mm256_blend_pd(_mm256_permute2f128_pd(_mm256_blend_pd(_t0_7, _t0_7, 2), _t0_11, 32), _mm256_setzero_pd(), 8);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_126 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_25, _t0_25, 32), _mm256_permute2f128_pd(_t0_25, _t0_25, 32), 0);

  // 4-BLAC: 4x1 Kro 1x4
  _t0_128 = _mm256_mul_pd(_t0_125, _t0_126);

  // 4-BLAC: 4x1 - 4x1
  _t0_129 = _mm256_sub_pd(_t0_124, _t0_128);

  // AVX Storer:
  _t0_26 = _t0_129;

  // Generating : v[4,1] = S(h(1, 4, 1), ( G(h(1, 4, 1), v[4,1],h(1, 1, 0)) Div G(h(1, 4, 1), L0[4,4],h(1, 4, 1)) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_130 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_26, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_131 = _t0_8;

  // 4-BLAC: 1x4 / 1x4
  _t0_133 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_130), _mm256_castpd256_pd128(_t0_131)));

  // AVX Storer:
  _t0_27 = _t0_133;

  // Generating : v[4,1] = S(h(2, 4, 2), ( G(h(2, 4, 2), v[4,1],h(1, 1, 0)) - ( G(h(2, 4, 2), L0[4,4],h(1, 4, 1)) Kro G(h(1, 4, 1), v[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // 2x1 -> 4x1
  _t0_134 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_26, 6), _mm256_permute2f128_pd(_t0_26, _t0_26, 129), 5);

  // AVX Loader:

  // 2x1 -> 4x1
  _t0_135 = _mm256_blend_pd(_mm256_unpacklo_pd(_t0_9, _t0_13), _mm256_setzero_pd(), 12);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_136 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_27, _t0_27, 32), _mm256_permute2f128_pd(_t0_27, _t0_27, 32), 0);

  // 4-BLAC: 4x1 Kro 1x4
  _t0_137 = _mm256_mul_pd(_t0_135, _t0_136);

  // 4-BLAC: 4x1 - 4x1
  _t0_138 = _mm256_sub_pd(_t0_134, _t0_137);

  // AVX Storer:
  _t0_28 = _t0_138;

  // Generating : v[4,1] = S(h(1, 4, 2), ( G(h(1, 4, 2), v[4,1],h(1, 1, 0)) Div G(h(1, 4, 2), L0[4,4],h(1, 4, 2)) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_139 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_28, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_140 = _t0_10;

  // 4-BLAC: 1x4 / 1x4
  _t0_142 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_139), _mm256_castpd256_pd128(_t0_140)));

  // AVX Storer:
  _t0_29 = _t0_142;

  // Generating : v[4,1] = S(h(1, 4, 3), ( G(h(1, 4, 3), v[4,1],h(1, 1, 0)) - ( G(h(1, 4, 3), L0[4,4],h(1, 4, 2)) Kro G(h(1, 4, 2), v[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_143 = _mm256_unpackhi_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_28, 2), _mm256_setzero_pd());

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_144 = _t0_14;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_145 = _t0_29;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_146 = _mm256_mul_pd(_t0_144, _t0_145);

  // 4-BLAC: 1x4 - 1x4
  _t0_147 = _mm256_sub_pd(_t0_143, _t0_146);

  // AVX Storer:
  _t0_30 = _t0_147;

  // Generating : v[4,1] = S(h(1, 4, 3), ( G(h(1, 4, 3), v[4,1],h(1, 1, 0)) Div G(h(1, 4, 3), L0[4,4],h(1, 4, 3)) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_148 = _t0_30;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_149 = _t0_15;

  // 4-BLAC: 1x4 / 1x4
  _t0_150 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_148), _mm256_castpd256_pd128(_t0_149)));

  // AVX Storer:
  _t0_30 = _t0_150;

  // Generating : var[1,1] = S(h(1, 1, 0), ( ( T( G(h(4, 4, 0), x[4,1],h(1, 1, 0)) ) * G(h(4, 4, 0), x[4,1],h(1, 1, 0)) ) - ( T( G(h(4, 4, 0), kx[4,1],h(1, 1, 0)) ) * G(h(4, 4, 0), kx[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // 4-BLAC: (4x1)^T
  _t0_186 = _t0_0;

  // AVX Loader:

  // 4-BLAC: 1x4 * 4x1
  _t0_151 = _mm256_add_pd(_mm256_blend_pd(_mm256_add_pd(_mm256_mul_pd(_t0_186, _t0_0), _mm256_permute2f128_pd(_mm256_mul_pd(_t0_186, _t0_0), _mm256_mul_pd(_t0_186, _t0_0), 129)), _mm256_setzero_pd(), 14), _mm256_shuffle_pd(_mm256_add_pd(_mm256_mul_pd(_t0_186, _t0_0), _mm256_permute2f128_pd(_mm256_mul_pd(_t0_186, _t0_0), _mm256_mul_pd(_t0_186, _t0_0), 129)), _mm256_add_pd(_mm256_mul_pd(_t0_186, _t0_0), _mm256_permute2f128_pd(_mm256_mul_pd(_t0_186, _t0_0), _mm256_mul_pd(_t0_186, _t0_0), 129)), 1));

  // AVX Loader:

  // 4-BLAC: (4x1)^T
  _t0_187 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_25, _t0_27), _mm256_unpacklo_pd(_t0_29, _t0_30), 32);

  // AVX Loader:

  // 4-BLAC: 1x4 * 4x1
  _t0_152 = _mm256_add_pd(_mm256_blend_pd(_mm256_add_pd(_mm256_mul_pd(_t0_187, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_25, _t0_27), _mm256_unpacklo_pd(_t0_29, _t0_30), 32)), _mm256_permute2f128_pd(_mm256_mul_pd(_t0_187, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_25, _t0_27), _mm256_unpacklo_pd(_t0_29, _t0_30), 32)), _mm256_mul_pd(_t0_187, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_25, _t0_27), _mm256_unpacklo_pd(_t0_29, _t0_30), 32)), 129)), _mm256_setzero_pd(), 14), _mm256_shuffle_pd(_mm256_add_pd(_mm256_mul_pd(_t0_187, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_25, _t0_27), _mm256_unpacklo_pd(_t0_29, _t0_30), 32)), _mm256_permute2f128_pd(_mm256_mul_pd(_t0_187, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_25, _t0_27), _mm256_unpacklo_pd(_t0_29, _t0_30), 32)), _mm256_mul_pd(_t0_187, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_25, _t0_27), _mm256_unpacklo_pd(_t0_29, _t0_30), 32)), 129)), _mm256_add_pd(_mm256_mul_pd(_t0_187, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_25, _t0_27), _mm256_unpacklo_pd(_t0_29, _t0_30), 32)), _mm256_permute2f128_pd(_mm256_mul_pd(_t0_187, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_25, _t0_27), _mm256_unpacklo_pd(_t0_29, _t0_30), 32)), _mm256_mul_pd(_t0_187, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_25, _t0_27), _mm256_unpacklo_pd(_t0_29, _t0_30), 32)), 129)), 1));

  // 4-BLAC: 1x4 - 1x4
  _t0_153 = _mm256_sub_pd(_t0_151, _t0_152);

  // AVX Storer:
  _t0_31 = _t0_153;

  // Generating : lp[1,1] = S(h(1, 1, 0), ( T( G(h(4, 4, 0), y[4,1],h(1, 1, 0)) ) * G(h(4, 4, 0), y[4,1],h(1, 1, 0)) ),h(1, 1, 0))

  // AVX Loader:

  // 4-BLAC: (4x1)^T
  _t0_188 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_16, _t0_18), _mm256_unpacklo_pd(_t0_20, _t0_21), 32);

  // AVX Loader:

  // 4-BLAC: 1x4 * 4x1
  _t0_154 = _mm256_add_pd(_mm256_blend_pd(_mm256_add_pd(_mm256_mul_pd(_t0_188, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_16, _t0_18), _mm256_unpacklo_pd(_t0_20, _t0_21), 32)), _mm256_permute2f128_pd(_mm256_mul_pd(_t0_188, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_16, _t0_18), _mm256_unpacklo_pd(_t0_20, _t0_21), 32)), _mm256_mul_pd(_t0_188, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_16, _t0_18), _mm256_unpacklo_pd(_t0_20, _t0_21), 32)), 129)), _mm256_setzero_pd(), 14), _mm256_shuffle_pd(_mm256_add_pd(_mm256_mul_pd(_t0_188, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_16, _t0_18), _mm256_unpacklo_pd(_t0_20, _t0_21), 32)), _mm256_permute2f128_pd(_mm256_mul_pd(_t0_188, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_16, _t0_18), _mm256_unpacklo_pd(_t0_20, _t0_21), 32)), _mm256_mul_pd(_t0_188, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_16, _t0_18), _mm256_unpacklo_pd(_t0_20, _t0_21), 32)), 129)), _mm256_add_pd(_mm256_mul_pd(_t0_188, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_16, _t0_18), _mm256_unpacklo_pd(_t0_20, _t0_21), 32)), _mm256_permute2f128_pd(_mm256_mul_pd(_t0_188, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_16, _t0_18), _mm256_unpacklo_pd(_t0_20, _t0_21), 32)), _mm256_mul_pd(_t0_188, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_16, _t0_18), _mm256_unpacklo_pd(_t0_20, _t0_21), 32)), 129)), 1));

  // AVX Storer:
  _t0_32 = _t0_154;

  _mm_store_sd(&(K[0]), _mm256_castpd256_pd128(_t0_5));
  _mm256_maskstore_pd(K + 4, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t0_7);
  _mm256_maskstore_pd(K + 8, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _mm256_shuffle_pd(_t0_7, _t0_7, 1));
  _mm_store_sd(&(K[5]), _mm256_castpd256_pd128(_t0_8));
  _mm_store_sd(&(K[9]), _mm256_castpd256_pd128(_t0_9));
  _mm_store_sd(&(K[10]), _mm256_castpd256_pd128(_t0_10));
  _mm_store_sd(&(K[12]), _mm256_castpd256_pd128(_t0_11));
  _mm_store_sd(&(K[13]), _mm256_castpd256_pd128(_t0_13));
  _mm_store_sd(&(K[14]), _mm256_castpd256_pd128(_t0_14));
  _mm_store_sd(&(K[15]), _mm256_castpd256_pd128(_t0_15));
  _mm_store_sd(&(y[3]), _mm256_castpd256_pd128(_t0_21));
  _mm_store_sd(&(y[2]), _mm256_castpd256_pd128(_t0_20));
  _mm_store_sd(&(y[1]), _mm256_castpd256_pd128(_t0_18));
  _mm_store_sd(&(y[0]), _mm256_castpd256_pd128(_t0_16));
  _mm_store_sd(&(f[0]), _mm256_castpd256_pd128(_t0_24));
  _mm_store_sd(&(kx[0]), _mm256_castpd256_pd128(_t0_25));
  _mm_store_sd(&(kx[1]), _mm256_castpd256_pd128(_t0_27));
  _mm_store_sd(&(kx[2]), _mm256_castpd256_pd128(_t0_29));
  _mm_store_sd(&(kx[3]), _mm256_castpd256_pd128(_t0_30));
  _mm_store_sd(&(var[0]), _mm256_castpd256_pd128(_t0_31));
  _mm_store_sd(&(lp[0]), _mm256_castpd256_pd128(_t0_32));

}
