#!/usr/bin/env python
import os, sys
from ROOT import *

main_data_dir  = '{0}/src/H2MuCombination/data'.format(os.environ['CMSSW_BASE'])
shape_data_dir = '{0}/src/H2MuCombination/Shape/data'.format(os.environ['CMSSW_BASE'])
input_file_head = 'ana_2Mu_'
input_file_tail = '.root'

hname = 'categories/hDiMuInvMass_'

sp = ['VBF', 'GluGlu', 'WMinusH', 'WPlusH', 'ZH']

cats = ['cat'+str(i).zfill(2) for i in xrange(1,16)]

sys = [
    'pu',
#    'hlt',
#    'id',
#    'iso',
#    'jec',
]

sign = ['Down', 'Up']

file_grid = [(s,p,d) for s in sys for p in sp for d in sign]
cats_grid = [(s,p,d,c) for s in sys for p in sp for d in sign for c in cats]


gROOT.SetBatch(kTRUE)

## ____________________________________________________________________________
def main():
    fns = {}
    tfs = {}
    hs = {}

    #for s,p,d in file_grid:

    #print fns

    for s in sys:
        fns[s] = {}
        tfs[s] = {}
        hs[s] = {}
        for p in sp:
            fns[s][p] = {}
            tfs[s][p] = {}
            hs[s][p] = {}
            for d in sign:
                 fns[s][p][d] = ('{0}/systematics/{sys}_{sign}/{head}_'
                     '_HToMuMu{tail}').format(main_data_dir, sys=s,
                         sign=d, head=input_file_head, 
                         tail=input_file_tail)
                 try:
                     print 'Opening tfs[{s}][{p}][{d}] = {0}'.format(fns[s][p][d], s=s,p=p,d=d)
                     tfs[s][p][d] = TFile.Open(fns[s][p][d])
                 except:
                     print 'Error opening input file ' + fns[s][p][d]
                     return


    #for cat in cats:



    for s,p,d in file_grid:
        try:
            print 'Closing tfs['+s+']['+p+']['+d+']'
            tfs[s][p][d].Close()
        except:
            pass

# __________________________________________________________
try:
    main()
except KeyboardInterrupt:
    print

