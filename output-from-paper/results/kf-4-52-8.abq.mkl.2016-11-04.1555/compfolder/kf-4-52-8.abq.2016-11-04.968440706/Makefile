# All Target
all: main

asm: main.cpp
	$(CC) $(ASMFLAGS) $(CFLAGS) -o main.s $<

main.o: main.cpp
	$(CC) $(CFLAGS) -c -o $@ $<

erm: main.cpp
	$(CC) $(CFLAGS) -c -o main.bc $<

tsc_$(ARCH).o: tsc_$(ARCH).cpp
	$(CC) $(CFLAGS) -c -o $@ $<

main: main.o tsc_$(ARCH).o
	$(LD) -o $@ $^ $(LDFLAGS) 

# Other Targets
clean:
	-@$(RM) main.s main.o main.bc tsc_*.o main

.PHONY: all clean asm erm
