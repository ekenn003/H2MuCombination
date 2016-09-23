# H2Mu combination
Set up combination tool:
    export SCRAM_ARCH=slc6_amd64_gcc491
    cmsrel CMSSW_7_4_7
    cd CMSSW_7_4_7/src 
    cmsenv
    git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
    cd HiggsAnalysis/CombinedLimit
    git fetch origin
    git checkout v6.3.0
    scramv1 b clean
    scramv1 b -j 8

Check out code:
    git clone
