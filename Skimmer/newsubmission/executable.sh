#!/bin/bash

echo $FILE_NAMES

env


#WD=/afs/cern.ch/work/m/mhuwiler/software/cc7/Wtagging/CMSSW_10_2_6/src/WTopScalefactorProducer/Skimmer/newsubmission

#cd $WD

#export SCRAM_ARCH=slc7_amd64_gcc700           #### Better to work on CC7 than SL6
#export X509_USER_PROXY=${HOME}/private/x509up

source env.sh

source /cvmfs/cms.cern.ch/cmsset_default.sh
cd ${CMSSW_BASE}/src
eval `scramv1 runtime -sh`

cd ${CMSSW_BASE}/src/*/Skimmer/newsubmission  #$WD


python $CMSSW_BASE/src/WTopScalefactorProducer/Skimmer/newsubmission/ProductionScript.py "$GC_SCRATCH" "$FILE_NAMES" "$YEAR"

# Additional manual copying of file for safety
# /scratch/mhuwiler/Wtagging/production/${GC_TASK_ID}/${DATASETPATH}/
if [ -n "${LOCAL_OUTPUT_DIR// }" ]
then

    DESTINATIONPATH=${LOCAL_OUTPUT_DIR}/${GC_TASK_ID}/${DATASETPATH}

    echo "Writing output files to local destination: ${DESTINATIONPATH}"

    mkdir -p $DESTINATIONPATH

    cp $GC_SCRATCH/out.root $DESTINATIONPATH/job_${GC_JOB_ID}_out.root
    cp $GC_SCRATCH/qualitycheck.pkl $DESTINATIONPATH/job_${GC_JOB_ID}_qualitycheck.pkl
    cp $GC_SCRATCH/timing.dat $DESTINATIONPATH/job_${GC_JOB_ID}_timing.dat

fi

echo $GC_SCRATCH
ls -l $GC_SCRATCH

