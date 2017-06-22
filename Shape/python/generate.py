import ROOT as R

#cats = ['cat'+str(i).zfill(2) for i in xrange(16)]
R.gROOT.SetBatch(R.kTRUE)


cats = ['cat'+str(i).zfill(2) for i in xrange(6)]


r = {'central':125, 'min':110, 'max':160, 'fitmin' : 115, 'fitmax' : 135}


## ____________________________________________________________________________
def build_mass_var(ws):
    print 'x[{central}, {min}, {max}]'.format(**r)
    ws.factory('x[{central}, {min}, {max}]'.format(**r))
    ws.var('x').SetTitle('m_{#mu#mu}')
    ws.var('x').setUnit('GeV')
    ws.defineSet('obs', 'x')

## ____________________________________________________________________________
def get_RooHist(ws, h, name=None):
    if not name:
        name = h.GetName()
    return R.RooDataHist(name, name, R.RooArgList(ws.set('obs')), h)




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

    # fraction
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
    fractions = R.RooArgList(ws.var('coef1_tripleGaus'),
        ws.var('coef2_tripleGaus'))
    print fractions.getSize()
    print gaussians.getSize()
    tripleGaus = R.RooAddPdf('tripleGaus', 'tripleGaus',
        gaussians, fractions, R.kTRUE)
    getattr(ws, 'import')(tripleGaus, R.RooFit.RecycleConflictNodes())

    return ws.pdf('tripleGaus')




## ____________________________________________________________________________
def build_(ws, th1):
    print 'building Triple Gaussian model'




## ____________________________________________________________________________
def main():
    for c in cats: print c



    wspace_name = 'higgs'
    signal_model = 'tripleGauss'
    data_f = R.TFile('/afs/cern.ch/work/e/ekennedy/work/fsanalysis/ana76/'
                     'root6/CMSSW_7_6_5/src/AnalysisToolLight/2Mu/'
                     'tmpout_VBF_full.root')
    h_name_base = 'categories/hDiMuInvMass_'


    for cat in cats: 
        wspace_fname = 'workspace_{0}_{1}.root'.format(cat, signal_model)
        wspace = R.RooWorkspace(wspace_name)
        build_mass_var(wspace)

        # get data and turn it into a RooDataHist
        h_data = data_f.Get(h_name_base+cat)
        h_name = 'data_obs_' + cat
        rh_data = get_RooHist(wspace, h_data, name=h_name)

        norm = rh_data.sumEntries()
        print cat, 'norm =', norm

        canv = R.TCanvas(cat, cat, 800, 600)
        canv.cd()
        frame = wspace.var('x').frame()

        sigpdf = build_tripleGaus(wspace, h_data)

        thissigfit = sigpdf.fitTo(rh_data, R.RooFit.Save(),
            R.RooFit.Range(r['fitmin'], r['fitmax']),
            R.RooFit.SumW2Error(R.kTRUE))



        bkgpdf = build_backgroundExp(wspace, h_data)


        thisbkgfit = bkgpdf.fitTo(rh_data, R.RooFit.Save(),
            R.RooFit.Range(r['fitmin'], r['fitmax']),
            R.RooFit.SumW2Error(R.kTRUE))











        rh_data.plotOn(frame)

        sigpdf.plotOn(frame, R.RooFit.LineColor(R.kBlue))
        bkgpdf.plotOn(frame, R.RooFit.LineColor(R.kRed))


        frame.SetTitle('DiMuon Invariant Mass ({0})'.format(cat))
        frame.Draw()
        canv.Print('test_'+cat+'.png')



    data_f.Close()











# _____________________________________________________________________________
try:
    main()
except KeyboardInterrupt:
    print
