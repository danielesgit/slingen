/*
 * upotrf_kernel.h
 *
Decl { {u'A': Symmetric[A, (100, 100), USMatAccess], 'T868': Matrix[T868, (1, 100), GenMatAccess]} }
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ann: {'part_schemes': {'ldiv_ut_ow_opt': {'m': 'm4.ll', 'n': 'n1.ll'}, 'chol_u_ow_opt': {'m': 'm3.ll'}}, 'cl1ck_v': 1, 'variant_tag': 'chol_u_ow_opt_m3_ldiv_ut_ow_opt_m4_n1'}

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Entry 0:
For_{fi377;0;95;4} ( Entry 0:
Eq: Tile( (1, 1), G(h(1, 100, fi377), A[100,100],h(1, 100, fi377)) ) = Sqrt( Tile( (1, 1), G(h(1, 100, fi377), A[100,100],h(1, 100, fi377)) ) )
Eq.ann: {}
Entry 1:
Eq: Tile( (1, 1), G(h(1, 1, 0), T868[1,100],h(1, 100, fi377)) ) = ( Tile( (1, 1), 1[1,1] ) Div Tile( (1, 1), G(h(1, 100, fi377), A[100,100],h(1, 100, fi377)) ) )
Eq.ann: {}
Entry 2:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377), A[100,100],h(3, 100, fi377 + 1)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 1, 0), T868[1,100],h(1, 100, fi377)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377), A[100,100],h(3, 100, fi377 + 1)) ) ) )
Eq.ann: {}
Entry 3:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(3, 100, fi377 + 1), A[100,100],h(3, 100, fi377 + 1)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(3, 100, fi377 + 1), A[100,100],h(3, 100, fi377 + 1)) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377), A[100,100],h(3, 100, fi377 + 1)) ) ) ) * Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377), A[100,100],h(3, 100, fi377 + 1)) ) ) ) )
Eq.ann: {}
Entry 4:
Eq: Tile( (1, 1), G(h(1, 100, fi377 + 1), A[100,100],h(1, 100, fi377 + 1)) ) = Sqrt( Tile( (1, 1), G(h(1, 100, fi377 + 1), A[100,100],h(1, 100, fi377 + 1)) ) )
Eq.ann: {}
Entry 5:
Eq: Tile( (1, 1), G(h(1, 1, 0), T868[1,100],h(1, 100, fi377 + 1)) ) = ( Tile( (1, 1), 1[1,1] ) Div Tile( (1, 1), G(h(1, 100, fi377 + 1), A[100,100],h(1, 100, fi377 + 1)) ) )
Eq.ann: {}
Entry 6:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377 + 1), A[100,100],h(2, 100, fi377 + 2)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 1, 0), T868[1,100],h(1, 100, fi377 + 1)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377 + 1), A[100,100],h(2, 100, fi377 + 2)) ) ) )
Eq.ann: {}
Entry 7:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(2, 100, fi377 + 2), A[100,100],h(2, 100, fi377 + 2)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(2, 100, fi377 + 2), A[100,100],h(2, 100, fi377 + 2)) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377 + 1), A[100,100],h(2, 100, fi377 + 2)) ) ) ) * Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377 + 1), A[100,100],h(2, 100, fi377 + 2)) ) ) ) )
Eq.ann: {}
Entry 8:
Eq: Tile( (1, 1), G(h(1, 100, fi377 + 2), A[100,100],h(1, 100, fi377 + 2)) ) = Sqrt( Tile( (1, 1), G(h(1, 100, fi377 + 2), A[100,100],h(1, 100, fi377 + 2)) ) )
Eq.ann: {}
Entry 9:
Eq: Tile( (1, 1), G(h(1, 100, fi377 + 2), A[100,100],h(1, 100, fi377 + 3)) ) = ( Tile( (1, 1), G(h(1, 100, fi377 + 2), A[100,100],h(1, 100, fi377 + 3)) ) Div Tile( (1, 1), G(h(1, 100, fi377 + 2), A[100,100],h(1, 100, fi377 + 2)) ) )
Eq.ann: {}
Entry 10:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377 + 3), A[100,100],h(1, 100, fi377 + 3)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377 + 3), A[100,100],h(1, 100, fi377 + 3)) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377 + 2), A[100,100],h(1, 100, fi377 + 3)) ) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377 + 2), A[100,100],h(1, 100, fi377 + 3)) ) ) ) )
Eq.ann: {}
Entry 11:
Eq: Tile( (1, 1), G(h(1, 100, fi377 + 3), A[100,100],h(1, 100, fi377 + 3)) ) = Sqrt( Tile( (1, 1), G(h(1, 100, fi377 + 3), A[100,100],h(1, 100, fi377 + 3)) ) )
Eq.ann: {}
Entry 12:
Eq: Tile( (1, 1), G(h(1, 1, 0), T868[1,100],h(1, 100, fi377 + 2)) ) = ( Tile( (1, 1), 1[1,1] ) Div Tile( (1, 1), G(h(1, 100, fi377 + 2), A[100,100],h(1, 100, fi377 + 2)) ) )
Eq.ann: {}
Entry 13:
Eq: Tile( (1, 1), G(h(1, 1, 0), T868[1,100],h(1, 100, fi377 + 3)) ) = ( Tile( (1, 1), 1[1,1] ) Div Tile( (1, 1), G(h(1, 100, fi377 + 3), A[100,100],h(1, 100, fi377 + 3)) ) )
Eq.ann: {}
Entry 14:
For_{fi438;0;-fi377 + 92;4} ( Entry 0:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377), A[100,100],h(4, 100, fi377 + fi438 + 4)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 1, 0), T868[1,100],h(1, 100, fi377)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377), A[100,100],h(4, 100, fi377 + fi438 + 4)) ) ) )
Eq.ann: {}
Entry 1:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(3, 100, fi377 + 1), A[100,100],h(4, 100, fi377 + fi438 + 4)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(3, 100, fi377 + 1), A[100,100],h(4, 100, fi377 + fi438 + 4)) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377), A[100,100],h(3, 100, fi377 + 1)) ) ) ) * Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377), A[100,100],h(4, 100, fi377 + fi438 + 4)) ) ) ) )
Eq.ann: {}
Entry 2:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377 + 1), A[100,100],h(4, 100, fi377 + fi438 + 4)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 1, 0), T868[1,100],h(1, 100, fi377 + 1)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377 + 1), A[100,100],h(4, 100, fi377 + fi438 + 4)) ) ) )
Eq.ann: {}
Entry 3:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(2, 100, fi377 + 2), A[100,100],h(4, 100, fi377 + fi438 + 4)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(2, 100, fi377 + 2), A[100,100],h(4, 100, fi377 + fi438 + 4)) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377 + 1), A[100,100],h(2, 100, fi377 + 2)) ) ) ) * Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377 + 1), A[100,100],h(4, 100, fi377 + fi438 + 4)) ) ) ) )
Eq.ann: {}
Entry 4:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377 + 2), A[100,100],h(4, 100, fi377 + fi438 + 4)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 1, 0), T868[1,100],h(1, 100, fi377 + 2)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377 + 2), A[100,100],h(4, 100, fi377 + fi438 + 4)) ) ) )
Eq.ann: {}
Entry 5:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377 + 3), A[100,100],h(4, 100, fi377 + fi438 + 4)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377 + 3), A[100,100],h(4, 100, fi377 + fi438 + 4)) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377 + 2), A[100,100],h(1, 100, fi377 + 3)) ) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377 + 2), A[100,100],h(4, 100, fi377 + fi438 + 4)) ) ) ) )
Eq.ann: {}
Entry 6:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377 + 3), A[100,100],h(4, 100, fi377 + fi438 + 4)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 1, 0), T868[1,100],h(1, 100, fi377 + 3)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 100, fi377 + 3), A[100,100],h(4, 100, fi377 + fi438 + 4)) ) ) )
Eq.ann: {}
 )Entry 15:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(-fi377 + 96, 100, fi377 + 4), A[100,100],h(-fi377 + 96, 100, fi377 + 4)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(-fi377 + 96, 100, fi377 + 4), A[100,100],h(-fi377 + 96, 100, fi377 + 4)) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), G(h(4, 100, fi377), A[100,100],h(-fi377 + 96, 100, fi377 + 4)) ) ) ) * Tile( (1, 1), Tile( (4, 4), G(h(4, 100, fi377), A[100,100],h(-fi377 + 96, 100, fi377 + 4)) ) ) ) )
Eq.ann: {}
 )Entry 1:
Eq: Tile( (1, 1), G(h(1, 100, 96), A[100,100],h(1, 100, 96)) ) = Sqrt( Tile( (1, 1), G(h(1, 100, 96), A[100,100],h(1, 100, 96)) ) )
Eq.ann: {}
Entry 2:
Eq: Tile( (1, 1), G(h(1, 1, 0), T868[1,100],h(1, 100, 96)) ) = ( Tile( (1, 1), 1[1,1] ) Div Tile( (1, 1), G(h(1, 100, 96), A[100,100],h(1, 100, 96)) ) )
Eq.ann: {}
Entry 3:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 100, 96), A[100,100],h(3, 100, 97)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 1, 0), T868[1,100],h(1, 100, 96)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 100, 96), A[100,100],h(3, 100, 97)) ) ) )
Eq.ann: {}
Entry 4:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(3, 100, 97), A[100,100],h(3, 100, 97)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(3, 100, 97), A[100,100],h(3, 100, 97)) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), G(h(1, 100, 96), A[100,100],h(3, 100, 97)) ) ) ) * Tile( (1, 1), Tile( (4, 4), G(h(1, 100, 96), A[100,100],h(3, 100, 97)) ) ) ) )
Eq.ann: {}
Entry 5:
Eq: Tile( (1, 1), G(h(1, 100, 97), A[100,100],h(1, 100, 97)) ) = Sqrt( Tile( (1, 1), G(h(1, 100, 97), A[100,100],h(1, 100, 97)) ) )
Eq.ann: {}
Entry 6:
Eq: Tile( (1, 1), G(h(1, 1, 0), T868[1,100],h(1, 100, 97)) ) = ( Tile( (1, 1), 1[1,1] ) Div Tile( (1, 1), G(h(1, 100, 97), A[100,100],h(1, 100, 97)) ) )
Eq.ann: {}
Entry 7:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 100, 97), A[100,100],h(2, 100, 98)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 1, 0), T868[1,100],h(1, 100, 97)) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 100, 97), A[100,100],h(2, 100, 98)) ) ) )
Eq.ann: {}
Entry 8:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(2, 100, 98), A[100,100],h(2, 100, 98)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(2, 100, 98), A[100,100],h(2, 100, 98)) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), G(h(1, 100, 97), A[100,100],h(2, 100, 98)) ) ) ) * Tile( (1, 1), Tile( (4, 4), G(h(1, 100, 97), A[100,100],h(2, 100, 98)) ) ) ) )
Eq.ann: {}
Entry 9:
Eq: Tile( (1, 1), G(h(1, 100, 98), A[100,100],h(1, 100, 98)) ) = Sqrt( Tile( (1, 1), G(h(1, 100, 98), A[100,100],h(1, 100, 98)) ) )
Eq.ann: {}
Entry 10:
Eq: Tile( (1, 1), G(h(1, 100, 98), A[100,100],h(1, 100, 99)) ) = ( Tile( (1, 1), G(h(1, 100, 98), A[100,100],h(1, 100, 99)) ) Div Tile( (1, 1), G(h(1, 100, 98), A[100,100],h(1, 100, 98)) ) )
Eq.ann: {}
Entry 11:
Eq: Tile( (1, 1), Tile( (4, 4), G(h(1, 100, 99), A[100,100],h(1, 100, 99)) ) ) = ( Tile( (1, 1), Tile( (4, 4), G(h(1, 100, 99), A[100,100],h(1, 100, 99)) ) ) - ( T( Tile( (1, 1), Tile( (4, 4), G(h(1, 100, 98), A[100,100],h(1, 100, 99)) ) ) ) Kro Tile( (1, 1), Tile( (4, 4), G(h(1, 100, 98), A[100,100],h(1, 100, 99)) ) ) ) )
Eq.ann: {}
Entry 12:
Eq: Tile( (1, 1), G(h(1, 100, 99), A[100,100],h(1, 100, 99)) ) = Sqrt( Tile( (1, 1), G(h(1, 100, 99), A[100,100],h(1, 100, 99)) ) )
Eq.ann: {}
 *
 * Created on: 2016-10-09
 * Author: danieles
 */

#pragma once

#include <x86intrin.h>


#define PARAM0 100

#define ERRTHRESH 1e-14

#define NUMREP 30

#define floord(n,d) (((n)<0) ? -((-(n)+(d)-1)/(d)) : (n)/(d))
#define ceild(n,d)  (((n)<0) ? -((-(n))/(d)) : ((n)+(d)-1)/(d))
#define max(x,y)    ((x) > (y) ? (x) : (y))
#define min(x,y)    ((x) < (y) ? (x) : (y))


static __attribute__((noinline)) void kernel(double * A)
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
	_t0_80;
  __m256d _t1_0, _t1_1, _t1_2, _t1_3, _t1_4, _t1_5, _t1_6, _t1_7,
	_t1_8, _t1_9, _t1_10, _t1_11, _t1_12, _t1_13, _t1_14, _t1_15,
	_t1_16, _t1_17, _t1_18, _t1_19, _t1_20, _t1_21, _t1_22, _t1_23,
	_t1_24, _t1_25, _t1_26, _t1_27, _t1_28, _t1_29, _t1_30, _t1_31,
	_t1_32, _t1_33, _t1_34, _t1_35, _t1_36, _t1_37, _t1_38;
  __m256d _t2_0, _t2_1, _t2_2, _t2_3, _t2_4, _t2_5, _t2_6, _t2_7,
	_t2_8, _t2_9, _t2_10, _t2_11, _t2_12, _t2_13, _t2_14, _t2_15,
	_t2_16, _t2_17, _t2_18, _t2_19, _t2_20, _t2_21, _t2_22, _t2_23;
  __m256d _t3_0, _t3_1, _t3_2, _t3_3, _t3_4, _t3_5, _t3_6, _t3_7,
	_t3_8, _t3_9, _t3_10, _t3_11, _t3_12, _t3_13, _t3_14, _t3_15;
  __m256d _t4_0, _t4_1, _t4_2, _t4_3, _t4_4, _t4_5, _t4_6, _t4_7,
	_t4_8, _t4_9, _t4_10, _t4_11, _t4_12, _t4_13, _t4_14, _t4_15,
	_t4_16, _t4_17, _t4_18, _t4_19, _t4_20, _t4_21, _t4_22, _t4_23;
  __m256d _t5_0, _t5_1, _t5_2, _t5_3, _t5_4, _t5_5, _t5_6, _t5_7,
	_t5_8, _t5_9, _t5_10, _t5_11, _t5_12, _t5_13, _t5_14, _t5_15,
	_t5_16, _t5_17, _t5_18, _t5_19, _t5_20, _t5_21, _t5_22, _t5_23,
	_t5_24, _t5_25, _t5_26, _t5_27, _t5_28, _t5_29, _t5_30, _t5_31,
	_t5_32, _t5_33, _t5_34, _t5_35, _t5_36, _t5_37, _t5_38, _t5_39,
	_t5_40, _t5_41, _t5_42, _t5_43, _t5_44, _t5_45, _t5_46, _t5_47,
	_t5_48, _t5_49, _t5_50, _t5_51, _t5_52, _t5_53, _t5_54, _t5_55,
	_t5_56, _t5_57, _t5_58, _t5_59, _t5_60, _t5_61, _t5_62, _t5_63,
	_t5_64, _t5_65, _t5_66, _t5_67, _t5_68, _t5_69, _t5_70, _t5_71,
	_t5_72, _t5_73, _t5_74, _t5_75, _t5_76, _t5_77, _t5_78, _t5_79,
	_t5_80, _t5_81, _t5_82, _t5_83, _t5_84, _t5_85, _t5_86, _t5_87,
	_t5_88, _t5_89, _t5_90, _t5_91, _t5_92, _t5_93, _t5_94, _t5_95,
	_t5_96, _t5_97, _t5_98, _t5_99, _t5_100, _t5_101, _t5_102, _t5_103,
	_t5_104, _t5_105, _t5_106, _t5_107, _t5_108, _t5_109, _t5_110, _t5_111,
	_t5_112, _t5_113, _t5_114, _t5_115, _t5_116, _t5_117, _t5_118, _t5_119,
	_t5_120, _t5_121, _t5_122, _t5_123, _t5_124, _t5_125, _t5_126, _t5_127,
	_t5_128, _t5_129, _t5_130, _t5_131, _t5_132, _t5_133, _t5_134, _t5_135,
	_t5_136, _t5_137, _t5_138, _t5_139, _t5_140, _t5_141, _t5_142, _t5_143,
	_t5_144, _t5_145, _t5_146, _t5_147, _t5_148, _t5_149, _t5_150, _t5_151,
	_t5_152, _t5_153, _t5_154, _t5_155, _t5_156, _t5_157, _t5_158, _t5_159,
	_t5_160, _t5_161, _t5_162, _t5_163, _t5_164, _t5_165, _t5_166, _t5_167,
	_t5_168, _t5_169, _t5_170, _t5_171, _t5_172, _t5_173, _t5_174, _t5_175,
	_t5_176, _t5_177, _t5_178, _t5_179, _t5_180, _t5_181, _t5_182, _t5_183,
	_t5_184, _t5_185, _t5_186, _t5_187, _t5_188, _t5_189, _t5_190, _t5_191,
	_t5_192, _t5_193, _t5_194, _t5_195, _t5_196, _t5_197, _t5_198, _t5_199,
	_t5_200, _t5_201, _t5_202, _t5_203, _t5_204, _t5_205, _t5_206, _t5_207,
	_t5_208, _t5_209, _t5_210, _t5_211, _t5_212;


  for( int fi377 = 0; fi377 <= 91; fi377+=4 ) {
    _t0_0 = _mm256_maskload_pd(A + 101*fi377, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0));
    _t0_2 = _mm256_maskload_pd(A + 101*fi377 + 1, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63, 0));
    _t0_3 = _mm256_maskload_pd(A + 101*fi377 + 101, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63, 0));
    _t0_4 = _mm256_maskload_pd(A + 101*fi377 + 201, _mm256_setr_epi64x(0, (__int64)1 << 63, (__int64)1 << 63, 0));
    _t0_5 = _mm256_maskload_pd(A + 101*fi377 + 301, _mm256_setr_epi64x(0, 0, (__int64)1 << 63, 0));

    // 1x1 -> 1x4
    _t0_25 = _t0_0;

    // 4-BLAC: sqrt(1x4)
    _t0_26 = _mm256_sqrt_pd(_t0_25);
    _t0_0 = _t0_26;

    // Constant 1x1 -> 1x4
    _t0_27 = _mm256_set_pd(0, 0, 0, 1);

    // 1x1 -> 1x4
    _t0_28 = _t0_0;

    // 4-BLAC: 1x4 / 1x4
    _t0_29 = _mm256_div_pd(_t0_27, _t0_28);
    _t0_1 = _t0_29;

    // 1x1 -> 1x4
    _t0_30 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_1, _t0_1, 32), _mm256_permute2f128_pd(_t0_1, _t0_1, 32), 0);

    // 1x3 -> 1x4
    _t0_31 = _t0_2;

    // 4-BLAC: 1x4 Kro 1x4
    _t0_32 = _mm256_mul_pd(_t0_30, _t0_31);
    _t0_2 = _t0_32;

    // 3x3 -> 4x4 - UpSymm
    _t0_33 = _t0_3;
    _t0_34 = _mm256_blend_pd(_mm256_shuffle_pd(_t0_3, _t0_4, 3), _t0_4, 12);
    _t0_35 = _mm256_permute2f128_pd(_mm256_shuffle_pd(_t0_3, _t0_4, 0), _t0_5, 49);
    _t0_36 = _mm256_setzero_pd();

    // 1x3 -> 1x4
    _t0_37 = _t0_2;

    // 4-BLAC: (1x4)^T
    _t0_38 = _t0_37;

    // 1x3 -> 1x4
    _t0_39 = _t0_2;

    // 4-BLAC: 4x1 * 1x4
    _t0_40 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_38, _t0_38, 32), _mm256_permute2f128_pd(_t0_38, _t0_38, 32), 0), _t0_39);
    _t0_41 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_38, _t0_38, 32), _mm256_permute2f128_pd(_t0_38, _t0_38, 32), 15), _t0_39);
    _t0_42 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_38, _t0_38, 49), _mm256_permute2f128_pd(_t0_38, _t0_38, 49), 0), _t0_39);
    _t0_43 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_38, _t0_38, 49), _mm256_permute2f128_pd(_t0_38, _t0_38, 49), 15), _t0_39);

    // 4-BLAC: 4x4 - 4x4
    _t0_44 = _mm256_sub_pd(_t0_33, _t0_40);
    _t0_45 = _mm256_sub_pd(_t0_34, _t0_41);
    _t0_46 = _mm256_sub_pd(_t0_35, _t0_42);
    _t0_47 = _mm256_sub_pd(_t0_36, _t0_43);

    // 4x4 -> 3x3 - UpSymm
    _t0_3 = _t0_44;
    _t0_4 = _t0_45;
    _t0_5 = _t0_46;

    // 1x1 -> 1x4
    _t0_48 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_3, 1);

    // 4-BLAC: sqrt(1x4)
    _t0_49 = _mm256_sqrt_pd(_t0_48);
    _t0_6 = _t0_49;

    // Constant 1x1 -> 1x4
    _t0_50 = _mm256_set_pd(0, 0, 0, 1);

    // 1x1 -> 1x4
    _t0_51 = _t0_6;

    // 4-BLAC: 1x4 / 1x4
    _t0_52 = _mm256_div_pd(_t0_50, _t0_51);
    _t0_7 = _t0_52;

    // 1x1 -> 1x4
    _t0_53 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_7, _t0_7, 32), _mm256_permute2f128_pd(_t0_7, _t0_7, 32), 0);

    // 1x2 -> 1x4
    _t0_54 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_3, 6), _mm256_permute2f128_pd(_t0_3, _t0_3, 129), 5);

    // 4-BLAC: 1x4 Kro 1x4
    _t0_55 = _mm256_mul_pd(_t0_53, _t0_54);
    _t0_8 = _t0_55;

    // 2x2 -> 4x4 - UpSymm
    _t0_56 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_4, 6), _mm256_permute2f128_pd(_t0_4, _t0_4, 129), 5);
    _t0_57 = _mm256_shuffle_pd(_mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_4, 6), _mm256_permute2f128_pd(_t0_4, _t0_4, 129), 5), _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_5, 4), _mm256_permute2f128_pd(_t0_5, _t0_5, 129), 5), 3);
    _t0_58 = _mm256_setzero_pd();
    _t0_59 = _mm256_setzero_pd();

    // 1x2 -> 1x4
    _t0_60 = _t0_8;

    // 4-BLAC: (1x4)^T
    _t0_61 = _t0_60;

    // 1x2 -> 1x4
    _t0_62 = _t0_8;

    // 4-BLAC: 4x1 * 1x4
    _t0_63 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_61, _t0_61, 32), _mm256_permute2f128_pd(_t0_61, _t0_61, 32), 0), _t0_62);
    _t0_64 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_61, _t0_61, 32), _mm256_permute2f128_pd(_t0_61, _t0_61, 32), 15), _t0_62);
    _t0_65 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_61, _t0_61, 49), _mm256_permute2f128_pd(_t0_61, _t0_61, 49), 0), _t0_62);
    _t0_66 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_61, _t0_61, 49), _mm256_permute2f128_pd(_t0_61, _t0_61, 49), 15), _t0_62);

    // 4-BLAC: 4x4 - 4x4
    _t0_67 = _mm256_sub_pd(_t0_56, _t0_63);
    _t0_68 = _mm256_sub_pd(_t0_57, _t0_64);
    _t0_69 = _mm256_sub_pd(_t0_58, _t0_65);
    _t0_70 = _mm256_sub_pd(_t0_59, _t0_66);

    // 4x4 -> 2x2 - UpSymm
    _t0_9 = _t0_67;
    _t0_10 = _t0_68;

    // 1x1 -> 1x4
    _t0_71 = _mm256_blend_pd(_mm256_setzero_pd(), _t0_9, 1);

    // 4-BLAC: sqrt(1x4)
    _t0_72 = _mm256_sqrt_pd(_t0_71);
    _t0_11 = _t0_72;

    // 1x1 -> 1x4
    _t0_73 = _mm256_unpackhi_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_9, 2), _mm256_setzero_pd());

    // 1x1 -> 1x4
    _t0_74 = _t0_11;

    // 4-BLAC: 1x4 / 1x4
    _t0_75 = _mm256_div_pd(_t0_73, _t0_74);
    _t0_12 = _t0_75;

    // 1x1 -> 1x4
    _t0_76 = _mm256_unpackhi_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t0_10, 2), _mm256_setzero_pd());

    // 1x1 -> 1x4
    _t0_77 = _t0_12;

    // 4-BLAC: (4x1)^T
    _t0_78 = _t0_77;

    // 1x1 -> 1x4
    _t0_79 = _t0_12;

    // 4-BLAC: 1x4 Kro 1x4
    _t0_80 = _mm256_mul_pd(_t0_78, _t0_79);

    // 4-BLAC: 1x4 - 1x4
    _t0_16 = _mm256_sub_pd(_t0_76, _t0_80);
    _t0_13 = _t0_16;

    // 1x1 -> 1x4
    _t0_17 = _t0_13;

    // 4-BLAC: sqrt(1x4)
    _t0_18 = _mm256_sqrt_pd(_t0_17);
    _t0_13 = _t0_18;

    // Constant 1x1 -> 1x4
    _t0_19 = _mm256_set_pd(0, 0, 0, 1);

    // 1x1 -> 1x4
    _t0_20 = _t0_11;

    // 4-BLAC: 1x4 / 1x4
    _t0_21 = _mm256_div_pd(_t0_19, _t0_20);
    _t0_14 = _t0_21;

    // Constant 1x1 -> 1x4
    _t0_22 = _mm256_set_pd(0, 0, 0, 1);

    // 1x1 -> 1x4
    _t0_23 = _t0_13;

    // 4-BLAC: 1x4 / 1x4
    _t0_24 = _mm256_div_pd(_t0_22, _t0_23);
    _t0_15 = _t0_24;
    _mm256_maskstore_pd(A + 101*fi377 + 101, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63, 0), _t0_3);
    _mm256_maskstore_pd(A + 101*fi377 + 201, _mm256_setr_epi64x(0, (__int64)1 << 63, (__int64)1 << 63, 0), _t0_4);
    _mm256_maskstore_pd(A + 101*fi377 + 202, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, 0, 0), _t0_9);

    for( int fi438 = 0; fi438 <= -fi377 + 92; fi438+=4 ) {
      _t1_3 = _mm256_loadu_pd(A + 101*fi377 + fi438 + 4);
      _t1_0 = _mm256_loadu_pd(A + 101*fi377 + fi438 + 104);
      _t1_1 = _mm256_loadu_pd(A + 101*fi377 + fi438 + 204);
      _t1_2 = _mm256_loadu_pd(A + 101*fi377 + fi438 + 304);

      // 1x1 -> 1x4
      _t1_5 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_1, _t0_1, 32), _mm256_permute2f128_pd(_t0_1, _t0_1, 32), 0);

      // 4-BLAC: 1x4 Kro 1x4
      _t1_3 = _mm256_mul_pd(_t1_5, _t1_3);

      // 3x4 -> 4x4
      _t1_6 = _t1_0;
      _t1_7 = _t1_1;
      _t1_8 = _t1_2;
      _t1_9 = _mm256_setzero_pd();

      // 1x3 -> 1x4
      _t1_10 = _t0_2;

      // 4-BLAC: (1x4)^T
      _t1_11 = _t1_10;

      // 4-BLAC: 4x1 * 1x4
      _t1_12 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t1_11, _t1_11, 32), _mm256_permute2f128_pd(_t1_11, _t1_11, 32), 0), _t1_3);
      _t1_13 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t1_11, _t1_11, 32), _mm256_permute2f128_pd(_t1_11, _t1_11, 32), 15), _t1_3);
      _t1_14 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t1_11, _t1_11, 49), _mm256_permute2f128_pd(_t1_11, _t1_11, 49), 0), _t1_3);
      _t1_15 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t1_11, _t1_11, 49), _mm256_permute2f128_pd(_t1_11, _t1_11, 49), 15), _t1_3);

      // 4-BLAC: 4x4 - 4x4
      _t1_16 = _mm256_sub_pd(_t1_6, _t1_12);
      _t1_17 = _mm256_sub_pd(_t1_7, _t1_13);
      _t1_18 = _mm256_sub_pd(_t1_8, _t1_14);
      _t1_19 = _mm256_sub_pd(_t1_9, _t1_15);
      _t1_0 = _t1_16;
      _t1_1 = _t1_17;
      _t1_2 = _t1_18;

      // 1x1 -> 1x4
      _t1_20 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_7, _t0_7, 32), _mm256_permute2f128_pd(_t0_7, _t0_7, 32), 0);

      // 4-BLAC: 1x4 Kro 1x4
      _t1_0 = _mm256_mul_pd(_t1_20, _t1_0);

      // 2x4 -> 4x4
      _t1_21 = _t1_1;
      _t1_22 = _t1_2;
      _t1_23 = _mm256_setzero_pd();
      _t1_24 = _mm256_setzero_pd();

      // 1x2 -> 1x4
      _t1_25 = _t0_8;

      // 4-BLAC: (1x4)^T
      _t1_26 = _t1_25;

      // 4-BLAC: 4x1 * 1x4
      _t1_27 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t1_26, _t1_26, 32), _mm256_permute2f128_pd(_t1_26, _t1_26, 32), 0), _t1_0);
      _t1_28 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t1_26, _t1_26, 32), _mm256_permute2f128_pd(_t1_26, _t1_26, 32), 15), _t1_0);
      _t1_29 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t1_26, _t1_26, 49), _mm256_permute2f128_pd(_t1_26, _t1_26, 49), 0), _t1_0);
      _t1_30 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t1_26, _t1_26, 49), _mm256_permute2f128_pd(_t1_26, _t1_26, 49), 15), _t1_0);

      // 4-BLAC: 4x4 - 4x4
      _t1_31 = _mm256_sub_pd(_t1_21, _t1_27);
      _t1_32 = _mm256_sub_pd(_t1_22, _t1_28);
      _t1_33 = _mm256_sub_pd(_t1_23, _t1_29);
      _t1_34 = _mm256_sub_pd(_t1_24, _t1_30);
      _t1_1 = _t1_31;
      _t1_2 = _t1_32;

      // 1x1 -> 1x4
      _t1_35 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_14, _t0_14, 32), _mm256_permute2f128_pd(_t0_14, _t0_14, 32), 0);

      // 4-BLAC: 1x4 Kro 1x4
      _t1_1 = _mm256_mul_pd(_t1_35, _t1_1);

      // 1x1 -> 1x4
      _t1_36 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_12, _t0_12, 32), _mm256_permute2f128_pd(_t0_12, _t0_12, 32), 0);

      // 4-BLAC: (4x1)^T
      _t1_37 = _t1_36;

      // 4-BLAC: 1x4 Kro 1x4
      _t1_4 = _mm256_mul_pd(_t1_37, _t1_1);

      // 4-BLAC: 1x4 - 1x4
      _t1_2 = _mm256_sub_pd(_t1_2, _t1_4);

      // 1x1 -> 1x4
      _t1_38 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t0_15, _t0_15, 32), _mm256_permute2f128_pd(_t0_15, _t0_15, 32), 0);

      // 4-BLAC: 1x4 Kro 1x4
      _t1_2 = _mm256_mul_pd(_t1_38, _t1_2);
      _mm256_storeu_pd(A + 101*fi377 + fi438 + 4, _t1_3);
      _mm256_storeu_pd(A + 101*fi377 + fi438 + 104, _t1_0);
      _mm256_storeu_pd(A + 101*fi377 + fi438 + 204, _t1_1);
      _mm256_storeu_pd(A + 101*fi377 + fi438 + 304, _t1_2);
    }
    _mm256_maskstore_pd(A + 101*fi377, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t0_0);
    _mm256_maskstore_pd(A + 101*fi377 + 1, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63, 0), _t0_2);
    _mm256_maskstore_pd(A + 101*fi377 + 301, _mm256_setr_epi64x(0, 0, (__int64)1 << 63, 0), _t0_5);
    _mm256_maskstore_pd(A + 101*fi377 + 101, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t0_6);
    _mm256_maskstore_pd(A + 101*fi377 + 102, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, 0, 0), _t0_8);
    _mm256_maskstore_pd(A + 101*fi377 + 302, _mm256_setr_epi64x(0, (__int64)1 << 63, 0, 0), _t0_10);
    _mm256_maskstore_pd(A + 101*fi377 + 202, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t0_11);
    _mm256_maskstore_pd(A + 101*fi377 + 203, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t0_12);
    _mm256_maskstore_pd(A + 101*fi377 + 303, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t0_13);

    for( int i72 = 0; i72 <= -fi377 + 88; i72+=4 ) {
      _t2_4 = _mm256_loadu_pd(A + 101*fi377 + 101*i72 + 404);
      _t2_5 = _mm256_maskload_pd(A + 101*fi377 + 101*i72 + 504, _mm256_setr_epi64x(0, (__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63));
      _t2_6 = _mm256_maskload_pd(A + 101*fi377 + 101*i72 + 604, _mm256_setr_epi64x(0, 0, (__int64)1 << 63, (__int64)1 << 63));
      _t2_7 = _mm256_maskload_pd(A + 101*fi377 + 101*i72 + 704, _mm256_setr_epi64x(0, 0, 0, (__int64)1 << 63));
      _t2_3 = _mm256_loadu_pd(A + 101*fi377 + i72 + 4);
      _t2_2 = _mm256_loadu_pd(A + 101*fi377 + i72 + 104);
      _t2_1 = _mm256_loadu_pd(A + 101*fi377 + i72 + 204);
      _t2_0 = _mm256_loadu_pd(A + 101*fi377 + i72 + 304);

      // 4x4 -> 4x4 - UpSymm
      _t2_16 = _t2_4;
      _t2_17 = _mm256_blend_pd(_mm256_shuffle_pd(_t2_4, _t2_5, 3), _t2_5, 12);
      _t2_18 = _mm256_permute2f128_pd(_mm256_shuffle_pd(_t2_4, _t2_5, 0), _t2_6, 49);
      _t2_19 = _mm256_permute2f128_pd(_mm256_shuffle_pd(_t2_4, _t2_5, 12), _mm256_shuffle_pd(_t2_6, _t2_7, 12), 49);

      // 4-BLAC: (4x4)^T
      _t2_20 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t2_3, _t2_2), _mm256_unpacklo_pd(_t2_1, _t2_0), 32);
      _t2_21 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t2_3, _t2_2), _mm256_unpackhi_pd(_t2_1, _t2_0), 32);
      _t2_22 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t2_3, _t2_2), _mm256_unpacklo_pd(_t2_1, _t2_0), 49);
      _t2_23 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t2_3, _t2_2), _mm256_unpackhi_pd(_t2_1, _t2_0), 49);

      // 4-BLAC: 4x4 * 4x4
      _t2_8 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t2_20, _t2_20, 32), _mm256_permute2f128_pd(_t2_20, _t2_20, 32), 0), _t2_3), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t2_20, _t2_20, 32), _mm256_permute2f128_pd(_t2_20, _t2_20, 32), 15), _t2_2)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t2_20, _t2_20, 49), _mm256_permute2f128_pd(_t2_20, _t2_20, 49), 0), _t2_1), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t2_20, _t2_20, 49), _mm256_permute2f128_pd(_t2_20, _t2_20, 49), 15), _t2_0)));
      _t2_9 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t2_21, _t2_21, 32), _mm256_permute2f128_pd(_t2_21, _t2_21, 32), 0), _t2_3), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t2_21, _t2_21, 32), _mm256_permute2f128_pd(_t2_21, _t2_21, 32), 15), _t2_2)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t2_21, _t2_21, 49), _mm256_permute2f128_pd(_t2_21, _t2_21, 49), 0), _t2_1), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t2_21, _t2_21, 49), _mm256_permute2f128_pd(_t2_21, _t2_21, 49), 15), _t2_0)));
      _t2_10 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t2_22, _t2_22, 32), _mm256_permute2f128_pd(_t2_22, _t2_22, 32), 0), _t2_3), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t2_22, _t2_22, 32), _mm256_permute2f128_pd(_t2_22, _t2_22, 32), 15), _t2_2)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t2_22, _t2_22, 49), _mm256_permute2f128_pd(_t2_22, _t2_22, 49), 0), _t2_1), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t2_22, _t2_22, 49), _mm256_permute2f128_pd(_t2_22, _t2_22, 49), 15), _t2_0)));
      _t2_11 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t2_23, _t2_23, 32), _mm256_permute2f128_pd(_t2_23, _t2_23, 32), 0), _t2_3), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t2_23, _t2_23, 32), _mm256_permute2f128_pd(_t2_23, _t2_23, 32), 15), _t2_2)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t2_23, _t2_23, 49), _mm256_permute2f128_pd(_t2_23, _t2_23, 49), 0), _t2_1), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t2_23, _t2_23, 49), _mm256_permute2f128_pd(_t2_23, _t2_23, 49), 15), _t2_0)));

      // 4-BLAC: 4x4 - 4x4
      _t2_12 = _mm256_sub_pd(_t2_16, _t2_8);
      _t2_13 = _mm256_sub_pd(_t2_17, _t2_9);
      _t2_14 = _mm256_sub_pd(_t2_18, _t2_10);
      _t2_15 = _mm256_sub_pd(_t2_19, _t2_11);

      // 4x4 -> 4x4 - UpSymm
      _t2_4 = _t2_12;
      _t2_5 = _t2_13;
      _t2_6 = _t2_14;
      _t2_7 = _t2_15;

      for( int j73 = 4*floord(i72 - 1, 4) + 8; j73 <= -fi377 + 95; j73+=4 ) {
        _t3_8 = _mm256_loadu_pd(A + 101*fi377 + 100*i72 + j73 + 404);
        _t3_9 = _mm256_loadu_pd(A + 101*fi377 + 100*i72 + j73 + 504);
        _t3_10 = _mm256_loadu_pd(A + 101*fi377 + 100*i72 + j73 + 604);
        _t3_11 = _mm256_loadu_pd(A + 101*fi377 + 100*i72 + j73 + 704);
        _t3_3 = _mm256_loadu_pd(A + 101*fi377 + j73 + 4);
        _t3_2 = _mm256_loadu_pd(A + 101*fi377 + j73 + 104);
        _t3_1 = _mm256_loadu_pd(A + 101*fi377 + j73 + 204);
        _t3_0 = _mm256_loadu_pd(A + 101*fi377 + j73 + 304);

        // 4-BLAC: (4x4)^T
        _t3_12 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t2_3, _t2_2), _mm256_unpacklo_pd(_t2_1, _t2_0), 32);
        _t3_13 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t2_3, _t2_2), _mm256_unpackhi_pd(_t2_1, _t2_0), 32);
        _t3_14 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t2_3, _t2_2), _mm256_unpacklo_pd(_t2_1, _t2_0), 49);
        _t3_15 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t2_3, _t2_2), _mm256_unpackhi_pd(_t2_1, _t2_0), 49);

        // 4-BLAC: 4x4 * 4x4
        _t3_4 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t3_12, _t3_12, 32), _mm256_permute2f128_pd(_t3_12, _t3_12, 32), 0), _t3_3), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t3_12, _t3_12, 32), _mm256_permute2f128_pd(_t3_12, _t3_12, 32), 15), _t3_2)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t3_12, _t3_12, 49), _mm256_permute2f128_pd(_t3_12, _t3_12, 49), 0), _t3_1), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t3_12, _t3_12, 49), _mm256_permute2f128_pd(_t3_12, _t3_12, 49), 15), _t3_0)));
        _t3_5 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t3_13, _t3_13, 32), _mm256_permute2f128_pd(_t3_13, _t3_13, 32), 0), _t3_3), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t3_13, _t3_13, 32), _mm256_permute2f128_pd(_t3_13, _t3_13, 32), 15), _t3_2)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t3_13, _t3_13, 49), _mm256_permute2f128_pd(_t3_13, _t3_13, 49), 0), _t3_1), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t3_13, _t3_13, 49), _mm256_permute2f128_pd(_t3_13, _t3_13, 49), 15), _t3_0)));
        _t3_6 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t3_14, _t3_14, 32), _mm256_permute2f128_pd(_t3_14, _t3_14, 32), 0), _t3_3), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t3_14, _t3_14, 32), _mm256_permute2f128_pd(_t3_14, _t3_14, 32), 15), _t3_2)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t3_14, _t3_14, 49), _mm256_permute2f128_pd(_t3_14, _t3_14, 49), 0), _t3_1), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t3_14, _t3_14, 49), _mm256_permute2f128_pd(_t3_14, _t3_14, 49), 15), _t3_0)));
        _t3_7 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t3_15, _t3_15, 32), _mm256_permute2f128_pd(_t3_15, _t3_15, 32), 0), _t3_3), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t3_15, _t3_15, 32), _mm256_permute2f128_pd(_t3_15, _t3_15, 32), 15), _t3_2)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t3_15, _t3_15, 49), _mm256_permute2f128_pd(_t3_15, _t3_15, 49), 0), _t3_1), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t3_15, _t3_15, 49), _mm256_permute2f128_pd(_t3_15, _t3_15, 49), 15), _t3_0)));

        // 4-BLAC: 4x4 - 4x4
        _t3_8 = _mm256_sub_pd(_t3_8, _t3_4);
        _t3_9 = _mm256_sub_pd(_t3_9, _t3_5);
        _t3_10 = _mm256_sub_pd(_t3_10, _t3_6);
        _t3_11 = _mm256_sub_pd(_t3_11, _t3_7);
        _mm256_storeu_pd(A + 101*fi377 + 100*i72 + j73 + 404, _t3_8);
        _mm256_storeu_pd(A + 101*fi377 + 100*i72 + j73 + 504, _t3_9);
        _mm256_storeu_pd(A + 101*fi377 + 100*i72 + j73 + 604, _t3_10);
        _mm256_storeu_pd(A + 101*fi377 + 100*i72 + j73 + 704, _t3_11);
      }
      _mm256_storeu_pd(A + 101*fi377 + 101*i72 + 404, _t2_4);
      _mm256_maskstore_pd(A + 101*fi377 + 101*i72 + 504, _mm256_setr_epi64x(0, (__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63), _t2_5);
      _mm256_maskstore_pd(A + 101*fi377 + 101*i72 + 604, _mm256_setr_epi64x(0, 0, (__int64)1 << 63, (__int64)1 << 63), _t2_6);
      _mm256_maskstore_pd(A + 101*fi377 + 101*i72 + 704, _mm256_setr_epi64x(0, 0, 0, (__int64)1 << 63), _t2_7);
    }
    _t4_4 = _mm256_loadu_pd(A + 9696);
    _t4_5 = _mm256_maskload_pd(A + 9796, _mm256_setr_epi64x(0, (__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63));
    _t4_6 = _mm256_maskload_pd(A + 9896, _mm256_setr_epi64x(0, 0, (__int64)1 << 63, (__int64)1 << 63));
    _t4_7 = _mm256_maskload_pd(A + 9996, _mm256_setr_epi64x(0, 0, 0, (__int64)1 << 63));
    _t4_3 = _mm256_loadu_pd(A + 100*fi377 + 96);
    _t4_2 = _mm256_loadu_pd(A + 100*fi377 + 196);
    _t4_1 = _mm256_loadu_pd(A + 100*fi377 + 296);
    _t4_0 = _mm256_loadu_pd(A + 100*fi377 + 396);

    // 4x4 -> 4x4 - UpSymm
    _t4_16 = _t4_4;
    _t4_17 = _mm256_blend_pd(_mm256_shuffle_pd(_t4_4, _t4_5, 3), _t4_5, 12);
    _t4_18 = _mm256_permute2f128_pd(_mm256_shuffle_pd(_t4_4, _t4_5, 0), _t4_6, 49);
    _t4_19 = _mm256_permute2f128_pd(_mm256_shuffle_pd(_t4_4, _t4_5, 12), _mm256_shuffle_pd(_t4_6, _t4_7, 12), 49);

    // 4-BLAC: (4x4)^T
    _t4_20 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t4_3, _t4_2), _mm256_unpacklo_pd(_t4_1, _t4_0), 32);
    _t4_21 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t4_3, _t4_2), _mm256_unpackhi_pd(_t4_1, _t4_0), 32);
    _t4_22 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t4_3, _t4_2), _mm256_unpacklo_pd(_t4_1, _t4_0), 49);
    _t4_23 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t4_3, _t4_2), _mm256_unpackhi_pd(_t4_1, _t4_0), 49);

    // 4-BLAC: 4x4 * 4x4
    _t4_8 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t4_20, _t4_20, 32), _mm256_permute2f128_pd(_t4_20, _t4_20, 32), 0), _t4_3), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t4_20, _t4_20, 32), _mm256_permute2f128_pd(_t4_20, _t4_20, 32), 15), _t4_2)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t4_20, _t4_20, 49), _mm256_permute2f128_pd(_t4_20, _t4_20, 49), 0), _t4_1), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t4_20, _t4_20, 49), _mm256_permute2f128_pd(_t4_20, _t4_20, 49), 15), _t4_0)));
    _t4_9 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t4_21, _t4_21, 32), _mm256_permute2f128_pd(_t4_21, _t4_21, 32), 0), _t4_3), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t4_21, _t4_21, 32), _mm256_permute2f128_pd(_t4_21, _t4_21, 32), 15), _t4_2)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t4_21, _t4_21, 49), _mm256_permute2f128_pd(_t4_21, _t4_21, 49), 0), _t4_1), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t4_21, _t4_21, 49), _mm256_permute2f128_pd(_t4_21, _t4_21, 49), 15), _t4_0)));
    _t4_10 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t4_22, _t4_22, 32), _mm256_permute2f128_pd(_t4_22, _t4_22, 32), 0), _t4_3), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t4_22, _t4_22, 32), _mm256_permute2f128_pd(_t4_22, _t4_22, 32), 15), _t4_2)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t4_22, _t4_22, 49), _mm256_permute2f128_pd(_t4_22, _t4_22, 49), 0), _t4_1), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t4_22, _t4_22, 49), _mm256_permute2f128_pd(_t4_22, _t4_22, 49), 15), _t4_0)));
    _t4_11 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t4_23, _t4_23, 32), _mm256_permute2f128_pd(_t4_23, _t4_23, 32), 0), _t4_3), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t4_23, _t4_23, 32), _mm256_permute2f128_pd(_t4_23, _t4_23, 32), 15), _t4_2)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t4_23, _t4_23, 49), _mm256_permute2f128_pd(_t4_23, _t4_23, 49), 0), _t4_1), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t4_23, _t4_23, 49), _mm256_permute2f128_pd(_t4_23, _t4_23, 49), 15), _t4_0)));

    // 4-BLAC: 4x4 - 4x4
    _t4_12 = _mm256_sub_pd(_t4_16, _t4_8);
    _t4_13 = _mm256_sub_pd(_t4_17, _t4_9);
    _t4_14 = _mm256_sub_pd(_t4_18, _t4_10);
    _t4_15 = _mm256_sub_pd(_t4_19, _t4_11);

    // 4x4 -> 4x4 - UpSymm
    _t4_4 = _t4_12;
    _t4_5 = _t4_13;
    _t4_6 = _t4_14;
    _t4_7 = _t4_15;
    _mm256_storeu_pd(A + 9696, _t4_4);
    _mm256_maskstore_pd(A + 9796, _mm256_setr_epi64x(0, (__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63), _t4_5);
    _mm256_maskstore_pd(A + 9896, _mm256_setr_epi64x(0, 0, (__int64)1 << 63, (__int64)1 << 63), _t4_6);
    _mm256_maskstore_pd(A + 9996, _mm256_setr_epi64x(0, 0, 0, (__int64)1 << 63), _t4_7);
  }

  _t5_0 = _mm256_maskload_pd(A + 9292, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0));
  _t5_2 = _mm256_maskload_pd(A + 9293, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63, 0));
  _t5_3 = _mm256_maskload_pd(A + 9393, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63, 0));
  _t5_4 = _mm256_maskload_pd(A + 9493, _mm256_setr_epi64x(0, (__int64)1 << 63, (__int64)1 << 63, 0));
  _t5_5 = _mm256_maskload_pd(A + 9593, _mm256_setr_epi64x(0, 0, (__int64)1 << 63, 0));
  _t5_37 = _mm256_loadu_pd(A + 9296);
  _t5_16 = _mm256_loadu_pd(A + 9396);
  _t5_17 = _mm256_loadu_pd(A + 9496);
  _t5_18 = _mm256_loadu_pd(A + 9596);
  _t5_19 = _mm256_loadu_pd(A + 9696);
  _t5_20 = _mm256_maskload_pd(A + 9796, _mm256_setr_epi64x(0, (__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63));
  _t5_21 = _mm256_maskload_pd(A + 9896, _mm256_setr_epi64x(0, 0, (__int64)1 << 63, (__int64)1 << 63));
  _t5_22 = _mm256_maskload_pd(A + 9996, _mm256_setr_epi64x(0, 0, 0, (__int64)1 << 63));

  // 1x1 -> 1x4
  _t5_47 = _t5_0;

  // 4-BLAC: sqrt(1x4)
  _t5_48 = _mm256_sqrt_pd(_t5_47);
  _t5_0 = _t5_48;

  // Constant 1x1 -> 1x4
  _t5_49 = _mm256_set_pd(0, 0, 0, 1);

  // 1x1 -> 1x4
  _t5_50 = _t5_0;

  // 4-BLAC: 1x4 / 1x4
  _t5_51 = _mm256_div_pd(_t5_49, _t5_50);
  _t5_1 = _t5_51;

  // 1x1 -> 1x4
  _t5_52 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_1, _t5_1, 32), _mm256_permute2f128_pd(_t5_1, _t5_1, 32), 0);

  // 1x3 -> 1x4
  _t5_53 = _t5_2;

  // 4-BLAC: 1x4 Kro 1x4
  _t5_54 = _mm256_mul_pd(_t5_52, _t5_53);
  _t5_2 = _t5_54;

  // 3x3 -> 4x4 - UpSymm
  _t5_55 = _t5_3;
  _t5_56 = _mm256_blend_pd(_mm256_shuffle_pd(_t5_3, _t5_4, 3), _t5_4, 12);
  _t5_57 = _mm256_permute2f128_pd(_mm256_shuffle_pd(_t5_3, _t5_4, 0), _t5_5, 49);
  _t5_58 = _mm256_setzero_pd();

  // 1x3 -> 1x4
  _t5_59 = _t5_2;

  // 4-BLAC: (1x4)^T
  _t5_60 = _t5_59;

  // 1x3 -> 1x4
  _t5_61 = _t5_2;

  // 4-BLAC: 4x1 * 1x4
  _t5_62 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_60, _t5_60, 32), _mm256_permute2f128_pd(_t5_60, _t5_60, 32), 0), _t5_61);
  _t5_63 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_60, _t5_60, 32), _mm256_permute2f128_pd(_t5_60, _t5_60, 32), 15), _t5_61);
  _t5_64 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_60, _t5_60, 49), _mm256_permute2f128_pd(_t5_60, _t5_60, 49), 0), _t5_61);
  _t5_65 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_60, _t5_60, 49), _mm256_permute2f128_pd(_t5_60, _t5_60, 49), 15), _t5_61);

  // 4-BLAC: 4x4 - 4x4
  _t5_66 = _mm256_sub_pd(_t5_55, _t5_62);
  _t5_67 = _mm256_sub_pd(_t5_56, _t5_63);
  _t5_68 = _mm256_sub_pd(_t5_57, _t5_64);
  _t5_69 = _mm256_sub_pd(_t5_58, _t5_65);

  // 4x4 -> 3x3 - UpSymm
  _t5_3 = _t5_66;
  _t5_4 = _t5_67;
  _t5_5 = _t5_68;

  // 1x1 -> 1x4
  _t5_70 = _mm256_blend_pd(_mm256_setzero_pd(), _t5_3, 1);

  // 4-BLAC: sqrt(1x4)
  _t5_71 = _mm256_sqrt_pd(_t5_70);
  _t5_6 = _t5_71;

  // Constant 1x1 -> 1x4
  _t5_72 = _mm256_set_pd(0, 0, 0, 1);

  // 1x1 -> 1x4
  _t5_73 = _t5_6;

  // 4-BLAC: 1x4 / 1x4
  _t5_74 = _mm256_div_pd(_t5_72, _t5_73);
  _t5_7 = _t5_74;

  // 1x1 -> 1x4
  _t5_75 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_7, _t5_7, 32), _mm256_permute2f128_pd(_t5_7, _t5_7, 32), 0);

  // 1x2 -> 1x4
  _t5_76 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t5_3, 6), _mm256_permute2f128_pd(_t5_3, _t5_3, 129), 5);

  // 4-BLAC: 1x4 Kro 1x4
  _t5_77 = _mm256_mul_pd(_t5_75, _t5_76);
  _t5_8 = _t5_77;

  // 2x2 -> 4x4 - UpSymm
  _t5_78 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t5_4, 6), _mm256_permute2f128_pd(_t5_4, _t5_4, 129), 5);
  _t5_79 = _mm256_shuffle_pd(_mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t5_4, 6), _mm256_permute2f128_pd(_t5_4, _t5_4, 129), 5), _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t5_5, 4), _mm256_permute2f128_pd(_t5_5, _t5_5, 129), 5), 3);
  _t5_80 = _mm256_setzero_pd();
  _t5_81 = _mm256_setzero_pd();

  // 1x2 -> 1x4
  _t5_82 = _t5_8;

  // 4-BLAC: (1x4)^T
  _t5_83 = _t5_82;

  // 1x2 -> 1x4
  _t5_84 = _t5_8;

  // 4-BLAC: 4x1 * 1x4
  _t5_85 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_83, _t5_83, 32), _mm256_permute2f128_pd(_t5_83, _t5_83, 32), 0), _t5_84);
  _t5_86 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_83, _t5_83, 32), _mm256_permute2f128_pd(_t5_83, _t5_83, 32), 15), _t5_84);
  _t5_87 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_83, _t5_83, 49), _mm256_permute2f128_pd(_t5_83, _t5_83, 49), 0), _t5_84);
  _t5_88 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_83, _t5_83, 49), _mm256_permute2f128_pd(_t5_83, _t5_83, 49), 15), _t5_84);

  // 4-BLAC: 4x4 - 4x4
  _t5_89 = _mm256_sub_pd(_t5_78, _t5_85);
  _t5_90 = _mm256_sub_pd(_t5_79, _t5_86);
  _t5_91 = _mm256_sub_pd(_t5_80, _t5_87);
  _t5_92 = _mm256_sub_pd(_t5_81, _t5_88);

  // 4x4 -> 2x2 - UpSymm
  _t5_9 = _t5_89;
  _t5_10 = _t5_90;

  // 1x1 -> 1x4
  _t5_93 = _mm256_blend_pd(_mm256_setzero_pd(), _t5_9, 1);

  // 4-BLAC: sqrt(1x4)
  _t5_94 = _mm256_sqrt_pd(_t5_93);
  _t5_11 = _t5_94;

  // 1x1 -> 1x4
  _t5_95 = _mm256_unpackhi_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t5_9, 2), _mm256_setzero_pd());

  // 1x1 -> 1x4
  _t5_96 = _t5_11;

  // 4-BLAC: 1x4 / 1x4
  _t5_97 = _mm256_div_pd(_t5_95, _t5_96);
  _t5_12 = _t5_97;

  // 1x1 -> 1x4
  _t5_98 = _mm256_unpackhi_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t5_10, 2), _mm256_setzero_pd());

  // 1x1 -> 1x4
  _t5_99 = _t5_12;

  // 4-BLAC: (4x1)^T
  _t5_100 = _t5_99;

  // 1x1 -> 1x4
  _t5_101 = _t5_12;

  // 4-BLAC: 1x4 Kro 1x4
  _t5_102 = _mm256_mul_pd(_t5_100, _t5_101);

  // 4-BLAC: 1x4 - 1x4
  _t5_103 = _mm256_sub_pd(_t5_98, _t5_102);
  _t5_13 = _t5_103;

  // 1x1 -> 1x4
  _t5_104 = _t5_13;

  // 4-BLAC: sqrt(1x4)
  _t5_105 = _mm256_sqrt_pd(_t5_104);
  _t5_13 = _t5_105;

  // Constant 1x1 -> 1x4
  _t5_106 = _mm256_set_pd(0, 0, 0, 1);

  // 1x1 -> 1x4
  _t5_107 = _t5_11;

  // 4-BLAC: 1x4 / 1x4
  _t5_108 = _mm256_div_pd(_t5_106, _t5_107);
  _t5_14 = _t5_108;

  // Constant 1x1 -> 1x4
  _t5_109 = _mm256_set_pd(0, 0, 0, 1);

  // 1x1 -> 1x4
  _t5_110 = _t5_13;

  // 4-BLAC: 1x4 / 1x4
  _t5_111 = _mm256_div_pd(_t5_109, _t5_110);
  _t5_15 = _t5_111;

  // 1x1 -> 1x4
  _t5_112 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_1, _t5_1, 32), _mm256_permute2f128_pd(_t5_1, _t5_1, 32), 0);

  // 4-BLAC: 1x4 Kro 1x4
  _t5_37 = _mm256_mul_pd(_t5_112, _t5_37);

  // 3x4 -> 4x4
  _t5_113 = _t5_16;
  _t5_114 = _t5_17;
  _t5_115 = _t5_18;
  _t5_116 = _mm256_setzero_pd();

  // 1x3 -> 1x4
  _t5_117 = _t5_2;

  // 4-BLAC: (1x4)^T
  _t5_118 = _t5_117;

  // 4-BLAC: 4x1 * 1x4
  _t5_119 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_118, _t5_118, 32), _mm256_permute2f128_pd(_t5_118, _t5_118, 32), 0), _t5_37);
  _t5_120 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_118, _t5_118, 32), _mm256_permute2f128_pd(_t5_118, _t5_118, 32), 15), _t5_37);
  _t5_121 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_118, _t5_118, 49), _mm256_permute2f128_pd(_t5_118, _t5_118, 49), 0), _t5_37);
  _t5_122 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_118, _t5_118, 49), _mm256_permute2f128_pd(_t5_118, _t5_118, 49), 15), _t5_37);

  // 4-BLAC: 4x4 - 4x4
  _t5_123 = _mm256_sub_pd(_t5_113, _t5_119);
  _t5_124 = _mm256_sub_pd(_t5_114, _t5_120);
  _t5_125 = _mm256_sub_pd(_t5_115, _t5_121);
  _t5_126 = _mm256_sub_pd(_t5_116, _t5_122);
  _t5_16 = _t5_123;
  _t5_17 = _t5_124;
  _t5_18 = _t5_125;

  // 1x1 -> 1x4
  _t5_127 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_7, _t5_7, 32), _mm256_permute2f128_pd(_t5_7, _t5_7, 32), 0);

  // 4-BLAC: 1x4 Kro 1x4
  _t5_16 = _mm256_mul_pd(_t5_127, _t5_16);

  // 2x4 -> 4x4
  _t5_128 = _t5_17;
  _t5_129 = _t5_18;
  _t5_130 = _mm256_setzero_pd();
  _t5_131 = _mm256_setzero_pd();

  // 1x2 -> 1x4
  _t5_132 = _t5_8;

  // 4-BLAC: (1x4)^T
  _t5_133 = _t5_132;

  // 4-BLAC: 4x1 * 1x4
  _t5_134 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_133, _t5_133, 32), _mm256_permute2f128_pd(_t5_133, _t5_133, 32), 0), _t5_16);
  _t5_135 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_133, _t5_133, 32), _mm256_permute2f128_pd(_t5_133, _t5_133, 32), 15), _t5_16);
  _t5_136 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_133, _t5_133, 49), _mm256_permute2f128_pd(_t5_133, _t5_133, 49), 0), _t5_16);
  _t5_137 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_133, _t5_133, 49), _mm256_permute2f128_pd(_t5_133, _t5_133, 49), 15), _t5_16);

  // 4-BLAC: 4x4 - 4x4
  _t5_138 = _mm256_sub_pd(_t5_128, _t5_134);
  _t5_139 = _mm256_sub_pd(_t5_129, _t5_135);
  _t5_140 = _mm256_sub_pd(_t5_130, _t5_136);
  _t5_141 = _mm256_sub_pd(_t5_131, _t5_137);
  _t5_17 = _t5_138;
  _t5_18 = _t5_139;

  // 1x1 -> 1x4
  _t5_142 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_14, _t5_14, 32), _mm256_permute2f128_pd(_t5_14, _t5_14, 32), 0);

  // 4-BLAC: 1x4 Kro 1x4
  _t5_17 = _mm256_mul_pd(_t5_142, _t5_17);

  // 1x1 -> 1x4
  _t5_143 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_12, _t5_12, 32), _mm256_permute2f128_pd(_t5_12, _t5_12, 32), 0);

  // 4-BLAC: (4x1)^T
  _t5_144 = _t5_143;

  // 4-BLAC: 1x4 Kro 1x4
  _t5_38 = _mm256_mul_pd(_t5_144, _t5_17);

  // 4-BLAC: 1x4 - 1x4
  _t5_18 = _mm256_sub_pd(_t5_18, _t5_38);

  // 1x1 -> 1x4
  _t5_145 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_15, _t5_15, 32), _mm256_permute2f128_pd(_t5_15, _t5_15, 32), 0);

  // 4-BLAC: 1x4 Kro 1x4
  _t5_18 = _mm256_mul_pd(_t5_145, _t5_18);

  // 4x4 -> 4x4 - UpSymm
  _t5_146 = _t5_19;
  _t5_147 = _mm256_blend_pd(_mm256_shuffle_pd(_t5_19, _t5_20, 3), _t5_20, 12);
  _t5_148 = _mm256_permute2f128_pd(_mm256_shuffle_pd(_t5_19, _t5_20, 0), _t5_21, 49);
  _t5_149 = _mm256_permute2f128_pd(_mm256_shuffle_pd(_t5_19, _t5_20, 12), _mm256_shuffle_pd(_t5_21, _t5_22, 12), 49);

  // 4-BLAC: (4x4)^T
  _t5_209 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t5_37, _t5_16), _mm256_unpacklo_pd(_t5_17, _t5_18), 32);
  _t5_210 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t5_37, _t5_16), _mm256_unpackhi_pd(_t5_17, _t5_18), 32);
  _t5_211 = _mm256_permute2f128_pd(_mm256_unpacklo_pd(_t5_37, _t5_16), _mm256_unpacklo_pd(_t5_17, _t5_18), 49);
  _t5_212 = _mm256_permute2f128_pd(_mm256_unpackhi_pd(_t5_37, _t5_16), _mm256_unpackhi_pd(_t5_17, _t5_18), 49);

  // 4-BLAC: 4x4 * 4x4
  _t5_39 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_209, _t5_209, 32), _mm256_permute2f128_pd(_t5_209, _t5_209, 32), 0), _t5_37), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_209, _t5_209, 32), _mm256_permute2f128_pd(_t5_209, _t5_209, 32), 15), _t5_16)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_209, _t5_209, 49), _mm256_permute2f128_pd(_t5_209, _t5_209, 49), 0), _t5_17), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_209, _t5_209, 49), _mm256_permute2f128_pd(_t5_209, _t5_209, 49), 15), _t5_18)));
  _t5_40 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_210, _t5_210, 32), _mm256_permute2f128_pd(_t5_210, _t5_210, 32), 0), _t5_37), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_210, _t5_210, 32), _mm256_permute2f128_pd(_t5_210, _t5_210, 32), 15), _t5_16)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_210, _t5_210, 49), _mm256_permute2f128_pd(_t5_210, _t5_210, 49), 0), _t5_17), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_210, _t5_210, 49), _mm256_permute2f128_pd(_t5_210, _t5_210, 49), 15), _t5_18)));
  _t5_41 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_211, _t5_211, 32), _mm256_permute2f128_pd(_t5_211, _t5_211, 32), 0), _t5_37), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_211, _t5_211, 32), _mm256_permute2f128_pd(_t5_211, _t5_211, 32), 15), _t5_16)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_211, _t5_211, 49), _mm256_permute2f128_pd(_t5_211, _t5_211, 49), 0), _t5_17), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_211, _t5_211, 49), _mm256_permute2f128_pd(_t5_211, _t5_211, 49), 15), _t5_18)));
  _t5_42 = _mm256_add_pd(_mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_212, _t5_212, 32), _mm256_permute2f128_pd(_t5_212, _t5_212, 32), 0), _t5_37), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_212, _t5_212, 32), _mm256_permute2f128_pd(_t5_212, _t5_212, 32), 15), _t5_16)), _mm256_add_pd(_mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_212, _t5_212, 49), _mm256_permute2f128_pd(_t5_212, _t5_212, 49), 0), _t5_17), _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_212, _t5_212, 49), _mm256_permute2f128_pd(_t5_212, _t5_212, 49), 15), _t5_18)));

  // 4-BLAC: 4x4 - 4x4
  _t5_43 = _mm256_sub_pd(_t5_146, _t5_39);
  _t5_44 = _mm256_sub_pd(_t5_147, _t5_40);
  _t5_45 = _mm256_sub_pd(_t5_148, _t5_41);
  _t5_46 = _mm256_sub_pd(_t5_149, _t5_42);

  // 4x4 -> 4x4 - UpSymm
  _t5_19 = _t5_43;
  _t5_20 = _t5_44;
  _t5_21 = _t5_45;
  _t5_22 = _t5_46;

  // 1x1 -> 1x4
  _t5_150 = _mm256_blend_pd(_mm256_setzero_pd(), _t5_19, 1);

  // 4-BLAC: sqrt(1x4)
  _t5_151 = _mm256_sqrt_pd(_t5_150);
  _t5_23 = _t5_151;

  // Constant 1x1 -> 1x4
  _t5_152 = _mm256_set_pd(0, 0, 0, 1);

  // 1x1 -> 1x4
  _t5_153 = _t5_23;

  // 4-BLAC: 1x4 / 1x4
  _t5_154 = _mm256_div_pd(_t5_152, _t5_153);
  _t5_24 = _t5_154;

  // 1x1 -> 1x4
  _t5_155 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_24, _t5_24, 32), _mm256_permute2f128_pd(_t5_24, _t5_24, 32), 0);

  // 1x3 -> 1x4
  _t5_156 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t5_19, 14), _mm256_permute2f128_pd(_t5_19, _t5_19, 129), 5);

  // 4-BLAC: 1x4 Kro 1x4
  _t5_157 = _mm256_mul_pd(_t5_155, _t5_156);
  _t5_25 = _t5_157;

  // 3x3 -> 4x4 - UpSymm
  _t5_158 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t5_20, 14), _mm256_permute2f128_pd(_t5_20, _t5_20, 129), 5);
  _t5_159 = _mm256_blend_pd(_mm256_shuffle_pd(_mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t5_20, 14), _mm256_permute2f128_pd(_t5_20, _t5_20, 129), 5), _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t5_21, 12), _mm256_permute2f128_pd(_t5_21, _t5_21, 129), 5), 3), _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t5_21, 12), _mm256_permute2f128_pd(_t5_21, _t5_21, 129), 5), 12);
  _t5_160 = _mm256_permute2f128_pd(_mm256_shuffle_pd(_mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t5_20, 14), _mm256_permute2f128_pd(_t5_20, _t5_20, 129), 5), _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t5_21, 12), _mm256_permute2f128_pd(_t5_21, _t5_21, 129), 5), 0), _mm256_unpackhi_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t5_22, 8), _mm256_setzero_pd()), 49);
  _t5_161 = _mm256_setzero_pd();

  // 1x3 -> 1x4
  _t5_162 = _t5_25;

  // 4-BLAC: (1x4)^T
  _t5_163 = _t5_162;

  // 1x3 -> 1x4
  _t5_164 = _t5_25;

  // 4-BLAC: 4x1 * 1x4
  _t5_165 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_163, _t5_163, 32), _mm256_permute2f128_pd(_t5_163, _t5_163, 32), 0), _t5_164);
  _t5_166 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_163, _t5_163, 32), _mm256_permute2f128_pd(_t5_163, _t5_163, 32), 15), _t5_164);
  _t5_167 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_163, _t5_163, 49), _mm256_permute2f128_pd(_t5_163, _t5_163, 49), 0), _t5_164);
  _t5_168 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_163, _t5_163, 49), _mm256_permute2f128_pd(_t5_163, _t5_163, 49), 15), _t5_164);

  // 4-BLAC: 4x4 - 4x4
  _t5_169 = _mm256_sub_pd(_t5_158, _t5_165);
  _t5_170 = _mm256_sub_pd(_t5_159, _t5_166);
  _t5_171 = _mm256_sub_pd(_t5_160, _t5_167);
  _t5_172 = _mm256_sub_pd(_t5_161, _t5_168);

  // 4x4 -> 3x3 - UpSymm
  _t5_26 = _t5_169;
  _t5_27 = _t5_170;
  _t5_28 = _t5_171;

  // 1x1 -> 1x4
  _t5_173 = _mm256_blend_pd(_mm256_setzero_pd(), _t5_26, 1);

  // 4-BLAC: sqrt(1x4)
  _t5_174 = _mm256_sqrt_pd(_t5_173);
  _t5_29 = _t5_174;

  // Constant 1x1 -> 1x4
  _t5_175 = _mm256_set_pd(0, 0, 0, 1);

  // 1x1 -> 1x4
  _t5_176 = _t5_29;

  // 4-BLAC: 1x4 / 1x4
  _t5_177 = _mm256_div_pd(_t5_175, _t5_176);
  _t5_30 = _t5_177;

  // 1x1 -> 1x4
  _t5_178 = _mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_30, _t5_30, 32), _mm256_permute2f128_pd(_t5_30, _t5_30, 32), 0);

  // 1x2 -> 1x4
  _t5_179 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t5_26, 6), _mm256_permute2f128_pd(_t5_26, _t5_26, 129), 5);

  // 4-BLAC: 1x4 Kro 1x4
  _t5_180 = _mm256_mul_pd(_t5_178, _t5_179);
  _t5_31 = _t5_180;

  // 2x2 -> 4x4 - UpSymm
  _t5_181 = _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t5_27, 6), _mm256_permute2f128_pd(_t5_27, _t5_27, 129), 5);
  _t5_182 = _mm256_shuffle_pd(_mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t5_27, 6), _mm256_permute2f128_pd(_t5_27, _t5_27, 129), 5), _mm256_shuffle_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t5_28, 4), _mm256_permute2f128_pd(_t5_28, _t5_28, 129), 5), 3);
  _t5_183 = _mm256_setzero_pd();
  _t5_184 = _mm256_setzero_pd();

  // 1x2 -> 1x4
  _t5_185 = _t5_31;

  // 4-BLAC: (1x4)^T
  _t5_186 = _t5_185;

  // 1x2 -> 1x4
  _t5_187 = _t5_31;

  // 4-BLAC: 4x1 * 1x4
  _t5_188 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_186, _t5_186, 32), _mm256_permute2f128_pd(_t5_186, _t5_186, 32), 0), _t5_187);
  _t5_189 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_186, _t5_186, 32), _mm256_permute2f128_pd(_t5_186, _t5_186, 32), 15), _t5_187);
  _t5_190 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_186, _t5_186, 49), _mm256_permute2f128_pd(_t5_186, _t5_186, 49), 0), _t5_187);
  _t5_191 = _mm256_mul_pd(_mm256_shuffle_pd(_mm256_permute2f128_pd(_t5_186, _t5_186, 49), _mm256_permute2f128_pd(_t5_186, _t5_186, 49), 15), _t5_187);

  // 4-BLAC: 4x4 - 4x4
  _t5_192 = _mm256_sub_pd(_t5_181, _t5_188);
  _t5_193 = _mm256_sub_pd(_t5_182, _t5_189);
  _t5_194 = _mm256_sub_pd(_t5_183, _t5_190);
  _t5_195 = _mm256_sub_pd(_t5_184, _t5_191);

  // 4x4 -> 2x2 - UpSymm
  _t5_32 = _t5_192;
  _t5_33 = _t5_193;

  // 1x1 -> 1x4
  _t5_196 = _mm256_blend_pd(_mm256_setzero_pd(), _t5_32, 1);

  // 4-BLAC: sqrt(1x4)
  _t5_197 = _mm256_sqrt_pd(_t5_196);
  _t5_34 = _t5_197;

  // 1x1 -> 1x4
  _t5_198 = _mm256_unpackhi_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t5_32, 2), _mm256_setzero_pd());

  // 1x1 -> 1x4
  _t5_199 = _t5_34;

  // 4-BLAC: 1x4 / 1x4
  _t5_200 = _mm256_div_pd(_t5_198, _t5_199);
  _t5_35 = _t5_200;

  // 1x1 -> 1x4
  _t5_201 = _mm256_unpackhi_pd(_mm256_blend_pd(_mm256_setzero_pd(), _t5_33, 2), _mm256_setzero_pd());

  // 1x1 -> 1x4
  _t5_202 = _t5_35;

  // 4-BLAC: (4x1)^T
  _t5_203 = _t5_202;

  // 1x1 -> 1x4
  _t5_204 = _t5_35;

  // 4-BLAC: 1x4 Kro 1x4
  _t5_205 = _mm256_mul_pd(_t5_203, _t5_204);

  // 4-BLAC: 1x4 - 1x4
  _t5_206 = _mm256_sub_pd(_t5_201, _t5_205);
  _t5_36 = _t5_206;

  // 1x1 -> 1x4
  _t5_207 = _t5_36;

  // 4-BLAC: sqrt(1x4)
  _t5_208 = _mm256_sqrt_pd(_t5_207);
  _t5_36 = _t5_208;

  _mm256_maskstore_pd(A + 9292, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t5_0);
  _mm256_maskstore_pd(A + 9293, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63, 0), _t5_2);
  _mm256_maskstore_pd(A + 9393, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63, 0), _t5_3);
  _mm256_maskstore_pd(A + 9493, _mm256_setr_epi64x(0, (__int64)1 << 63, (__int64)1 << 63, 0), _t5_4);
  _mm256_maskstore_pd(A + 9593, _mm256_setr_epi64x(0, 0, (__int64)1 << 63, 0), _t5_5);
  _mm256_maskstore_pd(A + 9393, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t5_6);
  _mm256_maskstore_pd(A + 9394, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, 0, 0), _t5_8);
  _mm256_maskstore_pd(A + 9494, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, 0, 0), _t5_9);
  _mm256_maskstore_pd(A + 9594, _mm256_setr_epi64x(0, (__int64)1 << 63, 0, 0), _t5_10);
  _mm256_maskstore_pd(A + 9494, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t5_11);
  _mm256_maskstore_pd(A + 9495, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t5_12);
  _mm256_maskstore_pd(A + 9595, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t5_13);
  _mm256_storeu_pd(A + 9296, _t5_37);
  _mm256_storeu_pd(A + 9396, _t5_16);
  _mm256_storeu_pd(A + 9496, _t5_17);
  _mm256_storeu_pd(A + 9596, _t5_18);
  _mm256_storeu_pd(A + 9696, _t5_19);
  _mm256_maskstore_pd(A + 9796, _mm256_setr_epi64x(0, (__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63), _t5_20);
  _mm256_maskstore_pd(A + 9896, _mm256_setr_epi64x(0, 0, (__int64)1 << 63, (__int64)1 << 63), _t5_21);
  _mm256_maskstore_pd(A + 9996, _mm256_setr_epi64x(0, 0, 0, (__int64)1 << 63), _t5_22);
  _mm256_maskstore_pd(A + 9696, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t5_23);
  _mm256_maskstore_pd(A + 9697, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63, 0), _t5_25);
  _mm256_maskstore_pd(A + 9797, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, (__int64)1 << 63, 0), _t5_26);
  _mm256_maskstore_pd(A + 9897, _mm256_setr_epi64x(0, (__int64)1 << 63, (__int64)1 << 63, 0), _t5_27);
  _mm256_maskstore_pd(A + 9997, _mm256_setr_epi64x(0, 0, (__int64)1 << 63, 0), _t5_28);
  _mm256_maskstore_pd(A + 9797, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t5_29);
  _mm256_maskstore_pd(A + 9798, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, 0, 0), _t5_31);
  _mm256_maskstore_pd(A + 9898, _mm256_setr_epi64x((__int64)1 << 63, (__int64)1 << 63, 0, 0), _t5_32);
  _mm256_maskstore_pd(A + 9998, _mm256_setr_epi64x(0, (__int64)1 << 63, 0, 0), _t5_33);
  _mm256_maskstore_pd(A + 9898, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t5_34);
  _mm256_maskstore_pd(A + 9899, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t5_35);
  _mm256_maskstore_pd(A + 9999, _mm256_setr_epi64x((__int64)1 << 63, 0, 0, 0), _t5_36);

}
