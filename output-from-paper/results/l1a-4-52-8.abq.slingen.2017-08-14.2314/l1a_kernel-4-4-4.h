/*
 * l1a_kernel.h
 *
Decl { {u'A': SquaredMatrix[A, (4, 4), GenMatAccess], u'a': Scalar[a, (1, 1), GenMatAccess], u'b': Scalar[b, (1, 1), GenMatAccess], u'y1': Matrix[y1, (4, 1), GenMatAccess], u'y2': Matrix[y2, (4, 1), GenMatAccess], u'v1': Matrix[v1, (4, 1), GenMatAccess], u'v2': Matrix[v2, (4, 1), GenMatAccess], u't': Scalar[t, (1, 1), GenMatAccess], u'W': SquaredMatrix[W, (4, 4), GenMatAccess], u'y': Matrix[y, (4, 1), GenMatAccess], u'x': Matrix[x, (4, 1), GenMatAccess], u'x0': Matrix[x0, (4, 1), GenMatAccess], u'x1': Matrix[x1, (4, 1), GenMatAccess], u'z1': Matrix[z1, (4, 1), GenMatAccess], u'z2': Matrix[z2, (4, 1), GenMatAccess]} }
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ann: {}

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Entry 0:
Entry 0:
Eq: Tile( (1, 1), Tile( (4, 4), y1[4,1] ) ) = ( ( Tile( (1, 1), Tile( (4, 4), a[1,1] ) ) Kro Tile( (1, 1), Tile( (4, 4), v1[4,1] ) ) ) + ( Tile( (1, 1), Tile( (4, 4), t[1,1] ) ) Kro Tile( (1, 1), Tile( (4, 4), z1[4,1] ) ) ) )
Eq.ann: {}
Entry 1:
Eq: Tile( (1, 1), Tile( (4, 4), y2[4,1] ) ) = ( ( Tile( (1, 1), Tile( (4, 4), a[1,1] ) ) Kro Tile( (1, 1), Tile( (4, 4), v2[4,1] ) ) ) + ( Tile( (1, 1), Tile( (4, 4), t[1,1] ) ) Kro Tile( (1, 1), Tile( (4, 4), z2[4,1] ) ) ) )
Eq.ann: {}
Entry 2:
Eq: Tile( (1, 1), Tile( (4, 4), x1[4,1] ) ) = ( ( T( Tile( (1, 1), Tile( (4, 4), W[4,4] ) ) ) * Tile( (1, 1), Tile( (4, 4), y1[4,1] ) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), A[4,4] ) ) ) * Tile( (1, 1), Tile( (4, 4), y2[4,1] ) ) ) )
Eq.ann: {}
Entry 3:
Eq: Tile( (1, 1), Tile( (4, 4), x[4,1] ) ) = ( Tile( (1, 1), Tile( (4, 4), x0[4,1] ) ) + ( Tile( (1, 1), Tile( (4, 4), b[1,1] ) ) Kro Tile( (1, 1), Tile( (4, 4), x1[4,1] ) ) ) )
Eq.ann: {}
Entry 4:
Eq: Tile( (1, 1), Tile( (4, 4), z1[4,1] ) ) = ( Tile( (1, 1), Tile( (4, 4), y1[4,1] ) ) - ( Tile( (1, 1), Tile( (4, 4), W[4,4] ) ) * Tile( (1, 1), Tile( (4, 4), x[4,1] ) ) ) )
Eq.ann: {}
Entry 5:
Eq: Tile( (1, 1), Tile( (4, 4), z2[4,1] ) ) = ( Tile( (1, 1), Tile( (4, 4), y2[4,1] ) ) - ( Tile( (1, 1), Tile( (4, 4), y[4,1] ) ) - ( Tile( (1, 1), Tile( (4, 4), A[4,4] ) ) * Tile( (1, 1), Tile( (4, 4), x[4,1] ) ) ) ) )
Eq.ann: {}
Entry 6:
Eq: Tile( (1, 1), Tile( (4, 4), v1[4,1] ) ) = ( ( Tile( (1, 1), Tile( (4, 4), a[1,1] ) ) Kro Tile( (1, 1), Tile( (4, 4), v1[4,1] ) ) ) + ( Tile( (1, 1), Tile( (4, 4), t[1,1] ) ) Kro Tile( (1, 1), Tile( (4, 4), z1[4,1] ) ) ) )
Eq.ann: {}
Entry 7:
Eq: Tile( (1, 1), Tile( (4, 4), v2[4,1] ) ) = ( ( Tile( (1, 1), Tile( (4, 4), a[1,1] ) ) Kro Tile( (1, 1), Tile( (4, 4), v2[4,1] ) ) ) + ( Tile( (1, 1), Tile( (4, 4), t[1,1] ) ) Kro Tile( (1, 1), Tile( (4, 4), z2[4,1] ) ) ) )
Eq.ann: {}
 *
 * Created on: 2017-08-14
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

#define ERRTHRESH 1e-5

#define SOFTERRTHRESH 1e-7

#define NUMREP 30

#define floord(n,d) (((n)<0) ? -((-(n)+(d)-1)/(d)) : (n)/(d))
#define ceild(n,d)  (((n)<0) ? -((-(n))/(d)) : ((n)+(d)-1)/(d))
#define max(x,y)    ((x) > (y) ? (x) : (y))
#define min(x,y)    ((x) < (y) ? (x) : (y))
#define Max(x,y)    ((x) > (y) ? (x) : (y))
#define Min(x,y)    ((x) < (y) ? (x) : (y))


static __attribute__((noinline)) void kernel(double a, double t, double const * W, double const * A, double const * x0, double b, double const * y, double * y1, double * v1, double * z1, double * y2, double * v2, double * z2, double * x1, double * x)
{
  __m256d _t0_0, _t0_1, _t0_2, _t0_3, _t0_4, _t0_5, _t0_6, _t0_7,
	_t0_8, _t0_9, _t0_10, _t0_11, _t0_12, _t0_13, _t0_14, _t0_15,
	_t0_16, _t0_17, _t0_18, _t0_19, _t0_20, _t0_21, _t0_22, _t0_23,
	_t0_24, _t0_25, _t0_26, _t0_27, _t0_28, _t0_29, _t0_30, _t0_31,
	_t0_32, _t0_33, _t0_34, _t0_35, _t0_36, _t0_37, _t0_38, _t0_39,
	_t0_40, _t0_41, _t0_42, _t0_43, _t0_44, _t0_45, _t0_46, _t0_47,
	_t0_48;

  _t0_10 = _asm256_loadu_pd(v1);
  _t0_31 = _asm256_loadu_pd(z1);
  _t0_11 = _asm256_loadu_pd(v2);
  _t0_29 = _asm256_loadu_pd(z2);
  _t0_9 = _asm256_loadu_pd(W);
  _t0_8 = _asm256_loadu_pd(W + 4);
  _t0_7 = _asm256_loadu_pd(W + 8);
  _t0_6 = _asm256_loadu_pd(W + 12);
  _t0_5 = _asm256_loadu_pd(A);
  _t0_4 = _asm256_loadu_pd(A + 4);
  _t0_3 = _asm256_loadu_pd(A + 8);
  _t0_2 = _asm256_loadu_pd(A + 12);
  _t0_1 = _asm256_loadu_pd(x0);
  _t0_0 = _asm256_loadu_pd(y);

  // Generating : y1[4,1] = S(h(4, 4, 0), ( ( G(h(1, 1, 0), a[1,1],h(1, 1, 0)) Kro G(h(4, 4, 0), v1[4,1],h(1, 1, 0)) ) + ( G(h(1, 1, 0), t[1,1],h(1, 1, 0)) Kro G(h(4, 4, 0), z1[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_38 = _mm256_broadcast_sd(&(a));

  // AVX Loader:

  // 4-BLAC: 1x4 Kro 4x1
  _t0_19 = _mm256_mul_pd(_t0_38, _t0_10);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_39 = _mm256_broadcast_sd(&(t));

  // AVX Loader:

  // 4-BLAC: 1x4 Kro 4x1
  _t0_20 = _mm256_mul_pd(_t0_39, _t0_31);

  // 4-BLAC: 4x1 + 4x1
  _t0_12 = _mm256_add_pd(_t0_19, _t0_20);

  // AVX Storer:

  // Generating : y2[4,1] = S(h(4, 4, 0), ( ( G(h(1, 1, 0), a[1,1],h(1, 1, 0)) Kro G(h(4, 4, 0), v2[4,1],h(1, 1, 0)) ) + ( G(h(1, 1, 0), t[1,1],h(1, 1, 0)) Kro G(h(4, 4, 0), z2[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_40 = _mm256_broadcast_sd(&(a));

  // AVX Loader:

  // 4-BLAC: 1x4 Kro 4x1
  _t0_21 = _mm256_mul_pd(_t0_40, _t0_11);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_32 = _mm256_broadcast_sd(&(t));

  // AVX Loader:

  // 4-BLAC: 1x4 Kro 4x1
  _t0_22 = _mm256_mul_pd(_t0_32, _t0_29);

  // 4-BLAC: 4x1 + 4x1
  _t0_13 = _mm256_add_pd(_t0_21, _t0_22);

  // AVX Storer:

  // Generating : x1[4,1] = S(h(4, 4, 0), ( ( T( G(h(4, 4, 0), W[4,4],h(4, 4, 0)) ) * G(h(4, 4, 0), y1[4,1],h(1, 1, 0)) ) - ( T( G(h(4, 4, 0), A[4,4],h(4, 4, 0)) ) * G(h(4, 4, 0), y2[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // 4-BLAC: (4x4)^T
  _t0_41 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_9, _t0_8), _mm256_unpacklo_pd(_t0_7, _t0_6), 32);
  _t0_42 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t0_9, _t0_8), _mm256_unpackhi_pd(_t0_7, _t0_6), 32);
  _t0_43 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_9, _t0_8), _mm256_unpacklo_pd(_t0_7, _t0_6), 49);
  _t0_44 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t0_9, _t0_8), _mm256_unpackhi_pd(_t0_7, _t0_6), 49);

  // AVX Loader:

  // 4-BLAC: 4x4 * 4x1
  _t0_25 = _mm256_add_pd(_mm256_permute2f128_pd(_mm256_hadd_pd(_mm256_mul_pd(_t0_41, _t0_12), _mm256_mul_pd(_t0_42, _t0_12)), _mm256_hadd_pd(_mm256_mul_pd(_t0_43, _t0_12), _mm256_mul_pd(_t0_44, _t0_12)), 33), _mm256_blend_pd(_mm256_hadd_pd(_mm256_mul_pd(_t0_41, _t0_12), _mm256_mul_pd(_t0_42, _t0_12)), _mm256_hadd_pd(_mm256_mul_pd(_t0_43, _t0_12), _mm256_mul_pd(_t0_44, _t0_12)), 12));

  // AVX Loader:

  // 4-BLAC: (4x4)^T
  _t0_45 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_5, _t0_4), _mm256_unpacklo_pd(_t0_3, _t0_2), 32);
  _t0_46 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t0_5, _t0_4), _mm256_unpackhi_pd(_t0_3, _t0_2), 32);
  _t0_47 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_5, _t0_4), _mm256_unpacklo_pd(_t0_3, _t0_2), 49);
  _t0_48 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t0_5, _t0_4), _mm256_unpackhi_pd(_t0_3, _t0_2), 49);

  // AVX Loader:

  // 4-BLAC: 4x4 * 4x1
  _t0_26 = _mm256_add_pd(_mm256_permute2f128_pd(_mm256_hadd_pd(_mm256_mul_pd(_t0_45, _t0_13), _mm256_mul_pd(_t0_46, _t0_13)), _mm256_hadd_pd(_mm256_mul_pd(_t0_47, _t0_13), _mm256_mul_pd(_t0_48, _t0_13)), 33), _mm256_blend_pd(_mm256_hadd_pd(_mm256_mul_pd(_t0_45, _t0_13), _mm256_mul_pd(_t0_46, _t0_13)), _mm256_hadd_pd(_mm256_mul_pd(_t0_47, _t0_13), _mm256_mul_pd(_t0_48, _t0_13)), 12));

  // 4-BLAC: 4x1 - 4x1
  _t0_30 = _mm256_sub_pd(_t0_25, _t0_26);

  // AVX Storer:

  // Generating : x[4,1] = S(h(4, 4, 0), ( G(h(4, 4, 0), x0[4,1],h(1, 1, 0)) + ( G(h(1, 1, 0), b[1,1],h(1, 1, 0)) Kro G(h(4, 4, 0), x1[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_33 = _mm256_broadcast_sd(&(b));

  // AVX Loader:

  // 4-BLAC: 1x4 Kro 4x1
  _t0_23 = _mm256_mul_pd(_t0_33, _t0_30);

  // 4-BLAC: 4x1 + 4x1
  _t0_14 = _mm256_add_pd(_t0_1, _t0_23);

  // AVX Storer:

  // Generating : z1[4,1] = S(h(4, 4, 0), ( G(h(4, 4, 0), y1[4,1],h(1, 1, 0)) - ( G(h(4, 4, 0), W[4,4],h(4, 4, 0)) * G(h(4, 4, 0), x[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // AVX Loader:

  // AVX Loader:

  // 4-BLAC: 4x4 * 4x1
  _t0_27 = _mm256_add_pd(_mm256_permute2f128_pd(_mm256_hadd_pd(_mm256_mul_pd(_t0_9, _t0_14), _mm256_mul_pd(_t0_8, _t0_14)), _mm256_hadd_pd(_mm256_mul_pd(_t0_7, _t0_14), _mm256_mul_pd(_t0_6, _t0_14)), 33), _mm256_blend_pd(_mm256_hadd_pd(_mm256_mul_pd(_t0_9, _t0_14), _mm256_mul_pd(_t0_8, _t0_14)), _mm256_hadd_pd(_mm256_mul_pd(_t0_7, _t0_14), _mm256_mul_pd(_t0_6, _t0_14)), 12));

  // 4-BLAC: 4x1 - 4x1
  _t0_31 = _mm256_sub_pd(_t0_12, _t0_27);

  // AVX Storer:

  // Generating : z2[4,1] = S(h(4, 4, 0), ( G(h(4, 4, 0), y2[4,1],h(1, 1, 0)) - ( G(h(4, 4, 0), y[4,1],h(1, 1, 0)) - ( G(h(4, 4, 0), A[4,4],h(4, 4, 0)) * G(h(4, 4, 0), x[4,1],h(1, 1, 0)) ) ) ),h(1, 1, 0))

  // AVX Loader:

  // AVX Loader:

  // AVX Loader:

  // AVX Loader:

  // 4-BLAC: 4x4 * 4x1
  _t0_24 = _mm256_add_pd(_mm256_permute2f128_pd(_mm256_hadd_pd(_mm256_mul_pd(_t0_5, _t0_14), _mm256_mul_pd(_t0_4, _t0_14)), _mm256_hadd_pd(_mm256_mul_pd(_t0_3, _t0_14), _mm256_mul_pd(_t0_2, _t0_14)), 33), _mm256_blend_pd(_mm256_hadd_pd(_mm256_mul_pd(_t0_5, _t0_14), _mm256_mul_pd(_t0_4, _t0_14)), _mm256_hadd_pd(_mm256_mul_pd(_t0_3, _t0_14), _mm256_mul_pd(_t0_2, _t0_14)), 12));

  // 4-BLAC: 4x1 - 4x1
  _t0_28 = _mm256_sub_pd(_t0_0, _t0_24);

  // 4-BLAC: 4x1 - 4x1
  _t0_29 = _mm256_sub_pd(_t0_13, _t0_28);

  // AVX Storer:

  // Generating : v1[4,1] = S(h(4, 4, 0), ( ( G(h(1, 1, 0), a[1,1],h(1, 1, 0)) Kro G(h(4, 4, 0), v1[4,1],h(1, 1, 0)) ) + ( G(h(1, 1, 0), t[1,1],h(1, 1, 0)) Kro G(h(4, 4, 0), z1[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_34 = _mm256_broadcast_sd(&(a));

  // AVX Loader:

  // 4-BLAC: 1x4 Kro 4x1
  _t0_15 = _mm256_mul_pd(_t0_34, _t0_10);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_35 = _mm256_broadcast_sd(&(t));

  // AVX Loader:

  // 4-BLAC: 1x4 Kro 4x1
  _t0_16 = _mm256_mul_pd(_t0_35, _t0_31);

  // 4-BLAC: 4x1 + 4x1
  _t0_10 = _mm256_add_pd(_t0_15, _t0_16);

  // AVX Storer:

  // Generating : v2[4,1] = S(h(4, 4, 0), ( ( G(h(1, 1, 0), a[1,1],h(1, 1, 0)) Kro G(h(4, 4, 0), v2[4,1],h(1, 1, 0)) ) + ( G(h(1, 1, 0), t[1,1],h(1, 1, 0)) Kro G(h(4, 4, 0), z2[4,1],h(1, 1, 0)) ) ),h(1, 1, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_36 = _mm256_broadcast_sd(&(a));

  // AVX Loader:

  // 4-BLAC: 1x4 Kro 4x1
  _t0_17 = _mm256_mul_pd(_t0_36, _t0_11);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_37 = _mm256_broadcast_sd(&(t));

  // AVX Loader:

  // 4-BLAC: 1x4 Kro 4x1
  _t0_18 = _mm256_mul_pd(_t0_37, _t0_29);

  // 4-BLAC: 4x1 + 4x1
  _t0_11 = _mm256_add_pd(_t0_17, _t0_18);

  // AVX Storer:

  _asm256_storeu_pd(y1, _t0_12);
  _asm256_storeu_pd(y2, _t0_13);
  _asm256_storeu_pd(x1, _t0_30);
  _asm256_storeu_pd(x, _t0_14);
  _asm256_storeu_pd(z1, _t0_31);
  _asm256_storeu_pd(z2, _t0_29);
  _asm256_storeu_pd(v1, _t0_10);
  _asm256_storeu_pd(v2, _t0_11);

}
