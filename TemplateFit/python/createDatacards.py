# produces datacards in an existing directory named 'Datacards'
# this only works for a single bin right now
import os, sys
from ROOT import *

datadir = '{0}/src/H2MuCombination/data'.format(os.environ['CMSSW_BASE'])

#################################################
# shapes file (has to be in data directory
#################################################
shapefile = 'test.root'

#################################################
# output datacard name
#################################################
datacard = 'Datacards/DataCard_HToMuMu_2Mu_13TeV_2016Analysis.txt'

#################################################
# channels
#################################################
binname = 'mm'

sigProcesses = ['sigVBF', 'sigGGF']
bkgProcesses = ['bkgTTJ', 'bkgDYJ']

# systematic = (name, shape, signal, background)
# still working on how to do this for only a single channel
systematics = []
# 13 tev luminosity
systematics += [('lumi_13TeV',   'lnN', '1.02', '1.02')]
systematics += [('sig_effUnc',   'lnN', '1.15', '-')]
systematics += [('bkg_shapeUnc', 'lnN', '-',    '1.20')]



# include data yield? (False for expected/blinded; if True, must have data_obs in shapefile)
includeData = False
#includeData = True





#################################################
#################################################
f0 = TFile.Open('{0}/{1}'.format(datadir, shapefile))

nSigs = len(sigProcesses)
nBkgs = len(bkgProcesses)
nNuis = len(systematics)


# fill rates
rates = []
for p in sigProcesses+bkgProcesses:
    rate = TH1F(f0.Get(p)).Integral()
    rates.append(rate)

if includeData:
    data_yield = TH1F(f0.Get('data_obs')).Integral()
else:
    data_yield = -1

#################################################
# write datacard
#################################################
with open(datacard, 'w') as fout:
    fout.write('imax \t{1 \tnumber of channels (1 for now)\n')
    fout.write('jmax \t{0} \tnumber of backgrounds \n'.format(nBkgs))
    fout.write('kmax \t{0} \tnumber of nuisance parameters (sources of systematic uncertainties) \n'.format(nNuis))
    fout.write('--------------------------\n')
    fout.write('bin \t{0} \n'.format(binname))
    fout.write('observation \t{0} \n'.format(data_yield))
    fout.write('--------------------------\n')
    fout.write('shapes \t*  \t{0} \tdata/{1} \t$PROCESS\n'.format(binname, shapefile))
    fout.write('--------------------------\n')

    fout.write('bin\t')
    for i in range(nSigs+nBkgs):
        fout.write('\t\t{0}'.format(binname))
    fout.write('\n')

    fout.write('process\t')
    for p in sigProcesses+bkgProcesses:
        fout.write('\t\t{0}'.format(p))
    fout.write('\n')

    fout.write('process\t')
    for i in range(1-nSigs,nBkgs+1,1):
        fout.write('\t\t{0}'.format(i))
    fout.write('\n')

    fout.write('rate\t\t')
    for r in rates:
        fout.write('\t{0}'.format(r))
    fout.write('\n')
    fout.write('--------------------------\n')

    for s in systematics:
        fout.write(s[0]+'\t'+s[1])
        for sp in sigProcesses:
            fout.write('\t'+s[2]+'\t')
        for bp in bkgProcesses:
            fout.write('\t'+s[3]+'\t')
        fout.write('\n')

    print 'Created ' + datacard

