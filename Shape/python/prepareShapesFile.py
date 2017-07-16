#!/usr/bin/env python
import os, sys
from ROOT import *
from tools.tools import *

main_data_dir  = '{0}/src/H2MuCombination/data'.format(os.environ['CMSSW_BASE'])
shape_data_dir = '{0}/src/H2MuCombination/Shape/data'.format(os.environ['CMSSW_BASE'])
input_file_head = 'ana_2Mu_'
input_file_tail = '.root'

background_model = 'bwzGamma'
degree = 1

ranges = {
    'blind_low'  : 120.,
    'blind_high' : 130.,
    'range_low'  : 100.,
    'range_high' : 150.,
    'sig_fit_low'  : 115.,
    'sig_fit_high' : 135.,
}

sp = ['VBF', 'GluGlu', 'WMinusH', 'WPlusH', 'ZH']

signal_model = 'double'

lumi = 35860.

cats = ['cat'+str(i).zfill(2) for i in xrange(1,16)]
#cats = ['cat'+str(i).zfill(2) for i in xrange(1)]

gROOT.SetBatch(kTRUE)
RooMsgService.instance().setGlobalKillBelow(5)

sig_integrals = {}

## ____________________________________________________________________________
def main():
    
    # create roo workspace
    w = RooWorkspace('mumu')
    build_mass_var(w, ranges)
    obs = w.set('obs')
    rooarg = RooArgSet(w.var('x'))
    # map of filenames
    fnames = {
        'data' : '{0}/{1}{2}{3}'.format(main_data_dir,
                     input_file_head, 'SingleMuon_Run2016', input_file_tail)
    }
    for p in sp:
        fnames[p] = '{0}/{1}{2}_HToMuMu{3}'.format(main_data_dir,
                    input_file_head, p, input_file_tail)
    # map of tfiles
    tf = {}
    try:
        tf['data'] = TFile.Open(fnames['data'])
    except:
        print 'Error opening input file ' + fnames['data']
        return
    for p in sp:
        try:
            tf[p] = TFile.Open(fnames[p])
        except:
            print 'Error opening input file ' + fnames[p]
            return


    for cat in cats:



        ##if cat != 'cat15': continue





        # get data RooDataHist
        data_obs = build_data_dist(w, cat, tf['data'])
        # create background model
        bkg_model = None
        if background_model=='sumExp':
            bkg_model = build_sum_exp(w, cat, degree)
        elif background_model=='bwzGamma':
            bkg_model = build_bwz_gamma(w, cat)
        # create bkg norm
        data_sume = data_obs.sumEntries()
        bkg_model_norm = RooRealVar('bkg_model_'+cat+'_norm',
            'bkg_model_'+cat+'_norm', data_sume/2., data_sume*2., 'Events')
        getattr(w, 'import')(bkg_model_norm, RooFit.RecycleConflictNodes())

        s_hists = {}
        s_dists = {}
        s_ivs = {}
        s_models = {}
        s_fits = {}
        for p in sp:
            # get signal histograms
            s_hists[p] = get_mc_hist(tf[p], cat, lumi, p)

            # get initial guesses for fit from histogram
            s_ivs[p] = get_initial_vals_from_TH1(s_hists[p], cat, p)

            print s_ivs[p]

            # create signal models
            if signal_model=='triple':
                s_models[p] = build_triple_gaus(w, cat, p, s_ivs[p])
            elif signal_model=='double':
                s_models[p] = build_double_gaus(w, cat, p, s_ivs[p])
            elif signal_model=='single':
                s_models[p] = build_single_gaus(w, cat, p, s_ivs[p])

            # get signal MC RooDataHists
            s_dists[p] = build_mc_dist(s_hists[p], w)

            # signal fit results
            s_fits[p] = s_models[p].fitTo(s_dists[p],
                RooFit.Save(), RooFit.Range('signal_fit'),
                RooFit.NormRange('signal_fit'),
                #RooFit.PrintLevel(-1),
                RooFit.SumW2Error(kTRUE))


            # plot and print results for later viewing pleasure
            save_plot_of(w, cat, lumi, signal_model, p, s_models[p], s_dists[p])

            # fix parameters of signal fits
            s_models[p].getParameters(RooArgSet(w.var('x'))
                ).setAttribAll('Constant', kTRUE)

            # save integral just in case
            #thisint = s_models[p].createIntegral(rooarg,rooarg,'full_range')
            thisint = s_models[p].createIntegral(rooarg,rooarg,'signal_fit')
            sig_integrals[cat] = thisint.getVal()


    # create output file
    output_file = 'workspace_allcats_{0}Gaus.root'.format(signal_model)
    f_out = TFile('{0}/{1}'.format(shape_data_dir, output_file), 'RECREATE')
    f_out.cd()
    # save workspace in output file
    w.Print('v')
    w.Write()
    f_out.Write()
    f_out.Close()
    print 'Created ' + '{0}/{1}'.format(shape_data_dir, output_file)

    #for key, val in sig_integrals.iteritems():
    #    print key, val

    # close inputs
    for p, f in tf.iteritems():
        tf[p].Close()




# __________________________________________________________
try:
    main()
except KeyboardInterrupt:
    print

