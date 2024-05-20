#!/bin/bash

JOBSTARTDATE=$(date)

scriptDir="/cluster/tufts/wongjiradlabnu/epanne01"
pythonScript="${scriptDir}/$1"

darkNuTruthFiles="/cluster/tufts/wongjiradlabnu/epanne01/$2"
recoFiles="/cluster/tufts/wongjiradlabnu/epanne01/$3"


outTag=$3

ubdlDir="/cluster/tufts/wongjiradlabnu/epanne01/ubdl"
source /usr/local/root/bin/thisroot.sh
source ${ubdlDir}/setenv_py3.sh
source ${ubdlDir}/configure.sh
export PYTHONPATH=${PYTHONPATH}:${scriptDir}


echo -e "the filename is $2"



maxFileCount=`wc -l < $recoFiles`
echo -e "max file count: " $maxFileCount
nfiles=2
let firstfile="${SLURM_ARRAY_TASK_ID}*${nfiles}+1"
let lastfile="$firstfile+$nfiles-1"
files=""

for n in $(seq $firstfile $lastfile); do
   if (($n > $maxFileCount)); then
        break
   fi
   newfile=`sed -n ${n}p ${recoFiles}`
   files="$files $newfile"
done

scriptName=`echo $1 | sed s/.py//g`
outDir="/cluster/tufts/wongjiradlabnu/epanne01/trainingimages"
logDir="/cluster/tufts/wongjiradlabnu/epanne01/logs"

logFile="${logDir}/${scriptName}_${outTag}_${SLURM_ARRAY_TASK_ID}.log"
#outFile="${scriptName}_${outTag}_output_${SLURM_ARRAY_TASK_ID}.root"
#logFile="${scriptName}_${outTag}_${SLURM_ARRAY_TASK_ID}.log"

#local_jobdir=`printf /tmp/larflowrecoval_jobid%d_%04d ${SLURM_JOB_ID} ${SLURM_ARRAY_TASK_ID}`
#rm -rf $local_jobdir
#mkdir -p $local_jobdir
#cd $local_jobdir


python3 $pythonScript -f $darkNuTruthFiles -r $files -o $outDir -v $SLURM_ARRAY_TASK_ID

JOBENDDATE=$(date)

echo "Job began at $JOBSTARTDATE" >> $logFile
echo "Job ended at $JOBENDDATE" >> $logFile
