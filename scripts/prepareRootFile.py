#!/usr/bin/env python
import os, sys
from collections import namedtuple
from ROOT import TFile, TH1F, TTree, TList, gDirectory
from math import ceil

# input files
indir = '/afs/cern.ch/work/e/ekennedy/work/fsanalysis/ana76/root6/CMSSW_7_6_5/src/AnalysisToolLight/2Mu'
#indir = '.'


Dataset = namedtuple('Dataset', ['name', 'tfile'])

datasets = [
    Dataset('sigVBF', TFile.Open('{0}/2mu_DYJetsToLL.root'.format(indir))),
    Dataset('sigGGF', TFile.Open('{0}/2mu_DYJetsToLL.root'.format(indir))),

    Dataset('bkgDYJ', TFile.Open('{0}/2mu_DYJetsToLL.root'.format(indir))),
    Dataset('bkgTTJ', TFile.Open('{0}/2mu_DYJetsToLL.root'.format(indir))),

    Dataset('data15', TFile.Open('{0}/2mu_DYJetsToLL.root'.format(indir))),
    Dataset('data16', TFile.Open('{0}/2mu_DYJetsToLL.root'.format(indir))),
]


# output file options
# this will be saved in H2MuCombination/data/
output_file = 'p_test.root'

#############################
# Shape (binned) options
#############################
# binning
bin_width = 2. # GeV
x_low  = 60.  # GeV
x_high = 200. # GeV


#############################
# Template (unbinned) options
#############################






# __________________________________________________________
def main():

    # print datasets
    for dset in datasets:
        print dset.name
    print

    # determine number of categories/bins (have to start with string 'Category')
    # and make sure there are the same number of categories present in each file
    f0 = datasets[0].tfile
    category_list = []
    category_list += [key.GetName() for key in f0.GetListOfKeys() if key.GetName().startswith('Category')]
    for dset in datasets:
        n = 0
        f = dset.tfile
        for key in f.GetListOfKeys():
            if key.GetName().startswith('Category'): n += 1
        assert (n == len(category_list)), 'Different number of categories across files!'

    print '{0} categories found:'.format(len(category_list))
    for cat in category_list:
        print cat
    print


    # open output file
    #f1 = TFile('{0}/src/H2MuCombination/data/{1}'.format(os.environ['CMSSW_BASE'], output_file), 'RECREATE')
    f1 = TFile('./{0}'.format(output_file), 'RECREATE')



    #############################
    # TEMPLATE                  #
    #############################

    h_to_write = []

    # MC ########################
    n_bins = int(ceil((x_high - x_low)/bin_width))

    for cat in category_list:

        this_cat_data_list = TList()

        for dset in datasets:
            f = dset.tfile
            # create unique histogram name
            hname = '{0}_{1}'.format(dset.name, cat)
            # get tree
            tree = f.Get(cat)
            # create histogram
            draw_string = 'tInvMass>>{0}({1},{2},{3})'.format(hname, n_bins, x_low, x_high)
            cut_string  = 'tEventWt'
            tree.Draw(draw_string, cut_string, 'goff')

            h_ = TH1F( gDirectory.Get(hname) )

            if (('sig' in dset.name) or ('bkg' in dset.name)):
                print 'adding {0} to h_to_write'.format(hname)
                h_to_write += [h_]
            elif 'data' in dset.name:
                print 'adding {0} to data_hists'.format(hname)
                #this_cat_data_list.Add(h_.Clone(hname))
                this_cat_data_list.Add(h_)


        d_ = (TH1F(this_cat_data_list.First())).Clone('data_obs_{0}'.format(cat))
        d_.Reset()
        d_.Merge(this_cat_data_list)
        h_to_write += [d_.Clone('data_obs_{0}'.format(cat))]

        this_cat_data_list.Delete()



    # write all the histograms
    f1.cd()
    for h in h_to_write:
        print 'writing {0} = {1}'.format(h.GetName(), type(h))
        h.Write()



    #############################
    # SHAPE                     #
    #############################


#    # get histograms made with AnalysisToolLight
#    f0 = TFile('{0}/{1}'.format(main_data_dir, input_file))
#    #h = f0.Get('data_obs')
#    h = f0.Get('Mass')
#
#    nbins = h.GetNbinsX()
#    xmin  = h.GetBinLowEdge(1)
#    xmax  = xmin + (nbins * h.GetBinWidth(1))






















    f1.Close()
    for dset in datasets:
        dset.tfile.Close()




















# __________________________________________________________
try:
    main()
except KeyboardInterrupt:
    print

