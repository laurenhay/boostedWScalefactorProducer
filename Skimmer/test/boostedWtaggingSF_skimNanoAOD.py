#!/usr/bin/env python
import os, sys
import psutil
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

#this takes care of converting the input files from CRAB
from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis

from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puAutoWeight_UL2016, puAutoWeight_UL2017, puAutoWeight_UL2018
from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer import btagSF2016, btagSF2017, btagSF2018, btagSF_UL2016, btagSF_UL2017, btagSF_UL2018
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import *

# our module
from boostedWScalefactorProducer.Skimmer.skimmer import Skimmer


print '---------------------------------------------------'
print 'Input files:'
print inputFiles()


import argparse

parser = argparse.ArgumentParser(description='Runs MEAnalysis')

parser.add_argument(
    '--sample',
    action="store",
    help="Sample to process",
    default='ttHTobb_M125_TuneCP5_13TeV-powheg-pythia8'
)

parser.add_argument(
    '--numEvents',
    action="store",
    type=int,
    help="Number of events to process",
    default=2000000000000,
)

parser.add_argument(
    '--iFile',
    action="store",
    help="Input file (for condor)",
    default=""
)

parser.add_argument(
    '--oFile',
    action="store",
    help="Output file (for condor)",
    default=""
)

parser.add_argument(
    '--local',
    action="store_true",
    help="Run local (0) or condor/crab (1)",
)

#parser.add_argument(
#    '--createTrees',
#    action="store_true",
#    help="Measure RAM"
#)
parser.add_argument(
    '--year',
    action="store",
    help="year of data",
    choices=["2016", "2017", "2018"],
    default="2017",
#    required=True
)

parser.add_argument(
    '--channel',
    action="store",
    help="Event selection: decay channel for semileptonic ttbar",
    choices=["mu", "el", "elmu"],
    default="mu",
    required=False
)

parser.add_argument(
    '--runEra',
    action="store",
    help="Run era for data",
    default="B"
)

args = parser.parse_args(sys.argv[1:])
#haddname = "boostedWtagging_%s_nanoskim.root"%args.year
if args.sample.startswith(('/EGamma', '/Single', 'EGamma', 'Single', 'UL16_Single', '/UL16_Single', 'UL17_Single', '/UL17_Single', 'UL18_Single', '/UL18_Single' )) or ('EGamma' in args.iFile or 'SingleMuon' in args.iFile ):
    isMC = False
    print "sample is data"
else: 
    isMC = True
    print "sample is MC"

### General selections:
PV = "(PV_npvsGood>0)"

METFilters = "( (Flag_goodVertices==1) && (Flag_globalSuperTightHalo2016Filter==1) && (Flag_HBHENoiseFilter==1) && (Flag_HBHENoiseIsoFilter==1) && (Flag_EcalDeadCellTriggerPrimitiveFilter==1) && (Flag_BadPFMuonFilter==1) )"
if not isMC: METFilters = METFilters + ' && (Flag_eeBadScFilter==1)'

#if args.sample.startswith(('SingleMuon', '/SingleMuon') or ('SingleMuon' in args.iFile or '\SingleMuon' in args.iFile)): 
#    Triggers = '(HLT_Mu50==1)' 

#if args.sample.startswith(('SingleElectron', '/SingleElectron', 'EGamma', '/EGamma') or ('SingleElectron' in args.iFile or '\SingleElectron' in args.iFile or 'EGamma' in args.iFile or '\EGamma' in args.iFile)): 
#    Triggers = '(HLT_Ele35_WPTight_Gsf==1) && (HLT_Ele115_CaloIdVT_GsfTrkIdT==1)'

if args.channel.startswith(('mu')): Triggers = '(HLT_Mu50==1)' 
if args.channel.startswith(('el')): 
    if args.year=='2017': Triggers  = '((HLT_Ele32_WPTight_Gsf==1) && ((L1_SingleLooseIsoEG30er1p5==1) || (L1_SingleEG45er2p5==1) || (L1_SingleEG36er2p5==1) || (L1_SingleIsoEG32er2p1==1) || (L1_SingleIsoEG34er2p5==1)) && (HLT_Ele115_CaloIdVT_GsfTrkIdT==1))'
    else: Triggers  = '(HLT_Ele32_WPTight_Gsf==1) && (HLT_Ele115_CaloIdVT_GsfTrkIdT==1)'
if args.channel=='elmu': Triggers  = Triggers+' || (HLT_Mu50==1)' 

cuts = PV + " && " + METFilters + " && " + Triggers


### Lepton scale factors 
### Lepton scale factors
LeptonSF = {

    '2017' : {
        'muon' : {
            'Trigger' : [ "MuonSF_UL17and18.root", "UL17_Trigger", False ],
            'ID' : [ "MuonSF_UL17and18.root", "UL17_ID", False ],
            'ISO' : [ "MuonSF_UL17and18.root", "UL17_ISO", False ],
            'RecoEff' : [ "MuonSF_UL17and18.root", "UL17_Reco", False ],
        },

    },
    '2018' : {
        'muon' : {
            'Trigger' : [ "MuonSF_UL17and18.root", "UL18_Trigger", False ],
            'ID' : [ "MuonSF_UL17and18.root", "UL18_ID", False ],
            'ISO' : [ "MuonSF_UL17and18.root", "UL18_ISO", False ],
            'RecoEff' : [ "MuonSF_UL17and18.root", "UL18_Reco", False ],
        },

    },
}

#### Modules to run
jetmetCorrector = createJMECorrector(isMC=isMC, applySmearing=False, dataYear='UL'+args.year, jesUncert="All", runPeriod=args.runEra )
fatJetCorrector = createJMECorrector(isMC=isMC, applySmearing=False, dataYear='UL'+args.year, jesUncert="All", jetType = "AK8PFPuppi", runPeriod=args.runEra)

modulesToRun = []
if isMC:
    if args.year=='2018':
	modulesToRun.append( puAutoWeight_UL2018() )
	print "Running with btag SF calc."
	modulesToRun.append( btagSF_UL2018() )
    if args.year=='2017':
	modulesToRun.append( puAutoWeight_UL2017() )
	print "Not running with btag SF calc."	
	modulesToRun.append( btagSF_UL2017() )
    if args.year=='2016':
	modulesToRun.append( puAutoWeight_UL2016() )
	print "Running with btag SF calc."
	modulesToRun.append( btagSF_UL2016() )
    
modulesToRun.append( fatJetCorrector() )
modulesToRun.append( jetmetCorrector() )
modulesToRun.append( Skimmer(channel=args.channel, leptonSF=LeptonSF[args.year], year=args.year)) 


#### Make it run
p1=PostProcessor(
        '.', (inputFiles() if not args.iFile else [args.iFile]),
        cut          = cuts,
        outputbranchsel   = "keep_and_drop.txt",
        modules      = modulesToRun,
        provenance   = True,
        #jsonInput   = runsAndLumis(),
        maxEntries   = args.numEvents,
        prefetch     = args.local,
        longTermCache = args.local,
        fwkJobReport = True,
        haddFileName = "boostedWtaggingSF_"+ args.year + "_" + args.channel + "_nanoskim.root" if args.local else "boostedWtaggingSF_nanoskim.root",
        histFileName = "boostedWtaggingSF_"+ args.year + "_" + args.channel + "_histograms.root" if args.local else 'boostedWtaggingSF_histograms.root',
        histDirName  = 'boostedWtaggingSF_'+ args.year,
        )
p1.run()
print "DONE"
#if not args.local: os.system("ls -lR")
