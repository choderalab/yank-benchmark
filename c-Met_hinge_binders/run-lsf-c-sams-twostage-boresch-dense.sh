#!/usr/bin/env bash
# Set walltime limit
#BSUB -W 05:59
#
# Set output file
#BSUB -o hinge-c-sams-boresch-dense.%J.log
#
# Specify node group
#BSUB -m "ls-gpu lt-gpu lp-gpu lg-gpu"
#BSUB -q gpuqueue
#
# nodes: number of nodes and GPU request
#BSUB -n 13
#BSUB -gpu "j_exclusive=yes:mode=shared"
#BSUB -R "{rusage[mem=12,ngpus_physical=2] span[ptile=2]} || {rusage[mem=12,ngpus_physical=3] span[ptile=3]} || {rusage[mem=12,ngpus_physical=4] span[ptile=4]} || {rusage[mem=12,ngpus_physical=1] span[ptile=1]}"
#
# job name (default = name of script file)
#BSUB -J "hinge-c-sams-boresch-dense"

build_mpirun_configfile --hostfilepath hostfile.sams.bored --configfilepath configfile.sams.bored "yank script --yaml=charge-sams-twostage-boresch-dense.yaml"
mpiexec.hydra -f hostfile.sams.bored -configfile configfile.sams.bored
