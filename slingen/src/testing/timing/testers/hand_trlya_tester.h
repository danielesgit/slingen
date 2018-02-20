/*
 * lyap_tester.h
 *
 * LX + XL' = C
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

#include "tsc.h"
#include "helpers.h"
#include "CommonDefs.h"

#define OW

/*
 * PARAM0 -> M
 */

double frob_norm_L(FLOAT const * M) {

	double res = 0;

	for (int i = 0; i < PARAM0; ++i)
		for (int j = 0; j <=i; ++j)
			res += M[i*PARAM0+j]*M[i*PARAM0+j];

	return sqrt(res);
}

double frob_norm_S(FLOAT const * M) {

	double res = 0;

	for (int i = 0; i < PARAM0; ++i)
		for (int j = 0; j < i; ++j)
			res += 2.*M[i*PARAM0+j]*M[i*PARAM0+j];

	for (int i = 0; i < PARAM0; ++i)
		res += M[i*PARAM0+i]*M[i*PARAM0+i];

	return sqrt(res);
}

#define NORM_L frob_norm_L
#define NORM_S frob_norm_S

/* From Sylvester: ||L X + X U - C|| / max( ||L||, ||U|| ) */
double func_err(FLOAT const * L, FLOAT const * C, FLOAT const * X) {

	std::vector<FLOAT> tXU(PARAM0*PARAM0, 0);
	std::vector<FLOAT> tLX(PARAM0*PARAM0, 0);
	double resid, l;

	for (int i = 0; i < PARAM0; ++i) {
		for (int j = 0; j <= i; ++j) {
			for (int k = 0; k <= i; ++k) {
				if (j<=k)
					tLX[i*PARAM0+j] += L[i*PARAM0+k]*X[k*PARAM0+j];
				else
					tLX[i*PARAM0+j] += L[i*PARAM0+k]*X[j*PARAM0+k];
			}
		}
	}

	for (int i = 0; i < PARAM0; ++i) {
		for (int j = 0; j <= i; ++j) {
			for (int k = 0; k <= j; ++k) {
				if (k<=i)
					tXU[i*PARAM0+j] += X[i*PARAM0+k]*L[j*PARAM0+k];
				else
					tXU[i*PARAM0+j] += X[k*PARAM0+i]*L[j*PARAM0+k];
			}
		}
	}

	for (int i = 0; i < PARAM0; ++i)
		for (int j = 0; j <= i; ++j) {
			tLX[i*PARAM0+j] += tXU[i*PARAM0+j];
			tLX[i*PARAM0+j] -= C[i*PARAM0+j];
		}

	resid = NORM_S(&tLX[0]);
	l     = NORM_L(L);

	return resid/l;
}

#ifndef OW
inline void build(FLOAT ** L, FLOAT ** C, FLOAT ** X)
{
	srand(time(NULL));

	*L = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));
	*C = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));
	*X = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));

	rands(*L, PARAM0, PARAM0);
	rands(*C, PARAM0, PARAM0);

	for (int i = 0; i < PARAM0; ++i) {
		(*L)[i*PARAM0+i] += PARAM0;
		(*C)[i*PARAM0+i] += 2.*PARAM0;
	}

	/*Making it symmetric for use with MKL */
	for (int i = 0; i < PARAM0-1; ++i)
		for (int j = i+1; j < PARAM0; ++j) {
			(*L)[i*PARAM0+j] = (*L)[j*PARAM0+i];
			(*C)[i*PARAM0+j] = (*C)[j*PARAM0+i];
		}

}

inline void destroy(FLOAT * L, FLOAT * C, FLOAT * X)
{
	aligned_free(L);
	aligned_free(C);
	aligned_free(X);
}

long validate(FLOAT * L, FLOAT * C, FLOAT * X, double threshold)
{
	bool failed = false;
	std::vector<string> errMsgs;

	double alpha;
	long retvalue = 0;


	// With Err func
	double err = func_err(L, C, X);
	failed =  err > threshold;

	if(failed) {

		stringstream ss;
		ss << "Error threshold: " << threshold << " - ";
		ss << "Error = " << err << endl;
		errMsgs.push_back(ss.str());

	}

    for(std::vector<string>::const_iterator i = errMsgs.begin(); i != errMsgs.end(); i++)
      cout << *i;

	return failed or retvalue;

}

#else

static __attribute__((noinline)) void kernel(FLOAT const * L, FLOAT * C) {

	FLOAT t;
	for(int k=0; k<PARAM0; ++k) { // for each row of x
		for(int i=0; i<k; ++i) { // for each col of x_10
			t = 0;
			//for(int j=0; j<k; ++j) {
			//	t += C[j*PARAM0+i]*L[k*PARAM0+j];
			//}
            // C is symmetric
			for(int j=0; j<i; ++j) {
				t += C[i*PARAM0+j]*L[k*PARAM0+j];
			}
			for(int j=i; j<k; ++j) {
				t += C[j*PARAM0+i]*L[k*PARAM0+j];
			}
			C[k*PARAM0+i] -= t;
		}
		// X10 = Sylv( L11, L00', X10 )
		for(int i=0; i<k; ++i) {
			t = 0;
			for(int j=0; j<i; ++j)
				t += L[j*PARAM0+i]*C[k*PARAM0+j];
			C[k*PARAM0+i] = (C[k*PARAM0+i] - t)/(L[i*PARAM0+i] + L[k*PARAM0+k]);
		}
        // X11 = lyap(L11, X11 - X10 L10' - L10 X10')
		for(int i=0; i<k; ++i) { // for each col of x_10
            C[k*PARAM0+k] -= 2*C[k*PARAM0+i]*L[k*PARAM0+i];
        }
        C[k*PARAM0+k] = C[k*PARAM0+k] / (L[k*PARAM0+k] + L[k*PARAM0+k]);
	}
}


inline void build(FLOAT ** L, FLOAT ** initC, FLOAT ** C)
{
	srand(time(NULL));

	*L = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));
	*initC = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));
	*C = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));

	rands(*L, PARAM0, PARAM0);
	rands(*C, PARAM0, PARAM0);

	for (int i = 0; i < PARAM0; ++i) {
		(*L)[i*PARAM0+i] += PARAM0;
		(*C)[i*PARAM0+i] += 2.*PARAM0;
	}

	/*Making it symmetric for use with MKL */
	for (int i = 0; i < PARAM0-1; ++i)
		for (int j = i+1; j < PARAM0; ++j) {
			(*L)[i*PARAM0+j] = (*L)[j*PARAM0+i];
			(*C)[i*PARAM0+j] = (*C)[j*PARAM0+i];
		}

	memcpy(*initC, *C, PARAM0*PARAM0*sizeof(FLOAT));
}

inline void destroy(FLOAT * L, FLOAT * initC, FLOAT * C)
{
	aligned_free(L);
	aligned_free(C);
	aligned_free(initC);
}

long validate(FLOAT const * L, FLOAT const * initC, FLOAT const * C, double threshold)
{
	bool failed = false;
	std::vector<string> errMsgs;

	double alpha;
	long retvalue = 0;

	// With Err func
	double err = func_err(L, initC, C);
	failed =  err > threshold;

	if(failed) {

		stringstream ss;
		ss << "Error threshold: " << threshold << " - ";
		ss << "Error = " << err << endl;
		errMsgs.push_back(ss.str());

	}

    for(std::vector<string>::const_iterator i = errMsgs.begin(); i != errMsgs.end(); i++)
      cout << *i;

	return failed or retvalue;

}

#endif

int test()
{

#ifndef OW
	FLOAT * L, * C, * X;
#else
	FLOAT * L, * initC, * C;
#endif
	myInt64 start, end, overhead, overhead_tsc;
	double cycles = 0.;
	size_t num_runs = RUNS, multiplier = 1;
	long retCode = 0;

#ifndef OW
#else
#endif

#ifndef OW
	build(&L, &C, &X);
#else
	build(&L, &initC, &C);
#endif

#ifdef VALIDATE
#ifndef OW
	kernel(L, C, X);
	retCode = validate(L,C,X, ERRTHRESH);
#else
	kernel(L, C);
	retCode = validate(L,initC,C, ERRTHRESH);
#endif
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
	init_tsc();
	overhead_tsc = get_tsc_overhead();

	do{
		num_runs = num_runs * multiplier;

#ifndef OW
		start = start_tsc();
		for(size_t i = 0; i < num_runs; i++) {
			std::vector<FLOAT> tC(initC, initC+PARAM0*PARAM0);
		}
		end = stop_tsc(start);
		overhead = overhead_tsc + end;
#else
		overhead = overhead_tsc;
#endif

		start = start_tsc();
		for(size_t i = 0; i < num_runs; i++) {
#ifndef OW
			kernel(L, C, X);
#else
			std::vector<FLOAT> tC(initC, initC+PARAM0*PARAM0);
			kernel(L, &tC[0]);
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

//	double flops = PARAM0*PARAM0*(PARAM0+PARAM0);
	double flops = PARAM0*PARAM0*PARAM0;

#ifdef OW
	start = start_tsc();
	for(size_t i = 0; i < num_runs; i++) {
		std::vector<FLOAT> tC(initC, initC+PARAM0*PARAM0);
	}
	end = stop_tsc(start);
	overhead = overhead_tsc + end;
#endif

	for (int k = 0; k < Rep; k++) {

		start = start_tsc();
		for (int i = 0; i < num_runs; ++i) {
#ifndef OW
			kernel(L, C, X);
#else
			std::vector<FLOAT> tC(initC, initC+PARAM0*PARAM0);
			kernel(L, &tC[0]);
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

#ifndef OW
	destroy(L, C, X);
#else
	destroy(L, initC, C);
#endif

#ifdef CONTONERR
return 0;
#else
return retCode;
#endif

}
