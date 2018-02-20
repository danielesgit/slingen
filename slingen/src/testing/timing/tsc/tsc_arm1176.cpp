#include <stdio.h>
#include "tsc.h"

#define PMCR_MASK 0x00000079

/**
* Read the PMCR and return its value.
**/
inline INT32 armv6_pmcr_read(void) {
	INT32 val;
	asm volatile("MRC   p15, 0, %0, c15, c12, 0" : "=r"(val));
	return val;
}

/**
* Write the PMCR using the specified value.
**/
inline void armv6_pmcr_write(INT32 val) {
	asm volatile("MCR   p15, 0, %0, c15, c12, 0" : : "r"(val));
}

inline void armv6_pmcr_init(void) {
	armv6_pmcr_write(0x00000000);
}


inline void disable_ccnt(void) {
	INT32 value;
	value = armv6_pmcr_read();
	armv6_pmcr_write((value & PMCR_MASK) & 0xfffffffe);
}

inline void enable_ccnt(void) {
	INT32 value;
	value = armv6_pmcr_read();
	value = ((value  & PMCR_MASK) | 0x00000001);
	armv6_pmcr_write(value);
}

inline void ccnt_divider(INT32 enable_divider) {
	INT32 value;
	value = armv6_pmcr_read();
	if (enable_divider)
		armv6_pmcr_write((value & PMCR_MASK) | 0x00000008);
	else
		armv6_pmcr_write((value & PMCR_MASK) & 0xfffffff7);
}

inline void reset_ccnt(void) {
	INT32 value;
	value = armv6_pmcr_read();
	armv6_pmcr_write((value  & PMCR_MASK) | 0x00000004);
}

inline void reset_flags(void) {
	INT32 value;
	value = armv6_pmcr_read();
	armv6_pmcr_write((value  & PMCR_MASK) | 0x00000700);
}

inline INT32 read_ccnt(void) {
	INT32 cycles;
	asm volatile ("MRC     	p15, 0, %0, c15, c12, 1\n\t":"=r"(cycles));
	return cycles;
}


void init_tsc() {
	armv6_pmcr_init();			// initialize the value of the PMCR register
	ccnt_divider(1);
}

myInt64 start_tsc(void) {
    reset_flags();   		   	// Reset the overflow flags
    reset_ccnt();				// Reset CCNT
    enable_ccnt();             	// Enable CCNT
    return 0ULL;
}

myInt64 stop_tsc(myInt64 start) {
	INT32 value, cycles, overflow, divider_on;
	myInt64 real_cycles;
    disable_ccnt();            // Stop CCNT
	cycles = read_ccnt();
	value = armv6_pmcr_read();
	overflow = value & (1 << 10);
	if (overflow) {
		fprintf(stderr, "Error: CCNT had an overflow.\n");
		return 0;
	}
	divider_on = value & 0x00000008;
	if (divider_on)
		real_cycles = ((myInt64) cycles) << 6;
	else
		real_cycles = (myInt64) cycles;
    return real_cycles - start;
}
