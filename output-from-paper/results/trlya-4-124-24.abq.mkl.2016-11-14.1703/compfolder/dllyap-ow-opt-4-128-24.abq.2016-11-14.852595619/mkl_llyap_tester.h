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

#include <mkl.h>

#include "params.h"

#include "tsc.h"
#include "helpers.h"
#include "CommonDefs.h"

#if TYPE == FLT
#define FQR	LAPACKE_shseqr
#define FCALL LAPACKE_strsyl
#else
#define FQR	LAPACKE_dhseqr
#define FCALL LAPACKE_dtrsyl
#endif

#define LAPACK_MAT_LAYOUT LAPACK_ROW_MAJOR
//#define LAPACK_MAT_LAYOUT LAPACK_COL_MAJOR

/*
 * PARAM0 -> M
 */

inline void build(FLOAT ** C, FLOAT ** L)
{
  srand(time(NULL));

  *L = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));
  *C = static_cast<FLOAT *>(aligned_malloc(PARAM0*PARAM0*sizeof(FLOAT), ALIGN));

  std::vector<FLOAT> ZL(PARAM0*PARAM0);
  std::vector<FLOAT> wrL(PARAM0);
  std::vector<FLOAT> wiL(PARAM0);

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

  for (int i = 0; i < PARAM0-1; ++i)
    (*L)[(i+1)*PARAM0 + i] = 0.;


  // Computing Schur form of L^T
  long retvalue = (long)FQR(LAPACK_MAT_LAYOUT, 'S', 'I', PARAM0, 1, PARAM0, *L, PARAM0, &wrL[0], &wiL[0], &ZL[0], PARAM0);

  if (retvalue > 0) {
	  cout << "Schur form of L^T. Positive ret. value." << endl;
	  cout << "  Ret = " << retvalue << endl;
	  exit(EXIT_FAILURE);
  } else if (retvalue < 0) {
	  cout << "Schur form of L^T. Parameter "<< retvalue << " had an illegal value." << endl;
	  exit(EXIT_FAILURE);
  }

}

inline void destroy(FLOAT * C, FLOAT * L)
{
  aligned_free(L);
  aligned_free(C);
}

long validate(FLOAT * C, FLOAT * L, double threshold)
{
  bool failed = false;

  double alpha;
  std::vector<FLOAT> tC(C, C+PARAM0*PARAM0);

  long retvalue = (long)FCALL(LAPACK_MAT_LAYOUT, 'T', 'N', 1, PARAM0, PARAM0, L, PARAM0, L, PARAM0, &tC[0], PARAM0, &alpha);

  if (retvalue == 1) {
	  cout << "A and B have common or close eigenvalues; perturbed values were used to solve the equation." << endl;
	  cout << "  Alpha = " << alpha << endl;
	  exit(EXIT_FAILURE);
  } else if (retvalue < 0) {
	  cout << "Parameter "<< retvalue << " had an illegal value." << endl;
	  exit(EXIT_FAILURE);
  }

  return failed;

}


int test()
{

  FLOAT * L, * C;
  myInt64 start, end, overhead, overhead_tsc;
  double cycles = 0.;
  size_t num_runs = RUNS, multiplier = 1;
  long retCode = 0;

  build(&C, &L);
#ifdef VALIDATE
  retCode = validate(C,L, ERRTHRESH);
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

  double alpha;

  do{
      num_runs = num_runs * multiplier;
      std::vector<FLOAT> tC(C, C+PARAM0*PARAM0);

//      start = start_tsc();
//      for(size_t i = 0; i < num_runs; i++) {
//    	  std::vector<FLOAT> tC(C, C+PARAM0*PARAM0);
//      }
//      end = stop_tsc(start);
//      overhead = overhead_tsc + end;

      start = start_tsc();
      for(size_t i = 0; i < num_runs; i++) {
//    	  std::vector<FLOAT> tC(C, C+PARAM0*PARAM0);
    	  FCALL(LAPACK_MAT_LAYOUT, 'T', 'N', 1, PARAM0, PARAM0, L, PARAM0, L, PARAM0, &tC[0], PARAM0, &alpha);
      }
      end = stop_tsc(start);
      if (end > overhead)
          end -= overhead;

      cycles = (double) end;
      multiplier = ceil (  (CYCLES_REQUIRED) / (cycles)  + 1.0 );

  }while (multiplier > 2);

  list< double > cycleList, flopList;
  size_t Rep = NUMREP;

  double flops = PARAM0*PARAM0*PARAM0;

//  start = start_tsc();
//  for(size_t i = 0; i < num_runs; i++) {
//	  std::vector<FLOAT> tC(C, C+PARAM0*PARAM0);
//  }
//  end = stop_tsc(start);
//  overhead = overhead_tsc + end;
  overhead = overhead_tsc;

  for (int k = 0; k < Rep; k++) {

	  std::vector<FLOAT> tC(C, C+PARAM0*PARAM0);

      start = start_tsc();
      for (int i = 0; i < num_runs; ++i) {
//    	  std::vector<FLOAT> tC(C, C+PARAM0*PARAM0);
    	  FCALL(LAPACK_MAT_LAYOUT, 'T', 'N', 1, PARAM0, PARAM0, L, PARAM0, L, PARAM0, &tC[0], PARAM0, &alpha);
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

  destroy(C, L);

  return retCode;

}
