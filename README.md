This is a simplest running example to get limits from higgs combine with a parametric shape fit

    # Install Higgs Combine correctly
    # https://twiki.cern.ch/twiki/bin/viewauth/CMS/SWGuideHiggsAnalysisCombinedLimit#GIT_recipe_the_only_supported_re
    export SCRAM_ARCH=slc6_amd64_gcc491
    cmsrel CMSSW_7_4_7
    cd CMSSW_7_4_7/src
    cmsenv
    git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
    cd HiggsAnalysis/CombinedLimit
    git checkout v6.2.1
    cd ../../
    scram b -j 8

    # check out code
    git clone https://github.com/ekenn003/ProtoCombination.git
    #git clone git@github.com:ekenn003/ProtoCombination.git
    cd ProtoCombination
    
    # use prototype .py to create pdfs, workspaces, roohist for "data" and save into p.root that the datacard uses
    python prototype.py
    
    # ok now test out higgs combine
    combine -M Asymptotic datacard.txt -H ProfileLikelihood --picky

