#!/usr/bin/env python
import os, sys
from ROOT import *

main_data_dir  = '{0}/src/H2MuCombination/data'.format(os.environ['CMSSW_BASE'])
shape_data_dir = '{0}/src/H2MuCombination/Shape/data'.format(os.environ['CMSSW_BASE'])
input_file  = 'ana_2Mu_SingleMuon_Run2016.root'
degree = 4
blind_low, blind_high = 120., 130.
range_low, range_high = 105., 200.

lumi = 36460.

cats = ['cat'+str(i).zfill(2) for i in xrange(16)]

RooMsgService.instance().setGlobalKillBelow(5)

sig_processes = ['VBF', 'GluGlu', 'WMinusH', 'WPlusH', 'ZH']





## ____________________________________________________________________________
def build_mass_var(ws):
    # create dimuon mass observable
    ws.factory('x[125.0, {0}, {1}]'.format(range_low, range_high))
    ws.var('x').setRange('signal_region', blind_low,blind_high)
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
    ws.factory('sigma1_sig_model_'+cat+'[5., 1., 20.]')
    ws.var('mean1_sig_model_'+cat).setUnit('GeV')
    ws.var('sigma1_sig_model_'+cat).setUnit('GeV')
    ws.factory('mean2_sig_model_'+cat+'[125., 121., 129.]')
    ws.factory('sigma2_sig_model_'+cat+'[5., 1., 20.]')
    ws.var('mean2_sig_model_'+cat).setUnit('GeV')
    ws.var('sigma2_sig_model_'+cat).setUnit('GeV')
    ws.factory('mean3_sig_model_'+cat+'[125., 121., 129.]')
    ws.factory('sigma3_sig_model_'+cat+'[5., 1., 20.]')
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
def main():
    
    # create roo workspace
    w = RooWorkspace('mumu')
    build_mass_var(w)
    obs = w.set('obs')
    # get data_obs for each bin
    fname = '{0}/{1}'.format(main_data_dir, input_file)
    try:
        f0 = TFile.Open(fname)
    except:
        print 'Error opening '+fname
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
        sig_dist_vbf = build_(f0, w, cat, 'VBF')
        sig_dist_ggf = build_(f0, w, cat, 'GluGlu')
        sig_dist_wm  = build_(f0, w, cat, 'WMinusH')
        sig_dist_wp  = build_(f0, w, cat, 'WPlusH')
        sig_dist_zh  = build_(f0, w, cat, 'ZH')
        # fit signal models to signal MC dists
        



    # create output file
    output_file = 'workspace_allcats_tripleGaus.root'
    f1 = TFile('{0}/{1}'.format(shape_data_dir, output_file), 'RECREATE')
    f1.cd()
    # save workspace in output file
    w.Print('v')
    w.Write()
    f1.Write()
    f1.Close()
    print 'Created ' + '{0}/{1}'.format(shape_data_dir, output_file)

    f0.Close()


# __________________________________________________________
try:
    main()
except KeyboardInterrupt:
    print

