from optparse import OptionParser

import ROOT

#Currently compatible with CMSSW_12_0
#run with python3

#open workspace written by makeRooDataset.py and load RooDataSet

parser = OptionParser()

parser.add_option('--workspace', action="store",type="string",dest="workspace",default="workspace", help="Name of workspace")
parser.add_option('--mass_var', action="store",type="string",dest="mass_var",default="", help="jet mass grooming variable")

(options, args) = parser.parse_args()


print(options.workspace)
filename = options.workspace.replace(".root","")+".root"

try: 
    os.stat(filename)
    print("Workspace root file found.")
except:
    print("Workspace root file now found -- please run makeRooDataset first")
f = ROOT.TFile(filename)
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
#set signal range
rrv_mass_j.setRange("signal_region",65,105)

#convert mc to histpdf for plotting
hist_mc = rdataset_mc_pass_mj.binnedClone()
histpdf_mc = ROOT.RooHistPdf(rdataset_mc_pass_mj.GetName()+"_histpdf", rdataset_data_pass_mj.GetName()+"_histpdf", ROOT.RooArgSet(rrv_mass_j), hist_mc)


#make frame for data
frame_mj = rrv_mass_j.frame(ROOT.RooFit.Title("Fits for Jet Mass "+options.mass_var),ROOT.RooFit.Bins(int(rrv_mass_j.getBins())) )

rrv_scale_number_mc = ROOT.RooRealVar("rrv_scale_number", "rrv_scale_number", (rdataset_mc_pass_mj.sumEntries()/rdataset_data_pass_mj.sumEntries()))
print(rdataset_mc_pass_mj.sumEntries())
print(rdataset_data_pass_mj.sumEntries())
#rescale
scale_number_mc = rrv_scale_number_mc.getValV()
#plot data
rdataset_data_pass_mj.plotOn(frame_mj, ROOT.RooFit.Name("data"))
#plot mc normalized to data
histpdf_mc.plotOn(frame_mj, ROOT.RooFit.Name("MC"), ROOT.RooFit.MoveToBack(), ROOT.RooFit.DrawOption("F"), ROOT.RooFit.FillColor(414),ROOT.RooFit.LineColor(ROOT.kBlack))
histpdf_mc.plotOn(frame_mj, ROOT.RooFit.Name("MC_invisible"), ROOT.RooFit.LineColor(ROOT.kBlack), ROOT.RooFit.LineWidth(2))

#model_histpdf.plotOn(frame_mj) #, ROOT.RooFit.Normalization(scale_number_mc), ROOT.RooFit.DrawOption("F"), ROOT.RooFit.FillColor(kMagenta))
#make frame for pdf before fit
frame_mj_pdf = rrv_mass_j.frame(ROOT.RooFit.Title("Gauss PDF before fit"))

def makePDF(workspace, label):
    #now we make our pdf model --> for simplicity for now double gaussian
    rrv_mean1_gaus  = ROOT.RooRealVar("rrv_mean1_gaus_"+label, "rrv_mean1_gaus_"+label, 80.,65.,100.)
    rrv_sigma1_gaus = ROOT.RooRealVar("rrv_sigma1_gaus_"+label ,"rrv_sigma1_gaus_"+label ,10,5.,30.)
    #rrv_mean2_gaus  = ROOT.RooRealVar("rrv_mean2_gaus"+label ,"rrv_mean2_gaus"+label ,170,150,180)
    #rrv_sigma2_gaus = ROOT.RooRealVar("rrv_sigma2_gaus"+label ,"rrv_sigma2_gaus"+label ,13,5.,30.)
    gaus1 = ROOT.RooGaussian("gaus1_"+label ,"gaus1_"+label ,rrv_mass_j,rrv_mean1_gaus,rrv_sigma1_gaus)     
    #gaus2 = ROOT.RooGaussian("gaus2"+label ,"gaus2"+label ,rrv_mass_j,rrv_mean2_gaus,rrv_sigma2_gaus)
    
    #adding an exponential
    rrv_const = ROOT.RooRealVar("rrv_const_"+label, "rrv_const_"+label, -2.0e-02, -1., 1.)
    exp = ROOT.RooExponential("exp"+label, "exp"+label, rrv_mass_j, rrv_const)
    


    rrv_frac1 = ROOT.RooRealVar("rrv_frac1_"+label ,"rrv_frac1_"+label ,0.99,0.,1.)
#    rrv_frac2 = ROOT.RooRealVar("rrv_frac2"+label, "rrv_frac2"+label, 0.10,0.,1.)
    
#    model_pdf = ROOT.RooAddPdf("model_pdf"+label,"model_pdf"+label,ROOT.RooArgList(gaus1,gaus2, exp),ROOT.RooArgList(rrv_frac1, rrv_frac2),1)
    model_pdf = gaus1
#    model_pdf = ROOT.RooAddPdf("model_pdf_"+label,"model_pdf_"+label,ROOT.RooArgList(gaus1,exp),ROOT.RooArgList(rrv_frac1),1)
    #Now make extended model
    print("Making extended model")
    rrv_number = ROOT.RooRealVar("rrv_number","number of events",500.,0.,1e5)
    model_extended = ROOT.RooExtendPdf("model_extendedpdf_"+label, "model_extendedpdf_"+label, model_pdf, rrv_number) #what should rrv number be? complicated in 
    
    #add pdf to workspace
    getattr(workspace, 'import')(model_extended)
    return workspace.pdf("model_extendedpdf_"+label)

#make models
model_extended_data = makePDF(workspace, "data") 
model_extended_mc = makePDF(workspace, "allMC")

#plot model before fit
model_extended_mc.plotOn(frame_mj_pdf)

#do fits
fitResult_data_pass = model_extended_data.fitTo(rdataset_data_pass_mj, ROOT.RooFit.Save(1), ROOT.RooFit.Extended(1), ROOT.RooFit.Verbose(0), ROOT.RooFit.Range("signal_region"))
fitResult_mc_pass = model_extended_mc.fitTo(rdataset_mc_pass_mj, ROOT.RooFit.Save(1), ROOT.RooFit.Extended(1), ROOT.RooFit.Verbose(0), ROOT.RooFit.Range("signal_region"))
fitResult_data_pass.Print()
fitResult_mc_pass.Print()

#plot fit results on same frame as data and MC
model_extended_data.plotOn(frame_mj,ROOT.RooFit.Name("Data fit"), ROOT.RooFit.LineStyle(ROOT.kSolid), ROOT.RooFit.LineColor(ROOT.kRed))
model_extended_mc.plotOn(frame_mj, ROOT.RooFit.Name("MC fit"), ROOT.RooFit.LineStyle(ROOT.kSolid),ROOT.RooFit.LineColor(ROOT.kBlue))
#plot fit errors
#model_extended_data.plotOn(frame_mj, ROOT.RooFit.DrawOption("F"), ROOT.RooFit.VisualizeError(fitResult_data_pass,1), ROOT.RooFit.Name("Fit error"),ROOT.RooFit.FillColor(kGray))
#model_extended_mc.plotOn(frame_mj, ROOT.RooFit.DrawOption("F"), ROOT.RooFit.VisualizeError(fitResult_mc_pass,1), ROOT.RooFit.Name("Fit error"))


#make legend
legend = ROOT.TLegend(0.6010112,0.7183362,0.8202143,0.919833)
legend.SetTextSize(0.032)
legend.SetLineColor(0)
legend.SetShadowColor(0)
legend.SetLineStyle(1)
legend.SetLineWidth(1)
legend.SetFillColor(0)
legend.SetFillStyle(0)
legend.SetMargin(0.35)
legend.AddEntry(frame_mj.findObject("data")       ,"Data"                ,"PLE");
legend.AddEntry(frame_mj.findObject("MC")       ,"MC"                ,"F");
legend.AddEntry(frame_mj.findObject("Data fit")   ,"Data fit"            ,"L");
legend.AddEntry(frame_mj.findObject("MC fit")     ,"MC fit"              ,"L");
frame_mj.addObject(legend)



rrv_mean_gaus_mc = workspace.var("rrv_mean1_gaus_allMC")
rrv_sigma_gaus_mc = workspace.var("rrv_sigma1_gaus_allMC")
rrv_mean_gaus_data = workspace.var("rrv_mean1_gaus_data")
rrv_sigma_gaus_data = workspace.var("rrv_sigma1_gaus_data")

data_over_mc_mean = rrv_mean_gaus_data.getVal()/rrv_mean_gaus_mc.getVal()
data_over_mc_mean_error = data_over_mc_mean*((rrv_mean_gaus_data.getError()/rrv_mean_gaus_data.getVal())**2+(rrv_mean_gaus_mc.getError()/rrv_mean_gaus_mc.getVal())**2 )**0.5

data_over_mc_sigma = rrv_sigma_gaus_data.getVal()/rrv_sigma_gaus_mc.getVal()
data_over_mc_sigma_error = data_over_mc_sigma*((rrv_sigma_gaus_data.getError()/rrv_sigma_gaus_data.getVal())**2+(rrv_sigma_gaus_mc.getError()/rrv_sigma_gaus_mc.getVal())**2 )**0.5

print("JMS (data/MC) = ", data_over_mc_mean, " +/- ", data_over_mc_mean_error)
print("JMR (data/MC) = ", data_over_mc_sigma, " +/- ", data_over_mc_sigma_error)

#draw fit parameters
tl_MC_mean  = ROOT.TLatex(0.75,0.62, ("#mu_{MC } = %3.2f #pm %2.2f")%(rrv_mean_gaus_mc.getVal(), rrv_mean_gaus_mc.getError()) );
tl_MC_sigma = ROOT.TLatex(0.75,0.57, ("#sigma_{MC }= %2.2f #pm %2.2f")%(rrv_sigma_gaus_mc.getVal(), rrv_sigma_gaus_mc.getError()) );
tl_MC_mean.SetNDC(); tl_MC_sigma.SetNDC();
tl_MC_mean.SetTextSize(0.03)
tl_MC_sigma.SetTextSize(0.03)
frame_mj.addObject(tl_MC_mean);
frame_mj.addObject(tl_MC_sigma);

tl_data_mean  = ROOT.TLatex(0.75,0.52, ("#mu_{data } = %3.2f #pm %2.2f")%(rrv_mean_gaus_data.getVal(), rrv_mean_gaus_data.getError()) );
tl_data_sigma = ROOT.TLatex(0.75,0.47, ("#sigma_{data }= %2.2f #pm %2.2f")%(rrv_sigma_gaus_data.getVal(), rrv_sigma_gaus_data.getError()) );
tl_data_mean.SetNDC(); tl_data_sigma.SetNDC();
tl_data_mean.SetTextSize(0.03)
tl_data_sigma.SetTextSize(0.03)
frame_mj.addObject(tl_data_mean);
frame_mj.addObject(tl_data_sigma);

tl_scale  = ROOT.TLatex(0.75,0.42, ("JMS_{data/MC} = %3.2f #pm %2.2f")%(data_over_mc_mean, data_over_mc_mean_error) );
tl_resolution = ROOT.TLatex(0.75,0.37, ("JMR_{data/MC}= %2.2f #pm %2.2f")%(data_over_mc_sigma, data_over_mc_sigma_error) );
tl_scale.SetNDC(); tl_resolution.SetNDC();
tl_scale.SetTextSize(0.03)
tl_resolution.SetTextSize(0.03)
frame_mj.addObject(tl_scale);
frame_mj.addObject(tl_resolution);


#draw frames on canvas
c = ROOT.TCanvas("dataTest", "dataTest", 1000, 800)
#c.Divide(2)
#c.cd(1)
ROOT.gPad.SetLeftMargin(0.15)
frame_mj.GetYaxis().SetTitleOffset(1.6)
frame_mj.Draw()
# c.cd(2)
# ROOT.gPad.SetLeftMargin(0.15)
# frame_mj_pdf.GetYaxis().SetTitleOffset(1.6)
# frame_mj_pdf.Draw()

c.SaveAs("Gaus_"+options.mass_var+"_range65_105.png")
    
