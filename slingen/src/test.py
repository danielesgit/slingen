#!/usr/bin/python
'''
Created on Apr 11, 2012

@author: danieles
'''

import random
import os
import subprocess
import shlex
import time
import itertools
import traceback
from datetime import datetime, date
from copy import copy, deepcopy

from src.dsls.processing import trackTiling
from src.dsls.ll import parseLL

# from src.rules.llrules import AtlasRuleSet_NuWay_HSquareTileForReg
# from src.rules.lrms import HOfflineLRM, HSimpleLRM
# 
# from src.generator import StructuresGenerator, CodeGenerator
from src.compiler import Compiler, openLog, closeLog, printToLog, send_email_with_log
from src.libtest import LibraryCode
# from src.unparser import Unparser
# 
# from src.isas.isabase import ISAManager
# from src.isas.avx import AVX
# from src.isas.sse4_1 import SSE4_1
# from src.isas.ssse3 import SSSE3
# from src.isas.sse3 import SSE3
# from src.isas.sse2 import SSE2
# from src.isas.sse import SSE
# from src.isas.x86 import x86
# from src.isas.armv7 import ARMv7
# from src.isas.neon import NEON 

def procOutcome(resMgr, compiler, opts, pad="", sizeParams=None):
    params = opts['static_params'] if sizeParams is None else sizeParams
    openLog(opts)
    validated = True
    if opts['validate']:
        if all(compiler.validateList):
            if not 'libname' in opts: 
                printToLog(pad + str(compiler.llprog) + " : " + "VALIDATED." + "\n\n", opts, openf=False, closef=False)
            else:
                printToLog(pad + opts.get('libname', "<Libname???>") + " : " + "VALIDATED." + "\n\n", opts, openf=False, closef=False)
            print "* Test passed" # if the test hadn't passed, an exception would have already been raised
        else:
            validated = False
            if not 'libname' in opts: 
                printToLog(pad + str(compiler.llprog) + " : " + "FAILED " + str(compiler.validateList.count(False)) + "/" + str(len(compiler.validateList))+ " VALIDATIONS." + "\n", opts, openf=False, closef=False)
            else:
                printToLog(pad + opts.get('libname', "<Libname???>") + " : " + "FAILED " + str(compiler.validateList.count(False)) + "/" + str(len(compiler.validateList))+ " VALIDATIONS." + "\n", opts, openf=False, closef=False)
            print "* Test not passed: " + str(compiler.validateList.count(False)) + "/" + str(len(compiler.validateList)) 
    if opts.get('test', True):
        if validated:
            bestout = compiler.outcome[0]
            print "\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Best computation $$$$$$$$$$$$$$$$$$$$$$$$$$$$\n" 
#             print "Tested expression: " + str(bestout[0]) + "\nPerformance: " + str(bestout[1][0]) + " f/c\n"
            print "Performance: " + str(bestout[1][0]) + " f/c\n"
            print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n"
    
            msg = pad
            for p in params:
                msg += str(p) + ', '
            printToLog(msg + str(bestout[0]) + ", " + str(bestout[1][0]) + " f/c -- folder: " + opts['compileroot']+'/'+opts['compilename'] + "\n\n", opts, openf=False, closef=False)
        
            size = str(params[0])
            for p in params[1:]:
                size +=  ','+str(p) 
            if len(params) > 1:
                size = '[' + size + ']'
            
#             if not 'libname' in opts:
#                 printTracking(bestout[0], size, opts) # Add track-tiling (tt) attribute to desired matrices (see mmm tester)
            
            curve_name = opts['legendname'] if 'legendname' in opts else ""
            resMgr.addCurve(opts['testname'], size, bestout[1][1:], basefolder=opts['logroot']+'/results', curve_name=curve_name,
                            curve_marker=opts['marker'], curve_color=opts['color'], curve_lw=opts['lw'], rank_by_variants=deepcopy(compiler.rank_by_variants))
        else:
            print "Some tests failed: Performance report aborted.\n\n"
    closeLog(opts)
    if opts.get('copycompfolder', True):
        compfolder = opts['compileroot'] + '/' + opts['compilename']
        dstfolder = opts['logroot'] + '/results/' + opts['testname'] + '/compfolder'
        print "Copying compilation folder: " + compfolder + "\n\n"
        if not os.path.exists(dstfolder):
            args = shlex.split("mkdir -p " + dstfolder)
            subprocess.call(args)
        if os.path.exists(compfolder):
            args = shlex.split("cp -r " + compfolder + " " + dstfolder)
            subprocess.call(args)


def printTracking(llprog, size, opts):
    """
    Deprecated.
    """
    for s,eqn in zip(llprog.stmtList, range(len(llprog.stmtList))):
        ttDict = {}
        trackTiling(s.eq, ttDict)
        for d, tLists in ttDict.items():
            for i, tl in zip(range(len(tLists)), tLists): 
                trackfname = opts['logroot'] + '/results/' + opts['testname'] + '/' +"eq" + str(eqn) + d + (str(i) if i > 0 else '') + '.csv' 
                trackfile = open(trackfname, 'a')
                rec = size + ',' + str(tl[0])
                for tc in tl[1:]:
                    rec += ',' + str(tc)
                rec += '\n' 
                trackfile.write( rec ) 
                trackfile.close()
    
def recordTime(time, opts):
    logfullname = opts['logroot'] + '/results/' + opts['testname'] + '/time.txt'
    logfile = open(logfullname, 'a')
    msg = str(time) + "\n"
    logfile.write( msg ) 
    logfile.close()

def prepareMake(opts):
    ''' Prepare the local filesystem for the upcoming experiment.
    
    Copy the necessary static files (e.g. helper files, Makefile) and create the necessary folders 
    for compilation and logging. 
    '''
    if 'libname' in opts or not 'onlygen' in opts or not opts['onlygen']:
        copy = "cp"
        mkdir = "mkdir -p"
#         mv = "mv"
        basefiles = opts['basefiles'] + [ opts['makefile'] ]        
        if 'libname' in opts  or not opts.get('gentester', True):
            basefiles.append("testers/" + opts['hfilebasename'] + "_tester.h")
        platform = opts.get('platform', opts['arch'].__name__)
        basefiles.append('tsc/tsc_%s.cpp' % platform)
        origindir = opts['testroot'] + "/"
        origin = " ".join( [ origindir+f for f in basefiles ] + opts.get('additionals', []) )
        destination = opts['compileroot'] + '/' + opts['compilename']
        if not os.path.exists(destination):
            args = shlex.split(mkdir + " " + destination)
            subprocess.call(args)
        if not 'libname' in opts and not os.path.exists(destination + "/kernels"):
            args = shlex.split(mkdir + " " + destination + "/kernels")
            subprocess.call(args)
        args = shlex.split(copy + " " + origin + " " + destination)
        subprocess.call(args)
        # If tester has specialized sizes copy them to compileroot
        origin = origindir+"testers/" + opts['hfilebasename'] + "_tester"
        if ('libname' in opts  or not opts.get('gentester', True)) and os.path.exists(origin):
            args = shlex.split(copy + " -r " + origin + " " + destination + "/kernels")
            subprocess.call(args)
        folder = opts['logroot'] + '/plots'
        if not os.path.exists(folder):
            args = shlex.split(mkdir + " " + folder)
            subprocess.call(args)
        folder = opts['logroot'] + '/results/' + opts['testname']
        if not os.path.exists(folder):
            args = shlex.split(mkdir + " " + folder)
            subprocess.call(args)
            if opts.get('dumptex', False):
                subfolder = folder + '/tex'
                args = shlex.split(mkdir + " " + subfolder)
                subprocess.call(args)
        if opts.get('erm', False) or opts.get('runwitherm', False):
            subfolder = folder + '/erm'
            if not os.path.exists(subfolder):
                args = shlex.split(mkdir + " " + subfolder)
                subprocess.call(args)
        if opts.get('copyallkernels', False):
            subfolder = folder + '/genkernels'
            if not os.path.exists(subfolder):
                args = shlex.split(mkdir + " " + subfolder)
                subprocess.call(args)

# def mmupdate(M, K, N, opts):
#     A = Matrix("A", scalar, (M,K))
#     B = Matrix("B", scalar, (K,N))
#     C = Matrix("C", scalar, (M,N), attr={'o':True, 'i':False})
#     
#     expr = Assign(C, A*B+C)
#     
#     return expr
# 
# def mmm(M, K, N, opts):
# #     A = Matrix("A", scalar, (M,K), attr={'tt':True})
# #     B = Matrix("B", scalar, (K,N), attr={'tt':True})
#     A = Matrix("A", scalar, (M,K))
#     B = Matrix("B", scalar, (K,N))
#     C = Matrix("C", scalar, (M,N), attr={'o':True, 'i':False})
#     
# #     nu = 1 if not opts['vectorize'] else opts['nu']
# 
#     expr = Assign(C, A*B)
#     
#     return expr
# 
# def gemm(M, K, N, opts):
#     a = Matrix("a", scalar, (1,1))
#     A = Matrix("A", scalar, (M,K), attr={'tt':True})
#     B = Matrix("B", scalar, (K,N), attr={'tt':True})
#     b = Matrix("b", scalar, (1,1))
#     C = Matrix("C", scalar, (M,N), attr={'o':True, 'i':False})
#     
# #     nu = 1 if not opts['vectorize'] else opts['nu']
# #     expr = Assign(Tile(nu,C), Tile(nu,a)*Tile(nu,A)*Tile(nu,B)+Tile(nu,b)*Tile(nu,C))
#     expr = Assign(C, a*(A*B)+b*C)
#     
#     return expr
# 
# def gemam(M, K, N, opts):
#     a = Matrix("a", scalar, (1,1))
#     A0 = Matrix("A0", scalar, (K,M))
#     A1 = Matrix("A1", scalar, (K,M))
#     B = Matrix("B", scalar, (K,N))
#     b = Matrix("b", scalar, (1,1))
#     C = Matrix("C", scalar, (M,N), attr={'o':True, 'i':False})
#     
# #     nu = 1 if not opts['vectorize'] else opts['nu']
# #     expr = Assign(Tile(nu,C), Tile(nu,a)*Tile(nu,A)*Tile(nu,B)+Tile(nu,b)*Tile(nu,C))
#     expr = Assign(C, a*(T(A0+A1)*B)+b*C)
#     
#     return expr

def testing1to3Param(resMgr, p0, f0, f1, f2, opts):
    sizesP0 = range(p0[0], p0[1]+1) if len(p0) == 2 else range(p0[0], p0[1]+1, p0[2]) 

    sizes = [ (f0(i),f1(i),f2(i),i) for i in sizesP0 ]
    
    fine = True
    for M,K,N,i in sizes:
        try:
            opts['static_params'] = [M,K,N]
            genCode = not 'libname' in opts 
            onlygen = 'onlygen' in opts and opts['onlygen'] 
            
            compiler = None
            if genCode:
                llprog = parseLL({'M': M, 'K': K, 'N': N}, opts)
                compiler = Compiler(llprog, opts)
            else:
                compiler = LibraryCode(opts)
            s = datetime.now()
            if not onlygen: 
                printToLog("  " + "Starting compiler at " + str(s) + " ----------------------------------------", opts)
            fine = fine and compiler.compile()
            e = datetime.now()
            if not (genCode and onlygen): 
                procOutcome(resMgr, compiler, opts, "  ", sizeParams=[i])
                printToLog("  " + "Compiling took " + str(e - s) + " ----------------------------------------------------------", opts)
                recordTime((e - s).total_seconds(), opts)
        except Exception:
            if opts.get('breakonexc',False):
                raise
            fine = False
            openLog(opts)
            ts = '%s.%s' % (date.today().isoformat(), time.strftime('%H-%M-%S', time.localtime(time.time())))
            msg = "=@"*10 + " Begin Exc Report from testing1to3Param (" + ts + ") " + "=@"*10 + "\n"
            msg += "-"*10 + " opts " + "-"*10 + "\n"
            msg += str(opts) + "\n"
            msg += "-"*10 + " traceback " + "-"*10 + "\n"
            printToLog(msg, opts, openf=False, closef=False)
            traceback.print_exc(file=opts['logfile'])
            msg = "\n" + "=@"*10 + " End Exc Report (" + ts + ") " + "=@"*10 + "\n"
            printToLog(msg, opts, openf=False)
    return fine

def testing3Param(resMgr, p0, p1, p2, opts):
    ''' Test the kernel for the cartesian product of the values in the given intervals p0, p1, p3. '''
    sizesP0 = range(p0[0], p0[1]+1) if len(p0) == 2 else range(p0[0], p0[1]+1, p0[2]) 
    sizesP1 = range(p1[0], p1[1]+1) if len(p1) == 2 else range(p1[0], p1[1]+1, p1[2]) 
    sizesP2 = range(p2[0], p2[1]+1) if len(p2) == 2 else range(p2[0], p2[1]+1, p2[2]) 

    sizes = [ (i,j,k) for i in sizesP0 for j in sizesP1 for k in sizesP2 ]

    fine = True
    for M,K,N in sizes:
        try:
    
            opts['static_params'] = [M,K,N]
            genCode = not 'libname' in opts 
            onlygen = 'onlygen' in opts and opts['onlygen'] 

            compiler = None
            if genCode:
                llprog = parseLL({'M': M, 'K': K, 'N': N}, opts)
    #             expr = eval(opts['hfilebasename'])(M, K, N, opts)
                compiler = Compiler(llprog, opts)
            else:
                compiler = LibraryCode(opts)
            s = datetime.now()
            if not onlygen: 
                printToLog("  " + "Starting compiler at " + str(s) + " ----------------------------------------", opts)
            fine = fine and compiler.compile()
            e = datetime.now()
            if not (genCode and onlygen): 
                procOutcome(resMgr, compiler, opts, "  ")
                printToLog("  " + "Compiling took " + str(e - s) + " ----------------------------------------------------------", opts)
                recordTime((e - s).total_seconds(), opts)
        except Exception:
            if opts.get('breakonexc',False):
                raise
            fine = False
            openLog(opts)
            ts = '%s.%s' % (date.today().isoformat(), time.strftime('%H-%M-%S', time.localtime(time.time())))
            msg = "=@"*10 + " Begin Exc Report from testing3Param (" + ts + ") " + "=@"*10 + "\n"
            msg += "-"*10 + " opts " + "-"*10 + "\n"
            msg += str(opts) + "\n"
            msg += "-"*10 + " traceback " + "-"*10 + "\n"
            printToLog(msg, opts, openf=False, closef=False)
            traceback.print_exc(file=opts['logfile'])
            msg = "\n" + "=@"*10 + " End Exc Report (" + ts + ") " + "=@"*10 + "\n"
            printToLog(msg, opts, openf=False)
    return fine

def testingRandom(resMgr, maxops, maxdim, maxeq, numgen, opts):
    
    fine = True
    llgen = RandomLLGen(maxops=maxops, maxdim=maxdim, maxeq=maxeq)
    for _ in range(numgen):
        genres = llgen.gen()
        srcfile = open(opts['source'], 'w')
        srcfile.write( genres[0] ) 
        srcfile.close()
        
        for pvalues in genres[2]:
            
            try:
                opts['static_params'] = pvalues
                genCode = not 'libname' in opts 
                onlygen = 'onlygen' in opts and opts['onlygen'] 
                
                compiler = None
                if genCode:
                    llprog = parseLL(dict(zip(genres[1], pvalues)), opts)
                    compiler = Compiler(llprog, opts)
                    s = datetime.now()
                    if not onlygen: 
                        printToLog("  " + "Starting compiler at " + str(s) + " ----------------------------------------", opts)
                    fine = fine and compiler.compile()
                    e = datetime.now()
                    if not (genCode and onlygen): 
                        procOutcome(resMgr, compiler, opts, "  ")
                        printToLog("  " + "Compiling took " + str(e - s) + " ----------------------------------------------------------", opts)
                        recordTime((e - s).total_seconds(), opts)
                else:
                    print "Please enable code generation."
            except Exception:
                if opts.get('breakonexc',False):
                    raise
                fine = False
                openLog(opts)
                ts = '%s.%s' % (date.today().isoformat(), time.strftime('%H-%M-%S', time.localtime(time.time())))
                msg = "=@"*10 + " Begin Exc Report from testingRandom (" + ts + ") " + "=@"*10 + "\n"
                msg += "Generation of:\n\n%s\n\nParams:\n\n%s = %s\n\n" % (genres[0], str(genres[1]), str(genres[2]))
                msg += "-"*10 + " opts " + "-"*10 + "\n"
                msg += str(opts) + "\n"
                msg += "-"*10 + " traceback " + "-"*10 + "\n"
                printToLog(msg, opts, openf=False, closef=False)
                traceback.print_exc(file=opts['logfile'])
                msg = "\n" + "=@"*10 + " End Exc Report (" + ts + ") " + "=@"*10 + "\n"
                printToLog(msg, opts, openf=False)
    return fine

# def batax(M, N, opts):
#     b = Matrix("b", scalar, (1,1))
#     A = Matrix("A", scalar, (M,N))
#     x = Matrix("x", scalar, (N,1))
#     y = Matrix("y", scalar, (N,1), attr={'o':True, 'i':False})
#     
# #     nu = 1 if not opts['vectorize'] else opts['nu']
# #     expr = Assign(Tile(nu,y), Tile(nu,a)*(Tile(nu,A)*Tile(nu,x))+Tile(nu,b)*Tile(nu,y))
#     expr = Assign( y, b*(T(A)*(A*x)) )
#     
#     return expr
# 
# def blinf(M, N, opts):
#     A = Matrix("A", scalar, (M,N))
#     x = Matrix("x", scalar, (M,1))
#     y = Matrix("y", scalar, (N,1))
#     b = Matrix("b", scalar, (1,1), attr={'o':True, 'i':False})
#     
# #     nu = 1 if not opts['vectorize'] else opts['nu']
# 
#     expr = Assign(b, T(x)*(A*y))
#     
#     return expr
# 
# def modifiedblinf(M, N, opts):
#     A = Matrix("A", scalar, (M,N))
#     B = Matrix("B", scalar, (M,N))
#     x = Matrix("x", scalar, (M,1))
#     y = Matrix("y", scalar, (N,1))
#     d = Matrix("d", scalar, (1,1))
#     b = Matrix("b", scalar, (1,1), attr={'o':True, 'i':False})
#     
# #     nu = 1 if not opts['vectorize'] else opts['nu']
# 
#     expr = Assign(b, T(x)*((A+B)*y)+d)
#     
#     return expr
# 
# def gesummv(M, N, opts):
#     a = Matrix("a", scalar, (1,1))
#     A = Matrix("A", scalar, (M,N))
#     x = Matrix("x", scalar, (N,1))
#     b = Matrix("b", scalar, (1,1))
#     B = Matrix("B", scalar, (M,N))
#     y = Matrix("y", scalar, (M,1), attr={'o':True, 'i':False})
#     
# #     nu = 1 if not opts['vectorize'] else opts['nu']
# #     expr = Assign(Tile(nu,y), Tile(nu,a)*(Tile(nu,A)*Tile(nu,x))+Tile(nu,b)*Tile(nu,y))
#     expr = Assign(y, a*(A*x)+b*(B*x))
#     
#     return expr
# 
# def mvm(M, N, opts):
#     A = Matrix("A", scalar, (M,N))
#     x = Matrix("x", scalar, (N,1))
#     y = Matrix("y", scalar, (M,1), attr={'o':True, 'i':False})
#     
# #     nu = 1 if not opts['vectorize'] else opts['nu']
# #     expr = Assign(Tile(nu,y), Tile(nu,a)*(Tile(nu,A)*Tile(nu,x))+Tile(nu,b)*Tile(nu,y))
#     expr = Assign(y, A*x)
#     
#     return expr
# 
# def ger(M, N, opts):
#     a = Matrix("a", scalar, (1,1))
#     x = Matrix("x", scalar, (M,1))
#     y = Matrix("y", scalar, (N,1))
#     A = Matrix("A", scalar, (M,N), attr={'o':True, 'i':False})
#     
# #     nu = 1 if not opts['vectorize'] else opts['nu']
# #     expr = Assign(Tile(nu,A), Tile(nu,a)*Tile(nu,x)*T(Tile(nu,y))+Tile(nu,A))
#     expr = Assign(A, a*x*T(y)+A)
#     
#     return expr
# 
# def gemv(M, N, opts):
#     a = Matrix("a", scalar, (1,1))
#     A = Matrix("A", scalar, (M,N), attr={'tt':True})
#     x = Matrix("x", scalar, (N,1))
#     b = Matrix("b", scalar, (1,1))
#     y = Matrix("y", scalar, (M,1), attr={'o':True, 'i':False})
#     
# #     nu = 1 if not opts['vectorize'] else opts['nu']
# #     expr = Assign(Tile(nu,y), Tile(nu,a)*(Tile(nu,A)*Tile(nu,x))+Tile(nu,b)*Tile(nu,y))
#     expr = Assign(y, a*(A*x)+b*y)
#     
#     return expr
# 
# def mma(M, N, opts):
#     A = Matrix("A", scalar, (M,N))
#     B = Matrix("B", scalar, (M,N))
#     C = Matrix("C", scalar, (M,N), attr={'o':True, 'i':False})
#     
#     expr = Assign(C, A+B)
#     
#     return expr
# 
# def smull(M, N, opts):
#     a = Matrix("a", scalar, (1,1))
#     B = Matrix("B", scalar, (M,N))
#     C = Matrix("C", scalar, (M,N), attr={'o':True, 'i':False})
#     
#     expr = Assign(C, a*B)
#     
#     return expr
# 
# def smulr(M, N, opts):
#     A = Matrix("A", scalar, (M,N))
#     b = Matrix("b", scalar, (1,1))
#     C = Matrix("C", scalar, (M,N), attr={'o':True, 'i':False})
#     
#     expr = Assign(C, A*b)
#     
#     return expr
# 
# def trans(M, N, opts):
#     A = Matrix("A", scalar, (M,N))
#     B = Matrix("B", scalar, (N,M), attr={'o':True, 'i':False})
#     
#     expr = Assign(B, T(A))
#     
#     return expr

def testing1to2Param(resMgr, p0, f0, f1, opts):
    sizesP0 = range(p0[0], p0[1]+1) if len(p0) == 2 else range(p0[0], p0[1]+1, p0[2]) 

    sizes = [ (f0(i),f1(i), i) for i in sizesP0 ]
    fine = True
    for M,N,i in sizes:
        try:
            opts['static_params'] = [M,N]
            genCode = not 'libname' in opts 
            onlygen = 'onlygen' in opts and opts['onlygen'] 
            
            compiler = None
            if genCode:
                llprog = parseLL({'M': M, 'N': N}, opts)
    #             expr = eval(opts['hfilebasename'])(M, N, opts)
                compiler = Compiler(llprog, opts)
            else:
                compiler = LibraryCode(opts)
    
            s = datetime.now()
            if not onlygen: 
                printToLog("  " + "Starting compiler at " + str(s) + " ----------------------------------------", opts)
            fine = fine and compiler.compile()
            e = datetime.now()
            
            if not (genCode and onlygen): 
                procOutcome(resMgr, compiler, opts, "  ", sizeParams=[i])
                printToLog("  " + "Compiling took " + str(e - s) + " ----------------------------------------------------------", opts)
                recordTime((e - s).total_seconds(), opts)
        except Exception:
            if opts.get('breakonexc',False):
                raise
            fine = False
            openLog(opts)
            ts = '%s.%s' % (date.today().isoformat(), time.strftime('%H-%M-%S', time.localtime(time.time())))
            msg = "=@"*10 + " Begin Exc Report from testing1to2Param (" + ts + ") " + "=@"*10 + "\n"
            msg += "-"*10 + " opts " + "-"*10 + "\n"
            msg += str(opts) + "\n"
            msg += "-"*10 + " traceback " + "-"*10 + "\n"
            printToLog(msg, opts, openf=False, closef=False)
            traceback.print_exc(file=opts['logfile'])
            msg = "\n" + "=@"*10 + " End Exc Report (" + ts + ") " + "=@"*10 + "\n"
            printToLog(msg, opts, openf=False)
    return fine
    
def testing2Param(resMgr, p0, p1, opts):
    ''' Test the kernel opts['hfilebasename'] for the cartesian product of the values in the given intervals p0, p1. '''
    sizesP0 = range(p0[0], p0[1]+1) if len(p0) == 2 else range(p0[0], p0[1]+1, p0[2]) 
    sizesP1 = range(p1[0], p1[1]+1) if len(p1) == 2 else range(p1[0], p1[1]+1, p1[2]) 
    sizes = [ (i,j) for i in sizesP0 for j in sizesP1 ]
    for M,N in sizes:

        opts['static_params'] = [M, N]
        genCode = not 'libname' in opts 
        onlygen = 'onlygen' in opts and opts['onlygen'] 

        compiler = None
        if genCode:
            llprog = parseLL({'M': M, 'N': N}, opts)
#             expr = eval(opts['hfilebasename'])(N, opts)
            compiler = Compiler(llprog, opts)
        else:
            compiler = LibraryCode(opts)

        s = datetime.now()
        if not onlygen: 
            printToLog("  " + "Starting compiler at " + str(s) + " ----------------------------------------", opts)
        compiler.compile()
        e = datetime.now()
        if not (genCode and onlygen): 
            procOutcome(resMgr, compiler, opts, "  ")
            printToLog("  " + "Compiling took " + str(e - s) + " ----------------------------------------------------------", opts)
            recordTime((e - s).total_seconds(), opts)

# def dot(N, opts):
#     a = Matrix("a", scalar, (1,1))
#     x = Matrix("x", scalar, (N,1))
#     y = Matrix("y", scalar, (N,1))
#     dot = Matrix("dot", scalar, (1,1), attr={'o':True, 'i':False})
#     
# #     nu = 1 if not opts['vectorize'] else opts['nu']
# #     expr = Assign(Tile(nu,dot), Tile(nu,a) + T(Tile(nu,x))*Tile(nu,y))
#     expr = Assign(dot, a + T(x)*y)
#     
#     return expr
# 
# def axpy(N, opts):
#     a = Matrix("a", scalar, (1,1))
#     x = Matrix("x", scalar, (N,1))
#     y = Matrix("y", scalar, (N,1), attr={'o':True, 'i':False})
#     
# #     nu = 1 if not opts['vectorize'] else opts['nu']
# #     expr = Assign(Tile(nu,y), Tile(nu,a)*Tile(nu,x)+Tile(nu,y))
#     expr = Assign(y, a*x+y)
#     
#     return expr

def testing1Param(resMgr, p, opts):
    sizes = range(p[0], p[1]+1) if len(p) == 2 else range(p[0], p[1]+1, p[2])
    fine = True 
    for M in sizes:
        try:
            opts['static_params'] = [M]
            genCode = not 'libname' in opts 
            onlygen = 'onlygen' in opts and opts['onlygen'] 
    
            compiler = None
            if genCode:
                llprog = parseLL({'M': M}, opts)
    #             expr = eval(opts['hfilebasename'])(N, opts)
                compiler = Compiler(llprog, opts)
            else:
                compiler = LibraryCode(opts)
    
            s = datetime.now()
            if not onlygen: 
                printToLog("  " + "Starting compiler at " + str(s) + " ----------------------------------------", opts)
            fine = fine and compiler.compile()
            e = datetime.now()
            
            if not (genCode and onlygen): 
                procOutcome(resMgr, compiler, opts, "  ")
                printToLog("  " + "Compiling took " + str(e - s) + " ----------------------------------------------------------", opts)
                recordTime((e - s).total_seconds(), opts)
        except Exception:
            if opts.get('breakonexc',False):
                raise
            fine = False
            openLog(opts)
            ts = '%s.%s' % (date.today().isoformat(), time.strftime('%H-%M-%S', time.localtime(time.time())))
            msg = "=@"*10 + " Begin Exc Report from testing1Param (" + ts + ") " + "=@"*10 + "\n"
            msg += "-"*10 + " opts " + "-"*10 + "\n"
            msg += str(opts) + "\n"
            msg += "-"*10 + " traceback " + "-"*10 + "\n"
            printToLog(msg, opts, openf=False, closef=False)
            traceback.print_exc(file=opts['logfile'])
            msg = "\n" + "=@"*10 + " End Exc Report (" + ts + ") " + "=@"*10 + "\n"
            printToLog(msg, opts, openf=False)
    return fine

def testingNParam(resMgr, ps, opts):
    ''' Test the kernel for the cartesian product of the values in the given intervals p0, p1, p2, ... '''
    params  = [ pi[0] for pi in ps ] 
    sizesPi = [ range(pi[1], pi[2]+1) if len(pi) == 3 else range(pi[1], pi[2]+1, pi[3]) for pi in ps ]

    sizes = list(itertools.product(*sizesPi))

    fine = True
    for pvalues in sizes:
        try:
    
            opts['static_params'] = list(pvalues)
            genCode = not 'libname' in opts 
            onlygen = 'onlygen' in opts and opts['onlygen'] 

            compiler = None
            if genCode:
                opts['pvalues'] = {p:pvalue for p,pvalue in zip(params,pvalues)}
                llprog = parseLL({p:pvalue for p,pvalue in zip(params,pvalues)}, opts)
                compiler = Compiler(llprog, opts)
            else:
                compiler = LibraryCode(opts)
            s = datetime.now()
            if not onlygen: 
                printToLog("  " + "Starting compiler at " + str(s) + " ----------------------------------------", opts)
            fine = fine and compiler.compile()
            e = datetime.now()
            if not (genCode and onlygen): 
                procOutcome(resMgr, compiler, opts, "  ")
                printToLog("  " + "Compiling took " + str(e - s) + " ----------------------------------------------------------", opts)
                recordTime((e - s).total_seconds(), opts)
        except Exception:
            openLog(opts)
            ts = '%s.%s' % (date.today().isoformat(), time.strftime('%H-%M-%S', time.localtime(time.time())))
            msg = "=@"*10 + " Begin Exc Report from testingNParam (" + ts + ") " + "=@"*10 + "\n"
            msg += "-"*10 + " opts " + "-"*10 + "\n"
            msg += str(opts) + "\n"
            msg += "-"*10 + " traceback " + "-"*10 + "\n"
#             printToLog(msg, opts, openf=False, closef=False)
#             traceback.print_exc(file=opts['logfile'])
            msg += traceback.format_exc()
            msg += "\n" + "=@"*10 + " End Exc Report (" + ts + ") " + "=@"*10 + "\n"
#             printToLog(msg, opts, openf=False)
            printToLog(msg, opts)
            if opts.get('breakonexc',False):
                send_email_with_log(opts, subj="SLinGen Report on Exception", body=msg)
                raise
            fine = False
    return fine

def testing1toNParam(resMgr, p0, fs, opts):
    sizesP0 = range(p0[0], p0[1]+1) if len(p0) == 2 else range(p0[0], p0[1]+1, p0[2]) 

    params = [ f[0] for f in fs ]
    sizes = []
    for i in sizesP0:
        sizes.append( [ f[1](i) for f in fs ] )
    
    fine = True
    for pvalues,i in zip(sizes, sizesP0):
        try:
            opts['static_params'] = pvalues
            genCode = not 'libname' in opts 
            onlygen = 'onlygen' in opts and opts['onlygen'] 
            
            compiler = None
            if genCode:
                opts['pvalues'] = {p:pvalue for p,pvalue in zip(params,pvalues)}
                llprog = parseLL({p:pvalue for p,pvalue in zip(params,pvalues)}, opts)
                compiler = Compiler(llprog, opts)
            else:
                compiler = LibraryCode(opts)
            s = datetime.now()
            if not onlygen: 
                printToLog("  " + "Starting compiler at " + str(s) + " ----------------------------------------", opts)
            fine = fine and compiler.compile()
            e = datetime.now()
            if not (genCode and onlygen): 
                procOutcome(resMgr, compiler, opts, "  ", sizeParams=[i])
                printToLog("  " + "Compiling took " + str(e - s) + " ----------------------------------------------------------", opts)
                recordTime((e - s).total_seconds(), opts)
        except Exception:
#             openLog(opts)
            ts = '%s.%s' % (date.today().isoformat(), time.strftime('%H-%M-%S', time.localtime(time.time())))
            msg = "=@"*10 + " Begin Exc Report from testing1toNParam (" + ts + ") " + "=@"*10 + "\n"
            msg += "-"*10 + " opts " + "-"*10 + "\n"
            msg += str(opts) + "\n"
            msg += "-"*10 + " traceback " + "-"*10 + "\n"
#             printToLog(msg, opts, openf=False, closef=False)
#             traceback.print_exc(file=opts['logfile'])
            msg += traceback.format_exc()
            msg += "\n" + "=@"*10 + " End Exc Report (" + ts + ") " + "=@"*10 + "\n"
            printToLog(msg, opts)
            if opts.get('breakonexc',False):
#                 openLog(opts, 'r')
#                 body = opts['logfile'].read()
#                 closeLog(opts)
                send_email_with_log(opts, subj="SLinGen Report on Exception", body=msg)
                raise
            fine = False
    return fine

def postprocess_config(opts, exp, exp_id, dev, lib, start_time):
    if 'slingen' in lib:
        opts['hfilebasename'] = exp
    else:
        opts['experiment'] = exp
        opts['hfilebasename'] = '%s_%s' % (opts['testerprefix'], exp)
    
    opts['erm'] = (dev == 'erm')
        
    opts['compilename'] = '%s.%s.%s.%s' % (exp_id, dev, date.today().isoformat(), str(random.randint(0,2**32)))
    opts['testname'] = '%s.%s.%s.%s.%s' % (exp_id, dev, lib, date.today().isoformat(), 
                                           time.strftime('%H%M', time.localtime(start_time)))

    opts['exp_id'] = exp_id
    opts['dev'] = dev
    opts['lib'] = lib
    
    if 'remote_execution' not in opts:
        opts['remote_execution'] = True
#     if 'hostname' in opts:
#         opts['remote_execution'] = True
#     else:
#         opts['remote_execution'] = False
    
    if 'osenviron' in opts:
        for p in opts['osenviron']:
            if p not in os.environ['PATH']:
                os.environ['PATH'] += os.pathsep + p
                
    if 'affinity' in opts:
        if not isinstance(opts['affinity'], list):
            opts['affinity'] = [int(opts['affinity'])]
        print "\nSet affinity to one of " + str(opts['affinity'])

#     if not opts.get('vectorize', False):
#         opts['isa'] = getattr(importlib.import_module(opts['arch'][0]), opts['arch'][1]) 
    
#     if 'vectorize' in opts and 'nu' in opts:
    print "\nVectorization opts:"
    print " - vectorize: " + str(opts['vectorize'])
    print " - nu:        " + str(opts['nu'])

    if not 'libname' in opts:
#         arch_isa = getattr(importlib.import_module(opts['arch'][0]), opts['arch'][1])
        isalist = [ opts['arch'](opts) ]
        if opts.get('useintrinsics', False):        
            isalist.append( opts['isa'](opts) )
        opts['isaman'] = opts['isaman'](isalist)
        print " - ISAs:      " + str(isalist)
 
    os.environ['PATH'] = os.environ['PATH'] + ':' + opts.get('texpath','')

def libs_sort_key(libname):
    for i, c in enumerate(LIBS_ORDER):
        if c == libname:
            return (i, libname)
    return (len(LIBS_ORDER), libname)

#order in which the libs will be tested (important for plotting)
LIBS_ORDER = ['slingen', 'hand', 'mkl', 'eigen']

class RandomLLGen(object):
    def __init__(self, maxops, maxdim, maxeq):
        self.maxops = maxops
        self.dims = [ 'M'+str(i) for i in range(maxdim) ] + ['1']
        self.useddims = set()
        self.maxeq = maxeq
        
    def gen(self):
        self.structs = {}
        self.declin = {}
        self.declinout = {}
        self.declout = {}
        self.dimidx = 0
        self.matc = 0
        self.scac = 0
        
        numeq = random.choice(range(1,self.maxeq+1))
        eqs = []
        for _ in range(numeq):
            self.numops=self.maxops
            eqs.append(self.Assign())
            
        p = self.ppDecl(self.declin, 'in')
        p += self.ppDecl(self.declinout, 'inout')
        p += self.ppDecl(self.declout, 'out')
        p += "\n"
        for eq in eqs:
            p += eq + "\n"
        params, values = self.randParams()    
        return [p, params, values]

    def randParams(self):
        staticParams = []
        ranges = []
        baseRange = range(1,51)
        for p in self.useddims:
            staticParams.append(p)
            if p == '1':
                ranges.append([1])
            else:
                ranges.append(range(2,51,random.choice(baseRange)))
        return (staticParams, itertools.product(*ranges))
            
    def ppDecl(self, decl, pos):
        res = ""
        for s in decl:
            res += ",".join(decl[s])
            res += ": " + s[0][0] + "<"
            if s[0][0] != 'scalar':
                if s[0][0] == 'vector':
                    res += s[1][0]
                elif s[0][0] != 'matrix':
                    res += s[1][0] + ', ' + s[0][1]
                else:
                    res += s[1][0] + ', ' + s[1][1]
                res += ', ' + pos + '>;\n'
            else:
                res += pos + '>;\n'
        return res
                
    def getDimSize(self, n):
        dims = []
        for _ in range(n):
            d = random.choice(self.dims)
            dims.append(d)
        self.useddims.update(dims)
        return dims
    
    def getStructInfo(self, dims):
        typ = None
        addInfo = None
#         if dims[1] == '1':
#             if dims[0] == '1':
#                 typ = "scalar"
#             else:
#                 typ = "vector"
        if dims[0] == dims[1] and dims[0] != '1':
            typ = random.choice(['matrix', 'triangular', 'symmetric'])
            if typ != 'matrix':
                addInfo = random.choice(['l', 'u'])
        else:
            typ = "matrix"
        struct = [typ] + ([] if addInfo is None else [addInfo])
        return struct
        
    def Assign(self):
        ops = [ 'Add', 'T', 'Kro', 'Mul', 'Matrix' ]
        dims = self.getDimSize(2)
        struct = self.getStructInfo(dims)
        dropops = set()
        if struct[0] == 'symmetric':
            dropops.update(['Mul'])
        lop = getattr(self, 'Matrix')(dims, 'l', struct, dropops)
        rop = getattr(self, random.choice(ops))(dims, 'r', struct, dropops)
        
        return lop + " = " + rop + ";"
    
    def Add(self, dims, pos, struct, dropops=None):
        if dropops is None: dropops = set()
        possops = [ op for op in [ 'Add', 'T', 'Kro', 'Mul', 'Matrix' ] if op not in dropops ]
        if dims[0] == dims[1]:
            if struct == ['matrix']:
                structs = random.choice([ [['triangular','l'],['triangular','u']], [['triangular','u'],['triangular','l']], [['matrix'],['matrix']], [['symmetric','l'],['symmetric','u']], [['symmetric','u'],['symmetric','l']] ])
            else:
                structs = [copy(struct),copy(struct)]
        else:
            structs = [['matrix'],['matrix']]
        self.numops -= 1
        if self.numops > 0:
            ops = possops
        else:
            ops = [ 'Matrix' ]
        dopsl, dopsr = copy(dropops), copy(dropops)
        if structs[0][0] == 'symmetric':
            dopsl.update(['Mul'])
        lop = getattr(self, random.choice(ops))(dims, pos, structs[0], dopsl)
        if self.numops > 0:
            ops = possops
        else:
            ops = [ 'Matrix' ]
        if structs[1][0] == 'symmetric':
            dopsr.update(['Mul'])
        rop = getattr(self, random.choice(ops))(dims, pos, structs[1], dopsr)
        
        return "(" + lop + " + " + rop + ")"

    def Mul(self, dims, pos, struct, dropops=None):
        if dropops is None: dropops = set()
        possops = [ op for op in [ 'Add', 'T', 'Kro', 'Matrix' ] if op not in dropops ]
        dropops.update(['Mul'])
        if struct[0] == 'triangular':
            k = [dims[0]]
            structs = [copy(struct), copy(struct)]
        else:
            typl = random.choice(['matrix', 'triangular', 'symmetric'])
            if typl != 'matrix':
                lAddInfo = random.choice(['l', 'u'])
                k = [dims[0]]
                if k[0] == dims[1]:
                    typr = random.choice(['matrix', 'triangular', 'symmetric'])
                else:
                    typr = 'matrix'
                if typl == typr:
                    rAddInfo = [ t for  t in ['l', 'u'] if t != lAddInfo][0]
                elif typr != 'matrix':
                    rAddInfo = random.choice(['l', 'u'])
                else:
                    rAddInfo = None
            else:
                lAddInfo = None
                typr = random.choice(['matrix', 'triangular', 'symmetric'])
                if typr != 'matrix':
                    rAddInfo = random.choice(['l', 'u'])
                    k = [dims[1]]
                else:
                    k = self.getDimSize(1)
                    rAddInfo = None
            structs = [[typl] + ([] if lAddInfo is None else [lAddInfo]),[typr] + ([] if rAddInfo is None else [rAddInfo])]
        diml = [dims[0], k[0]]
        dimr = [k[0], dims[1]]
        self.numops -= 1
        if self.numops > 0:
            ops = possops
        else:
            ops = [ 'Matrix' ]
        lop = getattr(self, random.choice(ops))(diml, pos, structs[0], dropops)
        if self.numops > 0:
            ops = possops
        else:
            ops = [ 'Matrix' ]
        rop = getattr(self, random.choice(ops))(dimr, pos, structs[1], dropops)
        
        return "(" + lop + " * " + rop + ")"

    def T(self, dims, pos, struct, dropops=None):
        if dropops is None: dropops = set()
        possops = [ op for op in [ 'Add', 'T', 'Kro', 'Matrix' ] if op not in dropops ]
        dropops.update(['Mul'])
        self.numops -= 1
        if self.numops > 0:
            ops = possops
        else:
            ops = [ 'Matrix' ]
        tstruct = copy(struct)
        if tstruct[0] != 'matrix':
            tstruct[1] = [ t for  t in ['l', 'u'] if t != tstruct[1]][0]
        op = getattr(self, random.choice(ops))(dims[::-1], pos, tstruct, dropops)
        
        return "trans(" + op + ")"

    def Kro(self, dims, pos, struct, dropops=None):
        if dropops is None: dropops = set()
        possops = [ op for op in [ 'Add', 'T', 'Kro', 'Mul', 'Matrix' ] if op not in dropops ]
        ids = [0,1]
        l = random.choice(ids)
        ids.remove(l)
        r = ids[0]
        
        self.numops -= 1
        if self.numops > 0:
            ops = [['Scalar'], possops][l]
        else:
            ops = [['Scalar'], [ 'Matrix' ]][l]
        lop = getattr(self, random.choice(ops))(dims, pos, struct, dropops)
        if self.numops > 0:
            ops = [['Scalar'], possops][r]
        else:
            ops = [['Scalar'], [ 'Matrix' ]][r]
        rop = getattr(self, random.choice(ops))(dims, pos, struct, dropops)
        
        return "(" + lop + " * " + rop + ")"

    def Matrix(self, dims, pos, struct, dropops=None):
        key = None
        baseName = 'A'
        if dims[0] == dims[1] == '1':
            key = (('scalar',),)
            baseName = 'b'
        elif dims[1] == '1':
            key = (('vector',), tuple(dims))
        else:
            key = (tuple(struct), tuple(dims))
        
        inl = self.declin.get(key,[])
        inoutl = self.declinout.get(key,[])
        outl = self.declout.get(key,[])
        
        op = random.choice( sum([inl,inoutl,outl], [baseName+str(self.matc)]) )
        self.matc += 1
        exist = isin = isout = isinout = False
        if op in inl:
            exist = isin = True
        elif op in outl:
            exist = isout = True
        elif op in inoutl:
            exist = isinout = True
        
        if not exist:
            decl = self.declout if pos == 'l' else self.declin  
            if key in decl:
                decl[key].append(op)
            else:
                decl[key] = [op]
        elif (isin and pos == 'l') or (isout and pos == 'r'):
            decl = self.declin if isin else self.declout
            decl[key].remove(op)
            if not decl[key]:
                del decl[key]
            if key in self.declinout:
                self.declinout[key].append(op)
            else:
                self.declinout[key] = [op]
        else:
            decl = None
            if isinout:
                decl = self.declinout
            elif isin:
                decl = self.declin
            else:
                decl = self.declout
            if op not in decl[key]:
                decl[key] = [op]
        return op
    
    def oldMatrix(self, dims, pos, dropops=None):
        op = random.choice(self.mats)
        exist = isin = isout = isinout = False
        if any(map(lambda s: op in s, self.declin.values())):
            exist = isin = True
        elif any(map(lambda s: op in s, self.declout.values())):
            exist = isout = True
        elif any(map(lambda s: op in s, self.declinout.values())):
            exist = isinout = True
        if not exist:
            decl = self.declin if pos == 'r' else self.declout  
            typ = ""
            if dims[1] == '1':
                if dims[0] == '1':
                    typ = "scalar<"
                else:
                    typ = "vector<"+str(dims[0]) + ", "
            elif dims[0] == dims[1]:
                typ = random.choice(['matrix', 'triangular', 'symmetric'])
                if typ != 'matrix':
                    struct = random.choice(['l', 'u'])
                    typ += "<"+str(dims[0])+", "+struct + ", "
                else:
                    typ = "matrix<"+str(dims[0])+", "+str(dims[1]) + ", "
            else:
                typ = "matrix<"+str(dims[0])+", "+str(dims[1]) + ", "
            decl[typ] = set([op])
        elif (isin and pos == 'l') or (isout and pos == 'r'):
            src = self.declin if isin else self.declout
            typ = filter(lambda typ: op in src[typ], src)[0]
            src[typ].remove(op)
            if not src[typ]:
                del src[typ]
            self.declinout[typ] = set([op])
        else:
            decl = None
            if isinout:
                decl = self.declinout
            elif isin:
                decl = self.declin
            else:
                decl = self.declout
            typ = filter(lambda typ: op in decl[typ], decl)[0]
            decl[typ].update([op])
        return op
    
    def Scalar(self, dims, pos, struct, dropops=None):
        return self.Matrix(['1','1'], pos, ['matrix'], dropops)
#         key = (('scalar',),)
#         
#         inl = self.declin.get(key,[])
#         inoutl = self.declinout.get(key,[])
#         outl = self.declout.get(key,[])
#         
#         op = random.choice(sum([inl,inoutl,outl], ['b'+str(self.matc)]))
#         self.matc += 1
#         exist = isin = isout = isinout = False
#         if op in inl:
#             exist = isin = True
#         elif op in outl:
#             exist = isout = True
#         elif op in inoutl:
#             exist = isinout = True
#         
#         if not exist:
#             decl = self.declout if pos == 'l' else self.declin  
#             if key in decl:
#                 decl[key].append(op)
#             else:
#                 decl[key] = [op]
#         elif (isin and pos == 'l') or (isout and pos == 'r'):
#             src = self.declin if isin else self.declout
#             src[key].remove(op)
#             if not src[key]:
#                 del src[key]
#             if key in self.declinout:
#                 self.declinout[key].append(op)
#             else:
#                 self.declinout[key] = [op]
#         else:
#             src = None
#             if isinout:
#                 src = self.declinout
#             elif isin:
#                 src = self.declin
#             else:
#                 src = self.declout
#             if op not in src[key]:
#                 src[key] = [op]
#         return op

if __name__ == '__main__':
    opts = {'source': 'tests/rdiv_nublac.ll'}
    llprog = parseLL({'M':4}, opts)
    print llprog
