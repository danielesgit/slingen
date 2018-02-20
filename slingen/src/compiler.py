'''
Created on Apr 16, 2012

@author: dgs
'''

import os
import shlex
import subprocess
import sys
import traceback
import time
import smtplib
import socket
import gc

import mimetypes
from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from datetime import date
from copy import deepcopy

from src.dsls.ll import resetCounters, llExtSemantics
from src.dsls.llparser import llParser
from src.dsls.processing import computeDependencies
from src.dsls.ll2sll import rewriteToSigma

# from src.rules.lrms import HOfflineLRM
# from src.rules.llrules import HValidateLLRuleSet
# from src.rules.slrms import HOfflineSLRM
# from src.rules.sllrules import HValidateSLLRuleSet

from src.dsls.processing import parse_config_file
from src.mediator import Device, Experiment, Client

from src.binding import bindExpression
from src.irbase import scalarRep, alignRep, icode
from src.physical import Scalars
# from src.eg import drawGraph

#from src.alexpr import *
# from src.physical import *
# from src.binding import *
# from src.unparser import *
#from eg import *
#from src.rules import *

# from src.generator import *

# import ir
#from ir import *
#from isa import ISAManager, x86, SSE, SSE2, SSE3, SSSE3, SSE4_1, AVX

#import src.irbase

# from src.irbase import *
# from src.isas.isabase import *
# from src.isas.x86 import *
# from src.isas.sse import *
# from src.isas.sse2 import *
# from src.isas.sse3 import *
# from src.isas.ssse3 import *
# from src.isas.sse4_1 import *
# from src.isas.avx import *


def openLog(opts, mode='a'):
    if opts.get('logfile', None) is None or opts['logfile'].closed:
        if opts.get('logtimestamp', None) is None:
            opts['logtimestamp'] = '%s.%s' % (date.today().isoformat(), time.strftime('%H-%M-%S', time.localtime(time.time())))
        logfullname = opts['logroot'] + '/results/' + opts['testname'] + '/log' + opts['logtimestamp'] + '.txt' 
        opts['logfile']  = open(logfullname, mode)        
    
def closeLog(opts):
    if opts.get('logfile', None) is not None and not opts['logfile'].closed:
        opts['logfile'].close()
        if os.path.getsize(opts['logfile'].name) > 10**5:
            opts['logfile'].close()
            opts['logtimestamp'] = '%s.%s' % (date.today().isoformat(), time.strftime('%H-%M-%S', time.localtime(time.time())))
            logfullname = opts['logroot'] + '/results/' + opts['testname'] + '/log' + opts['logtimestamp'] + '.txt' 
            opts['logfile']  = open(logfullname, 'a')
            opts['logfile'].close()

def printToLog(msg, opts, openf=True, closef=True):
    if openf:
        openLog(opts)
    msg += "\n\n"
    opts['logfile'].write( msg )
    if closef: 
        closeLog(opts)

def send_email_with_log(opts, subj=None, body=None, attachments=None, extra_to=None):
    to = opts.get('emailaddr', []) + ([] if extra_to is None else extra_to) 
    if not opts.get('sendemail', False) or not to:
        return
    body = '' if body is None else body
    msg = MIMEMultipart('mixed')
    bodyPart = MIMEText(body, 'plain')
    msg.attach(bodyPart)
    msg['Subject'] = "SLinGen Report" if subj is None else subj
    me = 'slingen@%s' % (socket.gethostname())
    msg['From'] = me
    msg['To'] = ', '.join(to)
    
    attachments = [] if attachments is None else attachments
    for directory, filename in attachments:
        path = os.path.join(directory, filename)
        if not os.path.isfile(path):
            continue
        # Guess the content type based on the file's extension.  Encoding
        # will be ignored, although we should check for simple things like
        # gzip'd or compressed files.
        ctype, encoding = mimetypes.guess_type(path)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        if maintype == 'text':
            with open(path) as fp:
                # Note: we should handle calculating the charset
                att = MIMEText(fp.read(), _subtype=subtype)
        elif maintype == 'image':
            with open(path, 'rb') as fp:
                att = MIMEImage(fp.read(), _subtype=subtype)
        elif maintype == 'audio':
            with open(path, 'rb') as fp:
                att = MIMEAudio(fp.read(), _subtype=subtype)
        else:
            with open(path, 'rb') as fp:
                att = MIMEBase(maintype, subtype)
                att.set_payload(fp.read())
            # Encode the payload using Base64
            encoders.encode_base64(att)
        # Set the filename parameter
        att.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(att)
    
    s = smtplib.SMTP('localhost')
    s.sendmail(me, to, msg.as_string())
    s.quit()

class Compiler(object):
    def __init__(self, llprog, opts):
#         self.exprList = [ expr ]
        self.llprog = llprog
        self.opts = opts
#         self.opts['scalar'] = opts['isa'].getScalarFPType()
        sys.path.append(self.opts['testroot'])
        meas = __import__('meas')
        self.measurer = meas.Meas(self.opts)
        self.measManager = meas.MeasManager()
        self.rank_by_variants = None
        
    def compile(self):
        self.perfthreshold = None
        if 'perf_threshold' in self.opts:
            self.perfthreshold = self.opts['perf_threshold']
        return self._compile()
    
    def _compile(self):
        fine = True

        if self.opts.get('runprecomputed', False):
            kernel_file = self.kernel_exists()
            if kernel_file:
                fine = self.use_precomp_kernel(kernel_file)
                return fine
            
        print "\nInstantiating " + self.opts['lrm'].__name__ + "...\n"
        self.opts['ll_parser'] = llParser
        self.opts['ll_sem'] = llExtSemantics
        lrm = self.opts['lrm'](self.llprog, [self.opts['vallrs'], self.opts['iterlrs']], self.measManager, self.opts)
        print "Using " + str(lrm) + "\n"
        print "With Rule Set " + str(self.opts['iterlrs']) + "\n"
        
        self.opts['inoutorder'] = self.llprog.getInOutOrder()
        
        if self.opts.get('gentester', True) and not self.opts['onlygen']:
            print "Generating Tester in folder:   " + self.opts['compileroot'] + '/' + self.opts["compilename"] + "\n"
            self.generateTester()
        
        self.validateList = []
        self.resetCompilerStatus()
        maxMeas = -1
        copyKernel = self.opts.get('copybestkernel', False)
        copy_all_kernels = self.opts.get('copyallkernels', False)
        
#         sys.exit()
        
        llp = lrm.next()
        while llp:
            gc.collect()
            print "\n######################## Testing following program: ########################"
            print self.llprog
            print "############################################################################\n"
            print "Generation of variant " + str(llp.ann.get('algo_v', 0))
            if self.opts['printchoices']: 
                print lrm.print_choices()
            
            try:
                sllp = self.generateSigmaLL(llp)
                
                uFsList = [ self.opts['baseufs'] ] + self.opts['ufslist']
                for uFs in uFsList:
                    self.opts['ufs'] = uFs
    
                    
                    print "Kernel generation with unrolling factors:\n\t" + str(uFs) + "\n"
                    self.generateKernel(sllp)
                    
                    if not 'onlygen' in self.opts or not self.opts['onlygen']: 
                        print "Generating header file in folder:   " + self.opts['compileroot'] + '/' + self.opts["compilename"] + "\n"
                        self.generateHeader(llp)
                        
                        try:
                            if self.opts.get('remote_execution', False):
                                retCode = self.runRemoteExperiment()
                            else:
                                print "Compiling code...\n"
                                self.compileCode()
                                if self.opts.get('asmflags', ""):
                                    print "Generating asm file...\n"
                                    self.genAsm()
                                print "Running code...\n"
                                retCode = self.runCode()
                                
                            if self.opts.get('runwitherm', False):
                                self.run_erm_experiment()
                                    
                            if self.opts['validate']:
                                self.copyErrorsToResultFolder()
                                if retCode != 0:
                                    raise Exception('retCode = %d' % retCode)
                                else:
                                    self.validateList.append(True)
                            if self.opts.get('test', True):
                                meas = self.collectMeasurement()
                                lrm.insertMeasurement(meas, llp.ann.get('variant_tag', None))
                                if copyKernel and meas[0] > maxMeas:
                                    self.copyKernelToResultFolder()
                                    maxMeas = meas[0]
                                if copy_all_kernels:
                                    self.copy_gen_kernel(meas)
                            
                                if self.perfthreshold is not None and self.perfthreshold < meas[0] - meas[1]:
                                    self.perfthreshold = meas[0] - meas[1]; # Set new perf threshold for next run
                                print "> " + str(meas) + " f/c\n"
                        except Exception:
                            openLog(self.opts)
                            ts = '%s.%s' % (date.today().isoformat(), time.strftime('%H-%M-%S', time.localtime(time.time())))
                            msg = "=@"*10 + " Begin Exc Report: Run (" + ts + ") " + "=@"*10 + "\n"
                            msg += "LL prog:\n\n%s\n\nWhile running:\n\n%s\n\n" % (str(self.llprog), str(llp))
                            msg += "-"*10 + " opts " + "-"*10 + "\n"
                            msg += str(self.opts) + "\n"
                            msg += "-"*10 + " traceback " + "-"*10 + "\n"
                            printToLog(msg, self.opts, openf=False, closef=False)
                            traceback.print_exc(file=self.opts['logfile'])
                            self.dumpKernel()
                            msg = "\n" + "=@"*10 + " End Exc Report: Run (" + ts + ") " + "=@"*10 + "\n"
                            printToLog(msg, self.opts, openf=False)
                            if self.opts.get('breakonexc',False):
                                raise
                            fine = False
                            self.validateList.append(False)
                        self.resetCompilerStatus()
                
    #             self.resetCompilerStatus()
            except Exception:
                openLog(self.opts)
                ts = '%s.%s' % (date.today().isoformat(), time.strftime('%H-%M-%S', time.localtime(time.time())))
                msg = "=@"*10 + " Begin Exc Report from _compile (" + ts + ") " + "=@"*10 + "\n"
                msg += "LL prog:\n\n%s\n\nWhile generating:\n\n%s\n\n" % (str(self.llprog), str(llp))
                msg += "-"*10 + " opts " + "-"*10 + "\n"
                msg += str(self.opts) + "\n"
                msg += "-"*10 + " traceback " + "-"*10 + "\n"
                printToLog(msg, self.opts, openf=False, closef=False)
                traceback.print_exc(file=self.opts['logfile'])
                msg = "\n" + "=@"*10 + " End Exc Report (" + ts + ") " + "=@"*10 + "\n"
                printToLog(msg, self.opts, openf=False)
                if self.opts.get('breakonexc',False):
                    raise
                fine = False
                self.validateList.append(False)
            llp = lrm.next()
        
        if (not 'onlygen' in self.opts or not self.opts['onlygen']) and self.opts.get('test', True) and fine: 
            if 'dumprank' in self.opts and self.opts['dumprank']:
                params = '-'.join(str(p) for p in self.opts['static_params']) 
                lrm.dumpRank(self.opts['logroot']+'/results/'+self.opts['testname']+'/rank-'+params+'.csv')
            self.outcome = [ lrm.getBestMeasurement() ]
            self.rank_by_variants = lrm.rank_by_variants
        return fine

    def use_precomp_kernel(self, kernel_file):
        fine = True
        self.validateList = []
        copyKernel = self.opts.get('copybestkernel', False)

        print "\n######################## Testing following program: ########################"
        print self.llprog
        print "############################################################################\n"
        
        print "Copying kernel file in folder:   " + self.opts['compileroot'] + '/' + self.opts["compilename"] + "\n"
        self.copy_header(kernel_file)
        
        try:
            if self.opts.get('remote_execution', False):
                retCode = self.runRemoteExperiment()
            else:
                print "Compiling code...\n"
                self.compileCode()
                if self.opts.get('asmflags', ""):
                    print "Generating asm file...\n"
                    self.genAsm()
                print "Running code...\n"
                retCode = self.runCode()
                
            if self.opts.get('runwitherm', False):
                self.run_erm_experiment()
                    
            if self.opts['validate']:
                self.copyErrorsToResultFolder()
                if retCode != 0:
                    raise Exception('retCode = %d' % retCode)
                else:
                    self.validateList.append(True)
            if self.opts.get('test', True):
                meas = self.collectMeasurement()
                if copyKernel:
                    self.copyKernelToResultFolder()
                print "> " + str(meas) + " f/c\n"
        except Exception:
            openLog(self.opts)
            ts = '%s.%s' % (date.today().isoformat(), time.strftime('%H-%M-%S', time.localtime(time.time())))
            msg = "=@"*10 + " Begin Exc Report: Run (" + ts + ") " + "=@"*10 + "\n"
            msg += "LL prog:\n\n%s\n\nWhile running:\n\n%s\n\n" % (str(self.llprog), kernel_file)
            msg += "-"*10 + " opts " + "-"*10 + "\n"
            msg += str(self.opts) + "\n"
            msg += "-"*10 + " traceback " + "-"*10 + "\n"
            printToLog(msg, self.opts, openf=False, closef=False)
            traceback.print_exc(file=self.opts['logfile'])
            self.dumpKernel()
            msg = "\n" + "=@"*10 + " End Exc Report: Run (" + ts + ") " + "=@"*10 + "\n"
            printToLog(msg, self.opts, openf=False)
            if self.opts.get('breakonexc',False):
                raise
            fine = False
            self.validateList.append(False)
            
        if self.opts.get('test', True) and fine: 
            self.outcome = [ ("<see header comment in kernel file>", meas) ]
        return fine

    def copyErrorsToResultFolder(self):
        srcfile = '%s/%s/err.txt' % (self.opts['compileroot'], self.opts['compilename'])
        if os.path.exists(srcfile):
            params = '-'.join(str(p) for p in self.opts['static_params'])
            destfile = '%s/results/%s/%s_err-%s.txt' % (self.opts['logroot'], self.opts['testname'], self.opts['hfilebasename'], params)
            args = shlex.split('cp %s %s' % (srcfile, destfile))
            subprocess.call(args)
    
    
    def dumpKernel(self, suffix=None):
        srcfile = '%s/%s/kernels/%s_kernel.h' % (self.opts['compileroot'], self.opts['compilename'], self.opts['hfilebasename'])
        if os.path.exists(srcfile):
            if suffix is None:
                suffix = '%s.%s' % (date.today().isoformat(), time.strftime('%H-%M-%S', time.localtime(time.time())))
            destfile = '%s/results/%s/%s_kernel-%s.h' % (self.opts['logroot'], self.opts['testname'], self.opts['hfilebasename'], suffix)
            args = shlex.split('cp %s %s' % (srcfile, destfile))
            subprocess.call(args)

    def kernel_exists(self):
        precomp_dir = self.opts['runprecompdir']
        precomp_folders = os.listdir(precomp_dir)
        precomp_exps = [f for f in precomp_folders if f.startswith('%s.%s.%s.' % (self.opts['exp_id'], self.opts['dev'],\
                                                                                  self.opts['lib']))]
        kernel_file = ''
        if len(precomp_exps) > 0:
            params = '-'.join(str(p) for p in self.opts['static_params'])
            filename = '%s/%s/%s_kernel-%s.h' % (precomp_dir, precomp_exps[0], self.opts['hfilebasename'], params)
            if os.path.exists(filename):
                kernel_file = filename
                print '\nFound precomputed kernel in %s' % (kernel_file)
        return kernel_file

    def copyKernelToResultFolder(self):
        params = '-'.join(str(p) for p in self.opts['static_params'])
        srcfile = '%s/%s/kernels/%s_kernel.h' % (self.opts['compileroot'], self.opts['compilename'], self.opts['hfilebasename'])
        destfile = '%s/results/%s/%s_kernel-%s.h' % (self.opts['logroot'], self.opts['testname'], self.opts['hfilebasename'], params)
        args = shlex.split('cp %s %s' % (srcfile, destfile))
        subprocess.call(args)
        if self.opts.get('printchoices', False):
            srcfile = '%s/results/%s/choices.txt' % (self.opts['logroot'], self.opts['testname'])
            destfile = '%s/results/%s/choices-%s.txt' % (self.opts['logroot'], self.opts['testname'], params)
            args = shlex.split('cp %s %s' % (srcfile, destfile))
            subprocess.call(args)
        if self.opts.get('erm', False) or self.opts.get('runwitherm', False):
            for ermout in self.opts.get('copytoermlog', []):
                if self.opts.get('runwitherm', False):
                    srcfile = '%s/%s/erm.%s' % (self.opts['compileroot'], self.opts['compilename'], ermout)
                else:
                    srcfile = '%s/%s/%s' % (self.opts['compileroot'], self.opts['compilename'], ermout)
                if os.path.exists(srcfile):
                    destfile = '%s/results/%s/erm/%s.%s' % (self.opts['logroot'], self.opts['testname'], params, ermout)
                    args = shlex.split('cp %s %s' % (srcfile, destfile))
                    subprocess.call(args)

    def copy_gen_kernel(self, meas):
        params = '-'.join(str(p) for p in self.opts['static_params'])
        srcfile = '%s/%s/kernels/%s_kernel.h' % (self.opts['compileroot'], self.opts['compilename'], self.opts['hfilebasename'])
        destfolder = '%s/results/%s/genkernels/%s-%s' % (self.opts['logroot'], self.opts['testname'], self.opts['hfilebasename'], params)
        if not os.path.exists(destfolder):
            args = shlex.split("mkdir " + destfolder)
            subprocess.call(args)
        supreffix = '%s.%s' % (date.today().isoformat(), time.strftime('%H-%M-%S', time.localtime(time.time())))
        destfile = destfolder + '/kernel-' + supreffix + '.h'
        args = shlex.split('cp %s %s' % (srcfile, destfile))
        subprocess.call(args)
        #Store additional output files
        output_files = self.opts.get('outputfiles', [])
        for ofile in output_files:
            srcfile = '%s/%s/%s' % (self.opts['compileroot'], self.opts['compilename'], ofile)
            destfile = '%s/%s-%s' % (destfolder, supreffix, ofile)
            args = shlex.split('cp %s %s' % (srcfile, destfile))
            subprocess.call(args)
        #Store measurements
        with open(destfolder + '/perf-'+supreffix+'.txt', 'w') as f:
            f.write(str(meas))

        if self.opts.get('printchoices', False):
            srcfile = '%s/results/%s/choices.txt' % (self.opts['logroot'], self.opts['testname'])
            destfile = ('%s/choices-%s.txt') % (destfolder, supreffix)
            args = shlex.split('cp %s %s' % (srcfile, destfile))
            subprocess.call(args)
            
        if self.opts.get('erm', False) or self.opts.get('runwitherm', False):
            if self.opts.get('runwitherm', False):
                srcfile = '%s/%s/erm.erm.out' % (self.opts['compileroot'], self.opts['compilename'])
            else:
                srcfile = '%s/%s/erm.out' % (self.opts['compileroot'], self.opts['compilename'])
            if os.path.exists(srcfile):
                destfolder = '%s/results/%s/erm/%s-%s' % (self.opts['logroot'], self.opts['testname'], self.opts['hfilebasename'], params)
                if not os.path.exists(destfolder):
                    args = shlex.split("mkdir " + destfolder)
                    subprocess.call(args)
                destfile = destfolder + '/erm-' + supreffix + '.out'
                args = shlex.split('cp %s %s' % (srcfile, destfile))
                subprocess.call(args)
    
    def generateValidateKernel(self, valopts):
        hfilebasename = self.opts['hfilebasename']
        hfullname = self.opts['compileroot'] + '/' + self.opts['compilename'] + '/kernels/' + hfilebasename + '_validate.h'
        hfile = open(hfullname, 'w')
    
        hfile.write("/*\n")
        hfile.write(" * " + hfilebasename + "_validate.h\n")
        hfile.write(" *\n")
        hfile.write(str(self.llprog))
        hfile.write(" *\n")
        hfile.write(" * Created on: " + str(date.today()) + "\n")
        hfile.write(" * Author: danieles\n")
        hfile.write(" */\n\n")
        hfile.write("#pragma once\n\n")

        hfile.write("\n#define floord(n,d) (((n)<0) ? -((-(n)+(d)-1)/(d)) : (n)/(d))")
        hfile.write("\n#define ceild(n,d)  (((n)<0) ? -((-(n))/(d)) : ((n)+(d)-1)/(d))")
        hfile.write("\n#define max(x,y)    ((x) > (y) ? (x) : (y))")
        hfile.write("\n#define min(x,y)    ((x) < (y) ? (x) : (y))")
        
        hfile.write("\n\n\n")

        lrm = valopts['lrm'](self.llprog, [valopts['vallrs']], self.measManager, valopts)
        sll = lrm.next()
#         sllp = rewriteToSigma(self.llprog, valopts)
        sllp = rewriteToSigma(sll, valopts)

        for rs in valopts['slrs']:
            slrm = valopts['slrm'](sllp, rs, valopts)
            sllp = slrm.next()
        
        valopts['ufs'] = valopts['baseufs']
        valopts['unroll'] = { i: 0 for i in valopts['unroll'] }
        
        bindExpression(sllp, icode, valopts)
        computeDependencies(sllp, valopts)
        valopts['codegen'](sllp, valopts)
#         for i in range(len(sllp.stmtList)):
#             bindExpression(sllp.stmtList[i].eq, icode, valopts)
#             computeDependencies(sllp.stmtList[i].eq, valopts)
#             valopts['codegen'](sllp.stmtList[i], valopts)
 
        icode.flatten()

        valopts['unparser'](hfile).unparse("val_kernel")         
        
        hfile.close()
        
    def generateValidate(self, hfile):
        valopts = deepcopy(self.opts)
        valopts.update({'scarep': False, 'vectorize': False, 'nu': 1})
#         valopts['isa'] = getattr(importlib.import_module(valopts['arch'][0]), valopts['arch'][1]) 
        valopts['isaman'] = valopts['isaman'].__class__([ valopts['arch'](valopts) ])

        self.generateValidateKernel(valopts)
        
        tab = "  "
        indent = 0
         
        self.out = []
        self.inp = []
        self.inout = []
        for p in icode.signature:
            if p.isOut and p.isIn:
                self.inout += [p]
            elif p.isOut:
                self.out += [p]
            else:
                self.inp += [p]
        params = ""
        callParams = ""
        for p in self.inp:
            params += p.declareAsInParam() + ", "
            callParams += p.name + ", "

        for p in self.inout:
            params += p.declareAsOutParam("orig") + ", "

        if self.out:
            for p in self.inout:
                params += p.declareAsOutParam() + ", "
                callParams += "orig" + p.name + ", "
            for p in self.out[:-1]:
                params += p.declareAsOutParam() + ", "
                callParams += "&t" + p.name + "[0], "
            params += self.out[-1].declareAsOutParam()
            callParams += "&t" + self.out[-1].name + "[0]"
        else:
            for p in self.inout[:-1]:
                params += p.declareAsOutParam() + ", "
                callParams += "orig" + p.name + ", "
            params += self.inout[-1].declareAsOutParam()
            callParams += "orig" + self.inout[-1].name

        hfile.write(indent*tab + "int validate(" + params + ", double threshold)\n{\n")
        indent += 1

        hfile.write(indent*tab + "bool success = true;\n")
        hfile.write(indent*tab + "std::vector<string> errMsgs;\n");
        for o in self.out:
            hfile.write(o.declareAsStdVector(indent*tab, "t"))
        hfile.write("\n");
        hfile.write(indent*tab + "val_kernel(" + callParams + ");\n");

        for p in self.inout:
            hfile.write("\n");
            hfile.write(indent*tab + "for (int i = 0; i < " + str(p.size) + "; ++i) {\n")
            indent += 1
            hfile.write(indent*tab + "double err, den = fabs(orig"+p.name+"[i]);\n")
            hfile.write(indent*tab + "err = fabs(fabs("+p.name+"[i]) - orig"+p.name+"[i])/den;\n")
            hfile.write(indent*tab + "if(den > 0.) {\n")
            indent += 1
            hfile.write(indent*tab + "err = fabs("+p.name+"[i] - orig"+p.name+"[i])/den;\n")
            indent -= 1
            hfile.write(indent*tab + "}\n")
            hfile.write(indent*tab + "if(err > threshold) {\n")
            indent += 1
            hfile.write(indent*tab + "success = false;\n")
            hfile.write(indent*tab + "stringstream ss;\n")
            hfile.write(indent*tab + "ss << \"Error at (\" << i << \"): \";\n")
            hfile.write(indent*tab + "ss << \""+p.name+" = \" << "+p.name+"[i] << \"\\t-- orig"+p.name+" = \" << orig"+p.name+"[i] << \"\\t-- Err = \" << err << endl;\n")
            hfile.write(indent*tab + "errMsgs.push_back(ss.str());\n")
            indent -= 1
            hfile.write(indent*tab + "}\n")
            indent -= 1
            hfile.write(indent*tab + "}\n")

        for p in self.out:
            hfile.write("\n");
            hfile.write(indent*tab + "for (int i = 0; i < " + str(p.size) + "; ++i) {\n")
            indent += 1
#             hfile.write(indent*tab + "double err = fabs("+p.name+"[i] - t"+p.name+"[i]);\n")
            hfile.write(indent*tab + "double err, den = fabs(t"+p.name+"[i]);\n")
            hfile.write(indent*tab + "if(den > 0.) {\n")
            indent += 1
            hfile.write(indent*tab + "err = fabs("+p.name+"[i] - t"+p.name+"[i])/den;\n")
            indent -= 1
            hfile.write(indent*tab + "}else {\n")
            indent += 1
            hfile.write(indent*tab + "err = fabs("+p.name+"[i] - t"+p.name+"[i]);\n")
            indent -= 1
            hfile.write(indent*tab + "}\n")
            hfile.write(indent*tab + "if(err > threshold) {\n")
            indent += 1
            hfile.write(indent*tab + "success = false;\n")
            hfile.write(indent*tab + "stringstream ss;\n")
            hfile.write(indent*tab + "ss << \"Error at (\" << i << \"): \";\n")
            hfile.write(indent*tab + "ss << \""+p.name+" = \" << "+p.name+"[i] << \"\\t-- t"+p.name+" = \" << t"+p.name+"[i] << \"\\t-- Err = \" << err << endl;\n")
            hfile.write(indent*tab + "errMsgs.push_back(ss.str());\n")
            indent -= 1
            hfile.write(indent*tab + "}\n")
            indent -= 1
            hfile.write(indent*tab + "}\n")
        
        hfile.write("\n");
        hfile.write(indent*tab + "if(!success)\n")
        indent += 1
        hfile.write(indent*tab + "for(std::vector<string>::const_iterator i = errMsgs.begin(); i != errMsgs.end(); i++)\n")
        indent += 1
        hfile.write(indent*tab + "cout << *i;\n")
        indent -= 1
        indent -= 1
        hfile.write("\n");
        hfile.write(indent*tab + "return !success;\n")
        indent -= 1
        hfile.write("\n" + indent*tab + "}\n")
    
    def generateBuild(self, hfile):
#         out = []
#         inp = []
#         inout = []
#         for p in icode.signature:
#             if p.isOut and p.isIn:
#                 inout += [p]
#             elif p.isOut:
#                 out += [p]
#             else:
#                 inp += [p]
        params = ""
        for p in self.inp:
            params += p.declareAsDblPointer() + ", "

        for p in self.inout:
            params += p.declareAsDblPointer("orig") + ", "

        if self.out:
            for p in self.inout:
                params += p.declareAsDblPointer() + ", "
            for p in self.out[:-1]:
                params += p.declareAsDblPointer() + ", "
            params += self.out[-1].declareAsDblPointer()
        else:
            for p in self.inout[:-1]:
                params += p.declareAsDblPointer() + ", "
            params += self.inout[-1].declareAsDblPointer()

        tab = "  "
        indent = 0
        
        hfile.write(indent*tab + "inline void build("+params+")\n")
        hfile.write(indent*tab + "{\n")
        indent += 1
        for p in self.inp:
            hfile.write(p.allocMem(indent*tab, self.opts['align']))
        for p in self.inout:
            hfile.write(p.allocMem(indent*tab, self.opts['align'], "orig"))
        for p in self.inout:
            hfile.write(p.allocMem(indent*tab, self.opts['align']))
        for p in self.out:
            hfile.write(p.allocMem(indent*tab, self.opts['align']))
        hfile.write("\n");

        for p in self.inp:
            mat = self.llprog.mDict[p.name]
            hfile.write(indent*tab + "rands(*"+p.name+", "+str(mat.size[0])+", "+str(mat.size[1])+");\n")
        for p in self.inout:
            mat = self.llprog.mDict[p.name]
            hfile.write(indent*tab + "rands(*orig"+p.name+", "+str(mat.size[0])+", "+str(mat.size[1])+");\n")
        for p in self.inout:
            hfile.write(p.memCpy(indent*tab, "*"+p.name, "*orig"))

        indent -= 1
        hfile.write(indent*tab + "}\n")


    def generateDestroy(self, hfile):
#         out = []
#         inp = []
#         inout = []
#         for p in icode.signature:
#             if p.isOut and p.isIn:
#                 inout += [p]
#             elif p.isOut:
#                 out += [p]
#             else:
#                 inp += [p]
        params = ""
        for p in self.inp:
            params += p.declareAsPointer() + ", "

        for p in self.inout:
            params += p.declareAsPointer("orig") + ", "

        if self.out:
            for p in self.inout:
                params += p.declareAsPointer() + ", "
            for p in self.out[:-1]:
                params += p.declareAsPointer() + ", "
            params += self.out[-1].declareAsPointer()
        else:
            for p in self.inout[:-1]:
                params += p.declareAsPointer() + ", "
            params += self.inout[-1].declareAsPointer()

        tab = "  "
        indent = 0
        
        hfile.write(indent*tab + "inline void destroy("+params+")\n")
        hfile.write(indent*tab + "{\n")
        indent += 1
        for p in self.inp:
            hfile.write(p.deallocMem(indent*tab))
        for p in self.inout:
            hfile.write(p.deallocMem(indent*tab, "orig"))
        for p in self.inout:
            hfile.write(p.deallocMem(indent*tab))
        for p in self.out:
            hfile.write(p.deallocMem(indent*tab))
        indent -= 1
        hfile.write(indent*tab + "}\n")

    def generateTestBody(self, hfile):
#         out = []
#         inp = []
#         inout = []
#         for p in icode.signature:
#             if p.isOut and p.isIn:
#                 inout += [p]
#             elif p.isOut:
#                 out += [p]
#             else:
#                 inp += [p]
        params = []
        buildcall = []
        kernelcall = []
        validatecall = []
        for p in self.inp:
            params += [ p.declareAsPointer() ]
            buildcall.append(p.name)
            pre = "*" if isinstance(p, Scalars) else ""
            kernelcall.append(pre+p.name)
            validatecall.append(pre+p.name)
        for p in self.inout:
            params += [ p.declareAsPointer("orig") ]
            name = "orig" + p.name
            buildcall.append(name)
            validatecall.append(name)
        for p in self.inout:
            params += [ p.declareAsPointer() ]
            buildcall.append(p.name)
            kernelcall.append(p.name)
            validatecall.append(p.name)
        for p in self.out:
            params += [ p.declareAsPointer() ]
            buildcall.append(p.name)
            kernelcall.append(p.name)
            validatecall.append(p.name)

        tab = "  "
        indent = 0
        
        hfile.write(indent*tab + "int test()\n")
        hfile.write(indent*tab + "{\n")
        
        indent += 1
        for p in params:
            hfile.write(indent*tab + p + ";\n")
        hfile.write(indent*tab + "myInt64 start, end, overhead;\n")
        hfile.write(indent*tab + "double cycles = 0.;\n")
        hfile.write(indent*tab + "size_t num_runs = RUNS, multiplier = 1;\n")
        hfile.write(indent*tab + "int retCode = 0;\n\n")

        hfile.write(indent*tab + "build(")
        for n in buildcall[:-1]:
            hfile.write("&" + n + ", ")
        hfile.write("&" + buildcall[-1] + ");\n")
        hfile.write("#ifdef VALIDATE\n")
        kernel = "kernel("
        for n in kernelcall[:-1]:
            kernel += n + ", "
        kernel += kernelcall[-1] + ");\n"
        hfile.write(indent*tab + kernel)
        hfile.write(indent*tab + "retCode = validate(")
        for n in validatecall:
            hfile.write(n + ", ")
        hfile.write("ERRTHRESH);\n")
        hfile.write("#endif\n")
        hfile.write("#ifdef TEST\n")
        hfile.write(indent*tab + "if(!retCode) {\n")
        indent += 1
        hfile.write(indent*tab + "init_tsc();\n")
        hfile.write(indent*tab + "overhead = get_tsc_overhead();\n\n")
        hfile.write(indent*tab + "do {\n")
        indent += 1
        hfile.write(indent*tab + "num_runs = num_runs * multiplier;\n")
        hfile.write(indent*tab + "start = start_tsc();\n")
        hfile.write(indent*tab + "for(size_t i = 0; i < num_runs; i++) {\n")
        indent += 1
        hfile.write(indent*tab + kernel)
        indent -= 1
        hfile.write(indent*tab + "}\n")
        hfile.write(indent*tab + "end = stop_tsc(start);\n")
        hfile.write(indent*tab + "if (end > overhead) end -= overhead;\n\n")
        hfile.write(indent*tab + "cycles = (double) end;\n")
        hfile.write(indent*tab + "multiplier = ceil (  (CYCLES_REQUIRED) / (cycles)  + 1.0 );\n")
        indent -= 1
        hfile.write(indent*tab + "} while (multiplier > 2);\n\n")
        hfile.write(indent*tab + "list< double > cycleList, flopList;\n")
        hfile.write(indent*tab + "size_t Rep = NUMREP;\n\n")
        hfile.write(indent*tab + "double flops = " + str(self.llprog.getFlops()) + ";\n\n")

        hfile.write(indent*tab + "for (int k = 0; k < Rep; k++) {\n\n")
        indent += 1
        for p in self.inout:
            hfile.write(p.memCpy(indent*tab, p.name, "orig"))
        hfile.write("\n" + indent*tab + "start = start_tsc();\n")
        hfile.write(indent*tab + "for (int i = 0; i < num_runs; ++i) {\n")
        indent += 1
        hfile.write(indent*tab + kernel)
        indent -= 1
        hfile.write(indent*tab + "}\n")
        hfile.write(indent*tab + "end = stop_tsc(start);\n")
        hfile.write(indent*tab + "end -= overhead;\n\n")
        hfile.write(indent*tab + "cycles = ((double) end) / num_runs;\n\n")
        hfile.write(indent*tab + "cycleList.push_back(cycles);\n")
        hfile.write(indent*tab + "flopList.push_back(flops);\n")
        indent -= 1
        hfile.write(indent*tab + "}\n\n")
        hfile.write(indent*tab + "dumpList(cycleList, string(EXEC_PATH) + \"/cycles.txt\");\n")
        hfile.write(indent*tab + "dumpList(flopList, string(EXEC_PATH) + \"/flops.txt\");\n\n")
        indent -= 1
        hfile.write(indent*tab + "}\n")
        hfile.write("#endif\n")
        hfile.write(indent*tab + "destroy(")
        for n in buildcall[:-1]:
            hfile.write(n + ", ")
        hfile.write(buildcall[-1] + ");\n\n")
        hfile.write(indent*tab + "return retCode;\n")
        indent -= 1
        hfile.write(indent*tab + "}")

#   dumpList(cycleList, string(EXEC_PATH) + "/cycles.txt");
#   dumpList(flopList, string(EXEC_PATH) + "/flops.txt");
# 
#   destroy(a, A0, A1, B, b, initC, C);
# 
#   return retCode;
# }
    
    def generateTester(self):
        hfilebasename = self.opts['hfilebasename']
        hfullname = self.opts['compileroot'] + '/' + self.opts['compilename'] + '/' + hfilebasename + '_tester.h'
        hfile = open(hfullname, 'w')
    
        hfile.write("/*\n")
        hfile.write(" * " + hfilebasename + "_tester.h\n")
        hfile.write(" *\n")
        hfile.write(str(self.llprog))
        hfile.write(" *\n")
        hfile.write(" * Created on: " + str(date.today()) + "\n")
        hfile.write(" * Author: danieles\n")
        hfile.write(" */\n\n")
        hfile.write("#pragma once\n\n")

        for incfile in ['<iostream>', '<sstream>', '<ctime>', '<list>', '<cstdlib>', '<cstring>', '<cmath>']:
            hfile.write("#include " + incfile + "\n")
        hfile.write("\n");
        for incfile in ['\"tsc.h\"', '\"helpers.h\"', '\"CommonDefs.h\"']:
            hfile.write("#include " + incfile + "\n")

        hfile.write("\n");
        hfile.write('#include \"kernels/' + hfilebasename + '_kernel.h\"\n')

        if self.opts.get('validate', True):
            hfile.write('#include \"kernels/' + hfilebasename + '_validate.h\"\n')
            hfile.write("\n\n")
            self.generateValidate(hfile)

        hfile.write("\n\n")
        self.generateBuild(hfile)
        hfile.write("\n\n")
        self.generateDestroy(hfile)
        hfile.write("\n\n")
        self.generateTestBody(hfile)

        hfile.close()
    
    def generateLatex(self, sllprog, version=None, comment=None):
        params = '-'.join(str(p) for p in self.opts['static_params'])
        destfile = '%s/results/%s/tex/%s-%s.' % (self.opts['logroot'], self.opts['testname'], self.opts['hfilebasename'], params)
        destfile += ( (str(version) + '.') if version is not None else '') + 'tex'  
        hfile = open(destfile, 'w')
        hfile.write(sllprog.toLatex(icode, comment=comment))
        hfile.close()
        
    def generateSigmaLL(self, llprog):
        sllprog = rewriteToSigma(llprog, self.opts)
        
        dumptex = not self.opts.get('onlygen', False) and self.opts.get('dumptex', False) 
        if dumptex:
            i = 0
            llhash = str(hash(llprog)) + '.'
            strll = str(llprog).replace('\n', '\n% ')
            self.generateLatex(sllprog, llhash+str(i), strll)
        for rs in self.opts['slrs']:
            slrm = self.opts['slrm'](sllprog, rs, self.opts)
            sllprog = slrm.next()
            if dumptex:
                i+=1
                self.generateLatex(sllprog, llhash+str(i), strll)
        
        return sllprog
    
    def generateKernel(self, sllprog):
        bindExpression(sllprog, icode, self.opts)

        computeDependencies(sllprog, self.opts)
        self.opts['codegen'](sllprog, self.opts)

        sllprog.resetComputed()
        
        icode.flatten()
        if self.opts['scarep']:
            scalarRep(self.opts)
            if self.opts.get('ssa', False):
                icode.placePhiFunctions()
                icode.rename(self.opts)
                icode.deSSA()
        if self.opts.get('alignrep', False):
            print 'Applying alignment replacement...'
            alignRep(self.opts)
         
        if 'printkernel' in self.opts and self.opts['printkernel']:
            self.opts['unparser'](sys.stdout).unparse(self.opts["func_name"])

#     def generateCIR(self, sllprog):
#         bindExpression(sllprog, icode, self.opts)
# 
#         computeDependencies(sllprog, self.opts)
#         self.opts['codegen'](sllprog, self.opts)
# 
#         sllprog.resetComputed()
#         icode.flatten()
# 
#     def generateCKernel(self):
#         if self.opts['scarep']:
#             scalarRep(self.opts)
#             if self.opts['ssa']:
#                 icode.placePhiFunctions()
#                 icode.rename(self.opts)
#                 icode.deSSA()
#         if self.opts.get('alignrep', False):
#             print 'Applying alignment replacement...'
#             alignRep(self.opts)
#          
#         if 'printkernel' in self.opts and self.opts['printkernel']:
#             self.opts['unparser'](sys.stdout).unparse(self.opts["func_name"])
                
    def resetCompilerStatus(self):
#        binding.bindingTable.resetTable() 
        icode.resetLists()
        resetCounters()

    def copy_header(self, kernel_file):
        hfilebasename = self.opts['hfilebasename']
        hfullname = self.opts['compileroot'] + '/' + self.opts['compilename'] + '/kernels/' + hfilebasename + '_kernel.h'

        args = shlex.split("cp " + kernel_file + " " + hfullname)
        subprocess.call(args)
        
        #Use the right tester
        hfilebasename = self.opts['hfilebasename']
        testfolder = self.opts['compileroot'] + '/' + self.opts['compilename']
        hfullname = testfolder + '/testers.h'
        hfile = open(hfullname, 'w')

        hfile.write("/*\n")
        hfile.write(" * testers.h\n")
        hfile.write(" *\n")
        hfile.write(" * Created on: " + str(date.today()) + "\n")
        hfile.write(" * Author: danieles\n")
        hfile.write(" */\n")
        hfile.write("\n#pragma once\n\n")
        if self.opts.get('remote_execution', False):
            hfile.write("#define EXEC_PATH \".\"\n\n") 
        else:
            hfile.write("#define EXEC_PATH \"" + testfolder + "\"\n\n")
        hfile.write("#include \"" + hfilebasename + "_tester.h\"\n\n")
        
        hfile.close()
        
    def generateHeader(self, llprog):
        hfilebasename = self.opts['hfilebasename']
        hfullname = self.opts['compileroot'] + '/' + self.opts['compilename'] + '/kernels/' + hfilebasename + '_kernel.h'
        hfile = open(hfullname, 'w')
    
        hfile.write("/*\n")
        hfile.write(" * " + hfilebasename + "_kernel.h\n")
        hfile.write(" *\n")
        hfile.write(str(llprog))
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
        
        add_func_defs = self.opts['isaman'].get_add_func_defs()
        print "\t> Including additional function definitions: " + str(len(add_func_defs)) + "\n"
        for f in add_func_defs:
            hfile.write(f + "\n")
            
#         i = 0
        for i,param in enumerate(self.opts['static_params']):
            hfile.write("#define PARAM" + str(i) + " " + str(param) + "\n")
#             i += 1

        if self.opts['validate']:
            hfile.write("\n#define ERRTHRESH " + self.opts['errthresh'] + "\n")
            hfile.write("\n#define SOFTERRTHRESH " + self.opts.get('softerrthresh', "1e10") + "\n")

        hfile.write("\n#define NUMREP " + self.opts['numrep'] + "\n")

        hfile.write("\n#define floord(n,d) (((n)<0) ? -((-(n)+(d)-1)/(d)) : (n)/(d))")
        hfile.write("\n#define ceild(n,d)  (((n)<0) ? -((-(n))/(d)) : ((n)+(d)-1)/(d))")
        hfile.write("\n#define max(x,y)    ((x) > (y) ? (x) : (y))")
        hfile.write("\n#define min(x,y)    ((x) < (y) ? (x) : (y))")
        hfile.write("\n#define Max(x,y)    ((x) > (y) ? (x) : (y))")
        hfile.write("\n#define Min(x,y)    ((x) < (y) ? (x) : (y))")
        
        hfile.write("\n\n\n")
        
        self.opts['unparser'](hfile).unparse(self.opts["func_name"])
        
        hfile.close()
        
        #Use the right tester
        hfilebasename = self.opts['hfilebasename']
        testfolder = self.opts['compileroot'] + '/' + self.opts['compilename']
        hfullname = testfolder + '/testers.h'
        hfile = open(hfullname, 'w')

        hfile.write("/*\n")
        hfile.write(" * testers.h\n")
        hfile.write(" *\n")
        hfile.write(" * Created on: " + str(date.today()) + "\n")
        hfile.write(" * Author: danieles\n")
        hfile.write(" */\n")
        hfile.write("\n#pragma once\n\n")
        if self.opts.get('remote_execution', False):
            hfile.write("#define EXEC_PATH \".\"\n\n") 
        else:
            hfile.write("#define EXEC_PATH \"" + testfolder + "\"\n\n")
        hfile.write("#include \"" + hfilebasename + "_tester.h\"\n\n")
        
        hfile.close()

#    def prepareMake(self):
#        copy = "cp"
#        mkdir = "mkdir"
#        basefiles = self.opts['basefiles'] + [ self.opts['hfilebasename'] + "_tester.h" ]
#        origindir = self.opts['testroot'] + '/' + self.opts['altver'] + "/"
#        origin = " ".join([ origindir+f for f in basefiles ])
#        makefile = origindir + ("Verify" if self.opts['validate'] else "Release") + "/Makefile" 
#        origin += " " + makefile
#        destination = self.opts['compileroot'] + '/' + self.opts['compilename']
#        if not os.path.exists(destination):
#            args = shlex.split(mkdir + " " + destination)
#            subprocess.call(args)
#        if not os.path.exists(destination + "/kernels"):
#            args = shlex.split(mkdir + " " + destination + "/kernels")
#            subprocess.call(args)
#        args = shlex.split(copy + " " + origin + " " + destination)
#        subprocess.call(args)

    def runRemoteExperiment(self):
        ''' Run a complete experiment (compile, execute, collect results) on a remote device. 
        
        The execution of this method should have exactly the same effects as executing an experiment locally.
        Returns the exit code of the execution.
        '''
        device = Device(self.opts['hostname'], self.opts['username'], password=self.opts.get('password', None), 
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
            cflags += ' -DERM' if self.opts.get('erm', False) else ''
            cflags += ' -DTEST' if self.opts.get('test', True) else ''
            cflags += ' -DCONTONERR' if self.opts.get('contonerr', False) else ''
            measLib = self.opts['meas'] if 'meas' in self.opts else "" 
            ldflags = measLib + " " + (self.opts['ldflags'] if 'ldflags' in self.opts else "")
            platform = self.opts.get('platform', self.opts['arch'].__name__)
#             arch = self.opts['arch'].__name__
            
            if 'compilepath' in self.opts and self.opts['compilepath']:
                path_command = 'export PATH=$PATH:%s' % self.opts['compilepath']
            clean_command = 'make -s clean'
            if self.opts.get('erm', False):
                compile_command = 'make -s CC=%s CFLAGS=\"%s\" erm' % (cc, cflags)
            else:
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
        exec_command = self.opts.get('exec', './main')
        output_files = self.opts.get('outputfiles', [])
        if self.opts.get('test', True):
            output_files.extend(['flops.txt', 'cycles.txt'])
        
        config = {
            'compileCommands': [com for com in [path_command, clean_command, compile_command, asm_command] if com],
            'execCommands': [exec_command],
            'outputFiles': output_files,
            'repetitions': 1,
        }
        
        experiment = Experiment(device, config)
        if self.opts['cross-compile']:
            print "Cross-compiling code...\n"
            self.compileCode()
            if 'asmflags' in self.opts:
                print "Generating asm file...\n"
                self.genAsm()
            experiment.add_file_from_filesystem('%s/%s' % (makedir, 'main'), 'main', is_executable=True)
        else:
            files_to_copy = self.opts['basefiles'] + ['testers.h', '%s_tester.h' % self.opts['hfilebasename'], 
                                                      'tsc_%s.cpp' % platform, self.opts['makefile'] ]
            import ntpath
            for addf in self.opts.get('additionals', []):
                files_to_copy.append( ntpath.basename(addf) )
            for local_filename in files_to_copy:
                experiment.add_file_from_filesystem('%s/%s' % (makedir, local_filename), local_filename)
            experiment.add_folder_from_filesystem('%s/kernels' % makedir, prefix_path='kernels')
        medclient = Client(self.opts['mediatorhostname'], int(self.opts['mediatorport']))
        print "Sending experiment to Mediator...\n"
        results = medclient.run_experiments([experiment])
        exit_code = self.processRemoteExpResults(results)
        return exit_code

    def run_erm_experiment(self):
        ''' Run a complete experiment (compile, execute, collect results) on ERM. 
        '''
        
        erm_config_file = '%s/devices/%s.conf' % (self.opts.get('main_config_folder', ''), 'erm')
        erm_opts = deepcopy(self.opts)
        erm_opts.update(parse_config_file(erm_config_file))
        #Used to copy to log folder's erm folder special output from erm.  
        self.opts['copytoermlog'] = erm_opts.get('copytoermlog', [])
        
        basefiles = [ f for f in erm_opts['basefiles'] if f not in self.opts['basefiles'] ]        
        origindir = erm_opts['testroot'] + "/"
        origin = " ".join([ origindir+f for f in basefiles ])
        destination = erm_opts['compileroot'] + '/' + erm_opts['compilename']
        args = shlex.split("cp " + origin + " " + destination)
        subprocess.call(args)
        
        device = Device(erm_opts['hostname'], erm_opts['username'], password=erm_opts.get('password', None), 
                        rsa_key_file=erm_opts.get('rsakeyfile', None), rsa_pass=erm_opts.get('rsakeypass', ''),
                        port=erm_opts['port'], exp_root_folder=erm_opts['exprootfolder'], os=erm_opts.get('os', 'LINUX'),
                        affinity=erm_opts.get('affinity', None))
        
        makedir = erm_opts['compileroot'] + '/' + erm_opts['compilename']
        path_command = ''
        compile_command = ''
        asm_command = ''
        if not erm_opts['cross-compile']: # remote compilation
            scaType = 0 if erm_opts['precision'] == 'float' else 1
            cc = erm_opts['cc']
            ld = erm_opts.get('ld', cc)
            
            if erm_opts['vectorize']:
                optscflags = erm_opts['cflags-vec']
            else:
                optscflags = erm_opts['cflags']
            
            cflags = optscflags + (' -DVALIDATE' if erm_opts['validate'] else '') + ' -DTYPE=' + str(scaType) + ' -DALIGN=' + str(erm_opts['align'])
            cflags += ' -DERM'
            cflags += ' -DTEST' if erm_opts.get('test', True) else ''
            cflags += ' -DCONTONERR' if erm_opts.get('contonerr', False) else ''
            arch = erm_opts['arch'].__name__
            
            if 'compilepath' in erm_opts and erm_opts['compilepath']:
                path_command = 'export PATH=$PATH:%s' % erm_opts['compilepath']
            clean_command = 'make -s clean'
            compile_command = 'make -s CC=%s CFLAGS=\"%s\" erm' % (cc, cflags)
            
            makelog = open(makedir + '/erm.make.log', 'w')
            makelog.write("CC = " + cc + "\n")
            makelog.write("LD = " + ld + "\n")
            makelog.write("CFLAGS = " + cflags + "\n")
            makelog.write("LDFLAGS = " + "" + "\n")
            makelog.write("ARCH = " + arch + "\n")
            makelog.write("\n" + compile_command + "\n")
            makelog.close()
        else: # cross-compilation
            clean_command = 'rm -rf ./*.txt'
        exec_command = erm_opts.get('exec', './main')
        output_files = erm_opts.get('outputfiles', ['flops.txt', 'cycles.txt'])
        
        config = {
            'compileCommands': [com for com in [path_command, clean_command, compile_command, asm_command] if com],
            'execCommands': [exec_command],
            'outputFiles': output_files,
            'repetitions': 1,
        }
        
        experiment = Experiment(device, config)
        if erm_opts['cross-compile']:
            print "Cross-compiling code...\n"
            self.compileCode()
            experiment.add_file_from_filesystem('%s/%s' % (makedir, 'main'), 'main', is_executable=True)
        else:
            files_to_copy = erm_opts['basefiles'] + ['testers.h', '%s_tester.h' % erm_opts['hfilebasename'], 
                                                      'tsc_%s.cpp' % erm_opts['arch'].__name__, erm_opts['makefile'] ]
            for local_filename in files_to_copy:
                experiment.add_file_from_filesystem('%s/%s' % (makedir, local_filename), local_filename)
            experiment.add_folder_from_filesystem('%s/kernels' % makedir, prefix_path='kernels')
        medclient = Client(erm_opts['mediatorhostname'], int(erm_opts['mediatorport']))
        print "Running same experiment with ERM...\n"
        results = medclient.run_experiments([experiment])
        exit_code = self.processRemoteExpResults(results, prefix='erm.')
        return exit_code
    
    def processRemoteExpResults(self, results, prefix=''):
        ''' Process the results of a remote experiment execution.
        
        Creates the needed output files in the local filesystem with the content that is included 
        in the mediator response (results). Returns the exit code of the remote experiment execution.
        '''
        folder = self.opts['compileroot'] + '/' + self.opts['compilename']
        if 'error' in results:
            raise Exception('%s: %s' % (results['error']['reason'], results['error']['message']))
        with open(os.path.join(folder, prefix+'output.txt'), 'w') as f:
            f.write(results['data'][0].get('output', ''))
        if 'error' in results['data'][0]:
            print results['data'][0].get('output', '')
            raise Exception('%s: %s' % (results['data'][0]['error']['reason'], results['data'][0]['error']['message']))
        
        for file_result in results['data'][0]['results'][0]['execResults']:
            with open(os.path.join(folder, prefix+file_result['outputFile']), 'w') as f:
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
        cflags += ' -DCONTONERR' if self.opts.get('contonerr', False) else ''
#         cflags += (' -DERRTHRESH=%s'%self.opts['errthresh']) if self.opts.get('validate', False) else ''
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
#         optscflags = self.opts['cross-cflags'] if crossCompile and 'cross-cflags' in self.opts else self.opts['cflags']
        compilepath = self.opts['cross-compilepath'] if crossCompile and 'cross-compilepath' in self.opts else self.opts['compilepath']  
        platform = self.opts.get('platform', self.opts['arch'].__name__)
#         arch = self.opts['arch'].__name__
        cflags = '%s%s -DTYPE=%d -DALIGN=%d' % (optscflags, (' -DVALIDATE' if self.opts['validate'] else ''), scaType, self.opts['align'])
        asmflags = self.opts['cross-asmflags'] if crossCompile and 'cross-asmflags' in self.opts else self.opts['asmflags']
        env = {'PATH': compilepath} if compilepath else None
        
        args = shlex.split('make -s -C ' + makedir + ' CC=' + cc + ' CFLAGS=\"' + cflags + '\" ASMFLAGS=\"' + asmflags + '\" ARCH=\"' + platform + '\" asm')
        subprocess.call(args, env=env)
            
    def runCode(self):
        progname = self.opts['compileroot'] + '/' + self.opts['compilename'] + '/main'
        if 'affinity' in self.opts:
            progname = "taskset -c " + str(self.opts['affinity'][0]) + " " + progname
        args = shlex.split(progname)
        return subprocess.call(args)
    
    def collectMeasurement(self):
#             resfilename = self.opts['compileroot'] + '/' + self.opts['compilename'] + '/outcome'
#             resfile = open(resfilename, 'r')
#             resstr = csv.reader(resfile).next()
#             resfile.close()
#             res = [ float(r) for r in resstr ]
#             return res
        return self.measurer.collectMeasurement()
    
    def printKernel(self, lexpr):
        self.generateKernel(lexpr)
        self.opts['unparser'](sys.stdout).unparse(self.opts["func_name"])
        
        
##############################################################################

# def testGenerate(lexpr, opts):
#     lrm = opts['lrm'](lexpr, None, opts)
# #    binding.bindingTable.resetTable() 
# #    icode.resetLists()
# #    src.alexpr.resetCounters()
#     
#     lexpr = lrm.next()
#     
#     while lexpr:
#         sigmal = rewriteToSigma(lexpr, opts)
#         sigmal = simplifyIndices(sigmal, opts)
# #         sigmal = lexpr
#         if opts['merge']: 
#             sigmal = merge(sigmal, opts)
#             sigmal = sumExchange(sigmal, opts)
# 
#         resetDependencies(sigmal, opts, [])
#         sigmal = computeDependencies(sigmal, opts, [])
# 
#         bindExpression(sigmal, icode, opts)
#         if not opts['init']: avoidInit(sigmal, icode, [], opts)
# #        printDependencies(sigmal, opts, [])
# 
#         opts['codegen'](sigmal, opts)
#     
#         icode.flatten()
#         if opts['scarep']:
#             scalarRep(opts)
#         if opts['ssa']:
#             icode.placePhiFunctions()
#             icode.rename(opts)
#             icode.deSSA()
#     
#     #    icode.printCFG()
#     #    icode.computeDT()
#     #    icode.printDT()
#     #    print icode.computeDF()
#     #    print "\n\n\n\n\n"
#     #    icode.printFlat()
#         opts['unparser'](sys.stdout).unparse(opts["func_name"])
# 
# #        binding.bindingTable.resetTable() 
#         icode.resetLists()
#         resetCounters()
#         
#         lexpr = lrm.next()


# if __name__ == "__main__":
#     
#     opts = {'func_name': "mmm", 'init': False, "scarep": False, "ssa": False, "merge": True}
#     opts['lrs'] = FixedRuleSet
#     opts['lrm'] = SimpleLRM
# #     opts['lrs'] = AtlasRuleSet
# #     opts['lrm'] = OfflineLRM
#     opts['random'] = True
#     opts['limit'] = 0
#     opts['codegen'] = CodeGenerator
#     opts['unparser'] = Unparser
#     opts['unrollinner'] = False
#     opts['indexorder'] = {0:'t', 1:'s', 2:'i'} # Priority among Temp. loc., Spa. loc., and ILP    
#     opts['vectorize'] = True
#     opts['nu'] = 4
#     opts['precision'] = 'double'
# #     opts['isaman'] = ISAManager([x86(opts), SSE(opts), SSE2(opts), SSE3(opts), SSSE3(opts), SSE4_1(opts), AVX(opts) ])
# 
#     nu = 4 if not opts['vectorize'] else opts['nu']
#     
#     M,N = 1,1
#     K = 4
#     a = Matrix("a", scalar, (1,1))
#     b = Matrix("b", scalar, (1,1))
#     c = Matrix("c", scalar, (1,1), attr={'o':True, 'i':False})
# #     A = Matrix("A", scalar, (M,K))
#     A = Matrix("A", scalar, (M,K))
#     B = Matrix("B", scalar, (K,N))
# #     B = Matrix("B", scalar, (M,K))
#     C = Matrix("C", scalar, (M,N))
#     D = Matrix("D", scalar, (M,N))
#     E = Matrix("E", scalar, (M,N))
#     F = Matrix("F", scalar, (M,N), attr={'o':True, 'i':False})
#     G = Matrix("G", scalar, (N,M))
#     H = Matrix("H", scalar, (M,M), attr={'o':True, 'i':False})
#     x = Matrix("x", scalar, (N,1))
#     z = Matrix("z", scalar, (M,1))
#     y = Matrix("y", scalar, (M,1))
#     yout = Matrix("y", scalar, (M,1), attr={'o':True, 'i':False})
#     
# #     expr = Assign(Tile((2,1), Tile((1,2), D)), Tile((2,1), Tile((1,2), A))*Tile((1,1), Tile((2,2), B)))
#     
# #     expr = Assign(Tile(2,D), Tile(2,a)*T(Tile(2,A)))
# #     expr = Assign(Tile(2,D), Tile(2,a)*T(Tile(2,A))*Tile(2,B)+Tile(2,D))
# #     expr = Assign(Tile((3,1), Tile((1,4),F)), Tile((3,1), Tile((1,4),a))*(Tile((3,2), Tile((1,4),A))*Tile((2,1), Tile((4,4),B)))+Tile((3,1), Tile((1,4),b))*Tile((3,1), Tile((1,4),C)))
# #     expr = Assign(F, a*(A*B)+b*C)
# #     expr = Assign(F, a*(T(A)*B)+b*C)
# #     expr = Assign(Tile( (3, 2), Tile( (4, 4), F ) ), ( ( Tile( (3, 2), Tile( (4, 4), a ) ) * ( Tile( (3, 9), Tile( (4, 4), A ) ) * Tile( (9, 2), Tile( (4, 4), B ) ) ) ) + ( Tile( (3, 2), Tile( (4, 4), b ) ) * Tile( (3, 2), Tile( (4, 4), F ) ) ) ))
#     expr = Assign(Tile(nu,F), Tile(nu,A)*Tile(nu,B))
#     expr = Assign(y, a*(C*x))
#     expr = Assign(Tile((1,5),Tile(nu,F)), Tile(1,Tile(nu,A))*Tile((1,5),Tile(nu,B)))
#     expr = Assign(Tile((1,6),Tile(nu,F)), Tile((1,6),Tile(nu,a))*(Tile(1,Tile(nu,A))*Tile((1,6),Tile(nu,B)))+Tile((1,6),Tile(nu,b))*Tile((1,6),Tile(nu,F)))
#     expr = Assign(yout, C*x+yout)
#     expr = Assign(Tile((1,2),Tile(nu,yout)), Tile((1,2),Tile(nu,C))*Tile((2,1),Tile(nu,x))+Tile((1,1),Tile(nu,a))*Tile((1,1),Tile(nu,yout)))
#     expr = Assign(Tile(nu,F), Tile(nu,A)*Tile(nu,B))
#    expr = Assign(Tile(nu,D), Tile(nu,A)*Tile(nu,B))
#     expr = Assign(Tile(nu,F), Tile(nu,A)*Tile(nu,B) + Tile(nu,F))
#     expr = Assign(Tile((1, 1), y), Tile((1, 1), a)*Tile((1, 1), A)*Tile((1, 1), x) + Tile((1, 1), b)*Tile((1, 1), y))
#     expr = Assign(Tile(nu,D), (Tile(nu,A)+Tile(nu,C)) * Tile(nu,B))
#     expr = Assign(Tile(nu,F), Tile(nu,a)*(Tile(nu,A)*Tile(nu,B)) + Tile(nu,b)*(Tile(nu,C)+Tile(nu,D)+Tile(nu,E)) + Tile(nu,F))
#     expr = Assign(Tile(nu,F), Tile(nu,a)*Tile(nu,A)*Tile(nu,B) + Tile(nu,b)*Tile(nu,F))
#     expr = Assign(Tile(nu,F), Tile(nu,A)*Tile(nu,B)+Tile(nu,a)*Tile(nu,C)+Tile(nu,D)+T(Tile(nu,E))+Tile(nu,F))
#     expr = Assign(F, A*B+C)
#     expr = Assign(Tile(nu,D), Tile(nu,a)*Tile(nu,B))
#     expr = Assign(Tile(nu,D), Tile(nu,A)*Tile(nu,B))
#     expr = Assign(Tile(nu,D), Tile(nu,A)+Tile(nu,B))
#     expr = Assign(Tile(nu,D), Tile(nu,A)+Tile(nu,B)+Tile(nu,C))
#     expr = Assign(Tile(nu,D), (Tile(nu,A)+Tile(nu,C))*Tile(nu,B))
#     expr = Assign(Tile((2,2),D), T(Tile((2,2),A)))
#     expr = Assign(Tile(2,D), Tile(2,A)*Tile(2,B))
#    A = Matrix("A", scalar, (M,N))
#    B = Matrix("B", scalar, (M,N))
#    D = Matrix("D", scalar, (M,N), attr={'o':True, 'i':False})

#    x,y,z = Matrix("x", scalar, (M,N)), Matrix("y", scalar, (M,N)), Matrix("z", scalar, (M,N))
#    w = Matrix("w", scalar, (M,N), attr={'o':True, 'i':False})
    
#    expr = Assign(Tile(2,w), T(Tile(2,x))+Tile(2,y))
#    expr = Assign(Tile(2,w), Tile(2,a)*Tile(2,x)+Tile(2,y))

#    expr = Assign(w, T(x)+y)
#    expr = Assign(Tile((1,2),w), T(Tile((2,1),x))+Tile((1,2),y))
#    expr = Assign(Tile(2,w), Tile(2,a)*Tile(2,x)+Tile(2,y))
    
#     i0,k0 =  Index("i0", 0, M, 1), Index("k0", 0, K, 1)
#     
#     fi0 = fHbs(1, M, i0.i, 1)
#     fk0 = fHbs(1, K, k0.i, 1)
#     fI = fHbs(1, 1, 0, 1) 
#     glhs  = G(fi0, A, fk0)
#     grhs  = G(fk0, y, fI)
#     smul0 = glhs * grhs
#     ssca0 = S(fi0, smul0, fI)
#     
#     sexpr = Sum([ ssca0 ], [k0,i0], acc=True, outDep=[ ssca0.fL.of(0), ssca0.fR.of(0) ])
# 
#     smul1 = glhs * grhs
#     gTOut = G(fi0, sexpr, fI)
#     sadd  = gTOut + smul1 
#     ssca1 = S(fi0, sadd, fI)
#     
#     sexpr.inexpr.append(ssca1)
#     sexpr.setAsPred()
# 
#     i1 =  Index("i1", 0, M, 1)
#     fi1 = fHbs(1, M, i1.i, 1)
#     
#     gsca = G(fI, a, fI)
#     gmat = G(fi1, sexpr, fI)
#     smul = Kro(gsca, gmat)
#     ssca = S(fi1, smul, fI)
#     topsum = Sum([ ssca ], [i1], outDep=[ ssca.fL.of(0), ssca.fR.of(0) ])
# 
#     expr = Assign(y, topsum)

#    idxListSum = [i,j]
#    idxListMul = [k]
#    uFactorsSum = [sympy.sympify(1),sympy.sympify(1)]
#    uFactorsMul = [sympy.sympify(1)]
#    suml,sumr = fHbs(1,M,i.i,1), fHbs(1,N,j.i,1)
#    mullr = fHbs(1,K,k.i,1)
#    
#    ga = G(suml, A, mullr)
#    gx = G(mullr, x, sumr)
#    
#    mul0 = Mul(ga, gx)
#    sigmaMul = Sum([ mul0 ], idxListMul, uFactorsMul, acc=True, init=opts['init'], outDep=[ i.i, j.i ])
#    
#    mul1 = Mul(ga, gx)
#    sum1 = sigmaMul + mul1
#    sigmaMul.inexpr.append(sum1)
#    
#    gw = G(suml, w, sumr)
#    add = sigmaMul + gw
#    
#    ssum = S(suml, add, sumr)
#    sigmaSum = Sum([ ssum ], idxListSum, uFactorsSum, init=opts['init'], outDep=[ i.i, j.i ])
#    
#    expr = Assign(w, sigmaSum) 
    
#     testGenerate(expr, opts)
