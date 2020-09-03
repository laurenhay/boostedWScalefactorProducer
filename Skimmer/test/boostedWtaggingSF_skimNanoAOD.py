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

from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeight_2016, puWeight_2017, puAutoWeight_2016, puAutoWeight_2017, puWeight_2018, puAutoWeight_2018
from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer import btagSF2016, btagSF2017, btagSF2018
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



args = parser.parse_args(sys.argv[1:])
#haddname = "boostedWtagging_%s_nanoskim.root"%args.year
if args.sample.startswith(('/EGamma', '/Single', 'EGamma', 'Single' )) or ('EGamma' in args.iFile or 'Single' in args.iFile ):
    isMC = False
    print "sample is data"
else: isMC = True

### General selections:
PV = "(PV_npvsGood>0)"

METFilters = "( (Flag_goodVertices==1) && (Flag_globalSuperTightHalo2016Filter==1) && (Flag_HBHENoiseFilter==1) && (Flag_HBHENoiseIsoFilter==1) && (Flag_EcalDeadCellTriggerPrimitiveFilter==1) && (Flag_BadPFMuonFilter==1) )"
if not isMC: METFilters = METFilters + ' && (Flag_eeBadScFilter==1)'

#if args.sample.startswith(('SingleMuon', '/SingleMuon') or ('SingleMuon' in args.iFile or '\SingleMuon' in args.iFile)): 
#    Triggers = '(HLT_Mu50==1)' 

#if args.sample.startswith(('SingleElectron', '/SingleElectron', 'EGamma', '/EGamma') or ('SingleElectron' in args.iFile or '\SingleElectron' in args.iFile or 'EGamma' in args.iFile or '\EGamma' in args.iFile)): 
#    Triggers = '(HLT_Ele35_WPTight_Gsf==1) && (HLT_Ele115_CaloIdVT_GsfTrkIdT==1)'

if args.channel.startswith(('mu')): Triggers = '(HLT_Mu50==1)' 
if args.channel.startswith(('el')): Triggers  = '(HLT_Ele35_WPTight_Gsf==1) && (HLT_Ele115_CaloIdVT_GsfTrkIdT==1)'
if args.channel=='elmu': Triggers  = '((HLT_Mu50==1) || ((HLT_Ele35_WPTight_Gsf==1) && (HLT_Ele115_CaloIdVT_GsfTrkIdT==1)))' 

cuts = PV + " && " + METFilters + " && " + Triggers


### Lepton scale factors 
### TODO: Change files for electrons (all years, as necessary), for Muons waiting for ID/ISO SFs  for 2018/2016, 2017 all available.
LeptonSF = {
    '2016' : {
        'muon' : {
            'Trigger' : [ "EfficienciesAndSF_RunBtoF.root", "Mu50_OR_TkMu50_PtEtaBins/pt_abseta_ratio" ],
            'ID' : [ "MuonID_2016_RunBCDEF_SF_ID.root", "NUM_TightID_DEN_genTracks_eta_pt", False ],       ### True: X:pt Y:eta
            'ISO' : [ "MuonID_2016_RunBCDEF_SF_ISO.root", "NUM_TightRelIso_DEN_TightIDandIPCut_eta_pt", True ],
        },
        'electron' : {
            'Trigger' : [ "TriggerSF_Run2016All_v1.root", "Ele27_WPTight_Gsf" ],
            'ID' : [ "2016LegacyReReco_ElectronTight_Fall17V2.root", "EGamma_SF2D", False ],
            'ISO' : [ "EGM2D_BtoH_GT20GeV_RecoSF_Legacy2016.root", "EGamma_SF2D", False ],
        },
    },
    '2017' : {
        'muon' : {
            'Trigger' : [ "EfficienciesAndSF_RunBtoF_Nov17Nov2017.root", "Mu50_PtEtaBins/pt_abseta_ratio" ],
            'ID' : [ "RunBCDEF_UL2017_SF_ID.root", "NUM_TightID_DEN_genTracks_pt_abseta", True ],     ### TODO: Change to tracker muons??? ### (True: X:pt Y:eta)
            'ISO' : [ "RunBCDEF_UL2017_SF_ISO.root", "NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta", True ],
        },
        'electron' : {
            'Trigger' : [ "SingleEG_JetHT_Trigger_Scale_Factors_ttHbb_Data_MC_v5.0.histo.root", "SFs_ele_pt_ele_sceta_ele28_ht150_OR_ele35_2017BCDEF" ],
            'ID' : [ "egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root", "EGamma_SF2D", False ],
            'ISO' : [ "2017_ElectronTight.root", "EGamma_SF2D", False ],
        },
    },
    '2018' : {
        'muon' : {
            'Trigger' : [ "EfficienciesAndSF_2018Data_AfterMuonHLTUpdate.root", "Mu50_OR_OldMu100_OR_TkMu100_PtEtaBins/pt_abseta_ratio" ],
            'ID' : [ "MuonID_2018_RunABCD_SF_ID.root", "NUM_TightID_DEN_TrackerMuons_pt_abseta", True ],
            'ISO' : [ "MuonID_2018_RunABCD_SF_ISO.root", "NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta", True ],
        },
        'electron' : {
            'Trigger' : [ "SingleEG_JetHT_Trigger_Scale_Factors_ttHbb_Data_MC_v5.0.root", "SFs_ele_pt_ele_sceta_ele28_ht150_OR_ele35_2017BCDEF" ],
            'ID' : [ "egammaEffi.txt_EGM2D_updatedAll.root", "EGamma_SF2D", False ],
            'ISO' : [ "2018_ElectronTight.root", "EGamma_SF2D", False ],
        },
    },
}


#### Modules to run
jetmetCorrector = createJMECorrector(isMC=isMC, dataYear=int(args.year), jesUncert="All", redojec=True)
fatJetCorrector = createJMECorrector(isMC=isMC, dataYear=int(args.year), jesUncert="All", redojec=True, jetType = "AK8PFPuppi")

modulesToRun = []
if isMC:
    if args.year=='2018':
	modulesToRun.append( puWeight_2018() )
	modulesToRun.append( btagSF2018() )
    if args.year=='2017':
	modulesToRun.append( puWeight_2017() )
	modulesToRun.append( btagSF2017() )
    if args.year=='2016':
	modulesToRun.append( puWeight_2016() )
	modulesToRun.append( btagSF2016() )
    
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
        longTermCache= args.local,
        fwkJobReport = True,
        haddFileName = "boostedWtaggingSF_"+ args.year + "_" + args.channel + "_nanoskim.root" if args.local else "boostedWtaggingSF_nanoskim.root",
        #histFileName = "boostedWtagging_"+args.year+"_histograms.root" if args.local else 'boostedWtagging_histograms.root',
        #histDirName  = 'boostedWtagging',
        )
p1.run()
print "DONE"
#if not args.local: os.system("ls -lR")
