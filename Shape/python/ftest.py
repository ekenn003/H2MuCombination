import ROOT as R

R.gROOT.SetBatch(R.kTRUE)

lumi = 215. # pb

blind_low = 120.
blind_high = 130.

#cats = ['cat'+str(i).zfill(2) for i in xrange(16)]
cats = ['cat'+str(i).zfill(2) for i in xrange(6)]
#cats = ['cat'+str(i).zfill(2) for i in xrange(1)]

max_expd = 6

#rs = {'central':125, 'min':110, 'max':200, 'fitmin' : 115, 'fitmax' : 135}
rb = {'central':130, 'min':110, 'max':200, 'fitmin' : 110, 'fitmax' : 200}

colors = [
    R.kGreen, R.kBlue, R.kYellow, R.kViolet,
    R.kOrange, R.kPink, R.kMagenta, R.kAzure, R.kCyan, R.kTeal,
    R.kSpring
]

#R.RooFit.RooMsgService.instance().setGlobalKillBelow(4)
R.RooMsgService.instance().setGlobalKillBelow(5)

## ____________________________________________________________________________
def build_mass_var(ws):
    print 'x[{central}, {min}, {max}]'.format(**rb)
    ws.factory('x[{central}, {min}, {max}]'.format(**rb))
    ws.var('x').SetTitle('m_{#mu#mu}')
    ws.var('x').setUnit('GeV')
    ws.defineSet('obs', 'x')
    ws.var('x').setRange('blinded_low', rb['min'], blind_low)
    ws.var('x').setRange('blinded_high', blind_high, rb['max'])

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
def build_sumExp(ws, degree):
    print 'building degree {0} exponential model'.format(degree)


    exps  = R.RooArgList()
    betas = R.RooArgList()

    for i in xrange(1, degree+1):
        ws.factory('alpha{0}_sumExp[{1}, -1., 0.]'.format(
            i, max(-1., -0.04*(i+1))))
        if i < degree:
            ws.factory('beta{0}_sumExp[{1}, 0.0001, .9999]'.format(
                i, 0.9-float(i-1)*1./degree))
            betas.add(ws.var('beta{0}_sumExp'.format(i)))


    for i in xrange(1, degree+1):
        ws.factory('Exponential::exp{0}_sumExp(x, alpha{0}_sumExp)'.format(i))
        exps.add(ws.pdf('exp{0}_sumExp'.format(i)))
    
    sumExp = R.RooAddPdf('sumExpOrd'+str(degree), 
                         'sumExpOrd'+str(degree), exps, betas, R.kTRUE)
    getattr(ws, 'import')(sumExp, R.RooFit.RecycleConflictNodes())


    return ws.pdf('sumExpOrd'+str(degree))






## ____________________________________________________________________________
def main():
    for c in cats: print c

    wspace_name = 'higgs'
    signal_model = 'tripleGauss'
    #f_base = ('/afs/cern.ch/work/e/ekennedy/work/fsanalysis/ana76/'
    #          'root6/CMSSW_7_6_5/src/AnalysisToolLight/2Mu/')
    f_base = ('')
    data_f = R.TFile(f_base+
                     #'tmpout_data.root')
                     'ana_2Mu_DYJetsToLL.root')
    vbf_f  = R.TFile(f_base+
                     #'tmpout_VBF_full.root')
                     'ana_2Mu_DYJetsToLL.root')
    h_name_base = 'categories/hDiMuInvMass_'

    ftest_results = {}


    for cat in cats: 
        wspace_fname = 'workspace_{0}_{1}.root'.format(cat, 'ftest')
        wspace = R.RooWorkspace(wspace_name)
        build_mass_var(wspace)

        bkg_models = []
        for order in xrange(1,max_expd+1):
            bkg_models.append(build_sumExp(wspace, order))


        ftest_results[cat] = {}
        leg = R.TLegend(0.35, 0.6, 0.9, 0.9)

        # get data and turn it into a RooDataHist
        h_data = data_f.Get(h_name_base+cat)
        #h_vbf = get_weighted_hist(vbf_f, h_name_base+cat)
    
        h_name = 'data_obs_' + cat
        rh_data = get_RooHist(wspace, h_data, name=h_name, blind=True)
    
        norm = rh_data.sumEntries()
        print cat, 'norm =', norm
    
        canv = R.TCanvas(cat, cat, 800, 600)
        canv.cd()
        frame = wspace.var('x').frame()

        rh_data.plotOn(frame, R.RooFit.DrawOption('P'))

        prevNLL = -1.

        for order in xrange(1,max_expd+1):
            print 'trying to get exp order', order
            thisbkgfit = bkg_models[order-1].fitTo(rh_data, R.RooFit.Save(),
                R.RooFit.Range('blinded_low,blinded_high'),
                R.RooFit.NormRange('blinded_low,blinded_high'),
                R.RooFit.PrintLevel(-1),
                R.RooFit.SumW2Error(R.kTRUE))

            bkg_models[order-1].plotOn(frame, R.RooFit.LineColor(colors[order]),
                R.RooFit.LineWidth(2),
                R.RooFit.Name('sumExpOrd'+str(order)),
                R.RooFit.Range('FULL'),
                #R.RooFit.Normalization(norm, R.RooAbsReal.NumEvent))
                )


            thisndof = order*2-1

            thischi2 = frame.chiSquare()
            thispval = R.TMath.Prob(thischi2, thisndof)

            print '\n'*10
            print '*'*80
            print '*'*80
            print 'order {0} chi2 value = {1}, p = {2}'.format(order, thischi2, thispval)
            print '*'*80
            print '*'*80
            print '\n'*10

            leg.AddEntry(frame.findObject('sumExpOrd'+str(order)), 
                'sumExpOrd{0}, #chi^2 ={1}, p={2}'.format(order, thischi2, thispval), 'l')


        frame.SetTitle('DiMuon Invariant Mass ({0})'.format(cat))
        frame.Draw()
        leg.Draw()
        R.gPad.Modified()
        canv.Print('ftest_sumExp_{0}.png'.format(cat))



    data_f.Close()


# _____________________________________________________________________________
try:
    main()
except KeyboardInterrupt:
    print
