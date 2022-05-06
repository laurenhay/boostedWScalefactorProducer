### JMR and JMS Study Instructions ###
```
cmsrel CMSSW_12_0_4
cd CMSSW_12_0_4/src
cmsenv
```
The available mass variables available in the datasets in makeRooDataset are sdB0, sdB1, sdB0Z0p05, sdB1Z0p05, sdB0Z0p15, sdB1Z0p15. All files are stored on LPC.
To make root RooDataset files for desired mass variable:
```
cd boostedWScalefactorProducer/Fitter/partiallyMerged
python3 makeRooDataset.py --mass_var=sdB0
```
To produce fitting variables and plots for the corresponding dataset:
```
python3 basicFit_nanoAOD.py --workspace=workspace_sdB0 --mass_var=sdB0
```

### W-tagging scalefactor producer ###
#########################################

Repository for fitting W-tagging scalefactors in a semi-leptonic ttbar enriched region. Contains code to skim nanoAOD samples using a semi-leptonic ttbar selection (WTopScalefactorProducer/Skimmer). This output is then used to fit data and MC and extract W-tagging scalefactors (WTopScalefactorProducer/Fitter) both from fitting the AK8 W-jet mass at low-pT (around 200 GeV) and fitting the top AK8 W-subjet mass (around 400 GeV). The calculated scalefactors are then statistically combined and fitted, yielding a parametrisation for the W-tagging pT-dependence.

boostedWScalefactorProducer/Skimmer : Start here. Produce samples.
boostedWScalefactorProducer/Fitter  : Based on output from above, run script mainBLABLA.sh to compute fully- and partially-merged W-tagging scalfactors as well as statistically combining the two

## installation instructions for CMSSW_10_6_X
Setup CMSSW and get nanoAOD packages
```
cmsrel CMSSW_10_6_12
cd CMSSW_10_6_12/src
cmsenv

git clone https://github.com/UBParker/NanoAODJMAR.git PhysicsTools/NanoAODJMAR
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools
git clone https://github.com/cms-jet/NanoAODJMARTools.git PhysicsTools/NanoAODJMARTools
git clone -b UL_R2 https://github.com/kaustuvdatta/boostedWScalefactorProducer.git 

ln -s $CMSSW_BASE/src/PhysicsTools/NanoAODTools/scripts/haddnano.py jetObservables/Skimmer/test/
scram b -j 6
```
## Step 1: Producing samples

First you need to produce your input files by skimming nanoAOD samples. For this, see README in subdirectory Skimmer/.


## Step 2: Running scalefactor code

When you have skimmed your samples you can move to fitting the W-tagging scalefactor. The fitting code is located in Fitter/, see README in that directory. For scalefactors from merged W AK8 jet, use Fitter/partiallyMerged. For scalefactors from merged top AK8 jet, use Fitter/fullyMerged

