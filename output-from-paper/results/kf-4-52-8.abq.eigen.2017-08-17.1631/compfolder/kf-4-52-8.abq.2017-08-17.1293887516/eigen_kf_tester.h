/*
 * kf_tester.h
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

#include "params.h"

#include <Eigen/Dense>

#ifdef TEST
#ifndef ERM
#include "tsc.h"
#endif
#endif

#include "helpers.h"
#include "CommonDefs.h"

using namespace std;
using namespace Eigen;

typedef Map< Matrix<FLOAT, PARAM0, 1> > Vec_m;
typedef Map< Matrix<FLOAT, PARAM1, 1> > Vec_k;
typedef Map< Matrix<FLOAT, PARAM2, 1> > Vec_n;

typedef Map< Matrix<FLOAT, PARAM1, PARAM1, RowMajor> > Mat_kk;
typedef Map< Matrix<FLOAT, PARAM2, PARAM2, RowMajor> > Mat_nn;
typedef Map< Matrix<FLOAT, PARAM2, PARAM0, RowMajor> > Mat_nm;
typedef Map< Matrix<FLOAT, PARAM1, PARAM2, RowMajor> > Mat_kn;
typedef Map< Matrix<FLOAT, PARAM2, PARAM1, RowMajor> > Mat_nk;

/*
 * PARAM0 -> M
 * PARAM1 -> K
 * PARAM2 -> N
 */

static __attribute__((noinline)) void kernel(const Mat_nn& F, const Mat_nm& B, const Vec_m& u, const Mat_nn& Q, const Vec_k& z,
		const Mat_kn& H, const Mat_kk& R, Vec_n& y, Vec_n& x, Mat_kk& L, Mat_nn& P, Mat_nn& Y, Vec_k& v0, Mat_kn& M1, Mat_nk& M2,
		Mat_kk& M3) {

	//	y = F*x + B*u;
	//	Y = F*P*F' + Q;
	y = F*x + B*u;
	Y = F*P.selfadjointView<Upper>()*F.transpose() + (L=Q.selfadjointView<Upper>());
	//	v0 = z - H*y;
	//	M1 = H*Y;
	//	M2 = Y*H';
	//	M3 = M1*H' + R;
	v0 = z - H*y;
	M1 = H*Y.selfadjointView<Upper>();
	M2 = Y.selfadjointView<Upper>()*H.transpose();
	M3 = M1*H.transpose() + (L=R.selfadjointView<Upper>());
	//	U = chol(M3);
	//	v1 = U'\v0;
	//	v2 = U\v1;
	LLT< Ref<Mat_kk>, Upper > lltOfS(M3);
	L.triangularView<Lower>() = M3.transpose();
	L.triangularView<Lower>().solveInPlace(v0);
	M3.triangularView<Upper>().solveInPlace(v0);
	//	M4 = U'\M1;
	//	M5 = U\M4;
	L.triangularView<Lower>().solveInPlace(M1);
	M3.triangularView<Upper>().solveInPlace(M1);
	//	x = y + M2*v2;
	//	P = Y - M2*M5;
	x = y + M2*v0;
	P = (L=Y.selfadjointView<Upper>()) - M2*M1;
}

double rel_diff(FLOAT a, FLOAT b) {

	using std::max;
	double c = fabs(a), d = fabs(b);
	double m = max(c, d);

	return (m == 0.) ? 0. : fabs(a-b)/m;
}

inline void build(FLOAT ** F, FLOAT ** B, FLOAT ** u, FLOAT ** Q, FLOAT ** z, FLOAT ** H, FLOAT ** R,
		FLOAT ** y, FLOAT ** init_x, FLOAT ** x, FLOAT ** L, FLOAT ** init_P, FLOAT ** P, FLOAT ** Y, FLOAT ** v0, FLOAT ** M1, FLOAT ** M2, FLOAT ** M3)
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
	*L = static_cast<FLOAT *>(aligned_malloc(PARAM1*PARAM1*sizeof(FLOAT), ALIGN));
	*init_P = static_cast<FLOAT *>(aligned_malloc(PARAM2*PARAM2*sizeof(FLOAT), ALIGN));
	*P = static_cast<FLOAT *>(aligned_malloc(PARAM2*PARAM2*sizeof(FLOAT), ALIGN));
	*Y = static_cast<FLOAT *>(aligned_malloc(PARAM2*PARAM2*sizeof(FLOAT), ALIGN));
	*v0 = static_cast<FLOAT *>(aligned_malloc(PARAM1*sizeof(FLOAT), ALIGN));
	*M1 = static_cast<FLOAT *>(aligned_malloc(PARAM1*PARAM2*sizeof(FLOAT), ALIGN));
	*M2 = static_cast<FLOAT *>(aligned_malloc(PARAM2*PARAM1*sizeof(FLOAT), ALIGN));
	*M3 = static_cast<FLOAT *>(aligned_malloc(PARAM1*PARAM1*sizeof(FLOAT), ALIGN));


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
		FLOAT * y, FLOAT * init_x, FLOAT * x, FLOAT * L, FLOAT * init_P, FLOAT * P, FLOAT * Y, FLOAT * v0, FLOAT * M1, FLOAT * M2, FLOAT * M3)
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
	aligned_free(L);
	aligned_free(init_P);
	aligned_free(P);
	aligned_free(Y);
	aligned_free(v0);
	aligned_free(M1);
	aligned_free(M2);
	aligned_free(M3);
}

long validate(FLOAT const * F, FLOAT const * B, FLOAT const * u, FLOAT const * Q, FLOAT const * z, FLOAT const * H, FLOAT const * R,
		FLOAT const * y, FLOAT const * init_x, FLOAT const * x, FLOAT const * L, FLOAT const * init_P, FLOAT const * P, FLOAT const * Y,
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

	FLOAT * aF, * aB, * au, * aQ, * az, * aH, * aR, * ay, * init_x, * ax, * aL, * init_P, * aP, * aY, * av0, * aM1, * aM2, * aM3;
	long retCode = 0;

	build(&aF, &aB, &au, &aQ, &az, &aH, &aR, &ay, &init_x, &ax, &aL, &init_P, &aP, &aY, &av0, &aM1, &aM2, &aM3);

	Vec_m u(au);
	Vec_k z(az), v0(av0);
	Vec_n x(ax), y(ay);
	Mat_kk R(aR), L(aL), M3(aM3);
	Mat_nn F(aF), Q(aQ), P(aP), Y(aY);
	Mat_kn H(aH), M1(aM1);
	Mat_nk M2(aM2);
	Mat_nm B(aB);

#ifdef VALIDATE
	kernel(F, B, u, Q, z, H, R, y, x, L, P, Y, v0, M1, M2, M3);
	retCode = validate(aF, aB, au, aQ, az, aH, aR, ay, init_x, ax, aL, init_P, aP, aY, av0, aM1, aM2, aM3, ERRTHRESH);

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
		kernel(F, B, u, Q, z, H, R, y, x, L, P, Y, v0, M1, M2, M3);
#endif

#ifndef ERM
	myInt64 start, end, overhead, overhead_tsc;
	double cycles = 0.;
	size_t num_runs = RUNS, multiplier = 1;

	init_tsc();
	overhead_tsc = get_tsc_overhead();

	do{
		num_runs = num_runs * multiplier;

		start = start_tsc();
		for(size_t i = 0; i < num_runs; i++) {
			memcpy(ax, init_x, PARAM2*sizeof(FLOAT));
			memcpy(aP, init_P, PARAM2*PARAM2*sizeof(FLOAT));
		}
		end = stop_tsc(start);
		overhead = overhead_tsc + end;

		start = start_tsc();
		for(size_t i = 0; i < num_runs; i++) {
			memcpy(ax, init_x, PARAM2*sizeof(FLOAT));
			memcpy(aP, init_P, PARAM2*PARAM2*sizeof(FLOAT));
			kernel(F, B, u, Q, z, H, R, y, x, L, P, Y, v0, M1, M2, M3);
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

	start = start_tsc();
	for(size_t i = 0; i < num_runs; i++) {
		memcpy(ax, init_x, PARAM2*sizeof(FLOAT));
		memcpy(aP, init_P, PARAM2*PARAM2*sizeof(FLOAT));
	}
	end = stop_tsc(start);
	overhead = overhead_tsc + end;

	for (int k = 0; k < Rep; k++) {

		start = start_tsc();
		for (int i = 0; i < num_runs; ++i) {
			memcpy(ax, init_x, PARAM2*sizeof(FLOAT));
			memcpy(aP, init_P, PARAM2*PARAM2*sizeof(FLOAT));
			kernel(F, B, u, Q, z, H, R, y, x, L, P, Y, v0, M1, M2, M3);
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

destroy(aF, aB, au, aQ, az, aH, aR, ay, init_x, ax, aL, init_P, aP, aY, av0, aM1, aM2, aM3);

return retCode;
}
