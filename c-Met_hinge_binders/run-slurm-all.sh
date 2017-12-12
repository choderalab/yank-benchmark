#!/bin/bash
#
#Walltime
#SBATCH -t 72:00:00
#
#SBATCH -o "slurm-%j.out"
#SBATCH -e "slurm-%j.err"
#
#partition
#SBATCH --partition=GTX
#
# Nodes
#SBATCH -N 2 -n 8 --gres=gpu:4
#
#SBATCH --export=ALL
#
#SBATCH --job-name="c-met-all"

source activate yank17
build_mpirun_configfile "yank script --yaml=explicit-all.yaml"
mpiexec.hydra -f hostfile -configfile configfile
