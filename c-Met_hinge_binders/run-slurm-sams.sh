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
#SBATCH -N 4 -n 8 --gres=gpu:2
#
#SBATCH --export=ALL
#
#SBATCH --job-name="c-met-sams"

build_mpirun_configfile "yank script --yaml=sams-twostage.yaml"
mpiexec.hydra -f hostfile -configfile configfile
