/*
 * l1a_kernel.h
 *
Decl { {u'A': SquaredMatrix[A, (12, 12), GenMatAccess], u'a': Scalar[a, (1, 1), GenMatAccess], u'b': Scalar[b, (1, 1), GenMatAccess], u'y1': Matrix[y1, (12, 1), GenMatAccess], u'y2': Matrix[y2, (12, 1), GenMatAccess], u'v1': Matrix[v1, (12, 1), GenMatAccess], u'v2': Matrix[v2, (12, 1), GenMatAccess], u't': Scalar[t, (1, 1), GenMatAccess], u'W': SquaredMatrix[W, (12, 12), GenMatAccess], u'y': Matrix[y, (12, 1), GenMatAccess], u'x': Matrix[x, (12, 1), GenMatAccess], u'x0': Matrix[x0, (12, 1), GenMatAccess], u'x1': Matrix[x1, (12, 1), GenMatAccess], u'z1': Matrix[z1, (12, 1), GenMatAccess], u'z2': Matrix[z2, (12, 1), GenMatAccess]} }
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ann: {}

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Entry 0:
Entry 0:
Eq: Tile( (1, 1), Tile( (4, 4), y1[12,1] ) ) = ( ( Tile( (1, 1), Tile( (4, 4), a[1,1] ) ) Kro Tile( (1, 1), Tile( (4, 4), v1[12,1] ) ) ) + ( Tile( (1, 1), Tile( (4, 4), t[1,1] ) ) Kro Tile( (1, 1), Tile( (4, 4), z1[12,1] ) ) ) )
Eq.ann: {}
Entry 1:
Eq: Tile( (1, 1), Tile( (4, 4), y2[12,1] ) ) = ( ( Tile( (1, 1), Tile( (4, 4), a[1,1] ) ) Kro Tile( (1, 1), Tile( (4, 4), v2[12,1] ) ) ) + ( Tile( (1, 1), Tile( (4, 4), t[1,1] ) ) Kro Tile( (1, 1), Tile( (4, 4), z2[12,1] ) ) ) )
Eq.ann: {}
Entry 2:
Eq: Tile( (1, 1), Tile( (4, 4), x1[12,1] ) ) = ( ( T( Tile( (1, 1), Tile( (4, 4), W[12,12] ) ) ) * Tile( (1, 1), Tile( (4, 4), y1[12,1] ) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), A[12,12] ) ) ) * Tile( (1, 1), Tile( (4, 4), y2[12,1] ) ) ) )
Eq.ann: {}
Entry 3:
Eq: Tile( (1, 1), Tile( (4, 4), x[12,1] ) ) = ( Tile( (1, 1), Tile( (4, 4), x0[12,1] ) ) + ( Tile( (1, 1), Tile( (4, 4), b[1,1] ) ) Kro Tile( (1, 1), Tile( (4, 4), x1[12,1] ) ) ) )
Eq.ann: {}
Entry 4:
Eq: Tile( (1, 1), Tile( (4, 4), z1[12,1] ) ) = ( Tile( (1, 1), Tile( (4, 4), y1[12,1] ) ) - ( Tile( (1, 1), Tile( (4, 4), W[12,12] ) ) * Tile( (1, 1), Tile( (4, 4), x[12,1] ) ) ) )
Eq.ann: {}
Entry 5:
Eq: Tile( (1, 1), Tile( (4, 4), z2[12,1] ) ) = ( Tile( (1, 1), Tile( (4, 4), y2[12,1] ) ) - ( Tile( (1, 1), Tile( (4, 4), y[12,1] ) ) - ( Tile( (1, 1), Tile( (4, 4), A[12,12] ) ) * Tile( (1, 1), Tile( (4, 4), x[12,1] ) ) ) ) )
Eq.ann: {}
Entry 6:
Eq: Tile( (1, 1), Tile( (4, 4), v1[12,1] ) ) = ( ( Tile( (1, 1), Tile( (4, 4), a[1,1] ) ) Kro Tile( (1, 1), Tile( (4, 4), v1[12,1] ) ) ) + ( Tile( (1, 1), Tile( (4, 4), t[1,1] ) ) Kro Tile( (1, 1), Tile( (4, 4), z1[12,1] ) ) ) )
Eq.ann: {}
Entry 7:
Eq: Tile( (1, 1), Tile( (4, 4), v2[12,1] ) ) = ( ( Tile( (1, 1), Tile( (4, 4), a[1,1] ) ) Kro Tile( (1, 1), Tile( (4, 4), v2[12,1] ) ) ) + ( Tile( (1, 1), Tile( (4, 4), t[1,1] ) ) Kro Tile( (1, 1), Tile( (4, 4), z2[12,1] ) ) ) )
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

#define PARAM0 12
#define PARAM1 12
#define PARAM2 12

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
  __m256d _t0_0, _t0_1;
  __m256d _t1_0, _t1_1, _t1_2, _t1_3, _t1_4;
  __m256d _t2_0, _t2_1;
  __m256d _t3_0, _t3_1, _t3_2, _t3_3, _t3_4;
  __m256d _t4_0, _t4_1, _t4_2, _t4_3, _t4_4, _t4_5, _t4_6, _t4_7,
	_t4_8, _t4_9, _t4_10, _t4_11, _t4_12, _t4_13, _t4_14, _t4_15,
	_t4_16, _t4_17, _t4_18, _t4_19, _t4_20;
  __m256d _t5_0, _t5_1, _t5_2, _t5_3, _t5_4, _t5_5, _t5_6, _t5_7,
	_t5_8, _t5_9, _t5_10;
  __m256d _t6_0, _t6_1, _t6_2, _t6_3, _t6_4, _t6_5, _t6_6, _t6_7,
	_t6_8, _t6_9, _t6_10;
  __m256d _t7_0;
  __m256d _t8_0, _t8_1, _t8_2, _t8_3;
  __m256d _t9_0, _t9_1, _t9_2, _t9_3, _t9_4, _t9_5, _t9_6, _t9_7;
  __m256d _t10_0, _t10_1, _t10_2, _t10_3, _t10_4, _t10_5, _t10_6;
  __m256d _t11_0, _t11_1, _t11_2, _t11_3, _t11_4, _t11_5, _t11_6, _t11_7,
	_t11_8, _t11_9;
  __m256d _t12_0, _t12_1, _t12_2, _t12_3, _t12_4, _t12_5, _t12_6;
  __m256d _t13_0, _t13_1;
  __m256d _t14_0, _t14_1, _t14_2, _t14_3;
  __m256d _t15_0, _t15_1;
  __m256d _t16_0, _t16_1, _t16_2, _t16_3;


  // Generating : y1[12,1] = Sum_{i0} ( S(h(4, 12, i0), ( ( G(h(1, 1, 0), a[1,1],h(1, 1, 0)) Kro G(h(4, 12, i0), v1[12,1],h(1, 1, 0)) ) + ( G(h(1, 1, 0), t[1,1],h(1, 1, 0)) Kro G(h(4, 12, i0), z1[12,1],h(1, 1, 0)) ) ),h(1, 1, 0)) )

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_0 = _mm256_broadcast_sd(&(a));
  _t0_0 = _mm256_blend_pd(_mm256_setzero_pd(), _mm256_blend_pd(_mm256_setzero_pd(), _t0_0, 15), 15);
  // AVX Loader:

  // 1x1 -> 1x4
  _t0_1 = _mm256_broadcast_sd(&(t));
  _t0_1 = _mm256_blend_pd(_mm256_setzero_pd(), _mm256_blend_pd(_mm256_setzero_pd(), _t0_1, 15), 15);

  for( int i0 = 0; i0 <= 11; i0+=4 ) {
    _t1_1 = _asm256_loadu_pd(v1 + i0);
    _t1_0 = _asm256_loadu_pd(z1 + i0);

    // AVX Loader:

    // 4-BLAC: 1x4 Kro 4x1
    _t1_3 = _mm256_mul_pd(_t0_0, _t1_1);

    // AVX Loader:

    // 4-BLAC: 1x4 Kro 4x1
    _t1_4 = _mm256_mul_pd(_t0_1, _t1_0);

    // 4-BLAC: 4x1 + 4x1
    _t1_2 = _mm256_add_pd(_t1_3, _t1_4);

    // AVX Storer:
    _asm256_storeu_pd(y1 + i0, _t1_2);
  }


  // Generating : y2[12,1] = Sum_{i0} ( S(h(4, 12, i0), ( ( G(h(1, 1, 0), a[1,1],h(1, 1, 0)) Kro G(h(4, 12, i0), v2[12,1],h(1, 1, 0)) ) + ( G(h(1, 1, 0), t[1,1],h(1, 1, 0)) Kro G(h(4, 12, i0), z2[12,1],h(1, 1, 0)) ) ),h(1, 1, 0)) )

  // AVX Loader:

  // 1x1 -> 1x4
  // _t2_0 = _mm256_broadcast_sd(&(a));

  // AVX Loader:

  // 1x1 -> 1x4
  // _t2_1 = _mm256_broadcast_sd(&(t));


  for( int i0 = 0; i0 <= 11; i0+=4 ) {
    _t3_1 = _asm256_loadu_pd(v2 + i0);
    _t3_0 = _asm256_loadu_pd(z2 + i0);

    // AVX Loader:

    // 4-BLAC: 1x4 Kro 4x1
    _t3_3 = _mm256_mul_pd(_t0_0, _t3_1);

    // AVX Loader:

    // 4-BLAC: 1x4 Kro 4x1
    _t3_4 = _mm256_mul_pd(_t0_1, _t3_0);

    // 4-BLAC: 4x1 + 4x1
    _t3_2 = _mm256_add_pd(_t3_3, _t3_4);

    // AVX Storer:
    _asm256_storeu_pd(y2 + i0, _t3_2);
  }


  // Generating : x1[12,1] = ( ( Sum_{k15} ( S(h(4, 12, k15), ( ( T( G(h(4, 12, 0), W[12,12],h(4, 12, k15)) ) * G(h(4, 12, 0), y1[12,1],h(1, 1, 0)) ) - ( T( G(h(4, 12, 0), A[12,12],h(4, 12, k15)) ) * G(h(4, 12, 0), y2[12,1],h(1, 1, 0)) ) ),h(1, 1, 0)) ) + Sum_{i6} ( Sum_{k15} ( $(h(4, 12, k15), ( T( G(h(4, 12, i6), W[12,12],h(4, 12, k15)) ) * G(h(4, 12, i6), y1[12,1],h(1, 1, 0)) ),h(1, 1, 0)) ) ) ) + Sum_{i0} ( Sum_{k15} ( -$(h(4, 12, k15), ( T( G(h(4, 12, i0), A[12,12],h(4, 12, k15)) ) * G(h(4, 12, i0), y2[12,1],h(1, 1, 0)) ),h(1, 1, 0)) ) ) )

  // AVX Loader:

  // AVX Loader:

    _t4_5 = _asm256_loadu_pd(y1);
    _t4_0 = _asm256_loadu_pd(y2);

  for( int k15 = 0; k15 <= 11; k15+=4 ) {
    _t4_9 = _asm256_loadu_pd(W + k15);
    _t4_8 = _asm256_loadu_pd(W + k15 + 12);
    _t4_7 = _asm256_loadu_pd(W + k15 + 24);
    _t4_6 = _asm256_loadu_pd(W + k15 + 36);
    _t4_4 = _asm256_loadu_pd(A + k15);
    _t4_3 = _asm256_loadu_pd(A + k15 + 12);
    _t4_2 = _asm256_loadu_pd(A + k15 + 24);
    _t4_1 = _asm256_loadu_pd(A + k15 + 36);

    // AVX Loader:

    // 4-BLAC: (4x4)^T
    _t4_13 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t4_9, _t4_8), _mm256_unpacklo_pd(_t4_7, _t4_6), 32);
    _t4_14 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t4_9, _t4_8), _mm256_unpackhi_pd(_t4_7, _t4_6), 32);
    _t4_15 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t4_9, _t4_8), _mm256_unpacklo_pd(_t4_7, _t4_6), 49);
    _t4_16 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t4_9, _t4_8), _mm256_unpackhi_pd(_t4_7, _t4_6), 49);

    // 4-BLAC: 4x4 * 4x1
    _t4_10 = _mm256_add_pd(_mm256_permute2f128_pd(_mm256_hadd_pd(_mm256_mul_pd(_t4_13, _t4_5), _mm256_mul_pd(_t4_14, _t4_5)), _mm256_hadd_pd(_mm256_mul_pd(_t4_15, _t4_5), _mm256_mul_pd(_t4_16, _t4_5)), 33), _mm256_blend_pd(_mm256_hadd_pd(_mm256_mul_pd(_t4_13, _t4_5), _mm256_mul_pd(_t4_14, _t4_5)), _mm256_hadd_pd(_mm256_mul_pd(_t4_15, _t4_5), _mm256_mul_pd(_t4_16, _t4_5)), 12));

    // AVX Loader:

    // 4-BLAC: (4x4)^T
    _t4_17 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t4_4, _t4_3), _mm256_unpacklo_pd(_t4_2, _t4_1), 32);
    _t4_18 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t4_4, _t4_3), _mm256_unpackhi_pd(_t4_2, _t4_1), 32);
    _t4_19 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t4_4, _t4_3), _mm256_unpacklo_pd(_t4_2, _t4_1), 49);
    _t4_20 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t4_4, _t4_3), _mm256_unpackhi_pd(_t4_2, _t4_1), 49);

    // 4-BLAC: 4x4 * 4x1
    _t4_11 = _mm256_add_pd(_mm256_permute2f128_pd(_mm256_hadd_pd(_mm256_mul_pd(_t4_17, _t4_0), _mm256_mul_pd(_t4_18, _t4_0)), _mm256_hadd_pd(_mm256_mul_pd(_t4_19, _t4_0), _mm256_mul_pd(_t4_20, _t4_0)), 33), _mm256_blend_pd(_mm256_hadd_pd(_mm256_mul_pd(_t4_17, _t4_0), _mm256_mul_pd(_t4_18, _t4_0)), _mm256_hadd_pd(_mm256_mul_pd(_t4_19, _t4_0), _mm256_mul_pd(_t4_20, _t4_0)), 12));

    // 4-BLAC: 4x1 - 4x1
    _t4_12 = _mm256_sub_pd(_t4_10, _t4_11);

    // AVX Storer:
    _asm256_storeu_pd(x1 + k15, _t4_12);
  }


  for( int i6 = 4; i6 <= 11; i6+=4 ) {

    // AVX Loader:
      _t5_0 = _asm256_loadu_pd(y1 + i6);

    for( int k15 = 0; k15 <= 11; k15+=4 ) {
      _t5_4 = _asm256_loadu_pd(W + 12*i6 + k15);
      _t5_3 = _asm256_loadu_pd(W + 12*i6 + k15 + 12);
      _t5_2 = _asm256_loadu_pd(W + 12*i6 + k15 + 24);
      _t5_1 = _asm256_loadu_pd(W + 12*i6 + k15 + 36);
      _t5_5 = _asm256_loadu_pd(x1 + k15);

      // AVX Loader:

      // 4-BLAC: (4x4)^T
      _t5_7 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t5_4, _t5_3), _mm256_unpacklo_pd(_t5_2, _t5_1), 32);
      _t5_8 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t5_4, _t5_3), _mm256_unpackhi_pd(_t5_2, _t5_1), 32);
      _t5_9 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t5_4, _t5_3), _mm256_unpacklo_pd(_t5_2, _t5_1), 49);
      _t5_10 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t5_4, _t5_3), _mm256_unpackhi_pd(_t5_2, _t5_1), 49);

      // AVX Loader:

      // 4-BLAC: 4x4 * 4x1
      _t5_6 = _mm256_add_pd(_mm256_permute2f128_pd(_mm256_hadd_pd(_mm256_mul_pd(_t5_7, _t5_0), _mm256_mul_pd(_t5_8, _t5_0)), _mm256_hadd_pd(_mm256_mul_pd(_t5_9, _t5_0), _mm256_mul_pd(_t5_10, _t5_0)), 33), _mm256_blend_pd(_mm256_hadd_pd(_mm256_mul_pd(_t5_7, _t5_0), _mm256_mul_pd(_t5_8, _t5_0)), _mm256_hadd_pd(_mm256_mul_pd(_t5_9, _t5_0), _mm256_mul_pd(_t5_10, _t5_0)), 12));

      // AVX Loader:

      // 4-BLAC: 4x1 + 4x1
      _t5_5 = _mm256_add_pd(_t5_5, _t5_6);

      // AVX Storer:
      _asm256_storeu_pd(x1 + k15, _t5_5);
    }
  }


  for( int i0 = 4; i0 <= 11; i0+=4 ) {

    // AVX Loader:
      _t6_0 = _asm256_loadu_pd(y2 + i0);

    for( int k15 = 0; k15 <= 11; k15+=4 ) {
      _t6_4 = _asm256_loadu_pd(A + 12*i0 + k15);
      _t6_3 = _asm256_loadu_pd(A + 12*i0 + k15 + 12);
      _t6_2 = _asm256_loadu_pd(A + 12*i0 + k15 + 24);
      _t6_1 = _asm256_loadu_pd(A + 12*i0 + k15 + 36);
      _t6_5 = _asm256_loadu_pd(x1 + k15);

      // AVX Loader:

      // 4-BLAC: (4x4)^T
      _t6_7 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t6_4, _t6_3), _mm256_unpacklo_pd(_t6_2, _t6_1), 32);
      _t6_8 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t6_4, _t6_3), _mm256_unpackhi_pd(_t6_2, _t6_1), 32);
      _t6_9 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t6_4, _t6_3), _mm256_unpacklo_pd(_t6_2, _t6_1), 49);
      _t6_10 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t6_4, _t6_3), _mm256_unpackhi_pd(_t6_2, _t6_1), 49);

      // AVX Loader:

      // 4-BLAC: 4x4 * 4x1
      _t6_6 = _mm256_add_pd(_mm256_permute2f128_pd(_mm256_hadd_pd(_mm256_mul_pd(_t6_7, _t6_0), _mm256_mul_pd(_t6_8, _t6_0)), _mm256_hadd_pd(_mm256_mul_pd(_t6_9, _t6_0), _mm256_mul_pd(_t6_10, _t6_0)), 33), _mm256_blend_pd(_mm256_hadd_pd(_mm256_mul_pd(_t6_7, _t6_0), _mm256_mul_pd(_t6_8, _t6_0)), _mm256_hadd_pd(_mm256_mul_pd(_t6_9, _t6_0), _mm256_mul_pd(_t6_10, _t6_0)), 12));

      // AVX Loader:

      // 4-BLAC: 4x1 - 4x1
      _t6_5 = _mm256_sub_pd(_t6_5, _t6_6);

      // AVX Storer:
      _asm256_storeu_pd(x1 + k15, _t6_5);
    }
  }


  // Generating : x[12,1] = Sum_{i0} ( S(h(4, 12, i0), ( G(h(4, 12, i0), x0[12,1],h(1, 1, 0)) + ( G(h(1, 1, 0), b[1,1],h(1, 1, 0)) Kro G(h(4, 12, i0), x1[12,1],h(1, 1, 0)) ) ),h(1, 1, 0)) )

  // AVX Loader:

  // 1x1 -> 1x4
  _t7_0 = _mm256_broadcast_sd(&(b));
  _t7_0 = _mm256_blend_pd(_mm256_setzero_pd(), _mm256_blend_pd(_mm256_setzero_pd(), _t7_0, 15), 15);

  for( int i0 = 0; i0 <= 11; i0+=4 ) {
    _t8_1 = _asm256_loadu_pd(x0 + i0);
    _t8_0 = _asm256_loadu_pd(x1 + i0);

    // AVX Loader:

    // AVX Loader:

    // 4-BLAC: 1x4 Kro 4x1
    _t8_3 = _mm256_mul_pd(_t7_0, _t8_0);

    // 4-BLAC: 4x1 + 4x1
    _t8_2 = _mm256_add_pd(_t8_1, _t8_3);

    // AVX Storer:
    _asm256_storeu_pd(x + i0, _t8_2);
  }


  // Generating : z1[12,1] = ( Sum_{i6} ( S(h(4, 12, i6), ( G(h(4, 12, i6), y1[12,1],h(1, 1, 0)) - ( G(h(4, 12, i6), W[12,12],h(4, 12, 0)) * G(h(4, 12, 0), x[12,1],h(1, 1, 0)) ) ),h(1, 1, 0)) ) + Sum_{i0} ( Sum_{i6} ( -$(h(4, 12, i6), ( G(h(4, 12, i6), W[12,12],h(4, 12, i0)) * G(h(4, 12, i0), x[12,1],h(1, 1, 0)) ),h(1, 1, 0)) ) ) )

  // AVX Loader:

    _t9_0 = _asm256_loadu_pd(x);

  for( int i6 = 0; i6 <= 11; i6+=4 ) {
    _t9_5 = _asm256_loadu_pd(y1 + i6);
    _t9_4 = _asm256_loadu_pd(W + 12*i6);
    _t9_3 = _asm256_loadu_pd(W + 12*i6 + 12);
    _t9_2 = _asm256_loadu_pd(W + 12*i6 + 24);
    _t9_1 = _asm256_loadu_pd(W + 12*i6 + 36);

    // AVX Loader:

    // AVX Loader:

    // 4-BLAC: 4x4 * 4x1
    _t9_6 = _mm256_add_pd(_mm256_permute2f128_pd(_mm256_hadd_pd(_mm256_mul_pd(_t9_4, _t9_0), _mm256_mul_pd(_t9_3, _t9_0)), _mm256_hadd_pd(_mm256_mul_pd(_t9_2, _t9_0), _mm256_mul_pd(_t9_1, _t9_0)), 33), _mm256_blend_pd(_mm256_hadd_pd(_mm256_mul_pd(_t9_4, _t9_0), _mm256_mul_pd(_t9_3, _t9_0)), _mm256_hadd_pd(_mm256_mul_pd(_t9_2, _t9_0), _mm256_mul_pd(_t9_1, _t9_0)), 12));

    // 4-BLAC: 4x1 - 4x1
    _t9_7 = _mm256_sub_pd(_t9_5, _t9_6);

    // AVX Storer:
    _asm256_storeu_pd(z1 + i6, _t9_7);
  }


  for( int i0 = 4; i0 <= 11; i0+=4 ) {

    // AVX Loader:
      _t10_0 = _asm256_loadu_pd(x + i0);

    for( int i6 = 0; i6 <= 11; i6+=4 ) {
      _t10_4 = _asm256_loadu_pd(W + i0 + 12*i6);
      _t10_3 = _asm256_loadu_pd(W + i0 + 12*i6 + 12);
      _t10_2 = _asm256_loadu_pd(W + i0 + 12*i6 + 24);
      _t10_1 = _asm256_loadu_pd(W + i0 + 12*i6 + 36);
      _t10_5 = _asm256_loadu_pd(z1 + i6);

      // AVX Loader:

      // AVX Loader:

      // 4-BLAC: 4x4 * 4x1
      _t10_6 = _mm256_add_pd(_mm256_permute2f128_pd(_mm256_hadd_pd(_mm256_mul_pd(_t10_4, _t10_0), _mm256_mul_pd(_t10_3, _t10_0)), _mm256_hadd_pd(_mm256_mul_pd(_t10_2, _t10_0), _mm256_mul_pd(_t10_1, _t10_0)), 33), _mm256_blend_pd(_mm256_hadd_pd(_mm256_mul_pd(_t10_4, _t10_0), _mm256_mul_pd(_t10_3, _t10_0)), _mm256_hadd_pd(_mm256_mul_pd(_t10_2, _t10_0), _mm256_mul_pd(_t10_1, _t10_0)), 12));

      // AVX Loader:

      // 4-BLAC: 4x1 - 4x1
      _t10_5 = _mm256_sub_pd(_t10_5, _t10_6);

      // AVX Storer:
      _asm256_storeu_pd(z1 + i6, _t10_5);
    }
  }


  // Generating : z2[12,1] = ( Sum_{i6} ( S(h(4, 12, i6), ( G(h(4, 12, i6), y2[12,1],h(1, 1, 0)) - ( G(h(4, 12, i6), y[12,1],h(1, 1, 0)) - ( G(h(4, 12, i6), A[12,12],h(4, 12, 0)) * G(h(4, 12, 0), x[12,1],h(1, 1, 0)) ) ) ),h(1, 1, 0)) ) + Sum_{i0} ( Sum_{i6} ( $(h(4, 12, i6), ( G(h(4, 12, i6), A[12,12],h(4, 12, i0)) * G(h(4, 12, i0), x[12,1],h(1, 1, 0)) ),h(1, 1, 0)) ) ) )

  // AVX Loader:

    _t11_0 = _asm256_loadu_pd(x);

  for( int i6 = 0; i6 <= 11; i6+=4 ) {
    _t11_6 = _asm256_loadu_pd(y2 + i6);
    _t11_5 = _asm256_loadu_pd(y + i6);
    _t11_4 = _asm256_loadu_pd(A + 12*i6);
    _t11_3 = _asm256_loadu_pd(A + 12*i6 + 12);
    _t11_2 = _asm256_loadu_pd(A + 12*i6 + 24);
    _t11_1 = _asm256_loadu_pd(A + 12*i6 + 36);

    // AVX Loader:

    // AVX Loader:

    // AVX Loader:

    // 4-BLAC: 4x4 * 4x1
    _t11_7 = _mm256_add_pd(_mm256_permute2f128_pd(_mm256_hadd_pd(_mm256_mul_pd(_t11_4, _t11_0), _mm256_mul_pd(_t11_3, _t11_0)), _mm256_hadd_pd(_mm256_mul_pd(_t11_2, _t11_0), _mm256_mul_pd(_t11_1, _t11_0)), 33), _mm256_blend_pd(_mm256_hadd_pd(_mm256_mul_pd(_t11_4, _t11_0), _mm256_mul_pd(_t11_3, _t11_0)), _mm256_hadd_pd(_mm256_mul_pd(_t11_2, _t11_0), _mm256_mul_pd(_t11_1, _t11_0)), 12));

    // 4-BLAC: 4x1 - 4x1
    _t11_8 = _mm256_sub_pd(_t11_5, _t11_7);

    // 4-BLAC: 4x1 - 4x1
    _t11_9 = _mm256_sub_pd(_t11_6, _t11_8);

    // AVX Storer:
    _asm256_storeu_pd(z2 + i6, _t11_9);
  }


  for( int i0 = 4; i0 <= 11; i0+=4 ) {

    // AVX Loader:
      _t12_0 = _asm256_loadu_pd(x + i0);

    for( int i6 = 0; i6 <= 11; i6+=4 ) {
      _t12_4 = _asm256_loadu_pd(A + i0 + 12*i6);
      _t12_3 = _asm256_loadu_pd(A + i0 + 12*i6 + 12);
      _t12_2 = _asm256_loadu_pd(A + i0 + 12*i6 + 24);
      _t12_1 = _asm256_loadu_pd(A + i0 + 12*i6 + 36);
      _t12_5 = _asm256_loadu_pd(z2 + i6);

      // AVX Loader:

      // AVX Loader:

      // 4-BLAC: 4x4 * 4x1
      _t12_6 = _mm256_add_pd(_mm256_permute2f128_pd(_mm256_hadd_pd(_mm256_mul_pd(_t12_4, _t12_0), _mm256_mul_pd(_t12_3, _t12_0)), _mm256_hadd_pd(_mm256_mul_pd(_t12_2, _t12_0), _mm256_mul_pd(_t12_1, _t12_0)), 33), _mm256_blend_pd(_mm256_hadd_pd(_mm256_mul_pd(_t12_4, _t12_0), _mm256_mul_pd(_t12_3, _t12_0)), _mm256_hadd_pd(_mm256_mul_pd(_t12_2, _t12_0), _mm256_mul_pd(_t12_1, _t12_0)), 12));

      // AVX Loader:

      // 4-BLAC: 4x1 + 4x1
      _t12_5 = _mm256_add_pd(_t12_5, _t12_6);

      // AVX Storer:
      _asm256_storeu_pd(z2 + i6, _t12_5);
    }
  }


  // Generating : v1[12,1] = Sum_{i0} ( S(h(4, 12, i0), ( ( G(h(1, 1, 0), a[1,1],h(1, 1, 0)) Kro G(h(4, 12, i0), v1[12,1],h(1, 1, 0)) ) + ( G(h(1, 1, 0), t[1,1],h(1, 1, 0)) Kro G(h(4, 12, i0), z1[12,1],h(1, 1, 0)) ) ),h(1, 1, 0)) )

  // AVX Loader:

  // 1x1 -> 1x4
  _t13_0 = _mm256_broadcast_sd(&(a));
  _t13_0 = _mm256_blend_pd(_mm256_setzero_pd(), _mm256_blend_pd(_mm256_setzero_pd(), _t13_0, 15), 15);
  // AVX Loader:

  // 1x1 -> 1x4
  _t13_1 = _mm256_broadcast_sd(&(t));
  _t13_1 = _mm256_blend_pd(_mm256_setzero_pd(), _mm256_blend_pd(_mm256_setzero_pd(), _t13_1, 15), 15);

  for( int i0 = 0; i0 <= 11; i0+=4 ) {
    _t14_1 = _asm256_loadu_pd(v1 + i0);
    _t14_0 = _asm256_loadu_pd(z1 + i0);

    // AVX Loader:

    // 4-BLAC: 1x4 Kro 4x1
    _t14_2 = _mm256_mul_pd(_t13_0, _t14_1);

    // AVX Loader:

    // 4-BLAC: 1x4 Kro 4x1
    _t14_3 = _mm256_mul_pd(_t13_1, _t14_0);

    // 4-BLAC: 4x1 + 4x1
    _t14_1 = _mm256_add_pd(_t14_2, _t14_3);

    // AVX Storer:
    _asm256_storeu_pd(v1 + i0, _t14_1);
  }


  // Generating : v2[12,1] = Sum_{i0} ( S(h(4, 12, i0), ( ( G(h(1, 1, 0), a[1,1],h(1, 1, 0)) Kro G(h(4, 12, i0), v2[12,1],h(1, 1, 0)) ) + ( G(h(1, 1, 0), t[1,1],h(1, 1, 0)) Kro G(h(4, 12, i0), z2[12,1],h(1, 1, 0)) ) ),h(1, 1, 0)) )

  // AVX Loader:

  // 1x1 -> 1x4
  _t15_0 = _mm256_broadcast_sd(&(a));

  // AVX Loader:

  // 1x1 -> 1x4
  _t15_1 = _mm256_broadcast_sd(&(t));


  for( int i0 = 0; i0 <= 11; i0+=4 ) {
    _t16_1 = _asm256_loadu_pd(v2 + i0);
    _t16_0 = _asm256_loadu_pd(z2 + i0);

    // AVX Loader:

    // 4-BLAC: 1x4 Kro 4x1
    _t16_2 = _mm256_mul_pd(_t13_0, _t16_1);

    // AVX Loader:

    // 4-BLAC: 1x4 Kro 4x1
    _t16_3 = _mm256_mul_pd(_t13_1, _t16_0);

    // 4-BLAC: 4x1 + 4x1
    _t16_1 = _mm256_add_pd(_t16_2, _t16_3);

    // AVX Storer:
    _asm256_storeu_pd(v2 + i0, _t16_1);
  }

}
