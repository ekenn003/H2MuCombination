#!/usr/bin/env python
import os, sys
from time import sleep
from ROOT import *

main_data_dir  = '{0}/src/H2MuCombination/data'.format(os.environ['CMSSW_BASE'])
shape_data_dir = '{0}/src/H2MuCombination/Shape/data'.format(os.environ['CMSSW_BASE'])
input_file  = 'simulated_mass_distribution.root'
output_file = 'p.root'


def main():
    RooMsgService.instance().setGlobalKillBelow(RooFit.FATAL)

    # get histograms made with PlotMaker
    f0 = TFile('{0}/{1}'.format(main_data_dir, input_file))
    #h = f0.Get('data_obs')
    h = f0.Get('Mass')
    
    nbins = h.GetNbinsX()
    xmin  = h.GetBinLowEdge(1)
    xmax  = xmin + (nbins * h.GetBinWidth(1))
    
    # create roo workspace
    w = RooWorkspace('mumu')
    
    # create di-muon mass variable
    # 'varname[initial-val, min-val, max-val]'
    w.factory('x[120.0, {0}, {1}]'.format(xmin, xmax))
    w.var('x').SetTitle('M_{#mu#mu}')
    w.var('x').setUnit('GeV')
    
    # how to make RooDataHist in C++:
    # RooDataSet dataset("data","data",x,Import(*h));
    # how to make it in pyroot:
    # define the set obs=(x) and make it known to python
    w.defineSet('obs', 'x')
    obs = w.set('obs')
    # create binned dataset from histograms and add to workspace
    dataset = RooDataHist('data_obs', 'data_obs', RooArgList(obs), h)
    # trick to use the import method in PyROOT
    getattr(w,'import')(dataset, RooCmdArg())
    #getattr(w,'import')(dataset)
    
    # create background model (exponential * 1/m^2)
    data_norm = int(dataset.sumEntries())
    
    # RooRealVars
    w.factory('a1[-0.1, -5., 0.]')
    w.factory('a2[-0.1, -5., 0.]')
    # RooAbsPdfs
    w.factory('Exponential::exp1(x, a1)')
    w.factory('GenericPdf::poly1("x^(-2)", x)')



    # multiply the two pdfs
    # https://root.cern.ch/root/html/tutorials/roofit/rf512_wsfactory_oper.C.html#37
    w.factory('PROD::bkg_pdf(x, exp1, poly1)')
    
    # create signal model (Double gaus)
    # RooRealVars
    w.factory('mean[125., {0}, {1}]'.format(xmin, xmax))
    w.factory('sigma1[1.0, 0.1, 10]')
    w.factory('sigma2[1.0, 0.1, 10]')
    # RooAbsPdfs
    w.factory('Gaussian::gaus1(x, mean, sigma1)')
    w.factory('Gaussian::gaus2(x, mean, sigma2)')
    # convo the two gausses
    w.factory('FCONV::sig_pdf(x, gaus1, gaus2)')
    w.var('mean').setConstant()
    
    # save models
    bkg_model = w.pdf('bkg_model')
    sig_model = w.pdf('sig_model')
    
    
    # save workspace in output file
    w.SaveAs('{0}/{1}'.format(shape_data_dir, output_file))


# __________________________________________________________
try:
    main()
except KeyboardInterrupt:
    print

