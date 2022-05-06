from optparse import OptionParser
import ROOT
#DON'T USE FUNCTIONS, WE BREAK LIKE MEN
#Currently compatible with CMSSW_12_0
#run with python3

parser = OptionParser()
parser.add_option('--mass_var', action="store",type="string",dest="mass_var",default="", help="jet mass grooming variable")
(options, args) = parser.parse_args()

# other mass_var options: sdB0, sdB1, sdB0Z0p05, sdB1Z0p05, sdB0Z0p15, sdB1Z0p15

BinWidth = 5.
in_mj_min = 50.
in_mj_max = 130.
AK8_pt_min = 200.
AK8_pt_max = 10000.

nbins_mj         = int( (in_mj_max - in_mj_min) / BinWidth )
in_mj_max        = in_mj_min+nbins_mj*BinWidth
rrv_mass_j = ROOT.RooRealVar("rrv_mass_j", "PUPPI softdrop jet mass" ,(in_mj_min+in_mj_max)/2.,in_mj_min,in_mj_max,"GeV")
rrv_mass_j.setBins(nbins_mj)

# Directory and input files
reDirector = "root://cmseos.fnal.gov/"   
file_Directory =  reDirector +  "/store/user/camclean/boostedWtaggingSF/haddsWithLumiWeight/"
list_file_data = ["boostedWtaggingSF_Skims_SingleMuon2017All_v00_nanoskim.root" ]
list_file_STop_mc = [ "ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8_nanoskim.root" , "ST_t-channel_antitop_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8_nanoskim.root" , "ST_t-channel_top_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8_nanoskim.root" ,"ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8_nanoskim.root" ,"ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8_nanoskim.root"  ]
list_file_TTbar_mc = ["TTJets_TuneCP5_13TeV-madgraphMLM-pythia8_nanoskim.root" ,"TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_nanoskim.root", "TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_nanoskim.root"]
list_file_WJets_mc = ["WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8_nanoskim.root"]
list_file_VV_mc = ["WW_TuneCP5_13TeV-pythia8_nanoskim.root","WZ_TuneCP5_13TeV-pythia8_nanoskim.root", "ZZ_TuneCP5_13TeV-pythia8_nanoskim.root"]
list_file_totalMC = list_file_STop_mc + list_file_VV_mc   + list_file_WJets_mc + list_file_TTbar_mc

#make workspace
workspace = ROOT.RooWorkspace("workspace", "workspace")

jet_mass = "SelectedJet_"+options.mass_var+"_mass"

def makeDataset(list_file_in, label, jet_mass):

    rrv_weight = ROOT.RooRealVar("rrv_weight","rrv_weight",0. ,10000000.)
    rdataset_mj = ROOT.RooDataSet("rdataset_"+label+"_mj","rdataset_"+label + "mj",ROOT.RooArgSet(rrv_mass_j,rrv_weight),ROOT.RooFit.WeightVar(rrv_weight) )
    rdataset_passtau21cut_mj     = ROOT.RooDataSet("rdataset_"+label+"_passtau21cut_mj","rdataset_"+label+"_passtau21cut_mj",ROOT.RooArgSet(rrv_mass_j,rrv_weight),ROOT.RooFit.WeightVar(rrv_weight) )
    rdataset_failtau21cut_mj = ROOT.RooDataSet("rdataset4fit_" +label+"_failtau21cut_mj","rdataset_"+label+"_failtau21cut_mj",ROOT.RooArgSet(rrv_mass_j,rrv_weight),ROOT.RooFit.WeightVar(rrv_weight) )
    rdataset_extremeFail_mj = ROOT.RooDataSet("rdataset4fit_" +label+"_extremeFail_mj","rdataset_"+label+"_extremeFail_mj",ROOT.RooArgSet(rrv_mass_j,rrv_weight),ROOT.RooFit.WeightVar(rrv_weight) )

    #Loop through events
    treeIn = ROOT.TChain("Events") #initialize TChain to store events from all files of interest
    treeIn.Print("SelectedJet*")
    for f in list_file_in:
        fileIn_name = ROOT.TString(file_Directory+f)  
        treeIn.Add(fileIn_name.Data())
        print("Using file: ", fileIn_name)
    print("Using mass variable: ", jet_mass)        
    print("N entries: ", treeIn.GetEntries())
        
    print("rrv_mass_j.getMax() = " ,rrv_mass_j.getMax())
    print("rrv_mass_j.getMin() = " ,rrv_mass_j.getMin())
    tmp_event_weight = 1.
    i = 0
    
    for i in range(treeIn.GetEntries()):
        if i % 5000 == 0: print("iEntry: ",i)
        #print("iEntry: ", i)
        event = treeIn.GetEntry(i)
        #apply pt cut
        if not (treeIn.SelectedJet_pt > AK8_pt_min): continue
        if not (treeIn.SelectedJet_pt < AK8_pt_max): continue
        #apply mass cut
        if getattr(treeIn, jet_mass) > rrv_mass_j.getMax() and getattr(treeIn, jet_mass)< rrv_mass_j.getMin() : continue
        #get tau21 values
        #tau21 = treeIn.SelectedJet_tau21_ddt_retune # we don't use ddt right?
        tau21 = treeIn.SelectedJet_tau21

        tmp_jet_mass = getattr(treeIn, jet_mass);
        treeWeight = treeIn.GetWeight()
        
        if not ROOT.TString(label).Contains("data"):
            lumiweight = 1.0
            tmp_scale_to_lumi = treeIn.eventweightlumi
            tmp_event_weight = tmp_scale_to_lumi
        else:
            tmp_scale_to_lumi = 1.
            tmp_event_weight = 1.
        
#        print("tau21 used: ", tau21)
#        print("temp_scale_to_lumi: ", tmp_scale_to_lumi, "treeIn.eventweightlumi: ", treeIn.eventweightlumi)

        if (rrv_mass_j.getMin() < tmp_jet_mass < rrv_mass_j.getMax()):
            rrv_mass_j.setVal(tmp_jet_mass)
            rdataset_mj.add(ROOT.RooArgSet(rrv_mass_j), tmp_event_weight)
        if (tau21 <= 0.35) and tmp_jet_mass > rrv_mass_j.getMin() and tmp_jet_mass < rrv_mass_j.getMax(): #HP cut
            rrv_mass_j.setVal(tmp_jet_mass)
            rdataset_passtau21cut_mj.add(ROOT.RooArgSet(rrv_mass_j), tmp_event_weight)
            # print("event ", i, " passed!")
            # print("pt: ", treeIn.SelectedJet_pt, "jet mass: ", getattr(treeIn, jet_mass), "sdB0_mass", treeIn.SelectedJet_sdB0_mass)
        if (0.35 < tau21 <= 0.75) and (rrv_mass_j.getMin() < tmp_jet_mass < rrv_mass_j.getMax()): #LP cut
            rrv_mass_j.setVal(tmp_jet_mass)
            rdataset_failtau21cut_mj.add(ROOT.RooArgSet(rrv_mass_j), tmp_event_weight)
        if (tau21 > 0.75) and (rrv_mass_j.getMin() < tmp_jet_mass < rrv_mass_j.getMax()): #extreme fail
            rdataset_extremeFail_mj.add(ROOT.RooArgSet(rrv_mass_j), tmp_event_weight)
    print("N events passing tau cut: ", rdataset_passtau21cut_mj.numEntries())
    print("Sum of weights of pass events: ", rdataset_passtau21cut_mj.sumEntries())
    print("Number of fail events: ", rdataset_failtau21cut_mj.numEntries())
    print("Sum of weight of fail events: ", rdataset_failtau21cut_mj.sumEntries())
    print("Total events passing pt and mass cut: ", rdataset_mj.numEntries())
    print("Sum of weights passing pt and mass cut: ", rdataset_mj.sumEntries())
    getattr(workspace, "import")(rdataset_mj)
    getattr(workspace, "import")(rdataset_passtau21cut_mj)
    getattr(workspace, "import")(rdataset_failtau21cut_mj)
    getattr(workspace, "import")(rdataset_extremeFail_mj)
#add dataSets to workspace for data and MC
makeDataset(list_file_totalMC, "totalMC", jet_mass)
#makeDataset(list_file_VV_mc, "VV")
makeDataset(list_file_data, "data", jet_mass)

workspace.Print()
workspace.writeToFile("workspace_"+options.mass_var+".root")
