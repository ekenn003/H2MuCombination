# produces datacards in an existing directory named 'Datacards'
# this only works for a single bin right now
import os, sys
from ROOT import *
from systematics import unc_map as u

main_data_dir  = '{0}/src/H2MuCombination/data'.format(os.environ['CMSSW_BASE'])
shape_data_dir = '{0}/src/H2MuCombination/Shape/data'.format(os.environ['CMSSW_BASE'])
# this CMSSW_BASE is written into the dcard so it doesn't have to be expanded
lhc_hxswg_dir = '$CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/data/lhc-hxswg/sm/'

wspace_name = 'mumu'

# output datacard name
datacard = 'Datacards/DataCard_HToMuMu_2Mu_13TeV_2016Analysis.txt'

# processes

sig_processes = ['VBF', 'GluGlu', 'WPlusH', 'WMinusH', 'ZH']

lumi = '36460.'




#################################################
# bin information (single category)
#################################################

cat = 'cat00' # this is aka the bin name
# shapes file (has to be in main data directory)
shape_file = 'workspace_{0}_tripleGaus.root'.format(cat)


#################################################
#################################################
#f0 = TFile.Open('{0}/{1}'.format(shape_data_dir, shape_file))


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
    fout.write(('shapes data_obs * data/{0}'
        '\t{1}:data_obs_$CHANNEL\n').format(shape_file, wspace_name))
    fout.write(('shapes BKG      * data/{0}'
        '\t{1}:bkg_model_$CHANNEL\n').format(shape_file, wspace_name))
    fout.write(('shapes *        * data/{0}'
        '\t{1}:sig_model_$CHANNEL_$PROCESS\n').format(
            shape_file, wspace_name))
    fout.write(delim)
    fout.write('bin\t{0}\n'.format(('\t\t'+cat)*6))
    fout.write('process\t\t\tBKG\t\tVBF\t\tGluGlu\t\tWPlusH\t\tWMinusH\t\tZH\n')
    fout.write('process\t\t\t1\t\t0\t\t-1\t\t-2\t\t-3\t\t-4\n')
    fout.write('rate\t\t\t1{0}\n'.format(('\t\t'+lumi)*5))
    fout.write(delim)
    #
    fout.write(('hmm           rateParam * VBF     '+lhc_hxswg_dir
                +'sm_br_yr4.root:br\n'))
    fout.write(('vbfH_13TeV    rateParam * VBF     '+lhc_hxswg_dir
                +'sm_yr4_13TeV.root:xs_13TeV\n'))
    fout.write(('hmm           rateParam * GluGlu  '+lhc_hxswg_dir
                +'sm_br_yr4.root:br\n'))
    fout.write(('ggH_13TeV     rateParam * GluGlu  '+lhc_hxswg_dir
                +'sm_yr4_13TeV.root:xs_13TeV\n'))
    fout.write(('hmm           rateParam * WPlusH  '+lhc_hxswg_dir
                +'sm_br_yr4.root:br\n'))
    fout.write(('WplusH_13TeV  rateParam * WPlusH  '+lhc_hxswg_dir
                +'sm_yr4_13TeV.root:xs_13TeV\n'))
    fout.write(('hmm           rateParam * WMinusH '+lhc_hxswg_dir
                +'sm_br_yr4.root:br\n'))
    fout.write(('WminusH_13TeV rateParam * WMinusH '+lhc_hxswg_dir
                +'sm_yr4_13TeV.root:xs_13TeV\n'))
    fout.write(('hmm           rateParam * ZH      '+lhc_hxswg_dir
                +'sm_br_yr4.root:br\n'))
    fout.write(('ZH_13TeV      rateParam * ZH      '+lhc_hxswg_dir
                +'sm_yr4_13TeV.root:xs_13TeV\n'))
    fout.write(delim)


    # systemtics
    for s in u:
        fout.write(s+'\tlnN\t')
        fout.write(u[s]['BKG']+'\t')
        fout.write(u[s]['VBF']+'\t')
        fout.write(u[s]['GluGlu']+'\t')
        fout.write(u[s]['WPlusH']+'\t')
        fout.write(u[s]['WMinusH']+'\t')
        fout.write(u[s]['ZH'])





        fout.write('\n')




    fout.write('\n')
    print 'Created ' + datacard
















