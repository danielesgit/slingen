'''
@author: danieles
'''
import sys
import shlex
import subprocess
from datetime import date
import os

import src.mediator as mediator


class LibraryCode(object):
    def __init__(self, opts):
        super(LibraryCode, self).__init__()
        self.opts = opts
        sys.path.append(self.opts['testroot'])
        meas = __import__('meas')
        self.measurer = meas.Meas(self.opts)
        self.outcome = None
        self.rank_by_variants = None
        
    def compile(self):
        self._compile()
        return True
    
    def _compile(self):
        self.validateList = []
        libname = self.opts['libname']
        print "\n######################## Testing " + str(libname) + " ########################\n"
        print "Tester:   " + self.opts['hfilebasename']+ "\n"
        print "Static Params:   " + str(self.opts['static_params']) + "\n"
        print "Generating header file in folder:   " + self.opts['compileroot'] + '/' + self.opts["compilename"] + "\n"
        self.generateParamHeader()
        
        if self.opts.get('remote_execution', False):
            retCode = self.runRemoteExperiment()
        else:
            print "Compiling code...\n"
            self.compileCode()
            if 'asmflags' in self.opts:
                print "Generating asm file...\n"
                self.genAsm()
            print "Running code...\n"
            retCode = self.runCode()
        
        if self.opts['validate']:
            if retCode != 0:
                self.validateList.append(False)
                raise Exception('retCode = %d' % retCode)
            else:
                self.validateList.append(True)
        meas = self.collectMeasurement()
        self.outcome = [ ( libname, meas ) ]
        
        print "> " + str(meas) + " f/c\n"
    
    def generateParamHeader(self):
        compilefolder = self.opts['compileroot'] + '/' + self.opts['compilename']
        if os.path.exists(compilefolder + "/kernels"):
            params = '-'.join(str(p) for p in self.opts['static_params'])
            srcfile = '%s/kernels/%s_kernel-%s.h' % (compilefolder, self.opts['experiment'], params)
            destfile = '%s/kernels/%s_kernel.h' % (compilefolder, self.opts['experiment'])
            args = shlex.split('cp %s %s' % (srcfile, destfile))
            subprocess.call(args)
        else:
            hfullname = compilefolder + '/params.h'
            hfile = open(hfullname, 'w')
        
            hfile.write("/*\n")
            hfile.write(" * params.h\n")
            hfile.write(" *\n")
            hfile.write(" * Created on: " + str(date.today()) + "\n")
            hfile.write(" * Author: danieles\n")
            hfile.write(" */\n\n")
            hfile.write("#pragma once\n\n")
            
            if 'includefiles' in self.opts:
                print "\t> Adding include directives: " + str(self.opts['includefiles']) + "\n"
                for incfile in self.opts['includefiles']:
                    hfile.write("#include " + incfile + "\n")
                hfile.write("\n\n")
            
            if 'defs' in self.opts:
                print "\t> Adding define directives: " + str(self.opts['defs']) + "\n"
                for d in self.opts['defs']:
                    t = (d[0]+' '+d[1]) if isinstance(d, tuple) else d
                    hfile.write("#define " + t + "\n")
                hfile.write("\n\n")
    
            if 'undefs' in self.opts:
                print "\t> Adding undef directives: " + str(self.opts['undefs']) + "\n"
                for d in self.opts['undefs']:
                    hfile.write("#undef " + d + "\n")
                hfile.write("\n\n")
                            
            # Performance Events
            if 'events' in self.opts:
                s = hex(self.opts["events"][0][0]) + ", " + hex(self.opts["events"][0][1])
                for event in self.opts["events"][1:]:
                    s += ", " + hex(event[0]) + ", " + hex(event[1]) 
                hfile.write("long counters[" + str(len(self.opts["events"])) + "] = { " + s + " }\n\n")
           
            i = 0
            for param in self.opts['static_params']:
                hfile.write("#define PARAM" + str(i) + " " + str(param) + "\n")
                i += 1
    
            if self.opts['validate']:
                hfile.write("\n#define ERRTHRESH " + self.opts['errthresh'] + "\n")
                hfile.write("\n#define SOFTERRTHRESH " + self.opts.get('softerrthresh', "1e10") + "\n")
    
            hfile.write("\n#define NUMREP " + self.opts['numrep'] + "\n")
    
            hfile.write("\n\n\n")
        
            hfile.close()

        #Use the right tester
        hfilebasename = self.opts['hfilebasename']
        hfullname = compilefolder + '/testers.h'
        hfile = open(hfullname, 'w')
    
        hfile.write("/*\n")
        hfile.write(" * testers.h\n")
        hfile.write(" *\n")
        hfile.write(" * Created on: " + str(date.today()) + "\n")
        hfile.write(" * Author: danieles\n")
        hfile.write(" */\n")
        hfile.write("\n#pragma once\n\n")
        if self.opts.get('remote_execution', False):
#             hfile.write("#define EXEC_PATH \"" + self.opts['remote_execution']['exprootfolder'] + "\"\n\n")
            hfile.write("#define EXEC_PATH \".\"\n\n") 
        else:
            hfile.write("#define EXEC_PATH \"" + compilefolder + "\"\n\n")
        hfile.write("#include \"" + hfilebasename + "_tester.h\"\n\n")
        
        hfile.close()
    
    def runRemoteExperiment(self):
        ''' Run a complete experiment (compile, execute, collect results) on a remote device. 
        
        The execution of this method should have exactly the same effects as executing an experiment locally.
        Returns the exit code of the execution.
        '''
        device = mediator.Device(self.opts['hostname'], self.opts['username'], password=self.opts.get('password', None), 
                        rsa_key_file=self.opts.get('rsakeyfile', None), rsa_pass=self.opts.get('rsakeypass', ''),
                        port=self.opts['port'], exp_root_folder=self.opts['exprootfolder'], os=self.opts.get('os', 'LINUX'),
                        affinity=self.opts.get('affinity', None))
        
        makedir = self.opts['compileroot'] + '/' + self.opts['compilename']
        path_command = ''
        compile_command = ''
        asm_command = ''
        if not self.opts['cross-compile']: # remote compilation
            scaType = 0 if self.opts['precision'] == 'float' else 1
            cc = self.opts['cc']
            ld = self.opts.get('ld', cc)
            
            if self.opts['vectorize']:
                optscflags = self.opts['cflags-vec']
            else:
                optscflags = self.opts['cflags']
                
            cflags = optscflags + (' -DVALIDATE' if self.opts['validate'] else '') + ' -DTYPE=' + str(scaType) + ' -DALIGN=' + str(self.opts['align'])
            cflags += ' -DTEST' if self.opts.get('test', True) else ''
            measLib = self.opts['meas'] if 'meas' in self.opts else "" 
            ldflags = measLib + " " + (self.opts['ldflags'] if 'ldflags' in self.opts else "")
            platform = self.opts.get('platform', self.opts['arch'].__name__)
#             arch = self.opts['arch'].__name__
            
            if 'compilepath' in self.opts and self.opts['compilepath']:
                path_command = 'export PATH=$PATH:%s' % self.opts['compilepath']
            clean_command = 'make -s clean'
            compile_command = 'make -s CC=%s CFLAGS=\"%s\" LD=%s LDFLAGS=\"%s\" ARCH=\"%s\" all' % (cc, cflags, ld, ldflags, platform)
            if 'asmflags' in self.opts:
                asmflags = self.opts.get('asmflags', '')
                asm_command = 'make -s CC=%s CFLAGS=\"%s\" ASMFLAGS=\"%s\" ARCH=\"%s\" asm' % (cc, cflags, asmflags, platform)

            makelog = open(makedir + '/make.log', 'w')
            makelog.write("CC = " + cc + "\n")
            makelog.write("LD = " + ld + "\n")
            makelog.write("CFLAGS = " + cflags + "\n")
            makelog.write("LDFLAGS = " + ldflags + "\n")
            makelog.write("ARCH = " + platform + "\n")
            makelog.write("\n" + compile_command + "\n")
            makelog.close()
        else: # cross-compilation
            clean_command = 'rm -rf ./*.txt'
        exec_command = './main'
        output_files = ['flops.txt', 'cycles.txt']
        config = {
            'compileCommands': [com for com in [path_command, clean_command, compile_command, asm_command] if com],
            'execCommands': [exec_command],
            'outputFiles': output_files,
            'repetitions': 1,
        }
        
        experiment = mediator.Experiment(device, config)
        if self.opts['cross-compile']:
            print "Cross-compiling code...\n"
            self.compileCode()
            if 'asmflags' in self.opts:
                print "Generating asm file...\n"
                self.genAsm()
            experiment.add_file_from_filesystem('%s/%s' % (makedir, 'main'), 'main', is_executable=True)
        else:
            files_to_copy = self.opts['basefiles'] + ['testers.h', 'params.h', '%s_tester.h' % self.opts['hfilebasename'], 
                                                  'tsc_%s.cpp' % platform, self.opts['makefile'] ]
            for local_filename in files_to_copy:
                experiment.add_file_from_filesystem('%s/%s' % (makedir, local_filename), local_filename)
        medclient = mediator.Client(self.opts['mediatorhostname'], int(self.opts['mediatorport']))
        print "Sending experiment to Mediator...\n"
        results = medclient.run_experiments([experiment])
        exit_code = self.processRemoteExpResults(results)
        return exit_code

    def processRemoteExpResults(self, results):
        ''' Process the results of a remote experiment execution.
        
        Creates the needed output files in the local filesystem with the content that is included 
        in the mediator response (results). Returns the exit code of the remote experiment execution.
        '''
        folder = self.opts['compileroot'] + '/' + self.opts['compilename']
        if 'error' in results:
            raise Exception('%s: %s' % (results['error']['reason'], results['error']['message']))
        with open(os.path.join(folder, 'output.txt'), 'w') as f:
            f.write(results['data'][0].get('output', ''))
        if 'error' in results['data'][0]:
            raise Exception('%s: %s' % (results['data'][0]['error']['reason'], results['data'][0]['error']['message']))
        
        for file_result in results['data'][0]['results'][0]['execResults']:
            with open(os.path.join(folder, file_result['outputFile']), 'w') as f:
                f.write(file_result['fileContents'][0])
        return results['data'][0]['results'][0]['exitCodes'][0]
    
    def compileCode(self):
        makedir = self.opts['compileroot'] + '/' + self.opts['compilename']
        scaType = 0 if self.opts['precision'] == 'float' else 1
        crossCompile = 'cross-compile' in self.opts
        vectorize = self.opts['vectorize']
        cc = self.opts['cross-cc'] if crossCompile and 'cross-cc' in self.opts else self.opts['cc']
        ld = self.opts['cross-ld'] if crossCompile and 'cross-ld' in self.opts else self.opts.get('ld', cc)
        if crossCompile:
            if vectorize:
                optscflags = self.opts['cross-cflags-vec'] if 'cross-cflags-vec' in self.opts else self.opts['cflags-vec']
            else:
                optscflags = self.opts['cross-cflags'] if 'cross-cflags' in self.opts else self.opts['cflags']
        else:
            if vectorize:
                optscflags = self.opts['cflags-vec']
            else:
                optscflags = self.opts['cflags']
#         optscflags = self.opts['cross-cflags'] if crossCompile and 'cross-cflags' in self.opts else self.opts['cflags']
        optsldflags = self.opts['cross-ldflags'] if crossCompile and 'cross-ldflags' in self.opts else self.opts.get('ldflags', '')
        compilepath = self.opts['cross-compilepath'] if crossCompile and 'cross-compilepath' in self.opts else self.opts['compilepath']  
        measLib = self.opts['meas'] if 'meas' in self.opts else "" 
        platform = self.opts.get('platform', self.opts['arch'].__name__)
#         arch = self.opts['arch'].__name__
        ldflags = measLib + ' ' + optsldflags
        cflags = '%s%s -DTYPE=%d -DALIGN=%d' % (optscflags, (' -DVALIDATE' if self.opts['validate'] else ''), scaType, self.opts['align'])
        cflags += ' -DTEST' if self.opts.get('test', True) else ''
        env = {'PATH': compilepath} if compilepath else None
        
        compile_command = 'make -s -C %s CC="%s" CFLAGS="%s" LD="%s" LDFLAGS="%s" ARCH="%s" all' % (makedir, cc, cflags, ld, ldflags, platform)
        makelog = open(makedir + '/make.log', 'w')
        makelog.write("CC = " + cc + "\n")
        makelog.write("LD = " + ld + "\n")
        makelog.write("CFLAGS = " + cflags + "\n")
        makelog.write("LDFLAGS = " + ldflags + "\n")
        makelog.write("ARCH = " + platform + "\n")
        makelog.write("\n" + compile_command + "\n")
        makelog.close()
        
        args = shlex.split('make -s -C %s clean' % makedir)
        subprocess.call(args)
        args = shlex.split(compile_command)
        subprocess.call(args, env=env)

    def genAsm(self):
        compilepath = self.opts['compilepath']
        makedir = self.opts['compileroot'] + '/' + self.opts['compilename']
        scaType = 0 if self.opts['precision'] == 'float' else 1
        crossCompile = 'cross-compile' in self.opts
        vectorize = self.opts['vectorize']
        cc = self.opts['cross-cc'] if crossCompile and 'cross-cc' in self.opts else self.opts['cc']
        if crossCompile:
            if vectorize:
                optscflags = self.opts['cross-cflags-vec'] if 'cross-cflags-vec' in self.opts else self.opts['cflags-vec']
            else:
                optscflags = self.opts['cross-cflags'] if 'cross-cflags' in self.opts else self.opts['cflags']
        else:
            if vectorize:
                optscflags = self.opts['cflags-vec']
            else:
                optscflags = self.opts['cflags']
        cflags = optscflags + (' -DVALIDATE' if self.opts['validate'] else '') + ' -DTYPE=' + str(scaType) + ' -DALIGN=' + str(self.opts['align'])
        asmflags = self.opts['cross-asmflags'] if crossCompile and 'cross-asmflags' in self.opts else self.opts['asmflags']
        platform = self.opts.get('platform', self.opts['arch'].__name__)
#         arch = self.opts['arch'].__name__
        env = {'PATH': compilepath} if compilepath else None
        
        args = shlex.split('make -s -C ' + makedir + ' CC=' + cc + ' CFLAGS=\"' + cflags + '\" ASMFLAGS=\"' + asmflags + '\" ARCH=\"' + platform + '\" asm')
        subprocess.call(args, env=env)
            
    def runCode(self):
        ldlibpath = self.opts.get('ldlibpath', '')
        progname = self.opts['compileroot'] + '/' + self.opts['compilename'] + '/main'
        env = {'LD_LIBRARY_PATH': ldlibpath} if ldlibpath else None
        if 'affinity' in self.opts:
            progname = "taskset -c " + str(self.opts['affinity'][0]) + " " + progname
        args = shlex.split(progname)
        return subprocess.call(args, env=env)

    def collectMeasurement(self):
        return self.measurer.collectMeasurement()
        