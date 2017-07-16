import ROOT as R
from tools.tools import build_mass_var, build_sum_exp, build_bwz_gamma

R.gROOT.SetBatch(R.kTRUE)

lumi = 36920. # pb

blind_low = 120.
blind_high = 130.

cats = ['cat'+str(i).zfill(2) for i in xrange(1,16)]
#cats = ['cat'+str(i).zfill(2) for i in xrange(6)]
#cats = ['cat'+str(i).zfill(2) for i in xrange(1)]

bkg_model = 'bwzGamma'
max_expd = 1

ranges = {
    'blind_low'  : 120.,
    'blind_high' : 130.,
    'range_low'  : 100.,
    'range_high' : 150.,
    'sig_fit_low'  : 115.,
    'sig_fit_high' : 135.,
}

colors = [
    R.kSpring,
    R.kBlue,
    R.kOrange,
    R.kPink,
    #R.kMagenta,
    R.kCyan,
    #R.kTeal,
    R.kViolet,
    R.kGreen, 
    R.kYellow,
]

R.RooMsgService.instance().setGlobalKillBelow(5)

## ____________________________________________________________________________
def get_RooHist(ws, h, name=None, blind=False):
    if not name:
        name = h.GetName()
    if blind:
        for ibin in range(h.GetNbinsX()):
            if (h.GetBinCenter(ibin+1)>blind_low 
                and h.GetBinCenter(ibin+1)<blind_high):
                h.SetBinContent(ibin+1, 0)
    rh = R.RooDataHist(name, name, R.RooArgList(ws.set('obs')), h)
    return rh



## ____________________________________________________________________________
def get_norm_integral(pdf, ws, fr):
    rooarg = R.RooArgSet(ws.var('x'))
    integral = pdf.createIntegral(rooarg, rooarg, 'signal_region')
    norm_yield = integral.getVal()
    yield_error = integral.getPropagatedError(fr)
    return norm_yield, yield_error



## ____________________________________________________________________________
def main():
    for c in cats: print c

    wspace_name = 'higgs'
    #signal_model = 'tripleGauss'
    #f_base = ('/afs/cern.ch/work/e/ekennedy/work/fsanalysis/ana76/'
    #          'root6/CMSSW_7_6_5/src/AnalysisToolLight/2Mu/')
    #f_base = ('')
    f_base = ('/afs/cern.ch/work/e/ekennedy/work/limits/h2mu/'
              'CMSSW_7_4_7/src/H2MuCombination/data/')
    data_f = R.TFile(f_base+
                     #'tmpout_data.root')
                     'ana_2Mu_SingleMuon_Run2016.root')
    #vbf_f  = R.TFile(f_base+
    #                 #'tmpout_VBF_full.root')
    #                 'ana_2Mu_DYJetsToLL.root')
    h_name_base = 'categories/hDiMuInvMass_'

    ftest_results = {}
    order_4_yields = []


    for cat in cats: 



        #if cat!='cat02': continue




        wspace_fname = 'workspace_{0}_{1}.root'.format(cat, 'ftest')
        wspace = R.RooWorkspace(wspace_name)
        build_mass_var(wspace, ranges)

        bkg_models = []
        for order in xrange(1,max_expd+1):
            #bkg_models.append(build_sum_exp(wspace, cat, order=order))
            bkg_models.append(build_bwz_gamma(wspace, cat))


        ftest_results[cat] = {}
        leg = R.TLegend(0.35, 0.6, 0.9, 0.9)

        # get data and turn it into a RooDataHist
        h_data = data_f.Get(h_name_base+cat)
        #h_vbf = get_weighted_hist(vbf_f, h_name_base+cat)
    
        h_name = 'data_obs_' + cat
        rh_data_unblind = get_RooHist(wspace, h_data, name=h_name, blind=False)
        rh_data = get_RooHist(wspace, h_data, name=h_name, blind=True)
    
        norm = rh_data_unblind.sumEntries()
        norm_blind = rh_data.sumEntries()
        print cat, 'norm =', norm, ', normblind =', norm_blind
    
        canv = R.TCanvas(cat, cat, 1200, 900)
        canv.cd()
        frame = wspace.var('x').frame()

        rh_data.plotOn(frame, R.RooFit.DrawOption('P'))


        for order in xrange(1,max_expd+1):
        #for order in xrange(max_expd,max_expd+1):
            thisbkgfit = bkg_models[order-1].fitTo(rh_data, R.RooFit.Save(),
                R.RooFit.Range('blinded_low,blinded_high'),
                R.RooFit.NormRange('blinded_low,blinded_high'),
                #R.RooFit.PrintLevel(-1),
                R.RooFit.SumW2Error(R.kTRUE))

            thisndof = order*2-1

            thischi2 = frame.chiSquare()
            thispval = 1. - R.TMath.Prob(thischi2, thisndof)

            #print '\n'*10
            #print '*'*80
            #print '*'*80
            #print 'order {0} chi2 value = {1}, p = {2}'.format(order, thischi2, thispval)
            #print '*'*80
            #print '*'*80
            #print '\n'*10

            bkg_models[order-1].plotOn(frame, R.RooFit.LineColor(colors[order]),
                R.RooFit.LineWidth(2),
                R.RooFit.Name(bkg_model+'Ord'+str(order)),
                R.RooFit.Range('full_range'),
                #R.RooFit.Normalization(norm, R.RooAbsReal.NumEvent))
                )

            bkg_models[order-1].paramOn(frame, R.RooFit.Layout(0.55, 0.95, 0.64))
            frame.getAttText().SetTextSize(0.02)


            b_integral = get_norm_integral(bkg_models[order-1], wspace, thisbkgfit)
            byield = b_integral[0]*norm, b_integral[1]*norm
            if order==4: order_4_yields.append(byield)


            #if thispval >= 0.05:
            #    leg.AddEntry(frame.findObject(bkg_model+'Ord'+str(order)), 
            #        (bkg_model+'Ord{0}, p = {1:0.3f}, y = {2:0.0f} +/- {3:0.0f}').format(
            #            order, thispval, byield[0], byield[1]), 'l')

        leg.AddEntry(rh_data, 'SingleMuon 2016', 'p')


        frame.SetTitle('F-test: M_{{#mu#mu}} {1} ({0})'.format(cat, bkg_model))
        frame.Draw()
        #leg.Draw()
        R.gPad.Modified()
        canv.Print('ftest_{1}_{0}_yields.png'.format(cat, bkg_model))


    #for i, cat in enumerate(cats):
    #    print '{0}: {1:0.0f} \pm {2:0.0f}'.format(cat, 
    #        order_4_yields[i][0], order_4_yields[i][1])


    data_f.Close()


# _____________________________________________________________________________
try:
    main()
except KeyboardInterrupt:
    print


