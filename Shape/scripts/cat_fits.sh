#!/bin/bash


blind=""
#blind="--run=blind"

#nosys="-S 0"
nosys=""

declare -a catsA=(
                "cat01" "cat02" "cat03" "cat04" "cat05" "cat06"
                "cat07" "cat08" "cat09" "cat10" "cat11" "cat12"
                "cat13" "cat14" "cat15"
                "comb_tot"
                )
declare -a catsC=(
                "cat01" "cat02" "cat03" "cat04" "cat05" "cat06"
                "cat07" "cat08" "cat09" "cat10" "cat11" "cat12"
                "cat13" "cat14" "cat15"
                "comb_01jet_tight" "comb_01jet_loose"
                "comb_2jet" "comb_01jet"
                "comb_tot"
                )

declare -a catsB=(
                "cat02"
                )


for c in "${catsA[@]}"; do

    echo
    echo "combine -M MaxLikelihoodFit Datacards/datacard_${c}_doubleGaus.txt -m 125 -n \"_${c}\" --plots ${nosys}"
    combine -M MaxLikelihoodFit Datacards/datacard_${c}_doubleGaus.txt -m 125 -n "_${c}" --plots --out fitplots ${nosys}

done


