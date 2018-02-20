/*
 * main.cpp
 *
 *  Created on: May 2, 2012
 *      Author: danieles
 */

#include <iostream>
#include <vector>
#include <cstdlib>
#include <string>
#include <algorithm>

// TESTER FUNCTIONS
#include "testers.h" // Must include header with definitions and implementation of tester functions
					 // and header with kernel implementation

using namespace std;

int main(int argc, char * argv[])
{
//  PerfRes perf;

  srand(time(NULL));

  int retCode = test();

//#ifndef VERIFY
//  string out_filename = (argc>1) ? argv[1] : string(EXEC_PATH) + "/outcome";
//  dump(perf, out_filename);
//#endif

  return retCode;
}


