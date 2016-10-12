# produces datacards in an existing directory named 'Datacards'
# this only works for a single bin right now
import os, sys
from ROOT import *

main_data_dir  = '{0}/src/H2MuCombination/data'.format(os.environ['CMSSW_BASE'])
template_data_dir = '{0}/src/H2MuCombination/Template/data'.format(os.environ['CMSSW_BASE'])

# shapes file (has to be in main data directory)
shape_file = 'test.root'

# output datacard name
datacard = 'Datacards/DataCard_HToMuMu_2Mu_13TeV_2016Analysis.txt'

# processes
bin_name = 'mm'

sig_processes = ['sigVBF', 'sigGGF']
bkg_processes = ['bkgTTJ', 'bkgDYJ']

# systematic = (name, shape, signal, background)
# still working on how to do this for only a single channel
systematics = []
# 13 tev luminosity
systematics += [('lumi_13TeV',   'lnN', '1.02', '1.02')]
systematics += [('sig_effUnc',   'lnN', '1.15', '-')]
systematics += [('bkg_shapeUnc', 'lnN', '-',    '1.20')]



# include data yield? (False for expected/blinded; if True, must have data_obs in shape_file)
include_data = False
#include_data = True





#################################################
#################################################
f0 = TFile.Open('{0}/{1}'.format(main_data_dir, shape_file))

n_sigs = len(sig_processes)
n_bkgs = len(bkg_processes)
n_nuis = len(systematics)


# fill rates
rates = []
for p in sig_processes+bkg_processes:
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
    fout.write('jmax \t{0} \tnumber of backgrounds \n'.format(n_bkgs))
    fout.write('kmax \t{0} \tnumber of nuisance parameters (sources of systematic uncertainties) \n'.format(n_nuis))
    fout.write('--------------------------\n')
    fout.write('bin \t{0} \n'.format(bin_name))
    fout.write('observation \t{0} \n'.format(data_yield))
    fout.write('--------------------------\n')
    fout.write('shapes \t*  \t{0} \tdata/{1} \t$PROCESS\n'.format(bin_name, shape_file))
    fout.write('--------------------------\n')

    fout.write('bin\t')
    for i in range(n_sigs+n_bkgs):
        fout.write('\t\t{0}'.format(bin_name))
    fout.write('\n')

    fout.write('process\t')
    for p in sig_processes+bkg_processes:
        fout.write('\t\t{0}'.format(p))
    fout.write('\n')

    fout.write('process\t')
    for i in range(1-n_sigs,n_bkgs+1,1):
        fout.write('\t\t{0}'.format(i))
    fout.write('\n')

    fout.write('rate\t\t')
    for r in rates:
        fout.write('\t{0}'.format(r))
    fout.write('\n')
    fout.write('--------------------------\n')

    for s in systematics:
        fout.write(s[0]+'\t'+s[1])
        for sp in sig_processes:
            fout.write('\t'+s[2]+'\t')
        for bp in bkg_processes:
            fout.write('\t'+s[3]+'\t')
        fout.write('\n')

    print 'Created ' + datacard

