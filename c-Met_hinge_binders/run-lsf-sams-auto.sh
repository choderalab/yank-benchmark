#!/usr/bin/env bash
# Set walltime limit
#BSUB -W 05:59
#
# Set output file
#BSUB -o  c-met-hinge-sams-auto.%J.log
#
# Specify node group
#BSUB -m "ls-gpu lt-gpu lp-gpu lg-gpu"
#BSUB -q gpuqueue
#
# nodes: number of nodes and GPU request
#BSUB -n 12 -R "rusage[mem=12]"
#BSUB -gpu "num=1:j_exclusive=yes:mode=shared"
#
# job name (default = name of script file)
#BSUB -J "c-met-hinge-sams-auto"

build_mpirun_configfile "yank script --yaml=sams-twostage-auto.yaml"
mpiexec.hydra -f hostfile -configfile configfile
