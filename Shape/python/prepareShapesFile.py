#!/usr/bin/env python
import os, sys
from ROOT import *

main_data_dir  = '{0}/src/H2MuCombination/data'.format(os.environ['CMSSW_BASE'])
shape_data_dir = '{0}/src/H2MuCombination/Shape/data'.format(os.environ['CMSSW_BASE'])
input_file_head = 'ana_2Mu_'
input_file_tail = '.root'
degree = 4
blind_low, blind_high = 120., 130.
range_low, range_high = 105., 200.
sig_fit_low, sig_fit_high = 115., 135.

lumi = 36460.

cats = ['cat'+str(i).zfill(2) for i in xrange(16)]

gROOT.SetBatch(kTRUE)
RooMsgService.instance().setGlobalKillBelow(5)

sig_processes = ['VBF', 'GluGlu', 'WMinusH', 'WPlusH', 'ZH']





## ____________________________________________________________________________
def build_mass_var(ws):
    # create dimuon mass observable
    ws.factory('x[125.0, {0}, {1}]'.format(range_low, range_high))
    ws.var('x').setRange('signal_region', blind_low,blind_high)
    ws.var('x').setRange('signal_fit', sig_fit_low,sig_fit_high)
    ws.var('x').setRange('blinded_low', range_low,blind_low)
    ws.var('x').setRange('blinded_high', blind_high,range_high)
    ws.var('x').setRange('full_range', range_low,range_high)
    ws.var('x').SetTitle('M_{#mu#mu}')
    ws.var('x').setUnit('GeV')
    # define the set obs=(x) and make it known to python
    ws.defineSet('obs', 'x')


## ____________________________________________________________________________
def build_triple_gaus(ws, cat_, proc):
    cat = cat_ + '_' + proc
    # RooRealVars
    ws.factory('mean1_sig_model_'+cat+'[125., 121., 129.]')
    ws.factory('sigma1_sig_model_'+cat+'[2., 1., 20.]')
    ws.var('mean1_sig_model_'+cat).setUnit('GeV')
    ws.var('sigma1_sig_model_'+cat).setUnit('GeV')
    ws.factory('mean2_sig_model_'+cat+'[125., 121., 129.]')
    ws.factory('sigma2_sig_model_'+cat+'[2., 1., 20.]')
    ws.var('mean2_sig_model_'+cat).setUnit('GeV')
    ws.var('sigma2_sig_model_'+cat).setUnit('GeV')
    ws.factory('mean3_sig_model_'+cat+'[125., 121., 129.]')
    ws.factory('sigma3_sig_model_'+cat+'[2., 1., 20.]')
    ws.var('mean3_sig_model_'+cat).setUnit('GeV')
    ws.var('sigma3_sig_model_'+cat).setUnit('GeV')
    ws.factory('coef1_sig_model_'+cat+'[0.5, 0., 1.]')
    ws.factory('coef2_sig_model_'+cat+'[0.5, 0., 1.]')
    # RooAbsPdfs
    #ws.var('mean1_sig_model').setConstant()
    #ws.var('mean2_sig_model').setConstant()
    #ws.var('mean3_sig_model').setConstant()
    g1 = ws.factory(('Gaussian::g1_sig_model_{cat}(x, mean1_sig_model_{cat},'
                     'sigma1_sig_model_{cat})').format(cat=cat))
    g2 = ws.factory(('Gaussian::g2_sig_model_{cat}(x, mean2_sig_model_{cat},'
                     'sigma2_sig_model_{cat})').format(cat=cat))
    g3 = ws.factory(('Gaussian::g3_sig_model_{cat}(x, mean3_sig_model_{cat},'
                     'sigma3_sig_model_{cat})').format(cat=cat))
    gaussians = RooArgList(g1, g2, g3)
    betas = RooArgList(ws.var('coef1_sig_model_'+cat),
        ws.var('coef2_sig_model_'+cat))

    sig_model = RooAddPdf('sig_model_'+cat, 'sig_model_'+cat,
        gaussians, betas, kTRUE)
    getattr(ws, 'import')(sig_model, RooFit.RecycleConflictNodes())
    return sig_model

    
## ____________________________________________________________________________
def build_sum_exp(ws, cat, order=4):
    # RooRealVars
    lambdas = RooArgList()
    betas   = RooArgList()
    for i in xrange(1, order+1):
        ws.factory('alpha{0}_bkg_model_{cat}[{1}, -1., 0.]'.format(
            i, max(-1., -0.04*(i+1)), cat=cat))
        if i < order:
            ws.factory('beta{0}_bkg_model_{cat}[{1}, 0.0001, .9999]'.format(
                i, 0.9-float(i-1)*1./order, cat=cat))
            betas.add(ws.var('beta{0}_bkg_model_{cat}'.format(i, cat=cat)))
    # RooAbsPdfs
    for i in xrange(1, order+1):
        ws.factory(('Exponential::lambda{0}_bkg_model_{cat}(x,'
            ' alpha{0}_bkg_model_{cat})').format(i, cat=cat))
        lambdas.add(ws.pdf('lambda{0}_bkg_model_{cat}'.format(i, cat=cat)))
    
    bkg_model = RooAddPdf('bkg_model_'+cat, 'bkg_model_'+cat,
        lambdas, betas, kTRUE)
    getattr(ws, 'import')(bkg_model, RooFit.RecycleConflictNodes())
    return bkg_model


## ____________________________________________________________________________
def build_data_dist(ws, cat, tfile):
    hname = 'categories/hDiMuInvMass_'+cat
    h = TH1F()
    try:
        h = tfile.Get(hname)
    except:
        print 'Error getting '+hname
        return
    # create binned dataset from histograms and add to workspace
    dataset = RooDataHist('data_obs_'+cat, 'data_obs_'+cat, RooArgList(ws.var('x')), h)
    # how to use the import method in PyROOT
    getattr(ws,'import')(dataset, RooCmdArg(), RooFit.RecycleConflictNodes())
    return dataset




## ____________________________________________________________________________
def get_mc_info(tfile):
    try:
        # get xsec and sumw/nevents
        tsummary = tfile.Get('Summary')
        tsummary.GetEntry(0)
        xsec = tsummary.tCrossSec
        sumw = 0.
        nevt = 0
        for entry in range(tsummary.GetEntries()):
            tsummary.GetEntry(entry)
            sumw += tsummary.tSumWts
            nevt += tsummary.tNumEvts
    except:
        print 'Could not get summary info from {0}'.format(tfile)
        xsec = -1.
        sumw = -1.
        nevt = -1
    if nevt and not sumw: sumw = nevt
    return xsec, sumw



## ____________________________________________________________________________
def build_mc_dist(tfile, ws, cat, proc):
    hname = 'categories/hDiMuInvMass_'+cat
    xsec, sumw = get_mc_info(tfile)
    try:
        h = tfile.Get(hname)
    except:
        print 'ERROR: could not get {0} from {1}.'.format(hname, tfile)
        return False
    h.Scale((lumi*xsec)/sumw)
    # create binned dataset from histograms and add to workspace
    mcset = RooDataHist('sig_hist_'+cat+'_'+proc, 'sig_hist_'+cat+'_'+proc,
        RooArgList(ws.var('x')), h)
    # how to use the import method in PyROOT
    getattr(ws,'import')(mcset, RooCmdArg(), RooFit.RecycleConflictNodes())
    return mcset


## ____________________________________________________________________________
def save_plot_of(ws, cat, proc, pdf, dist):
    sig_color = kBlack
    if proc=='VBF': sig_color = kGreen
    elif proc=='GluGlu': sig_color = kBlue
    elif proc=='WMinusH': sig_color = kRed
    elif proc=='WPlusH': sig_color = kViolet
    elif proc=='ZH': sig_color = kMagenta
    canv = TCanvas(cat, cat, 1200, 900)
    canv.cd()
    thisframe = ws.var('x').frame()
    dist.plotOn(thisframe, RooFit.DrawOption('hist'))
    pdf.plotOn(thisframe, RooFit.LineColor(sig_color),
        RooFit.Name('tripleGaus_'+cat+'_'+proc),
        RooFit.Range('signal_fit'))
    pdf.paramOn(thisframe, RooFit.Layout(0.55, 0.95, 0.74))
    thisframe.getAttText().SetTextSize(0.02)
    leg = TLegend(0.65, 0.75, 0.9, 0.9)
    leg.AddEntry(thisframe.findObject('tripleGaus_'+cat+'_'+proc),
        'tripleGaus_'+cat+'_'+proc, 'l')
    leg.AddEntry(thisframe.findObject('sig_hist_'+cat+'_'+proc),
        'sig_hist_'+cat+'_'+proc, 'P')
    thisframe.SetTitle('{0} sig. only fit, M_{{#mu#mu}} ({1}, {2}/pb)'.format(proc, cat, lumi))
    thisframe.Draw()
    leg.Draw()
    gPad.Modified()
    canv.Print('sig_fit_'+cat+'_'+proc+'.png')




## ____________________________________________________________________________
def main():
    
    # create roo workspace
    w = RooWorkspace('mumu')
    build_mass_var(w)
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
    # get histograms
    for cat in cats:
        # get data RooDataHist
        data_obs = build_data_dist(w, cat, f0)
        # create background model
        bkg_model = build_sum_exp(w, cat)
        # create signal models
        sig_model_vbf = build_triple_gaus(w, cat, 'VBF')
        sig_model_ggf = build_triple_gaus(w, cat, 'GluGlu')
        sig_model_wm  = build_triple_gaus(w, cat, 'WMinusH')
        sig_model_wp  = build_triple_gaus(w, cat, 'WPlusH')
        sig_model_zh  = build_triple_gaus(w, cat, 'ZH')
        # get signal MC RooDataHists
        sig_dist_vbf = build_mc_dist(f1, w, cat, 'VBF')
        sig_dist_ggf = build_mc_dist(f2, w, cat, 'GluGlu')
        sig_dist_wm  = build_mc_dist(f3, w, cat, 'WMinusH')
        sig_dist_wp  = build_mc_dist(f4, w, cat, 'WPlusH')
        sig_dist_zh  = build_mc_dist(f5, w, cat, 'ZH')
        # fit signal models to signal MC dists
        fit_result_vbf = sig_model_vbf.fitTo(sig_dist_vbf,
            RooFit.Save(), RooFit.Range('signal_fit'),
            RooFit.SumW2Error(kTRUE))
        fit_result_ggf = sig_model_ggf.fitTo(sig_dist_ggf,
            RooFit.Save(), RooFit.Range('signal_fit'),
            RooFit.SumW2Error(kTRUE))
        fit_result_wm = sig_model_wm.fitTo(sig_dist_wm,
            RooFit.Save(), RooFit.Range('signal_fit'),
            RooFit.SumW2Error(kTRUE))
        fit_result_wp = sig_model_wp.fitTo(sig_dist_wp,
            RooFit.Save(), RooFit.Range('signal_fit'),
            RooFit.SumW2Error(kTRUE))
        fit_result_zh = sig_model_zh.fitTo(sig_dist_zh,
            RooFit.Save(), RooFit.Range('signal_fit'),
            RooFit.SumW2Error(kTRUE))
        # fix parameters of signal fits




        # plot and print results for later viewing pleasure
        save_plot_of(w, cat, 'VBF', sig_model_vbf, sig_dist_vbf)
        save_plot_of(w, cat, 'GluGlu', sig_model_ggf, sig_dist_ggf)
        save_plot_of(w, cat, 'WMinusH', sig_model_wm, sig_dist_wm)
        save_plot_of(w, cat, 'WPlusH', sig_model_wp, sig_dist_wp)
        save_plot_of(w, cat, 'ZH', sig_model_zh, sig_dist_zh)



    # create output file
    output_file = 'workspace_allcats_tripleGaus.root'
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

