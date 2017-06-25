#!/usr/bin/env python
import os, sys
from ROOT import *

main_data_dir  = '{0}/src/H2MuCombination/data'.format(os.environ['CMSSW_BASE'])
shape_data_dir = '{0}/src/H2MuCombination/Shape/data'.format(os.environ['CMSSW_BASE'])
input_file  = 'simulated_mass_distribution.root'
output_file = 'p.root'
degree = 4
blind_low, blind_high = 120., 130.

# __________________________________________________________
def main():
#    # get histograms made with generate.py
#    f0 = TFile('{0}/{1}'.format(main_data_dir, input_file)).Open()
#    #h = f0.Get('data_obs')
#    h = f0.Get('Mass')
#    
#    nbins = h.GetNbinsX()
#    xmin  = h.GetBinLowEdge(1)
#    xmax  = xmin + (nbins * h.GetBinWidth(1))
    
    # create roo workspace
    w = RooWorkspace('mumu')
    
    # create dimuon mass observable
    w.factory('x[123.0, 110., 200.]')
    w.var('x').setRange('blinded_low', 110., blind_low)
    w.var('x').setRange('blinded_high', blind_high, 200.)
    w.var('x').SetTitle('M_{#mu#mu}')
    w.var('x').setUnit('GeV')
    
    # how to make RooDataHist in C++:
    #     RooDataSet dataset("data","data",x,Import(*h));
    # how to make it in pyroot:
    # define the set obs=(x) and make it known to python
    w.defineSet('obs', 'x')
    obs = w.set('obs')
    # create binned dataset from histograms and add to workspace
#    dataset = RooDataHist('data_obs', 'data_obs', RooArgList(obs), h)
    # how to use the import method in PyROOT
#    getattr(w,'import')(dataset, RooCmdArg())
    
    # create background model
    # RooRealVars
    lambdas = RooArgList()
    betas   = RooArgList()
    for i in xrange(1, degree+1):
        w.factory('alpha{0}_bkg_model[{1}, -1., 0.]'.format(
            i, max(-1., -0.04*(i+1))))
        if i < degree:
            w.factory('beta{0}_bkg_model[{1}, 0.0001, .9999]'.format(
                i, 0.9-float(i-1)*1./degree))
            betas.add(w.var('beta{0}_bkg_model'.format(i)))
    # RooAbsPdfs
    for i in xrange(1, degree+1):
        w.factory('Exponential::lambda{0}_bkg_model(x, alpha{0}_bkg_model)'.format(i))
        lambdas.add(w.pdf('lambda{0}_bkg_model'.format(i)))
    
    bkg_model = RooAddPdf('bkg_model', 'bkg_model', lambdas, betas, kTRUE)
    getattr(w, 'import')(bkg_model, RooFit.RecycleConflictNodes())
    #return w.pdf('sumExp')


    
    # create signal model
    # RooRealVars
    w.factory('mean1_sig_model[125., 122., 128.]')
    w.factory('sigma1_sig_model[5., 1., 20.]')
    w.var('mean1_sig_model').setUnit('GeV')
    w.var('sigma1_sig_model').setUnit('GeV')
    w.factory('mean2_sig_model[125., 122., 128.]')
    w.factory('sigma2_sig_model[5., 1., 20.]')
    w.var('mean2_sig_model').setUnit('GeV')
    w.var('sigma2_sig_model').setUnit('GeV')
    w.factory('mean3_sig_model[125., 122., 128.]')
    w.factory('sigma3_sig_model[5., 1., 20.]')
    w.var('mean3_sig_model').setUnit('GeV')
    w.var('sigma3_sig_model').setUnit('GeV')
    w.factory('coef1_sig_model[0.5, 0., 1.]')
    w.factory('coef2_sig_model[0.5, 0., 1.]')
    # RooAbsPdfs
    #w.var('mean').setConstant()
    g1 = w.factory('Gaussian::g1_sig_model(x, mean1_sig_model,'
                    'sigma1_sig_model)')
    g2 = w.factory('Gaussian::g2_sig_model(x, mean2_sig_model,'
                    'sigma2_sig_model)')
    g3 = w.factory('Gaussian::g3_sig_model(x, mean3_sig_model,'
                    'sigma3_sig_model)')
    gaussians = RooArgList(g1, g2, g3)
    betas = RooArgList(w.var('coef1_sig_model'),
        w.var('coef2_sig_model'))



    # save models
    bkg_model = w.pdf('bkg_model')
    sig_model = w.pdf('sig_model')
    
    
    # create output file
    f1 = TFile('{0}/{1}'.format(shape_data_dir, output_file), 'RECREATE')
    f1.cd()

    # save workspace in output file
    w.Write()

    # save original histograms for rates calculation
#    h_sigVBF = f0.Get('histos/dimuMass_VBF').Clone('sigVBF')
#    h_sigGGF = f0.Get('histos/dimuMass_GGF').Clone('sigGGF')
#    h_bkgTTJ = f0.Get('histos/dimuMass_TTJets').Clone('bkgTTJ')
#    h_bkgDYJ = f0.Get('histos/dimuMass_DYJetsToLL').Clone('bkgDYJ')
#    h_data   = f0.Get('Mass').Clone('data_obs')
#    h_sigVBF.Write()
#    h_sigGGF.Write()
#    h_bkgTTJ.Write()
#    h_bkgDYJ.Write()
#    h_data.Write()

    f1.Write()
    f1.Close()
    print 'Created ' + '{0}/{1}'.format(shape_data_dir, output_file)


# __________________________________________________________
try:
    main()
except KeyboardInterrupt:
    print

