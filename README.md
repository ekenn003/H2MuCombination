# H2Mu combination + limits

Install combine tool

    export SCRAM_ARCH=slc6_amd64_gcc491
    cmsrel CMSSW_7_4_7
    cd CMSSW_7_4_7/src 
    cmsenv
    git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
    cd HiggsAnalysis/CombinedLimit
    git fetch origin
    git checkout v6.3.0
    scramv1 b clean
    scramv1 b

Check out code

    cd $CMSSW_BASE/src/
    git clone https://github.com/ekenn003/H2MuCombination.git
    #git clone git@github.com:ekenn003/H2MuCombination.git

Create datacards

    mkdir Datacards
    python createDatacards.py

Test

    combine -M Asymptotic Datacards/Datacard2.txt -H ProfileLikelihood --picky

