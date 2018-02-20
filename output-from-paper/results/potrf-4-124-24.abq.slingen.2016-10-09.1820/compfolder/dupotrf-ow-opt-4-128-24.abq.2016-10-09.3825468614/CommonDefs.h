/*
 * CommonSettings.h
 *
 *  Created on: Jan 23, 2012
 *      Author: danieles
 */

#pragma once

// Define how many times a test should be repeated, the cpu freq and
// whether to verify the computation at the end of every test or not
#define RUNS     2
#define CYCLES_REQUIRED 1e7

//Define what data type to use
#define FLT 0
#define DBL 1

//#define ALIGN 16

#if TYPE == FLT
#define FLOAT float
#else
#define FLOAT double
#endif
