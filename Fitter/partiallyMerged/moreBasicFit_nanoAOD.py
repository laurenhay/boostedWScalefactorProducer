import ROOT
from ROOT import *
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

rrv_mass_j = RooRealVar("rrv_mass_j", "PUPPI softdrop jet mass" ,(in_mj_min+in_mj_max)/2.,in_mj_min,in_mj_max,"GeV")
rrv_mass_j.setBins(nbins_mj)

# Directory and input files
reDirector = "root://cmseos.fnal.gov/"   
file_Directory         =  reDirector +  "/store/user/camclean/boostedWtaggingSF/haddsWithLumiWeight/"

list_file_data       = ["boostedWtaggingSF_Skims_SingleMuon2017All_v00_nanoskim.root" ]

#Loop through events
treeIn = TChain("Events") #initialize TChain to store events from all files of interest
for f in list_file_data:
    fileIn_name = TString(file_Directory+f)  
    treeIn.Add(fileIn_name.Data())
    print("Using file: ", fileIn_name)
            
    rrv_weight = RooRealVar("rrv_weight","rrv_weight",0. ,10000000.)
    rdataset_mj     = RooDataSet("rdataset_mj","rdataset_mj",RooArgSet(rrv_mass_j,rrv_weight),RooFit.WeightVar(rrv_weight) )

            
    print("N entries: ", treeIn.GetEntries())
        
    print("rrv_mass_j.getMax() = " ,rrv_mass_j.getMax())
    print("rrv_mass_j.getMin() = " ,rrv_mass_j.getMin())
    tmp_event_weight = 1.
    i = 0
    testing = True        
    for i in range(treeIn.GetEntries()):
        if testing == True and i % 5000 == 0: 
            print("iEntry: ",i, "only considering these events -- TESTING MODE")
            event = treeIn.GetEntry(i)
            if not (treeIn.SelectedJet_pt > AK8_pt_min): continue 
            if not (treeIn.SelectedJet_pt < AK8_pt_max): continue
            
            jet_mass = "SelectedJet_sdB0_mass"
                
            if getattr(treeIn, jet_mass) > rrv_mass_j.getMax() and getattr(treeIn, jet_mass)< rrv_mass_j.getMin() : continue
                    
            tmp_jet_mass = getattr(treeIn, jet_mass);
            treeWeight = treeIn.GetWeight()
            if tmp_jet_mass > rrv_mass_j.getMin() and tmp_jet_mass < rrv_mass_j.getMax():
                rrv_mass_j.setVal(tmp_jet_mass)
                rdataset_mj.add(RooArgSet(rrv_mass_j), tmp_event_weight)

                print("Passed mass and pt cuts, adding ", i, " to rdataset")
        else:
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

                rdataset_mj.add(RooArgSet(rrv_mass_j), tmp_event_weight)

    rdataset_mj.Print("v")

#Plot data on frame
frame_mj_data = rrv_mass_j.frame(RooFit.Title("2017 muon skim data TEST"))
rdataset_mj.plotOn(frame_mj_data)

#now we make our pdf model --> for simplicity for now double gaussian
rrv_mean1_gaus  = RooRealVar("rrv_mean1_gaus","rrv_mean1_gaus"   ,80.,75.,87.)
rrv_sigma1_gaus = RooRealVar("rrv_sigma1_gaus" ,"rrv_sigma1_gaus" ,7.6,5.,16. )
rrv_mean2_gaus  = RooRealVar("rrv_mean2_gaus" ,"rrv_mean2_gaus"   ,170,150,180)
rrv_sigma2_gaus = RooRealVar("rrv_sigma2_gaus" ,"rrv_sigma2_gaus" ,13,10.,20. )
gaus1 = RooGaussian("gaus1" ,"gaus1" ,rrv_mass_j,rrv_mean1_gaus,rrv_sigma1_gaus)     
gaus2 = RooGaussian("gaus2" ,"gaus2" ,rrv_mass_j,rrv_mean2_gaus,rrv_sigma2_gaus)

rrv_frac2 = RooRealVar("rrv_frac2" ,"rrv_frac2" ,0.05,0.0,1.)

model_pdf = RooAddPdf("model_pdf","model_pdf",RooArgList(gaus1,gaus2),RooArgList(rrv_frac2),1)

#Now make extended model
print("Making extended model")
rrv_number = RooRealVar("rrv_number","number of events",500.,0.,1e5)
model_extended = RooExtendPdf("model_extended", "model_extended", model_pdf, rrv_number) #what should rrv number be? complicated in 

#Plot models
frame_mj_pdf = rrv_mass_j.frame(RooFit.Title("Double Gaussian PDF plot TEST"))
model_pdf.plotOn(frame_mj_pdf)
frame_mj_pdfExtended = rrv_mass_j.frame(RooFit.Title("Double Gaussian PDF plot TEST"))
model_pdf.plotOn(frame_mj_pdfExtended)

#draw frames on canvas
c = TCanvas("dataTest", "dataTest", 800, 400)
c.Divide(2, 2)
c.cd(1)
gPad.SetLeftMargin(0.15)
frame_mj_data.GetYaxis().SetTitleOffset(1.6)
frame_mj_data.Draw()
c.cd(2)
gPad.SetLeftMargin(0.15)
frame_mj_pdf.GetYaxis().SetTitleOffset(1.6)
frame_mj_pdf.Draw()
c.cd(3)
gPad.SetLeftMargin(0.15)
frame_mj_pdfExtended.GetYaxis().SetTitleOffset(1.6)
frame_mj_pdfExtended.Draw()

c.SaveAs("plotTest.png")
    
