import FWCore.ParameterSet.Config as cms
process = cms.Process('NANO')
process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring(),
)
process.source.fileNames = [
    'root://cms-xrd-global.cern.ch///store/mc/RunIISummer19UL17NanoAOD/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/106X_mc2017_realistic_v6-v1/100000/B8E8D3C6-B111-DB43-92B7-2FD447A95C87.root',
    #'root://xrootd-cms.infn.it//store/group/lpctlbsm/NanoAODJMAR_2019_V1/Production/CRAB/TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/TTJetsTuneCUETP8M113TeV-madgraphMLM-pythia8RunIISummer16MiniAODv3-PUMoriond1794XmcRun2/190321_164456/0000/nano102x_on_mini94x_2016_mc_NANO_12.root',
    #'root://cms-xrd-global.cern.ch///store/mc/RunIISummer19UL17NanoAOD/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/NANOAODSIM/106X_mc2017_realistic_v6-v1/70000/FF73DD72-FFB2-CB41-AE38-261D7B69E049.root',
    #'root://cms-xrd-global.cern.ch///store/mc/RunIIAutumn18NanoAODv7/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/NANOAODSIM/Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/60000/EF3977F7-2F3E-7F44-9DE3-73895A82D5BD.root',
    #'root://cms-xrd-global.cern.ch///store/mc/RunIIAutumn18NanoAODv5/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/NANOAODSIM/Nano1June2019_102X_upgrade2018_realistic_v19-v1/120000/B53AD17E-D55D-074B-843D-AD8A597C2D74.root',
    #'root://xrootd-cms.infn.it//store/mc/RunIIAutumn18NanoAODv5/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/NANOAODSIM/Nano1June2019_102X_upgrade2018_realistic_v19-v1/60000/8ABD924A-A197-6848-8949-A5539DC012C3.root',
    #'root://xrootd-cms.infn.it//store/group/lpctlbsm/NanoAODJMAR_2019_V1/Production/CRAB/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/TTTuneCUETP8M2T413TeV-powheg-pythia8RunIISummer16MiniAODv3-PUMoriond1794XmcRun2/190321_164443/0000/nano102x_on_mini94x_2016_mc_NANO_221.root',
    #'root://xrootd-cms.infn.it//store/group/lpctlbsm/NanoAODJMAR_2019_V1/Production/CRAB/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/TTTuneCUETP8M2T413TeV-powheg-pythia8RunIISummer16MiniAODv3-PUMoriond1794XmcRun2/190321_164443/0000/nano102x_on_mini94x_2016_mc_NANO_534.root',
    #'root://xrootd-cms.infn.it//store/group/lpctlbsm/NanoAODJMAR_2019_V1/Production/CRAB/SingleMuon/SingleMuon_Run2016E-17Jul2018-v1/190429_210147/0000/nano102x_on_mini94x_2016_data_NANO_393.root',
]
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))#-1 for all
process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))


process.output = cms.OutputModule("PoolOutputModule",
	                          fileName = cms.untracked.string('boostedWtaggingSF_nanoskim.root'),
				  fakeNameForCrab =cms.untracked.bool(True)
                                 )
process.out = cms.EndPath(process.output)
