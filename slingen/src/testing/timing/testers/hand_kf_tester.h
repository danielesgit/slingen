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

#ifdef TEST
#ifndef ERM
#include "tsc.h"
#endif
#endif

#include "helpers.h"
#include "CommonDefs.h"

#include "kernels/kf_kernel.h"

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
 * PARAM2 -> N
 */

inline void build(FLOAT ** F, FLOAT ** B, FLOAT ** u, FLOAT ** Q, FLOAT ** z, FLOAT ** H, FLOAT ** R,
		FLOAT ** y, FLOAT ** init_x, FLOAT ** x, FLOAT ** M0, FLOAT ** init_P, FLOAT ** P, FLOAT ** Y, FLOAT ** v0, FLOAT ** M1, FLOAT ** M2, FLOAT ** M3)
{
  srand(time(NULL));

  *F = static_cast<FLOAT *>(aligned_malloc(PARAM2*PARAM2*sizeof(FLOAT), ALIGN));
  *B = static_cast<FLOAT *>(aligned_malloc(PARAM2*PARAM0*sizeof(FLOAT), ALIGN));
  *u = static_cast<FLOAT *>(aligned_malloc(PARAM0*sizeof(FLOAT), ALIGN));
  *Q = static_cast<FLOAT *>(aligned_malloc(PARAM2*PARAM2*sizeof(FLOAT), ALIGN));
  *z = static_cast<FLOAT *>(aligned_malloc(PARAM1*sizeof(FLOAT), ALIGN));
  *H = static_cast<FLOAT *>(aligned_malloc(PARAM1*PARAM2*sizeof(FLOAT), ALIGN));
  *R = static_cast<FLOAT *>(aligned_malloc(PARAM1*PARAM1*sizeof(FLOAT), ALIGN));

  *y = static_cast<FLOAT *>(aligned_malloc(PARAM2*sizeof(FLOAT), ALIGN));
  *init_x = static_cast<FLOAT *>(aligned_malloc(PARAM2*sizeof(FLOAT), ALIGN));
  *x = static_cast<FLOAT *>(aligned_malloc(PARAM2*sizeof(FLOAT), ALIGN));
  *M0 = static_cast<FLOAT *>(aligned_malloc(PARAM2*PARAM2*sizeof(FLOAT), ALIGN));
  *init_P = static_cast<FLOAT *>(aligned_malloc(PARAM2*PARAM2*sizeof(FLOAT), ALIGN));
  *P = static_cast<FLOAT *>(aligned_malloc(PARAM2*PARAM2*sizeof(FLOAT), ALIGN));
  *Y = static_cast<FLOAT *>(aligned_malloc(PARAM2*PARAM2*sizeof(FLOAT), ALIGN));
  *v0 = static_cast<FLOAT *>(aligned_malloc(PARAM1*sizeof(FLOAT), ALIGN));
  *M1 = static_cast<FLOAT *>(aligned_malloc(PARAM1*PARAM2*sizeof(FLOAT), ALIGN));
  *M2 = static_cast<FLOAT *>(aligned_malloc(PARAM2*PARAM1*sizeof(FLOAT), ALIGN));
//  *M2 = static_cast<FLOAT *>(aligned_malloc(PARAM1*PARAM1*sizeof(FLOAT), ALIGN));
  *M3 = static_cast<FLOAT *>(aligned_malloc(PARAM1*PARAM1*sizeof(FLOAT), ALIGN));
//  *M3 = static_cast<FLOAT *>(aligned_malloc(PARAM2*PARAM2*sizeof(FLOAT), ALIGN));


  rands(*u, PARAM0, 1);
  rands(*z, PARAM1, 1);
  rands(*x, PARAM2, 1);
  rands(*F, PARAM2, PARAM2);
  rands(*B, PARAM2, PARAM0);
  rands(*H, PARAM1, PARAM2);
  rands(*P, PARAM2, PARAM2);
  rands(*Q, PARAM2, PARAM2);
  rands(*R, PARAM1, PARAM1);

  for (int i = 0; i < PARAM2; ++i) {
	  (*P)[i*PARAM2+i] += PARAM2;
	  (*Q)[i*PARAM2+i] += PARAM2;
  }

  for (int i = 0; i < PARAM1; ++i)
    (*R)[i*PARAM1+i] += PARAM1;

  for (int i = 0; i < PARAM2; ++i) {
    for (int j = 0; j < i; ++j) {
      (*P)[i*PARAM2+j] = (*P)[j*PARAM2+i];
      (*Q)[i*PARAM2+j] = (*Q)[j*PARAM2+i];
    }
  }

  for (int i = 0; i < PARAM1; ++i)
    for (int j = 0; j < i; ++j)
  	  (*R)[i*PARAM1+j] = (*R)[j*PARAM1+i];

  memcpy(*init_x, *x, PARAM2*sizeof(FLOAT));
  memcpy(*init_P, *P, PARAM2*PARAM2*sizeof(FLOAT));

}

inline void destroy(FLOAT * F, FLOAT * B, FLOAT * u, FLOAT * Q, FLOAT * z, FLOAT * H, FLOAT * R,
		FLOAT * y, FLOAT * init_x, FLOAT * x, FLOAT * M0, FLOAT * init_P, FLOAT * P, FLOAT * Y, FLOAT * v0, FLOAT * M1, FLOAT * M2, FLOAT * M3)
{
  aligned_free(F);
  aligned_free(B);
  aligned_free(u);
  aligned_free(Q);
  aligned_free(z);
  aligned_free(H);
  aligned_free(R);
  aligned_free(y);
  aligned_free(init_x);
  aligned_free(x);
  aligned_free(M0);
  aligned_free(init_P);
  aligned_free(P);
  aligned_free(Y);
  aligned_free(v0);
  aligned_free(M1);
  aligned_free(M2);
  aligned_free(M3);
}

long validate(FLOAT const * F, FLOAT const * B, FLOAT const * u, FLOAT const * Q, FLOAT const * z, FLOAT const * H, FLOAT const * R,
		FLOAT const * y, FLOAT const * init_x, FLOAT const * x, FLOAT const * M0, FLOAT const * init_P, FLOAT const * P, FLOAT const * Y,
		FLOAT const * v0, FLOAT const * M1, FLOAT const * M2, FLOAT const * M3,
		double threshold)
{
  bool failed = false;
  std::list<string> soft_err_msgs;
  std::vector<string> errMsgs;

  _dlmwrite(u, PARAM0, 1, 0, 0, 1, string(EXEC_PATH) + "/u.txt");
  _dlmwrite(init_x, PARAM2, 1, 0, 0, 1, string(EXEC_PATH) + "/x.txt");
  _dlmwrite(z, PARAM1, 1, 0, 0, 1, string(EXEC_PATH) + "/z.txt");
  _dlmwrite(v0, PARAM1, 1, 0, 0, 1, string(EXEC_PATH) + "/v0.txt");

  _dlmwrite(F, PARAM2, PARAM2, 0, 0, PARAM2, string(EXEC_PATH) + "/F.txt");
  _dlmwrite(B, PARAM2, PARAM0, 0, 0, PARAM0, string(EXEC_PATH) + "/B.txt");
  _dlmwrite(H, PARAM1, PARAM2, 0, 0, PARAM2, string(EXEC_PATH) + "/H.txt");
  _dlmwrite(init_P, PARAM2, PARAM2, 0, 0, PARAM2, string(EXEC_PATH) + "/P.txt");
  _dlmwrite(Q, PARAM2, PARAM2, 0, 0, PARAM2, string(EXEC_PATH) + "/Q.txt");
  _dlmwrite(R, PARAM1, PARAM1, 0, 0, PARAM1, string(EXEC_PATH) + "/R.txt");
  _dlmwrite(M2, PARAM2, PARAM1, 0, 0, PARAM1, string(EXEC_PATH) + "/M2.txt");
  _dlmwrite(M3, PARAM1, PARAM1, 0, 0, PARAM1, string(EXEC_PATH) + "/M3.txt");

  string s = string("/usr/local/bin/matlab -nodisplay -nosplash -nodesktop -r \"execpath='") + string(EXEC_PATH) + "'; addpath(execpath); run('validatekf.m');\"";
  system(s.c_str());

  std::vector<FLOAT> xout(PARAM2);
  std::vector<FLOAT> Pout(PARAM2*PARAM2);

  _dlmread(&xout[0], PARAM2, 1, 0, 0, 1, string(EXEC_PATH) + "/x-out.txt");
  _dlmread(&Pout[0], PARAM2, PARAM2, 0, 0, PARAM2, string(EXEC_PATH) + "/P-out.txt");

  for (int i=0; i<PARAM2; i++) {
	  double err = rel_diff(x[i], xout[i]);
	  if (err > threshold) {
		  failed = true;
		  stringstream ss;
		  ss << "Error = " << err << ": x | at i = "<< i << " x = " << x[i] << " - xout = " << xout[i] << endl;
		  errMsgs.push_back(ss.str());
	  }
  }

  for (int i=0; i<PARAM2; i++) {
	  for (int j=i; j<PARAM2; j++) {
		  double err = rel_diff(P[i*PARAM2+j], Pout[i*PARAM2+j]);
		  if (err > SOFTERRTHRESH) {
			  stringstream ss;
			  ss << "WARNING: Error = " << err << ": P | at (i,j) = ("<< i << "," << j << ") P = " << P[i*PARAM2+j] << " - Pout = " << Pout[i*PARAM2+j] << endl;
			  soft_err_msgs.push_back(ss.str());
		  }
		  if (err > threshold) {
			  failed = true;
			  stringstream ss;
			  ss << "Error = " << err << ": P | at (i,j) = ("<< i << "," << j << ") P = " << P[i*PARAM2+j] << " - Pout = " << Pout[i*PARAM2+j] << endl;
			  errMsgs.push_back(ss.str());
		  }
	  }
  }

  dumpList(soft_err_msgs, string(EXEC_PATH) + "/soft_errors.txt");

  if(failed)
    for(std::vector<string>::const_iterator i = errMsgs.begin(); i != errMsgs.end(); i++)
      cout << *i;

  return failed;

}


int test()
{

#ifndef OW
  FLOAT * S, * U;
#else
  FLOAT * F, * B, * u, * Q, * z, * H, * R, * y, * init_x, * x, * M0, * init_P, * P, * Y, * v0, * M1, * M2, * M3;
#endif
  long retCode = 0;

#ifndef OW
  build(&S, &U);
#else
  build(&F, &B, &u, &Q, &z, &H, &R,	&y, &init_x, &x, &M0, &init_P, &P, &Y, &v0, &M1, &M2, &M3);
#endif

#ifdef VALIDATE
#ifndef OW
  kernel(S, U);
  retCode = validate(S,U, ERRTHRESH);
#else
  kernel(F, B, u, Q, z, H, R, y, x, M0, P, Y, v0, M1, M2, M3);
  retCode = validate(F, B, u, Q, z, H, R, y, init_x, x, M0, init_P, P, Y, v0, M1, M2, M3, ERRTHRESH);
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
		kernel(F, B, u, Q, z, H, R, y, x, M0, P, Y, v0, M1, M2, M3);
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
    	  std::vector<FLOAT> tx(init_x, init_x+PARAM2);
    	  std::vector<FLOAT> tP(init_P, init_P+PARAM2*PARAM2);
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
    	  std::vector<FLOAT> tx(init_x, init_x+PARAM2);
    	  std::vector<FLOAT> tP(init_P, init_P+PARAM2*PARAM2);
    	  kernel(F, B, u, Q, z, H, R, y, &tx[0], M0, &tP[0], Y, v0, M1, M2, M3);
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

  double flops = double(PARAM1)*PARAM1*PARAM1/3. + 3.*PARAM1*PARAM1*PARAM2 + 2.*PARAM1*PARAM1 + 5.*PARAM1*PARAM2*PARAM2 + 4.*PARAM1*PARAM2 + 2.*PARAM0*PARAM2 + 3.*PARAM2*PARAM2*PARAM2 + 2.*PARAM2*PARAM2;
//  double flops = double(PARAM1)*PARAM1*PARAM1/3. + 3.*PARAM1*PARAM1*PARAM2 + 4.*PARAM1*PARAM2*PARAM2 + 4.*PARAM1*PARAM2 + 2.*PARAM0*PARAM2 + 4.*PARAM2*PARAM2*PARAM2 + 2.*PARAM2*PARAM2;

#ifdef OW
  start = start_tsc();
  for(size_t i = 0; i < num_runs; i++) {
	  std::vector<FLOAT> tx(init_x, init_x+PARAM2);
	  std::vector<FLOAT> tP(init_P, init_P+PARAM2*PARAM2);
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
    	  std::vector<FLOAT> tx(init_x, init_x+PARAM2);
    	  std::vector<FLOAT> tP(init_P, init_P+PARAM2*PARAM2);
    	  kernel(F, B, u, Q, z, H, R, y, &tx[0], M0, &tP[0], Y, v0, M1, M2, M3);
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
  destroy(S, U);
#else
  destroy(F, B, u, Q, z, H, R, y, init_x, x, M0, init_P, P, Y, v0, M1, M2, M3);
#endif

  return retCode;
}
