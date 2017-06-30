#!/usr/bin/env python
import os, sys
from ROOT import *
from tools.tools import *
#from tools.initial_values import *

main_data_dir  = '{0}/src/H2MuCombination/data'.format(os.environ['CMSSW_BASE'])
shape_data_dir = '{0}/src/H2MuCombination/Shape/data'.format(os.environ['CMSSW_BASE'])
input_file_head = 'ana_2Mu_'
input_file_tail = '.root'
degree = 4

ranges = {
    'blind_low'  : 120.,
    'blind_high' : 130.,
    'range_low'  : 105.,
    'range_high' : 200.,
    'sig_fit_low'  : 115.,
    'sig_fit_high' : 135.,
}

sp = ['VBF', 'GluGlu', 'WMinusH', 'WPlusH', 'ZH']

#signal_model = 'single'
signal_model = 'double'
#signal_model = 'triple'

lumi = 36460.

cats = ['cat'+str(i).zfill(2) for i in xrange(16)]

gROOT.SetBatch(kTRUE)
RooMsgService.instance().setGlobalKillBelow(5)


## ____________________________________________________________________________
def main():
    
    # create roo workspace
    w = RooWorkspace('mumu')
    build_mass_var(w, ranges)
    obs = w.set('obs')
    # get data_obs for each bin
    fname_data = '{0}/{1}SingleMuon_Run2016{2}'.format(
        main_data_dir, input_file_head, input_file_tail)
    fname_vbf  = '{0}/{1}VBF_HToMuMu{2}'.format(
        main_data_dir, input_file_head, input_file_tail)
    fname_ggf  = '{0}/{1}GluGlu_HToMuMu{2}'.format(
        main_data_dir, input_file_head, input_file_tail)
    fname_wm   = '{0}/{1}WMinusH_HToMuMu{2}'.format(
        main_data_dir, input_file_head, input_file_tail)
    fname_wp   = '{0}/{1}WPlusH_HToMuMu{2}'.format(
        main_data_dir, input_file_head, input_file_tail)
    fname_zh   = '{0}/{1}ZH_HToMuMu{2}'.format(
        main_data_dir, input_file_head, input_file_tail)
    try:
        f0 = TFile.Open(fname_data)
        f1 = TFile.Open(fname_vbf)
        f2 = TFile.Open(fname_ggf)
        f3 = TFile.Open(fname_wm)
        f4 = TFile.Open(fname_wp)
        f5 = TFile.Open(fname_zh)
    except:
        print 'Error opening input files'
        return
    for cat in cats:
        #if cat != 'cat00': continue
        # get data RooDataHist
        data_obs = build_data_dist(w, cat, f0)
        # create background model
        bkg_model = build_sum_exp(w, cat)
        # create bkg norm
        data_sume = data_obs.sumEntries()
        bkg_model_norm = RooRealVar('bkg_model_'+cat+'_norm',
            'bkg_model_'+cat+'_norm', data_sume/2., data_sume*2., 'Events')
        getattr(w, 'import')(bkg_model_norm, RooFit.RecycleConflictNodes())
        # get signal histograms
        sig_h_vbf = get_mc_hist(f1, cat, lumi, 'VBF')
        sig_h_ggf = get_mc_hist(f2, cat, lumi, 'GluGlu')
        sig_h_wm  = get_mc_hist(f3, cat, lumi, 'WMinusH')
        sig_h_wp  = get_mc_hist(f4, cat, lumi, 'WPlusH')
        sig_h_zh  = get_mc_hist(f5, cat, lumi, 'ZH')

        iv_vbf = get_initial_vals_from_TH1(sig_h_vbf, cat, 'VBF')
        iv_ggf = get_initial_vals_from_TH1(sig_h_ggf, cat, 'GluGlu')
        iv_wm  = get_initial_vals_from_TH1(sig_h_wm, cat, 'WMinusH')
        iv_wp  = get_initial_vals_from_TH1(sig_h_wp, cat, 'WPlusH')
        iv_zh  = get_initial_vals_from_TH1(sig_h_zh, cat, 'ZH')

        # create signal models
        if signal_model=='triple':
            sig_model_vbf = build_triple_gaus(w, cat, 'VBF', iv_vbf)
            sig_model_ggf = build_triple_gaus(w, cat, 'GluGlu', iv_ggf)
            sig_model_wm  = build_triple_gaus(w, cat, 'WMinusH', iv_wm)
            sig_model_wp  = build_triple_gaus(w, cat, 'WPlusH', iv_wp)
            sig_model_zh  = build_triple_gaus(w, cat, 'ZH', iv_zh)
        elif signal_model=='double':
            sig_model_vbf = build_double_gaus(w, cat, 'VBF', iv_vbf)
            sig_model_ggf = build_double_gaus(w, cat, 'GluGlu', iv_ggf)
            sig_model_wm  = build_double_gaus(w, cat, 'WMinusH', iv_wm)
            sig_model_wp  = build_double_gaus(w, cat, 'WPlusH', iv_wp)
            sig_model_zh  = build_double_gaus(w, cat, 'ZH', iv_zh)
        elif signal_model=='single':
            sig_model_vbf = build_single_gaus(w, cat, 'VBF', iv_vbf)
            sig_model_ggf = build_single_gaus(w, cat, 'GluGlu', iv_ggf)
            sig_model_wm  = build_single_gaus(w, cat, 'WMinusH', iv_wm)
            sig_model_wp  = build_single_gaus(w, cat, 'WPlusH', iv_wp)
            sig_model_zh  = build_single_gaus(w, cat, 'ZH', iv_zh)

        # get signal MC RooDataHists
        sig_dist_vbf = build_mc_dist(sig_h_vbf, w)
        sig_dist_ggf = build_mc_dist(sig_h_ggf, w)
        sig_dist_wm  = build_mc_dist(sig_h_wm, w)
        sig_dist_wp  = build_mc_dist(sig_h_wp, w)
        sig_dist_zh  = build_mc_dist(sig_h_zh, w)


        # fit signal models to signal MC dists
        fit_result_vbf = sig_model_vbf.fitTo(sig_dist_vbf,
            RooFit.Save(), RooFit.Range('signal_fit'),
            RooFit.NormRange('signal_fit'),
            RooFit.SumW2Error(kTRUE))
        fit_result_ggf = sig_model_ggf.fitTo(sig_dist_ggf,
            RooFit.Save(), RooFit.Range('signal_fit'),
            RooFit.NormRange('signal_fit'),
            RooFit.SumW2Error(kTRUE))
        fit_result_wm = sig_model_wm.fitTo(sig_dist_wm,
            RooFit.Save(), RooFit.Range('signal_fit'),
            RooFit.NormRange('signal_fit'),
            RooFit.SumW2Error(kTRUE))
        fit_result_wp = sig_model_wp.fitTo(sig_dist_wp,
            RooFit.Save(), RooFit.Range('signal_fit'),
            RooFit.NormRange('signal_fit'),
            RooFit.SumW2Error(kTRUE))
        fit_result_zh = sig_model_zh.fitTo(sig_dist_zh,
            RooFit.Save(), RooFit.Range('signal_fit'),
            RooFit.NormRange('signal_fit'),
            RooFit.SumW2Error(kTRUE))
        # fix parameters of signal fits
        sig_model_vbf.getParameters(RooArgSet(w.var('x'))).setAttribAll('Constant', kTRUE)
        sig_model_ggf.getParameters(RooArgSet(w.var('x'))).setAttribAll('Constant', kTRUE)
        sig_model_wm.getParameters(RooArgSet(w.var('x'))).setAttribAll('Constant', kTRUE)
        sig_model_wp.getParameters(RooArgSet(w.var('x'))).setAttribAll('Constant', kTRUE)
        sig_model_zh.getParameters(RooArgSet(w.var('x'))).setAttribAll('Constant', kTRUE)


        # plot and print results for later viewing pleasure
        save_plot_of(w, cat, lumi, signal_model, 'VBF', sig_model_vbf, sig_dist_vbf)
        save_plot_of(w, cat, lumi, signal_model, 'GluGlu', sig_model_ggf, sig_dist_ggf)
        save_plot_of(w, cat, lumi, signal_model, 'WMinusH', sig_model_wm, sig_dist_wm)
        save_plot_of(w, cat, lumi, signal_model, 'WPlusH', sig_model_wp, sig_dist_wp)
        save_plot_of(w, cat, lumi, signal_model, 'ZH', sig_model_zh, sig_dist_zh)



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

    f0.Close()
    f1.Close()
    f2.Close()
    f3.Close()
    f4.Close()
    f5.Close()



# __________________________________________________________
try:
    main()
except KeyboardInterrupt:
    print

