/*
 * kf_tester.h
 *
 *  Created on: Sep 6, 2016
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

#include <mkl.h>

#include "tsc.h"
#include "helpers.h"
#include "CommonDefs.h"

#include "params.h"

#if TYPE == FLT
#else
#define FCHOL LAPACKE_dpotrf
#define FTRSV cblas_dtrsv
#define FGEMV cblas_dgemv
#define FDOT  cblas_ddot
#endif

#define OW

double rel_diff(FLOAT a, FLOAT b) {

	using std::max;
	double c = fabs(a), d = fabs(b);
	double m = max(c, d);

	return (m == 0.) ? 0. : fabs(a-b)/m;
}

/*
 * PARAM0 -> M
 * PARAM1 -> K
 */

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

void kernel(FLOAT const * X, FLOAT const * x, FLOAT * K, FLOAT * y, FLOAT * kx, FLOAT * f, FLOAT * var, FLOAT * lp)
{
	// L*trans(L) = K;
	FCHOL(LAPACK_ROW_MAJOR, 'L', PARAM0, K, PARAM0);
	//L0*t0 = y;
	FTRSV(CblasRowMajor, CblasLower, CblasNoTrans, CblasNonUnit, PARAM0, K, PARAM0, y, 1);
	//trans(L0)*a = t1;
	FTRSV(CblasRowMajor, CblasLower, CblasTrans, CblasNonUnit, PARAM0, K, PARAM0, y, 1);
	//kx = X*x;
	FGEMV(CblasRowMajor, CblasNoTrans, PARAM0, PARAM1, 1., X, PARAM0, x, 1, 0., kx, 1);
	//f = trans(kx)*y;
	*f = FDOT(PARAM0, kx, 1, y, 1);
	//L0*v = t2;
	FTRSV(CblasRowMajor, CblasLower, CblasNoTrans, CblasNonUnit, PARAM0, K, PARAM0, kx, 1);
	//var = trans(x)*x - trans(kx)*kx;
	*var = FDOT(PARAM1, x, 1, x, 1) - FDOT(PARAM0, kx, 1, kx, 1);
	//lp  = trans(y)*y;
	*lp = FDOT(PARAM0, y, 1, y, 1);

}


int test()
{

#ifndef OW
  FLOAT * S, * U;
#else
  FLOAT * X, * x, * init_K, * K, * init_y, * y, * kx;
  FLOAT f, var, lp;
#endif
  myInt64 start, end, overhead, overhead_tsc;
  double cycles = 0.;
  size_t num_runs = RUNS, multiplier = 1;
  long retCode = 0;

#ifndef OW
  build(&S, &U);
#else
  build(&X, &x, &init_K, &K, &init_y, &y, &kx);
#endif

#ifdef VALIDATE
#ifndef OW
  kernel(S, U);
  retCode = validate(S,U, ERRTHRESH);
#else
  kernel(X, x, K, y, kx, &f, &var, &lp);
  retCode = validate(X, x, init_K, K, init_y, y, kx, f, var, lp, ERRTHRESH);
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
  init_tsc();
  overhead_tsc = get_tsc_overhead();

  do{
      num_runs = num_runs * multiplier;

#ifdef OW
      start = start_tsc();
      for(size_t i = 0; i < num_runs; i++) {
    	  std::vector<FLOAT> ty(init_y, init_y+PARAM0);
    	  std::vector<FLOAT> tK(init_K, init_K+PARAM0*PARAM0);
      }
      end = stop_tsc(start);
      overhead = overhead_tsc + end;
#else
      overhead = overhead_tsc;
#endif

      start = start_tsc();
      for(size_t i = 0; i < num_runs; i++) {
#ifndef OW
    	  kernel(S, U);
#else
    	  std::vector<FLOAT> ty(init_y, init_y+PARAM0);
    	  std::vector<FLOAT> tK(init_K, init_K+PARAM0*PARAM0);
    	  kernel(X, x, &tK[0], &ty[0], kx, &f, &var, &lp);
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

  double flops = double(PARAM0)*PARAM0*PARAM0/3. + 3.*PARAM0*PARAM0 + 2.*PARAM0*PARAM1 + 6.*PARAM0 + 2.*PARAM1;

#ifdef OW
  start = start_tsc();
  for(size_t i = 0; i < num_runs; i++) {
	  std::vector<FLOAT> ty(init_y, init_y+PARAM0);
	  std::vector<FLOAT> tK(init_K, init_K+PARAM0*PARAM0);
  }
  end = stop_tsc(start);
  overhead = overhead_tsc + end;
#endif

  for (int k = 0; k < Rep; k++) {

      start = start_tsc();
      for (int i = 0; i < num_runs; ++i) {
#ifndef OW
    	  kernel(S, U);
#else
    	  std::vector<FLOAT> ty(init_y, init_y+PARAM0);
    	  std::vector<FLOAT> tK(init_K, init_K+PARAM0*PARAM0);
    	  kernel(X, x, &tK[0], &ty[0], kx, &f, &var, &lp);
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
  destroy(S, U);
#else
  destroy(X, x, init_K, K, init_y, y, kx);
#endif

  return retCode;
}
