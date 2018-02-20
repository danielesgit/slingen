/*
 * lusyl_tester.h
 *
 * LX + XU = C
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
 * PARAM1 -> N
 */

static __attribute__((noinline)) void kernel(FLOAT const * L, FLOAT const * U, FLOAT * C) {

	FLOAT t;

	for(int k=0; k<PARAM1; ++k) {

		for(int i=0; i<PARAM0; ++i) {
			t = 0;
			for(int j=0; j<k; ++j) {
				t += C[i*PARAM1+j]*U[j*PARAM1+k];
			}
			C[i*PARAM1+k] -= t;
		}
		//Solve
		C[k] /= (L[0] + U[k*PARAM1+k]);
		for(int i=1; i<PARAM0; ++i) {
			t = 0;
			for(int j=0; j<i; ++j)
				t += L[i*PARAM0+j]*C[j*PARAM1+k];
			C[i*PARAM1+k] = (C[i*PARAM1+k] - t)/(L[i*PARAM0+i] + U[k*PARAM1+k]);
		}

	}

}

inline void build(FLOAT ** L, FLOAT ** U, FLOAT ** initC, FLOAT ** C)
{
	srand(time(NULL));

	*L = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));
	*U = static_cast<FLOAT *>(aligned_malloc(PARAM1*PARAM1*sizeof(FLOAT), ALIGN));
	*C = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM1*sizeof(FLOAT), ALIGN));
	*initC = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM1*sizeof(FLOAT), ALIGN));

	rands(*L, PARAM0, PARAM0);
	rands(*U, PARAM1, PARAM1);
	rands(*C, PARAM0, PARAM1);

	memcpy(*initC, *C, PARAM0*PARAM1*sizeof(FLOAT));

	for (int i = 0; i < PARAM0; ++i)
		(*L)[i*PARAM0+i] += PARAM0;

	/*Making it symmetric for use with MKL */
	for (int i = 0; i < PARAM0-1; ++i)
		for (int j = i+1; j < PARAM0; ++j)
			(*L)[i*PARAM0+j] = (*L)[j*PARAM0+i];

	for (int i = 0; i < PARAM1; ++i)
		(*U)[i*PARAM1+i] += 2.*PARAM1;

}

inline void destroy(FLOAT * L, FLOAT * U, FLOAT * initC, FLOAT * C)
{
	aligned_free(L);
	aligned_free(U);
	aligned_free(C);
	aligned_free(initC);
}

double frob_norm_L(FLOAT const * M) {

	double res = 0;

	for (int i = 0; i < PARAM0; ++i)
		for (int j = 0; j <=i; ++j)
			res += M[i*PARAM0+j]*M[i*PARAM0+j];

	return sqrt(res);
}

double frob_norm_U(FLOAT const * M) {

	double res = 0;

	for (int i = 0; i < PARAM1; ++i)
		for (int j = i; j < PARAM1; ++j)
			res += M[i*PARAM1+j]*M[i*PARAM1+j];

	return sqrt(res);
}

double frob_norm(FLOAT const * M) {

	double res = 0;

	for (int i = 0; i < PARAM0; ++i)
		for (int j = 0; j < PARAM1; ++j)
			res += M[i*PARAM1+j]*M[i*PARAM1+j];

	return sqrt(res);
}

#define NORM frob_norm
#define NORM_L frob_norm_L
#define NORM_U frob_norm_U

/* From Sylvester: ||L X + X U - C|| / max( ||L||, ||U|| ) */
double func_err(FLOAT const * L, FLOAT const * U, FLOAT const * C, FLOAT const * X) {

	std::vector<FLOAT> tXU(PARAM0*PARAM1, 0);
	std::vector<FLOAT> tLX(PARAM0*PARAM1, 0);
	double resid, l, u;

	for (int i = 0; i < PARAM0; ++i) {
		for (int j = 0; j < PARAM1; ++j) {
			for (int k = 0; k <= i; ++k) {
				tLX[i*PARAM1+j] += L[i*PARAM0+k]*X[k*PARAM1+j];
			}
		}
	}

	for (int i = 0; i < PARAM0; ++i) {
		for (int j = 0; j < PARAM1; ++j) {
			for (int k = 0; k <= j; ++k) {
				tXU[i*PARAM1+j] += X[i*PARAM1+k]*U[k*PARAM1+j];
			}
		}
	}

	for (int i = 0; i < PARAM0; ++i)
		for (int j = 0; j < PARAM1; ++j) {
			tLX[i*PARAM1+j] += tXU[i*PARAM1+j];
			tLX[i*PARAM1+j] -= C[i*PARAM1+j];
		}

	resid = NORM(&tLX[0]);
	l     = NORM_L(L);
	u     = NORM_U(U);

	using std::max;
	return resid/max(l,u);
}

long validate(FLOAT * L, FLOAT * U, FLOAT * initC, FLOAT * C, double threshold)
{
	bool failed = false;
	std::vector<string> errMsgs;

	// With Err func
	double err = func_err(L, U, initC, C);
	failed =  err > threshold;


	if(failed) {
		stringstream ss;
		ss << "Error threshold: " << threshold << " - ";
		ss << "Error = " << err << endl;
		errMsgs.push_back(ss.str());

	}

	for(std::vector<string>::const_iterator i = errMsgs.begin(); i != errMsgs.end(); i++)
		cout << *i;


//	return failed or retvalue;
	return failed;

}


int test()
{

	FLOAT * L, * U, * initC, * C;
	long retCode = 0;

	build(&L, &U, &initC, &C);

#ifdef VALIDATE
	kernel(L, U, C);
	retCode = validate(L,U,initC,C, ERRTHRESH);
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

#ifdef ERM
	for(int i=0; i<2; i++)
		kernel(L, U, C);
#endif

#ifndef ERM

	myInt64 start, end, overhead, overhead_tsc;
	double cycles = 0.;
	size_t num_runs = RUNS, multiplier = 1;

	init_tsc();
	overhead_tsc = get_tsc_overhead();

	do{
		num_runs = num_runs * multiplier;

		start = start_tsc();
		for(size_t i = 0; i < num_runs; i++) {
			std::vector<FLOAT> tC(initC, initC+PARAM0*PARAM1);
		}
		end = stop_tsc(start);
		overhead = overhead_tsc + end;

		start = start_tsc();
		for(size_t i = 0; i < num_runs; i++) {
			std::vector<FLOAT> tC(initC, initC+PARAM0*PARAM1);
			kernel(L, U, &tC[0]);
		}
		end = stop_tsc(start);
		if (end > overhead)
			end -= overhead;

		cycles = (double) end;
		multiplier = ceil (  (CYCLES_REQUIRED) / (cycles)  + 1.0 );

	}while (multiplier > 2);

	list< double > cycleList, flopList;
	size_t Rep = NUMREP;

	double flops = PARAM0*PARAM1*(PARAM0+PARAM1);

	start = start_tsc();
	for(size_t i = 0; i < num_runs; i++) {
		std::vector<FLOAT> tC(initC, initC+PARAM0*PARAM1);
	}
	end = stop_tsc(start);
	overhead = overhead_tsc + end;

	for (int k = 0; k < Rep; k++) {

		start = start_tsc();
		for (int i = 0; i < num_runs; ++i) {
			std::vector<FLOAT> tC(initC, initC+PARAM0*PARAM1);
			kernel(L, U, &tC[0]);
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

destroy(L, U, initC, C);

#ifdef CONTONERR
return 0;
#else
return retCode;
#endif

}
