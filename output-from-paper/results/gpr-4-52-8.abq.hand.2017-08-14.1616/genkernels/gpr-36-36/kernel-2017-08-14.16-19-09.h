/*
 * gpr_kernel.h
 *
Decl { {u'a': Matrix[a, (36, 1), GenMatAccess], u'x': Matrix[x, (36, 1), GenMatAccess], u'lp': Scalar[lp, (1, 1), GenMatAccess], u'f': Scalar[f, (1, 1), GenMatAccess], u'K': Symmetric[K, (36, 36), LSMatAccess], u't2': Matrix[t2, (36, 1), GenMatAccess], u'L': LowerTriangular[L, (36, 36), GenMatAccess], u't0': Matrix[t0, (36, 1), GenMatAccess], u't1': Matrix[t1, (36, 1), GenMatAccess], u'var': Scalar[var, (1, 1), GenMatAccess], u'L0': LowerTriangular[L0, (36, 36), GenMatAccess], u'v': Matrix[v, (36, 1), GenMatAccess], u'y': Matrix[y, (36, 1), GenMatAccess], u'X': SquaredMatrix[X, (36, 36), GenMatAccess], u'kx': Matrix[kx, (36, 1), GenMatAccess]} }
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ann: {'part_schemes': {'Assign_Mul_T_LowerTriangular_Matrix_Matrix_opt': {'m0': 'm04.ll', 'm2': 'm21.ll'}, 'Assign_Mul_LowerTriangular_Matrix_Matrix_opt': {'m0': 'm04.ll', 'm2': 'm21.ll'}, 'rdiv_ltn_ow_opt': {'m': 'm1.ll', 'n': 'n4.ll'}, 'Assign_Mul_LowerTriangular_T_LowerTriangular_Symmetric_opt': {'m0': 'm01.ll'}}, 'cl1ck_v': 0, 'variant_tag': 'Assign_Mul_LowerTriangular_Matrix_Matrix_opt_m04_m21_Assign_Mul_LowerTriangular_T_LowerTriangular_Symmetric_opt_m01_Assign_Mul_T_LowerTriangular_Matrix_Matrix_opt_m04_m21_rdiv_ltn_ow_opt_m1_n4'}

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Entry 0:
Eq: Tile( (1, 1), G(h(1, 36, 0), L[36,36],h(1, 36, 0)) ) = Sqrt( Tile( (1, 1), G(h(1, 36, 0), L[36,36],h(1, 36, 0)) ) )
Eq.ann: {}
Entry 1:
For_{fi18;1;35;1} ( Entry 0:
For_{fi43;0;fi18 - 2;1} ( Entry 0:
Eq: Tile( (1, 1), G(h(1, 36, fi18), L[36,36],h(1, 36, fi43)) ) = ( Tile( (1, 1), G(h(1, 36, fi18), L[36,36],h(1, 36, fi43)) ) Div Tile( (1, 1), G(h(1, 36, fi43), L[36,36],h(1, 36, fi43)) ) )
Eq.ann: {}
Entry 1:
Eq: Tile( (1, 1), G(h(1, 36, fi18), L[36,36],h(fi18 - fi43 - 1, 36, fi43 + 1)) ) = ( Tile( (1, 1), G(h(1, 36, fi18), L[36,36],h(fi18 - fi43 - 1, 36, fi43 + 1)) ) - ( Tile( (1, 1), G(h(1, 36, fi18), L[36,36],h(1, 36, fi43)) ) Kro T( Tile( (1, 1), G(h(fi18 - fi43 - 1, 36, fi43 + 1), L[36,36],h(1, 36, fi43)) ) ) ) )
Eq.ann: {}
 )Entry 1:
Eq: Tile( (1, 1), G(h(1, 36, fi18), L[36,36],h(1, 36, Max(0, fi18 - 1))) ) = ( Tile( (1, 1), G(h(1, 36, fi18), L[36,36],h(1, 36, Max(0, fi18 - 1))) ) Div Tile( (1, 1), G(h(1, 36, Max(0, fi18 - 1)), L[36,36],h(1, 36, Max(0, fi18 - 1))) ) )
Eq.ann: {}
Entry 2:
Eq: Tile( (1, 1), G(h(1, 36, fi18), L[36,36],h(1, 36, fi18)) ) = ( Tile( (1, 1), G(h(1, 36, fi18), K[36,36],h(1, 36, fi18)) ) - ( Tile( (1, 1), G(h(1, 36, fi18), L[36,36],h(fi18, 36, 0)) ) * T( Tile( (1, 1), G(h(1, 36, fi18), L[36,36],h(fi18, 36, 0)) ) ) ) )
Eq.ann: {}
Entry 3:
Eq: Tile( (1, 1), G(h(1, 36, fi18), L[36,36],h(1, 36, fi18)) ) = Sqrt( Tile( (1, 1), G(h(1, 36, fi18), L[36,36],h(1, 36, fi18)) ) )
Eq.ann: {}
 )Entry 2:
For_{fi75;0;34;1} ( Entry 0:
Eq: Tile( (1, 1), G(h(1, 36, fi75), t0[36,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 36, fi75), t0[36,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 36, fi75), L0[36,36],h(1, 36, fi75)) ) )
Eq.ann: {}
Entry 1:
Eq: Tile( (1, 1), G(h(-fi75 + 35, 36, fi75 + 1), t0[36,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(-fi75 + 35, 36, fi75 + 1), t0[36,1],h(1, 1, 0)) ) - ( Tile( (1, 1), G(h(-fi75 + 35, 36, fi75 + 1), L0[36,36],h(1, 36, fi75)) ) Kro Tile( (1, 1), G(h(1, 36, fi75), t0[36,1],h(1, 1, 0)) ) ) )
Eq.ann: {}
 )Entry 3:
Eq: Tile( (1, 1), G(h(1, 36, 35), t0[36,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 36, 35), t0[36,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 36, 35), L0[36,36],h(1, 36, 35)) ) )
Eq.ann: {}
Entry 4:
For_{fi104;0;34;1} ( Entry 0:
Eq: Tile( (1, 1), G(h(1, 36, -fi104 + 35), a[36,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 36, -fi104 + 35), a[36,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 36, -fi104 + 35), L0[36,36],h(1, 36, -fi104 + 35)) ) )
Eq.ann: {}
Entry 1:
Eq: Tile( (1, 1), G(h(-fi104 + 35, 36, 0), a[36,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(-fi104 + 35, 36, 0), a[36,1],h(1, 1, 0)) ) - ( T( Tile( (1, 1), G(h(1, 36, -fi104 + 35), L0[36,36],h(-fi104 + 35, 36, 0)) ) ) Kro Tile( (1, 1), G(h(1, 36, -fi104 + 35), a[36,1],h(1, 1, 0)) ) ) )
Eq.ann: {}
 )Entry 5:
Eq: Tile( (1, 1), G(h(1, 36, 0), a[36,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 36, 0), a[36,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 36, 0), L0[36,36],h(1, 36, 0)) ) )
Eq.ann: {}
Entry 6:
Eq: Tile( (1, 1), kx[36,1] ) = ( Tile( (1, 1), X[36,36] ) * Tile( (1, 1), x[36,1] ) )
Eq.ann: {}
Entry 7:
Eq: Tile( (1, 1), f[1,1] ) = ( T( Tile( (1, 1), kx[36,1] ) ) * Tile( (1, 1), y[36,1] ) )
Eq.ann: {}
Entry 8:
For_{fi133;0;34;1} ( Entry 0:
Eq: Tile( (1, 1), G(h(1, 36, fi133), v[36,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 36, fi133), v[36,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 36, fi133), L0[36,36],h(1, 36, fi133)) ) )
Eq.ann: {}
Entry 1:
Eq: Tile( (1, 1), G(h(-fi133 + 35, 36, fi133 + 1), v[36,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(-fi133 + 35, 36, fi133 + 1), v[36,1],h(1, 1, 0)) ) - ( Tile( (1, 1), G(h(-fi133 + 35, 36, fi133 + 1), L0[36,36],h(1, 36, fi133)) ) Kro Tile( (1, 1), G(h(1, 36, fi133), v[36,1],h(1, 1, 0)) ) ) )
Eq.ann: {}
 )Entry 9:
Eq: Tile( (1, 1), G(h(1, 36, 35), v[36,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 36, 35), v[36,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 36, 35), L0[36,36],h(1, 36, 35)) ) )
Eq.ann: {}
Entry 10:
Eq: Tile( (1, 1), var[1,1] ) = ( ( T( Tile( (1, 1), x[36,1] ) ) * Tile( (1, 1), x[36,1] ) ) - ( T( Tile( (1, 1), kx[36,1] ) ) * Tile( (1, 1), kx[36,1] ) ) )
Eq.ann: {}
Entry 11:
Eq: Tile( (1, 1), lp[1,1] ) = ( T( Tile( (1, 1), y[36,1] ) ) * Tile( (1, 1), y[36,1] ) )
Eq.ann: {}
 *
 * Created on: 2017-08-14
 * Author: danieles
 */

#pragma once

#include <x86intrin.h>


#define PARAM0 36
#define PARAM1 36

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
  double trg86[1];
  double kr87[1];
  double trg110[1];
  double kr111[1];
  double trg130[1];
  double kr131[1];
  double trg138[1];
  double kr139[1];
  double kr165[1];
  double trg190[1];
  double kr193[1];
  double kr214[1];
  double trg220[1];
  double trg224[1];
  double kr226[1];
  double kr245[1];
  double trg259[1];
  double kr261[1];
  double trg262[1];
  double kr264[1];
  double trg267[1];
  double kr269[1];
  double trg272[1];
  double kr274[1];
  double trg281[1];
  double trg285[1];
  double kr287[1];


  // Generating : L[36,36] = S(h(1, 36, 0), Sqrt( G(h(1, 36, 0), L[36,36],h(1, 36, 0)) ),h(1, 36, 0))

  // 1-BLAC: sqrt(1x1)
  K[0] = sqrt(K[0]);

  // Generating : L[36,36] = S(h(1, 36, 1), ( G(h(1, 36, 1), L[36,36],h(1, 36, 0)) Div G(h(1, 36, 0), L[36,36],h(1, 36, 0)) ),h(1, 36, 0))

  // 1-BLAC: 1x1 / 1x1
  K[36] = K[36] / K[0];

  // Generating : L[36,36] = S(h(1, 36, 1), ( G(h(1, 36, 1), K[36,36],h(1, 36, 1)) - ( G(h(1, 36, 1), L[36,36],h(1, 36, 0)) Kro T( G(h(1, 36, 1), L[36,36],h(1, 36, 0)) ) ) ),h(1, 36, 1))

  // 1-BLAC: (1x1)^T
  trg86[0] = K[36];

  // 1-BLAC: 1x1 Kro 1x1
  kr87[0] = K[36] * trg86[0];

  // 1-BLAC: 1x1 - 1x1
  K[37] = K[37] - kr87[0];

  // Generating : L[36,36] = S(h(1, 36, 1), Sqrt( G(h(1, 36, 1), L[36,36],h(1, 36, 1)) ),h(1, 36, 1))

  // 1-BLAC: sqrt(1x1)
  K[37] = sqrt(K[37]);


  for( int fi18 = 2; fi18 <= 35; fi18++ ) {

    for( int fi43 = 0; fi43 <= fi18 - 2; fi43++ ) {

      // Generating : L[36,36] = S(h(1, 36, fi18), ( G(h(1, 36, fi18), L[36,36],h(1, 36, fi43)) Div G(h(1, 36, fi43), L[36,36],h(1, 36, fi43)) ),h(1, 36, fi43))

      // 1-BLAC: 1x1 / 1x1
      K[36*fi18 + fi43] = K[36*fi18 + fi43] / K[37*fi43];

      // Generating : L[36,36] = Sum_{j7} ( S(h(1, 36, fi18), ( G(h(1, 36, fi18), L[36,36],h(1, 36, fi43 + j7 + 1)) - ( G(h(1, 36, fi18), L[36,36],h(1, 36, fi43)) Kro T( G(h(1, 36, fi43 + j7 + 1), L[36,36],h(1, 36, fi43)) ) ) ),h(1, 36, fi43 + j7 + 1)) )

      for( int j7 = 0; j7 <= fi18 - fi43 - 2; j7++ ) {

        // 1-BLAC: (1x1)^T
        trg110[0] = K[37*fi43 + 36*j7 + 36];

        // 1-BLAC: 1x1 Kro 1x1
        kr111[0] = K[36*fi18 + fi43] * trg110[0];

        // 1-BLAC: 1x1 - 1x1
        K[36*fi18 + fi43 + j7 + 1] = K[36*fi18 + fi43 + j7 + 1] - kr111[0];
      }
    }

    // Generating : L[36,36] = S(h(1, 36, fi18), ( G(h(1, 36, fi18), L[36,36],h(1, 36, Max(0, fi18 - 1))) Div G(h(1, 36, Max(0, fi18 - 1)), L[36,36],h(1, 36, Max(0, fi18 - 1))) ),h(1, 36, Max(0, fi18 - 1)))

    // 1-BLAC: 1x1 / 1x1
    K[36*fi18 + Max(0, fi18 - 1)] = K[36*fi18 + Max(0, fi18 - 1)] / K[37*Max(0, fi18 - 1)];

    // Generating : L[36,36] = ( S(h(1, 36, fi18), ( G(h(1, 36, fi18), K[36,36],h(1, 36, fi18)) - ( G(h(1, 36, fi18), L[36,36],h(1, 36, 0)) Kro T( G(h(1, 36, fi18), L[36,36],h(1, 36, 0)) ) ) ),h(1, 36, fi18)) + Sum_{j7} ( -$(h(1, 36, fi18), ( G(h(1, 36, fi18), L[36,36],h(1, 36, j7)) Kro T( G(h(1, 36, fi18), L[36,36],h(1, 36, j7)) ) ),h(1, 36, fi18)) ) )

    // 1-BLAC: (1x1)^T
    trg130[0] = K[36*fi18];

    // 1-BLAC: 1x1 Kro 1x1
    kr131[0] = K[36*fi18] * trg130[0];

    // 1-BLAC: 1x1 - 1x1
    K[37*fi18] = K[37*fi18] - kr131[0];

    for( int j7 = 1; j7 <= fi18 - 1; j7++ ) {

      // 1-BLAC: (1x1)^T
      trg138[0] = K[36*fi18 + j7];

      // 1-BLAC: 1x1 Kro 1x1
      kr139[0] = K[36*fi18 + j7] * trg138[0];

      // 1-BLAC: 1x1 - 1x1
      K[37*fi18] = K[37*fi18] - kr139[0];
    }

    // Generating : L[36,36] = S(h(1, 36, fi18), Sqrt( G(h(1, 36, fi18), L[36,36],h(1, 36, fi18)) ),h(1, 36, fi18))

    // 1-BLAC: sqrt(1x1)
    K[37*fi18] = sqrt(K[37*fi18]);
  }


  for( int fi18 = 0; fi18 <= 34; fi18++ ) {

    // Generating : t0[36,1] = S(h(1, 36, fi18), ( G(h(1, 36, fi18), t0[36,1],h(1, 1, 0)) Div G(h(1, 36, fi18), L0[36,36],h(1, 36, fi18)) ),h(1, 1, 0))

    // 1-BLAC: 1x1 / 1x1
    y[fi18] = y[fi18] / K[37*fi18];

    // Generating : t0[36,1] = Sum_{j7} ( S(h(1, 36, fi18 + j7 + 1), ( G(h(1, 36, fi18 + j7 + 1), t0[36,1],h(1, 1, 0)) - ( G(h(1, 36, fi18 + j7 + 1), L0[36,36],h(1, 36, fi18)) Kro G(h(1, 36, fi18), t0[36,1],h(1, 1, 0)) ) ),h(1, 1, 0)) )

    for( int j7 = 0; j7 <= -fi18 + 34; j7++ ) {

      // 1-BLAC: 1x1 Kro 1x1
      kr165[0] = K[37*fi18 + 36*j7 + 36] * y[fi18];

      // 1-BLAC: 1x1 - 1x1
      y[fi18 + j7 + 1] = y[fi18 + j7 + 1] - kr165[0];
    }
  }


  // Generating : t0[36,1] = S(h(1, 36, 35), ( G(h(1, 36, 35), t0[36,1],h(1, 1, 0)) Div G(h(1, 36, 35), L0[36,36],h(1, 36, 35)) ),h(1, 1, 0))

  // 1-BLAC: 1x1 / 1x1
  y[35] = y[35] / K[1295];


  for( int fi18 = 0; fi18 <= 34; fi18++ ) {

    // Generating : a[36,1] = S(h(1, 36, -fi18 + 35), ( G(h(1, 36, -fi18 + 35), a[36,1],h(1, 1, 0)) Div G(h(1, 36, -fi18 + 35), L0[36,36],h(1, 36, -fi18 + 35)) ),h(1, 1, 0))

    // 1-BLAC: 1x1 / 1x1
    y[-fi18 + 35] = y[-fi18 + 35] / K[-37*fi18 + 1295];

    // Generating : a[36,1] = Sum_{j7} ( S(h(1, 36, j7), ( G(h(1, 36, j7), a[36,1],h(1, 1, 0)) - ( T( G(h(1, 36, -fi18 + 35), L0[36,36],h(1, 36, j7)) ) Kro G(h(1, 36, -fi18 + 35), a[36,1],h(1, 1, 0)) ) ),h(1, 1, 0)) )

    for( int j7 = 0; j7 <= -fi18 + 34; j7++ ) {

      // 1-BLAC: (1x1)^T
      trg190[0] = K[-36*fi18 + j7 + 1260];

      // 1-BLAC: 1x1 Kro 1x1
      kr193[0] = trg190[0] * y[-fi18 + 35];

      // 1-BLAC: 1x1 - 1x1
      y[j7] = y[j7] - kr193[0];
    }
  }


  // Generating : a[36,1] = S(h(1, 36, 0), ( G(h(1, 36, 0), a[36,1],h(1, 1, 0)) Div G(h(1, 36, 0), L0[36,36],h(1, 36, 0)) ),h(1, 1, 0))

  // 1-BLAC: 1x1 / 1x1
  y[0] = y[0] / K[0];

  // Generating : kx[36,1] = ( Sum_{k16} ( S(h(1, 36, k16), ( G(h(1, 36, k16), X[36,36],h(1, 36, 0)) Kro G(h(1, 36, 0), x[36,1],h(1, 1, 0)) ),h(1, 1, 0)) ) + Sum_{j7} ( Sum_{k16} ( $(h(1, 36, k16), ( G(h(1, 36, k16), X[36,36],h(1, 36, j7)) Kro G(h(1, 36, j7), x[36,1],h(1, 1, 0)) ),h(1, 1, 0)) ) ) )


  for( int k16 = 0; k16 <= 35; k16++ ) {

    // 1-BLAC: 1x1 Kro 1x1
    kx[k16] = X[36*k16] * x[0];
  }


  for( int j7 = 1; j7 <= 35; j7++ ) {

    for( int k16 = 0; k16 <= 35; k16++ ) {

      // 1-BLAC: 1x1 Kro 1x1
      kr214[0] = X[j7 + 36*k16] * x[j7];

      // 1-BLAC: 1x1 + 1x1
      kx[k16] = kx[k16] + kr214[0];
    }
  }


  // Generating : f[1,1] = ( S(h(1, 1, 0), ( T( G(h(1, 36, 0), kx[36,1],h(1, 1, 0)) ) Kro G(h(1, 36, 0), y[36,1],h(1, 1, 0)) ),h(1, 1, 0)) + Sum_{j7} ( $(h(1, 1, 0), ( T( G(h(1, 36, j7), kx[36,1],h(1, 1, 0)) ) Kro G(h(1, 36, j7), y[36,1],h(1, 1, 0)) ),h(1, 1, 0)) ) )

  // 1-BLAC: (1x1)^T
  trg220[0] = kx[0];

  // 1-BLAC: 1x1 Kro 1x1
  f[0] = trg220[0] * y[0];


  for( int j7 = 1; j7 <= 35; j7++ ) {

    // 1-BLAC: (1x1)^T
    trg224[0] = kx[j7];

    // 1-BLAC: 1x1 Kro 1x1
    kr226[0] = trg224[0] * y[j7];

    // 1-BLAC: 1x1 + 1x1
    f[0] = f[0] + kr226[0];
  }


  for( int fi18 = 0; fi18 <= 34; fi18++ ) {

    // Generating : v[36,1] = S(h(1, 36, fi18), ( G(h(1, 36, fi18), v[36,1],h(1, 1, 0)) Div G(h(1, 36, fi18), L0[36,36],h(1, 36, fi18)) ),h(1, 1, 0))

    // 1-BLAC: 1x1 / 1x1
    kx[fi18] = kx[fi18] / K[37*fi18];

    // Generating : v[36,1] = Sum_{j7} ( S(h(1, 36, fi18 + j7 + 1), ( G(h(1, 36, fi18 + j7 + 1), v[36,1],h(1, 1, 0)) - ( G(h(1, 36, fi18 + j7 + 1), L0[36,36],h(1, 36, fi18)) Kro G(h(1, 36, fi18), v[36,1],h(1, 1, 0)) ) ),h(1, 1, 0)) )

    for( int j7 = 0; j7 <= -fi18 + 34; j7++ ) {

      // 1-BLAC: 1x1 Kro 1x1
      kr245[0] = K[37*fi18 + 36*j7 + 36] * kx[fi18];

      // 1-BLAC: 1x1 - 1x1
      kx[fi18 + j7 + 1] = kx[fi18 + j7 + 1] - kr245[0];
    }
  }


  // Generating : v[36,1] = S(h(1, 36, 35), ( G(h(1, 36, 35), v[36,1],h(1, 1, 0)) Div G(h(1, 36, 35), L0[36,36],h(1, 36, 35)) ),h(1, 1, 0))

  // 1-BLAC: 1x1 / 1x1
  kx[35] = kx[35] / K[1295];

  // Generating : var[1,1] = ( ( S(h(1, 1, 0), ( ( T( G(h(1, 36, 0), x[36,1],h(1, 1, 0)) ) Kro G(h(1, 36, 0), x[36,1],h(1, 1, 0)) ) - ( T( G(h(1, 36, 0), kx[36,1],h(1, 1, 0)) ) Kro G(h(1, 36, 0), kx[36,1],h(1, 1, 0)) ) ),h(1, 1, 0)) + Sum_{k16} ( $(h(1, 1, 0), ( T( G(h(1, 36, k16), x[36,1],h(1, 1, 0)) ) Kro G(h(1, 36, k16), x[36,1],h(1, 1, 0)) ),h(1, 1, 0)) ) ) + Sum_{j7} ( -$(h(1, 1, 0), ( T( G(h(1, 36, j7), kx[36,1],h(1, 1, 0)) ) Kro G(h(1, 36, j7), kx[36,1],h(1, 1, 0)) ),h(1, 1, 0)) ) )

  // 1-BLAC: (1x1)^T
  trg259[0] = x[0];

  // 1-BLAC: 1x1 Kro 1x1
  kr261[0] = trg259[0] * x[0];

  // 1-BLAC: (1x1)^T
  trg262[0] = kx[0];

  // 1-BLAC: 1x1 Kro 1x1
  kr264[0] = trg262[0] * kx[0];

  // 1-BLAC: 1x1 - 1x1
  var[0] = kr261[0] - kr264[0];


  for( int k16 = 1; k16 <= 35; k16++ ) {

    // 1-BLAC: (1x1)^T
    trg267[0] = x[k16];

    // 1-BLAC: 1x1 Kro 1x1
    kr269[0] = trg267[0] * x[k16];

    // 1-BLAC: 1x1 + 1x1
    var[0] = var[0] + kr269[0];
  }


  for( int j7 = 1; j7 <= 35; j7++ ) {

    // 1-BLAC: (1x1)^T
    trg272[0] = kx[j7];

    // 1-BLAC: 1x1 Kro 1x1
    kr274[0] = trg272[0] * kx[j7];

    // 1-BLAC: 1x1 - 1x1
    var[0] = var[0] - kr274[0];
  }


  // Generating : lp[1,1] = ( S(h(1, 1, 0), ( T( G(h(1, 36, 0), y[36,1],h(1, 1, 0)) ) Kro G(h(1, 36, 0), y[36,1],h(1, 1, 0)) ),h(1, 1, 0)) + Sum_{j7} ( $(h(1, 1, 0), ( T( G(h(1, 36, j7), y[36,1],h(1, 1, 0)) ) Kro G(h(1, 36, j7), y[36,1],h(1, 1, 0)) ),h(1, 1, 0)) ) )

  // 1-BLAC: (1x1)^T
  trg281[0] = y[0];

  // 1-BLAC: 1x1 Kro 1x1
  lp[0] = trg281[0] * y[0];


  for( int j7 = 1; j7 <= 35; j7++ ) {

    // 1-BLAC: (1x1)^T
    trg285[0] = y[j7];

    // 1-BLAC: 1x1 Kro 1x1
    kr287[0] = trg285[0] * y[j7];

    // 1-BLAC: 1x1 + 1x1
    lp[0] = lp[0] + kr287[0];
  }

}
