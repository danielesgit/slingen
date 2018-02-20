/*
 * ltrtri_tester.h
 *
 * Computes L = L^-1
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

#include <mkl.h>

#include "tsc.h"
#include "helpers.h"
#include "CommonDefs.h"

#include "params.h"

#if TYPE == FLT
#define FCALL LAPACKE_strtri
#else
#define FCALL LAPACKE_dtrtri
#endif

#define LAPACK_MAT_LAYOUT LAPACK_ROW_MAJOR
//#define LAPACK_MAT_LAYOUT LAPACK_COL_MAJOR

/*
 * PARAM0 -> M
 */

inline void build(FLOAT ** L)
{
  srand(time(NULL));

  *L = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));

  rands(*L, PARAM0, PARAM0);

  for (int i = 0; i < PARAM0; ++i)
	  (*L)[i*PARAM0+i] += PARAM0;

}

inline void destroy(FLOAT * L)
{
  aligned_free(L);
}

long validate(FLOAT const * L, double threshold)
{
  bool success = true;
  std::vector<string> errMsgs;
  std::vector<FLOAT> tL(L, L+PARAM0*PARAM0);
  long retvalue = (long)FCALL(LAPACK_MAT_LAYOUT, 'L', 'N', PARAM0, &tL[0], PARAM0);

  if (retvalue > 0) {
	  cout << "The "<< retvalue << "-th diagonal element of L is zero, L is singular, and the inversion could not be completed." << endl;
	  return retvalue;
  } else if (retvalue < 0) {
	  cout << "Parameter "<< retvalue << " had an illegal value." << endl;
	  return retvalue;
  }

  return !success;

}


int test()
{

  FLOAT * L;
  myInt64 start, end, overhead, overhead_tsc;
  double cycles = 0.;
  size_t num_runs = RUNS, multiplier = 1;
  long retCode = 0;

  build(&L);
#ifdef VALIDATE
  retCode = validate(L, ERRTHRESH);
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

      start = start_tsc();
      for(size_t i = 0; i < num_runs; i++) {
    	  std::vector<FLOAT> tL(L, L+PARAM0*PARAM0);
      }
      end = stop_tsc(start);
      overhead = overhead_tsc + end;

      start = start_tsc();
      for(size_t i = 0; i < num_runs; i++) {
    	  std::vector<FLOAT> tL(L, L+PARAM0*PARAM0);
    	  FCALL(LAPACK_MAT_LAYOUT, 'L', 'N', PARAM0, &tL[0], PARAM0);
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
	  std::vector<FLOAT> tL(L, L+PARAM0*PARAM0);
  }
  end = stop_tsc(start);
  overhead = overhead_tsc + end;

  for (int k = 0; k < Rep; k++) {

      start = start_tsc();
      for (int i = 0; i < num_runs; ++i) {
    	  std::vector<FLOAT> tL(L, L+PARAM0*PARAM0);
    	  FCALL(LAPACK_MAT_LAYOUT, 'L', 'N', PARAM0, &tL[0], PARAM0);
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

  destroy(L);

  return retCode;
}
