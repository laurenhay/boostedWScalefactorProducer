#!/usr/bin/env python

from __future__ import division, print_function


patternsData  = [
  "/SingleMuon/Run2018A-Nano1June2019-v1/NANOAOD",
  "/SingleMuon/Run2018B-Nano1June2019-v1/NANOAOD",
  "/SingleMuon/Run2018C-Nano1June2019-v1/NANOAOD",
  "/SingleMuon/Run2018D-Nano1June2019-v1/NANOAOD",
  "/EGamma/Run2018A-Nano1June2019-v1/NANOAOD",
  "/EGamma/Run2018B-Nano1June2019-v1/NANOAOD",
  "/EGamma/Run2018C-Nano1June2019-v1/NANOAOD",
  "/EGamma/Run2018D-Nano1June2019-v1/NANOAOD",
]
patternsTT    = [
  "/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/TT_TuneCH3_13TeV-powheg-herwig7/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19_ext1-v1/NANOAODSIM",
]
patternsST    = [
  "/ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19_ext1-v1/NANOAODSIM",
  "/ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19_ext1-v1/NANOAODSIM",
#   "/ST_t-channel_top_5f_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
#   "/ST_t-channel_antitop_5f_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/ST_t-channel_top_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19_ext1-v1/NANOAODSIM",
]
patternsVV    = [
  "/WZ_TuneCP5_13TeV-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/WW_TuneCP5_13TeV-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/ZZ_TuneCP5_13TeV-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
]
patternsWJets = [
  "/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/WJetsToLNu_HT-70To100_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/WJetsToLNu_HT-100To200_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/WJetsToLNu_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/WJetsToLNu_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/WJetsToLNu_HT-600To800_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/WJetsToLNu_HT-800To1200_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/WJetsToLNu_HT-1200To2500_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
]
patternsQCD = [
  "/QCD_HT100to200_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/QCD_HT200to300_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/QCD_HT300to500_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/QCD_HT500to700_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
  "/QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
]

def getDataset(description):
	patterns = []
	
	if description == "data":  patterns = patternsData  
	elif description == "TT":    patterns = patternsTT    
	elif description == "ST":    patterns = patternsST    
	elif description == "VV":    patterns = patternsVV    
	elif description == "WJets": patterns = patternsWJets 
	elif description == "QCD":   patterns = patternsQCD

	elif description == "mc":    patterns = patternsTT+patternsST+patternsVV+patternsWJets+patternsQCD
	elif description == "all":   patterns = patternsTT+patternsST+patternsVV+patternsWJets+patternsQCD+patternsData

	else: 
		print("Dataset: No dataset was specified!\n Please specify which dataset to process (e.g. {TT, ST, VV, WJets, QCD, mc, data, all})! ")

	return patterns
