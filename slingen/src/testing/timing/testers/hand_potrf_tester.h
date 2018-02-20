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

#ifdef TEST
#ifndef ERM
#include "tsc.h"
#endif
#endif

#include "params.h"

#include "helpers.h"
#include "CommonDefs.h"


#define OW

double max_norm(FLOAT const * M) {

	double res = M[0];

	for (int i = 0; i < PARAM0; ++i)
		for (int j = i; j < PARAM0; ++j)
			if (M[i*PARAM0+j] > res)
				res = M[i*PARAM0+j];

	return res;
}

double frob_norm(FLOAT const * M) {

	double res = 0;

	for (int i = 0; i < PARAM0; ++i)
		for (int j = i; j < PARAM0; ++j)
			if (j>i)
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
		for (int j = i; j < PARAM0; ++j) {
			for (int k = 0; k <= i; ++k) {
				UtU[i*PARAM0+j] += U[k*PARAM0+i]*U[k*PARAM0+j];
			}
			UtUmS[i*PARAM0+j] = UtU[i*PARAM0+j] - S[i*PARAM0+j];
		}
	}

	utums = NORM(&UtUmS[0]);
	s     = NORM(S);

	return utums/s;
}


/*
 * PARAM0 -> M
 */

#ifndef OW

inline void build(FLOAT ** S, FLOAT ** U)
{
  srand(time(NULL));

  *U = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));
  *S = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));

  rands(*S, PARAM0, PARAM0);

  for (int i = 0; i < PARAM0; ++i)
	  (*S)[i*PARAM0+i] += PARAM0;

}

inline void destroy(FLOAT * S, FLOAT * U)
{
  aligned_free(S);
  aligned_free(U);
}

long validate(FLOAT const * S, FLOAT const * U, double threshold)
{
  bool success = true;
  std::vector<string> errMsgs;

  double err = func_err(S, U);
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

#else

static __attribute__((noinline)) void kernel(FLOAT * S)
{
  FLOAT t[PARAM0];

  for (int i = 0; i < PARAM0; ++i) {
	  if(i>0) {
		  for(int j=i; j<PARAM0; j++) {
			  t[j] = 0;
			  for(int k=0; k<i; k++)
				  t[j] += S[k*PARAM0+i]*S[k*PARAM0+j];
		  }
		  for(int j=i; j<PARAM0; ++j)
	  		  S[i*PARAM0+j] -= t[j];
	  }
	  S[i*PARAM0+i] = sqrt(S[i*PARAM0+i]);
  	  for(int j=i+1; j<PARAM0; ++j)
  		  S[i*PARAM0+j] /= S[i*PARAM0+i];
  }

}

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

#endif


int test()
{

#ifndef OW
  FLOAT * S, * U;
#else
  FLOAT * S, * initS;
#endif
  long retCode = 0;

#ifndef OW
  build(&S, &U);
#else
  build(&initS, &S);
#endif

#ifdef VALIDATE
#ifndef OW
  kernel(S, U);
  retCode = validate(S,U, ERRTHRESH);
#else
  kernel(S);
  retCode = validate(initS, S, ERRTHRESH);
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
#ifndef OW
		kernel(S, U);
#else
		kernel(S);
#endif
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
    	  std::vector<FLOAT> tS(initS, initS+PARAM0*PARAM0);
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
    	  std::vector<FLOAT> tS(initS, initS+PARAM0*PARAM0);
    	  kernel(&tS[0]);
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

  double flops = (PARAM0*PARAM0*PARAM0)/3.;

#ifdef OW
  start = start_tsc();
  for(size_t i = 0; i < num_runs; i++) {
	  std::vector<FLOAT> tS(initS, initS+PARAM0*PARAM0);
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
    	  std::vector<FLOAT> tS(initS, initS+PARAM0*PARAM0);
    	  kernel(&tS[0]);
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
  destroy(initS, S);
#endif

  return retCode;
}
