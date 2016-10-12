# produces datacards in an existing directory named 'Datacards'
# this only works for a single bin right now
import os, sys
from ROOT import *

main_data_dir  = '{0}/src/H2MuCombination/data'.format(os.environ['CMSSW_BASE'])
shape_data_dir = '{0}/src/H2MuCombination/Shape/data'.format(os.environ['CMSSW_BASE'])

# shapes file (has to be in main data directory)
shape_file = 'p.root'
wspace_name = 'mumu'

# output datacard name
datacard = 'Datacards/DataCard_HToMuMu_2Mu_13TeV_2016Analysis.txt'

# processes
bin_name = 'mm'

sig_processes = ['sigVBF', 'sigGGF']
bkg_processes = ['bkgTTJ', 'bkgDYJ']

# systematic = (name, shape, signal, background)
# fit parameters in Shape/scripts/prepareShapesFile.py
fit_params = []
# signal
fit_params += [('mean',   'param', '0.1', '0.0')]
fit_params += [('sigma1', 'param', '0.1', '0.0')]
fit_params += [('sigma1', 'param', '0.1', '0.0')]
# background
fit_params += [('lambda1', 'param', '0.0', '0.1')]


# include data yield? (False for expected/blinded; if True, must have data_obs in shape_file)
include_data = False
#include_data = True





#################################################
#################################################
f0 = TFile.Open('{0}/{1}'.format(shape_data_dir, shape_file))

n_sigs = len(sig_processes)
n_bkgs = len(bkg_processes)
#n_nuis = len(systematics)
n_params = len(fit_params)


# fill rates
sig_rate = 0.
bkg_rate = 0.
for p in sig_processes:
    sig_rate += TH1F(f0.Get(p)).Integral()
for p in bkg_processes:
    bkg_rate += TH1F(f0.Get(p)).Integral()

if include_data:
    data_yield = TH1F(f0.Get('data_obs')).Integral()
else:
    data_yield = -1

#################################################
# write datacard
#################################################
with open(datacard, 'w') as fout:
    fout.write('imax \t1 \tnumber of channels (1 for now)\n')
    fout.write('jmax \t* \tnumber of backgrounds \n')
    fout.write('kmax \t* \tnumber of nuisance parameters (sources of systematic uncertainties) \n')
    fout.write('--------------------------\n')
    fout.write('bin \t{0} \n'.format(bin_name))
    fout.write('observation \t{0} \n'.format(data_yield))
    fout.write('--------------------------\n')
    fout.write('shapes \t*  \t{0} \tdata/{1} \t{2}:$PROCESS\n'.format(bin_name, shape_file, wspace_name))
    fout.write('--------------------------\n')

    fout.write('bin')
    for i in range(2):
        fout.write('\t\t{0}'.format(bin_name))
    fout.write('\n')

    fout.write('process\t')
    #for p in sig_processes+bkg_processes:
    #    fout.write('\t\t{0}'.format(p))
    fout.write('\tsig_model')
    fout.write('\tbkg_model')
    fout.write('\n')

    fout.write('process')
    for i in range(2):
        fout.write('\t\t{0}'.format(i))
    fout.write('\n')

    fout.write('rate\t')
    fout.write('\t{0}'.format(sig_rate))
    fout.write('\t{0}'.format(bkg_rate))
    fout.write('\n')
    fout.write('--------------------------\n')

    for p in fit_params:
        fout.write(p[0]+'\t'+p[1]+'\t'+p[2]+'\t\t'+p[3]+'\t')
        fout.write('\n')
    #for s in systematics:
    #    fout.write(s[0]+'\t'+s[1])
    #    for sp in sig_processes:
    #        fout.write('\t'+s[2]+'\t')
    #    for bp in bkg_processes:
    #        fout.write('\t'+s[3]+'\t')
    #    fout.write('\n')

    print 'Created ' + datacard

