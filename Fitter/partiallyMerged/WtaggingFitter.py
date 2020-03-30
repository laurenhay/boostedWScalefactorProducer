import ROOT
from WTopScalefactorProducer.Fitter.tdrstyle import *
from InitialiseFits import initialiseFits


class doWtagFits:
    def __init__(self, options):
        
        # --- Open the workspace
        self.workspace4fit_ = self.OpenWorkspace(options)

        self.boostedW_fitter_em = initialiseFits(options, "em", self.workspace4fit_)   # Define all shapes to be used for Mj, define regions (SB,signal) and input files. 
        self.boostedW_fitter_em.get_datasets_fit_minor_bkg(options)                    # Loop over intrees to create datasets om Mj and fit the single MCs.
       
#        print "Printing workspace:"; self.workspace4fit_ .Print(); print ""
        workspace4fit_ = self.workspace4fit_
        self.boostedW_fitter_em.get_sim_fit_components()     
        
        print "Define categories:"

        #Defining categories
        sample_type = RooCategory("sample_type","sample_type")
        sample_type.defineType("em_pass")
        sample_type.defineType("em_fail")
        getattr(workspace4fit_,'import')(sample_type)

        #Importing fit variables
        rrv_mass_j = workspace4fit_.var("rrv_mass_j")
        rrv_weight = RooRealVar("rrv_weight","rrv_weight",0. ,10000000.)
        
        #-------------IMPORT DATA-------------
        print "Importing datasets"
        rdataset_data_em_mj      = workspace4fit_.data("rdataset_data_em_mj")
        rdataset_data_em_mj_fail = workspace4fit_.data("rdataset_data_failtau2tau1cut_em_mj")

        #For binned fit (shorter computing time, more presise when no SumW2Error is used!)
        if options.doBinnedFit:
          #Converting to RooDataHist
          rdatahist_data_em_mj      = RooDataHist(rdataset_data_em_mj.binnedClone())
          rdatahist_data_em_mj_fail = RooDataHist(rdataset_data_em_mj_fail.binnedClone())

          #Converting back to RooDataSet
          rdataset_data_em_mj_2 = rdataset_data_em_mj.emptyClone()
          for i in range(0,rdatahist_data_em_mj.numEntries()):
            rdataset_data_em_mj_2.add(rdatahist_data_em_mj.get(i),rdatahist_data_em_mj.weight())

          rdataset_data_em_mj_fail_2 = rdataset_data_em_mj_fail.emptyClone()
          for i in range(0,rdatahist_data_em_mj_fail.numEntries()):
            rdataset_data_em_mj_fail_2.add(rdatahist_data_em_mj_fail.get(i),rdatahist_data_em_mj_fail.weight())

          #Combined dataset
          combData_data = RooDataSet("combData_data","combData_data",RooArgSet(rrv_mass_j,rrv_weight),RooFit.WeightVar(rrv_weight),RooFit.Index(sample_type),RooFit.Import("em_pass",rdataset_data_em_mj_2),RooFit.Import("em_fail",rdataset_data_em_mj_fail_2) )

        #For unbinned fit
        else:
          combData_data = RooDataSet("combData_data","combData_data",RooArgSet(rrv_mass_j,rrv_weight),RooFit.WeightVar(rrv_weight),RooFit.Index(sample_type),RooFit.Import("em_pass",rdataset_data_em_mj),RooFit.Import("em_fail",rdataset_data_em_mj_fail) )

        #Combined dataset for plotting
        combData_data_plot = RooDataSet("combData_data_plot","combData_data_plot",RooArgSet(rrv_mass_j,rrv_weight),RooFit.WeightVar(rrv_weight),RooFit.Index(sample_type),RooFit.Import("em_pass",rdataset_data_em_mj),RooFit.Import("em_fail",rdataset_data_em_mj_fail) )
        
        
        #-------------IMPORT MC-------------
        #Importing MC datasets
        rdataset_TotalMC_em_mj      = self.workspace4fit_.data("rdataset_TotalMC_em_mj")
        rdataset_TotalMC_em_mj_fail = self.workspace4fit_.data("rdataset_TotalMC_failtau2tau1cut_em_mj")

        if options.doBinnedFit:
          #Converting to RooDataHist
          rdatahist_TotalMC_em_mj      = RooDataHist(rdataset_TotalMC_em_mj.binnedClone())
          rdatahist_TotalMC_em_mj_fail = RooDataHist(rdataset_TotalMC_em_mj_fail.binnedClone())

          #Converting back to RooDataSet
          rdataset_TotalMC_em_mj_2 = rdataset_TotalMC_em_mj.emptyClone()
          for i in range(0,rdatahist_TotalMC_em_mj.numEntries()):
            rdataset_TotalMC_em_mj_2.add(rdatahist_TotalMC_em_mj.get(i),rdatahist_TotalMC_em_mj.weight())

          rdataset_TotalMC_em_mj_fail_2 = rdataset_TotalMC_em_mj_fail.emptyClone()
          for i in range(0,rdatahist_TotalMC_em_mj_fail.numEntries()):
            rdataset_TotalMC_em_mj_fail_2.add(rdatahist_TotalMC_em_mj_fail.get(i),rdatahist_TotalMC_em_mj_fail.weight())

          #Combined MC dataset
          combData_TotalMC = RooDataSet("combData_TotalMC","combData_TotalMC",RooArgSet(rrv_mass_j,rrv_weight),RooFit.WeightVar(rrv_weight),RooFit.Index(sample_type),RooFit.Import("em_pass",rdataset_TotalMC_em_mj_2),RooFit.Import("em_fail",rdataset_TotalMC_em_mj_fail_2) )
         
        else:
         combData_TotalMC = RooDataSet("combData_TotalMC","combData_TotalMC",RooArgSet(rrv_mass_j,rrv_weight),RooFit.WeightVar(rrv_weight),RooFit.Index(sample_type),RooFit.Import("em_pass",rdataset_TotalMC_em_mj),RooFit.Import("em_fail",rdataset_TotalMC_em_mj_fail) )

        #Combined MC dataset for plotting
        combData_TotalMC_plot = RooDataSet("combData_TotalMC_plot","combData_TotalMC_plot",RooArgSet(rrv_mass_j,rrv_weight),RooFit.WeightVar(rrv_weight),RooFit.Index(sample_type),RooFit.Import("em_pass",rdataset_TotalMC_em_mj),RooFit.Import("em_fail",rdataset_TotalMC_em_mj_fail) )
        
        #-------------Define and perform fit to data-------------
        print "Import pdf from single fits and define the simultaneous total pdf"
        model_data_em      = self.workspace4fit_.pdf("model_data_em")
        model_data_fail_em = self.workspace4fit_.pdf("model_data_failtau2tau1cut_em")

        simPdf_data = RooSimultaneous("simPdf_data_em","simPdf_data_em",sample_type)
        simPdf_data.addPdf(model_data_em,"em_pass")
        simPdf_data.addPdf(model_data_fail_em,"em_fail")

        print "Import Gaussian constraints to propagate error to likelihood"
        constrainslist_data_em = []
        for i in range(len(self.boostedW_fitter_em.constrainslist_data)):
            constrainslist_data_em.append(self.boostedW_fitter_em.constrainslist_data[i])
            print self.boostedW_fitter_em.constrainslist_data[i]
        pdfconstrainslist_data_em = RooArgSet("pdfconstrainslist_data_em")
        for i in range(len(constrainslist_data_em)):
          pdfconstrainslist_data_em.add(self.workspace4fit_.pdf(constrainslist_data_em[i]) )
          pdfconstrainslist_data_em.Print()

        from WTopScalefactorProducer.Fitter.fitutils import pdfDSCBtoGAUS, pdfGAUStoDSCB

        print " Perform simultaneous fit to data"
        pdfDSCBtoGAUS(self.workspace4fit_, "data")
        rfresult_data = simPdf_data.fitTo(combData_data,RooFit.Save(kTRUE),RooFit.Verbose(kFALSE), RooFit.Minimizer("Minuit"),RooFit.Strategy(0),RooFit.ExternalConstraints(pdfconstrainslist_data_em))
        pdfGAUStoDSCB(self.workspace4fit_, "data")
        rfresult_data = simPdf_data.fitTo(combData_data,RooFit.Save(kTRUE),RooFit.Verbose(kFALSE), RooFit.Minimizer("Minuit"),RooFit.Strategy(0),RooFit.ExternalConstraints(pdfconstrainslist_data_em))
        
#        if options.doBinnedFit:
#          rfresult_data = simPdf_data.fitTo(combData_data,RooFit.Save(kTRUE),RooFit.Verbose(kFALSE), RooFit.Minimizer("Minuit"),RooFit.ExternalConstraints(pdfconstrainslist_data_em))
#          # rfresult_data = simPdf_data.fitTo(combData_data,RooFit.Save(kTRUE),RooFit.Verbose(kFALSE), RooFit.Minimizer("Minuit2"),RooFit.ExternalConstraints(pdfconstrainslist_data_em))
#          # rfresult_data = simPdf_data.fitTo(combData_data,RooFit.Save(kTRUE),RooFit.Verbose(kFALSE), RooFit.Minimizer("Minuit2"),RooFit.ExternalConstraints(pdfconstrainslist_data_em))
#        else:
#          rfresult_data = simPdf_data.fitTo(combData_data,RooFit.Save(kTRUE),RooFit.Verbose(kFALSE), RooFit.Minimizer("Minuit"),RooFit.ExternalConstraints(pdfconstrainslist_data_em))
#          # rfresult_data = simPdf_data.fitTo(combData_data,RooFit.Save(kTRUE),RooFit.Verbose(kFALSE), RooFit.Minimizer("Minuit2"),RooFit.ExternalConstraints(pdfconstrainslist_data_em))
#          # rfresult_data = simPdf_data.fitTo(combData_data,RooFit.Save(kTRUE),RooFit.Verbose(kFALSE), RooFit.Minimizer("Minuit2"),RooFit.ExternalConstraints(pdfconstrainslist_data_em))
        
        
        getattr(workspace4fit_,'import')(combData_data_plot)
        getattr(workspace4fit_,'import')(simPdf_data)
        
        print "Draw"       
        isData = True
        chi2FailData = drawFrameGetChi2(rrv_mass_j,rfresult_data,rdataset_data_em_mj_fail,model_data_fail_em,isData)
        chi2PassData = drawFrameGetChi2(rrv_mass_j,rfresult_data,rdataset_data_em_mj,model_data_em,isData)

        #Print final data fit results
        print "FIT parameters (DATA) :"; print ""
        print "CHI2 PASS = %.3f    CHI2 FAIL = %.3f" %(chi2PassData,chi2FailData)
        print ""; print rfresult_data.Print(); print ""

        #-------------Define and perform fit to MC-------------

        # fit TotalMC --> define the simultaneous total pdf
        model_TotalMC_em      = self.workspace4fit_.pdf("model_TotalMC_em")
        model_TotalMC_fail_em = self.workspace4fit_.pdf("model_TotalMC_failtau2tau1cut_em")
        simPdf_TotalMC = RooSimultaneous("simPdf_TotalMC_em","simPdf_TotalMC_em",sample_type)
        simPdf_TotalMC.addPdf(model_TotalMC_em,"em_pass")
        simPdf_TotalMC.addPdf(model_TotalMC_fail_em,"em_fail")
        
        #Import Gaussian constraints  for fixed paramters to propagate error to likelihood
        constrainslist_TotalMC_em =[]
        for i in range(len(self.boostedW_fitter_em.constrainslist_mc)):
            constrainslist_TotalMC_em.append(self.boostedW_fitter_em.constrainslist_mc[i])
        pdfconstrainslist_TotalMC_em = RooArgSet("pdfconstrainslist_TotalMC_em")
        for i in range(len(constrainslist_TotalMC_em)):
          pdfconstrainslist_TotalMC_em.add(self.workspace4fit_.pdf(constrainslist_TotalMC_em[i]) )

        # Perform simoultaneous fit to MC
        pdfDSCBtoGAUS(self.workspace4fit_, "TotalMC")
        rfresult_TotalMC = simPdf_TotalMC.fitTo(combData_TotalMC,RooFit.Save(kTRUE),RooFit.Verbose(kFALSE), RooFit.Minimizer("Minuit"),RooFit.Strategy(0), RooFit.SumW2Error(kFALSE), RooFit.ExternalConstraints(pdfconstrainslist_TotalMC_em))
        pdfGAUStoDSCB(self.workspace4fit_, "TotalMC")
        rfresult_TotalMC = simPdf_TotalMC.fitTo(combData_TotalMC,RooFit.Save(kTRUE),RooFit.Verbose(kFALSE), RooFit.Minimizer("Minuit"),RooFit.Strategy(0), RooFit.SumW2Error(kFALSE), RooFit.ExternalConstraints(pdfconstrainslist_TotalMC_em))
        
#        if options.doBinnedFit:
#          rfresult_TotalMC = simPdf_TotalMC.fitTo(combData_TotalMC,RooFit.Save(kTRUE),RooFit.Verbose(kFALSE), RooFit.Minimizer("Minuit"), RooFit.SumW2Error(kTRUE), RooFit.ExternalConstraints(pdfconstrainslist_TotalMC_em))#, RooFit.SumW2Error(kTRUE))--> Removing due to unexected behaviour. See https://root.cern.ch/phpBB3/viewtopic.php?t=16917, https://root.cern.ch/phpBB3/viewtopic.php?t=16917
#          # rfresult_TotalMC = simPdf_TotalMC.fitTo(combData_TotalMC,RooFit.Save(kTRUE),RooFit.Verbose(kFALSE), RooFit.Minimizer("Minuit2"),RooFit.ExternalConstraints(pdfconstrainslist_TotalMC_em))#, RooFit.SumW2Error(kTRUE))
#        else:
#          rfresult_TotalMC = simPdf_TotalMC.fitTo(combData_TotalMC,RooFit.Save(kTRUE),RooFit.Verbose(kFALSE), RooFit.Minimizer("Minuit"), RooFit.SumW2Error(kTRUE), RooFit.ExternalConstraints(pdfconstrainslist_TotalMC_em))
#          # rfresult_TotalMC = simPdf_TotalMC.fitTo(combData_TotalMC,RooFit.Save(kTRUE),RooFit.Verbose(kFALSE), RooFit.Minimizer("Minuit2"),RooFit.ExternalConstraints(pdfconstrainslist_TotalMC_em))
        
        getattr(workspace4fit_,'import')(combData_TotalMC_plot)
        getattr(workspace4fit_,'import')(simPdf_TotalMC)  
        
        isData = False  
        chi2FailMC = drawFrameGetChi2(rrv_mass_j,rfresult_TotalMC,rdataset_TotalMC_em_mj_fail,model_TotalMC_fail_em,isData)
        chi2PassMC = drawFrameGetChi2(rrv_mass_j,rfresult_TotalMC,rdataset_TotalMC_em_mj,model_TotalMC_em,isData)
        
        #Print final MC fit results
        print "FIT Par. (MC) :"; print ""
        print "CHI2 PASS = %.3f    CHI2 FAIL = %.3f" %(chi2PassMC,chi2FailMC)
        print ""; print rfresult_TotalMC.Print(); print ""
        
        # draw the final fit results
        from WTopScalefactorProducer.Fitter.fitutils import DrawScaleFactorTTbarControlSample
        DrawScaleFactorTTbarControlSample(options.xtitle,self.workspace4fit_,self.boostedW_fitter_em.color_palet,"","em",self.boostedW_fitter_em.wtagger_label,self.boostedW_fitter_em.AK8_pt_min,self.boostedW_fitter_em.AK8_pt_max,options.sample,options.workspace)
       
        # Get W-tagging scalefactor and efficiencies
        GetWtagScalefactors(self.workspace4fit_,self.boostedW_fitter_em)
        
        # Delete workspace
        del self.workspace4fit_


    def CreateWorkspace(self, options): 
        workspace = RooWorkspace("workspace4fit_",options.workspace)

        print "No workspace found! Looping over infiles and creating datasets, output in " , filename
         
        rrv_mass_j = self.workspace4fit_.var("rrv_mass_j")

        self.get_mj_dataset(self.list_file_STop_mc,"_STop", options)
        self.get_mj_dataset(self.list_file_WJets_mc,"_WJets", options)
        self.get_mj_dataset(self.list_file_VV_mc,"_VV", options)
        # self.get_mj_dataset(self.list_file_QCD_mc,"_QCD")
        if options.fitMC: return
        self.get_mj_dataset(self.list_file_TTbar_mc,"_TTbar", options)
        self.get_mj_dataset(self.list_file_TTbar_mc,"_TTbar_realW", options)
        self.get_mj_dataset(self.list_file_TTbar_mc,"_TTbar_fakeW", options)
        self.get_mj_dataset(self.list_file_data,"_data", options)
        from WTopScalefactorProducer.Fitter.fitutils import doTTscalefactor
        ttSF = doTTscalefactor(self.workspace4fit_,self.channel)
        #for f in self.list_file_TTbar_mc:
        #  fname  = rt.TString(self.file_Directory+"/"+f)
        #  print "scaling with tt SF: " ,fname
        #  fileIn = TFile(fname.Data())
        #  treeIn = fileIn.Get("tree")
        #  treeIn.SetWeight(ttSF)
        #  treeIn.AutoSave()
        #  fileIn.Close()
        self.get_mj_dataset(self.list_file_pseudodata,"_TotalMC", options.massvar, options)
        print "Saving workspace in %s! To save time when debugging use option --WS %s to avoid recreating workspace every time"%(options.workspace+".root",options.workspace+".root")
        
        self.workspace4fit_.writeToFile(filename)

        return workspace

    def OpenWorkspace(self, options): 
        if options.doWS: #create workspace if requested 
            return self.CreateWorkspace(options)

        file = ROOT.TFile(options.workspace.replace(".root","")+".root") #TODO: close file
        workspace  = f.Get("workspace4fit_")
        #  print "No workspace found! Looping over infiles and creating datasets, output in " , filename TODO: Put as an exception 
        workspace.SetTitle(options.workspace)
        return workspace
