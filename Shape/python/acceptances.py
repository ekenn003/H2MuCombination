#!/usr/bin/env python
import os, sys
from ROOT import *
from tools.tools import get_mc_info

main_data_dir  = '{0}/src/H2MuCombination/data'.format(os.environ['CMSSW_BASE'])
shape_data_dir = '{0}/src/H2MuCombination/Shape/data'.format(os.environ['CMSSW_BASE'])
input_file_head = 'ana_2Mu_'
input_file_tail = '.root'

# categories
cats = ['cat'+str(i).zfill(2) for i in xrange(16)]
# signal processes
sp = ['VBF', 'GluGlu', 'WMinusH', 'WPlusH', 'ZH']

## ____________________________________________________________________________
def get_signal_rate_map(lumi):
    # rate map
    rates = {}
    for p in sp:
        rates[p] = {}

    # acceptance map
    acc = {}
    for p in sp:
        acc[p] = {}

    # filenames and tfiles
    fnames = {}
    tf = {}
    for p in sp:
        fnames[p] = '{0}/{1}{2}_HToMuMu{3}'.format(main_data_dir,
            input_file_head, p, input_file_tail)
        try:
            tf[p] = TFile.Open(fnames[p])
        except:
            print 'Error opening input files'
            return

    # sum weights / xsec for each sample
    nsw = {
        'VBF'     : 249200,
        'GluGlu'  : 250000,
        'WMinusH' : 125000,
        'WPlusH'  : 124547,
        'ZH'      : 249748,
    }
    xsc = {}
    #nsw = {}
    for p in sp:
        xsc[p] = float(get_mc_info(tf[p])[0])
        #nsw[p] = float(get_mc_info(tf[p])[1])

    # get rates for each category
    for cat in cats:
        for p in sp:
            h = TH1F(tf[p].Get('categories/hDiMuInvMass_'+cat))
            num = h.Integral()
            den = nsw[p]
            acc[p][cat] = num/den
            rates[p][cat] = (num/den) * lumi * (xsc[p])
            #print
            #print p, cat, 'acceptance =', acc[p][cat]
            #print p, cat, 'rate       =', rates[p][cat]
  
    return rates




#
## __________________________________________________________
#try:
#    get_signal_rate_map(36000)
#except KeyboardInterrupt:
#    print

