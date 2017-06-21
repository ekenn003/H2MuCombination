import ROOT as R

#cats = ['cat'+str(i).zfill(2) for i in xrange(16)]
cats = ['cat'+str(i).zfill(2) for i in xrange(6)]

diMuonMass125 = {'name':'DiMuonMass', 'central':125, 'min':110, 'max':160,
    'fitmin' : 115, 'fitmax' : 135}
diMuonMass120 = {'name':'DiMuonMass', 'central':120, 'min':110, 'max':160,
    'fitmin' : 110, 'fitmax' : 130}
diMuonMass130 = {'name':'DiMuonMass', 'central':130, 'min':110, 'max':160,
    'fitmin' : 120, 'fitmax' : 140}


## ____________________________________________________________________________
def build_mass_variable(ws, **kwargs):
    print kwargs
    print 'x[{central}, {min}, {max}]'.format(**kwargs)
    ws.factory('x[{central}, {min}, {max}]'.format(**kwargs))
    ws.var('x').SetTitle('m_{#mu#mu}')
    ws.var('x').setUnit('GeV')
    ws.defineSet('obs', 'x')




## ____________________________________________________________________________
def get_RooHist(ws, hist, name=None):
    if not name:
        name = h.GetName()
    roohist = R.RooDataHist(name, name,
        R.RooArgList(ws.set('obs')), h)
    return roohist


## ____________________________________________________________________________
def main():
    for c in cats: print c



    f_test_results = {}

    wspace_name = 'higgs'
    signal_model = 'tripleGauss'
    data_f = R.TFile('filenamejere')


    for cat in cats: 
        f_test_results[cat] = {}
        wspace_fname = 'workspace_{0}_{1}.root'.format(cat, signal_model)
        wspace = R.RooWorkspace(wspace_name)


        # get data and turn it into a RooDataHist
        h_data = data_f.Get('datahistnamehere'+cat)
        h_name = 'data_obs_' + cat
        rh_data = get_RooHist(wspace, h_data, h_name)
        # ?
        getattr(wspace, 'import')(rh_data, R.RooFit.RecycleConflictNodes())











    data_f.Close()











# _____________________________________________________________________________
try:
    main()
except KeyboardInterrupt:
    print
