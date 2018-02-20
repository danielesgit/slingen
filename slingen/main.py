'''
Created on Dec 18, 2013

@author: danieles
'''

import os
import time
import gc
from datetime import date, timedelta
from copy import deepcopy

from sympy.printing.precedence import precedence
from sympy.printing.str import StrPrinter
 
class IslModPrinter(StrPrinter):
    def _print_Mod(self,expr):
        own_level = precedence(expr)
        return "({} % {})".format(self.parenthesize(expr.args[0], own_level), expr.args[1])
    
    def _print_floor(self, expr):
        return "floord({}, {})".format(*expr.args[0].as_numer_denom())

    def _print_ceiling(self, expr):
        return "ceild({}, {})".format(*expr.args[0].as_numer_denom())

 
from sympy import Basic
 
Basic.__str__ = lambda expr, printer=IslModPrinter(): printer.doprint(expr)

from src.test import testing1Param, testing2Param, testing1to2Param, testing1to3Param, testingRandom, prepareMake, libs_sort_key, postprocess_config,\
    testingNParam, testing1toNParam
from src.dsls.processing import parse_config_file
from src.plotter import ResultManager
from src.compiler import send_email_with_log

MAIN_CONFIG_FOLDER = 'src/config'


if __name__ == '__main__':
    with open('name.txt') as fname:
        print fname.read()

    experiments = [

        ('trlya', testingNParam, [ [('m', 4, 124, 24)] ], 'trlya-4-124-24'),
        ('potrf', testingNParam, [ [('m', 4, 124, 24)] ], 'potrf-4-124-24'),
        ('trsyl', testing1toNParam, [ (4, 124, 24), [('m', lambda n: n), ('n', lambda n: n)] ], 'trsyl-4-124-24'),
        ('trtri', testingNParam, [ [('m', 4, 124, 24)] ], 'trtri-4-124-24'),
        ('kf', testing1toNParam, [(4, 52, 8), [('m', lambda N: N), ('k', lambda N: N), ('n', lambda N: N)] ], 'kf-4-52-8'),
        ('kf', testing1toNParam, [(4, 28, 4), [('m', lambda N: N), ('k', lambda N: N), ('n', lambda N: 28)] ], 'kf-n28-4-28-4'),
        ('gpr', testing1toNParam, [(4, 52, 8), [('m', lambda N: N), ('k', lambda N: N)] ], 'gpr-4-52-8'),
        ('l1a', testing1toNParam, [(4, 52, 8), [('m', lambda N: N), ('k', lambda N: N), ('n', lambda N: N)] ], 'l1a-4-52-8')


    ]

    devices = ['local']
    # if a device doesn't support a lib (see devcompatiblelibs in device config), this lib won't be tested on this device
    # the same happens if an experiment doesn't support a lib
    libs = ['slingen', 'mkl', 'hand', 'polly', 'relapack', 'recsy', 'eigen']
    libs.sort(key=libs_sort_key)

    common_config = parse_config_file('%s/common.conf' % MAIN_CONFIG_FOLDER)
    common_config['main_config_folder'] = MAIN_CONFIG_FOLDER
    overwrite_config_file = '%s/overwrite.conf' % MAIN_CONFIG_FOLDER
    start_all_exps = time.time()
    for experiment in experiments:
        exp_config_file = '%s/experiments/%s.conf' % (MAIN_CONFIG_FOLDER, experiment[0])
        exp = experiment[0]
        exp_fun = experiment[1]
        exp_fun_args = experiment[2]
        exp_id = experiment[3] if len(experiment) >= 4 else exp
        exp_description = experiment[4] if len(experiment) >= 5 else exp
        for dev in devices:
            dev_config_file = '%s/devices/%s.conf' % (MAIN_CONFIG_FOLDER, dev)
            precomp_series = []
            precomp_markers = []
            precomp_linestyles = []
            precomp_colors = []
            precomp_lw = []
            start_time = time.time()
            print 'Experiment %s on %s started on %s.' % (exp, dev, 
                                            time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime(start_time)))
            resMgr = ResultManager()
            something_happend = False
            precomp_order = []
            for lib in libs:
                lib_config_file = '%s/libs/%s.conf' % (MAIN_CONFIG_FOLDER, lib)
                opts = deepcopy(common_config)
                opts.update(parse_config_file(exp_config_file, ignore_non_existent_file=True, opts=opts))
                opts.update(parse_config_file(dev_config_file, opts=opts))
                opts.update(parse_config_file(lib_config_file, opts=opts))
                opts.update(parse_config_file(overwrite_config_file, ignore_non_existent_file=True, opts=opts))
                postprocess_config(opts, exp, exp_id, dev, lib, start_time)
                if ('devcompatiblelibs' in opts and lib not in opts['devcompatiblelibs']) or \
                            ('expcompatiblelibs' in opts and lib not in opts['expcompatiblelibs']):
                    print '%s not compatible with either %s or %s' % (lib, dev, exp_id)
                    continue
                something_happend = True
                fine = True
                if opts.get('useprecomputed', False):
                    precomp_dir = opts['precompdir'] #'_precomputed/%s' % ('vec' if opts['vectorize'] else 'novec')
                    precomp_folders = os.listdir(precomp_dir)
                    precomp_exps = [f for f in precomp_folders if f.startswith('%s.%s.%s.' % (exp_id, dev, lib))]
                    if len(precomp_exps) > 0:
                        precomp_series.append('%s/%s' % (precomp_dir, precomp_exps[0]))
                        precomp_markers.append(opts['marker'])
                        precomp_linestyles.append(opts.get('linestyle', '-'))
                        precomp_colors.append(opts['color'])
                        precomp_lw.append(opts['lw'])
                        print 'Found precomputed results for %s.%s.%s' % (exp_id, dev, lib)
                        continue
                prepareMake(opts)
                fine = exp_fun(resMgr, *(exp_fun_args + [opts]))
            end_time = time.time()
            print 'Experiment %s on %s finished at %s (duration: %s).' % (exp, dev, 
                                    time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime(end_time)), 
                                    str(timedelta(seconds=int(end_time-start_time))))
            
            if opts['plot'] and opts.get('test', True) and (not 'onlygen' in opts or not opts['onlygen']) and something_happend and fine:
                if len(precomp_series) == 0:
                    precomp_series = None
                    precomp_markers = None
                    precomp_linestyles = None
                    precomp_colors = None
                    precomp_lw = None
                filename = '%s.%s.%s.pdf' % (exp_id, dev, date.today().isoformat())
                resMgr.makePlot(opts, 0, 4, exp_description, "n [" +opts['precision']+ "]",  
                                "Performance [f/c]", opts['logroot'], filename, addLegend=opts['addlegend'], addTitle=opts['addtitle'],
                                xLabelStride=opts['xlabelstride'], series=precomp_series, seriesMarkers=precomp_markers, 
                                seriesColors=precomp_colors, seriesLw=precomp_lw, seriesLinestyles=precomp_linestyles, adjust_yaxis=False)
#                 resMgr.makePlot(opts, 0, opts['peak'][opts['isa'].__name__][opts['precision']], exp_description, "n [" +opts['precision']+ "]",  
#                                 "Performance [f/c]", opts['logroot'], filename, addLegend=opts['addlegend'], addTitle=opts['addtitle'],
#                                 xLabelStride=opts['xlabelstride'], series=precomp_series, seriesMarkers=precomp_markers, seriesColors=precomp_colors, seriesLw=precomp_lw, seriesLinestyles=precomp_linestyles)
        opts.clear()
        gc.collect()
    end_all_exps = time.time()
    final_msg = 'Total execution time for %d experiments on %d devices: %s' % (len(experiments), len(devices), str(timedelta(seconds=int(end_all_exps - start_all_exps))))
    print final_msg
    send_email_with_log(common_config, subj="Experiments Completed", body=final_msg)
    
