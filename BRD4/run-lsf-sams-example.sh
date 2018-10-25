#!/usr/bin/env bash
# Set walltime limit
#BSUB -W 5:59
#
# Set output file
#BSUB -o sams_example.%J.log
#
# Specify node group
#BSUB -m "lt-gpu"
##BSUB -m "ls-gpu lt-gpu lp-gpu lg-gpu"
#BSUB -q gpuqueue
#
# nodes: number of nodes and GPU request
#BSUB -n 4
#BSUB -gpu "num=4:j_exclusive=yes:mode=shared" -R "rusage[mem=36] span[ptile=4]"
#
# job name (default = name of script file)
#BSUB -J "sams_example"

build_mpirun_configfile --hostfilepath hostfile.${LSB_JOBNAME} --configfilepath configfile.${LSB_JOBNAME} "yank script --yaml=${LSB_JOBNAME}.yaml"
mpiexec.hydra -f hostfile.${LSB_JOBNAME} -configfile configfile.${LSB_JOBNAME}
