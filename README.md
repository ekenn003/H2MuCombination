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

    # https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideHiggsAnalysisCombinedLimit#How_to_prepare_the_datacard
    cd TemplateFit # (or ShapeFit)
    python python/createDatacards.py

Expected/observed limits (upper limit on the signal strength)

    combine -M Asymptotic Datacards/Datacard2.txt -m 125 -H ProfileLikelihood --picky

Expected significance

    combine -d Datacards/Datacard2.txt -M ProfileLikelihood -v 1 --significance --expectSignal=1 -t -1 -m 125 -n Expected

Observed significance

    combine -d Datacards/Datacard2.txt -M ProfileLikelihood -v 1 --significance -m 125

Best fit signal strength with uncertainty

    combine -d Datacards/Datacard2.txt -M MaxLikelihoodFit -m 125

