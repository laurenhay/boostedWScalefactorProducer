
### Producing samples

## Running locally
First you need to produce your input files by skimming nanoAOD samples.

For local skimming tests, go to the test folder, the syntax is (remember to change defaults as necessary infile!):
```
  python boostedWtaggingSF_skimNanoAOD.py --iFile 'root://cms-xrd-global.cern.ch///store/mc/RunIIAutumn18NanoAODv7/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/NANOAODSIM/Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/60000/EF3977F7-2F3E-7F44-9DE3-73895A82D5BD.root' --numEvents 200000 --year '2018' --local --channel 'mu' 
```
The --local option is particularly useful as it downloads the above inp. file to a local /tmp directory and further tests can be run without accessing via xrootd, just give it the file path of the downloaded file (which is printed out when the script runs).

## Running with crab
To submit batch jobs go to directory 
```Skimmer/test```
Remember to perform VOMS login: ```voms-proxy-init --voms cms --valid 48:00```

Submit to crab with:
```
python multicrab_boostedWtaggingSF.py --dataset TT --v v01_test
```  
Remember to check and update listed datasets in-file. Check if multiple datasets start with the above string, here e.g. 'TT', and run like this only if you want to skim all the listed datasets starting with the string else, comment out/use the full key corresponding to one dataset in the samples dict.

Resubmissions for crab are done the usual way, by crab resubmit crab_projects/crab_boostedWtaggingSF_X (X=sample dict key, crab_projects folder is created automatically in your test directory once a crab job is run).
