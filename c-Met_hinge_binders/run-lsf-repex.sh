#!/usr/bin/env bash
# Set walltime limit
#BSUB -W 72:00
#
# Set output file
#BSUB -o  c-met-hinge-repex.%J.log
#
# Specify node group
#BSUB -m "ls-gpu lt-gpu"
#BSUB -q gpuqueue
#
# nodes: number of nodes and GPU request
#BSUB -n 12 -R "rusage[mem=12]"
#BSUB -gpu "num=1:j_exclusive=yes:mode=shared"
#
# job name (default = name of script file)
#BSUB -J "c-met-hinge-repex"

build_mpirun_configfile "yank script --yaml=repex-twostage.yaml"
mpiexec.hydra -f hostfile -configfile configfile
