/*
 * ltrtri_kernel.h
 *
Decl { {u'L': LowerTriangular[L, (4, 4), GenMatAccess]} }
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ann: {'part_schemes': {'tril_inv_ow_opt': {'m': 'm1.ll'}}, 'cl1ck_v': 1, 'variant_tag': 'tril_inv_ow_opt_m1'}

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Entry 0:
Eq: Tile( (1, 1), G(h(1, 4, 0), L[4,4],h(1, 4, 0)) ) = ( Tile( (1, 1), 1[1,1] ) Div Tile( (1, 1), G(h(1, 4, 0), L[4,4],h(1, 4, 0)) ) )
Eq.ann: {}
Entry 1:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 1), L[4,4],h(1, 4, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 1), L[4,4],h(1, 4, 0)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), L[4,4],h(1, 4, 0)) ) ) )
Eq.ann: {}
Entry 2:
Eq: Tile( (1, 1), G(h(1, 4, 1), L[4,4],h(1, 4, 1)) ) = ( Tile( (1, 1), 1[1,1] ) Div Tile( (1, 1), G(h(1, 4, 1), L[4,4],h(1, 4, 1)) ) )
Eq.ann: {}
Entry 3:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 2), L[4,4],h(1, 4, 1)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 2), L[4,4],h(1, 4, 1)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), L[4,4],h(1, 4, 1)) ) ) )
Eq.ann: {}
Entry 4:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 2), L[4,4],h(1, 4, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 2), L[4,4],h(1, 4, 0)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 2), L[4,4],h(1, 4, 1)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), L[4,4],h(1, 4, 0)) ) ) ) )
Eq.ann: {}
Entry 5:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), L[4,4],h(1, 4, 0)) ) ) = Neg( ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), L[4,4],h(1, 4, 1)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), L[4,4],h(1, 4, 0)) ) ) ) )
Eq.ann: {}
Entry 6:
Eq: Tile( (1, 1), G(h(1, 4, 2), L[4,4],h(1, 4, 2)) ) = ( Tile( (1, 1), 1[1,1] ) Div Tile( (1, 1), G(h(1, 4, 2), L[4,4],h(1, 4, 2)) ) )
Eq.ann: {}
Entry 7:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), L[4,4],h(1, 4, 2)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), L[4,4],h(1, 4, 2)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), L[4,4],h(1, 4, 2)) ) ) )
Eq.ann: {}
Entry 8:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), L[4,4],h(2, 4, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), L[4,4],h(2, 4, 0)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), L[4,4],h(1, 4, 2)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), L[4,4],h(2, 4, 0)) ) ) ) )
Eq.ann: {}
Entry 9:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), L[4,4],h(2, 4, 0)) ) ) = Neg( ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), L[4,4],h(1, 4, 2)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), L[4,4],h(2, 4, 0)) ) ) ) )
Eq.ann: {}
Entry 10:
Eq: Tile( (1, 1), G(h(1, 4, 3), L[4,4],h(1, 4, 3)) ) = ( Tile( (1, 1), 1[1,1] ) Div Tile( (1, 1), G(h(1, 4, 3), L[4,4],h(1, 4, 3)) ) )
Eq.ann: {}
Entry 11:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), L[4,4],h(3, 4, 0)) ) ) = Neg( ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), L[4,4],h(1, 4, 3)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), L[4,4],h(3, 4, 0)) ) ) ) )
Eq.ann: {}
 *
 * Created on: 2016-10-12
 * Author: danieles
 */

#pragma once

#include <x86intrin.h>


#define PARAM0 4

#define ERRTHRESH 1e-14

#define NUMREP 30

#define floord(n,d) (((n)<0) ? -((-(n)+(d)-1)/(d)) : (n)/(d))
#define ceild(n,d)  (((n)<0) ? -((-(n))/(d)) : ((n)+(d)-1)/(d))
#define max(x,y)    ((x) > (y) ? (x) : (y))
#define min(x,y)    ((x) < (y) ? (x) : (y))


static __attribute__((noinline)) void kernel(double * L)
{
  __m256d _t0_0, _t0_1, _t0_2, _t0_3, _t0_4, _t0_5, _t0_6, _t0_7,
	_t0_8, _t0_9, _t0_10, _t0_11, _t0_12, _t0_13, _t0_14, _t0_15,
	_t0_16, _t0_17, _t0_18, _t0_19, _t0_20, _t0_21, _t0_22, _t0_23,
	_t0_24, _t0_25, _t0_26, _t0_27, _t0_28, _t0_29, _t0_30, _t0_31,
	_t0_32, _t0_33, _t0_34, _t0_35, _t0_36, _t0_37, _t0_38, _t0_39,
	_t0_40, _t0_41, _t0_42, _t0_43, _t0_44, _t0_45, _t0_46, _t0_47,
	_t0_48, _t0_49, _t0_50, _t0_51, _t0_52, _t0_53, _t0_54;

  _t0_0 = _mm256_maskload_pd(L, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0));
  _t0_1 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_mm256_maskload_pd(L + 4, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0)), _mm256_maskload_pd(L + 8, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0))), _mm256_maskload_pd(L + 12, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0)), 32);
  _t0_2 = _mm256_maskload_pd(L + 5, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0));
  _t0_3 = _mm256_shuffle_pd(_mm256_maskload_pd(L + 9, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0)), _mm256_maskload_pd(L + 13, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0)), 0);
  _t0_6 = _mm256_maskload_pd(L + 10, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0));
  _t0_7 = _mm256_maskload_pd(L + 14, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0));
  _t0_10 = _mm256_maskload_pd(L + 15, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0));

  // Constant 1x1 -> 1x4
  _t0_16 = _mm256_set_pd(0, 0, 0, 1);

  // 1x1 -> 1x4
  _t0_21 = _t0_0;

  // 4-BLAC: 1x4 / 1x4
  _t0_36 = _mm256_div_pd(_t0_16, _t0_21);
  _t0_0 = _t0_36;

  // 3x1 -> 4x1
  _t0_50 = _t0_1;

  // 1x1 -> 1x4
  _t0_12 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_0, _t0_0, 32), _mm256_permute2f128_pd(_t0_0, _t0_0, 32), 0);

  // 4-BLAC: 4x1 Kro 1x4
  _t0_13 = _mm256_mul_pd(_t0_50, _t0_12);
  _t0_1 = _t0_13;

  // Constant 1x1 -> 1x4
  _t0_14 = _mm256_set_pd(0, 0, 0, 1);

  // 1x1 -> 1x4
  _t0_15 = _t0_2;

  // 4-BLAC: 1x4 / 1x4
  _t0_17 = _mm256_div_pd(_t0_14, _t0_15);
  _t0_2 = _t0_17;

  // 2x1 -> 4x1
  _t0_18 = _t0_3;

  // 1x1 -> 1x4
  _t0_19 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_2, _t0_2, 32), _mm256_permute2f128_pd(_t0_2, _t0_2, 32), 0);

  // 4-BLAC: 4x1 Kro 1x4
  _t0_20 = _mm256_mul_pd(_t0_18, _t0_19);
  _t0_3 = _t0_20;

  // 2x1 -> 4x1
  _t0_22 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_1, 2), _mm256_permute2f128_pd(_t0_1, _t0_1, 129), 5);

  // 2x1 -> 4x1
  _t0_23 = _t0_3;

  // 1x1 -> 1x4
  _t0_24 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_1, _t0_1, 32), _mm256_permute2f128_pd(_t0_1, _t0_1, 32), 0);

  // 4-BLAC: 4x1 Kro 1x4
  _t0_25 = _mm256_mul_pd(_t0_23, _t0_24);

  // 4-BLAC: 4x1 - 4x1
  _t0_26 = _mm256_sub_pd(_t0_22, _t0_25);
  _t0_4 = _t0_26;

  // 1x1 -> 1x4
  _t0_27 = _t0_2;

  // 1x1 -> 1x4
  _t0_28 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_1, 1);

  // 4-BLAC: 1x4 Kro 1x4
  _t0_29 = _mm256_mul_pd(_t0_27, _t0_28);

  // 4-BLAC: -( 1x4 )
  _t0_30 = _mm256_sub_pd(_mm256_setzero_pd(), _t0_29);
  _t0_5 = _t0_30;

  // Constant 1x1 -> 1x4
  _t0_31 = _mm256_set_pd(0, 0, 0, 1);

  // 1x1 -> 1x4
  _t0_32 = _t0_6;

  // 4-BLAC: 1x4 / 1x4
  _t0_33 = _mm256_div_pd(_t0_31, _t0_32);
  _t0_6 = _t0_33;

  // 1x1 -> 1x4
  _t0_34 = _t0_7;

  // 1x1 -> 1x4
  _t0_35 = _t0_6;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_37 = _mm256_mul_pd(_t0_34, _t0_35);
  _t0_7 = _t0_37;

  // 1x2 -> 1x4
  _t0_38 = _mm256_unpackhi_pd(_mm256_blend_pd(_t0_4, _mm256_setzero_pd(), 12), _mm256_blend_pd(_t0_3, _mm256_setzero_pd(), 12));

  // 1x1 -> 1x4
  _t0_39 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_7, _t0_7, 32), _mm256_permute2f128_pd(_t0_7, _t0_7, 32), 0);

  // 1x2 -> 1x4
  _t0_40 = _mm256_blend_pd(_mm256_unpacklo_pd(_t0_4, _t0_3), _mm256_setzero_pd(), 12);

  // 4-BLAC: 1x4 Kro 1x4
  _t0_41 = _mm256_mul_pd(_t0_39, _t0_40);

  // 4-BLAC: 1x4 - 1x4
  _t0_42 = _mm256_sub_pd(_t0_38, _t0_41);
  _t0_8 = _t0_42;

  // 1x1 -> 1x4
  _t0_43 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_6, _t0_6, 32), _mm256_permute2f128_pd(_t0_6, _t0_6, 32), 0);

  // 1x2 -> 1x4
  _t0_44 = _mm256_blend_pd(_mm256_unpacklo_pd(_t0_4, _t0_3), _mm256_setzero_pd(), 12);

  // 4-BLAC: 1x4 Kro 1x4
  _t0_45 = _mm256_mul_pd(_t0_43, _t0_44);

  // 4-BLAC: -( 1x4 )
  _t0_46 = _mm256_sub_pd(_mm256_setzero_pd(), _t0_45);
  _t0_9 = _t0_46;

  // Constant 1x1 -> 1x4
  _t0_47 = _mm256_set_pd(0, 0, 0, 1);

  // 1x1 -> 1x4
  _t0_48 = _t0_10;

  // 4-BLAC: 1x4 / 1x4
  _t0_49 = _mm256_div_pd(_t0_47, _t0_48);
  _t0_10 = _t0_49;

  // 1x1 -> 1x4
  _t0_51 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_10, _t0_10, 32), _mm256_permute2f128_pd(_t0_10, _t0_10, 32), 0);

  // 1x3 -> 1x4
  _t0_52 = _mm256_blend_pd(_t0_8, _mm256_permute2f128_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_7, 1), _mm256_blend_pd(_mm256_setzero_pd(), _t0_7, 1), 8), 12);

  // 4-BLAC: 1x4 Kro 1x4
  _t0_53 = _mm256_mul_pd(_t0_51, _t0_52);

  // 4-BLAC: -( 1x4 )
  _t0_54 = _mm256_sub_pd(_mm256_setzero_pd(), _t0_53);
  _t0_11 = _t0_54;

  _mm256_maskstore_pd(L, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t0_0);
  _mm256_maskstore_pd(L + 4, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t0_1);
  _mm256_maskstore_pd(L + 8, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _mm256_shuffle_pd(_t0_1, _t0_1, 1));
  _mm256_maskstore_pd(L + 12, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _mm256_permute2f128_pd(_t0_1, _t0_1, 129));
  _mm256_maskstore_pd(L + 5, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t0_2);
  _mm256_maskstore_pd(L + 9, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t0_3);
  _mm256_maskstore_pd(L + 13, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _mm256_shuffle_pd(_t0_3, _t0_3, 1));
  _mm256_maskstore_pd(L + 8, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t0_4);
  _mm256_maskstore_pd(L + 12, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _mm256_shuffle_pd(_t0_4, _t0_4, 1));
  _mm256_maskstore_pd(L + 4, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t0_5);
  _mm256_maskstore_pd(L + 10, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t0_6);
  _mm256_maskstore_pd(L + 14, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t0_7);
  _mm256_maskstore_pd(L + 12, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, 0, 0), _t0_8);
  _mm256_maskstore_pd(L + 8, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, 0, 0), _t0_9);
  _mm256_maskstore_pd(L + 15, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t0_10);
  _mm256_maskstore_pd(L + 12, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63, 0), _t0_11);

}
