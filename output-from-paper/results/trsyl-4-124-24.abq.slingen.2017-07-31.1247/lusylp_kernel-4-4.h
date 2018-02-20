/*
 * lusylp_kernel.h
 *
Decl { {u'X': SquaredMatrix[X, (4, 4), GenMatAccess], u'C': SquaredMatrix[C, (4, 4), GenMatAccess], u'U': UpperTriangular[U, (4, 4), GenMatAccess], u'L': LowerTriangular[L, (4, 4), GenMatAccess]} }
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ann: {'part_schemes': {'Assign_Add_Mul_LowerTriangular_SquaredMatrix_Mul_SquaredMatrix_UpperTriangular_SquaredMatrix_opt': {'m0': 'm04.ll', 'm2': 'm22.ll'}}, 'cl1ck_v': 1, 'variant_tag': 'Assign_Add_Mul_LowerTriangular_SquaredMatrix_Mul_SquaredMatrix_UpperTriangular_SquaredMatrix_opt_m04_m22'}

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Entry 0:
Eq: Tile( (1, 1), G(h(1, 4, 0), X[4,4],h(1, 4, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 0), X[4,4],h(1, 4, 0)) ) Div ( Tile( (1, 1), G(h(1, 4, 0), L[4,4],h(1, 4, 0)) ) + Tile( (1, 1), G(h(1, 4, 0), U[4,4],h(1, 4, 0)) ) ) )
Eq.ann: {}
Entry 1:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), X[4,4],h(3, 4, 1)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), X[4,4],h(3, 4, 1)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), X[4,4],h(1, 4, 0)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), U[4,4],h(3, 4, 1)) ) ) ) )
Eq.ann: {}
Entry 2:
Eq: Tile( (1, 1), G(h(1, 4, 0), X[4,4],h(1, 4, 1)) ) = ( Tile( (1, 1), G(h(1, 4, 0), X[4,4],h(1, 4, 1)) ) Div ( Tile( (1, 1), G(h(1, 4, 0), L[4,4],h(1, 4, 0)) ) + Tile( (1, 1), G(h(1, 4, 1), U[4,4],h(1, 4, 1)) ) ) )
Eq.ann: {}
Entry 3:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), X[4,4],h(2, 4, 2)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), X[4,4],h(2, 4, 2)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), X[4,4],h(1, 4, 1)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), U[4,4],h(2, 4, 2)) ) ) ) )
Eq.ann: {}
Entry 4:
Eq: Tile( (1, 1), G(h(1, 4, 0), X[4,4],h(1, 4, 2)) ) = ( Tile( (1, 1), G(h(1, 4, 0), X[4,4],h(1, 4, 2)) ) Div ( Tile( (1, 1), G(h(1, 4, 0), L[4,4],h(1, 4, 0)) ) + Tile( (1, 1), G(h(1, 4, 2), U[4,4],h(1, 4, 2)) ) ) )
Eq.ann: {}
Entry 5:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), X[4,4],h(1, 4, 3)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), X[4,4],h(1, 4, 3)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), X[4,4],h(1, 4, 2)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), U[4,4],h(1, 4, 3)) ) ) ) )
Eq.ann: {}
Entry 6:
Eq: Tile( (1, 1), G(h(1, 4, 0), X[4,4],h(1, 4, 3)) ) = ( Tile( (1, 1), G(h(1, 4, 0), X[4,4],h(1, 4, 3)) ) Div ( Tile( (1, 1), G(h(1, 4, 0), L[4,4],h(1, 4, 0)) ) + Tile( (1, 1), G(h(1, 4, 3), U[4,4],h(1, 4, 3)) ) ) )
Eq.ann: {}
Entry 7:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 1), X[4,4],h(4, 4, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 1), X[4,4],h(4, 4, 0)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(3, 4, 1), L[4,4],h(1, 4, 0)) ) ) * Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), X[4,4],h(4, 4, 0)) ) ) ) )
Eq.ann: {}
Entry 8:
Eq: Tile( (1, 1), G(h(1, 4, 1), X[4,4],h(1, 4, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 1), X[4,4],h(1, 4, 0)) ) Div ( Tile( (1, 1), G(h(1, 4, 1), L[4,4],h(1, 4, 1)) ) + Tile( (1, 1), G(h(1, 4, 0), U[4,4],h(1, 4, 0)) ) ) )
Eq.ann: {}
Entry 9:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), X[4,4],h(3, 4, 1)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), X[4,4],h(3, 4, 1)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), X[4,4],h(1, 4, 0)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), U[4,4],h(3, 4, 1)) ) ) ) )
Eq.ann: {}
Entry 10:
Eq: Tile( (1, 1), G(h(1, 4, 1), X[4,4],h(1, 4, 1)) ) = ( Tile( (1, 1), G(h(1, 4, 1), X[4,4],h(1, 4, 1)) ) Div ( Tile( (1, 1), G(h(1, 4, 1), L[4,4],h(1, 4, 1)) ) + Tile( (1, 1), G(h(1, 4, 1), U[4,4],h(1, 4, 1)) ) ) )
Eq.ann: {}
Entry 11:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), X[4,4],h(2, 4, 2)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), X[4,4],h(2, 4, 2)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), X[4,4],h(1, 4, 1)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), U[4,4],h(2, 4, 2)) ) ) ) )
Eq.ann: {}
Entry 12:
Eq: Tile( (1, 1), G(h(1, 4, 1), X[4,4],h(1, 4, 2)) ) = ( Tile( (1, 1), G(h(1, 4, 1), X[4,4],h(1, 4, 2)) ) Div ( Tile( (1, 1), G(h(1, 4, 1), L[4,4],h(1, 4, 1)) ) + Tile( (1, 1), G(h(1, 4, 2), U[4,4],h(1, 4, 2)) ) ) )
Eq.ann: {}
Entry 13:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), X[4,4],h(1, 4, 3)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), X[4,4],h(1, 4, 3)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), X[4,4],h(1, 4, 2)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), U[4,4],h(1, 4, 3)) ) ) ) )
Eq.ann: {}
Entry 14:
Eq: Tile( (1, 1), G(h(1, 4, 1), X[4,4],h(1, 4, 3)) ) = ( Tile( (1, 1), G(h(1, 4, 1), X[4,4],h(1, 4, 3)) ) Div ( Tile( (1, 1), G(h(1, 4, 1), L[4,4],h(1, 4, 1)) ) + Tile( (1, 1), G(h(1, 4, 3), U[4,4],h(1, 4, 3)) ) ) )
Eq.ann: {}
Entry 15:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 2), X[4,4],h(4, 4, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 2), X[4,4],h(4, 4, 0)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(2, 4, 2), L[4,4],h(1, 4, 1)) ) ) * Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), X[4,4],h(4, 4, 0)) ) ) ) )
Eq.ann: {}
Entry 16:
Eq: Tile( (1, 1), G(h(1, 4, 2), X[4,4],h(1, 4, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 2), X[4,4],h(1, 4, 0)) ) Div ( Tile( (1, 1), G(h(1, 4, 2), L[4,4],h(1, 4, 2)) ) + Tile( (1, 1), G(h(1, 4, 0), U[4,4],h(1, 4, 0)) ) ) )
Eq.ann: {}
Entry 17:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), X[4,4],h(3, 4, 1)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), X[4,4],h(3, 4, 1)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), X[4,4],h(1, 4, 0)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), U[4,4],h(3, 4, 1)) ) ) ) )
Eq.ann: {}
Entry 18:
Eq: Tile( (1, 1), G(h(1, 4, 2), X[4,4],h(1, 4, 1)) ) = ( Tile( (1, 1), G(h(1, 4, 2), X[4,4],h(1, 4, 1)) ) Div ( Tile( (1, 1), G(h(1, 4, 2), L[4,4],h(1, 4, 2)) ) + Tile( (1, 1), G(h(1, 4, 1), U[4,4],h(1, 4, 1)) ) ) )
Eq.ann: {}
Entry 19:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), X[4,4],h(2, 4, 2)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), X[4,4],h(2, 4, 2)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), X[4,4],h(1, 4, 1)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), U[4,4],h(2, 4, 2)) ) ) ) )
Eq.ann: {}
Entry 20:
Eq: Tile( (1, 1), G(h(1, 4, 2), X[4,4],h(1, 4, 2)) ) = ( Tile( (1, 1), G(h(1, 4, 2), X[4,4],h(1, 4, 2)) ) Div ( Tile( (1, 1), G(h(1, 4, 2), L[4,4],h(1, 4, 2)) ) + Tile( (1, 1), G(h(1, 4, 2), U[4,4],h(1, 4, 2)) ) ) )
Eq.ann: {}
Entry 21:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), X[4,4],h(1, 4, 3)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), X[4,4],h(1, 4, 3)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), X[4,4],h(1, 4, 2)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), U[4,4],h(1, 4, 3)) ) ) ) )
Eq.ann: {}
Entry 22:
Eq: Tile( (1, 1), G(h(1, 4, 2), X[4,4],h(1, 4, 3)) ) = ( Tile( (1, 1), G(h(1, 4, 2), X[4,4],h(1, 4, 3)) ) Div ( Tile( (1, 1), G(h(1, 4, 2), L[4,4],h(1, 4, 2)) ) + Tile( (1, 1), G(h(1, 4, 3), U[4,4],h(1, 4, 3)) ) ) )
Eq.ann: {}
Entry 23:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), X[4,4],h(4, 4, 0)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), X[4,4],h(4, 4, 0)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), L[4,4],h(1, 4, 2)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), X[4,4],h(4, 4, 0)) ) ) ) )
Eq.ann: {}
Entry 24:
Eq: Tile( (1, 1), G(h(1, 4, 3), X[4,4],h(1, 4, 0)) ) = ( Tile( (1, 1), G(h(1, 4, 3), X[4,4],h(1, 4, 0)) ) Div ( Tile( (1, 1), G(h(1, 4, 3), L[4,4],h(1, 4, 3)) ) + Tile( (1, 1), G(h(1, 4, 0), U[4,4],h(1, 4, 0)) ) ) )
Eq.ann: {}
Entry 25:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), X[4,4],h(3, 4, 1)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), X[4,4],h(3, 4, 1)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), X[4,4],h(1, 4, 0)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 0), U[4,4],h(3, 4, 1)) ) ) ) )
Eq.ann: {}
Entry 26:
Eq: Tile( (1, 1), G(h(1, 4, 3), X[4,4],h(1, 4, 1)) ) = ( Tile( (1, 1), G(h(1, 4, 3), X[4,4],h(1, 4, 1)) ) Div ( Tile( (1, 1), G(h(1, 4, 3), L[4,4],h(1, 4, 3)) ) + Tile( (1, 1), G(h(1, 4, 1), U[4,4],h(1, 4, 1)) ) ) )
Eq.ann: {}
Entry 27:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), X[4,4],h(2, 4, 2)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), X[4,4],h(2, 4, 2)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), X[4,4],h(1, 4, 1)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 1), U[4,4],h(2, 4, 2)) ) ) ) )
Eq.ann: {}
Entry 28:
Eq: Tile( (1, 1), G(h(1, 4, 3), X[4,4],h(1, 4, 2)) ) = ( Tile( (1, 1), G(h(1, 4, 3), X[4,4],h(1, 4, 2)) ) Div ( Tile( (1, 1), G(h(1, 4, 3), L[4,4],h(1, 4, 3)) ) + Tile( (1, 1), G(h(1, 4, 2), U[4,4],h(1, 4, 2)) ) ) )
Eq.ann: {}
Entry 29:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), X[4,4],h(1, 4, 3)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), X[4,4],h(1, 4, 3)) ) ) - ( Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 3), X[4,4],h(1, 4, 2)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 4, 2), U[4,4],h(1, 4, 3)) ) ) ) )
Eq.ann: {}
Entry 30:
Eq: Tile( (1, 1), G(h(1, 4, 3), X[4,4],h(1, 4, 3)) ) = ( Tile( (1, 1), G(h(1, 4, 3), X[4,4],h(1, 4, 3)) ) Div ( Tile( (1, 1), G(h(1, 4, 3), L[4,4],h(1, 4, 3)) ) + Tile( (1, 1), G(h(1, 4, 3), U[4,4],h(1, 4, 3)) ) ) )
Eq.ann: {}
 *
 * Created on: 2017-07-31
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

#define ERRTHRESH 1e-14

#define NUMREP 30

#define floord(n,d) (((n)<0) ? -((-(n)+(d)-1)/(d)) : (n)/(d))
#define ceild(n,d)  (((n)<0) ? -((-(n))/(d)) : ((n)+(d)-1)/(d))
#define max(x,y)    ((x) > (y) ? (x) : (y))
#define min(x,y)    ((x) < (y) ? (x) : (y))
#define Max(x,y)    ((x) > (y) ? (x) : (y))
#define Min(x,y)    ((x) < (y) ? (x) : (y))


static __attribute__((noinline)) void kernel(double const * L, double const * U, double * C)
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
	_t0_208;

  _t0_14 = _mm256_castpd128_pd256(_mm_load_sd(&(C[0])));
  _t0_13 = _mm256_castpd128_pd256(_mm_load_sd(&(L[0])));
  _t0_12 = _mm256_castpd128_pd256(_mm_load_sd(&(U[0])));
  _t0_15 = _mm256_maskload_pd(C + 1, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63, 0));
  _t0_11 = _mm256_maskload_pd(U + 1, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63, 0));
  _t0_10 = _mm256_castpd128_pd256(_mm_load_sd(&(U[5])));
  _t0_9 = _mm256_maskload_pd(U + 6, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, 0, 0));
  _t0_8 = _mm256_castpd128_pd256(_mm_load_sd(&(U[10])));
  _t0_7 = _mm256_castpd128_pd256(_mm_load_sd(&(U[11])));
  _t0_6 = _mm256_castpd128_pd256(_mm_load_sd(&(U[15])));
  _t0_20 = _asm256_loadu_pd(C + 4);
  _t0_21 = _asm256_loadu_pd(C + 8);
  _t0_22 = _asm256_loadu_pd(C + 12);
  _t0_5 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_mm256_castpd128_pd256(_mm_load_sd(L + 4)), _mm256_castpd128_pd256(_mm_load_sd(L + 8))), _mm256_castpd128_pd256(_mm_load_sd(L + 12)), 32);
  _t0_4 = _mm256_castpd128_pd256(_mm_load_sd(&(L[5])));
  _t0_3 = _mm256_shuffle_pd(_mm256_castpd128_pd256(_mm_load_sd(L + 9)), _mm256_castpd128_pd256(_mm_load_sd(L + 13)), 0);
  _t0_2 = _mm256_castpd128_pd256(_mm_load_sd(&(L[10])));
  _t0_1 = _mm256_broadcast_sd(&(L[14]));
  _t0_0 = _mm256_castpd128_pd256(_mm_load_sd(&(L[15])));

  // Generating : X[4,4] = S(h(1, 4, 0), ( G(h(1, 4, 0), X[4,4],h(1, 4, 0)) Div ( G(h(1, 4, 0), L[4,4],h(1, 4, 0)) + G(h(1, 4, 0), U[4,4],h(1, 4, 0)) ) ),h(1, 4, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_170 = _t0_14;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_175 = _t0_13;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_180 = _t0_12;

  // 4-BLAC: 1x4 + 1x4
  _t0_203 = _mm256_add_pd(_t0_175, _t0_180);

  // 4-BLAC: 1x4 / 1x4
  _t0_51 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_170), _mm256_castpd256_pd128(_t0_203)));

  // AVX Storer:
  _t0_14 = _t0_51;

  // Generating : X[4,4] = S(h(1, 4, 0), ( G(h(1, 4, 0), X[4,4],h(3, 4, 1)) - ( G(h(1, 4, 0), X[4,4],h(1, 4, 0)) Kro G(h(1, 4, 0), U[4,4],h(3, 4, 1)) ) ),h(3, 4, 1))

  // AVX Loader:

  // 1x3 -> 1x4
  _t0_66 = _t0_15;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_72 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_14, _t0_14, 32), _mm256_permute2f128_pd(_t0_14, _t0_14, 32), 0);

  // AVX Loader:

  // 1x3 -> 1x4
  _t0_80 = _t0_11;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_101 = _mm256_mul_pd(_t0_72, _t0_80);

  // 4-BLAC: 1x4 - 1x4
  _t0_115 = _mm256_sub_pd(_t0_66, _t0_101);

  // AVX Storer:
  _t0_15 = _t0_115;

  // Generating : X[4,4] = S(h(1, 4, 0), ( G(h(1, 4, 0), X[4,4],h(1, 4, 1)) Div ( G(h(1, 4, 0), L[4,4],h(1, 4, 0)) + G(h(1, 4, 1), U[4,4],h(1, 4, 1)) ) ),h(1, 4, 1))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_130 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_15, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_136 = _t0_13;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_142 = _t0_10;

  // 4-BLAC: 1x4 + 1x4
  _t0_155 = _mm256_add_pd(_t0_136, _t0_142);

  // 4-BLAC: 1x4 / 1x4
  _t0_166 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_130), _mm256_castpd256_pd128(_t0_155)));

  // AVX Storer:
  _t0_16 = _t0_166;

  // Generating : X[4,4] = S(h(1, 4, 0), ( G(h(1, 4, 0), X[4,4],h(2, 4, 2)) - ( G(h(1, 4, 0), X[4,4],h(1, 4, 1)) Kro G(h(1, 4, 1), U[4,4],h(2, 4, 2)) ) ),h(2, 4, 2))

  // AVX Loader:

  // 1x2 -> 1x4
  _t0_167 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_15, 6), _mm256_permute2f128_pd(_t0_15, _t0_15, 129), 5);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_168 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_16, _t0_16, 32), _mm256_permute2f128_pd(_t0_16, _t0_16, 32), 0);

  // AVX Loader:

  // 1x2 -> 1x4
  _t0_169 = _t0_9;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_171 = _mm256_mul_pd(_t0_168, _t0_169);

  // 4-BLAC: 1x4 - 1x4
  _t0_172 = _mm256_sub_pd(_t0_167, _t0_171);

  // AVX Storer:
  _t0_17 = _t0_172;

  // Generating : X[4,4] = S(h(1, 4, 0), ( G(h(1, 4, 0), X[4,4],h(1, 4, 2)) Div ( G(h(1, 4, 0), L[4,4],h(1, 4, 0)) + G(h(1, 4, 2), U[4,4],h(1, 4, 2)) ) ),h(1, 4, 2))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_173 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_17, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_174 = _t0_13;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_176 = _t0_8;

  // 4-BLAC: 1x4 + 1x4
  _t0_177 = _mm256_add_pd(_t0_174, _t0_176);

  // 4-BLAC: 1x4 / 1x4
  _t0_178 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_173), _mm256_castpd256_pd128(_t0_177)));

  // AVX Storer:
  _t0_18 = _t0_178;

  // Generating : X[4,4] = S(h(1, 4, 0), ( G(h(1, 4, 0), X[4,4],h(1, 4, 3)) - ( G(h(1, 4, 0), X[4,4],h(1, 4, 2)) Kro G(h(1, 4, 2), U[4,4],h(1, 4, 3)) ) ),h(1, 4, 3))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_179 = _mm256_unpackhi_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_17, 2), _mm256_setzero_pd());

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_181 = _t0_18;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_182 = _t0_7;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_183 = _mm256_mul_pd(_t0_181, _t0_182);

  // 4-BLAC: 1x4 - 1x4
  _t0_184 = _mm256_sub_pd(_t0_179, _t0_183);

  // AVX Storer:
  _t0_19 = _t0_184;

  // Generating : X[4,4] = S(h(1, 4, 0), ( G(h(1, 4, 0), X[4,4],h(1, 4, 3)) Div ( G(h(1, 4, 0), L[4,4],h(1, 4, 0)) + G(h(1, 4, 3), U[4,4],h(1, 4, 3)) ) ),h(1, 4, 3))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_185 = _t0_19;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_186 = _t0_13;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_187 = _t0_6;

  // 4-BLAC: 1x4 + 1x4
  _t0_188 = _mm256_add_pd(_t0_186, _t0_187);

  // 4-BLAC: 1x4 / 1x4
  _t0_189 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_185), _mm256_castpd256_pd128(_t0_188)));

  // AVX Storer:
  _t0_19 = _t0_189;

  // Generating : X[4,4] = S(h(3, 4, 1), ( G(h(3, 4, 1), X[4,4],h(4, 4, 0)) - ( G(h(3, 4, 1), L[4,4],h(1, 4, 0)) * G(h(1, 4, 0), X[4,4],h(4, 4, 0)) ) ),h(4, 4, 0))

  // AVX Loader:

  // 3x4 -> 4x4
  _t0_190 = _t0_20;
  _t0_191 = _t0_21;
  _t0_192 = _t0_22;
  _t0_193 = _mm256_setzero_pd();

  // AVX Loader:

  // 3x1 -> 4x1
  _t0_194 = _t0_5;

  // AVX Loader:

  // 4-BLAC: 4x1 * 1x4
  _t0_195 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_194, _t0_194, 32), _mm256_permute2f128_pd(_t0_194, _t0_194, 32), 0), _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_14, _t0_16), _mm256_unpacklo_pd(_t0_18, _t0_19), 32));
  _t0_196 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_194, _t0_194, 32), _mm256_permute2f128_pd(_t0_194, _t0_194, 32), 15), _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_14, _t0_16), _mm256_unpacklo_pd(_t0_18, _t0_19), 32));
  _t0_197 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_194, _t0_194, 49), _mm256_permute2f128_pd(_t0_194, _t0_194, 49), 0), _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_14, _t0_16), _mm256_unpacklo_pd(_t0_18, _t0_19), 32));
  _t0_198 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_194, _t0_194, 49), _mm256_permute2f128_pd(_t0_194, _t0_194, 49), 15), _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_14, _t0_16), _mm256_unpacklo_pd(_t0_18, _t0_19), 32));

  // 4-BLAC: 4x4 - 4x4
  _t0_199 = _mm256_sub_pd(_t0_190, _t0_195);
  _t0_200 = _mm256_sub_pd(_t0_191, _t0_196);
  _t0_201 = _mm256_sub_pd(_t0_192, _t0_197);
  _t0_202 = _mm256_sub_pd(_t0_193, _t0_198);

  // AVX Storer:
  _t0_20 = _t0_199;
  _t0_21 = _t0_200;
  _t0_22 = _t0_201;

  // Generating : X[4,4] = S(h(1, 4, 1), ( G(h(1, 4, 1), X[4,4],h(1, 4, 0)) Div ( G(h(1, 4, 1), L[4,4],h(1, 4, 1)) + G(h(1, 4, 0), U[4,4],h(1, 4, 0)) ) ),h(1, 4, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_204 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_20, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_205 = _t0_4;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_206 = _t0_12;

  // 4-BLAC: 1x4 + 1x4
  _t0_207 = _mm256_add_pd(_t0_205, _t0_206);

  // 4-BLAC: 1x4 / 1x4
  _t0_208 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_204), _mm256_castpd256_pd128(_t0_207)));

  // AVX Storer:
  _t0_23 = _t0_208;

  // Generating : X[4,4] = S(h(1, 4, 1), ( G(h(1, 4, 1), X[4,4],h(3, 4, 1)) - ( G(h(1, 4, 1), X[4,4],h(1, 4, 0)) Kro G(h(1, 4, 0), U[4,4],h(3, 4, 1)) ) ),h(3, 4, 1))

  // AVX Loader:

  // 1x3 -> 1x4
  _t0_42 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_20, 14), _mm256_permute2f128_pd(_t0_20, _t0_20, 129), 5);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_43 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_23, _t0_23, 32), _mm256_permute2f128_pd(_t0_23, _t0_23, 32), 0);

  // AVX Loader:

  // 1x3 -> 1x4
  _t0_44 = _t0_11;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_45 = _mm256_mul_pd(_t0_43, _t0_44);

  // 4-BLAC: 1x4 - 1x4
  _t0_46 = _mm256_sub_pd(_t0_42, _t0_45);

  // AVX Storer:
  _t0_24 = _t0_46;

  // Generating : X[4,4] = S(h(1, 4, 1), ( G(h(1, 4, 1), X[4,4],h(1, 4, 1)) Div ( G(h(1, 4, 1), L[4,4],h(1, 4, 1)) + G(h(1, 4, 1), U[4,4],h(1, 4, 1)) ) ),h(1, 4, 1))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_47 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_24, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_48 = _t0_4;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_49 = _t0_10;

  // 4-BLAC: 1x4 + 1x4
  _t0_50 = _mm256_add_pd(_t0_48, _t0_49);

  // 4-BLAC: 1x4 / 1x4
  _t0_52 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_47), _mm256_castpd256_pd128(_t0_50)));

  // AVX Storer:
  _t0_25 = _t0_52;

  // Generating : X[4,4] = S(h(1, 4, 1), ( G(h(1, 4, 1), X[4,4],h(2, 4, 2)) - ( G(h(1, 4, 1), X[4,4],h(1, 4, 1)) Kro G(h(1, 4, 1), U[4,4],h(2, 4, 2)) ) ),h(2, 4, 2))

  // AVX Loader:

  // 1x2 -> 1x4
  _t0_53 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_24, 6), _mm256_permute2f128_pd(_t0_24, _t0_24, 129), 5);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_54 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_25, _t0_25, 32), _mm256_permute2f128_pd(_t0_25, _t0_25, 32), 0);

  // AVX Loader:

  // 1x2 -> 1x4
  _t0_55 = _t0_9;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_56 = _mm256_mul_pd(_t0_54, _t0_55);

  // 4-BLAC: 1x4 - 1x4
  _t0_57 = _mm256_sub_pd(_t0_53, _t0_56);

  // AVX Storer:
  _t0_26 = _t0_57;

  // Generating : X[4,4] = S(h(1, 4, 1), ( G(h(1, 4, 1), X[4,4],h(1, 4, 2)) Div ( G(h(1, 4, 1), L[4,4],h(1, 4, 1)) + G(h(1, 4, 2), U[4,4],h(1, 4, 2)) ) ),h(1, 4, 2))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_58 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_26, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_59 = _t0_4;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_60 = _t0_8;

  // 4-BLAC: 1x4 + 1x4
  _t0_61 = _mm256_add_pd(_t0_59, _t0_60);

  // 4-BLAC: 1x4 / 1x4
  _t0_62 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_58), _mm256_castpd256_pd128(_t0_61)));

  // AVX Storer:
  _t0_27 = _t0_62;

  // Generating : X[4,4] = S(h(1, 4, 1), ( G(h(1, 4, 1), X[4,4],h(1, 4, 3)) - ( G(h(1, 4, 1), X[4,4],h(1, 4, 2)) Kro G(h(1, 4, 2), U[4,4],h(1, 4, 3)) ) ),h(1, 4, 3))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_63 = _mm256_unpackhi_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_26, 2), _mm256_setzero_pd());

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_64 = _t0_27;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_65 = _t0_7;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_67 = _mm256_mul_pd(_t0_64, _t0_65);

  // 4-BLAC: 1x4 - 1x4
  _t0_68 = _mm256_sub_pd(_t0_63, _t0_67);

  // AVX Storer:
  _t0_28 = _t0_68;

  // Generating : X[4,4] = S(h(1, 4, 1), ( G(h(1, 4, 1), X[4,4],h(1, 4, 3)) Div ( G(h(1, 4, 1), L[4,4],h(1, 4, 1)) + G(h(1, 4, 3), U[4,4],h(1, 4, 3)) ) ),h(1, 4, 3))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_69 = _t0_28;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_70 = _t0_4;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_71 = _t0_6;

  // 4-BLAC: 1x4 + 1x4
  _t0_73 = _mm256_add_pd(_t0_70, _t0_71);

  // 4-BLAC: 1x4 / 1x4
  _t0_74 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_69), _mm256_castpd256_pd128(_t0_73)));

  // AVX Storer:
  _t0_28 = _t0_74;

  // Generating : X[4,4] = S(h(2, 4, 2), ( G(h(2, 4, 2), X[4,4],h(4, 4, 0)) - ( G(h(2, 4, 2), L[4,4],h(1, 4, 1)) * G(h(1, 4, 1), X[4,4],h(4, 4, 0)) ) ),h(4, 4, 0))

  // AVX Loader:

  // 2x4 -> 4x4
  _t0_75 = _t0_21;
  _t0_76 = _t0_22;
  _t0_77 = _mm256_setzero_pd();
  _t0_78 = _mm256_setzero_pd();

  // AVX Loader:

  // 2x1 -> 4x1
  _t0_79 = _t0_3;

  // AVX Loader:

  // 4-BLAC: 4x1 * 1x4
  _t0_81 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_79, _t0_79, 32), _mm256_permute2f128_pd(_t0_79, _t0_79, 32), 0), _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_23, _t0_25), _mm256_unpacklo_pd(_t0_27, _t0_28), 32));
  _t0_82 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_79, _t0_79, 32), _mm256_permute2f128_pd(_t0_79, _t0_79, 32), 15), _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_23, _t0_25), _mm256_unpacklo_pd(_t0_27, _t0_28), 32));
  _t0_83 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_79, _t0_79, 49), _mm256_permute2f128_pd(_t0_79, _t0_79, 49), 0), _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_23, _t0_25), _mm256_unpacklo_pd(_t0_27, _t0_28), 32));
  _t0_84 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_79, _t0_79, 49), _mm256_permute2f128_pd(_t0_79, _t0_79, 49), 15), _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_23, _t0_25), _mm256_unpacklo_pd(_t0_27, _t0_28), 32));

  // 4-BLAC: 4x4 - 4x4
  _t0_85 = _mm256_sub_pd(_t0_75, _t0_81);
  _t0_86 = _mm256_sub_pd(_t0_76, _t0_82);
  _t0_87 = _mm256_sub_pd(_t0_77, _t0_83);
  _t0_88 = _mm256_sub_pd(_t0_78, _t0_84);

  // AVX Storer:
  _t0_21 = _t0_85;
  _t0_22 = _t0_86;

  // Generating : X[4,4] = S(h(1, 4, 2), ( G(h(1, 4, 2), X[4,4],h(1, 4, 0)) Div ( G(h(1, 4, 2), L[4,4],h(1, 4, 2)) + G(h(1, 4, 0), U[4,4],h(1, 4, 0)) ) ),h(1, 4, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_89 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_21, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_90 = _t0_2;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_91 = _t0_12;

  // 4-BLAC: 1x4 + 1x4
  _t0_92 = _mm256_add_pd(_t0_90, _t0_91);

  // 4-BLAC: 1x4 / 1x4
  _t0_93 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_89), _mm256_castpd256_pd128(_t0_92)));

  // AVX Storer:
  _t0_29 = _t0_93;

  // Generating : X[4,4] = S(h(1, 4, 2), ( G(h(1, 4, 2), X[4,4],h(3, 4, 1)) - ( G(h(1, 4, 2), X[4,4],h(1, 4, 0)) Kro G(h(1, 4, 0), U[4,4],h(3, 4, 1)) ) ),h(3, 4, 1))

  // AVX Loader:

  // 1x3 -> 1x4
  _t0_94 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_21, 14), _mm256_permute2f128_pd(_t0_21, _t0_21, 129), 5);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_95 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_29, _t0_29, 32), _mm256_permute2f128_pd(_t0_29, _t0_29, 32), 0);

  // AVX Loader:

  // 1x3 -> 1x4
  _t0_96 = _t0_11;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_97 = _mm256_mul_pd(_t0_95, _t0_96);

  // 4-BLAC: 1x4 - 1x4
  _t0_98 = _mm256_sub_pd(_t0_94, _t0_97);

  // AVX Storer:
  _t0_30 = _t0_98;

  // Generating : X[4,4] = S(h(1, 4, 2), ( G(h(1, 4, 2), X[4,4],h(1, 4, 1)) Div ( G(h(1, 4, 2), L[4,4],h(1, 4, 2)) + G(h(1, 4, 1), U[4,4],h(1, 4, 1)) ) ),h(1, 4, 1))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_99 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_30, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_100 = _t0_2;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_102 = _t0_10;

  // 4-BLAC: 1x4 + 1x4
  _t0_103 = _mm256_add_pd(_t0_100, _t0_102);

  // 4-BLAC: 1x4 / 1x4
  _t0_104 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_99), _mm256_castpd256_pd128(_t0_103)));

  // AVX Storer:
  _t0_31 = _t0_104;

  // Generating : X[4,4] = S(h(1, 4, 2), ( G(h(1, 4, 2), X[4,4],h(2, 4, 2)) - ( G(h(1, 4, 2), X[4,4],h(1, 4, 1)) Kro G(h(1, 4, 1), U[4,4],h(2, 4, 2)) ) ),h(2, 4, 2))

  // AVX Loader:

  // 1x2 -> 1x4
  _t0_105 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_30, 6), _mm256_permute2f128_pd(_t0_30, _t0_30, 129), 5);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_106 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_31, _t0_31, 32), _mm256_permute2f128_pd(_t0_31, _t0_31, 32), 0);

  // AVX Loader:

  // 1x2 -> 1x4
  _t0_107 = _t0_9;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_108 = _mm256_mul_pd(_t0_106, _t0_107);

  // 4-BLAC: 1x4 - 1x4
  _t0_109 = _mm256_sub_pd(_t0_105, _t0_108);

  // AVX Storer:
  _t0_32 = _t0_109;

  // Generating : X[4,4] = S(h(1, 4, 2), ( G(h(1, 4, 2), X[4,4],h(1, 4, 2)) Div ( G(h(1, 4, 2), L[4,4],h(1, 4, 2)) + G(h(1, 4, 2), U[4,4],h(1, 4, 2)) ) ),h(1, 4, 2))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_110 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_32, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_111 = _t0_2;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_112 = _t0_8;

  // 4-BLAC: 1x4 + 1x4
  _t0_113 = _mm256_add_pd(_t0_111, _t0_112);

  // 4-BLAC: 1x4 / 1x4
  _t0_114 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_110), _mm256_castpd256_pd128(_t0_113)));

  // AVX Storer:
  _t0_33 = _t0_114;

  // Generating : X[4,4] = S(h(1, 4, 2), ( G(h(1, 4, 2), X[4,4],h(1, 4, 3)) - ( G(h(1, 4, 2), X[4,4],h(1, 4, 2)) Kro G(h(1, 4, 2), U[4,4],h(1, 4, 3)) ) ),h(1, 4, 3))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_116 = _mm256_unpackhi_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_32, 2), _mm256_setzero_pd());

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_117 = _t0_33;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_118 = _t0_7;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_119 = _mm256_mul_pd(_t0_117, _t0_118);

  // 4-BLAC: 1x4 - 1x4
  _t0_120 = _mm256_sub_pd(_t0_116, _t0_119);

  // AVX Storer:
  _t0_34 = _t0_120;

  // Generating : X[4,4] = S(h(1, 4, 2), ( G(h(1, 4, 2), X[4,4],h(1, 4, 3)) Div ( G(h(1, 4, 2), L[4,4],h(1, 4, 2)) + G(h(1, 4, 3), U[4,4],h(1, 4, 3)) ) ),h(1, 4, 3))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_121 = _t0_34;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_122 = _t0_2;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_123 = _t0_6;

  // 4-BLAC: 1x4 + 1x4
  _t0_124 = _mm256_add_pd(_t0_122, _t0_123);

  // 4-BLAC: 1x4 / 1x4
  _t0_125 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_121), _mm256_castpd256_pd128(_t0_124)));

  // AVX Storer:
  _t0_34 = _t0_125;

  // Generating : X[4,4] = S(h(1, 4, 3), ( G(h(1, 4, 3), X[4,4],h(4, 4, 0)) - ( G(h(1, 4, 3), L[4,4],h(1, 4, 2)) Kro G(h(1, 4, 2), X[4,4],h(4, 4, 0)) ) ),h(4, 4, 0))

  // AVX Loader:

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_126 = _t0_1;

  // AVX Loader:

  // 4-BLAC: 1x4 Kro 1x4
  _t0_41 = _mm256_mul_pd(_t0_126, _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t0_29, _t0_31), _mm256_unpacklo_pd(_t0_33, _t0_34), 32));

  // 4-BLAC: 1x4 - 1x4
  _t0_22 = _mm256_sub_pd(_t0_22, _t0_41);

  // AVX Storer:

  // Generating : X[4,4] = S(h(1, 4, 3), ( G(h(1, 4, 3), X[4,4],h(1, 4, 0)) Div ( G(h(1, 4, 3), L[4,4],h(1, 4, 3)) + G(h(1, 4, 0), U[4,4],h(1, 4, 0)) ) ),h(1, 4, 0))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_127 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_22, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_128 = _t0_0;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_129 = _t0_12;

  // 4-BLAC: 1x4 + 1x4
  _t0_131 = _mm256_add_pd(_t0_128, _t0_129);

  // 4-BLAC: 1x4 / 1x4
  _t0_132 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_127), _mm256_castpd256_pd128(_t0_131)));

  // AVX Storer:
  _t0_35 = _t0_132;

  // Generating : X[4,4] = S(h(1, 4, 3), ( G(h(1, 4, 3), X[4,4],h(3, 4, 1)) - ( G(h(1, 4, 3), X[4,4],h(1, 4, 0)) Kro G(h(1, 4, 0), U[4,4],h(3, 4, 1)) ) ),h(3, 4, 1))

  // AVX Loader:

  // 1x3 -> 1x4
  _t0_133 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_22, 14), _mm256_permute2f128_pd(_t0_22, _t0_22, 129), 5);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_134 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_35, _t0_35, 32), _mm256_permute2f128_pd(_t0_35, _t0_35, 32), 0);

  // AVX Loader:

  // 1x3 -> 1x4
  _t0_135 = _t0_11;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_137 = _mm256_mul_pd(_t0_134, _t0_135);

  // 4-BLAC: 1x4 - 1x4
  _t0_138 = _mm256_sub_pd(_t0_133, _t0_137);

  // AVX Storer:
  _t0_36 = _t0_138;

  // Generating : X[4,4] = S(h(1, 4, 3), ( G(h(1, 4, 3), X[4,4],h(1, 4, 1)) Div ( G(h(1, 4, 3), L[4,4],h(1, 4, 3)) + G(h(1, 4, 1), U[4,4],h(1, 4, 1)) ) ),h(1, 4, 1))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_139 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_36, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_140 = _t0_0;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_141 = _t0_10;

  // 4-BLAC: 1x4 + 1x4
  _t0_143 = _mm256_add_pd(_t0_140, _t0_141);

  // 4-BLAC: 1x4 / 1x4
  _t0_144 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_139), _mm256_castpd256_pd128(_t0_143)));

  // AVX Storer:
  _t0_37 = _t0_144;

  // Generating : X[4,4] = S(h(1, 4, 3), ( G(h(1, 4, 3), X[4,4],h(2, 4, 2)) - ( G(h(1, 4, 3), X[4,4],h(1, 4, 1)) Kro G(h(1, 4, 1), U[4,4],h(2, 4, 2)) ) ),h(2, 4, 2))

  // AVX Loader:

  // 1x2 -> 1x4
  _t0_145 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_36, 6), _mm256_permute2f128_pd(_t0_36, _t0_36, 129), 5);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_146 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_37, _t0_37, 32), _mm256_permute2f128_pd(_t0_37, _t0_37, 32), 0);

  // AVX Loader:

  // 1x2 -> 1x4
  _t0_147 = _t0_9;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_148 = _mm256_mul_pd(_t0_146, _t0_147);

  // 4-BLAC: 1x4 - 1x4
  _t0_149 = _mm256_sub_pd(_t0_145, _t0_148);

  // AVX Storer:
  _t0_38 = _t0_149;

  // Generating : X[4,4] = S(h(1, 4, 3), ( G(h(1, 4, 3), X[4,4],h(1, 4, 2)) Div ( G(h(1, 4, 3), L[4,4],h(1, 4, 3)) + G(h(1, 4, 2), U[4,4],h(1, 4, 2)) ) ),h(1, 4, 2))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_150 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_38, 1);

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_151 = _t0_0;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_152 = _t0_8;

  // 4-BLAC: 1x4 + 1x4
  _t0_153 = _mm256_add_pd(_t0_151, _t0_152);

  // 4-BLAC: 1x4 / 1x4
  _t0_154 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_150), _mm256_castpd256_pd128(_t0_153)));

  // AVX Storer:
  _t0_39 = _t0_154;

  // Generating : X[4,4] = S(h(1, 4, 3), ( G(h(1, 4, 3), X[4,4],h(1, 4, 3)) - ( G(h(1, 4, 3), X[4,4],h(1, 4, 2)) Kro G(h(1, 4, 2), U[4,4],h(1, 4, 3)) ) ),h(1, 4, 3))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_156 = _mm256_unpackhi_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_38, 2), _mm256_setzero_pd());

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_157 = _t0_39;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_158 = _t0_7;

  // 4-BLAC: 1x4 Kro 1x4
  _t0_159 = _mm256_mul_pd(_t0_157, _t0_158);

  // 4-BLAC: 1x4 - 1x4
  _t0_160 = _mm256_sub_pd(_t0_156, _t0_159);

  // AVX Storer:
  _t0_40 = _t0_160;

  // Generating : X[4,4] = S(h(1, 4, 3), ( G(h(1, 4, 3), X[4,4],h(1, 4, 3)) Div ( G(h(1, 4, 3), L[4,4],h(1, 4, 3)) + G(h(1, 4, 3), U[4,4],h(1, 4, 3)) ) ),h(1, 4, 3))

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_161 = _t0_40;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_162 = _t0_0;

  // AVX Loader:

  // 1x1 -> 1x4
  _t0_163 = _t0_6;

  // 4-BLAC: 1x4 + 1x4
  _t0_164 = _mm256_add_pd(_t0_162, _t0_163);

  // 4-BLAC: 1x4 / 1x4
  _t0_165 = _mm256_castpd128_pd256(_mm_div_pd(_mm256_castpd256_pd128(_t0_161), _mm256_castpd256_pd128(_t0_164)));

  // AVX Storer:
  _t0_40 = _t0_165;

  _mm_store_sd(&(C[0]), _mm256_castpd256_pd128(_t0_14));
  _mm_store_sd(&(C[1]), _mm256_castpd256_pd128(_t0_16));
  _mm_store_sd(&(C[2]), _mm256_castpd256_pd128(_t0_18));
  _mm_store_sd(&(C[3]), _mm256_castpd256_pd128(_t0_19));
  _mm_store_sd(&(C[4]), _mm256_castpd256_pd128(_t0_23));
  _mm_store_sd(&(C[5]), _mm256_castpd256_pd128(_t0_25));
  _mm_store_sd(&(C[6]), _mm256_castpd256_pd128(_t0_27));
  _mm_store_sd(&(C[7]), _mm256_castpd256_pd128(_t0_28));
  _mm_store_sd(&(C[8]), _mm256_castpd256_pd128(_t0_29));
  _mm_store_sd(&(C[9]), _mm256_castpd256_pd128(_t0_31));
  _mm_store_sd(&(C[10]), _mm256_castpd256_pd128(_t0_33));
  _mm_store_sd(&(C[11]), _mm256_castpd256_pd128(_t0_34));
  _mm_store_sd(&(C[12]), _mm256_castpd256_pd128(_t0_35));
  _mm_store_sd(&(C[13]), _mm256_castpd256_pd128(_t0_37));
  _mm_store_sd(&(C[14]), _mm256_castpd256_pd128(_t0_39));
  _mm_store_sd(&(C[15]), _mm256_castpd256_pd128(_t0_40));

}
