# produces datacards in an existing directory named 'Datacards'
import os, sys
from ROOT import *

datadir = '{0}/src/H2MuCombination/data'.format(os.environ['CMSSW_BASE'])

#################################################
# shapes file
#################################################
f0 = TFile.Open('{0}/test.root'.format(datadir))
shapefile = 'test.root'

#################################################
#################################################
datacard = 'Datacards/DataCard_HToMuMu_2Mu_13TeV_2016Analysis.txt'

#h = TH1F(f0.Get('ZPrime{0}'.format(mass)))
#signal_yield = -999999
#signal_yield = h.Integral()


#################################################
# channels
#################################################
sigProcesses = ['sigVBF', 'sigGGF']
bkgProcesses = ['bkgTTJ', 'bkgDYJ']

binname = 'mm'

#################################################
# data yield (-1 for expected/blinded)
#################################################
#data_yield = TH1F(f0.Get('data_obs')).Integral()
data_yield = -1





#################################################
#################################################

nSigs = len(sigProcesses)
nBkgs = len(bkgProcesses)


# fill rates
rates = []
for p in sigProcesses+bkgProcesses:
    rate = TH1F(f0.Get(p)).Integral()
    rates.append(rate)

#################################################
# write datacard
#################################################
with open(datacard, 'w') as fout:
    fout.write('imax \t* \tnumber of channels \n')
    fout.write('jmax \t{0} \tnumber of backgrounds \n'.format(nBkgs))
    fout.write('kmax \t* \tnumber of nuisance parameters (sources of systematic uncertainties) \n')
    fout.write('-------------\n')
    fout.write('bin \t{0} \n'.format(binname))
    fout.write('observation \t{0} \n'.format(data_yield))
    fout.write('-------------\n')
    fout.write('shapes \t*  \t{0} \tdata/{1} \t$PROCESS\n'.format(binname, shapefile))
    fout.write('-------------\n')

    fout.write('bin')
    for i in range(nSigs+nBkgs):
        fout.write('\t\t{0}'.format(binname))
    fout.write('\n')

    fout.write('process')
    for p in sigProcesses+bkgProcesses:
        fout.write('\t\t{0}'.format(p))
    fout.write('\n')

    fout.write('process')
    for i in range(1-nSigs,nBkgs+1,1):
        fout.write('\t\t{0}'.format(i))
    fout.write('\n')

    fout.write('rate\t')
    for r in rates:
        fout.write('\t{0}'.format(r))
    fout.write('\n')
    fout.write('-------------\n')

    #fout.write('lumi_13TeV \tlnN \t1.02 \t1.02\n')
    #fout.write('sig_effUnc \tlnN \t1.15 \t-\n')
    #fout.write('bkg_shapeUnc \tlnN \t- \t1.2\n')

    print 'Created ' + datacard

