#!/usr/bin/env bash
#Walltime
#BSUB -W 72:00
#
# Set Output file
#BSUB -o  c-met-hinge-neutral.%J.log
#
# Specify node group
#BSUB -m "ls-gpu lt-gpu"
#BSUB -q gpuqueue
#
# nodes: number of nodes and GPU request
# 12 GPU's spread over 3 nodes
#BSUB -n 12 -R "rusage[mem=12] span[ptile=4]"
#BSUB -gpu "num=1:j_exclusive=yes:mode=shared"
#
# job name (default = name of script file)
#BSUB -J "c-met-hinge-neutral"

build_mpirun_configfile "yank script --yaml=explicit-all.yaml"
mpiexec.hydra -f hostfile -configfile configfile