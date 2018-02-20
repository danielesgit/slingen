#include <stdio.h>
#include "tsc.h"

inline void activate_ccnt(void) {
	ASM VOLATILE ("MRC 		p15, 0, r0, c9, c12, 0\n\t"		\
  				  "ORR     	r0, r0, #0x11\n\t"				\
  				  "MCR     	p15, 0, r0, c9, c12, 0\n\t"		\
  				  :											\
  				  :											\
  				  : "r0"
  				  );
}

inline void disable_ccnt(void) {
	ASM VOLATILE ("MCR 		p15, 0, %0, c9, c12, 2\n\t"::"r"(0x80000000));
}

inline void enable_ccnt(void) {
	ASM VOLATILE ("MCR     	p15, 0, %0, c9, c12, 1\n\t"::"r"(0x80000000));
}

/*
inline void ccnt_divider(INT32 enable_divider) {
	ASM VOLATILE ("MRC 		p15, 0, r0, c9, c12, 0\n\t"		\
				  "CMP 		%0, #0x0\n\t"					\
				  "BICEQ   	r0, r0, #0x08\n\t"				\
				  "ORRNE   	r0, r0, #0x08\n\t"				\
  				  "MCR 		p15, 0, r0, c9, c12, 0\n\t"		\
  				  :											\
				  : "r"(enable_divider)						\
				  : "r0", "cc"					
				  );
}
 */

inline void ccnt_divider(INT32 enable_divider) {
    INT32 reg;
	ASM VOLATILE ("MRC 		p15, 0, %0, c9, c12, 0\n\t":"=r"(reg));
    if (enable_divider == 0)
        reg &= 0xfffffff7;
    else
        reg |= 0x08;
    ASM VOLATILE ("MCR 		p15, 0, %0, c9, c12, 0\n\t"::"r"(reg));
}

inline void reset_ccnt(void) {
	ASM VOLATILE ("MRC 		p15, 0, r0, c9, c12, 0\n\t"		\
  				  "ORR     	r0, r0, #0x4\n\t"				\
  				  "MCR     	p15, 0, r0, c9, c12, 0\n\t"		\
  				  :											\
  				  :											\
  				  : "r0"
  				  );
}

inline INT32 read_ccnt(void) {
	INT32 cycles;
	ASM VOLATILE ("MRC     	p15, 0, %0, c9, c13, 0\n\t":"=r"(cycles));
	return cycles;
}

inline void write_flags(INT32 flags) {
	ASM VOLATILE ("MCR     	p15, 0, %0, c9, c12, 3\n\t"		\
				  "#ISB\n\t"									\
				  ::"r"(flags)								\
				  );
}

inline INT32 read_flags(void) {
	INT32 flags;
	ASM VOLATILE ("MRC     	p15, 0, %0, c9, c12, 3\n\t":"=r"(flags));
	return flags;
}

inline void reset_flags(void) {
	write_flags(0x8000000f);
}


void enable_runfast() {
	static const unsigned int x = 0x04086060;
	static const unsigned int y = 0x03000000;
	int r;
	asm volatile (
                  "vmrs	%0, fpscr			\n\t"	//r0 = FPSCR
                  "and	%0, %0, %1			\n\t"	//r0 = r0 & 0x04086060
                  "orr	%0, %0, %2			\n\t"	//r0 = r0 | 0x03000000
                  "vmsr	fpscr, %0			\n\t"	//FPSCR = r0
                  : "=r"(r)
                  : "r"(x), "r"(y)
                  );
}

void init_tsc() {
	enable_runfast();
	activate_ccnt();
	disable_ccnt();
	ccnt_divider(1);
}

myInt64 start_tsc(void) {
    reset_ccnt();              // Reset the CCNT
    reset_flags();   		   // Reset the overflow flags
    enable_ccnt();             // Enable CCNT
    return 0ULL;
}

myInt64 stop_tsc(myInt64 start) {
	INT32 flags, cycles, overflow, divider_on;
	myInt64 real_cycles;
    disable_ccnt();            // Stop CCNT
	cycles = read_ccnt();
	flags = read_flags();
	overflow = flags & 0x80000000;
	if (overflow) {
		fprintf(stderr, "Error: CCNT had an overflow.\n");
		return 0;
	}
	ASM VOLATILE ("MRC 		p15, 0, %0, c9, c12, 0\n\t":"=r"(divider_on));
	divider_on &= 0x08;
	if (divider_on)
		real_cycles = ((myInt64) cycles) << 6;
	else
		real_cycles = (myInt64) cycles;
    return real_cycles - start;
}

