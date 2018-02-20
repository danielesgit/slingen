################################################################################

RM := rm -rf

USER_OBJS :=

LIBS :=

# All of the sources participating in the build are defined here
# Add inputs and outputs from these tool invocations to the build variables 
CPP_SRCS += \
./main.cpp 

OBJS += \
./main.o 

CPP_DEPS += \
./main.d 

# Each subdirectory must supply rules for building sources it contributes
%.o: %.cpp
#	icpc -O3 -xHost -ipp=common -I/home/danieles/sw/eigen -no-prec-div -fargument-noalias -fno-alias -no-vec $(CFLAGS) -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -c -o "$@" "$<"
	@icpc -O3 -xHost -ipp=common -I/home/danieles/sw/eigen -no-prec-div -fargument-noalias -fno-alias -no-vec -no-ipo -no-ip $(CFLAGS) -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -c -o "$@" "$<"
#	icpc -O3 -xHost -ipp=common -I/home/danieles/sw/eigen -no-prec-div -fargument-noalias -fno-alias -no-vec -no-ipo -no-ip $(CFLAGS) -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -S -fsource-asm -o "$@" "$<"

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(strip $(CPP_DEPS)),)
-include $(CPP_DEPS)
endif
endif

# Add inputs and outputs from these tool invocations to the build variables 

# All Target
all: main

# Tool invocations
main: $(OBJS) $(USER_OBJS)
#	@echo 'Building target: $@'
	@icpc -ipp=common -o "main" $(OBJS) $(USER_OBJS) $(LIBS)
#	@echo 'Finished building target: $@'

# Other Targets
clean:
	-@$(RM) $(OBJS)$(CPP_DEPS) main
	-@echo ' '

.PHONY: all clean dependents
