

class Dataset: 


	self.files_Directory       = "/work/mhuwiler/data/WScaleFactors/Mergeddefinition2017/"

    self.files["data"] = ["SingleMuon-Run2018A.root", "SingleMuon-Run2018B.root", "SingleMuon-Run2018C.root", "SingleMuon-Run2018D.root"]
    self.files["TT"]   = ["TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8.root", "TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8.root"]
    self.list_file_WJets_mc   = ["WJetsToLNu_HT-70To100_TuneCP5_13TeV-madgraphMLM-pythia8.root", "WJetsToLNu_HT-100To200_TuneCP5_13TeV-madgraphMLM-pythia8.root", "WJetsToLNu_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8.root", "WJetsToLNu_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8.root", "WJetsToLNu_HT-600To800_TuneCP5_13TeV-madgraphMLM-pythia8.root", "WJetsToLNu_HT-800To1200_TuneCP5_13TeV-madgraphMLM-pythia8.root", "WJetsToLNu_HT-1200To2500_TuneCP5_13TeV-madgraphMLM-pythia8.root", "WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8.root"]
    self.list_file_STop_mc    = ["ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-madgraph-pythia8.root", "ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8.root", "ST_t-channel_top_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8.root", "ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8.root", "ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8.root"] #["ST_t-channel_antitop_5f_TuneCP5_13TeV-powheg-pythia8.root", "ST_t-channel_top_5f_TuneCP5_13TeV-powheg-pythia8.root", "ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8.root", "ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8.root"]
    self.list_file_VV_mc      = ["WW_TuneCP5_13TeV-pythia8.root", "WZ_TuneCP5_13TeV-pythia8.root", "ZZ_TuneCP5_13TeV-pythia8.root"]

    # For topShower only
    self.list_file_TTbar_mc   = ["TT_TuneCH3_13TeV-powheg-herwig7.root"]
    # For topGen only
    self.list_file_TTbar_mc   = ["TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8.root"]

    
    self.list_file_pseudodata =  self.list_file_STop_mc + self.list_file_VV_mc   + self.list_file_WJets_mc + self.list_file_TTbar_mc

