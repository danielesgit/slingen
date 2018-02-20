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

//#include <mkl.h>

#ifdef TEST
#ifndef ERM
#include "tsc.h"
#endif
#endif

#include "helpers.h"
#include "CommonDefs.h"

#include "kernels/lusylp_kernel.h"

//#if TYPE == FLT
//#define FQR	LAPACKE_shseqr
//#define FCALL LAPACKE_strsyl
//#else
//#define FQR	LAPACKE_dhseqr
//#define FCALL LAPACKE_dtrsyl
//#endif

/*
 * PARAM0 -> M
 * PARAM1 -> N
 */

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

//	double alpha;
//
//	std::vector<FLOAT> tC(C, C+PARAM0*PARAM1);
//	std::vector<FLOAT> tC1(PARAM0*PARAM1, 0);
//	std::vector<FLOAT> tT1(PARAM0*PARAM1, 0);
//	std::vector<FLOAT> tT2(PARAM0*PARAM1, 0);
//	std::vector<FLOAT> tL(L, L+PARAM0*PARAM0);
//	std::vector<FLOAT> ZL(PARAM0*PARAM0);
//	std::vector<FLOAT> wrL(PARAM0);
//	std::vector<FLOAT> wiL(PARAM0);
//	std::vector<FLOAT> tU(U, U+PARAM1*PARAM1);
//	std::vector<FLOAT> ZU(PARAM1*PARAM1);
//	std::vector<FLOAT> wrU(PARAM1);
//	std::vector<FLOAT> wiU(PARAM1);
//
//	long retvalue;
//
//	for (int i = 0; i < PARAM0-1; ++i)
//		tL[(i+1)*PARAM0 + i] = 0.;
//
//	for (int i = 0; i < PARAM1-1; ++i)
//		tU[(i+1)*PARAM1 + i] = 0.;
//
//
//	// Computing Schur form of L^T and U
//	retvalue = (long)FQR(LAPACK_ROW_MAJOR, 'S', 'I', PARAM0, 1, PARAM0, &tL[0], PARAM0, &wrL[0], &wiL[0], &ZL[0], PARAM0);
//
//	if (retvalue > 0) {
//		stringstream ss;
//		ss << "Schur form of L^T. Positive ret. value." << endl;
//		ss << "  Ret = " << retvalue << endl;
//		errMsgs.push_back(ss.str());
//		//	  return retvalue;
//	} else if (retvalue < 0) {
//		stringstream ss;
//		ss << "Schur form of L^T. Parameter "<< retvalue << " had an illegal value." << endl;
//		errMsgs.push_back(ss.str());
//		//	  return retvalue;
//	}
//
//	retvalue = (long)FQR(LAPACK_ROW_MAJOR, 'S', 'I', PARAM1, 1, PARAM1, &tU[0], PARAM1, &wrU[0], &wiU[0], &ZU[0], PARAM1);
//
//	if (retvalue > 0) {
//		stringstream ss;
//		ss << "Schur form of U. Positive ret. value." << endl;
//		ss << "  Ret = " << retvalue << endl;
//		errMsgs.push_back(ss.str());
//		//	  return retvalue;
//	} else if (retvalue < 0) {
//		stringstream ss;
//		ss << "Schur form of U. Parameter "<< retvalue << " had an illegal value." << endl;
//		errMsgs.push_back(ss.str());
//		//	  return retvalue;
//	}
//
//
//	retvalue = (long)FCALL(LAPACK_ROW_MAJOR, 'T', 'N', 1, PARAM0, PARAM1, &tL[0], PARAM0, &tU[0], PARAM1, &tC[0], PARAM1, &alpha);
//
//	if (retvalue == 1) {
//		stringstream ss;
//		ss << "A and B have common or close eigenvalues; perturbed values were used to solve the equation." << endl;
//		ss << "  Alpha = " << alpha << endl;
//		//	  return retvalue;
//	} else if (retvalue < 0) {
//		stringstream ss;
//		ss << "Parameter "<< retvalue << " had an illegal value." << endl;
//		//	  return retvalue;
//	}
//
//	if (retvalue == 0)
//		for (int i = 0; i < PARAM0; ++i) {
//			for (int j = 0; j < PARAM1; ++j) {
//				double err, den = fabs(tC[i*PARAM1+j]);
//				bool rel = true;
//				if(den > 0.) {
//					err = fabs(X[i*PARAM1+j] - tC[i*PARAM1+j])/den;
//				}else {
//					rel = false;
//					err = fabs(X[i*PARAM1+j] - tC[i*PARAM1+j]);
//				}
//				if(err > threshold) {
//					failed = true;
//					stringstream ss;
//					ss << "Error at (" << i << ","<< j << "): ";
//					ss << "X = " << X[i*PARAM1+j] << "\t-- tC = " << tC[i*PARAM1+j] << "\t-- Err = " << err << " (relative: "<< rel << " )" << endl;
//					errMsgs.push_back(ss.str());
//				}
//			}
//		}
	// With Err func
	double err = func_err(L, U, initC, C);
	failed =  err > threshold;


	if(failed) {
		stringstream ss;
		ss << "Error threshold: " << threshold << " - ";
		ss << "Error = " << err << endl;
		errMsgs.push_back(ss.str());

//		errMsgs.push_back("------------------------------------------------- Residual -----------------------------------------------\n");
//
//		for(int i=0; i<PARAM0; i++)
//			for(int j=0;j<PARAM1; j++)
//				for(int k=0;k<=i; k++)
//					tT1[i*PARAM1+j] += L[i*PARAM0+k]*X[k*PARAM1+j];
//
//		for(int i=0; i<PARAM0; i++)
//			for(int j=0;j<PARAM1; j++)
//				for(int k=0;k<=j; k++)
//					tT2[i*PARAM1+j] += X[i*PARAM1+k]*U[k*PARAM1+j];
//
//		for(int i=0; i<PARAM0; i++){
//			for(int j=0;j<PARAM1; j++) {
//				tC1[i*PARAM1+j] = tT1[i*PARAM1+j]+tT2[i*PARAM1+j];
//
//			}
//		}
//
//		for (int i = 0; i < PARAM0; ++i) {
//			for (int j = 0; j < PARAM1; ++j) {
//				double err, den = fabs(C[i*PARAM1+j]);
//				bool rel = true;
//				if(den > 0.) {
//					err = fabs(tC1[i*PARAM1+j] - C[i*PARAM1+j])/den;
//				}else {
//					rel = false;
//					err = fabs(tC1[i*PARAM1+j] - C[i*PARAM1+j]);
//				}
//				if(err > threshold) {
//					failed = true;
//					stringstream ss;
//					ss << "|C-(LX+XU)| Error at (" << i << ","<< j << "): ";
//					ss << "LX+XU = " << tC1[i*PARAM1+j] << "\t-- C = " << C[i*PARAM1+j] << "\t-- Err = " << err << " (relative: "<< rel << " )" << endl;
//					errMsgs.push_back(ss.str());
//				}
//			}
//		}
//
//
//		ofstream outfile;
//		outfile.open(( string(EXEC_PATH) + "/err.txt" ).c_str(), ios_base::out);
//		outfile << "Error threshold: " << threshold << "\n\n";
//		for(std::vector<string>::const_iterator i = errMsgs.begin(); i != errMsgs.end(); i++) {
//			cout << *i;
//			outfile << *i;
//		}
//		outfile.close();
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
