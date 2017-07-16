#!/usr/bin/env python
import os, sys
#from prettytable import PrettyTable
from ROOT import *
from tools.tools import get_mc_info

main_data_dir  = '{0}/src/H2MuCombination/data'.format(os.environ['CMSSW_BASE'])
shape_data_dir = '{0}/src/H2MuCombination/Shape/data'.format(os.environ['CMSSW_BASE'])
input_file_head = 'ana_2Mu_'
input_file_tail = '.root'

# categories
cats = ['cat'+str(i).zfill(2) for i in xrange(16)]
# signal processes
sp = ['VBF', 'GluGlu', 'WMinusH', 'WPlusH', 'ZH']

## ____________________________________________________________________________
def get_signal_rate_map(lumi):
    # rate map
    rates = {}
    rates_err = {}
    for p in sp:
        rates[p] = {}
        rates_err[p] = {}

    # acceptance map
    acc = {}
    for p in sp:
        acc[p] = {}

    # filenames and tfiles
    fnames = {}
    tf = {}
    for p in sp:
        fnames[p] = '{0}/{1}{2}_HToMuMu{3}'.format(main_data_dir,
            input_file_head, p, input_file_tail)
        try:
            tf[p] = TFile.Open(fnames[p])
        except:
            print 'Error opening input files'
            return

    # sum weights / xsec for each sample
    nsw = {
        'VBF'     : 249200,
        'GluGlu'  : 250000,
        'WMinusH' : 125000,
        'WPlusH'  : 124547,
        'ZH'      : 249748,
    }
    xsc = {}
    #nsw = {}
    for p in sp:
        xsc[p] = float(get_mc_info(tf[p])[0])
        #nsw[p] = float(get_mc_info(tf[p])[1])

    # get rates for each category
    for cat in cats:
        for p in sp:
            h = TH1F(tf[p].Get('categories/hDiMuInvMass_'+cat))
            num = h.Integral()
            thiserr = Double(0.)
            h.IntegralAndError(h.GetXaxis().FindBin(120.),
                h.GetXaxis().FindBin(130.) , thiserr)
            num_e = thiserr
            den = nsw[p]
            acc[p][cat] = num/den
            rates[p][cat]     = (num/den) * lumi * (xsc[p])
            rates_err[p][cat] = (num_e/den) * lumi * (xsc[p])
            #print
            #print p, cat, 'acceptance =', acc[p][cat]

    for cat in cats:
        e1 = rates_err['WMinusH'][cat]
        e2 = rates_err['WPlusH'][cat]
        e3 = rates_err['ZH'][cat]
        e4 = rates_err['VBF'][cat]
        e5 = rates_err['GluGlu'][cat]
        thise = TMath.Sqrt(e1**2 + e2**2 + e3**2 + e4**2 + e5**2)
        #print cat, '\pm'+str(thise)

    return rates, rates_err



## ____________________________________________________________________________
def ugly_print_yields(lumi):
    # print expected signal yields 
    r, e = get_signal_rate_map(lumi)

    #ytab = PrettyTable(['Category', 'VBF', 'ggH', 'VH', 'Total'])
    #ytab.align = 'c'
    ugly_table = []
    uglier_table = []

    y_vbf_all = 0.
    y_ggh_all = 0.
    y_vh_all = 0.
    y_tot_all = 0.

    e2_vbf_all = 0.
    e2_ggh_all = 0.
    e2_vh_all = 0.
    e2_tot_all = 0.

    print
    ugly_table.append('Cat.      VBF                  ggH                  '
                      'VH                   Total')
    for c in ['cat'+str(i).zfill(2) for i in xrange(1,16)]:
        y_vbf = r['VBF'][c]
        y_ggh = r['GluGlu'][c]
        y_vh  = r['ZH'][c] + r['WMinusH'][c] + r['WPlusH'][c]

        e_vbf = e['VBF'][c]
        e_ggh = e['GluGlu'][c]
        e_vh  = TMath.Sqrt((e['ZH'][c])**2 + (e['WMinusH'][c])**2
            + (e['WPlusH'][c])**2)

        y_tot = y_vbf + y_ggh + y_vh
        e_tot = TMath.Sqrt((e['ZH'][c])**2 + (e['WMinusH'][c])**2
            + (e['WPlusH'][c])**2 + e_vbf**2 + e_ggh**2)


        y_vbf_all += y_vbf
        y_ggh_all += y_ggh
        y_vh_all  += y_vh
        y_tot_all += y_tot

        e2_vbf_all += e_vbf**2
        e2_ggh_all += e_ggh**2
        e2_vh_all  += (e['ZH'][c])**2 + (e['WMinusH'][c])**2 + (e['WPlusH'][c])**2
        e2_tot_all += ((e['ZH'][c])**2 + (e['WMinusH'][c])**2
            + (e['WPlusH'][c])**2 + e_vbf**2 + e_ggh**2)

        y_vbf_ = str(y_vbf)[:5]
        e_vbf_ = str(e_vbf)[:5]
        y_ggh_ = str(y_ggh)[:5]
        e_ggh_ = str(e_ggh)[:5]
        y_vh_  = str(y_vh)[:5]
        e_vh_  = str(e_vh)[:5]
        y_tot_ = str(y_tot)[:5]
        e_tot_ = str(e_tot)[:5]


        ugly_table.append(('{0}     '
            '{1} +/- {2}    {3} +/- {4}    '
            '{5} +/- {6}    {7} +/- {8}').format(c, y_vbf_, e_vbf_, y_ggh_,
                e_ggh_, y_vh_, e_vh_, y_tot_, e_tot_))

        uglier_table.append(('{0}                              & $'
            '{1}\pm{2}$                 & ${3}\pm{4}$                 & $'
            '{5}\pm{6}$                 & ${7}\pm{8}$  \\\\').format(c, y_vbf_, e_vbf_, y_ggh_,
                e_ggh_, y_vh_, e_vh_, y_tot_, e_tot_))

#        uglier_table.append(c+'     ' \
#            + str(y_vbf)[:6] + ' +/- ' + str(e_vbf)[:6]+'    ' \
#            + str(y_ggh)[:6] + ' +/- ' + str(e_ggh)[:6]+'    ' \
#            + str(y_vh)[:6]  + ' +/- ' + str(e_vh)[:6]+'    ' \
#            + str(y_tot)[:6] + ' +/- ' + str(e_tot)[:6])
#
#cat07                              & $1.1515\pm0.0110$                 & $16.690\pm0.1448$                 & $0.6749\pm0.0049$                 & $18.517\pm0.1453$  \\
#

    y_vbf_all_ = str(y_vbf_all)[:5]
    e_vbf_all_ = str(TMath.Sqrt(e2_vbf_all))[:5]
    y_ggh_all_ = str(y_ggh_all)[:5]
    e_ggh_all_ = str(TMath.Sqrt(e2_ggh_all))[:5]
    y_vh_all_  = str(y_vh_all)[:5]
    e_vh_all_  = str(TMath.Sqrt(e2_vh_all))[:5]
    y_tot_all_ = str(y_tot_all)[:5]
    e_tot_all_ = str(TMath.Sqrt(e2_tot_all))[:5]


    ugly_table.append(('{0}     '
        '{1} +/- {2}    {3} +/- {4}    '
        '{5} +/- {6}    {7} +/- {8}').format('Total', y_vbf_all_, e_vbf_all_, y_ggh_all_,
            e_ggh_all_, y_vh_all_, e_vh_all_, y_tot_all_, e_tot_all_))

    uglier_table.append('\hline')
    uglier_table.append(('\\textbf{{Total}}                     & $'
        '{1}\pm{2}$                 & ${3}\pm{4}$                 & $'
        '{5}\pm{6}$                 & ${7}\pm{8} $   \\\\').format('dingus',
            y_vbf_all_, e_vbf_all_, y_ggh_all_,
            e_ggh_all_, y_vh_all_, e_vh_all_, y_tot_all_, e_tot_all_))
    uglier_table.append('\hline')



    for l in ugly_table:
        print l

    print
    print
    for l in uglier_table:
        print l














    #print ytab.get_string()


## ____________________________________________________________________________
try:
    m = get_signal_rate_map(35860)

except KeyboardInterrupt:
    print


