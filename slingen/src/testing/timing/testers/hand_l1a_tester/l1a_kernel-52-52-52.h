/*
 * l1a_kernel.h
 *
Decl { {u'A': SquaredMatrix[A, (52, 52), GenMatAccess], u'a': Scalar[a, (1, 1), GenMatAccess], u'b': Scalar[b, (1, 1), GenMatAccess], u'y1': Matrix[y1, (52, 1), GenMatAccess], u'y2': Matrix[y2, (52, 1), GenMatAccess], u'v1': Matrix[v1, (52, 1), GenMatAccess], u'v2': Matrix[v2, (52, 1), GenMatAccess], u't': Scalar[t, (1, 1), GenMatAccess], u'W': SquaredMatrix[W, (52, 52), GenMatAccess], u'y': Matrix[y, (52, 1), GenMatAccess], u'x': Matrix[x, (52, 1), GenMatAccess], u'x0': Matrix[x0, (52, 1), GenMatAccess], u'x1': Matrix[x1, (52, 1), GenMatAccess], u'z1': Matrix[z1, (52, 1), GenMatAccess], u'z2': Matrix[z2, (52, 1), GenMatAccess]} }
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ann: {}

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Entry 0:
Entry 0:
Eq: Tile( (1, 1), y1[52,1] ) = ( ( Tile( (1, 1), a[1,1] ) Kro Tile( (1, 1), v1[52,1] ) ) + ( Tile( (1, 1), t[1,1] ) Kro Tile( (1, 1), z1[52,1] ) ) )
Eq.ann: {}
Entry 1:
Eq: Tile( (1, 1), y2[52,1] ) = ( ( Tile( (1, 1), a[1,1] ) Kro Tile( (1, 1), v2[52,1] ) ) + ( Tile( (1, 1), t[1,1] ) Kro Tile( (1, 1), z2[52,1] ) ) )
Eq.ann: {}
Entry 2:
Eq: Tile( (1, 1), x1[52,1] ) = ( ( T( Tile( (1, 1), W[52,52] ) ) * Tile( (1, 1), y1[52,1] ) ) - ( T( Tile( (1, 1), A[52,52] ) ) * Tile( (1, 1), y2[52,1] ) ) )
Eq.ann: {}
Entry 3:
Eq: Tile( (1, 1), x[52,1] ) = ( Tile( (1, 1), x0[52,1] ) + ( Tile( (1, 1), b[1,1] ) Kro Tile( (1, 1), x1[52,1] ) ) )
Eq.ann: {}
Entry 4:
Eq: Tile( (1, 1), z1[52,1] ) = ( Tile( (1, 1), y1[52,1] ) - ( Tile( (1, 1), W[52,52] ) * Tile( (1, 1), x[52,1] ) ) )
Eq.ann: {}
Entry 5:
Eq: Tile( (1, 1), z2[52,1] ) = ( Tile( (1, 1), y2[52,1] ) - ( Tile( (1, 1), y[52,1] ) - ( Tile( (1, 1), A[52,52] ) * Tile( (1, 1), x[52,1] ) ) ) )
Eq.ann: {}
Entry 6:
Eq: Tile( (1, 1), v1[52,1] ) = ( ( Tile( (1, 1), a[1,1] ) Kro Tile( (1, 1), v1[52,1] ) ) + ( Tile( (1, 1), t[1,1] ) Kro Tile( (1, 1), z1[52,1] ) ) )
Eq.ann: {}
Entry 7:
Eq: Tile( (1, 1), v2[52,1] ) = ( ( Tile( (1, 1), a[1,1] ) Kro Tile( (1, 1), v2[52,1] ) ) + ( Tile( (1, 1), t[1,1] ) Kro Tile( (1, 1), z2[52,1] ) ) )
Eq.ann: {}
 *
 * Created on: 2017-08-15
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


static __attribute__((noinline)) void kernel(double a, double t, double const * W, double const * A, double const * x0, double b, double const * y, double * y1, double * v1, double * z1, double * y2, double * v2, double * z2, double * x1, double * x)
{
  double kr40[1];
  double kr43[1];
  double kr50[1];
  double kr53[1];
  double trg58[1];
  double kr60[1];
  double trg61[1];
  double kr63[1];
  double trg67[1];
  double kr69[1];
  double trg73[1];
  double kr75[1];
  double kr86[1];
  double kr94[1];
  double kr100[1];
  double kr111[1];
  double sub112[1];
  double kr118[1];
  double kr128[1];
  double kr131[1];
  double kr138[1];
  double kr141[1];


  // Generating : y1[52,1] = Sum_{i0} ( S(h(1, 52, i0), ( ( G(h(1, 1, 0), a[1,1],h(1, 1, 0)) Kro G(h(1, 52, i0), v1[52,1],h(1, 1, 0)) ) + ( G(h(1, 1, 0), t[1,1],h(1, 1, 0)) Kro G(h(1, 52, i0), z1[52,1],h(1, 1, 0)) ) ),h(1, 1, 0)) )


  for( int i0 = 0; i0 <= 51; i0++ ) {

    // 1-BLAC: 1x1 Kro 1x1
    kr40[0] = a * v1[i0];

    // 1-BLAC: 1x1 Kro 1x1
    kr43[0] = t * z1[i0];

    // 1-BLAC: 1x1 + 1x1
    y1[i0] = kr40[0] + kr43[0];
  }


  // Generating : y2[52,1] = Sum_{i0} ( S(h(1, 52, i0), ( ( G(h(1, 1, 0), a[1,1],h(1, 1, 0)) Kro G(h(1, 52, i0), v2[52,1],h(1, 1, 0)) ) + ( G(h(1, 1, 0), t[1,1],h(1, 1, 0)) Kro G(h(1, 52, i0), z2[52,1],h(1, 1, 0)) ) ),h(1, 1, 0)) )


  for( int i0 = 0; i0 <= 51; i0++ ) {

    // 1-BLAC: 1x1 Kro 1x1
    kr50[0] = a * v2[i0];

    // 1-BLAC: 1x1 Kro 1x1
    kr53[0] = t * z2[i0];

    // 1-BLAC: 1x1 + 1x1
    y2[i0] = kr50[0] + kr53[0];
  }


  // Generating : x1[52,1] = ( ( Sum_{k15} ( S(h(1, 52, k15), ( ( T( G(h(1, 52, 0), W[52,52],h(1, 52, k15)) ) Kro G(h(1, 52, 0), y1[52,1],h(1, 1, 0)) ) - ( T( G(h(1, 52, 0), A[52,52],h(1, 52, k15)) ) Kro G(h(1, 52, 0), y2[52,1],h(1, 1, 0)) ) ),h(1, 1, 0)) ) + Sum_{i6} ( Sum_{k15} ( $(h(1, 52, k15), ( T( G(h(1, 52, i6), W[52,52],h(1, 52, k15)) ) Kro G(h(1, 52, i6), y1[52,1],h(1, 1, 0)) ),h(1, 1, 0)) ) ) ) + Sum_{i0} ( Sum_{k15} ( -$(h(1, 52, k15), ( T( G(h(1, 52, i0), A[52,52],h(1, 52, k15)) ) Kro G(h(1, 52, i0), y2[52,1],h(1, 1, 0)) ),h(1, 1, 0)) ) ) )


  for( int k15 = 0; k15 <= 51; k15++ ) {

    // 1-BLAC: (1x1)^T
    trg58[0] = W[k15];

    // 1-BLAC: 1x1 Kro 1x1
    kr60[0] = trg58[0] * y1[0];

    // 1-BLAC: (1x1)^T
    trg61[0] = A[k15];

    // 1-BLAC: 1x1 Kro 1x1
    kr63[0] = trg61[0] * y2[0];

    // 1-BLAC: 1x1 - 1x1
    x1[k15] = kr60[0] - kr63[0];
  }


  for( int i6 = 1; i6 <= 51; i6++ ) {

    for( int k15 = 0; k15 <= 51; k15++ ) {

      // 1-BLAC: (1x1)^T
      trg67[0] = W[52*i6 + k15];

      // 1-BLAC: 1x1 Kro 1x1
      kr69[0] = trg67[0] * y1[i6];

      // 1-BLAC: 1x1 + 1x1
      x1[k15] = x1[k15] + kr69[0];
    }
  }


  for( int i0 = 1; i0 <= 51; i0++ ) {

    for( int k15 = 0; k15 <= 51; k15++ ) {

      // 1-BLAC: (1x1)^T
      trg73[0] = A[52*i0 + k15];

      // 1-BLAC: 1x1 Kro 1x1
      kr75[0] = trg73[0] * y2[i0];

      // 1-BLAC: 1x1 - 1x1
      x1[k15] = x1[k15] - kr75[0];
    }
  }


  // Generating : x[52,1] = Sum_{i0} ( S(h(1, 52, i0), ( G(h(1, 52, i0), x0[52,1],h(1, 1, 0)) + ( G(h(1, 1, 0), b[1,1],h(1, 1, 0)) Kro G(h(1, 52, i0), x1[52,1],h(1, 1, 0)) ) ),h(1, 1, 0)) )


  for( int i0 = 0; i0 <= 51; i0++ ) {

    // 1-BLAC: 1x1 Kro 1x1
    kr86[0] = b * x1[i0];

    // 1-BLAC: 1x1 + 1x1
    x[i0] = x0[i0] + kr86[0];
  }


  // Generating : z1[52,1] = ( Sum_{i6} ( S(h(1, 52, i6), ( G(h(1, 52, i6), y1[52,1],h(1, 1, 0)) - ( G(h(1, 52, i6), W[52,52],h(1, 52, 0)) Kro G(h(1, 52, 0), x[52,1],h(1, 1, 0)) ) ),h(1, 1, 0)) ) + Sum_{i0} ( Sum_{i6} ( -$(h(1, 52, i6), ( G(h(1, 52, i6), W[52,52],h(1, 52, i0)) Kro G(h(1, 52, i0), x[52,1],h(1, 1, 0)) ),h(1, 1, 0)) ) ) )


  for( int i6 = 0; i6 <= 51; i6++ ) {

    // 1-BLAC: 1x1 Kro 1x1
    kr94[0] = W[52*i6] * x[0];

    // 1-BLAC: 1x1 - 1x1
    z1[i6] = y1[i6] - kr94[0];
  }


  for( int i0 = 1; i0 <= 51; i0++ ) {

    for( int i6 = 0; i6 <= 51; i6++ ) {

      // 1-BLAC: 1x1 Kro 1x1
      kr100[0] = W[i0 + 52*i6] * x[i0];

      // 1-BLAC: 1x1 - 1x1
      z1[i6] = z1[i6] - kr100[0];
    }
  }


  // Generating : z2[52,1] = ( Sum_{i6} ( S(h(1, 52, i6), ( G(h(1, 52, i6), y2[52,1],h(1, 1, 0)) - ( G(h(1, 52, i6), y[52,1],h(1, 1, 0)) - ( G(h(1, 52, i6), A[52,52],h(1, 52, 0)) Kro G(h(1, 52, 0), x[52,1],h(1, 1, 0)) ) ) ),h(1, 1, 0)) ) + Sum_{i0} ( Sum_{i6} ( $(h(1, 52, i6), ( G(h(1, 52, i6), A[52,52],h(1, 52, i0)) Kro G(h(1, 52, i0), x[52,1],h(1, 1, 0)) ),h(1, 1, 0)) ) ) )


  for( int i6 = 0; i6 <= 51; i6++ ) {

    // 1-BLAC: 1x1 Kro 1x1
    kr111[0] = A[52*i6] * x[0];

    // 1-BLAC: 1x1 - 1x1
    sub112[0] = y[i6] - kr111[0];

    // 1-BLAC: 1x1 - 1x1
    z2[i6] = y2[i6] - sub112[0];
  }


  for( int i0 = 1; i0 <= 51; i0++ ) {

    for( int i6 = 0; i6 <= 51; i6++ ) {

      // 1-BLAC: 1x1 Kro 1x1
      kr118[0] = A[i0 + 52*i6] * x[i0];

      // 1-BLAC: 1x1 + 1x1
      z2[i6] = z2[i6] + kr118[0];
    }
  }


  // Generating : v1[52,1] = Sum_{i0} ( S(h(1, 52, i0), ( ( G(h(1, 1, 0), a[1,1],h(1, 1, 0)) Kro G(h(1, 52, i0), v1[52,1],h(1, 1, 0)) ) + ( G(h(1, 1, 0), t[1,1],h(1, 1, 0)) Kro G(h(1, 52, i0), z1[52,1],h(1, 1, 0)) ) ),h(1, 1, 0)) )


  for( int i0 = 0; i0 <= 51; i0++ ) {

    // 1-BLAC: 1x1 Kro 1x1
    kr128[0] = a * v1[i0];

    // 1-BLAC: 1x1 Kro 1x1
    kr131[0] = t * z1[i0];

    // 1-BLAC: 1x1 + 1x1
    v1[i0] = kr128[0] + kr131[0];
  }


  // Generating : v2[52,1] = Sum_{i0} ( S(h(1, 52, i0), ( ( G(h(1, 1, 0), a[1,1],h(1, 1, 0)) Kro G(h(1, 52, i0), v2[52,1],h(1, 1, 0)) ) + ( G(h(1, 1, 0), t[1,1],h(1, 1, 0)) Kro G(h(1, 52, i0), z2[52,1],h(1, 1, 0)) ) ),h(1, 1, 0)) )


  for( int i0 = 0; i0 <= 51; i0++ ) {

    // 1-BLAC: 1x1 Kro 1x1
    kr138[0] = a * v2[i0];

    // 1-BLAC: 1x1 Kro 1x1
    kr141[0] = t * z2[i0];

    // 1-BLAC: 1x1 + 1x1
    v2[i0] = kr138[0] + kr141[0];
  }

}
