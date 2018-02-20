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

#include "params.h"

#include "Eigen/Dense"


using namespace std;
using namespace Eigen;

typedef Map< Matrix<FLOAT, PARAM0, PARAM0, RowMajor> > MapMatL;

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


inline void build(FLOAT ** L, FLOAT ** LI)
{
  srand(time(NULL));

  *L = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));
  *LI = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));

  rands(*L, PARAM0, PARAM0);

  for (int i = 0; i < PARAM0; ++i)
	  (*L)[i*PARAM0+i] += PARAM0;

}

inline void destroy(FLOAT * L, FLOAT * LI)
{
  aligned_free(L);
  aligned_free(LI);
}

long validate(FLOAT const * L, FLOAT const * LI, double threshold)
{
  bool success = true;
  std::vector<string> errMsgs;

  // With error func
    double err = func_err(LI, L);
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

static __attribute__((noinline)) void kernel(const MapMatL& L, MapMatL& LI) {
	LI = L.inverse();
}


int test()
{

  FLOAT * aL, * aLI;
  long retCode = 0;

  build(&aL, &aLI);

  MapMatL L(aL), LI(aLI);

  L = L.triangularView<Lower>();

#ifdef VALIDATE
  kernel(L, LI);
  retCode = validate(aL, aLI, ERRTHRESH);

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
		kernel(L, LI);
#endif

#ifndef ERM
  myInt64 start, end, overhead, overhead_tsc;
  double cycles = 0.;
  size_t num_runs = RUNS, multiplier = 1;

  init_tsc();
  overhead_tsc = get_tsc_overhead();

  do{
	  num_runs = num_runs * multiplier;
	  overhead = overhead_tsc;

      start = start_tsc();
      for(size_t i = 0; i < num_runs; i++) {
    	  kernel(L, LI);
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

  for (int k = 0; k < Rep; k++) {

      start = start_tsc();
      for (int i = 0; i < num_runs; ++i) {
    	  kernel(L, LI);
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

  destroy(aL, aLI);

  return retCode;
}
