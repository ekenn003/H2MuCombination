#!/usr/bin/env python
import os, sys
from collections import namedtuple
import ROOT

# input files
indir = '/afs/cern.ch/work/e/ekennedy/work/fsanalysis/ana76/root6/CMSSW_7_6_5/src/AnalysisToolLight/2Mu'

Dataset = namedtuple('Dataset', ['name', 'tfile'])

signals = [
    Dataset('sigVBF', '{0}/2mu_DYJetsToLL.root'.format(indir)),
    Dataset('sigGGF', '{0}/2mu_DYJetsToLL.root'.format(indir)),
]

backgrounds = [
    Dataset('bkgDYJ', '{0}/2mu_DYJetsToLL.root'.format(indir)),
    Dataset('bkgTTJ', '{0}/2mu_DYJetsToLL.root'.format(indir)),
]

datas = [
    Dataset('data15', '{0}/2mu_DYJetsToLL.root'.format(indir)),
    Dataset('data16', '{0}/2mu_DYJetsToLL.root'.format(indir)),
]


# output file
# this will be saved in H2MuCombination/data/
outfile = 'p_test.root'






# __________________________________________________________
def main():


    # determine number of categories/bins
    # (has to start with string 'Category')
    f0 = ROOT.TFile(datas[0].tfile)
    category_list = []
    category_list += [key.GetName() for key in f0.GetListOfKeys() if key.GetName().startswith('Category')]

    print '{0} categories found:'.format(len(category_list))
    for cat in category_list:
        print cat

    
#    # get histograms made with AnalysisToolLight
#    f0 = TFile('{0}/{1}'.format(main_data_dir, input_file))
#    #h = f0.Get('data_obs')
#    h = f0.Get('Mass')
#    
#    nbins = h.GetNbinsX()
#    xmin  = h.GetBinLowEdge(1)
#    xmax  = xmin + (nbins * h.GetBinWidth(1))
    

























# __________________________________________________________
try:
    main()
except KeyboardInterrupt:
    print
