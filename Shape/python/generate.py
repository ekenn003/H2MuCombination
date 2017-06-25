import ROOT as R

R.gROOT.SetBatch(R.kTRUE)

lumi = 215. # pb

blind_low = 120.
blind_high = 130.

#cats = ['cat'+str(i).zfill(2) for i in xrange(16)]
#cats = ['cat'+str(i).zfill(2) for i in xrange(6)]
cats = ['cat'+str(i).zfill(2) for i in xrange(1)]

expd = 5

rs = {'central':125, 'min':110, 'max':200, 'fitmin' : 115, 'fitmax' : 135}
rb = {'central':130, 'min':110, 'max':200, 'fitmin' : 110, 'fitmax' : 200}

colors = [
    R.kGreen, R.kBlue, R.kYellow, R.kViolet,
    R.kOrange, R.kPink, R.kMagenta, R.kAzure, R.kCyan, R.kTeal,
    R.kSpring
]

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
def get_weighted_hist(tfile, hname):
    xsec, sumw = get_mc_info(tfile)
    try:
        h = tfile.Get(hname)
    except:
        print 'ERROR: could not get {0} from {1}.'.format(hname, tfile)
        return False
    h.Scale((lumi*xsec)/sumw)
    return h



## ____________________________________________________________________________
def build_mass_var(ws):
    print 'x[{central}, {min}, {max}]'.format(**rs)
    ws.factory('x[{central}, {min}, {max}]'.format(**rs))
    ws.var('x').SetTitle('m_{#mu#mu}')
    ws.var('x').setUnit('GeV')
    ws.defineSet('obs', 'x')

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
def build_tripleGaus(ws, th1):
    print 'building Triple Gaussian model'

    initial_values = {
        'mean1' : th1.GetMean(), 'mean1min' : th1.GetMean() - 0.2*th1.GetRMS(),
        'mean1max' : th1.GetMean() + 0.2*th1.GetRMS(),
        'sigma1' : 0.6*th1.GetRMS(), 'sigma1min' : 0.2*th1.GetRMS(),
        'sigma1max' : 1.2*th1.GetRMS(),
        'mean2' : th1.GetMean(), 'mean2min' : th1.GetMean() - 0.4*th1.GetRMS(),
        'mean2max' : th1.GetMean() + 0.4*th1.GetRMS(),
        'sigma2' : 1.0*th1.GetRMS(), 'sigma2min' : 0.4*th1.GetRMS(),
        'sigma2max' : 1.8*th1.GetRMS(),
        'mean3' : th1.GetMean(), 'mean3min' : th1.GetMean() - 2.4*th1.GetRMS(),
        'mean3max' : th1.GetMean() + 0.8*th1.GetRMS(),
        'sigma3' : 2.4*th1.GetRMS(), 'sigma3min' : 1.2*th1.GetRMS(),
        'sigma3max' : 4.8*th1.GetRMS(),
        'coef1' : 0.7, 'coef1min' : 0.5, 'coef1max' : 1,
        'coef2' : 0.6, 'coef2min' : 0.0, 'coef2max' : 1
    }

    print initial_values





    ws.factory('mean1_tripleGaus[{mean1}, {mean1min}, {mean1max}]'.format(
         **initial_values))
    ws.factory('sigma1_tripleGaus[{sigma1}, {sigma1min}, {sigma1max}]'.format(
         **initial_values))
    ws.var('mean1_tripleGaus').setUnit('GeV')
    ws.var('sigma1_tripleGaus').setUnit('GeV')
    ws.factory('mean2_tripleGaus[{mean2}, {mean2min}, {mean2max}]'.format(
         **initial_values))
    ws.factory('sigma2_tripleGaus[{sigma2}, {sigma2min}, {sigma2max}]'.format(
         **initial_values))
    ws.var('mean2_tripleGaus').setUnit('GeV')
    ws.var('sigma2_tripleGaus').setUnit('GeV')
    ws.factory('mean3_tripleGaus[{mean3}, {mean3min}, {mean3max}]'.format(
         **initial_values))
    ws.factory('sigma3_tripleGaus[{sigma3}, {sigma3min}, {sigma3max}]'.format(
         **initial_values))
    ws.var('mean3_tripleGaus').setUnit('GeV')
    ws.var('sigma3_tripleGaus').setUnit('GeV')

    # beta
    ws.factory('coef1_tripleGaus[{coef1}, {coef1min}, {coef1max}]'.format(
         **initial_values
    ))
    ws.factory('coef2_tripleGaus[{coef2}, {coef2min}, {coef2max}]'.format(
         **initial_values
    ))




    g1 = ws.factory('Gaussian::g1_tripleGaus(x, mean1_tripleGaus,'
                    'sigma1_tripleGaus)')
    g2 = ws.factory('Gaussian::g2_tripleGaus(x, mean2_tripleGaus,'
                    'sigma2_tripleGaus)')
    g3 = ws.factory('Gaussian::g3_tripleGaus(x, mean3_tripleGaus,'
                    'sigma3_tripleGaus)')
    gaussians = R.RooArgList(g1, g2, g3)
    betas = R.RooArgList(ws.var('coef1_tripleGaus'),
        ws.var('coef2_tripleGaus'))
    print betas.getSize()
    print gaussians.getSize()
    tripleGaus = R.RooAddPdf('tripleGaus', 'tripleGaus',
        gaussians, betas, R.kTRUE)
    getattr(ws, 'import')(tripleGaus, R.RooFit.RecycleConflictNodes())

    return ws.pdf('tripleGaus')




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
    
    sumExp = R.RooAddPdf('sumExp', 'sumExp', exps, betas, R.kTRUE)
    getattr(ws, 'import')(sumExp, R.RooFit.RecycleConflictNodes())


    return ws.pdf('sumExp')






## ____________________________________________________________________________
def main():
    for c in cats: print c

    wspace_name = 'mumu'
    signal_model = 'tripleGaus'
    #f_base = ('/afs/cern.ch/work/e/ekennedy/work/fsanalysis/ana76/'
    #          'root6/CMSSW_7_6_5/src/AnalysisToolLight/2Mu/')
    f_base = ('')
    data_f = R.TFile(f_base+
                     #'tmpout_data.root')
                     'ana_2Mu_DYJetsToLL.root')
    vbf_f  = R.TFile(f_base+
                     'tmpout_VBF_full.root')
                     #'ana_2Mu_DYJetsToLL.root')
    h_name_base = 'categories/hDiMuInvMass_'



    for cat in cats: 
        wspace_fname = 'workspace_{0}_{1}.root'.format(cat, signal_model)
        wspace = R.RooWorkspace(wspace_name)
        build_mass_var(wspace)

        # get data and turn it into a RooDataHist
        h_data = data_f.Get(h_name_base+cat)
        h_vbf = get_weighted_hist(vbf_f, h_name_base+cat)

        h_name = 'data_obs_' + cat
        rh_data = get_RooHist(wspace, h_data, name=h_name, blind=True)

        norm = rh_data.sumEntries()
        print cat, 'norm =', norm

        canv = R.TCanvas(cat, cat, 1200, 900)
        canv.cd()
        frame = wspace.var('x').frame()

        sigpdf = build_tripleGaus(wspace, h_vbf)

        thissigfit = sigpdf.fitTo(rh_data, R.RooFit.Save(),
            R.RooFit.Range(rs['fitmin'], rs['fitmax']),
            R.RooFit.Range(rs['fitmin'], rs['fitmax']),
            R.RooFit.SumW2Error(R.kTRUE))



        bkgpdf = build_sumExp(wspace, expd)
        wspace.var('x').setRange('blinded_low', rb['min'], blind_low)
        wspace.var('x').setRange('blinded_high', blind_high, rb['max'])
        thisbkgfit = bkgpdf.fitTo(rh_data, R.RooFit.Save(),
            R.RooFit.Range('blinded_low,blinded_high'),
            R.RooFit.NormRange('blinded_low,blinded_high'),
            R.RooFit.SumW2Error(R.kTRUE))


        rh_data.plotOn(frame, R.RooFit.DrawOption('P'))

        sigpdf.plotOn(frame, R.RooFit.LineColor(R.kBlue),
                      R.RooFit.Name('tripleGaus'),
                      R.RooFit.Range('FULL'))
        bkgpdf.plotOn(frame, R.RooFit.LineColor(R.kRed),
                      R.RooFit.Name('sumExp'),
                      R.RooFit.Range('FULL'))
                      #R.RooFit.Normalization(norm, R.RooAbsReal.NumEvent)))

        leg = R.TLegend(0.65, 0.6, 0.9, 0.9)
        leg.AddEntry(frame.findObject('tripleGaus'), 'tripleGaus', 'l')
        leg.AddEntry(frame.findObject('sumExp'), 'sumExp', 'l')

#        for i in xrange(1,expd+1):
#            bkgpdf.plotOn(frame, R.RooFit.LineColor(colors[i]),
#                R.RooFit.LineWidth(1),
#                R.RooFit.Components('exp{0}_sumExp'.format(i)),
#                R.RooFit.Name('exp{0}_sumExp'.format(i)))
#            leg.AddEntry(frame.findObject('exp{0}_sumExp'.format(i)), 'exp{0}_sumExp'.format(i), 'l')


        frame.SetTitle('Bkg only + signal, M_{{#mu#mu}} ({0})'.format(cat))
        frame.Draw()
        leg.Draw()
        R.gPad.Modified()
        canv.Print('test_'+cat+'.png')
        wspace.Print('v')
        wspace.SaveAs(wspace_fname)



    data_f.Close()


# _____________________________________________________________________________
try:
    main()
except KeyboardInterrupt:
    print
