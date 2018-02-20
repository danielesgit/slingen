/*
 * upotrf_tester.h
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
  void dpotrf_(const char *uplo, const int *n, double *a, const int *lda, int *info);
};

#define FCALL dpotrf_

inline void build(FLOAT ** initS, FLOAT ** S)
{
  srand(time(NULL));

  *S = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));
  *initS = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));

  rands(*S, PARAM0, PARAM0);

  for (int i = 0; i < PARAM0; ++i)
	  (*S)[i*PARAM0+i] += PARAM0;

  memcpy(*initS, *S, PARAM0*PARAM0*sizeof(FLOAT));

}

inline void destroy(FLOAT * initS, FLOAT * S)
{
  aligned_free(S);
  aligned_free(initS);
}

double frob_norm(FLOAT const * M) {

	double res = 0;

	for (int i = 0; i < PARAM0; ++i)
		for (int j = 0; j <=i; ++j)
			if (j<i)
				res += 2.*M[i*PARAM0+j]*M[i*PARAM0+j];
			else
				res += M[i*PARAM0+j]*M[i*PARAM0+j];

	return sqrt(res);
}


#define NORM frob_norm

/*
 * ||U'*U - S || / ||S||
 */
double func_err(FLOAT const * S, FLOAT const * U) {


	std::vector<FLOAT> UtU(PARAM0*PARAM0, 0);
	std::vector<FLOAT> UtUmS(PARAM0*PARAM0, 0);

	double utums, s;

	for (int i = 0; i < PARAM0; ++i) {
		for (int j = 0; j <= i; ++j) {
			for (int k = 0; k <= j; ++k) {
				UtU[i*PARAM0+j] += U[j*PARAM0+k]*U[i*PARAM0+k];
			}
			UtUmS[i*PARAM0+j] = UtU[i*PARAM0+j] - S[i*PARAM0+j];
		}
	}

	utums = NORM(&UtUmS[0]);
	s     = NORM(S);

	return utums/s;
}

long validate(FLOAT const * initS, FLOAT const * S, double threshold)
{
  bool success = true;
  std::vector<string> errMsgs;

  double err = func_err(initS, S);
  if (err > threshold) {
	  success = false;
	  stringstream ss;
	  ss << "Error = " << err << endl;
	  errMsgs.push_back(ss.str());
  }

  if(!success)
    for(std::vector<string>::const_iterator i = errMsgs.begin(); i != errMsgs.end(); i++)
      cout << *i;

  return !success;

}


int test()
{

	int m = PARAM0, info;
	int lds = m;
	FLOAT * S, * initS;
	long retCode = 0;

	build(&initS, &S);

#ifdef VALIDATE
        FCALL("U", &m, S, &lds, &info );
	if (info > 0) {
		cout << "The leading minor of order "<< info <<" (and therefore the matrix A itself) is not positive-definite" << endl;
		exit(EXIT_FAILURE);
	} else if (info < 0) {
		cout << "Parameter "<< info << " had an illegal value." << endl;
		exit(EXIT_FAILURE);
	}

	retCode = validate(initS, S, ERRTHRESH);
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
			std::vector<FLOAT> tS(initS, initS+PARAM0*PARAM0);
		}
		end = stop_tsc(start);
		overhead = overhead_tsc + end;

		start = start_tsc();
		for(size_t i = 0; i < num_runs; i++) {
	    	std::vector<FLOAT> tS(initS, initS+PARAM0*PARAM0);
			FCALL("U", &m, &tS[0], &lds, &info );
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
		std::vector<FLOAT> tS(initS, initS+PARAM0*PARAM0);
	}
	end = stop_tsc(start);
	overhead = overhead_tsc + end;

	for (int k = 0; k < Rep; k++) {

		start = start_tsc();
		for (int i = 0; i < num_runs; ++i) {
	    	std::vector<FLOAT> tS(initS, initS+PARAM0*PARAM0);
			FCALL("U", &m, &tS[0], &lds, &info );
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

destroy(initS, S);

#ifdef CONTONERR
return 0;
#else
return retCode;
#endif

}
