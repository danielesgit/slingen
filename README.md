
This version of the SLinGen generator is meant to reproduce the results described in the paper *Program Generation for Small-Scale Linear Algebra Applications*, by D. G. Spampinato, D. Fabregat-Traver, P. Binetinesi, and M. Püschel, presented at
CGO'18. The artifact evaluation requires a Linux system (we used Ubuntu 14.04 with Linux kernel v3.13 for our experiments)
and a CPU with support for AVX. SLinGen kernels are compared against straightforward optimized with Intel icc and clang with the polyhedral Polly, the template-based Eigen, and library-based code using Intel’s MKL, ReLAPACK, and RECSY. If the user is interested in replicating the result from any of the latter competitors, for performance reasons she is required to install her libraries of choice on the target experimental platform.

Hardware dependencies
-----------

The only required hardware is a CPU with AVX. Sec. 4 provides more details about the exact hardware used for the experiments.

Software dependencies
------------------

SLinGen is created to run on a Linux system. All dependencies, except for experimental competitors, can be installed through the package managers on distributions such as Ubuntu and Red Hat.
In particular SLinGen requires the following software:
* python2.7 and 3.5: Including development files. In particular, *libpython2.7* should be available as a shared library.
* pip, pip3, and virtualenv.
* gcc or Intel icc compiler.
* GMP: The GNU MP library. On Ubuntu you may install the libgmp-dev package.
* FreeType: FreeType 2 font engine required by Matplotlib. On Ubuntu you may install the libfreetype6-dev package.
* A working LATEX installation required by Matplotlib (if plotting required).
* MATLAB (if validating results for the application-level benchmarks).

Experimental competitors are not necessary to run SLinGen. If some of them cannot be installed they can be disabled as discussed below.

Installation
----------------

Before starting with the installation please define the variables `PYTHON2BIN`, `PYTHON3BIN`, and `PYTHON2INC` in file `envvar.sh`. `PYTHON2BIN` (`PYTHON3BIN`) should contain the path to the python2.7 (python3.5) executable while `PYTHON2INC` the path to python2.7’s include directory. 
The use of experimental competitors requires the definition of root variables in envvar.sh. For example, for Intel MKL the variable `MKLROOT` should refer to the MKL’s installation directory (in the specific case of Intel MKL, the variable could be already available in your environment). The file `envvar.sh` contains commented examples from a systemwide installation. In case the libpython2.7 shared library is not reachable from `LIBRARY_PATH` and `LD_LIBRARY_PATH`, please add its path to the `PYTHON2LIB` variable.
Assuming that all dependencies are satisfied, SLinGen can be installed as follows:
```
cd slingen
./install.sh
```
The file *slingen/src/config/devices/local.conf* defines which compiler should be used to compile SLinGen's generated code. 
If Intel icc is not available, *local.conf* should be modified to point to the desired compiler with appropriate flags (e.g., move *local.conf.gcc* to *local.conf* for compiling with gcc).

Input files
--------------
SLinGen takes as an input a linear algebra program described in LA, a language with Matlab-like notation. All LA source files are stored in folder *slingen/src/tests*. Names follow the labelling convention defined in Sec. 4.

Experiment workflow
------------

The evaluation process can be started from the root folder using the `run.sh` script.
File *slingen/main.py* contains three lists: experiments, devices, and libs. The three lists contain information respectively about what experiments should be run, on which devices, and for which set of competitors. Labels in list
```python
libs = [ slingen, mkl, hand, polly, relapack, recsy, eigen ]
```
respectively denote: SLinGen, Intel MKL, icpc- and clang+Polly-compiled straightforward code, ReLAPACK, RECSY, and Eigen. 
If a competitor should not be considered (e.g., it was not installed) then it should be removed from this list.
As the experiments are run on a single local device, SLinGen iterates over the set of experiments and competitors as follows:
```python
for experiment in experiments :
  for lib in libs :
    for n in experiment.size_range :
      test( lib, experiment , n ) on local_device
```
Every experiment is specialized to the sizes reported on the x-axis of the plots in Figures 17–18. In particular, every combination experiment/competitor is associated to a test file used to run the experiment. Such files are located in folder *slingen/src/testing/timing/testers*. Test files without a prefix such as mkl and hand, are those associated to SLinGen. SLinGen generates header files containing the optimized kernel functions. Such header files are compiled together with their test file to perform an experiment.
During the execution of the evaluation process the composition of the different unit tests can be monitored within the *compileroot* folder.
It is possible to modify the CPU affinity for the experiments from the configuration file *local.conf* located in *lgen/src/config/devices* (option `affinity = [x]`).

Evaluation and expected result
----------

The process is composed of the eight experiments related to the 7 benchmarks reported in Sec. 4. After execution, the header files with the best kernels generated by SLinGen for a given experiment are stored in the *output/results* folder. Every experiment will generate a folder named after the experiment’s label, competitor, and time of execution.
The result folders will also contain files collecting cycles and performance information. Such files will be used together with similar files generated for other competitors to create the final plots stored in the *output/plots* folder.

For a faster evaluation SLinGen is setup to use a subset of the available algorithmic choices to produce the solid black lines associated to SLinGen in Figures 17–18 (for some points small performance drops may be noticed compared to the thorough search shown in the paper). To demonstrate the algorithmic space exploration that led to those lines, we enabled multiple algorithmic variants for the *trslya* benchmark. These variants should appear as colored, dashed lines in the benchmark plot. The synthesized basic linear algebra programs used to generate the final C code are stored in the alg subfolder of each experimental folder.

### Delayed plot creation. 
Sometimes it can be difficult or not desired to install LATEX on certain systems, such as a computing node of a cluster. For this reason, it possible to separate the execution of the experiments from the creation of the performance plots. We assume the following scenario: We run SLinGen on two systems, a system A where we want to run the experiments and a system B where we want to plot the results. 
1. Install SLinGen as described above on both systems. 
2. Run the experiments on system A. Set the `plot` variable in *slingen/src/config/common.conf* to `False` and execute using the `run.sh` script. As described in the previous paragraph, at the end of the execution the final results should be available in folder *output/results*.
3. Create the plots. Copy the final results from folder *output/results* on system A to the same folder on system B. On system B, set the following variables in *slingen/src/config/common.conf*:
```python
plot = True
useprecomputed = True
precompdir = "../output/results"
```
At this point execute the `run.sh` script on system B, making sure that the main.py file on system B lists exactly the experiments executed on system A. As a result, the performance plots of the experiments should appear in folder *output/plots*.