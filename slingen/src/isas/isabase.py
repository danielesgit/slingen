'''
Created on May 13, 2013

@author: danieles
'''

from src.rules.base import OptClass

class ISA(object):
    def __init__(self):
        super(ISA, self).__init__()
        self.name = "Empty_ISA"
        self.types = {}
    
    def vectorize(self, t): # t can only be fp at the moment
        return max(self.types[t].keys()) > 1

    def updateType(self, typ, oldTyp, categList):
        for c in categList:
            typ[c] += oldTyp[c]
                    
    def __repr__(self):
        return self.name
        
class NuBLAC(object):
    def __init__(self):
        super(NuBLAC, self).__init__()


class Loader(object):
    def __init__(self):
        super(Loader, self).__init__()


class Storer(object):
    def __init__(self):
        super(Storer, self).__init__()

    
class LoadReplacer(OptClass):
    def __init__(self, opts):
        super(LoadReplacer, self).__init__(opts)

    def getOpt(self):
        return self
    
    def src_dsts_map(self, src, dsts_by_line):
        '''
        Map src's vec. positions to dsts'. dsts_by_line sorted from largest #line to smallest. 
        '''
        res = []
        taken_src_pos = set()
        p_dict_src = src.getPointerDict()
        for p_src,th_src,notum_src in zip(p_dict_src['pList'],p_dict_src['mrmap'],p_dict_src['notum']):
            sidx = p_src.linIdx
            for dst in dsts_by_line:
                p_dict_dst = dst.getPointerDict()
                for p_dst,th_dst,notum_dst in zip(p_dict_dst['pList'],p_dict_dst['mrmap'],p_dict_dst['notum']):
                    didx = p_dst.linIdx
                    if sidx - didx >= 0:
                        who_inf, inf, infmrmap = 'd', didx, th_dst
                        sup, supmrmap = sidx, th_src
                    else:
                        who_inf, inf, infmrmap = 's', sidx, th_src
                        sup, supmrmap = didx, th_dst
                    lim = inf + len(infmrmap) if (sup + len(supmrmap) - inf - len(infmrmap)) >= 0 else sup + len(supmrmap)     
                    src_begin, src_end = (sup - inf, lim - inf) if who_inf == 's' else (0, lim - sup)
                    dst_begin, dst_end = (sup - inf, lim - inf) if who_inf == 'd' else (0, lim - sup)
                    src_pos_list, dst_pos_list = [], []
                    for spos, dpos in zip(th_src[src_begin:src_end],th_dst[dst_begin:dst_end]):
                        if not spos in taken_src_pos:
                            src_pos_list.append(spos)
                            dst_pos_list.append(dpos)
                            taken_src_pos.add(spos)
                    if src_pos_list:
                        res.append( (src_pos_list, dst_pos_list, dst) )
        res = sorted(res, key=lambda t: t[0])
        leftovers = [ p for p in src.mrmap if p not in taken_src_pos and not src.not_using_mask[src.mrmap.index(p)] ]
        if leftovers:
            res.append( (leftovers, None, None) )
        return res
            
            
    def replace(self, src, repList, bounds): # Note the use of bounds has not appeard after the introduction of load/storeGx
        return getattr(self, src.__class__.__name__)(src, repList, bounds)


########################################################################################################################

class ISAManager(object):
    def __init__(self, isaList):
        super(ISAManager, self).__init__()
        self.isaDict = {isa.name: isa for isa in isaList}
        isaList.reverse()
        self.isaList = isaList

    def getNuBLAC(self, prec, nu):
        for isa in self.isaList:
            if (prec, nu) in isa.types['fp']:
                if 'nublac' in isa.types['fp'][(prec, nu)]:
                    return isa.types['fp'][(prec, nu)]['nublac']
        return None
    
    def getLoader(self, prec, nu):
        for isa in self.isaList:
            if (prec, nu) in isa.types['fp']:
                if 'loader' in isa.types['fp'][(prec, nu)]:
                    return isa.types['fp'][(prec, nu)]['loader']
        return None

    def getStorer(self, prec, nu):
        for isa in self.isaList:
            if (prec, nu) in isa.types['fp']:
                if 'storer' in isa.types['fp'][(prec, nu)]:
                    return isa.types['fp'][(prec, nu)]['storer']
        return None

    def getPacker(self):
        for isa in self.isaList:
            return isa.packer
        return None

    def getLoadReplacer(self, prec, nu):
        for isa in self.isaList:
            if (prec, nu) in isa.types['fp']:
                if 'loadreplacer' in isa.types['fp'][(prec, nu)]:
                    return isa.types['fp'][(prec, nu)]['loadreplacer']
        return None
        
    def getNuTypeDict(self, t, prec):
        nuTypesDict = {}
        for isa in self.isaList:
            isaFp = isa.types[t]
            for prec_nu in isaFp.keys():
                if prec_nu[0] == prec and not prec_nu[1] in nuTypesDict:
                    nuTypesDict[prec_nu[1]] = isaFp[prec_nu]['type']
        return nuTypesDict
        
    def getStore(self, t, regnu, memnu, prec, horizontal=True, isAligned=False):
        for isa in self.isaList:
            if (prec,regnu) in isa.types[t]:
                for store in isa.types[t][(prec,regnu)]['store']:
                    if store.canStore(regnu, memnu, horizontal, isAligned):
                        return store
        return None
    
    def get_add_func_defs(self):
        res = []
        for isa in self.isaList:
            for inst in isa.add_func_defs:
                res.extend(inst.add_func_defs())
        return res
    
    def __str__(self):
        return str(self.isaList)