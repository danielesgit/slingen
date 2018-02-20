/*
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

#include "params.h"

#ifdef TEST
#ifndef ERM
#include "tsc.h"
#endif
#endif

#include "helpers.h"
#include "CommonDefs.h"

/*
 * PARAM0 -> M
 */

extern "C" {
  // void dtrsyl_(const char *tranA, const char *tranB, const int *isgn,
  //              const int *m, const int *n, const double *A, const int *ldA, const double *B, const int *ldB,
  //              double *C, const int *ldC, double *scale, int *info);
  void dtrtri_(const char *uplo, const char *diag, const int *n, double *a, const int *lda, int *info);
};

#define FCALL dtrtri_

double frob_norm_L(FLOAT const * M) {

	double res = 0;
        //Col-wise access
	for (int i = 0; i < PARAM0; ++i)
		for (int j = i; j <PARAM0; ++j)
			res += M[i*PARAM0+j]*M[i*PARAM0+j];

	return sqrt(res);
}

#define NORM frob_norm_L

double func_err(FLOAT const * X, FLOAT const * L) {

	std::vector<FLOAT> tXL(PARAM0*PARAM0, 0);
	std::vector<FLOAT> tLX(PARAM0*PARAM0, 0);
	double xlmi, lxmi, l;

	for (int i = 0; i < PARAM0; ++i) {
		for (int j = i; j < PARAM0; ++j) {
			for (int k = i; k <= j; ++k) {
				tXL[i*PARAM0+j] += X[k*PARAM0+j]*L[i*PARAM0+k];
				tLX[i*PARAM0+j] += L[k*PARAM0+j]*X[i*PARAM0+k];
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


int test()
{

	int m = PARAM0, info;
	int ldl = m;
	FLOAT * L, * initL;
	long retCode = 0;

	build(&initL, &L);

#ifdef VALIDATE
        FCALL("L", "N", &m, L, &ldl, &info );
	if (info > 0) {
		cout << "The "<< info <<"-th diagonal element of A is zero." << endl;
		exit(EXIT_FAILURE);
	} else if (info < 0) {
		cout << "Parameter "<< info << " had an illegal value." << endl;
		exit(EXIT_FAILURE);
	}

	retCode = validate(initL, L, ERRTHRESH);
	if (retCode) {
		cout << "Validation failed." << endl;
#ifdef CONTONERR
		cout << "Continue-on-error flag is set." << endl;
#else
		return retCode;
#endif
	}
#endif
	//Cache warm-up
	// RDTSCP reads ts register guaranteeing that the execution of all the code
	// we wanted to measure is completed. This way we avoid including the
	// execution of a CPUID in between. The last CPUID guarantees no other
	// instruction can be scheduled before it (and so also before RDTSCP)
#ifdef TEST

	myInt64 start, end, overhead, overhead_tsc;
	double cycles = 0.;
	size_t num_runs = RUNS, multiplier = 1;

	init_tsc();
	overhead_tsc = get_tsc_overhead();

	do{
		num_runs = num_runs * multiplier;

		start = start_tsc();
		for(size_t i = 0; i < num_runs; i++) {
			std::vector<FLOAT> tL(initL, initL+PARAM0*PARAM0);
		}
		end = stop_tsc(start);
		overhead = overhead_tsc + end;

		start = start_tsc();
		for(size_t i = 0; i < num_runs; i++) {
	    	std::vector<FLOAT> tL(initL, initL+PARAM0*PARAM0);
			FCALL("L", "N", &m, L, &ldl, &info );
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

	start = start_tsc();
	for(size_t i = 0; i < num_runs; i++) {
		std::vector<FLOAT> tL(initL, initL+PARAM0*PARAM0);
	}
	end = stop_tsc(start);
	overhead = overhead_tsc + end;

	for (int k = 0; k < Rep; k++) {

		start = start_tsc();
		for (int i = 0; i < num_runs; ++i) {
	    	std::vector<FLOAT> tL(initL, initL+PARAM0*PARAM0);
			FCALL("L", "N", &m, L, &ldl, &info );
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

destroy(initL, L);

#ifdef CONTONERR
return 0;
#else
return retCode;
#endif

}
