#General imports:

import os
import shlex
import subprocess
import webcolors
import hashlib
# from numpy import *
from pylab import setp
from matplotlib import rc
#from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
import matplotlib.lines as lns

from src.compiler import send_email_with_log

class ResultManager(object):
    def __init__(self):
        super(ResultManager, self).__init__()
        background_color =(0.90,0.90,0.90) #'#C0C0C0' 
        grid_color = 'white' #FAFAF7'
        rc('text', usetex=True)
        rc('axes', facecolor = background_color)
        rc('axes', edgecolor = grid_color)
        rc('axes', linewidth = 1.2)
        rc('axes', grid = True )
        rc('axes', axisbelow = True)
        rc('grid',color = grid_color)
        rc('grid',linestyle='-' )
        rc('grid',linewidth=1.5 )
        rc('xtick.major',size =4 )
        rc('xtick.minor',size =0 )
        rc('ytick.major',size =0 )
        rc('ytick.minor',size =0 )
        rc('font', family='serif')
        self.series = []
        self.variants_dict = {}
        self.markers = []
        self.colors=[]
        self.lw=[]
        self.linestyles=[]
        self.default_colors=['#000000', '#202020', '#404040', '#606060', '#808080', '#A0A0A0', '#505050', '#707070', '#909090', '#B0B0B0' ]
        self.ms = [18.]*len(self.default_colors)
        self.default_markers=['', 'v', '^','o','s','p', '*', '>', '<']
        self.default_linestyles=['-'] * len(self.colors)
        self.default_lw = [3.] + [1.] * (len(self.default_colors) - 1)
        
    def addCurve(self, curve, size, out, dump=True, basefolder="", curve_name="", curve_marker=".", curve_color="#000000", curve_lw=1., curve_linestyle='-', rank_by_variants=None):
        
        if not curve in self.series:
            self.series.append(curve)
            self.markers.append(curve_marker)
            self.linestyles.append(curve_linestyle)
            self.colors.append(curve_color)
            self.lw.append(curve_lw)
            self.variants_dict[curve] = []
#         self.series[curve][size] = out[0]
        if dump:
            for filename,i in zip(['perf.txt', 'flops.txt', 'cycles.txt'], range(3)):
                f = open(basefolder+'/'+curve+'/'+filename, 'a')
                f.write(" ".join([str(v) for v in out[i]]) + '\n')
                f.close()

            rank_by_variants = {} if rank_by_variants is None else rank_by_variants
            for vartag,meas in rank_by_variants.items():
                pfc = meas[1:]
                md5_vartag = hashlib.md5(vartag).hexdigest()
                vardir = basefolder+'/'+curve+'/perf_variants/'+md5_vartag
                if not os.path.exists(vardir):
                    self.variants_dict[curve].append(vartag)
                    args = shlex.split("mkdir -p " + vardir)
                    subprocess.call(args)
                    with open(vardir+'/vartag.txt', 'a') as f:
                        f.write(vartag + '\n')
                for i,filename in enumerate(['perf.txt', 'flops.txt', 'cycles.txt']):
                    with open(vardir+'/'+filename, 'a') as f:
                        f.write(" ".join([str(v) for v in pfc[i]]) + '\n')
                
            prepend = ""
            if os.path.exists(basefolder+'/'+curve+'/sizes.txt'):
                prepend = " "
            f = open(basefolder+'/'+curve+'/sizes.txt', 'a')
            f.write(prepend + size)
            f.close()
            if not os.path.exists(basefolder+'/'+curve+'/legend.txt'):
                f = open(basefolder+'/'+curve+'/legend.txt', 'w')
                f.write(curve if curve_name == "" else curve_name)
                f.close()
            
    
    def _setup_x_axis(self, curve, xLabelStride):
        file_in = open(curve+'/sizes.txt','r')
        txDataLabels = file_in.readline().rstrip('\n').split(' ')
        file_in.close()

        xDataLabels = ['']*len(txDataLabels) 
        xDataLabels[::xLabelStride] = txDataLabels[::xLabelStride] 

        xData = range(len(xDataLabels))
        x_min=xData[0]
        x_max=xData[-1]    

        return (x_min, x_max, xDataLabels, xData) 
    
    def _add_line(self, ax, nFLOPS, nCycles, plotStats, xData, color, linestyle, lw, marker, markeredgecolor, markersize, label, yDataAll=None):

        yData =[]
        for f,c in zip(nFLOPS,nCycles):
            yData.append([float(vf)/float(vc) for vf, vc in zip(f,c) if vf != '' and vc != ''])
        if yDataAll is not None:
            yDataAll.append(yData)
        
        if plotStats:    
            """
            Percentile boxes
            On each box, the central mark is the median, the edges of the box are the lower hinge (defined as the 25th percentile
            ) and the upper hinge (the 75th percentile), the whiskers extend to the most extreme data points not considered outliers,
             this ones are plotted individually.    
            """
#                 rectanglesWidths = [0 for x in xData]
            rectanglesWidths = [0]*len(xData)
            bp = ax.boxplot(yData, positions=xData, widths = rectanglesWidths)

            setp(bp['medians'], color='black')
            setp(bp['fliers'], color=color,marker='None')
            setp(bp['whiskers'], color=color, linestyle= '-')
            setp(bp['boxes'], color=color)
            setp(bp['caps'], color=color)
    
            medians = range(len(xData))
            for j in range(len(xData)):
                med = bp['medians'][j]
                medianX = []
                medianY = []
                for k in range(2):
                    medianX.append(med.get_xdata()[k])
                    medianY.append(med.get_ydata()[k])
                    medians[j] = medianY[0]    
    
            ax.plot(xData, medians, linestyle, lw=lw, color=color, marker=marker, markeredgecolor=markeredgecolor, markersize=markersize, label=label, mfc='white', mew=2.)
        else:
            ax.plot(xData, yData, linestyle, lw=lw, color=color, marker=marker, markeredgecolor=markeredgecolor, markersize=markersize, label=label)    
        
    def makePlot(self, opts, y_min, y_max, title, x_label, y_label, basefolder, 
                 plotfilename, addLegend=True, addTitle=True, xLabelStride=1, series=None, seriesMarkers=None, seriesColors=None, 
                 seriesLw=None, seriesLinestyles=None, plotStats=True, adjust_yaxis=True):

        fig = plt.figure()
        if addTitle:
            fig.suptitle(title,fontsize=14,fontweight='bold')
        ax = fig.add_subplot(111)
        
        # formatting of axis labels
        ax.set_title(y_label,fontsize=12,ha='left',position=(0,1))
        ax.set_xlabel(x_label, fontsize=12)

        # uncomment to remove the x-axis
#         ax.axes.get_xaxis().set_visible(False)
        
        self.series = [ basefolder+'/results/'+curve for curve in self.series ]
        
        # Load the data
        if series is not None:
            linestyles = seriesLinestyles + self.linestyles
            markers = seriesMarkers + self.markers
            colors = seriesColors + self.colors
            lw = seriesLw + self.lw
            series += self.series
        else:
            linestyles = self.linestyles
            markers = self.markers
            colors = self.colors
            lw = self.lw
            series = self.series
                    
        x_min, x_max, xDataLabels, xData = self._setup_x_axis(series[0], xLabelStride) if series else (0, 0, [], []) 
        yDataAll = []
        
        def _read_multiline(filename, linelist):
            with open(filename,'r') as file_in:
                for line in file_in.readlines():
                    split_line = line.rstrip('\n').split(' ')
                    linelist.append(split_line)
            
        for i, curve in enumerate(series):
            
            print "Plotting curve " + curve
            
            #Plot Max line
            nCycles = []
            _read_multiline(curve+'/cycles.txt', nCycles)
#             file_in = open(curve+'/cycles.txt','r')
#             lines = file_in.readlines()
#             for line in lines:
#                 split_line = line.rstrip('\n').split(' ')
#                 nCycles.append(split_line)
#             file_in.close()
        
            nFLOPS = []
            _read_multiline(curve+'/flops.txt', nFLOPS)
#             file_in = open(curve+'/flops.txt','r')
#             lines = file_in.readlines()
#             for line in lines:
#                     split_line = line.rstrip('\n').split(' ')
#                     nFLOPS.append(split_line)
#             file_in.close()
            
            curve_label = ''
            with open(curve+'/legend.txt','r') as file_in:
                curve_label = file_in.readlines()[0].strip()
#             file_in = open(curve+'/legend.txt','r')
#             curve_label = file_in.readlines()[0].strip()
#             file_in.close()
            
            self._add_line(ax, nFLOPS, nCycles, plotStats, xData, colors[i], linestyles[i], lw[i], markers[i], colors[i], self.ms[i], curve_label, yDataAll)
            if os.path.exists(curve+'/perf_variants'):
#                 Temp
#                 rgb_color_lst = [[255,51,51],[175,51,51],[95,51,51]]
#                 mrkr_lst = ['D','v','s','*']
#                 cm_lst = [ (rgb,mrkr) for mrkr in mrkr_lst for rgb in rgb_color_lst  ]
#                 Temp
                vartags = sorted(next(os.walk(curve+'/perf_variants'))[1])
                num_lines = len(vartags)
                color_stride = 256//num_lines
#                 rgb_color = [255,51,51]
                rgb_color = [255,33,33]
#                 for cm,vartag in zip(cm_lst,vartags):
#                 for m,vartag in zip(mrkr_lst,vartags):
                for vartag in vartags:
                    vardir = curve+'/perf_variants/'+vartag
                    nCycles = []
                    _read_multiline(vardir+'/cycles.txt', nCycles)
                    nFLOPS = []
                    _read_multiline(vardir+'/flops.txt', nFLOPS)

#                     hex_color = webcolors.rgb_to_hex(cm[0])
#                     self._add_line(ax, nFLOPS, nCycles, plotStats, xData, hex_color, '--', 1., cm[1], hex_color, self.ms[i], vartag.replace('_','-'))

                    hex_color = webcolors.rgb_to_hex(rgb_color)
#                     self._add_line(ax, nFLOPS, nCycles, plotStats, xData, hex_color, '--', 1., m, '#333333', self.ms[i], vartag.replace('_','-'))
                    self._add_line(ax, nFLOPS, nCycles, plotStats, xData, hex_color, '--', 1., markers[i], hex_color, self.ms[i], vartag.replace('_','-'))
                    rgb_color[0] -= color_stride 
                    
#             yData =[]
#             for f,c in zip(nFLOPS,nCycles):
#                 yData.append([float(vf)/float(vc) for vf, vc in zip(f,c) if vf != '' and vc != ''])
#             yDataAll.append(yData)
#             
# #             txDataLabels = []
# #             file_in = open(curve+'/sizes.txt','r')
# #             txDataLabels = file_in.readline().rstrip('\n').split(' ')
# # #             txDataLabels = [s[1:s.find(',')] for s in  file_in.readline().rstrip('\n').split(' ')]
# #             file_in.close()
# # 
# #             xDataLabels = ['']*len(txDataLabels) 
# #             xDataLabels[::xLabelStride] = txDataLabels[::xLabelStride] 
# # 
# #             xData = range(len(xDataLabels))
# #             x_min=xData[0]
# #             x_max=xData[-1]    
#         
#             if plotStats:    
#                 """
#                 Percentile boxes
#                 On each box, the central mark is the median, the edges of the box are the lower hinge (defined as the 25th percentile
#                 ) and the upper hinge (the 75th percentile), the whiskers extend to the most extreme data points not considered outliers,
#                  this ones are plotted individually.    
#                 """
# #                 rectanglesWidths = [0 for x in xData]
#                 rectanglesWidths = [0]*len(xData)
#                 bp = ax.boxplot(yData, positions=xData, widths = rectanglesWidths)
# 
#                 setp(bp['medians'], color='black')
#                 setp(bp['fliers'], color=colors[i],marker='None')
#                 setp(bp['whiskers'], color=colors[i], linestyle= '-')
#                 setp(bp['boxes'], color=colors[i])
#                 setp(bp['caps'], color=colors[i])
#         
#                 medians = range(len(xData))
#                 for j in range(len(xData)):
#                     med = bp['medians'][j]
#                     medianX = []
#                     medianY = []
#                     for k in range(2):
#                         medianX.append(med.get_xdata()[k])
#                         medianY.append(med.get_ydata()[k])
#                         medians[j] = medianY[0]    
#         
#                 ax.plot(xData, medians, linestyles[i], lw=lw[i], color=colors[i], marker=markers[i], markeredgecolor=colors[i], markersize=self.ms[i], label=curve_label, mfc='white', mew=2.)
#             else:
#                 ax.plot(xData, yData, linestyles[i], lw=lw[i], color=colors[i], marker=markers[i], markeredgecolor=colors[i], markersize=self.ms[i], label=curve_label)    
#             # end of if-else
#         #end for loop

#        ax.set_xticklabels(xDataLabels, rotation=45)
        ax.xaxis.grid(False)
        ax.tick_params(direction='out', pad=5)        
        ax.xaxis.set_ticks_position('bottom')
        ax.spines['bottom'].set_color('#000000')
        ax.spines['bottom'].set_linewidth(2)
        for line in ax.xaxis.get_ticklines():
            line.set_markeredgewidth(1)
            line.set_marker(lns.TICKDOWN)
        ax.set_xticklabels(xDataLabels)
        #ax.legend(numpoints=1, loc='best',frameon = False )
#         ax.legend(numpoints=1, loc='best').get_frame().set_visible(False)
        legframe = ax.legend(numpoints=1, loc='best', fancybox=True).get_frame()
        legframe.set_facecolor('#FFFFFF')
#         legframe.set_visible(False)
        
        if adjust_yaxis:
            y_min, y_max = self.adjust_yaxis_scale(yDataAll, y_min, y_max, addLegend)
        #x-y range
        ax.axis([x_min-0.15,x_max+0.15,y_min,y_max])
        
#         ax.legend().set_visible(addLegend)
        if not addLegend:
            ax.legend().set_visible(False)
        
# Uncomment to change the font size of the x-axis labels
#         ax.tick_params(axis='x', labelsize=2)
        
        #save file
        print '\n\nSaving plot in ' + basefolder+'/plots/'+plotfilename + '\n\n'
        fig.savefig(basefolder+'/plots/'+plotfilename, dpi=250,  bbox_inches='tight')
        send_email_with_log(opts, "Perf Plot", attachments=[(basefolder+'/plots/', plotfilename)], extra_to=opts.get('onlypdfs', []))
        
    def adjust_yaxis_scale(self, yDataAll, suggested_ymin, suggested_ymax, legendOn=True):
        ymin = suggested_ymin
        ymax = suggested_ymax
        max_val = max([max([max(row) for row in yData]) for yData in yDataAll])
        if legendOn:
            ymax = (1 + 0.15 + len(yDataAll) / 6.0) * max_val
        else:
            ymax = (1 + 0.15) * max_val
        return ymin, ymax
            
        
