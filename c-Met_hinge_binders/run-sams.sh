#!/usr/bin/env bash
# Set walltime limit
#BSUB -W 72:00
#
# Set output file
#BSUB -o cMet-sams.%J.log
#
# Specify node group
#BSUB -m "ls-gpu lt-gpu lp-gpu lg-gpu"
#BSUB -q gpuqueue
#
# nodes: number of nodes and GPU request
#BSUB -n 12
#BSUB -gpu "num=4:j_exclusive=yes:mode=shared" -R "rusage[mem=36] span[ptile=4]"
#
# job name (default = name of script file)
#BSUB -J "cMet-sams"

build_mpirun_configfile --hostfilepath hostfile.${LSB_JOBNAME} --configfilepath configfile.${LSB_JOBNAME} "python run_yank.py --yaml=${LSB_JOBNAME}.yaml"
mpiexec.hydra -f hostfile.${LSB_JOBNAME} -configfile configfile.${LSB_JOBNAME}
