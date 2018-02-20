/*
 * ltrtri_tester.h
 *
 * Computes L = L^-1
 *
 *  Created on: June 6, 2012
 *      Author: danieles
 */

#pragma once

#include <iostream>
#include <sstream>
#include <ctime>
#include <list>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <algorithm>

#ifdef TEST
#ifndef ERM
#include "tsc.h"
#endif
#endif

#include "helpers.h"
#include "CommonDefs.h"

#include "kernels/ltrtri_kernel.h"

#if TYPE == FLT
#define FCALL LAPACKE_strtri
#else
#define FCALL LAPACKE_dtrtri
#endif

#define OW

/*
 * PARAM0 -> M
 */

double max_norm(FLOAT const * M) {

	double res = M[0];

	for (int i = 0; i < PARAM0; ++i)
		for (int j = 0; j <=i; ++j)
			if (M[i*PARAM0+j] > res)
				res = M[i*PARAM0+j];

	return res;
}

double frob_norm(FLOAT const * M) {

	double res = 0;

	for (int i = 0; i < PARAM0; ++i)
		for (int j = 0; j <=i; ++j)
			res += M[i*PARAM0+j]*M[i*PARAM0+j];

	return sqrt(res);
}

#define NORM frob_norm

double func_err(FLOAT const * X, FLOAT const * L) {

	std::vector<FLOAT> tXL(PARAM0*PARAM0, 0);
	std::vector<FLOAT> tLX(PARAM0*PARAM0, 0);
	double xlmi, lxmi, l;

	for (int i = 0; i < PARAM0; ++i) {
		for (int j = 0; j <= i; ++j) {
			for (int k = j; k <= i; ++k) {
				tXL[i*PARAM0+j] += X[i*PARAM0+k]*L[k*PARAM0+j];
				tLX[i*PARAM0+j] += L[i*PARAM0+k]*X[k*PARAM0+j];
			}
		}
	}

	for (int i = 0; i < PARAM0; ++i) {
		tXL[i*PARAM0+i] -= 1;
		tLX[i*PARAM0+i] -= 1;
	}

	xlmi = NORM(&tXL[0]);
	lxmi = NORM(&tLX[0]);
	l    = NORM(L);

	using std::max;
	return max(xlmi/l, lxmi/l);
}

#ifndef OW

inline void build(FLOAT ** L, FLOAT ** X)
{
  srand(time(NULL));

  *L = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));
  *X = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));

  rands(*L, PARAM0, PARAM0);

  for (int i = 0; i < PARAM0; ++i)
	  (*L)[i*PARAM0+i] += PARAM0;

}

inline void destroy(FLOAT * L, FLOAT * X)
{
  aligned_free(L);
  aligned_free(X);
}

long validate(FLOAT const * L, FLOAT const * X, double threshold)
{
  bool success = true;
  std::vector<string> errMsgs;

//  std::vector<FLOAT> tL(L, L+PARAM0*PARAM0);
//  long retvalue = (long)FCALL(LAPACK_ROW_MAJOR, 'L', 'N', PARAM0, &tL[0], PARAM0);

//  if (retvalue > 0) {
//	  cout << "The "<< retvalue << "-th diagonal element of L is zero, L is singular, and the inversion could not be completed." << endl;
//	  return retvalue;
//  } else if (retvalue < 0) {
//	  cout << "Parameter "<< retvalue << " had an illegal value." << endl;
//	  return retvalue;
//  }

//  for (int i = 0; i < PARAM0; ++i) {
//	  for (int j = 0; j <= i; ++j) {
//		double err, den = fabs(tL[i*PARAM0+j]);
//		if(den > 0.) {
//		  err = fabs(X[i*PARAM0+j] - tL[i*PARAM0+j])/den;
//		}else {
//		  err = fabs(X[i*PARAM0+j] - tL[i*PARAM0+j]);
//		}
//		if(err > threshold) {
//		  success = false;
//		  stringstream ss;
//		  ss << "Error at (" << i << ","<< j << "): ";
//		  ss << "X = " << X[i*PARAM0+j] << "\t-- tL = " << tL[i*PARAM0+j] << "\t-- Err = " << err << endl;
//		  errMsgs.push_back(ss.str());
//		}
//	  }
//  }

// With error func
  double err = func_err(X, L);
  if (err > threshold) {
	  success = false;
	  stringstream ss;
	  ss << "Error = " << err << endl;
	  errMsgs.push_back(ss.str());
  }

//  //Element-wise residual
//  std::vector<FLOAT> tXL(PARAM0*PARAM0, 0);
//  std::vector<FLOAT> tLX(PARAM0*PARAM0, 0);
//
//  for (int i = 0; i < PARAM0; ++i) {
//	  for (int j = 0; j <= i; ++j) {
//		  for (int k = j; k <= i; ++k) {
//			  tXL[i*PARAM0+j] += X[i*PARAM0+k]*L[k*PARAM0+j];
//			  tLX[i*PARAM0+j] += L[i*PARAM0+k]*X[k*PARAM0+j];
//		  }
//	  }
//  }
//
//  for (int i = 0; i < PARAM0; ++i) {
//	  tXL[i*PARAM0+i] -= 1;
//	  tLX[i*PARAM0+i] -= 1;
//  }
//
//  for (int i = 0; i < PARAM0; ++i) {
//	  for (int j = 0; j <= i; ++j) {
//		  double err;
//		  using std::max;
//		  err = max(tXL[i*PARAM0+j], tLX[i*PARAM0+j]);
//
//		  if(err > threshold) {
//			  success = false;
//			  stringstream ss;
//			  ss << "Error at (" << i << ","<< j << "): ";
//			  ss << "\t-- Err = " << err << endl;
//			  errMsgs.push_back(ss.str());
//		  }
//	  }
//  }
//
  if(!success) {
    for(std::vector<string>::const_iterator i = errMsgs.begin(); i != errMsgs.end(); i++)
      cout << *i;
  }

  return !success;

}
#else

inline void build(FLOAT ** initL, FLOAT ** L)
{
  srand(time(NULL));

  *L = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));
  *initL = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));

  rands(*L, PARAM0, PARAM0);

  for (int i = 0; i < PARAM0; ++i)
	  (*L)[i*PARAM0+i] += PARAM0;

  memcpy(*initL, *L, PARAM0*PARAM0*sizeof(FLOAT));

}

inline void destroy(FLOAT * initL, FLOAT * L)
{
  aligned_free(L);
  aligned_free(initL);
}

long validate(FLOAT const * initL, FLOAT const * L, double threshold)
{
  bool success = true;
  std::vector<string> errMsgs;

  // With error func
    double err = func_err(L, initL);
    if (err > threshold) {
  	  success = false;
  	  stringstream ss;
  	  ss << "Error = " << err << endl;
  	  errMsgs.push_back(ss.str());
    }

  if(!success) {
    for(std::vector<string>::const_iterator i = errMsgs.begin(); i != errMsgs.end(); i++)
      cout << *i;
  }

  return !success;

}

#endif

int test()
{

#ifndef OW
  FLOAT * L, * X;
#else
  FLOAT * L, * initL;
#endif
  long retCode = 0;

#ifndef OW
  build(&L, &X);
#else
  build(&initL, &L);
#endif

#ifdef VALIDATE
#ifndef OW
  kernel(L, X);
  retCode = validate(L,X, ERRTHRESH);
#else
  kernel(L);
  retCode = validate(initL, L, ERRTHRESH);
#endif
  if (retCode > 0) {
	  cout << "Validation failed." << endl;
	  return retCode;
  }
#endif
  //Cache warm-up
  // RDTSCP reads ts register guaranteeing that the execution of all the code
  // we wanted to measure is completed. This way we avoid including the
  // execution of a CPUID in between. The last CPUID guarantees no other
  // instruction can be scheduled before it (and so also before RDTSCP)
#ifdef TEST

#ifdef ERM
	for(int i=0; i<2; i++)
#ifndef OW
		kernel(L, X);
#else
		kernel(L);
#endif
#endif

#ifndef ERM
  myInt64 start, end, overhead, overhead_tsc;
  double cycles = 0.;
  size_t num_runs = RUNS, multiplier = 1;

  init_tsc();
  overhead_tsc = get_tsc_overhead();

  do{
      num_runs = num_runs * multiplier;
#ifdef OW
      start = start_tsc();
      for(size_t i = 0; i < num_runs; i++) {
    	  std::vector<FLOAT> tL(initL, initL+PARAM0*PARAM0);
      }
      end = stop_tsc(start);
      overhead = overhead_tsc + end;
#else
      overhead = overhead_tsc;
#endif
      start = start_tsc();
      for(size_t i = 0; i < num_runs; i++) {
#ifndef OW
    	  kernel(L, X);
#else
    	  std::vector<FLOAT> tL(initL, initL+PARAM0*PARAM0);
    	  kernel(&tL[0]);
#endif
      }
      end = stop_tsc(start);
      if (end > overhead)
          end -= overhead;

      cycles = (double) end;
      multiplier = ceil (  (CYCLES_REQUIRED) / (cycles)  + 1.0 );

  }while (multiplier > 2);

  list< double > cycleList, flopList;
  size_t Rep = NUMREP;

  double flops = (PARAM0*PARAM0*PARAM0)/3.;

#ifdef OW
  start = start_tsc();
  for(size_t i = 0; i < num_runs; i++) {
	  std::vector<FLOAT> tL(initL, initL+PARAM0*PARAM0);
  }
  end = stop_tsc(start);
  overhead = overhead_tsc + end;
#endif

  for (int k = 0; k < Rep; k++) {

      start = start_tsc();
      for (int i = 0; i < num_runs; ++i) {
#ifndef OW
    	  kernel(L, X);
#else
    	  std::vector<FLOAT> tL(initL, initL+PARAM0*PARAM0);
    	  kernel(&tL[0]);
#endif
      }
      end = stop_tsc(start);
      end -= overhead;
 
      cycles = ((double) end) / num_runs;

      cycleList.push_back(cycles);
      flopList.push_back(flops);

  }

  dumpList(cycleList, string(EXEC_PATH) + "/cycles.txt");
  dumpList(flopList, string(EXEC_PATH) + "/flops.txt");
#endif
#endif

#ifndef OW
  destroy(L, X);
#else
  destroy(initL, L);
#endif

  return retCode;
}
