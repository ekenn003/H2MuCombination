from ROOT import *

f0 = TFile.Open('data/simulated_mass_distribution.root')

xlow, xhigh = 60., 200.

h_sigVBF = f0.Get('histos/dimuMass_VBF')
b_h_sigVBF = h_sigVBF.GetBinWidth(h_sigVBF.FindBin(xlow))
h_sigGGF = f0.Get('histos/dimuMass_GGF')
b_h_sigGGF = h_sigGGF.GetBinWidth(h_sigGGF.FindBin(xlow))

h_bkgTTJ = f0.Get('histos/dimuMass_TTJets')
b_h_bkgTTJ = h_bkgTTJ.GetBinWidth(h_bkgTTJ.FindBin(xlow))
h_bkgDYJ = f0.Get('histos/dimuMass_DYJetsToLL')
b_h_bkgDYJ = h_bkgDYJ.GetBinWidth(h_bkgDYJ.FindBin(xlow))

h_data   = f0.Get('Mass')
b_h_data = h_data.GetBinWidth(h_data.FindBin(xlow))


binning = [b_h_sigVBF, b_h_sigGGF, b_h_bkgTTJ, b_h_bkgDYJ]

# check binning consistency
assert (len(set(binning))==1), 'Binning is not consistent'

print 'data integral = ' + str(h_data.Integral())
print 'sig VBF integral = ' + str(h_sigVBF.Integral())
print 'sig GGF integral = ' + str(h_sigGGF.Integral())
print 'bkg TTJ integral = ' + str(h_bkgTTJ.Integral())
print 'bkg DYJ integral = ' + str(h_bkgDYJ.Integral())
