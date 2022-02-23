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

#total dataset
rdataset_mj = workspace.data("rdataset_data_mj")
rdataset_mj.Print("v")
#totalMC
rdataset_mc_mj = workspace.data("rdataset_totalMC_mj")
#pass data
rdataset_data_pass_mj = workspace.data("rdataset_data_passtau21cut_mj")
#pass MC
rdataset_mc_pass_mj = workspace.data("rdataset_totalMC_passtau21cut_mj")

rrv_mass_j  = workspace.var("rrv_mass_j")

#convert mc to histpdf for plotting
hist_mc = rdataset_mc_pass_mj.binnedClone()
histpdf_mc = ROOT.RooHistPdf(rdataset_mc_pass_mj.GetName()+"_histpdf", rdataset_data_pass_mj.GetName()+"_histpdf", RooArgSet(rrv_mass_j), hist_mc)


#make frame for data
frame_mj = rrv_mass_j.frame(RooFit.Title("MC and Data fits PASS"),ROOT.RooFit.Bins(int(rrv_mass_j.getBins())) )
#make legend
legend = TLegend(0.6010112,0.7183362,0.8202143,0.919833)
legend.SetTextSize(0.032)
legend.SetLineColor(0)
legend.SetShadowColor(0)
legend.SetLineStyle(1)
legend.SetLineWidth(1)
legend.SetFillColor(0)
legend.SetFillStyle(0)
legend.SetMargin(0.35)

rrv_scale_number_mc = ROOT.RooRealVar("rrv_scale_number", "rrv_scale_number", (rdataset_mc_pass_mj.sumEntries()/rdataset_data_pass_mj.sumEntries()))
print(rdataset_mc_pass_mj.sumEntries())
print(rdataset_data_pass_mj.sumEntries())
#rescale
scale_number_mc = rrv_scale_number_mc.getValV()
#plot data
rdataset_data_pass_mj.plotOn(frame_mj)
#plot mc normalized to data
histpdf_mc.plotOn(frame_mj, ROOT.RooFit.MoveToBack(), ROOT.RooFit.DrawOption("F"), ROOT.RooFit.FillColor(414),ROOT.RooFit.LineColor(ROOT.kBlack))
#model_histpdf.plotOn(frame_mj) #, RooFit.Normalization(scale_number_mc), RooFit.DrawOption("F"), RooFit.FillColor(kMagenta))
#make frame for pdf before fit
frame_mj_pdf = rrv_mass_j.frame(RooFit.Title("DoubleGauss PDF before fit"))

def makePDF(workspace, label):
    #now we make our pdf model --> for simplicity for now double gaussian
    rrv_mean1_gaus  = RooRealVar("rrv_mean1_gaus_"+label, "rrv_mean1_gaus"+label, 80.,65.,100.)
    rrv_sigma1_gaus = RooRealVar("rrv_sigma1_gaus"+label ,"rrv_sigma1_gaus"+label ,10,5.,30.)
    rrv_mean2_gaus  = RooRealVar("rrv_mean2_gaus"+label ,"rrv_mean2_gaus"+label ,170,150,180)
    rrv_sigma2_gaus = RooRealVar("rrv_sigma2_gaus"+label ,"rrv_sigma2_gaus"+label ,13,5.,30.)
    gaus1 = RooGaussian("gaus1"+label ,"gaus1"+label ,rrv_mass_j,rrv_mean1_gaus,rrv_sigma1_gaus)     
    gaus2 = RooGaussian("gaus2"+label ,"gaus2"+label ,rrv_mass_j,rrv_mean2_gaus,rrv_sigma2_gaus)
    #adding an exponential
    rrv_const = RooRealVar("rrv_const"+label, "rrv_const"+label, -2.0e-02, -1., 1.)
    exp = RooExponential("exp"+label, "exp"+label, rrv_mass_j, rrv_const)


    rrv_frac1 = RooRealVar("rrv_frac1"+label ,"rrv_frac1"+label ,0.75,0.,1.)
    rrv_frac2 = RooRealVar("rrv_frac2"+label, "rrv_frac2"+label, 0.20,0.,1.)
    
    model_pdf = RooAddPdf("model_pdf"+label,"model_pdf"+label,RooArgList(gaus1,gaus2, exp),RooArgList(rrv_frac1, rrv_frac2),1)
    
    #Now make extended model
    print("Making extended model")
    rrv_number = RooRealVar("rrv_number","number of events",500.,0.,1e5)
    model_extended = RooExtendPdf("model_extendedpdf_"+label, "model_extendedpdf_"+label, model_pdf, rrv_number) #what should rrv number be? complicated in 
    
    #add pdf to workspace
    getattr(workspace, 'import')(model_extended)
    return workspace.pdf("model_extendedpdf_"+label)

    #plot model before fit
    model_extended.plotOn(frame_mj_pdf)

#do fit
model_extended_data = makePDF(workspace, "data") 
model_extended_mc = makePDF(workspace, "allMC")

fitResult_data_pass = model_extended_data.fitTo(rdataset_data_pass_mj, RooFit.Save(1), RooFit.Extended(1), RooFit.Verbose(1))
fitResult_mc_pass = model_extended_mc.fitTo(rdataset_mc_pass_mj, RooFit.Save(1), RooFit.Extended(1), RooFit.Verbose(1))
fitResult_data_pass.Print()
fitResult_mc_pass.Print()

#plot fit results on same frame as data and MC
model_extended_data.plotOn(frame_mj,ROOT.RooFit.LineStyle(ROOT.kSolid), ROOT.RooFit.LineColor(ROOT.kRed))
model_extended_mc.plotOn(frame_mj, ROOT.RooFit.LineStyle(ROOT.kSolid),ROOT.RooFit.LineColor(ROOT.kBlue))
#plot fit errors
#model_extended_data.plotOn(frame_mj, RooFit.DrawOption("F"), RooFit.VisualizeError(fitResult_data_pass,1), RooFit.Name("Fit error"),RooFit.FillColor(kGray))
#model_extended_mc.plotOn(frame_mj, RooFit.DrawOption("F"), RooFit.VisualizeError(fitResult_mc_pass,1), RooFit.Name("Fit error"))


#calculate efficiences


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
    
