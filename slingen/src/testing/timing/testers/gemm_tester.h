/*
 * gemm_tester.h
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
#include "tsc.h"
#endif

#include "helpers.h"
#include "CommonDefs.h"

#include "kernels/gemm_kernel.h"


/*
 * PARAM0 -> M
 * PARAM1 -> K
 * PARAM2 -> N
 */

inline void build(FLOAT ** A, FLOAT ** B, FLOAT ** initC, FLOAT ** C)
{
  srand(time(NULL));

  *A = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM1*sizeof(FLOAT), ALIGN));
  *B = static_cast<FLOAT *>(aligned_malloc(PARAM1*PARAM2*sizeof(FLOAT), ALIGN));
  *initC = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM2*sizeof(FLOAT), ALIGN));
  *C = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM2*sizeof(FLOAT), ALIGN));

  rands(*A, PARAM0, PARAM1);
  rands(*B, PARAM1, PARAM2);
  rands(*initC, PARAM0, PARAM2);
  memcpy(*C, *initC, PARAM0*PARAM2*sizeof(FLOAT));
}

inline void destroy(FLOAT * A, FLOAT * B, FLOAT * initC, FLOAT * C)
{
  aligned_free(A);
  aligned_free(B);
  aligned_free(initC);
  aligned_free(C);
}

int validate(FLOAT * A, FLOAT * B, FLOAT * initC, FLOAT * C, double threshold)
{

  bool success = true;
  std::vector<FLOAT> temp(PARAM0*PARAM2, 0.);

  std::vector<string> errMsgs;

  for (int i = 0; i < PARAM0; ++i) {
      for (int j = 0; j < PARAM2; ++j) {
    	  for (int k = 0; k < PARAM1; ++k) {
    		  temp[i*PARAM2 + j] += A[i*PARAM1 + k] * B[k*PARAM2 + j];
    	  }
      }
  }

  for (int i = 0; i < PARAM0; ++i) {
	  for (int j = 0; j < PARAM2; ++j) {
		  temp[i*PARAM2+j] += initC[i*PARAM2+j];

		  double err = fabs(C[i*PARAM2+j] - temp[i*PARAM2+j])/temp[i*PARAM2+j];
		  if(err > threshold)
		  {
			  success = false;
			  stringstream ss;
			  ss << "Error at (" << i << ", " << j << "): ";
			  ss << "C = " << C[i*PARAM2+j] << "\t-- Cref = " << temp[i*PARAM2+j] << "\t-- Err = " << err << endl;
			  errMsgs.push_back(ss.str());
		  }
	  }
  }

  if(!success)
    for(std::vector<string>::const_iterator i = errMsgs.begin(); i != errMsgs.end(); i++)
      cout << *i;

  return !success;
}

/**
 * Test for gemm kernels
 */

int test()
{

  FLOAT * A, * B, * initC, * C;
  int retCode = 0;

  build(&A, &B, &initC, &C);
#ifdef VALIDATE
  kernel(A,B,C);
  retCode = validate(A,B,initC,C, ERRTHRESH);
  if (retCode > 0) {
	cout << "Validation failed." << endl;
	return retCode;
  }
#endif

#ifdef TEST
  //Cache warm-up
  // RDTSCP reads ts register guaranteeing that the execution of all the code
  // we wanted to measure is completed. This way we avoid including the
  // execution of a CPUID in between. The last CPUID guarantees no other
  // instruction can be scheduled before it (and so also before RDTSCP)
  myInt64 start, end, overhead;
  double cycles = 0.;
  size_t num_runs = RUNS, multiplier = 1;

  init_tsc();
  overhead = get_tsc_overhead();

  do{
      num_runs = num_runs * multiplier;
      start = start_tsc();
      for(size_t i = 0; i < num_runs; i++) {
    	  kernel(A,B,C);
      }
      end = stop_tsc(start);
      if (end > overhead)
          end -= overhead;

      cycles = (double) end;
      multiplier = ceil (  (CYCLES_REQUIRED) / (cycles)  + 1.0 );

  }while (multiplier > 2);

  list< double > cycleList, flopList;
  size_t Rep = NUMREP;

  double flops = 2.*PARAM0*PARAM2*PARAM1;

  for (int k = 0; k < Rep; k++) {

	  memcpy(C, initC, PARAM0*PARAM2*sizeof(FLOAT));

      start = start_tsc();
      for (int i = 0; i < num_runs; ++i) {
    	  kernel(A,B,C);
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
  
  destroy(A, B, initC, C);

  return retCode;
}
