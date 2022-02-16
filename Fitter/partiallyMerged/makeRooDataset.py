import ROOT
#DON'T USE FUNCTIONS, WE BREAK LIKE MEN
#Currently compatible with CMSSW_12_0
#run with python3
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
file_Directory         =  reDirector +  "/store/user/camclean/boostedWtaggingSF/haddsWithLumiWeight/"
list_file_data       = ["boostedWtaggingSF_Skims_SingleMuon2017All_v00_nanoskim.root" ]
rrv_weight = ROOT.RooRealVar("rrv_weight","rrv_weight",0. ,10000000.)
rdataset_mj     = ROOT.RooDataSet("rdataset_mj","rdataset_mj",ROOT.RooArgSet(rrv_mass_j,rrv_weight),ROOT.RooFit.WeightVar(rrv_weight) )
#Loop through events
treeIn = ROOT.TChain("Events") #initialize TChain to store events from all files of interest
for f in list_file_data:
    fileIn_name = ROOT.TString(file_Directory+f)  
    treeIn.Add(fileIn_name.Data())
    print("Using file: ", fileIn_name)
            
            
    print("N entries: ", treeIn.GetEntries())
        
    print("rrv_mass_j.getMax() = " ,rrv_mass_j.getMax())
    print("rrv_mass_j.getMin() = " ,rrv_mass_j.getMin())
    tmp_event_weight = 1.
    i = 0
    testing = True        
    for i in range(treeIn.GetEntries()):
        if i % 5000 == 0: print("iEntry: ",i, " storing all")
        event = treeIn.GetEntry(i)
        if not (treeIn.SelectedJet_pt > AK8_pt_min): continue
        if not (treeIn.SelectedJet_pt < AK8_pt_max): continue
        jet_mass = "SelectedJet_sdB0_mass"
        if getattr(treeIn, jet_mass) > rrv_mass_j.getMax() and getattr(treeIn, jet_mass)< rrv_mass_j.getMin() : continue
        tmp_jet_mass = getattr(treeIn, jet_mass);
        treeWeight = treeIn.GetWeight()
        if tmp_jet_mass > rrv_mass_j.getMin() and tmp_jet_mass < rrv_mass_j.getMax():
            rrv_mass_j.setVal(tmp_jet_mass)
            rdataset_mj.add(ROOT.RooArgSet(rrv_mass_j), tmp_event_weight)
ws = ROOT.RooWorkspace("workspace", "workspace")
getattr(ws, "import")(rdataset_mj)
ws.Print()
ws.writeToFile("workspace.root")
