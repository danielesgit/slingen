#ifndef TSC_H_INCLUDED
	#define TSC_H_INCLUDED
	
	/* ==================== GNU C and possibly other UNIX compilers ===================== */
	#ifndef WIN32

		#if defined(__GNUC__) || defined(__linux__)
		#define VOLATILE __volatile__
		#define ASM __asm__
		#else
		/* if we're neither compiling with gcc or under linux, we can hope
		 * the following lines work, they probably won't */
		#define ASM asm
		#define VOLATILE 
		#endif

		#define myInt64 unsigned long long
		#define INT32 unsigned int

	/* ======================== WIN32 ======================= */
	#else

		#define myInt64 signed __int64
		#define INT32 unsigned __int32

	#endif

	void init_tsc();
	myInt64 start_tsc(void);
	myInt64 stop_tsc(myInt64 start);
	
#endif
