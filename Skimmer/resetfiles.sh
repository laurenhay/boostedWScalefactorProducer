WORKDIR=/scratch/mhuwiler/data/WTagging/ #/work/mhuwiler/data/WScaleFactors/UL2017/
rm -r $WORKDIR/UL17_Wtagging_files_new/ #/work/mhuwiler/data/WScaleFactors/UL2017/UL17_Wtagging_files/
#cp -r /work/kadatta/private/CMSSW_10_6_12/src/UL17_Wtagging_files/ /work/mhuwiler/data/WScaleFactors/UL2017/
cp -r /work/kadatta/private/CMSSW_10_6_12/src/UL17_Wtagging_files_new $WORKDIR
