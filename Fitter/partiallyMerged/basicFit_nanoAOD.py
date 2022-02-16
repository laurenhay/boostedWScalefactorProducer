import ROOT
from ROOT import *

# Set up component pdfs
# ---------------------------------------

# Declare observable x

#x = ROOT.RooRealVar("x", "x", 0, 10)

def MakePdf(workspace):

    rrv_x = workspace.var("rrv_mass_j")

    #Following from makepdf.py line 455 for data ONLY (applying signal data region fit to whole dataset), specifications founds in runSF_nanoAOD.py line 639 [DoubleSidedCB_ttbar_fitMC]
    #combined with roofit tutorial for extended range max liklhood fit rf204_extrangefit.py
    
    print("Making double gaussian pdf")
    
    # Create double sided crystal ball pdf and its parameters
    # rrv_mean = RooRealVar("mean1", "mean of gaussian", 89., 90., 100.)
    # rrv_sigma = RooRealVar("sigma1", "width of gaussian", 8., 5., 20.)
    # rrv_alpha1 = RooRealVar("alpha1", "left tail alpha", 0.5, 0.1, 10.)
    # rrv_alpha2 = RooRealVar("alpha2", "right tail alpha", 1.0, 0.1, 10.)
    # rrv_n1 = RooRealVar("n1", "right tail n", 0.2, 0.1, 5.)
    # rrv_n1 = RooRealVar("n2", "left tail n", 0.2, 0.1, 10.)
    
    #model_pdf = RooDoubleCrystalBall("model_pdf_data", "model_pdf_data", rrv_x, rv_mean, rrv_sigma, rrv_alpha1, rrv_n1, rrv_alpha2, rrv_n2)
    #see class reference https://root.cern/doc/master/classRooCrystalBall.html, alpha1 is left, alpha2 is right
    
    #custom DSCB is broken and this version of CMSSW's root version is old so the officail one isn't included
    rrv_mean1_gaus  = RooRealVar("rrv_mean1_gaus","rrv_mean1_gaus"   ,80.,75.,87.)
    rrv_sigma1_gaus = RooRealVar("rrv_sigma1_gaus" ,"rrv_sigma1_gaus" ,7.6,5.,16. )
    rrv_mean2_gaus  = RooRealVar("rrv_mean2_gaus" ,"rrv_mean2_gaus"   ,170,150,180)
    rrv_sigma2_gaus = RooRealVar("rrv_sigma2_gaus" ,"rrv_sigma2_gaus" ,13,10.,20. )
    gaus1 = RooGaussian("gaus1" ,"gaus1" ,rrv_x,rrv_mean1_gaus,rrv_sigma1_gaus)     
    gaus2 = RooGaussian("gaus2" ,"gaus2" ,rrv_x,rrv_mean2_gaus,rrv_sigma2_gaus)

    rrv_frac2 = RooRealVar("rrv_frac2" ,"rrv_frac2" ,0.05,0.0,1.)
    
    model_pdf = RooAddPdf("model_pdf","model_pdf",RooArgList(gaus1,gaus2),RooArgList(rrv_frac2),1)

    #Now make extended model
    print("Making extended model")
    rrv_number = RooRealVar("rrv_number","number of events",500.,0.,1e5)
    model_extended = RooExtendPdf("model_extended", "model_extended", model_pdf, rrv_number) #what should rrv number be? complicated in 


    #add signal and background region to make ranged fit
    
    getattr(workspace,'import')(model_extended)
    return workspace.pdf("model_extended")

doWS = False
class doFits:
    def __init__(self):
        filename = "workspace.root"
        print("Checking if workspace exists, if not, produce " ,filename)
        try: 
            os.stat(filename)
            doWS = False
            print("workspace found!")
        except: 
            doWS = True
        if doWS:
            print("no workspace found!")
            self.workspace4fit_  = RooWorkspace("workspace4fit_","workspace")
            self.workspace4fit_.writeToFile(filename)
        else:
            f = TFile(options.workspace.replace(".root","")+".root")
            self.workspace4fit_  = f.Get("workspace4fit_")
        workspace = self.workspace4fit_

        #now do everything necessary from initialiseFits class
        self.BinWidth_mj = 5.
        self.Narrow_factor = 1.

        in_mj_min = 50.
        in_mj_max = 130.
        self.AK8_pt_min = 200.
        self.AK8_pt_max = 10000.
        
        self.BinWidth_mj = self.BinWidth_mj/self.Narrow_factor
        nbins_mj         = int( (in_mj_max - in_mj_min) / self.BinWidth_mj )
        in_mj_max        = in_mj_min+nbins_mj*self.BinWidth_mj
      

        rrv_mass_j = RooRealVar("rrv_mass_j", "PUPPI softdrop jet mass" ,(in_mj_min+in_mj_max)/2.,in_mj_min,in_mj_max,"GeV")
        rrv_mass_j.setBins(nbins_mj)
        
        #import fit variable to existing workspace
        getattr(self.workspace4fit_,'import')(rrv_mass_j)

        # Directory and input files
        self.reDirector = "root://cmseos.fnal.gov/"   
        self.file_Directory         =  self.reDirector +  "/store/user/camclean/boostedWtaggingSF/haddsWithLumiWeight/"

        self.list_file_data       = ["boostedWtaggingSF_Skims_SingleMuon2017All_v00_nanoskim.root" ]
#        self.list_file_data       = [ ]

        #get data
        self.getData(self.list_file_data, testing = True)

        #fit
        model = MakePdf(workspace)

        #quick and dirty "data" generation for testing
        x = ROOT.RooRealVar("x", "x", 50, 150)
        data = model.generate(RooArgSet(x), 1000)
        dataset = workspace.data("rdataset_mj")
        dataset.Print("v")
 #       fitResult_data = model.fitTo(workspace.data("rdataset_mj"), RooFit.Save(1), RooFit.Extended(1))
        fitResult_data = model.fitTo(data, RooFit.Save(1), RooFit.Extended(1)) #this works
        

        xframe = rrv_mass_j.frame(RooFit.Title("loaded data")) 
        xframe2 = x.frame(RooFit.Title("Gaussian p.d.f. with fake data"))  # RooPlot
#        dataset.plotOn(xframe, RooFit.DataError(RooAbsData.Poisson),RooFit.Name(dataset.GetName())) #broken
        data.plotOn(xframe2)
        model.plotOn(xframe2)
        
        # Draw all frames on a canvas
        c = ROOT.TCanvas("rf101_basics", "rf101_basics", 800, 400)
        c.Divide(2)
        c.cd(1)
        ROOT.gPad.SetLeftMargin(0.15)
        xframe.GetYaxis().SetTitleOffset(1.6)
        xframe.Draw()
        c.cd(2)
        ROOT.gPad.SetLeftMargin(0.15)
        xframe2.GetYaxis().SetTitleOffset(1.6)
        xframe2.Draw()
        
        
        c.SaveAs("rf101_basics.png")
    
#        plots = drawPlots(x, fitResult_data, data, model)
        del self.workspace4fit_

    def getData(self, list_file_data, testing = False):
        #Loop through events
        treeIn = TChain("Events") #initialize TChain to store events from all files of interest
        for f in list_file_data:
            fileIn_name = TString(self.file_Directory+f)  
            treeIn.Add(fileIn_name.Data())
            print("Using file: ", fileIn_name)
            
            rrv_mass_j = self.workspace4fit_.var("rrv_mass_j")
            rrv_weight = RooRealVar("rrv_weight","rrv_weight",0. ,10000000.)


            rdataset_mj     = RooDataSet("rdataset_mj","rdataset_mj",RooArgSet(rrv_mass_j,rrv_weight),RooFit.WeightVar(rrv_weight) )
            rdataset4fit_mj     = RooDataSet("rdataset4fit_data_mj","rdataset_mj",RooArgSet(rrv_mass_j,rrv_weight),RooFit.WeightVar(rrv_weight) )
            
            print("N entries: ", treeIn.GetEntries())
        
            print("rrv_mass_j.getMax() = " ,rrv_mass_j.getMax())
            print("rrv_mass_j.getMin() = " ,rrv_mass_j.getMin())
            tmp_scale_to_lumi = 1.
            tmp_event_weight = 1.
            tmp_event_weight4fit = 1.
            i = 0
            
            SF = 1.0
            for i in range(treeIn.GetEntries()):
                if testing == True and i % 5000 == 0: 
                    print("iEntry: ",i, "only storing these -- testing = True")
                    event = treeIn.GetEntry(i)
                    if not (treeIn.SelectedJet_pt > self.AK8_pt_min): continue 
                    if not (treeIn.SelectedJet_pt < self.AK8_pt_max): continue
                
                    jet_mass = "SelectedJet_sdB0_mass"
                
                    if getattr(treeIn, jet_mass) > rrv_mass_j.getMax() and getattr(treeIn, jet_mass)< rrv_mass_j.getMin() : continue
                    
                    tmp_jet_mass = getattr(treeIn, jet_mass);
                    treeWeight = treeIn.GetWeight()
                    if tmp_jet_mass > rrv_mass_j.getMin() and tmp_jet_mass < rrv_mass_j.getMax():
                        rrv_mass_j.setVal(tmp_jet_mass)

                        rdataset_mj    .add(RooArgSet(rrv_mass_j), tmp_event_weight)
                        rdataset4fit_mj.add(RooArgSet(rrv_mass_j), tmp_event_weight4fit)
                        print("Added ", i, " to rdataset")
                else:
                    if i % 5000 == 0: print("iEntry: ",i, " storing all")
                    event = treeIn.GetEntry(i)
                    if not (treeIn.SelectedJet_pt > self.AK8_pt_min): continue
                    if not (treeIn.SelectedJet_pt < self.AK8_pt_max): continue

                    jet_mass = "SelectedJet_sdB0_mass"

                    if getattr(treeIn, jet_mass) > rrv_mass_j.getMax() and getattr(treeIn, jet_mass)< rrv_mass_j.getMin() : continue
                    tmp_jet_mass = getattr(treeIn, jet_mass);
                    treeWeight = treeIn.GetWeight()
                    if tmp_jet_mass > rrv_mass_j.getMin() and tmp_jet_mass < rrv_mass_j.getMax():
                        rrv_mass_j.setVal(tmp_jet_mass)

                        rdataset_mj    .add(RooArgSet(rrv_mass_j), tmp_event_weight)
                        rdataset4fit_mj.add(RooArgSet(rrv_mass_j), tmp_event_weight4fit)
              
        #if designation signal/bg regions sort here (see line 1076 of runSF_nanoAOD.py --> ADD THIS LATER
#        rrv_scale_to_lumi= RooRealVar("rrv_scale_to_lumi_data","rrv_scale_to_lumi_data",tmp_scale_to_lumi*SF)    
#        getattr(self.workspace4fit_,"import")(rrv_scale_to_lumi) #do i need this?
        #do I need an rrv_number?
        getattr(self.workspace4fit_,"import")(rdataset_mj)
        getattr(self.workspace4fit_,"import")(rdataset4fit_mj)    
    
#add plotting
c1 = ROOT.TCanvas("test","test",800,800) 
def drawPlots(variable, fitResult, dataset, pdfModel):
    frame = variable.frame()
    dataset.plotOn(frame,RooFit.DataError(RooAbsData.Poisson),RooFit.Name(dataset.GetName ()))
    pdfModel.plotOn(frame,RooFit.VisualizeError(fitResult,1), RooFit.Name("Fit error"),RooFit.FillColor(kGray),RooFit.LineColor(kGray)) #,RooFit.Normalization(1.0,RooAbsReal.RelativeExpected))
    pdfModel.plotOn(frame,RooFit.LineColor(kBlack),RooFit.Name(pdfModel.GetName())) #,RooFit.Normalization(1.0,RooAbsReal.RelativeExpected))
    chi2 = frame.chiSquare(pdfModel.GetName(), dataset.GetName (), -2)
    dataset.plotOn(frame,RooFit.DataError(RooAbsData.Poisson),RooFit.Name(dataset.GetName ())) #why twice?
    c1.cd()
    frame.GetYaxis().SetNdivisions(203);
    frame.GetXaxis().SetNdivisions(202);
    labelsize = 0.02
    frame.GetYaxis().SetTitleSize(0.001)
    frame.GetXaxis().SetTitleSize(0.001)
    frame.GetYaxis().SetTitleOffset(1.7) #1.35
    frame.SetName("mjjFit")
    frame.GetYaxis().SetTitle("A.U")
    frame.GetXaxis().SetTitle(title)
    frame.Draw("a")
    #add legend info
    #add pavetext
    c1.Update()
    c1.Modified()
    dirname = "plots/"+options.workspace.replace('workspace_', '')
    c1.SaveAs(dirname+"/"+pdfModel.GetName()+".png")
    c1.SaveAs(dirname+"/"+pdfModel.GetName()+".pdf")
    c1.SaveAs(dirname+"/"+pdfModel.GetName()+".root")
    c1.SaveAs(dirname+"/"+pdfModel.GetName()+".C")
    return chi2


### Start  main
if __name__ == '__main__':
    boostedW_fitter = doFits()
