#!/usr/bin/env bash
# Set walltime limit
#BSUB -W 05:59
#
# Set output file
#BSUB -o  c-met-hinge-repex-dense.%J.log
#
# Specify node group
#BSUB -m "ls-gpu lt-gpu lp-gpu lg-gpu"
#BSUB -q gpuqueue
#
# nodes: number of nodes and GPU request
#BSUB -n 12
#BSUB -gpu "j_exclusive=yes:mode=shared"
#BSUB -R "{rusage[mem=12,ngpus_physical=2] span[ptile=2]} || {rusage[mem=12,ngpus_physical=3] span[ptile=3]} || {rusage[mem=12,ngpus_physical=4] span[ptile=4]} || {rusage[mem=12,ngpus_physical=1] span[ptile=1]}"
#
# job name (default = name of script file)
#BSUB -J "c-met-hinge-repex-dense"

build_mpirun_configfile --hostfilepath hostfile.repex.bored --configfilepath configfile.repex.bored "yank script --yaml=repex-twostage-boresch-dense.yaml"
mpiexec.hydra -f hostfile.repex.bored -configfile configfile.repex.bored
