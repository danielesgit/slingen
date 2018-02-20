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
#include <algorithm>

#include "params.h"

#include <mkl.h>

#include "tsc.h"
#include "helpers.h"
#include "CommonDefs.h"

#if TYPE == FLT
#define FCALL LAPACKE_spotrf
#else
#define FCALL LAPACKE_dpotrf
#endif

#define MAT_LAYOUT LAPACK_ROW_MAJOR
//#define MAT_LAYOUT LAPACK_COL_MAJOR

/*
 * PARAM0 -> M
 */

inline void build(FLOAT ** S)
{
  srand(time(NULL));

  *S = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));

  rands(*S, PARAM0, PARAM0);

  for (int i = 0; i < PARAM0; ++i)
	  (*S)[i*PARAM0+i] += PARAM0;

}

inline void destroy(FLOAT * S)
{
  aligned_free(S);
}

long validate(FLOAT const * S, double threshold)
{
  bool success = true;

  std::vector<FLOAT> tU(S, S+PARAM0*PARAM0);
  long retvalue = (long)FCALL(MAT_LAYOUT, 'U', PARAM0, &tU[0], PARAM0);

  if (retvalue > 0) {
	  cout << "The leading minor of order "<< retvalue << " (and therefore the matrix A itself) is not positive-definite, and the factorization could not be completed. This may indicate an error in forming the matrix A." << endl;
	  return retvalue;
  } else if (retvalue < 0) {
	  cout << "Parameter "<< retvalue << " had an illegal value." << endl;
	  return retvalue;
  }

  return !success;

}

int test()
{

  FLOAT * S;
  myInt64 start, end, overhead_tsc, overhead;
  double cycles = 0.;
  size_t num_runs = RUNS, multiplier = 1;
  long retCode = 0;

  build(&S);
#ifdef VALIDATE
  retCode = validate(S, ERRTHRESH);
  if (retCode) {
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
    	  std::vector<FLOAT> tU(S, S+PARAM0*PARAM0);
      }
      end = stop_tsc(start);
      overhead = overhead_tsc + end;

      start = start_tsc();
      for(size_t i = 0; i < num_runs; i++) {
    	  std::vector<FLOAT> tU(S, S+PARAM0*PARAM0);
    	  FCALL(MAT_LAYOUT, 'U', PARAM0, &tU[0], PARAM0);
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
	  std::vector<FLOAT> tU(S, S+PARAM0*PARAM0);
  }
  end = stop_tsc(start);
  overhead = overhead_tsc + end;

  for (int k = 0; k < Rep; k++) {

      start = start_tsc();
      for (int i = 0; i < num_runs; ++i) {
    	  std::vector<FLOAT> tU(S, S+PARAM0*PARAM0);
    	  FCALL(MAT_LAYOUT, 'U', PARAM0, &tU[0], PARAM0);
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

  destroy(S);

  return retCode;
}
