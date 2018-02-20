/*
 * helpers.h
 *
 *  Created on: May 2, 2012
 *      Author: danieles
 */

#pragma once

#include <iostream>
#include <iomanip>
#include <fstream>
#include <string>
#include <sstream>
#include <list>
#include <vector>
#include <cstdlib>
#include <assert.h>
#if __cplusplus <= 199711L
#include <stdint.h>
#else
// C++11 or later
#include <cstdint>
#endif

#include "CommonDefs.h"

#ifdef TEST
#ifndef ERM
#include "tsc.h"

static void swap(myInt64 *x, myInt64 *y) {
	myInt64 temp;
	temp = *x;
	*x = *y;
	*y = temp;
}

/* Median of 3 */
myInt64 get_tsc_overhead(void) {
	myInt64 t1, t2, t3, t;
	t = start_tsc(); stop_tsc(t);
	t = start_tsc(); stop_tsc(t);
	t = start_tsc(); stop_tsc(t);
	t1 = start_tsc(); t1 = stop_tsc(t1);
	t2 = start_tsc(); t2 = stop_tsc(t2);
	t3 = start_tsc(); t3 = stop_tsc(t3);
	if (t1 > t2)
		swap(&t1, &t2);
	if (t2 > t3)
		swap(&t2, &t3);
	if (t1 > t2)
		swap(&t1, &t2);
	/*
	if (t2 - t1 < t3 - t2)
		t = t1 + (t2 - t1) / 2;
	else
		t = t2 + (t3 - t2) / 2;
	 */
	return t2;
}
#endif
#endif


using namespace std;

template<typename vType>
union vtoa {
	vType v;
	FLOAT a[4];
};

void rands(FLOAT * m, size_t row, size_t col)
{
	for (size_t i = 0; i < row*col; ++i)  m[i] = (FLOAT)(rand())/RAND_MAX + 1;
}

void zeros(FLOAT * m, size_t row, size_t col)
{
	for (size_t i = 0; i < row*col; ++i)  m[i] = 0.;
}

void dumpList(std::list< double > const & l, string const & filename)
{
	ofstream outfile;
	outfile.open(filename.c_str(), ios_base::out);

	std::list< double >::const_iterator it = l.begin();
	outfile << *it;
	for (++it; it != l.end(); ++it)
		outfile << " " << *it;

	outfile.close();
}

template <typename vType>
void _printVec(ostream& out, vType v, string title)
{
	out << std::setprecision(15);

	vtoa<vType> u;
	u.v = v;
	out << "=========" << endl;
	out << title << " = [" << endl;
	for (size_t i = 0; i < 4; ++i) {
		out << u.a[i] << "\t";
	}
	out << "]" << endl;
	out << "=========" << endl << endl;
}

void _dlmwrite(FLOAT const * m, size_t const row, size_t const col, size_t const ox, size_t const oy, size_t const ldm, string fname)
{
	ofstream outfile;
	outfile.open(fname.c_str(), ios_base::out);

	outfile << std::setprecision(15);

	for (size_t i = ox; i < ox+row; ++i) {
		for (size_t j = oy; j < oy+col-1; ++j) {
			outfile << m[i*ldm + j] << ",";
		}
		outfile << m[i*ldm + oy+col-1] << endl;
	}
	outfile.close();
}

void _dlmread(FLOAT * m, size_t const row, size_t const col, size_t const ox, size_t const oy, size_t const ldm, string fname)
{
	ifstream infile;
	infile.open(fname.c_str(), ios_base::in);
	string line, value;

	while(getline(infile, line)) {
		stringstream linestream(line);
		while(getline(linestream, value, ',')) {
			*m = atof(value.c_str());
			++m;
		}
	}

	infile.close();
}

void _printM(ostream& out, FLOAT const * m, size_t const row, size_t const col, size_t const ox, size_t const oy, size_t const ldm, string title)
{
	out << std::setprecision(15);

	out << "=========" << endl;
	out << title << " = [" << endl;
	for (size_t i = ox; i < ox+row; ++i) {
		for (size_t j = oy; j < oy+col; ++j) {
			out << m[i*ldm + j] << "\t";
		}
		out << ";" << endl;
	}
	out << "]" << endl;
	out << "=========" << endl << endl;
}

void _printV(std::vector<FLOAT>& m, size_t const row, size_t const col, string title)
{
	cout << "=========" << endl;
	cout << title << ":" << endl;
	for (size_t i = 0; i < row; ++i) {
		cout << "[ ";
		for (size_t j = 0; j < col; ++j) {
			cout << m[i*col + j] << "\t";
		}
		cout << "]" << endl;
	}
	cout << "=========" << endl << endl;
}

/* Credits to http://cottonvibes.blogspot.ch/2011/01/dynamically-allocate-aligned-memory.html */
// Alignment must be power of 2 (1,2,4,8,16...2^15)
void* aligned_malloc(size_t size, size_t alignment, size_t offset) {
	assert(alignment <= 0x8000);
	uintptr_t r = (uintptr_t)malloc(size + --alignment + 2 + offset);
	uintptr_t o = ((r + 2 + alignment) & ~(uintptr_t)alignment) + offset;
	if (!r) return NULL;
	((uint16_t*)o)[-1] = (uint16_t)(o-r);
	return (void*)o;
}

void* aligned_malloc(size_t size, size_t alignment) {
	return aligned_malloc(size, alignment, 0);
}

void aligned_free(void* p) {
	if (!p) return;
	free((void*)((uintptr_t)p-((uint16_t*)p)[-1]));
}

