#!/bin/bash

#SBATCH --job-name=e+e-
#SBATCH --time=4:00:00
#SBATCH --exclude=s1cmp001,s1cmp002,s1cmp003,p1cmp041,s1cmp012,s1cmp011,s1cmp013,s1cmp010,s1cmp014,s1cmp015
#SBATCH --error=gridlog_fmdata_nue.%j.%N.err
#SBATCH --mem-per-cpu=10000
#SBATCH --array=0-1
#SBATCH --partition=preempt

ls /cluster/tufts/wongjiradlabnu/epanne01/run_cropimages.sh

CONTAINER=/cluster/tufts/wongjiradlabnu/larbys/larbys-container/singularity_minkowskiengine_u20.04.cu111.torch1.9.0_comput8.sif
VALSCRIPT=/cluster/tufts/wongjiradlabnu/epanne01/run_cropimages.sh

module load singularity/3.5.3

singularity exec --bind /cluster/tufts/wongjiradlabnu:/cluster/tufts/wongjiradlabnu,/cluster/tufts/wongjiradlab:/cluster/tufts/wongjiradlab ${CONTAINER} bash -c "source $VALSCRIPT cropimages.py  darkNuTruth.txt darkNuReco.txt" 
