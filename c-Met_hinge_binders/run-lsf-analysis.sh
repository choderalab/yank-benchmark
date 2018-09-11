#!/usr/bin/env bash
# Set walltime limit
#BSUB -W 5:59
#
# Set output file
#BSUB -o analyze.%J.log
#
# Specify node group
#BSUB -m "ls-gpu lt-gpu lp-gpu lg-gpu"
#BSUB -q cpuqueue
#
# nodes: number of nodes and GPU request
#BSUB -n 12
#BSUB -R "rusage[mem=48]"
#
# job name (default = name of script file)
#BSUB -J "analyze"

mpirun -np 12 yank analyze report --yaml neutral-sams-rmsd-0.yaml --output reports-0 --serial=analysis.yaml
mpirun -np 12 yank analyze --yaml neutral-sams-rmsd-0.yaml --serial=analysis-0.pkl

mpirun -np 12 yank analyze report --yaml neutral-sams-rmsd.yaml --output reports --serial=analysis.yaml
mpirun -np 12 yank analyze --yaml neutral-sams-rmsd.yaml --serial=analysis.pkl
