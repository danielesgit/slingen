/*
 * gpr_tester.h
 *
 *  Created on: Aug 12, 2017
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

typedef Map< Matrix<FLOAT, PARAM0, 1> > Vec_m;
typedef Map< Matrix<FLOAT, PARAM1, 1> > Vec_k;

typedef Map< Matrix<FLOAT, PARAM0, PARAM0, RowMajor> > Mat_mm;
typedef Map< Matrix<FLOAT, PARAM0, PARAM1, RowMajor> > Mat_mk;

/*
 * PARAM0 -> M
 * PARAM1 -> K
 */

static __attribute__((noinline)) void kernel(const Mat_mk& X, const Vec_k& x, Mat_mm& K, Vec_m& y, Vec_m& kx,
		FLOAT& f, FLOAT& var, FLOAT& lp) {
	//	L   = chol(K, 'lower');
	//	y   = L\y;
	//	y   = L'\y;
	LLT< Ref<Mat_mm> > lltOfS(K);
	K.triangularView<Lower>().solveInPlace(y);
	K.transpose().triangularView<Upper>().solveInPlace(y);
	//	kx  = X*x;
	kx = X*x;
	//	f   = kx'*y;
	f = kx.transpose()*y;
	//	kx  = L\kx;
	K.triangularView<Lower>().solveInPlace(kx);
	//	var = x'*x - kx'*kx;
	var = x.transpose()*x;
	var -= kx.transpose()*kx;
	//	lp  = y'*y;
	lp = y.transpose()*y;
}

double rel_diff(FLOAT a, FLOAT b) {

	using std::max;
	double c = fabs(a), d = fabs(b);
	double m = max(c, d);

	return (m == 0.) ? 0. : fabs(a-b)/m;
}

void build(FLOAT ** X, FLOAT ** x, FLOAT ** init_K, FLOAT ** K, FLOAT ** init_y, FLOAT ** y, FLOAT ** kx)
{
	srand(time(NULL));

	*X = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM1*sizeof(FLOAT), ALIGN));
	*x = static_cast<FLOAT *>(aligned_malloc(PARAM1*sizeof(FLOAT), ALIGN));

	*init_K = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));
	*K = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));
	*init_y = static_cast<FLOAT *>(aligned_malloc(PARAM0*sizeof(FLOAT), ALIGN));
	*y = static_cast<FLOAT *>(aligned_malloc(PARAM0*sizeof(FLOAT), ALIGN));
	*kx = static_cast<FLOAT *>(aligned_malloc(PARAM0*sizeof(FLOAT), ALIGN));


	rands(*X, PARAM0, PARAM1);
	rands(*x, PARAM1, 1);
	rands(*K, PARAM0, PARAM0);
	rands(*y, PARAM0, 1);

	for (int i = 0; i < PARAM0; ++i) {
		(*K)[i*PARAM0+i] += PARAM0;
	}

	for (int i = 0; i < PARAM0; ++i) {
		for (int j = 0; j < i; ++j) {
			(*K)[i*PARAM0+j] = (*K)[j*PARAM0+i];
		}
	}

	memcpy(*init_y, *y, PARAM0*sizeof(FLOAT));
	memcpy(*init_K, *K, PARAM0*PARAM0*sizeof(FLOAT));

}

void destroy(FLOAT * X, FLOAT * x, FLOAT * init_K, FLOAT * K, FLOAT * init_y, FLOAT * y, FLOAT * kx)
{
	aligned_free(X);
	aligned_free(x);
	aligned_free(init_y);
	aligned_free(y);
	aligned_free(init_K);
	aligned_free(K);
	aligned_free(kx);
}

long validate(FLOAT const * X, FLOAT const * x, FLOAT const * init_K, FLOAT const * K, FLOAT const * init_y,
		FLOAT const * y, FLOAT const * kx, const FLOAT f, const FLOAT var, const FLOAT lp, const double threshold)
{
	bool failed = false;
	std::list<string> soft_err_msgs;
	std::vector<string> errMsgs;

	_dlmwrite(X, PARAM0, PARAM1, 0, 0, PARAM1, string(EXEC_PATH) + "/X.txt");
	_dlmwrite(x, PARAM1, 1, 0, 0, 1, string(EXEC_PATH) + "/x.txt");

	_dlmwrite(init_K, PARAM0, PARAM0, 0, 0, PARAM0, string(EXEC_PATH) + "/K.txt");
	_dlmwrite(init_y, PARAM0, 1, 0, 0, 1, string(EXEC_PATH) + "/y.txt");

	string s = string("/usr/local/bin/matlab -nodisplay -nosplash -nodesktop -r \"execpath='") + string(EXEC_PATH) + "'; addpath(execpath); run('validategpr.m');\"";
	system(s.c_str());

	FLOAT fout, varout, lpout;

	_dlmread(&fout, 1, 1, 0, 0, 1, string(EXEC_PATH) + "/f-out.txt");
	_dlmread(&varout, 1, 1, 0, 0, 1, string(EXEC_PATH) + "/var-out.txt");
	_dlmread(&lpout, 1, 1, 0, 0, 1, string(EXEC_PATH) + "/lp-out.txt");

	double err = rel_diff(f, fout);
	if (err > SOFTERRTHRESH) {
		stringstream ss;
		ss << "WARNING: Error = " << err << ": f = " << f << " - fout = " << fout << endl;
		soft_err_msgs.push_back(ss.str());
	}
	if (err > threshold) {
		failed = true;
		stringstream ss;
		ss << "Error = " << err << ": f = " << f << " - fout = " << fout << endl;
		errMsgs.push_back(ss.str());
	}

	err = rel_diff(var, varout);
	if (err > SOFTERRTHRESH) {
		stringstream ss;
		ss << "WARNING: Error = " << err << ": var = " << var << " - varout = " << varout << endl;
		soft_err_msgs.push_back(ss.str());
	}
	if (err > threshold) {
		failed = true;
		stringstream ss;
		ss << "Error = " << err << ": var = " << var << " - varout = " << varout << endl;
		errMsgs.push_back(ss.str());
	}

	err = rel_diff(lp, lpout);
	if (err > SOFTERRTHRESH) {
		stringstream ss;
		ss << "WARNING: Error = " << err << ": lp = " << lp << " - lpout = " << lpout << endl;
		soft_err_msgs.push_back(ss.str());
	}
	if (err > threshold) {
		failed = true;
		stringstream ss;
		ss << "WARNING: Error = " << err << ": lp = " << lp << " - lpout = " << lpout << endl;
		errMsgs.push_back(ss.str());
	}

	dumpList(soft_err_msgs, string(EXEC_PATH) + "/soft_errors.txt");

	if(failed)
		for(std::vector<string>::const_iterator i = errMsgs.begin(); i != errMsgs.end(); i++)
			cout << *i;

	return failed;

}


int test()
{

	FLOAT * aX, * ax, * init_K, * aK, * init_y, * ay, * akx;
	FLOAT f, var, lp;
	long retCode = 0;

	build(&aX, &ax, &init_K, &aK, &init_y, &ay, &akx);

	Vec_m y(ay), kx(akx);
	Vec_k x(ax);
	Mat_mk X(aX);
	Mat_mm K(aK);


#ifdef VALIDATE
	kernel(X, x, K, y, kx, f, var, lp);
	retCode = validate(aX, ax, init_K, aK, init_y, ay, akx, f, var, lp, ERRTHRESH);

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
		kernel(X, x, K, y, kx, f, var, lp);
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
			memcpy(ay, init_y, PARAM0*sizeof(FLOAT));
			memcpy(aK, init_K, PARAM0*PARAM0*sizeof(FLOAT));
		}
		end = stop_tsc(start);
		overhead = overhead_tsc + end;

		start = start_tsc();
		for(size_t i = 0; i < num_runs; i++) {
			memcpy(ay, init_y, PARAM0*sizeof(FLOAT));
			memcpy(aK, init_K, PARAM0*PARAM0*sizeof(FLOAT));
			kernel(X, x, K, y, kx, f, var, lp);
		}
		end = stop_tsc(start);
		if (end > overhead)
			end -= overhead;

		cycles = (double) end;
		multiplier = ceil (  (CYCLES_REQUIRED) / (cycles)  + 1.0 );

	}while (multiplier > 2);

	list< double > cycleList, flopList;
	size_t Rep = NUMREP;

	double flops = double(PARAM0)*PARAM0*PARAM0/3. + 3.*PARAM0*PARAM0 + 2.*PARAM0*PARAM1 + 6.*PARAM0 + 2.*PARAM1;

	start = start_tsc();
	for(size_t i = 0; i < num_runs; i++) {
		memcpy(ay, init_y, PARAM0*sizeof(FLOAT));
		memcpy(aK, init_K, PARAM0*PARAM0*sizeof(FLOAT));
	}
	end = stop_tsc(start);
	overhead = overhead_tsc + end;

	for (int k = 0; k < Rep; k++) {

		start = start_tsc();
		for (int i = 0; i < num_runs; ++i) {
			memcpy(ay, init_y, PARAM0*sizeof(FLOAT));
			memcpy(aK, init_K, PARAM0*PARAM0*sizeof(FLOAT));
			kernel(X, x, K, y, kx, f, var, lp);
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

destroy(aX, ax, init_K, aK, init_y, ay, akx);

return retCode;
}
