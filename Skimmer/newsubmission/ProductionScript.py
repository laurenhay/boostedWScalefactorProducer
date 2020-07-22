#!/Usr-/bin/env python
import os,sys
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import * 
from WTopScalefactorProducer.Skimmer.skimmer import Skimmer
import time
import pickle
import glob
if len(sys.argv)<2:
  sys.stderr.write("ERROR: There are too few arguments. The script needs the following arguments: 1. output directory, 2. list of source files") 

outputDir = os.path.expandvars(sys.argv[1]) #outputDir = os.path.expandvars("$GC_SCRATCH")

infile = sys.argv[2].split(' ')

year = int(sys.argv[3])


print "argv: ", sys.argv

print "infile: ", infile

print "outputDir: ", outputDir

writetimingfile = True
runastest = False

if (runastest == True): 
  numentriespertree = 1000 # Need this number to have at least a couple of events written to thee output file
else: 
  numentriespertree = None

# HLT_Mu50&&nMuon>0&&Muon_pt[0]>55.&&Muon_pfRelIso03_chg[0]<0.15&&Muon_highPtId>1&&nFatJet>0&&FatJet_pt>200

jsonfile=os.path.expandvars('$CMSSW_BASE/src/WTopScalefactorProducer/Skimmer/python/JSON/Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt')


if infile[0].find("SingleMuon")!=-1:
  channel = "mu"
  print "Processing a Single Muon dataset file..."
  p=PostProcessor(outputDir, infile, None, None, #"HLT_Mu50 && nMuon>0 && Muon_pt[0]>55. && nFatJet>0"
                    modules=[Skimmer(channel, year),],provenance=False,fwkJobReport=False, maxEntries = numentriespertree,  
                    jsonInput=jsonfile,
                    )

elif infile[0].find("EGamma")!=-1:
  channel = "el"
  print "Processing a Single Electron dataset file..."
  p=PostProcessor(outputDir, infile, None, None, #"(event.HLT_Ele32_WPTight_Gsf || event.HLT_Ele35_WPTight_Gsf || event.HLT_Ele40_WPTight_Gsf || HLT_Ele115_CaloIdVT_GsfTrkIdT) && nElectron>0 && Electron_pt[0]>55. && nFatJet>0"
                    modules=[Skimmer(channel, year)],provenance=False,fwkJobReport=False, maxEntries = numentriespertree, 
                    jsonInput=jsonfile,
                    )

else:
  print "Processing MC dataset files..."
  channel = "elmu"
  p=PostProcessor(outputDir, infile, None, None,
                    modules=[Skimmer(channel, year)],provenance=False,fwkJobReport=False, maxEntries = numentriespertree, 
                    #jsonInput=jsonfile,
)

start = time.time()
p.run()
#time.sleep(5)
endpostprocessing = time.time()

#os.system("xrdcp root://eosuser.cern.ch//eos/user/m/mhuwiler/data/Wtagging/prodexample/8C2AE8D3-E2DA-524D-9F98-05FEA3DF3063_Skim.root {} ; xrdcp root://eosuser.cern.ch//eos/user/m/mhuwiler/data/Wtagging/prodexample/BB978C6D-1770-CB42-A45E-AFAA249DAA82_Skim.root {} ".format(outputDir, outputDir))


os.popen("haddnano.py {}/out.root {}/*Skim.root".format(outputDir, outputDir)).read()
endhadd = time.time()

# Computing time 
processingtime = endpostprocessing - start
haddtime = endhadd - endpostprocessing

print "Pocessing time:", processingtime
print "Hadd time:", haddtime

# Quality test: 
sanitycheck = []
allgood = True
numEntries = 0
sumNumEntries = 0 
addedNumEntries = -1
for filename in glob.glob(outputDir+"/*.root"): 
  #filename = os.path.expandvars(outputDir)+"/"+filename
  isOpen = False
  isValid = False
  treeFilled = False
  isFile = os.path.isfile(filename)
  if isFile: 
    file = ROOT.TFile(filename, "r")
    isOpen = file.IsOpen()
    if isOpen: 
      isValid = (file.GetListOfKeys().Contains("Runs") and file.GetListOfKeys().Contains("Events"))
            
      if isValid: 
        tree = file.Get("Events")
        treeFilled = (tree.GetEntries() > 1)
        numEntries = tree.GetEntries()
        if (filename.find("out.root") != -1): 
          addedNumEntries = numEntries
        else: 
          sumNumEntries += numEntries
    file.Close()

  isBroken = not (isFile and isOpen and isValid and treeFilled)
  allgood = allgood and not isBroken
  sanitycheck.append([filename, int(isFile), int(isOpen), int(isValid), int(treeFilled), int(isBroken), numEntries])

print sanitycheck
print "All files valid and filled:", allgood 
entriesmatch = False
if (sumNumEntries == addedNumEntries): 
  print "The number of entries in the hadded file corresponds to the sum of entries in individual files. "
  entriesmatch = True
else: 
  print "ERROR: The number of entries in the added file does not match the number of entries in the processed files! "

print "Number of entries in the pricessed files (sum): ", sumNumEntries, "Number of entries in the added file: ", addedNumEntries 

with open(os.path.expandvars(outputDir)+"/qualitycheck.pkl", "wb") as outputfile: 
  pickle.dump(sanitycheck, outputfile, pickle.HIGHEST_PROTOCOL)

if (writetimingfile): 
  with open(os.path.expandvars(outputDir)+"/timing.dat", "w") as outfile: 
    outfile.write(str(start)+","+str(endpostprocessing)+","+str(endhadd)+"\n")

print "Job seems to be sucessful:", allgood and entriesmatch

print "ProductionScript.py: DONE"
