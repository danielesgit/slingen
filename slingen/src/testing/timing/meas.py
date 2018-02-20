'''
Created on Jun 13, 2013

@author: danieles
'''

import csv
from operator import itemgetter

class Meas(object):
    def __init__(self, opts):
        super(Meas, self).__init__()
        self.opts = opts
    
    def collectMeasurement(self):
        flopfilename = self.opts['compileroot'] + '/' + self.opts['compilename'] + '/flops.txt'
        tscfilename = self.opts['compileroot'] + '/' + self.opts['compilename'] + '/cycles.txt'
        filenames = [ flopfilename, tscfilename ]
        
        lists = []
        for name in filenames:
            f = open(name, 'r')
            line = f.readline().rstrip("\n").split(" ")
            lists.append([ float(i) for i in line ])
            f.close()

        ps = [ f/s for f,s in zip(*lists) ]
        ps.sort()
        p = ps[len(ps)/2]
        
        res = [ p, ps ] + lists
        return res

class MeasManager(object):
    def __init__(self):
        super(MeasManager, self).__init__()
    
    def getBestMeasurement(self, rankDict):
        return max(rankDict.iteritems(), key=itemgetter(1))
    
    def compare(self, meas0, meas1):
        if meas0 and (meas0[0] > meas1[0] or meas1 is None):
            return 1
        elif meas1 and (meas0 is None or meas0[0] < meas1[0]):
            return -1
        else:
            return 0
        
    def dumpRank(self, fname, rankDict):
        writer = csv.writer(open(fname, 'wb'))
        i = 0
        for key, value in rankDict.items():
            i = i+1
            writer.writerow([i, key, value[0]])
        