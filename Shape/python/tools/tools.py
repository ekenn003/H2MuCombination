#!/usr/bin/env python
import os, sys
from ROOT import *
#from initial_values import iv as initial_values

## ____________________________________________________________________________
def build_mass_var(ws, r):
    # create dimuon mass observable
    ws.factory('x[125.0, {0}, {1}]'.format(r['range_low'], r['range_high']))
    ws.var('x').setRange('signal_region', r['blind_low'],r['blind_high'])
    ws.var('x').setRange('signal_fit', r['sig_fit_low'],r['sig_fit_high'])
    ws.var('x').setRange('blinded_low', r['range_low'],r['blind_low'])
    ws.var('x').setRange('blinded_high', r['blind_high'],r['range_high'])
    ws.var('x').setRange('full_range', r['range_low'],r['range_high'])
    ws.var('x').SetTitle('M_{#mu#mu}')
    ws.var('x').setUnit('GeV')
    # define the set obs=(x) and make it known to python
    ws.defineSet('obs', 'x')


## ____________________________________________________________________________
def get_initial_vals_from_TH1(th1, cat, proc):
    sigma_max = 10.
    mean_min = 121.
    mean_max = 129.
    f1, f2, c1 = 1., 1., 1.

    if cat=='cat15' and proc=='WMinusH':
        f1 *= 1.1
        
    if cat=='cat14' and proc=='VBF':
        f2 *= 1.1
        c1 *= 1.1

    # these values work for double gaus
    # DUPLICATE BEFORE DOING TRIPLE
    initial_values = {
        # single Gaus
        'mean1' : th1.GetMean(),
        'mean1min' : max(mean_min, th1.GetMean() - 0.2*th1.GetRMS()),
        'mean1max' : min(mean_max, th1.GetMean() + 0.2*th1.GetRMS()),
        'sigma1' : f1*0.45*th1.GetRMS(),
        'sigma1min' : f1*0.2*th1.GetRMS(),
        'sigma1max' : f1*1.2*th1.GetRMS(),
        # double Gaus
        'mean2' : th1.GetMean(), 
        'mean2min' : max(mean_min, th1.GetMean() - 0.4*th1.GetRMS()),
        'mean2max' : min(mean_max, th1.GetMean() + 0.4*th1.GetRMS()),
        'sigma2' : f2*0.6*th1.GetRMS(), 
        'sigma2min' : f1*0.7*th1.GetRMS(),
        'sigma2max' : f2*1.2*th1.GetRMS(),
        'coef1' : c1*0.45, 'coef1min' : 0.00, 'coef1max' : .9,
        # triple Gaus
        'mean3' : th1.GetMean(),
        'mean3min' : max(mean_min, th1.GetMean() - 2.4*th1.GetRMS()),
        'mean3max' : min(mean_max, th1.GetMean() + 0.8*th1.GetRMS()),
        'sigma3' : 2.4*th1.GetRMS(),
        'sigma3min' : 1.2*th1.GetRMS(),
        'sigma3max' : 4.8*th1.GetRMS(),
        'coef2' : 0.6, 'coef2min' : 0.0, 'coef2max' : 1,
    }

    #for key, val in initial_values.iteritems():
    #    print key, ':', val

    return initial_values




## ____________________________________________________________________________
def build_single_gaus(ws, cat_, proc, iv):
    cat = cat_ + '_' + proc
    # RooRealVars
    ws.factory(('mean1_sig_model_'+cat
        +'[{mean1}, {mean1min}, {mean1max}]').format(**iv))
    ws.factory(('sigma1_sig_model_'+cat
        +'[{sigma1}, {sigma1min}, {sigma1max}]').format(**iv))

    # RooAbsPdfs
    g1 = ws.factory(('Gaussian::g1_sig_model_{cat}(x, mean1_sig_model_{cat},'
                     'sigma1_sig_model_{cat})').format(cat=cat))
    gaussians = RooArgList(g1)
    betas = RooArgList()

    ws.var('mean1_sig_model_'+cat).setUnit('GeV')
    ws.var('sigma1_sig_model_'+cat).setUnit('GeV')

    sig_model = RooAddPdf('sig_model_'+cat, 'sig_model_'+cat,
        gaussians, betas, kTRUE)
    getattr(ws, 'import')(sig_model, RooFit.RecycleConflictNodes())
    return sig_model


## ____________________________________________________________________________
def build_double_gaus(ws, cat_, proc, iv):
    cat = cat_ + '_' + proc
    # RooRealVars
    ws.factory(('mean1_sig_model_'+cat
        +'[{mean1}, {mean1min}, {mean1max}]').format(**iv))
    ws.factory(('sigma1_sig_model_'+cat
        +'[{sigma1}, {sigma1min}, {sigma1max}]').format(**iv))
    ws.factory(('mean2_sig_model_'+cat
        +'[{mean2}, {mean2min}, {mean2max}]').format(**iv))
    ws.factory(('sigma2_sig_model_'+cat
        +'[{sigma2}, {sigma2min}, {sigma2max}]').format(**iv))
    ws.factory(('coef1_sig_model_'+cat
        +'[{coef1}, {coef1min}, {coef1max}]').format(**iv))

    # RooAbsPdfs
    g1 = ws.factory(('Gaussian::g1_sig_model_{cat}(x, mean1_sig_model_{cat},'
                     'sigma1_sig_model_{cat})').format(cat=cat))
    g2 = ws.factory(('Gaussian::g2_sig_model_{cat}(x, mean2_sig_model_{cat},'
                     'sigma2_sig_model_{cat})').format(cat=cat))
    gaussians = RooArgList(g1, g2)
    betas = RooArgList(ws.var('coef1_sig_model_'+cat))

    ws.var('mean1_sig_model_'+cat).setUnit('GeV')
    ws.var('sigma1_sig_model_'+cat).setUnit('GeV')
    ws.var('mean2_sig_model_'+cat).setUnit('GeV')
    ws.var('sigma2_sig_model_'+cat).setUnit('GeV')

    sig_model = RooAddPdf('sig_model_'+cat, 'sig_model_'+cat,
        gaussians, betas, kTRUE)
    getattr(ws, 'import')(sig_model, RooFit.RecycleConflictNodes())
    return sig_model

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
    dataset = RooDataHist('data_obs_'+cat, 'data_obs_'+cat,
        RooArgList(ws.var('x')), h)
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
def get_mc_hist(tfile, cat, lumi, proc):
    hname = 'categories/hDiMuInvMass_'+cat
    xsec, sumw = get_mc_info(tfile)
    try:
        h = TH1F(tfile.Get(hname))
    except:
        print 'ERROR: could not get {0} from {1}.'.format(hname, tfile)
        return False
 #   h.Scale((lumi*xsec)/sumw)
    h.SetName('sig_hist_'+cat+'_'+proc)
    return h


## ____________________________________________________________________________
def build_mc_dist(h, ws):
    hname = h.GetName()
    # create binned dataset from histograms and add to workspace
    mcset = RooDataHist(hname, hname, RooArgList(ws.var('x')), h)
    # how to use the import method in PyROOT
    getattr(ws,'import')(mcset, RooCmdArg(), RooFit.RecycleConflictNodes())
    return mcset


## ____________________________________________________________________________
def save_plot_of(ws, cat, lumi, signal_model, proc, pdf, dist):
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
        RooFit.Name(signal_model+'Gaus_'+cat+'_'+proc),
        RooFit.Range('signal_fit'))
    pdf.paramOn(thisframe, RooFit.Layout(0.55, 0.95, 0.74))
    thisframe.getAttText().SetTextSize(0.02)
    leg = TLegend(0.65, 0.75, 0.9, 0.9)
    leg.AddEntry(thisframe.findObject(signal_model+'Gaus_'+cat+'_'+proc),
        signal_model+'Gaus_'+cat+'_'+proc, 'l')
    leg.AddEntry(thisframe.findObject('sig_hist_'+cat+'_'+proc),
        'sig_hist_'+cat+'_'+proc, 'P')
    thisframe.SetTitle(('{0} sig. only fit, M_{{#mu#mu}} ({1}, '
        '{2}/pb)').format(proc, cat, lumi))
    thisframe.Draw()
    leg.Draw()
    gPad.Modified()
    canv.Print('sig_'+signal_model+'_fit_'+cat+'_'+proc+'.png')


