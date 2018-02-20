//#define _GNU_SOURCE
//#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>
#include <linux/perf_event.h>
#include "tsc.h"


static int fddev = -1;

__attribute__((constructor)) static void init(void) {
        static struct perf_event_attr attr;
        attr.type = PERF_TYPE_HARDWARE;
        attr.config = PERF_COUNT_HW_CPU_CYCLES;
        fddev = syscall(__NR_perf_event_open, &attr, 0, 0, -1, 0);
}

__attribute__((destructor)) static void fini(void) {
        close(fddev);
}

void init_tsc() {
	;
}

myInt64 start_tsc(void) {
	myInt64 result = 0;
    if (read(fddev, &result, sizeof(result)) < sizeof(result)) return 0;
    return result;
}

myInt64 stop_tsc(myInt64 start) {
	myInt64 result = 0;
    if (read(fddev, &result, sizeof(result)) < sizeof(result)) return 0;
    return result - start;
}


