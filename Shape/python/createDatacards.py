# produces datacards in an existing directory named 'Datacards'
# this only works for a single bin right now
import os, sys
from ROOT import *
from systematics import get_systematics_map
from acceptances import get_signal_rate_map

# this CMSSW_BASE is written into the dcard so it doesn't have to be expanded
#main_data_dir  = '$CMSSW_BASE/src/H2MuCombination/data'.format(os.environ['CMSSW_BASE'])
main_data_dir  = '$CMSSW_BASE/src/H2MuCombination/data'
shape_data_dir = '$CMSSW_BASE/src/H2MuCombination/Shape/data'
lhc_hxswg_dir = '$CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/data/lhc-hxswg/sm/'

wspace_name = 'mumu'

signal_model = 'double'

lumi = '36460.'

#include_sys = True
include_sys = False

r = get_signal_rate_map(float(lumi))
u = get_systematics_map()


#################################################
# bin information (single category)
#################################################
# bins
cats = ['cat'+str(i).zfill(2) for i in xrange(1,15+1)]
cats_01jet_tight = ['cat'+str(i).zfill(2) for i in xrange(4,9+1)]
cats_01jet_loose = ['cat'+str(i).zfill(2) for i in xrange(10,15+1)]
cats_2jet  = ['cat'+str(i).zfill(2) for i in xrange(1,3+1)]
cats_01jet = ['cat'+str(i).zfill(2) for i in xrange(4,15+1)]



# input shapes file (has to be in main data directory)
shape_file = shape_data_dir+'/workspace_allcats_'+signal_model+'Gaus.root'


for cat in cats:
    # output datacard name
    #datacard = 'Datacards/DataCard_HToMuMu_2Mu_13TeV_2016Analysis.txt'
    datacard = 'Datacards/datacard_'+cat+'_'+signal_model+'Gaus.txt'
    
    
    #################################################
    # write datacard
    #################################################
    delim = '-'*70+'\n'
    with open(datacard, 'w') as fout:
        fout.write('imax \t1 \tnumber of channels (i.e. cats/bins) \n')
        fout.write('jmax \t5 \tnumber of processes minus one \n')
        fout.write('kmax \t* \tnumber of nuisance parameters '
            '(sources of systematic uncertainties) \n')
        fout.write(delim)
        fout.write('bin \t\t{0} \n'.format(cat))
        fout.write('observation \t-1 \n')
        fout.write(delim)
        fout.write(('shapes data_obs * {0}'
            '\t{1}:data_obs_$CHANNEL\n').format(shape_file, wspace_name))
        fout.write(('shapes BKG      * {0}'
            '\t{1}:bkg_model_$CHANNEL\n').format(shape_file, wspace_name))
        fout.write(('shapes *        * {0}'
            '\t{1}:sig_model_$CHANNEL_$PROCESS\n').format(
                shape_file, wspace_name))
        fout.write(delim)
        fout.write('bin\t{0}\n'.format(('\t\t'+cat)*6))
        fout.write('process\t\t\tBKG\t\tVBF\t\tGluGlu\t\tWPlusH\t\tWMinusH\t\tZH\n')
        fout.write('process\t\t\t1\t\t0\t\t-1\t\t-2\t\t-3\t\t-4\n')
        #fout.write('rate\t\t\t1{0}\n'.format(('\t\t'+lumi)*5))
        fout.write('rate\t\t\t1\t')
        fout.write('\t'+str(r['VBF'][cat]))
        fout.write('\t'+str(r['GluGlu'][cat]))
        fout.write('\t'+str(r['WMinusH'][cat]))
        fout.write('\t'+str(r['WPlusH'][cat]))
        fout.write('\t'+str(r['ZH'][cat]))
        fout.write('\n')
        fout.write(delim)
    
        # systematics
        if include_sys:
            for s in u:
                fout.write(s)
                if len(s) < 8: fout.write('\t')
                fout.write('\tlnN')
                fout.write('\t'+u[s]['BKG'][cat])
                fout.write('\t'+u[s]['VBF'][cat])
                fout.write('\t'+u[s]['GluGlu'][cat])
                fout.write('\t'+u[s]['WPlusH'][cat])
                fout.write('\t'+u[s]['WMinusH'][cat])
                fout.write('\t'+u[s]['ZH'][cat])
                fout.write('\n')
    
            fout.write('\n')
        print 'Created', datacard

# combine them

# total combo
comb_command = 'combineCards.py '
for cat in cats:
    comb_command += '{c}=datacard_{c}_{sm}Gaus.txt '.format(c=cat, sm=signal_model)
comb_command += '> datacard_comb_tot_{sm}Gaus.txt'.format(sm=signal_model)

# 2jet combo
comb_2jet_command = 'combineCards.py '
for cat in cats_2jet:
    comb_2jet_command += '{c}=datacard_{c}_{sm}Gaus.txt '.format(c=cat, sm=signal_model)
comb_2jet_command += '> datacard_comb_2jet_{sm}Gaus.txt'.format(sm=signal_model)

# 01jet combo
comb_01jet_command = 'combineCards.py '
for cat in cats_01jet:
    comb_01jet_command += '{c}=datacard_{c}_{sm}Gaus.txt '.format(c=cat, sm=signal_model)
comb_01jet_command += '> datacard_comb_01jet_{sm}Gaus.txt'.format(sm=signal_model)

# 01jet_tight combo
comb_01jet_tight_command = 'combineCards.py '
for cat in cats_01jet_tight:
    comb_01jet_tight_command += '{c}=datacard_{c}_{sm}Gaus.txt '.format(c=cat, sm=signal_model)
comb_01jet_tight_command += '> datacard_comb_01jet_tight_{sm}Gaus.txt'.format(sm=signal_model)

# 01jet_loose combo
comb_01jet_loose_command = 'combineCards.py '
for cat in cats_01jet_loose:
    comb_01jet_loose_command += '{c}=datacard_{c}_{sm}Gaus.txt '.format(c=cat, sm=signal_model)
comb_01jet_loose_command += '> datacard_comb_01jet_loose_{sm}Gaus.txt'.format(sm=signal_model)




os.chdir('Datacards')
os.system(comb_command)
os.system(comb_2jet_command)
os.system(comb_01jet_command)
os.system(comb_01jet_tight_command)
os.system(comb_01jet_loose_command)
os.chdir('..')

print 'Created Datacards/datacard_comb_tot_{sm}Gaus.txt'.format(sm=signal_model)
print 'Created Datacards/datacard_comb_2jet_{sm}Gaus.txt'.format(sm=signal_model)
print 'Created Datacards/datacard_comb_01jet_{sm}Gaus.txt'.format(sm=signal_model)
print 'Created Datacards/datacard_comb_01jet_tight_{sm}Gaus.txt'.format(sm=signal_model)
print 'Created Datacards/datacard_comb_01jet_loose_{sm}Gaus.txt'.format(sm=signal_model)






