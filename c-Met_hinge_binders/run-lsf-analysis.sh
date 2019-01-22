#!/usr/bin/env bash
# Set walltime limit
#BSUB -W 5:59
#
# Set output file
#BSUB -o cMet-analyze-6.%J.log
#
# Specify node group
#BSUB -m "ls-gpu lt-gpu lp-gpu lg-gpu"
#BSUB -q cpuqueue
#
# nodes: number of nodes and GPU request
#BSUB -n 16
##BSUB -gpu "num=1:j_exclusive=yes:mode=shared"
#BSUB -R "rusage[mem=24] span[ptile=16]" 
#
# job name (default = name of script file)
#BSUB -J "cMet-analyze-6"

YAMLNAME="cMet-repex-6"
mpirun -np 16 yank analyze --skipunbiasing --yaml ${YAMLNAME}.yaml --serial=analysis-${YAMLNAME}.pkl
mpirun -np 16 yank analyze report --skipunbiasing --yaml ${YAMLNAME}.yaml --output reports-${YAMLNAME}

YAMLNAME="cMet-sams-6"
mpirun -np 16 yank analyze --skipunbiasing --yaml ${YAMLNAME}.yaml --serial=analysis-${YAMLNAME}.pkl
mpirun -np 16 yank analyze report --skipunbiasing --yaml ${YAMLNAME}.yaml --output reports-${YAMLNAME}



