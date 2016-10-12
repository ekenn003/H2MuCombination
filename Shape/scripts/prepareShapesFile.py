#!/usr/bin/env python
import os, sys
from ROOT import *

main_data_dir  = '{0}/src/H2MuCombination/data'.format(os.environ['CMSSW_BASE'])
shape_data_dir = '{0}/src/H2MuCombination/Shape/data'.format(os.environ['CMSSW_BASE'])
input_file  = 'simulated_mass_distribution.root'
output_file = 'p.root'


# __________________________________________________________
def main():
    # get histograms made with PlotMaker
    f0 = TFile('{0}/{1}'.format(main_data_dir, input_file))
    #h = f0.Get('data_obs')
    h = f0.Get('Mass')
    
    nbins = h.GetNbinsX()
    xmin  = h.GetBinLowEdge(1)
    xmax  = xmin + (nbins * h.GetBinWidth(1))
    
    # create roo workspace
    w = RooWorkspace('mumu')
    
    # create dimuon mass observable
    w.factory('x[120.0, {0}, {1}]'.format(xmin, xmax))
    w.var('x').SetTitle('M_{#mu#mu}')
    w.var('x').setUnit('GeV')
    
    # how to make RooDataHist in C++:
    #     RooDataSet dataset("data","data",x,Import(*h));
    # how to make it in pyroot:
    # define the set obs=(x) and make it known to python
    w.defineSet('obs', 'x')
    obs = w.set('obs')
    # create binned dataset from histograms and add to workspace
    dataset = RooDataHist('data_obs', 'data_obs', RooArgList(obs), h)
    # how to use the import method in PyROOT
    getattr(w,'import')(dataset, RooCmdArg())
    
    # create background model
    # RooRealVars
    w.factory('lambda1[-0.1, -10., 10.]')
    # RooAbsPdfs
#    w.factory('Exponential::exp1(x, lambda1)')
    w.factory('Exponential::bkg_model(x, lambda1)')
    #w.factory('GenericPdf::bkg_model("x^(-2)", x)')
    # multiply the two pdfs
    # https://root.cern.ch/root/html/tutorials/roofit/rf512_wsfactory_oper.C.html#37
#    w.factory('PROD::bkg_model(x, exp1, poly1)')
    
    # create signal model
    # RooRealVars
    w.factory('mean[125., {0}, {1}]'.format(xmin, xmax))
    w.factory('sigma1[1.0, -10., 10.]')
    w.factory('gamma1[1.0, -10., 10.]')
    # RooAbsPdfs
    w.factory('Voigtian::sig_model(x, mean, sigma1, gamma1)')
    w.var('mean').setConstant()
    
    # save models
    bkg_model = w.pdf('bkg_model')
    sig_model = w.pdf('sig_model')
    
    
    # create output file
    f1 = TFile('{0}/{1}'.format(shape_data_dir, output_file), 'RECREATE')
    f1.cd()

    # save workspace in output file
    w.Write()

    # save original histograms for rates calculation
    h_sigVBF = f0.Get('histos/dimuMass_VBF').Clone('sigVBF')
    h_sigGGF = f0.Get('histos/dimuMass_GGF').Clone('sigGGF')
    h_bkgTTJ = f0.Get('histos/dimuMass_TTJets').Clone('bkgTTJ')
    h_bkgDYJ = f0.Get('histos/dimuMass_DYJetsToLL').Clone('bkgDYJ')
    h_data   = f0.Get('Mass').Clone('data_obs')
    h_sigVBF.Write()
    h_sigGGF.Write()
    h_bkgTTJ.Write()
    h_bkgDYJ.Write()
    h_data.Write()

    f1.Write()
    f1.Close()
    print 'Created ' + '{0}/{1}'.format(shape_data_dir, output_file)


# __________________________________________________________
try:
    main()
except KeyboardInterrupt:
    print

