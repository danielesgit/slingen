/*
 * lusylp_tester.h
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

#include <Eigen/Dense>

#ifdef TEST
#ifndef ERM
#include "tsc.h"
#endif
#endif

#include "helpers.h"
#include "CommonDefs.h"

using namespace std;
using namespace Eigen;

typedef Map< Matrix<FLOAT, PARAM0, PARAM0, RowMajor> > MapMatL;
typedef Map< Matrix<FLOAT, PARAM1, PARAM1, RowMajor> > MapMatU;
typedef Map< Matrix<FLOAT, PARAM0, PARAM1, RowMajor> > MapMat;


/*
 * PARAM0 -> M
 * PARAM1 -> N
 */

inline void build(FLOAT ** L, FLOAT ** U, FLOAT ** T, FLOAT ** initC, FLOAT ** C)
{
	srand(time(NULL));

	*L = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));
	*U = static_cast<FLOAT *>(aligned_malloc(PARAM1*PARAM1*sizeof(FLOAT), ALIGN));
	*T = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));
	*C = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM1*sizeof(FLOAT), ALIGN));
	*initC = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM1*sizeof(FLOAT), ALIGN));

	rands(*L, PARAM0, PARAM0);
	rands(*U, PARAM1, PARAM1);
	rands(*C, PARAM0, PARAM1);

	memcpy(*initC, *C, PARAM0*PARAM1*sizeof(FLOAT));

	for (int i = 0; i < PARAM0; ++i)
		(*L)[i*PARAM0+i] += PARAM0;

	for (int i = 0; i < PARAM1; ++i)
		(*U)[i*PARAM1+i] += 2.*PARAM1;

}

inline void destroy(FLOAT * L, FLOAT * U, FLOAT * T, FLOAT * initC, FLOAT * C)
{
	aligned_free(L);
	aligned_free(U);
	aligned_free(T);
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

static __attribute__((noinline)) void kernel(const MapMatL& L, const MapMatU& U, MapMatL& T, MapMat& C) {

	for(int k = 0; k < PARAM1; k++) {
		if(k>0)
			C.col(k) -= C.block(0, 0, PARAM0, k)*U.block(0, k, k, 1);
		T = MapMatL::Identity()*U(k,k);
		T += L.triangularView<Lower>();
		T.triangularView<Lower>().solveInPlace(C.col(k));
	}
}

int test()
{

	FLOAT * aL, * aU, * aT, * initC, * aC;

	long retCode = 0;

	cout << "Eigen - SIMD ISAs in use: " << SimdInstructionSetsInUse() << endl;

	build(&aL, &aU, &aT, &initC, &aC);

	MapMatL L(aL), T(aT);
	MapMatU U(aU);
	MapMat C(aC);

#ifdef VALIDATE
	kernel(L, U, T, C);
	retCode = validate(aL, aU, initC, aC, ERRTHRESH);
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
		kernel(L, U, T, C);
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
			memcpy(aC, initC, PARAM0*PARAM1*sizeof(FLOAT));
		}
		end = stop_tsc(start);
		overhead = overhead_tsc + end;

		start = start_tsc();
		for(size_t i = 0; i < num_runs; i++) {
			memcpy(aC, initC, PARAM0*PARAM1*sizeof(FLOAT));
			kernel(L, U, T, C);
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
		memcpy(aC, initC, PARAM0*PARAM1*sizeof(FLOAT));
	}
	end = stop_tsc(start);
	overhead = overhead_tsc + end;

	for (int k = 0; k < Rep; k++) {

		start = start_tsc();
		for (int i = 0; i < num_runs; ++i) {
			memcpy(aC, initC, PARAM0*PARAM1*sizeof(FLOAT));
			kernel(L, U, T, C);
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

destroy(aL, aU, aT, initC, aC);

#ifdef CONTONERR
return 0;
#else
return retCode;
#endif

}
