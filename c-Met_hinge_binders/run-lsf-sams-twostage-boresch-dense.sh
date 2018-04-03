#!/usr/bin/env bash
# Set walltime limit
#BSUB -W 05:59
#
# Set output file
#BSUB -o hinge-sams-boresch-dense.%J.log
#
# Specify node group
#BSUB -m "ls-gpu lt-gpu lp-gpu lg-gpu"
#BSUB -q gpuqueue
#
# nodes: number of nodes and GPU request
#BSUB -n 12 -R "{span[ptile=1] rusage[mem=8]} || {span[ptile=2] rusage[mem=8]} || {span[ptile=3] rusage[mem=8]} || {span[ptile=4] rusage[mem=8]}"
#BSUB -gpu "num=1:j_exclusive=yes:mode=shared"
#
# job name (default = name of script file)
#BSUB -J "hinge-sams-boresch-dense"

build_mpirun_configfile "yank script --yaml=sams-twostage-boresch-dense.yaml"
mpiexec.hydra -f hostfile -configfile configfile
