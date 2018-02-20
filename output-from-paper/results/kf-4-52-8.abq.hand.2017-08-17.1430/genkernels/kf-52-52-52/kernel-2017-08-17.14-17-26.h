/*
 * kf_kernel.h
 *
Decl { {u'B': SquaredMatrix[B, (52, 52), GenMatAccess], u'F': SquaredMatrix[F, (52, 52), GenMatAccess], u'H': SquaredMatrix[H, (52, 52), GenMatAccess], u'U0': UpperTriangular[U0, (52, 52), GenMatAccess], u'M5': SquaredMatrix[M5, (52, 52), GenMatAccess], u'P': Symmetric[P, (52, 52), USMatAccess], u'M7': SquaredMatrix[M7, (52, 52), GenMatAccess], u'M6': SquaredMatrix[M6, (52, 52), GenMatAccess], u'v4': Matrix[v4, (52, 1), GenMatAccess], u'M0': SquaredMatrix[M0, (52, 52), GenMatAccess], u'M3': Symmetric[M3, (52, 52), USMatAccess], u'M2': SquaredMatrix[M2, (52, 52), GenMatAccess], u'Y': Symmetric[Y, (52, 52), USMatAccess], u'R': Symmetric[R, (52, 52), USMatAccess], u'U': UpperTriangular[U, (52, 52), GenMatAccess], u'M8': SquaredMatrix[M8, (52, 52), GenMatAccess], u'v0': Matrix[v0, (52, 1), GenMatAccess], u'u': Matrix[u, (52, 1), GenMatAccess], u'M4': Symmetric[M4, (52, 52), USMatAccess], u'v2': Matrix[v2, (52, 1), GenMatAccess], u'v1': Matrix[v1, (52, 1), GenMatAccess], u'v3': Matrix[v3, (52, 1), GenMatAccess], u'Q': Symmetric[Q, (52, 52), USMatAccess], u'x': Matrix[x, (52, 1), GenMatAccess], u'y': Matrix[y, (52, 1), GenMatAccess], u'M1': SquaredMatrix[M1, (52, 52), GenMatAccess], u'z': Matrix[z, (52, 1), GenMatAccess]} }
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ann: {'part_schemes': {'Assign_Mul_UpperTriangular_Matrix_Matrix_opt': {'m0': 'm04.ll', 'm2': 'm21.ll'}, 'Assign_Mul_T_UpperTriangular_UpperTriangular_Symmetric_opt': {'m0': 'm01.ll'}, 'ldiv_utn_ow_opt': {'m': 'm4.ll', 'n': 'n1.ll'}, 'Assign_Mul_T_UpperTriangular_Matrix_Matrix_opt': {'m0': 'm04.ll', 'm2': 'm21.ll'}, 'Assign_Mul_T_UpperTriangular_SquaredMatrix_SquaredMatrix_opt': {'m0': 'm04.ll', 'm2': 'm21.ll'}, 'Assign_Mul_UpperTriangular_SquaredMatrix_SquaredMatrix_opt': {'m0': 'm04.ll', 'm2': 'm21.ll'}}, 'cl1ck_v': 0, 'variant_tag': 'Assign_Mul_T_UpperTriangular_Matrix_Matrix_opt_m04_m21_Assign_Mul_T_UpperTriangular_SquaredMatrix_SquaredMatrix_opt_m04_m21_Assign_Mul_T_UpperTriangular_UpperTriangular_Symmetric_opt_m01_Assign_Mul_UpperTriangular_Matrix_Matrix_opt_m04_m21_Assign_Mul_UpperTriangular_SquaredMatrix_SquaredMatrix_opt_m04_m21_ldiv_utn_ow_opt_m4_n1'}

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Entry 0:
Eq: Tile( (1, 1), y[52,1] ) = ( ( Tile( (1, 1), F[52,52] ) * Tile( (1, 1), x[52,1] ) ) + ( Tile( (1, 1), B[52,52] ) * Tile( (1, 1), u[52,1] ) ) )
Eq.ann: {}
Entry 1:
Eq: Tile( (1, 1), M0[52,52] ) = ( Tile( (1, 1), F[52,52] ) * Tile( (1, 1), P[52,52] ) )
Eq.ann: {}
Entry 2:
Eq: Tile( (1, 1), Y[52,52] ) = ( ( Tile( (1, 1), M0[52,52] ) * T( Tile( (1, 1), F[52,52] ) ) ) + Tile( (1, 1), Q[52,52] ) )
Eq.ann: {}
Entry 3:
Eq: Tile( (1, 1), v0[52,1] ) = ( Tile( (1, 1), z[52,1] ) - ( Tile( (1, 1), H[52,52] ) * Tile( (1, 1), y[52,1] ) ) )
Eq.ann: {}
Entry 4:
Eq: Tile( (1, 1), M1[52,52] ) = ( Tile( (1, 1), H[52,52] ) * Tile( (1, 1), Y[52,52] ) )
Eq.ann: {}
Entry 5:
Eq: Tile( (1, 1), M2[52,52] ) = ( Tile( (1, 1), Y[52,52] ) * T( Tile( (1, 1), H[52,52] ) ) )
Eq.ann: {}
Entry 6:
Eq: Tile( (1, 1), M3[52,52] ) = ( ( Tile( (1, 1), M1[52,52] ) * T( Tile( (1, 1), H[52,52] ) ) ) + Tile( (1, 1), R[52,52] ) )
Eq.ann: {}
Entry 7:
Eq: Tile( (1, 1), G(h(1, 52, 0), U[52,52],h(1, 52, 0)) ) = Sqrt( Tile( (1, 1), G(h(1, 52, 0), U[52,52],h(1, 52, 0)) ) )
Eq.ann: {}
Entry 8:
For_{fi35;1;51;1} ( Entry 0:
For_{fi60;0;fi35 - 2;1} ( Entry 0:
Eq: Tile( (1, 1), G(h(1, 52, fi60), U[52,52],h(1, 52, fi35)) ) = ( Tile( (1, 1), G(h(1, 52, fi60), U[52,52],h(1, 52, fi35)) ) Div Tile( (1, 1), G(h(1, 52, fi60), U[52,52],h(1, 52, fi60)) ) )
Eq.ann: {}
Entry 1:
Eq: Tile( (1, 1), G(h(fi35 - fi60 - 1, 52, fi60 + 1), U[52,52],h(1, 52, fi35)) ) = ( Tile( (1, 1), G(h(fi35 - fi60 - 1, 52, fi60 + 1), U[52,52],h(1, 52, fi35)) ) - ( T( Tile( (1, 1), G(h(1, 52, fi60), U[52,52],h(fi35 - fi60 - 1, 52, fi60 + 1)) ) ) Kro Tile( (1, 1), G(h(1, 52, fi60), U[52,52],h(1, 52, fi35)) ) ) )
Eq.ann: {}
 )Entry 1:
Eq: Tile( (1, 1), G(h(1, 52, Max(0, fi35 - 1)), U[52,52],h(1, 52, fi35)) ) = ( Tile( (1, 1), G(h(1, 52, Max(0, fi35 - 1)), U[52,52],h(1, 52, fi35)) ) Div Tile( (1, 1), G(h(1, 52, Max(0, fi35 - 1)), U[52,52],h(1, 52, Max(0, fi35 - 1))) ) )
Eq.ann: {}
Entry 2:
Eq: Tile( (1, 1), G(h(1, 52, fi35), U[52,52],h(1, 52, fi35)) ) = ( Tile( (1, 1), G(h(1, 52, fi35), M4[52,52],h(1, 52, fi35)) ) - ( T( Tile( (1, 1), G(h(fi35, 52, 0), U[52,52],h(1, 52, fi35)) ) ) * Tile( (1, 1), G(h(fi35, 52, 0), U[52,52],h(1, 52, fi35)) ) ) )
Eq.ann: {}
Entry 3:
Eq: Tile( (1, 1), G(h(1, 52, fi35), U[52,52],h(1, 52, fi35)) ) = Sqrt( Tile( (1, 1), G(h(1, 52, fi35), U[52,52],h(1, 52, fi35)) ) )
Eq.ann: {}
 )Entry 9:
For_{fi92;0;50;1} ( Entry 0:
Eq: Tile( (1, 1), G(h(1, 52, fi92), v2[52,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 52, fi92), v2[52,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 52, fi92), U0[52,52],h(1, 52, fi92)) ) )
Eq.ann: {}
Entry 1:
Eq: Tile( (1, 1), G(h(-fi92 + 51, 52, fi92 + 1), v2[52,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(-fi92 + 51, 52, fi92 + 1), v2[52,1],h(1, 1, 0)) ) - ( T( Tile( (1, 1), G(h(1, 52, fi92), U0[52,52],h(-fi92 + 51, 52, fi92 + 1)) ) ) Kro Tile( (1, 1), G(h(1, 52, fi92), v2[52,1],h(1, 1, 0)) ) ) )
Eq.ann: {}
 )Entry 10:
Eq: Tile( (1, 1), G(h(1, 52, 51), v2[52,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 52, 51), v2[52,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 52, 51), U0[52,52],h(1, 52, 51)) ) )
Eq.ann: {}
Entry 11:
For_{fi121;0;50;1} ( Entry 0:
Eq: Tile( (1, 1), G(h(1, 52, -fi121 + 51), v4[52,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 52, -fi121 + 51), v4[52,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 52, -fi121 + 51), U0[52,52],h(1, 52, -fi121 + 51)) ) )
Eq.ann: {}
Entry 1:
Eq: Tile( (1, 1), G(h(-fi121 + 51, 52, 0), v4[52,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(-fi121 + 51, 52, 0), v4[52,1],h(1, 1, 0)) ) - ( Tile( (1, 1), G(h(-fi121 + 51, 52, 0), U0[52,52],h(1, 52, -fi121 + 51)) ) Kro Tile( (1, 1), G(h(1, 52, -fi121 + 51), v4[52,1],h(1, 1, 0)) ) ) )
Eq.ann: {}
 )Entry 12:
Eq: Tile( (1, 1), G(h(1, 52, 0), v4[52,1],h(1, 1, 0)) ) = ( Tile( (1, 1), G(h(1, 52, 0), v4[52,1],h(1, 1, 0)) ) Div Tile( (1, 1), G(h(1, 52, 0), U0[52,52],h(1, 52, 0)) ) )
Eq.ann: {}
Entry 13:
For_{fi150;0;50;1} ( Entry 0:
For_{fi169;0;51;1} ( Entry 0:
Eq: Tile( (1, 1), G(h(1, 52, fi150), M6[52,52],h(1, 52, fi169)) ) = ( Tile( (1, 1), G(h(1, 52, fi150), M6[52,52],h(1, 52, fi169)) ) Div Tile( (1, 1), G(h(1, 52, fi150), U0[52,52],h(1, 52, fi150)) ) )
Eq.ann: {}
 )Entry 1:
Eq: Tile( (1, 1), G(h(-fi150 + 51, 52, fi150 + 1), M6[52,52],h(52, 52, 0)) ) = ( Tile( (1, 1), G(h(-fi150 + 51, 52, fi150 + 1), M6[52,52],h(52, 52, 0)) ) - ( T( Tile( (1, 1), G(h(1, 52, fi150), U0[52,52],h(-fi150 + 51, 52, fi150 + 1)) ) ) * Tile( (1, 1), G(h(1, 52, fi150), M6[52,52],h(52, 52, 0)) ) ) )
Eq.ann: {}
 )Entry 14:
For_{fi180;0;51;1} ( Entry 0:
Eq: Tile( (1, 1), G(h(1, 52, 51), M6[52,52],h(1, 52, fi180)) ) = ( Tile( (1, 1), G(h(1, 52, 51), M6[52,52],h(1, 52, fi180)) ) Div Tile( (1, 1), G(h(1, 52, 51), U0[52,52],h(1, 52, 51)) ) )
Eq.ann: {}
 )Entry 15:
For_{fi191;0;50;1} ( Entry 0:
For_{fi210;0;51;1} ( Entry 0:
Eq: Tile( (1, 1), G(h(1, 52, -fi191 + 51), M8[52,52],h(1, 52, fi210)) ) = ( Tile( (1, 1), G(h(1, 52, -fi191 + 51), M8[52,52],h(1, 52, fi210)) ) Div Tile( (1, 1), G(h(1, 52, -fi191 + 51), U0[52,52],h(1, 52, -fi191 + 51)) ) )
Eq.ann: {}
 )Entry 1:
Eq: Tile( (1, 1), G(h(-fi191 + 51, 52, 0), M8[52,52],h(52, 52, 0)) ) = ( Tile( (1, 1), G(h(-fi191 + 51, 52, 0), M8[52,52],h(52, 52, 0)) ) - ( Tile( (1, 1), G(h(-fi191 + 51, 52, 0), U0[52,52],h(1, 52, -fi191 + 51)) ) * Tile( (1, 1), G(h(1, 52, -fi191 + 51), M8[52,52],h(52, 52, 0)) ) ) )
Eq.ann: {}
 )Entry 16:
For_{fi221;0;51;1} ( Entry 0:
Eq: Tile( (1, 1), G(h(1, 52, 0), M8[52,52],h(1, 52, fi221)) ) = ( Tile( (1, 1), G(h(1, 52, 0), M8[52,52],h(1, 52, fi221)) ) Div Tile( (1, 1), G(h(1, 52, 0), U0[52,52],h(1, 52, 0)) ) )
Eq.ann: {}
 )Entry 17:
Eq: Tile( (1, 1), x[52,1] ) = ( Tile( (1, 1), y[52,1] ) + ( Tile( (1, 1), M2[52,52] ) * Tile( (1, 1), v0[52,1] ) ) )
Eq.ann: {}
Entry 18:
Eq: Tile( (1, 1), P[52,52] ) = ( Tile( (1, 1), Y[52,52] ) - ( Tile( (1, 1), M2[52,52] ) * Tile( (1, 1), M1[52,52] ) ) )
Eq.ann: {}
 *
 * Created on: 2017-08-17
 * Author: danieles
 */

#pragma once

#include <x86intrin.h>


#define PARAM0 52
#define PARAM1 52
#define PARAM2 52

#define ERRTHRESH 1e-5

#define SOFTERRTHRESH 1e-7

#define NUMREP 30

#define floord(n,d) (((n)<0) ? -((-(n)+(d)-1)/(d)) : (n)/(d))
#define ceild(n,d)  (((n)<0) ? -((-(n))/(d)) : ((n)+(d)-1)/(d))
#define max(x,y)    ((x) > (y) ? (x) : (y))
#define min(x,y)    ((x) < (y) ? (x) : (y))
#define Max(x,y)    ((x) > (y) ? (x) : (y))
#define Min(x,y)    ((x) < (y) ? (x) : (y))


static __attribute__((noinline)) void kernel(double const * F, double const * B, double const * u, double const * Q, double const * z, double const * H, double const * R, double * y, double * x, double * M0, double * P, double * Y, double * v0, double * M1, double * M2, double * M3)
{
  double kr95[1];
  double kr98[1];
  double kr104[1];
  double kr110[1];
  double trg129[1];
  double kr130[1];
  double kr136[1];
  double kr141[1];
  double trg149[1];
  double kr150[1];
  double kr156[1];
  double trg165[1];
  double kr166[1];
  double trg171[1];
  double kr172[1];
  double trg178[1];
  double kr179[1];
  double trg186[1];
  double kr187[1];
  double trg190[1];
  double kr191[1];
  double trg195[1];
  double kr196[1];
  double kr208[1];
  double kr214[1];
  double trg233[1];
  double kr234[1];
  double kr240[1];
  double kr245[1];
  double trg253[1];
  double kr254[1];
  double kr260[1];
  double trg269[1];
  double trg272[1];
  double trg273[1];
  double trg280[1];
  double kr281[1];
  double trg285[1];
  double kr286[1];
  double trg288[1];
  double trg289[1];
  double kr290[1];
  double trg298[1];
  double kr299[1];
  double trg303[1];
  double kr304[1];
  double trg312[1];
  double kr313[1];
  double trg318[1];
  double kr319[1];
  double trg325[1];
  double kr326[1];
  double trg333[1];
  double kr334[1];
  double trg337[1];
  double kr338[1];
  double trg342[1];
  double kr343[1];
  double trg368[1];
  double kr371[1];
  double trg392[1];
  double kr395[1];
  double trg412[1];
  double kr415[1];
  double trg420[1];
  double kr423[1];
  double trg446[1];
  double kr449[1];
  double kr477[1];
  double trg502[1];
  double kr505[1];
  double kr534[1];
  double kr552[1];
  double kr558[1];
  double kr567[1];
  double kr573[1];
  double kr580[1];
  double kr587[1];
  double kr592[1];
  double kr598[1];


  // Generating : y[52,1] = ( ( Sum_{i0} ( S(h(1, 52, i0), ( ( G(h(1, 52, i0), F[52,52],h(1, 52, 0)) Kro G(h(1, 52, 0), x[52,1],h(1, 1, 0)) ) + ( G(h(1, 52, i0), B[52,52],h(1, 52, 0)) Kro G(h(1, 52, 0), u[52,1],h(1, 1, 0)) ) ),h(1, 1, 0)) ) + Sum_{k2} ( Sum_{i0} ( $(h(1, 52, i0), ( G(h(1, 52, i0), F[52,52],h(1, 52, k2)) Kro G(h(1, 52, k2), x[52,1],h(1, 1, 0)) ),h(1, 1, 0)) ) ) ) + Sum_{k3} ( Sum_{i0} ( $(h(1, 52, i0), ( G(h(1, 52, i0), B[52,52],h(1, 52, k3)) Kro G(h(1, 52, k3), u[52,1],h(1, 1, 0)) ),h(1, 1, 0)) ) ) )


  for( int i0 = 0; i0 <= 51; i0++ ) {

    // 1-BLAC: 1x1 Kro 1x1
    kr95[0] = F[52*i0] * x[0];

    // 1-BLAC: 1x1 Kro 1x1
    kr98[0] = B[52*i0] * u[0];

    // 1-BLAC: 1x1 + 1x1
    y[i0] = kr95[0] + kr98[0];
  }


  for( int k2 = 1; k2 <= 51; k2++ ) {

    for( int i0 = 0; i0 <= 51; i0++ ) {

      // 1-BLAC: 1x1 Kro 1x1
      kr104[0] = F[52*i0 + k2] * x[k2];

      // 1-BLAC: 1x1 + 1x1
      y[i0] = y[i0] + kr104[0];
    }
  }


  for( int k3 = 1; k3 <= 51; k3++ ) {

    for( int i0 = 0; i0 <= 51; i0++ ) {

      // 1-BLAC: 1x1 Kro 1x1
      kr110[0] = B[52*i0 + k3] * u[k3];

      // 1-BLAC: 1x1 + 1x1
      y[i0] = y[i0] + kr110[0];
    }
  }


  // Generating : M0[52,52] = ( ( ( ( Sum_{i0} ( S(h(1, 52, i0), ( G(h(1, 52, i0), F[52,52],h(1, 52, 0)) Kro G(h(1, 52, 0), P[52,52],h(1, 52, 0)) ),h(1, 52, 0)) ) + Sum_{k2} ( Sum_{i0} ( S(h(1, 52, i0), ( G(h(1, 52, i0), F[52,52],h(1, 52, 0)) Kro G(h(1, 52, 0), P[52,52],h(1, 52, k2)) ),h(1, 52, k2)) ) ) ) + Sum_{k3} ( ( ( Sum_{k2} ( Sum_{i0} ( $(h(1, 52, i0), ( G(h(1, 52, i0), F[52,52],h(1, 52, k3)) Kro T( G(h(1, 52, k2), P[52,52],h(1, 52, k3)) ) ),h(1, 52, k2)) ) ) + Sum_{i0} ( $(h(1, 52, i0), ( G(h(1, 52, i0), F[52,52],h(1, 52, k3)) Kro G(h(1, 52, k3), P[52,52],h(1, 52, k3)) ),h(1, 52, k3)) ) ) + Sum_{k2} ( Sum_{i0} ( $(h(1, 52, i0), ( G(h(1, 52, i0), F[52,52],h(1, 52, k3)) Kro G(h(1, 52, k3), P[52,52],h(1, 52, k2)) ),h(1, 52, k2)) ) ) ) ) ) + Sum_{k2} ( Sum_{i0} ( $(h(1, 52, i0), ( G(h(1, 52, i0), F[52,52],h(1, 52, 51)) Kro T( G(h(1, 52, k2), P[52,52],h(1, 52, 51)) ) ),h(1, 52, k2)) ) ) ) + Sum_{i0} ( $(h(1, 52, i0), ( G(h(1, 52, i0), F[52,52],h(1, 52, 51)) Kro G(h(1, 52, 51), P[52,52],h(1, 52, 51)) ),h(1, 52, 51)) ) )


  for( int i0 = 0; i0 <= 51; i0++ ) {

    // 1-BLAC: 1x1 Kro 1x1
    M0[52*i0] = F[52*i0] * P[0];
  }


  for( int k2 = 1; k2 <= 51; k2++ ) {

    for( int i0 = 0; i0 <= 51; i0++ ) {

      // 1-BLAC: 1x1 Kro 1x1
      M0[52*i0 + k2] = F[52*i0] * P[k2];
    }
  }


  for( int k3 = 1; k3 <= 50; k3++ ) {

    for( int k2 = 0; k2 <= k3 - 1; k2++ ) {

      for( int i0 = 0; i0 <= 51; i0++ ) {

        // 1-BLAC: (1x1)^T
        trg129[0] = P[52*k2 + k3];

        // 1-BLAC: 1x1 Kro 1x1
        kr130[0] = F[52*i0 + k3] * trg129[0];

        // 1-BLAC: 1x1 + 1x1
        M0[52*i0 + k2] = M0[52*i0 + k2] + kr130[0];
      }
    }

    for( int i0 = 0; i0 <= 51; i0++ ) {

      // 1-BLAC: 1x1 Kro 1x1
      kr136[0] = F[52*i0 + k3] * P[53*k3];

      // 1-BLAC: 1x1 + 1x1
      M0[52*i0 + k3] = M0[52*i0 + k3] + kr136[0];
    }

    for( int k2 = k3 + 1; k2 <= 51; k2++ ) {

      for( int i0 = 0; i0 <= 51; i0++ ) {

        // 1-BLAC: 1x1 Kro 1x1
        kr141[0] = F[52*i0 + k3] * P[k2 + 52*k3];

        // 1-BLAC: 1x1 + 1x1
        M0[52*i0 + k2] = M0[52*i0 + k2] + kr141[0];
      }
    }
  }


  for( int k2 = 0; k2 <= 50; k2++ ) {

    // 1-BLAC: (1x1)^T
    trg149[0] = P[52*k2 + 51];

    for( int i0 = 0; i0 <= 51; i0++ ) {

      // 1-BLAC: (1x1)^T
      trg149[0] = P[52*k2 + 51];

      // 1-BLAC: 1x1 Kro 1x1
      kr150[0] = F[52*i0 + 51] * trg149[0];

      // 1-BLAC: 1x1 + 1x1
      M0[52*i0 + k2] = M0[52*i0 + k2] + kr150[0];
    }
  }


  for( int i0 = 0; i0 <= 51; i0++ ) {

    // 1-BLAC: 1x1 Kro 1x1
    kr156[0] = F[52*i0 + 51] * P[2703];

    // 1-BLAC: 1x1 + 1x1
    M0[52*i0 + 51] = M0[52*i0 + 51] + kr156[0];
  }


  // Generating : Y[52,52] = ( ( S(h(1, 52, 0), ( ( G(h(1, 52, 0), M0[52,52],h(1, 52, 0)) Kro T( G(h(1, 52, 0), F[52,52],h(1, 52, 0)) ) ) + G(h(1, 52, 0), Q[52,52],h(1, 52, 0)) ),h(1, 52, 0)) + Sum_{k2} ( ( Sum_{i0} ( S(h(1, 52, i0), ( ( G(h(1, 52, i0), M0[52,52],h(1, 52, 0)) Kro T( G(h(1, 52, k2), F[52,52],h(1, 52, 0)) ) ) + G(h(1, 52, i0), Q[52,52],h(1, 52, k2)) ),h(1, 52, k2)) ) + S(h(1, 52, k2), ( ( G(h(1, 52, k2), M0[52,52],h(1, 52, 0)) Kro T( G(h(1, 52, k2), F[52,52],h(1, 52, 0)) ) ) + G(h(1, 52, k2), Q[52,52],h(1, 52, k2)) ),h(1, 52, k2)) ) ) ) + Sum_{k3} ( ( $(h(1, 52, 0), ( G(h(1, 52, 0), M0[52,52],h(1, 52, k3)) Kro T( G(h(1, 52, 0), F[52,52],h(1, 52, k3)) ) ),h(1, 52, 0)) + Sum_{k2} ( ( Sum_{i0} ( $(h(1, 52, i0), ( G(h(1, 52, i0), M0[52,52],h(1, 52, k3)) Kro T( G(h(1, 52, k2), F[52,52],h(1, 52, k3)) ) ),h(1, 52, k2)) ) + $(h(1, 52, k2), ( G(h(1, 52, k2), M0[52,52],h(1, 52, k3)) Kro T( G(h(1, 52, k2), F[52,52],h(1, 52, k3)) ) ),h(1, 52, k2)) ) ) ) ) )

  // 1-BLAC: (1x1)^T
  trg165[0] = F[0];

  // 1-BLAC: 1x1 Kro 1x1
  kr166[0] = M0[0] * trg165[0];

  // 1-BLAC: 1x1 + 1x1
  Y[0] = kr166[0] + Q[0];


  for( int k2 = 1; k2 <= 51; k2++ ) {

    // 1-BLAC: (1x1)^T
    trg171[0] = F[52*k2];

    for( int i0 = 0; i0 <= k2 - 1; i0++ ) {

      // 1-BLAC: (1x1)^T
      trg171[0] = F[52*k2];

      // 1-BLAC: 1x1 Kro 1x1
      kr172[0] = M0[52*i0] * trg171[0];

      // 1-BLAC: 1x1 + 1x1
      Y[52*i0 + k2] = kr172[0] + Q[52*i0 + k2];
    }

    // 1-BLAC: (1x1)^T
    trg178[0] = F[52*k2];

    // 1-BLAC: 1x1 Kro 1x1
    kr179[0] = M0[52*k2] * trg178[0];

    // 1-BLAC: 1x1 + 1x1
    Y[53*k2] = kr179[0] + Q[53*k2];
  }


  for( int k3 = 1; k3 <= 51; k3++ ) {

    // 1-BLAC: (1x1)^T
    trg186[0] = F[k3];

    // 1-BLAC: 1x1 Kro 1x1
    kr187[0] = M0[k3] * trg186[0];

    // 1-BLAC: 1x1 + 1x1
    Y[0] = Y[0] + kr187[0];

    for( int k2 = 1; k2 <= 51; k2++ ) {

      // 1-BLAC: (1x1)^T
      trg190[0] = F[52*k2 + k3];

      for( int i0 = 0; i0 <= k2 - 1; i0++ ) {

        // 1-BLAC: (1x1)^T
        trg190[0] = F[52*k2 + k3];

        // 1-BLAC: 1x1 Kro 1x1
        kr191[0] = M0[52*i0 + k3] * trg190[0];

        // 1-BLAC: 1x1 + 1x1
        Y[52*i0 + k2] = Y[52*i0 + k2] + kr191[0];
      }

      // 1-BLAC: (1x1)^T
      trg195[0] = F[52*k2 + k3];

      // 1-BLAC: 1x1 Kro 1x1
      kr196[0] = M0[52*k2 + k3] * trg195[0];

      // 1-BLAC: 1x1 + 1x1
      Y[53*k2] = Y[53*k2] + kr196[0];
    }
  }


  // Generating : v0[52,1] = ( Sum_{k2} ( S(h(1, 52, k2), ( G(h(1, 52, k2), z[52,1],h(1, 1, 0)) - ( G(h(1, 52, k2), H[52,52],h(1, 52, 0)) Kro G(h(1, 52, 0), y[52,1],h(1, 1, 0)) ) ),h(1, 1, 0)) ) + Sum_{k3} ( Sum_{k2} ( -$(h(1, 52, k2), ( G(h(1, 52, k2), H[52,52],h(1, 52, k3)) Kro G(h(1, 52, k3), y[52,1],h(1, 1, 0)) ),h(1, 1, 0)) ) ) )


  for( int k2 = 0; k2 <= 51; k2++ ) {

    // 1-BLAC: 1x1 Kro 1x1
    kr208[0] = H[52*k2] * y[0];

    // 1-BLAC: 1x1 - 1x1
    v0[k2] = z[k2] - kr208[0];
  }


  for( int k3 = 1; k3 <= 51; k3++ ) {

    for( int k2 = 0; k2 <= 51; k2++ ) {

      // 1-BLAC: 1x1 Kro 1x1
      kr214[0] = H[52*k2 + k3] * y[k3];

      // 1-BLAC: 1x1 - 1x1
      v0[k2] = v0[k2] - kr214[0];
    }
  }


  // Generating : M1[52,52] = ( ( ( ( Sum_{i0} ( S(h(1, 52, i0), ( G(h(1, 52, i0), H[52,52],h(1, 52, 0)) Kro G(h(1, 52, 0), Y[52,52],h(1, 52, 0)) ),h(1, 52, 0)) ) + Sum_{k2} ( Sum_{i0} ( S(h(1, 52, i0), ( G(h(1, 52, i0), H[52,52],h(1, 52, 0)) Kro G(h(1, 52, 0), Y[52,52],h(1, 52, k2)) ),h(1, 52, k2)) ) ) ) + Sum_{k3} ( ( ( Sum_{k2} ( Sum_{i0} ( $(h(1, 52, i0), ( G(h(1, 52, i0), H[52,52],h(1, 52, k3)) Kro T( G(h(1, 52, k2), Y[52,52],h(1, 52, k3)) ) ),h(1, 52, k2)) ) ) + Sum_{i0} ( $(h(1, 52, i0), ( G(h(1, 52, i0), H[52,52],h(1, 52, k3)) Kro G(h(1, 52, k3), Y[52,52],h(1, 52, k3)) ),h(1, 52, k3)) ) ) + Sum_{k2} ( Sum_{i0} ( $(h(1, 52, i0), ( G(h(1, 52, i0), H[52,52],h(1, 52, k3)) Kro G(h(1, 52, k3), Y[52,52],h(1, 52, k2)) ),h(1, 52, k2)) ) ) ) ) ) + Sum_{k2} ( Sum_{i0} ( $(h(1, 52, i0), ( G(h(1, 52, i0), H[52,52],h(1, 52, 51)) Kro T( G(h(1, 52, k2), Y[52,52],h(1, 52, 51)) ) ),h(1, 52, k2)) ) ) ) + Sum_{i0} ( $(h(1, 52, i0), ( G(h(1, 52, i0), H[52,52],h(1, 52, 51)) Kro G(h(1, 52, 51), Y[52,52],h(1, 52, 51)) ),h(1, 52, 51)) ) )


  for( int i0 = 0; i0 <= 51; i0++ ) {

    // 1-BLAC: 1x1 Kro 1x1
    M1[52*i0] = H[52*i0] * Y[0];
  }


  for( int k2 = 1; k2 <= 51; k2++ ) {

    for( int i0 = 0; i0 <= 51; i0++ ) {

      // 1-BLAC: 1x1 Kro 1x1
      M1[52*i0 + k2] = H[52*i0] * Y[k2];
    }
  }


  for( int k3 = 1; k3 <= 50; k3++ ) {

    for( int k2 = 0; k2 <= k3 - 1; k2++ ) {

      for( int i0 = 0; i0 <= 51; i0++ ) {

        // 1-BLAC: (1x1)^T
        trg233[0] = Y[52*k2 + k3];

        // 1-BLAC: 1x1 Kro 1x1
        kr234[0] = H[52*i0 + k3] * trg233[0];

        // 1-BLAC: 1x1 + 1x1
        M1[52*i0 + k2] = M1[52*i0 + k2] + kr234[0];
      }
    }

    for( int i0 = 0; i0 <= 51; i0++ ) {

      // 1-BLAC: 1x1 Kro 1x1
      kr240[0] = H[52*i0 + k3] * Y[53*k3];

      // 1-BLAC: 1x1 + 1x1
      M1[52*i0 + k3] = M1[52*i0 + k3] + kr240[0];
    }

    for( int k2 = k3 + 1; k2 <= 51; k2++ ) {

      for( int i0 = 0; i0 <= 51; i0++ ) {

        // 1-BLAC: 1x1 Kro 1x1
        kr245[0] = H[52*i0 + k3] * Y[k2 + 52*k3];

        // 1-BLAC: 1x1 + 1x1
        M1[52*i0 + k2] = M1[52*i0 + k2] + kr245[0];
      }
    }
  }


  for( int k2 = 0; k2 <= 50; k2++ ) {

    // 1-BLAC: (1x1)^T
    trg253[0] = Y[52*k2 + 51];

    for( int i0 = 0; i0 <= 51; i0++ ) {

      // 1-BLAC: (1x1)^T
      trg253[0] = Y[52*k2 + 51];

      // 1-BLAC: 1x1 Kro 1x1
      kr254[0] = H[52*i0 + 51] * trg253[0];

      // 1-BLAC: 1x1 + 1x1
      M1[52*i0 + k2] = M1[52*i0 + k2] + kr254[0];
    }
  }


  for( int i0 = 0; i0 <= 51; i0++ ) {

    // 1-BLAC: 1x1 Kro 1x1
    kr260[0] = H[52*i0 + 51] * Y[2703];

    // 1-BLAC: 1x1 + 1x1
    M1[52*i0 + 51] = M1[52*i0 + 51] + kr260[0];
  }


  // Generating : M2[52,52] = ( ( Sum_{k2} ( ( S(h(1, 52, 0), ( G(h(1, 52, 0), Y[52,52],h(1, 52, 0)) Kro T( G(h(1, 52, k2), H[52,52],h(1, 52, 0)) ) ),h(1, 52, k2)) + Sum_{i0} ( S(h(1, 52, i0), ( T( G(h(1, 52, 0), Y[52,52],h(1, 52, i0)) ) Kro T( G(h(1, 52, k2), H[52,52],h(1, 52, 0)) ) ),h(1, 52, k2)) ) ) ) + Sum_{k3} ( Sum_{k2} ( ( ( Sum_{i0} ( $(h(1, 52, i0), ( G(h(1, 52, i0), Y[52,52],h(1, 52, k3)) Kro T( G(h(1, 52, k2), H[52,52],h(1, 52, k3)) ) ),h(1, 52, k2)) ) + $(h(1, 52, k3), ( G(h(1, 52, k3), Y[52,52],h(1, 52, k3)) Kro T( G(h(1, 52, k2), H[52,52],h(1, 52, k3)) ) ),h(1, 52, k2)) ) + Sum_{i0} ( $(h(1, 52, i0), ( T( G(h(1, 52, k3), Y[52,52],h(1, 52, i0)) ) Kro T( G(h(1, 52, k2), H[52,52],h(1, 52, k3)) ) ),h(1, 52, k2)) ) ) ) ) ) + Sum_{k2} ( ( Sum_{i0} ( $(h(1, 52, i0), ( G(h(1, 52, i0), Y[52,52],h(1, 52, 51)) Kro T( G(h(1, 52, k2), H[52,52],h(1, 52, 51)) ) ),h(1, 52, k2)) ) + $(h(1, 52, 51), ( G(h(1, 52, 51), Y[52,52],h(1, 52, 51)) Kro T( G(h(1, 52, k2), H[52,52],h(1, 52, 51)) ) ),h(1, 52, k2)) ) ) )


  for( int k2 = 0; k2 <= 51; k2++ ) {

    // 1-BLAC: (1x1)^T
    trg269[0] = H[52*k2];

    // 1-BLAC: 1x1 Kro 1x1
    M2[k2] = Y[0] * trg269[0];

    // 1-BLAC: (1x1)^T
    trg273[0] = H[52*k2];

    for( int i0 = 1; i0 <= 51; i0++ ) {

      // 1-BLAC: (1x1)^T
      trg272[0] = Y[i0];

      // 1-BLAC: (1x1)^T
      trg273[0] = H[52*k2];

      // 1-BLAC: 1x1 Kro 1x1
      M2[52*i0 + k2] = trg272[0] * trg273[0];
    }
  }


  for( int k3 = 1; k3 <= 50; k3++ ) {

    for( int k2 = 0; k2 <= 51; k2++ ) {

      // 1-BLAC: (1x1)^T
      trg280[0] = H[52*k2 + k3];

      for( int i0 = 0; i0 <= k3 - 1; i0++ ) {

        // 1-BLAC: (1x1)^T
        trg280[0] = H[52*k2 + k3];

        // 1-BLAC: 1x1 Kro 1x1
        kr281[0] = Y[52*i0 + k3] * trg280[0];

        // 1-BLAC: 1x1 + 1x1
        M2[52*i0 + k2] = M2[52*i0 + k2] + kr281[0];
      }

      // 1-BLAC: (1x1)^T
      trg285[0] = H[52*k2 + k3];

      // 1-BLAC: 1x1 Kro 1x1
      kr286[0] = Y[53*k3] * trg285[0];

      // 1-BLAC: 1x1 + 1x1
      M2[k2 + 52*k3] = M2[k2 + 52*k3] + kr286[0];

      // 1-BLAC: (1x1)^T
      trg289[0] = H[52*k2 + k3];

      for( int i0 = k3 + 1; i0 <= 51; i0++ ) {

        // 1-BLAC: (1x1)^T
        trg288[0] = Y[i0 + 52*k3];

        // 1-BLAC: (1x1)^T
        trg289[0] = H[52*k2 + k3];

        // 1-BLAC: 1x1 Kro 1x1
        kr290[0] = trg288[0] * trg289[0];

        // 1-BLAC: 1x1 + 1x1
        M2[52*i0 + k2] = M2[52*i0 + k2] + kr290[0];
      }
    }
  }


  for( int k2 = 0; k2 <= 51; k2++ ) {

    // 1-BLAC: (1x1)^T
    trg298[0] = H[52*k2 + 51];

    for( int i0 = 0; i0 <= 50; i0++ ) {

      // 1-BLAC: (1x1)^T
      trg298[0] = H[52*k2 + 51];

      // 1-BLAC: 1x1 Kro 1x1
      kr299[0] = Y[52*i0 + 51] * trg298[0];

      // 1-BLAC: 1x1 + 1x1
      M2[52*i0 + k2] = M2[52*i0 + k2] + kr299[0];
    }

    // 1-BLAC: (1x1)^T
    trg303[0] = H[52*k2 + 51];

    // 1-BLAC: 1x1 Kro 1x1
    kr304[0] = Y[2703] * trg303[0];

    // 1-BLAC: 1x1 + 1x1
    M2[k2 + 2652] = M2[k2 + 2652] + kr304[0];
  }


  // Generating : M3[52,52] = ( ( S(h(1, 52, 0), ( ( G(h(1, 52, 0), M1[52,52],h(1, 52, 0)) Kro T( G(h(1, 52, 0), H[52,52],h(1, 52, 0)) ) ) + G(h(1, 52, 0), R[52,52],h(1, 52, 0)) ),h(1, 52, 0)) + Sum_{k2} ( ( Sum_{i0} ( S(h(1, 52, i0), ( ( G(h(1, 52, i0), M1[52,52],h(1, 52, 0)) Kro T( G(h(1, 52, k2), H[52,52],h(1, 52, 0)) ) ) + G(h(1, 52, i0), R[52,52],h(1, 52, k2)) ),h(1, 52, k2)) ) + S(h(1, 52, k2), ( ( G(h(1, 52, k2), M1[52,52],h(1, 52, 0)) Kro T( G(h(1, 52, k2), H[52,52],h(1, 52, 0)) ) ) + G(h(1, 52, k2), R[52,52],h(1, 52, k2)) ),h(1, 52, k2)) ) ) ) + Sum_{k3} ( ( $(h(1, 52, 0), ( G(h(1, 52, 0), M1[52,52],h(1, 52, k3)) Kro T( G(h(1, 52, 0), H[52,52],h(1, 52, k3)) ) ),h(1, 52, 0)) + Sum_{k2} ( ( Sum_{i0} ( $(h(1, 52, i0), ( G(h(1, 52, i0), M1[52,52],h(1, 52, k3)) Kro T( G(h(1, 52, k2), H[52,52],h(1, 52, k3)) ) ),h(1, 52, k2)) ) + $(h(1, 52, k2), ( G(h(1, 52, k2), M1[52,52],h(1, 52, k3)) Kro T( G(h(1, 52, k2), H[52,52],h(1, 52, k3)) ) ),h(1, 52, k2)) ) ) ) ) )

  // 1-BLAC: (1x1)^T
  trg312[0] = H[0];

  // 1-BLAC: 1x1 Kro 1x1
  kr313[0] = M1[0] * trg312[0];

  // 1-BLAC: 1x1 + 1x1
  M3[0] = kr313[0] + R[0];


  for( int k2 = 1; k2 <= 51; k2++ ) {

    // 1-BLAC: (1x1)^T
    trg318[0] = H[52*k2];

    for( int i0 = 0; i0 <= k2 - 1; i0++ ) {

      // 1-BLAC: (1x1)^T
      trg318[0] = H[52*k2];

      // 1-BLAC: 1x1 Kro 1x1
      kr319[0] = M1[52*i0] * trg318[0];

      // 1-BLAC: 1x1 + 1x1
      M3[52*i0 + k2] = kr319[0] + R[52*i0 + k2];
    }

    // 1-BLAC: (1x1)^T
    trg325[0] = H[52*k2];

    // 1-BLAC: 1x1 Kro 1x1
    kr326[0] = M1[52*k2] * trg325[0];

    // 1-BLAC: 1x1 + 1x1
    M3[53*k2] = kr326[0] + R[53*k2];
  }


  for( int k3 = 1; k3 <= 51; k3++ ) {

    // 1-BLAC: (1x1)^T
    trg333[0] = H[k3];

    // 1-BLAC: 1x1 Kro 1x1
    kr334[0] = M1[k3] * trg333[0];

    // 1-BLAC: 1x1 + 1x1
    M3[0] = M3[0] + kr334[0];

    for( int k2 = 1; k2 <= 51; k2++ ) {

      // 1-BLAC: (1x1)^T
      trg337[0] = H[52*k2 + k3];

      for( int i0 = 0; i0 <= k2 - 1; i0++ ) {

        // 1-BLAC: (1x1)^T
        trg337[0] = H[52*k2 + k3];

        // 1-BLAC: 1x1 Kro 1x1
        kr338[0] = M1[52*i0 + k3] * trg337[0];

        // 1-BLAC: 1x1 + 1x1
        M3[52*i0 + k2] = M3[52*i0 + k2] + kr338[0];
      }

      // 1-BLAC: (1x1)^T
      trg342[0] = H[52*k2 + k3];

      // 1-BLAC: 1x1 Kro 1x1
      kr343[0] = M1[52*k2 + k3] * trg342[0];

      // 1-BLAC: 1x1 + 1x1
      M3[53*k2] = M3[53*k2] + kr343[0];
    }
  }


  // Generating : U[52,52] = S(h(1, 52, 0), Sqrt( G(h(1, 52, 0), U[52,52],h(1, 52, 0)) ),h(1, 52, 0))

  // 1-BLAC: sqrt(1x1)
  M3[0] = sqrt(M3[0]);

  // Generating : U[52,52] = S(h(1, 52, 0), ( G(h(1, 52, 0), U[52,52],h(1, 52, 1)) Div G(h(1, 52, 0), U[52,52],h(1, 52, 0)) ),h(1, 52, 1))

  // 1-BLAC: 1x1 / 1x1
  M3[1] = M3[1] / M3[0];

  // Generating : U[52,52] = S(h(1, 52, 1), ( G(h(1, 52, 1), M4[52,52],h(1, 52, 1)) - ( T( G(h(1, 52, 0), U[52,52],h(1, 52, 1)) ) Kro G(h(1, 52, 0), U[52,52],h(1, 52, 1)) ) ),h(1, 52, 1))

  // 1-BLAC: (1x1)^T
  trg368[0] = M3[1];

  // 1-BLAC: 1x1 Kro 1x1
  kr371[0] = trg368[0] * M3[1];

  // 1-BLAC: 1x1 - 1x1
  M3[53] = M3[53] - kr371[0];

  // Generating : U[52,52] = S(h(1, 52, 1), Sqrt( G(h(1, 52, 1), U[52,52],h(1, 52, 1)) ),h(1, 52, 1))

  // 1-BLAC: sqrt(1x1)
  M3[53] = sqrt(M3[53]);


  for( int fi35 = 2; fi35 <= 51; fi35++ ) {

    for( int fi60 = 0; fi60 <= fi35 - 2; fi60++ ) {

      // Generating : U[52,52] = S(h(1, 52, fi60), ( G(h(1, 52, fi60), U[52,52],h(1, 52, fi35)) Div G(h(1, 52, fi60), U[52,52],h(1, 52, fi60)) ),h(1, 52, fi35))

      // 1-BLAC: 1x1 / 1x1
      M3[fi35 + 52*fi60] = M3[fi35 + 52*fi60] / M3[53*fi60];

      // Generating : U[52,52] = Sum_{k3} ( S(h(1, 52, fi60 + k3 + 1), ( G(h(1, 52, fi60 + k3 + 1), U[52,52],h(1, 52, fi35)) - ( T( G(h(1, 52, fi60), U[52,52],h(1, 52, fi60 + k3 + 1)) ) Kro G(h(1, 52, fi60), U[52,52],h(1, 52, fi35)) ) ),h(1, 52, fi35)) )

      for( int k3 = 0; k3 <= fi35 - fi60 - 2; k3++ ) {

        // 1-BLAC: (1x1)^T
        trg392[0] = M3[53*fi60 + k3 + 1];

        // 1-BLAC: 1x1 Kro 1x1
        kr395[0] = trg392[0] * M3[fi35 + 52*fi60];

        // 1-BLAC: 1x1 - 1x1
        M3[fi35 + 52*fi60 + 52*k3 + 52] = M3[fi35 + 52*fi60 + 52*k3 + 52] - kr395[0];
      }
    }

    // Generating : U[52,52] = S(h(1, 52, Max(0, fi35 - 1)), ( G(h(1, 52, Max(0, fi35 - 1)), U[52,52],h(1, 52, fi35)) Div G(h(1, 52, Max(0, fi35 - 1)), U[52,52],h(1, 52, Max(0, fi35 - 1))) ),h(1, 52, fi35))

    // 1-BLAC: 1x1 / 1x1
    M3[fi35 + 52*Max(0, fi35 - 1)] = M3[fi35 + 52*Max(0, fi35 - 1)] / M3[53*Max(0, fi35 - 1)];

    // Generating : U[52,52] = ( S(h(1, 52, fi35), ( G(h(1, 52, fi35), M4[52,52],h(1, 52, fi35)) - ( T( G(h(1, 52, 0), U[52,52],h(1, 52, fi35)) ) Kro G(h(1, 52, 0), U[52,52],h(1, 52, fi35)) ) ),h(1, 52, fi35)) + Sum_{k3} ( -$(h(1, 52, fi35), ( T( G(h(1, 52, k3), U[52,52],h(1, 52, fi35)) ) Kro G(h(1, 52, k3), U[52,52],h(1, 52, fi35)) ),h(1, 52, fi35)) ) )

    // 1-BLAC: (1x1)^T
    trg412[0] = M3[fi35];

    // 1-BLAC: 1x1 Kro 1x1
    kr415[0] = trg412[0] * M3[fi35];

    // 1-BLAC: 1x1 - 1x1
    M3[53*fi35] = M3[53*fi35] - kr415[0];

    for( int k3 = 1; k3 <= fi35 - 1; k3++ ) {

      // 1-BLAC: (1x1)^T
      trg420[0] = M3[fi35 + 52*k3];

      // 1-BLAC: 1x1 Kro 1x1
      kr423[0] = trg420[0] * M3[fi35 + 52*k3];

      // 1-BLAC: 1x1 - 1x1
      M3[53*fi35] = M3[53*fi35] - kr423[0];
    }

    // Generating : U[52,52] = S(h(1, 52, fi35), Sqrt( G(h(1, 52, fi35), U[52,52],h(1, 52, fi35)) ),h(1, 52, fi35))

    // 1-BLAC: sqrt(1x1)
    M3[53*fi35] = sqrt(M3[53*fi35]);
  }


  for( int fi35 = 0; fi35 <= 50; fi35++ ) {

    // Generating : v2[52,1] = S(h(1, 52, fi35), ( G(h(1, 52, fi35), v2[52,1],h(1, 1, 0)) Div G(h(1, 52, fi35), U0[52,52],h(1, 52, fi35)) ),h(1, 1, 0))

    // 1-BLAC: 1x1 / 1x1
    v0[fi35] = v0[fi35] / M3[53*fi35];

    // Generating : v2[52,1] = Sum_{k3} ( S(h(1, 52, fi35 + k3 + 1), ( G(h(1, 52, fi35 + k3 + 1), v2[52,1],h(1, 1, 0)) - ( T( G(h(1, 52, fi35), U0[52,52],h(1, 52, fi35 + k3 + 1)) ) Kro G(h(1, 52, fi35), v2[52,1],h(1, 1, 0)) ) ),h(1, 1, 0)) )

    for( int k3 = 0; k3 <= -fi35 + 50; k3++ ) {

      // 1-BLAC: (1x1)^T
      trg446[0] = M3[53*fi35 + k3 + 1];

      // 1-BLAC: 1x1 Kro 1x1
      kr449[0] = trg446[0] * v0[fi35];

      // 1-BLAC: 1x1 - 1x1
      v0[fi35 + k3 + 1] = v0[fi35 + k3 + 1] - kr449[0];
    }
  }


  // Generating : v2[52,1] = S(h(1, 52, 51), ( G(h(1, 52, 51), v2[52,1],h(1, 1, 0)) Div G(h(1, 52, 51), U0[52,52],h(1, 52, 51)) ),h(1, 1, 0))

  // 1-BLAC: 1x1 / 1x1
  v0[51] = v0[51] / M3[2703];


  for( int fi35 = 0; fi35 <= 50; fi35++ ) {

    // Generating : v4[52,1] = S(h(1, 52, -fi35 + 51), ( G(h(1, 52, -fi35 + 51), v4[52,1],h(1, 1, 0)) Div G(h(1, 52, -fi35 + 51), U0[52,52],h(1, 52, -fi35 + 51)) ),h(1, 1, 0))

    // 1-BLAC: 1x1 / 1x1
    v0[-fi35 + 51] = v0[-fi35 + 51] / M3[-53*fi35 + 2703];

    // Generating : v4[52,1] = Sum_{k3} ( S(h(1, 52, k3), ( G(h(1, 52, k3), v4[52,1],h(1, 1, 0)) - ( G(h(1, 52, k3), U0[52,52],h(1, 52, -fi35 + 51)) Kro G(h(1, 52, -fi35 + 51), v4[52,1],h(1, 1, 0)) ) ),h(1, 1, 0)) )

    for( int k3 = 0; k3 <= -fi35 + 50; k3++ ) {

      // 1-BLAC: 1x1 Kro 1x1
      kr477[0] = M3[-fi35 + 52*k3 + 51] * v0[-fi35 + 51];

      // 1-BLAC: 1x1 - 1x1
      v0[k3] = v0[k3] - kr477[0];
    }
  }


  // Generating : v4[52,1] = S(h(1, 52, 0), ( G(h(1, 52, 0), v4[52,1],h(1, 1, 0)) Div G(h(1, 52, 0), U0[52,52],h(1, 52, 0)) ),h(1, 1, 0))

  // 1-BLAC: 1x1 / 1x1
  v0[0] = v0[0] / M3[0];


  for( int fi35 = 0; fi35 <= 50; fi35++ ) {

    for( int fi60 = 0; fi60 <= 51; fi60++ ) {

      // Generating : M6[52,52] = S(h(1, 52, fi35), ( G(h(1, 52, fi35), M6[52,52],h(1, 52, fi60)) Div G(h(1, 52, fi35), U0[52,52],h(1, 52, fi35)) ),h(1, 52, fi60))

      // 1-BLAC: 1x1 / 1x1
      M1[52*fi35 + fi60] = M1[52*fi35 + fi60] / M3[53*fi35];
    }

    // Generating : M6[52,52] = Sum_{k3} ( Sum_{k2} ( S(h(1, 52, fi35 + k2 + 1), ( G(h(1, 52, fi35 + k2 + 1), M6[52,52],h(1, 52, k3)) - ( T( G(h(1, 52, fi35), U0[52,52],h(1, 52, fi35 + k2 + 1)) ) Kro G(h(1, 52, fi35), M6[52,52],h(1, 52, k3)) ) ),h(1, 52, k3)) ) )

    for( int k3 = 0; k3 <= 51; k3++ ) {

      for( int k2 = 0; k2 <= -fi35 + 50; k2++ ) {

        // 1-BLAC: (1x1)^T
        trg502[0] = M3[53*fi35 + k2 + 1];

        // 1-BLAC: 1x1 Kro 1x1
        kr505[0] = trg502[0] * M1[52*fi35 + k3];

        // 1-BLAC: 1x1 - 1x1
        M1[52*fi35 + 52*k2 + k3 + 52] = M1[52*fi35 + 52*k2 + k3 + 52] - kr505[0];
      }
    }
  }


  for( int fi35 = 0; fi35 <= 51; fi35++ ) {

    // Generating : M6[52,52] = S(h(1, 52, 51), ( G(h(1, 52, 51), M6[52,52],h(1, 52, fi35)) Div G(h(1, 52, 51), U0[52,52],h(1, 52, 51)) ),h(1, 52, fi35))

    // 1-BLAC: 1x1 / 1x1
    M1[fi35 + 2652] = M1[fi35 + 2652] / M3[2703];
  }


  for( int fi35 = 0; fi35 <= 50; fi35++ ) {

    for( int fi60 = 0; fi60 <= 51; fi60++ ) {

      // Generating : M8[52,52] = S(h(1, 52, -fi35 + 51), ( G(h(1, 52, -fi35 + 51), M8[52,52],h(1, 52, fi60)) Div G(h(1, 52, -fi35 + 51), U0[52,52],h(1, 52, -fi35 + 51)) ),h(1, 52, fi60))

      // 1-BLAC: 1x1 / 1x1
      M1[-52*fi35 + fi60 + 2652] = M1[-52*fi35 + fi60 + 2652] / M3[-53*fi35 + 2703];
    }

    // Generating : M8[52,52] = Sum_{k3} ( Sum_{k2} ( S(h(1, 52, k2), ( G(h(1, 52, k2), M8[52,52],h(1, 52, k3)) - ( G(h(1, 52, k2), U0[52,52],h(1, 52, -fi35 + 51)) Kro G(h(1, 52, -fi35 + 51), M8[52,52],h(1, 52, k3)) ) ),h(1, 52, k3)) ) )

    for( int k3 = 0; k3 <= 51; k3++ ) {

      for( int k2 = 0; k2 <= -fi35 + 50; k2++ ) {

        // 1-BLAC: 1x1 Kro 1x1
        kr534[0] = M3[-fi35 + 52*k2 + 51] * M1[-52*fi35 + k3 + 2652];

        // 1-BLAC: 1x1 - 1x1
        M1[52*k2 + k3] = M1[52*k2 + k3] - kr534[0];
      }
    }
  }


  for( int fi35 = 0; fi35 <= 51; fi35++ ) {

    // Generating : M8[52,52] = S(h(1, 52, 0), ( G(h(1, 52, 0), M8[52,52],h(1, 52, fi35)) Div G(h(1, 52, 0), U0[52,52],h(1, 52, 0)) ),h(1, 52, fi35))

    // 1-BLAC: 1x1 / 1x1
    M1[fi35] = M1[fi35] / M3[0];
  }


  // Generating : x[52,1] = ( Sum_{k2} ( S(h(1, 52, k2), ( G(h(1, 52, k2), y[52,1],h(1, 1, 0)) + ( G(h(1, 52, k2), M2[52,52],h(1, 52, 0)) Kro G(h(1, 52, 0), v0[52,1],h(1, 1, 0)) ) ),h(1, 1, 0)) ) + Sum_{k3} ( Sum_{k2} ( $(h(1, 52, k2), ( G(h(1, 52, k2), M2[52,52],h(1, 52, k3)) Kro G(h(1, 52, k3), v0[52,1],h(1, 1, 0)) ),h(1, 1, 0)) ) ) )


  for( int k2 = 0; k2 <= 51; k2++ ) {

    // 1-BLAC: 1x1 Kro 1x1
    kr552[0] = M2[52*k2] * v0[0];

    // 1-BLAC: 1x1 + 1x1
    x[k2] = y[k2] + kr552[0];
  }


  for( int k3 = 1; k3 <= 51; k3++ ) {

    for( int k2 = 0; k2 <= 51; k2++ ) {

      // 1-BLAC: 1x1 Kro 1x1
      kr558[0] = M2[52*k2 + k3] * v0[k3];

      // 1-BLAC: 1x1 + 1x1
      x[k2] = x[k2] + kr558[0];
    }
  }


  // Generating : P[52,52] = ( ( S(h(1, 52, 0), ( G(h(1, 52, 0), Y[52,52],h(1, 52, 0)) - ( G(h(1, 52, 0), M2[52,52],h(1, 52, 0)) Kro G(h(1, 52, 0), M1[52,52],h(1, 52, 0)) ) ),h(1, 52, 0)) + Sum_{k2} ( ( Sum_{i0} ( S(h(1, 52, i0), ( G(h(1, 52, i0), Y[52,52],h(1, 52, k2)) - ( G(h(1, 52, i0), M2[52,52],h(1, 52, 0)) Kro G(h(1, 52, 0), M1[52,52],h(1, 52, k2)) ) ),h(1, 52, k2)) ) + S(h(1, 52, k2), ( G(h(1, 52, k2), Y[52,52],h(1, 52, k2)) - ( G(h(1, 52, k2), M2[52,52],h(1, 52, 0)) Kro G(h(1, 52, 0), M1[52,52],h(1, 52, k2)) ) ),h(1, 52, k2)) ) ) ) + Sum_{k3} ( ( -$(h(1, 52, 0), ( G(h(1, 52, 0), M2[52,52],h(1, 52, k3)) Kro G(h(1, 52, k3), M1[52,52],h(1, 52, 0)) ),h(1, 52, 0)) + Sum_{k2} ( ( Sum_{i0} ( -$(h(1, 52, i0), ( G(h(1, 52, i0), M2[52,52],h(1, 52, k3)) Kro G(h(1, 52, k3), M1[52,52],h(1, 52, k2)) ),h(1, 52, k2)) ) + -$(h(1, 52, k2), ( G(h(1, 52, k2), M2[52,52],h(1, 52, k3)) Kro G(h(1, 52, k3), M1[52,52],h(1, 52, k2)) ),h(1, 52, k2)) ) ) ) ) )

  // 1-BLAC: 1x1 Kro 1x1
  kr567[0] = M2[0] * M1[0];

  // 1-BLAC: 1x1 - 1x1
  P[0] = Y[0] - kr567[0];


  for( int k2 = 1; k2 <= 51; k2++ ) {

    for( int i0 = 0; i0 <= k2 - 1; i0++ ) {

      // 1-BLAC: 1x1 Kro 1x1
      kr573[0] = M2[52*i0] * M1[k2];

      // 1-BLAC: 1x1 - 1x1
      P[52*i0 + k2] = Y[52*i0 + k2] - kr573[0];
    }

    // 1-BLAC: 1x1 Kro 1x1
    kr580[0] = M2[52*k2] * M1[k2];

    // 1-BLAC: 1x1 - 1x1
    P[53*k2] = Y[53*k2] - kr580[0];
  }


  for( int k3 = 1; k3 <= 51; k3++ ) {

    // 1-BLAC: 1x1 Kro 1x1
    kr587[0] = M2[k3] * M1[52*k3];

    // 1-BLAC: 1x1 - 1x1
    P[0] = P[0] - kr587[0];

    for( int k2 = 1; k2 <= 51; k2++ ) {

      for( int i0 = 0; i0 <= k2 - 1; i0++ ) {

        // 1-BLAC: 1x1 Kro 1x1
        kr592[0] = M2[52*i0 + k3] * M1[k2 + 52*k3];

        // 1-BLAC: 1x1 - 1x1
        P[52*i0 + k2] = P[52*i0 + k2] - kr592[0];
      }

      // 1-BLAC: 1x1 Kro 1x1
      kr598[0] = M2[52*k2 + k3] * M1[k2 + 52*k3];

      // 1-BLAC: 1x1 - 1x1
      P[53*k2] = P[53*k2] - kr598[0];
    }
  }

}
