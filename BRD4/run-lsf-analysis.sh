#!/usr/bin/env bash
# Set walltime limit
#BSUB -W 5:59
#
# Set output file
#BSUB -o analyze.%J.log
#
# Specify node group
#BSUB -m "ls-gpu lt-gpu lp-gpu lg-gpu"
#BSUB -q gpuqueue
#
# nodes: number of nodes and GPU request
#BSUB -n 1
#BSUB -gpu "num=1:j_exclusive=yes:mode=shared"
#BSUB -R "rusage[mem=48]"
#
# job name (default = name of script file)
#BSUB -J "BRD4-analyze-2"

YAMLNAME="BRD4-sams-2"

yank analyze --yaml ${YAMLNAME}.yaml --serial=analysis-${YAMLNAME}.pkl
yank analyze report --yaml ${YAMLNAME}.yaml --output reports-${YAMLNAME}
