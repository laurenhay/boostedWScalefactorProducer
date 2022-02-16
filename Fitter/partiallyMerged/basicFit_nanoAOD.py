import ROOT
from ROOT import *
#DON'T USE FUNCTIONS, WE BREAK LIKE MEN
#Currently compatible with CMSSW_12_0
#run with python3

#open workspace written by makeRooDataset.py and load RooDataSet
filename = "workspace.root"
try: 
    os.stat(filename)
    print("Workspace root file found.")
except:
    print("Workspace root file now found -- please run makeRooDataset first")
f = TFile(filename)
workspace = f.Get("workspace")
rdataset_mj = workspace.data("rdataset_mj")
rrv_mass_j  = workspace.var("rrv_mass_j")
rdataset_mj.Print("v")

#Plot data on frame
frame_mj = rrv_mass_j.frame(RooFit.Title("2017 muon skim data TEST"))
rdataset_mj.plotOn(frame_mj)

#now we make our pdf model --> for simplicity for now double gaussian
rrv_mean1_gaus  = RooRealVar("rrv_mean1_gaus","rrv_mean1_gaus"   ,80.,65.,100.)
rrv_sigma1_gaus = RooRealVar("rrv_sigma1_gaus" ,"rrv_sigma1_gaus" ,10,5.,30.)
rrv_mean2_gaus  = RooRealVar("rrv_mean2_gaus" ,"rrv_mean2_gaus"   ,170,150,180)
rrv_sigma2_gaus = RooRealVar("rrv_sigma2_gaus" ,"rrv_sigma2_gaus" ,13,5.,30.)
gaus1 = RooGaussian("gaus1" ,"gaus1" ,rrv_mass_j,rrv_mean1_gaus,rrv_sigma1_gaus)     
gaus2 = RooGaussian("gaus2" ,"gaus2" ,rrv_mass_j,rrv_mean2_gaus,rrv_sigma2_gaus)
#adding an exponential
rrv_const = RooRealVar("rrv_const", "rrv_const", -2.0e-02, -1., 1.)
exp = RooExponential("exp", "exp", rrv_mass_j, rrv_const)


rrv_frac1 = RooRealVar("rrv_frac1" ,"rrv_frac1" ,0.60,0.,1.)
rrv_frac2 = RooRealVar("rrv_frac2", "rrv_frac2", 0.20,0.,1.)

model_pdf = RooAddPdf("model_pdf","model_pdf",RooArgList(gaus1,gaus2, exp),RooArgList(rrv_frac1, rrv_frac2),1)

#Now make extended model
print("Making extended model")
rrv_number = RooRealVar("rrv_number","number of events",500.,0.,1e5)
model_extended = RooExtendPdf("model_extended", "model_extended", model_pdf, rrv_number) #what should rrv number be? complicated in 

#plot model before fit
frame_mj_pdf = rrv_mass_j.frame(RooFit.Title("Double Gaussian PDF plot TEST"))
model_extended.plotOn(frame_mj_pdf)

#do fit
fitResult = model_extended.fitTo(rdataset_mj, RooFit.Save(1), RooFit.Extended(1), RooFit.Verbose(1))

#plot fit result error
model_pdf.plotOn(frame_mj, RooFit.DrawOption("F"), RooFit.VisualizeError(fitResult,1), RooFit.Name("Fit error"),RooFit.FillColor(kGray),RooFit.LineColor(kGray))
model_pdf.plotOn(frame_mj_pdf, RooFit.DrawOption("F"), RooFit.VisualizeError(fitResult,1), RooFit.Name("Fit error"),RooFit.FillColor(kGray))
model_extended.plotOn(frame_mj)


#draw frames on canvas
c = TCanvas("dataTest", "dataTest", 800, 400)
c.Divide(2)
c.cd(1)
gPad.SetLeftMargin(0.15)
frame_mj.GetYaxis().SetTitleOffset(1.6)
frame_mj.Draw()
c.cd(2)
gPad.SetLeftMargin(0.15)
frame_mj_pdf.GetYaxis().SetTitleOffset(1.6)
frame_mj_pdf.Draw()

c.SaveAs("plotTest.png")
    
