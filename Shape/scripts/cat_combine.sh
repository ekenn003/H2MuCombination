#!/bin/bash

#rmax=90

run="both"
#run="expected"

#nosys="-S 0"
nosys=""

declare -a catsA=(
                "cat01" "cat02" "cat03" "cat04" "cat05" "cat06"
                "cat07" "cat08" "cat09" "cat10" "cat11" "cat12"
                "cat13" "cat14" "cat15"
                "comb_01jet_tight" "comb_01jet_loose"
                "comb_2jet" "comb_01jet"
                "comb_tot"
                )


declare -a catsB=(
                "comb_tot"
                )

for c in "${catsA[@]}"; do
#for c in "${catsB[@]}"; do

    echo
    echo "combine -M Asymptotic Datacards/datacard_${c}_doubleGaus.txt -m 125 --run=${run} -n \"_${c}\" ${nosys}"
    combine -M Asymptotic Datacards/datacard_${c}_doubleGaus.txt -m 125 --run=${run} --saveWorkspace -n "_${c}" ${nosys} -v 9

done






