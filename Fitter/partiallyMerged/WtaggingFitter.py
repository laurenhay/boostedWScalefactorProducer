import ROOT
import os
from WTopScalefactorProducer.Fitter.tdrstyle import *
from InitialiseFits import initialiseFits
from Dataset import Dataset

WORKSPACENAME = "WTaggingFitter"


class WTaggingFitter:
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


    def get_mj_dataset(self,in_file_name, label, jet_mass,lumi): 
            
            print "Using mass variable " ,jet_mass
          
            treeIn = TChain(options.intree)
            for f in in_file_name:
              print "Using file: ", TString(self.file_Directory+f)
              fileIn_name = TString(self.file_Directory+f)  
              treeIn.Add(fileIn_name.Data())
            
             #Get in tree
            # treeIn      = fileIn.Get(options.intree)
            
            rrv_mass_j = self.workspace4fit_.var("rrv_mass_j")
            rrv_weight = RooRealVar("rrv_weight","rrv_weight",0. ,10000000.)    

            # Mj dataset before tau2tau1 cut : Passed
            rdataset_mj     = RooDataSet("rdataset"     +label+"_"+self.channel+"_mj","rdataset"    +label+"_"+self.channel+"_mj",RooArgSet(rrv_mass_j,rrv_weight),RooFit.WeightVar(rrv_weight) )
            rdataset4fit_mj = RooDataSet("rdataset4fit" +label+"_"+self.channel+"_mj","rdataset4fit"+label+"_"+self.channel+"_mj",RooArgSet(rrv_mass_j,rrv_weight),RooFit.WeightVar(rrv_weight) )
            # rrv_number_pass = RooRealVar("rrv_number_ttbar"+label+"_passtau2tau1cut_em_mj","rrv_number_ttbar"+label+"_passtau2tau1cut_em_mj",0.,10000000.) #LUCA
        
            # Mj dataset before tau2tau1 cut : Total
            rdataset_beforetau2tau1cut_mj     = RooDataSet("rdataset"     +label+"_beforetau2tau1cut_"+self.channel+"_mj","rdataset"    +label+"_beforetau2tau1cut_"+self.channel+"_mj",RooArgSet(rrv_mass_j,rrv_weight),RooFit.WeightVar(rrv_weight) )
            rdataset4fit_beforetau2tau1cut_mj = RooDataSet("rdataset4fit" +label+"_beforetau2tau1cut_"+self.channel+"_mj","rdataset4fit"+label+"_beforetau2tau1cut_"+self.channel+"_mj",RooArgSet(rrv_mass_j,rrv_weight),RooFit.WeightVar(rrv_weight) )
            # rrv_number_before = RooRealVar("rrv_number_ttbar"+label+"_beforetau2tau1cut_em_mj","rrv_number_ttbar"+label+"_beforetau2tau1cut_em_mj",0.,10000000.) #LUCA
       
            ### Mj dataset failed tau2tau1 cut :
            rdataset_failtau2tau1cut_mj     = RooDataSet("rdataset"     +label+"_failtau2tau1cut_"+self.channel+"_mj","rdataset"    +label+"_failtau2tau1cut_"+self.channel+"_mj",RooArgSet(rrv_mass_j,rrv_weight),RooFit.WeightVar(rrv_weight) )
            rdataset4fit_failtau2tau1cut_mj = RooDataSet("rdataset4fit" +label+"_failtau2tau1cut_"+self.channel+"_mj","rdataset4fit"+label+"_failtau2tau1cut_"+self.channel+"_mj",RooArgSet(rrv_mass_j,rrv_weight),RooFit.WeightVar(rrv_weight) )
            # rrv_number_fail = RooRealVar("rrv_number_ttbar"+label+"_failingtau2tau1cut_em_mj","rrv_number_ttbar"+label+"_failingtau2tau1cut_em_mj",0.,10000000.) #LUCA    

            ### Mj dataset extreme failed tau2tau1 cut: > 0.75
            rdataset_extremefailtau2tau1cut_mj     = RooDataSet("rdataset"    +label+"_extremefailtau2tau1cut_"+self.channel+"_mj","rdataset"     +label+"_extremefailtau2tau1cut_"+self.channel+"_mj",RooArgSet(rrv_mass_j,rrv_weight),RooFit.WeightVar(rrv_weight) )
            rdataset4fit_extremefailtau2tau1cut_mj = RooDataSet("rdataset4fit"+label+"_extremefailtau2tau1cut_"+self.channel+"_mj","rdataset4fit" +label+"_extremefailtau2tau1cut_"+self.channel+"_mj",RooArgSet(rrv_mass_j,rrv_weight),RooFit.WeightVar(rrv_weight) )
            rrv_number_extremefail = RooRealVar("rrv_number_ttbar"+label+"_extremefailtau2tau1cut_em_mj","rrv_number_ttbar"+label+"_extremefailtau2tau1cut_em_mj",0.,10000000.) #LUCA
            
            
            # Define categories
            if self.workspace4fit_.cat("category_p_f"+"_"+self.channel):
              category_p_f = self.workspace4fit_.cat("category_p_f"+"_"+self.channel)
            else:
              category_p_f = RooCategory("category_p_f"+"_"+self.channel,"category_p_f"+"_"+self.channel)
              category_p_f.defineType("pass")
              category_p_f.defineType("fail")
              getattr(self.workspace4fit_,"import")(category_p_f)
            
            combData_p_f = RooDataSet("combData_p_f"+label+"_"+self.channel,"combData_p_f"+label+"_"+self.channel,RooArgSet(rrv_mass_j, category_p_f, rrv_weight),RooFit.WeightVar(rrv_weight))
            
            print "N entries: ", treeIn.GetEntries()
            
            hnum_4region                    = TH1D("hnum_4region"       +label+"_"+self.channel,"hnum_4region"        +label+"_"+self.channel,4, -1.5, 2.5) # m_j -1: sb_lo; 0:signal_region; 1: sb_hi; 2:total
            hnum_4region_error2             = TH1D("hnum_4region_error2"+label+"_"+self.channel,"hnum_4region_error2" +label+"_"+self.channel,4, -1.5, 2.5) # m_j -1: sb_lo; 0:signal_region; 1: sb_hi; 2:total     

            hnum_4region_before_cut         = TH1D("hnum_4region_before_cut"        +label+"_"+self.channel,"hnum_4region_before_cut"       +label+"_"+self.channel,4,-1.5,2.5);# m_j -1: sb_lo; 0:signal_region; 1: sb_hi; 2:total
            hnum_4region_before_cut_error2  = TH1D("hnum_4region_before_cut_error2" +label+"_"+self.channel,"hnum_4region_before_cut_error2"+label+"_"+self.channel,4,-1.5,2.5);# m_j -1: sb_lo; 0:signal_region; 1: sb_hi; 2:total     

            hnum_2region                    = TH1D("hnum_2region"       +label+"_"+self.channel,"hnum_2region"        +label+"_"+self.channel,2,-0.5,1.5);# m_lvj 0: signal_region; 1: total --> There is only 1 and that is SIGNAL REGION?!
            hnum_2region_error2             = TH1D("hnum_2region_error2"+label+"_"+self.channel,"hnum_2region_error2" +label+"_"+self.channel,2,-0.5,1.5);# m_lvj 0: signal_region; 1: total
            
        
            #-------------------------------------------------------------------------------------------
            
            # Loop over tree entries
            print "rrv_mass_j.getMax() = " ,rrv_mass_j.getMax()
            print "rrv_mass_j.getMin() = " ,rrv_mass_j.getMin()
            tmp_scale_to_lumi = 1
            i = 0
            
            SF = 1.0
      #      if label.find("QCD")!=-1: 
      #          SF = 0.697187387981
            
            for i in range(treeIn.GetEntries()):
                if i % 5000 == 0: print "iEntry: ",i
                event = treeIn.GetEntry(i)
                if not (treeIn.SelectedJet_pt > self.AK8_pt_min): continue
                if not (treeIn.SelectedJet_pt < self.AK8_pt_max): continue
                if not (treeIn.passedMETfilters):continue
                if not (treeIn.maxAK4CSV>0.8484):continue   

                if getattr(treeIn, jet_mass) > rrv_mass_j.getMax() and getattr(treeIn, jet_mass)< rrv_mass_j.getMin() : continue
                
      #          try:
      #            if TString(label).Contains("realW") and not getattr(treeIn,"genmatchedAK8"): #mergedVTruth Is a real W, meaning both daughters of W is withing jet cone!!
      #              continue
      #            if TString(label).Contains("realW") and getattr(treeIn,"genmatchedAK8"): #mergedTopTruth Is a real top, meaning both daughters of W and b is withing jet cone!!
      #              continue
      #              
      #            if TString(label).Contains("fakeW") and getattr(treeIn,"genmatchedAK8") and not getattr(treeIn,"genmatchedAK8"): #mergedVTruth mergedTopTruth
      #                continue
      #          except:
      #            print "WARNING: no genmatchedAK8 in tree", treeIn.GetName()
                
                if TString(label).Contains("realW") and not treeIn.genmatchedAK82017: continue
                if TString(label).Contains("fakeW") and treeIn.genmatchedAK82017: continue
                
                if options.tagger.find("ddt")==-1 and options.tagger.find("DDT")==-1: 
                    wtagger = getattr(treeIn,options.tagger)
                else: 
                    wtagger = treeIn.SelectedJet_tau21_ddt_retune #treeIn.jetAK8_tau21+(0.079*rt.TMath.Log((treeIn.jetAK8_softDrop_mass*treeIn.jetAK8_softDrop_mass)/treeIn.jetAK8_pt))
                  
                discriminantCut = 0
                if wtagger <= options.tau2tau1cutHP: # HP
                    discriminantCut = 2
                elif wtagger > options.tau2tau1cutHP and wtagger <= options.tau2tau1cutLP: #LP
                    discriminantCut = 1
                elif wtagger > options.tau2tau1cutLP: # Extreme fail
                    discriminantCut = 0     

                tmp_jet_mass = getattr(treeIn, jet_mass);
                treeWeight = treeIn.GetWeight()
                
                # if i==0:
                  
                
                if not TString(label).Contains("data"):     

                    tmp_scale_to_lumi = treeIn.eventweightlumi ## weigth for xs and lumi FIXME
                    if options.topPt: tmp_scale_to_lumi *= treeIn.topweight
      #              # tmp_event_weight  = treeWeight*treeIn.normGenWeight*treeIn.puWeight*treeIn.eventWeightLumi*treeIn.topWeight*lumi*SF#*treeIn.muTrigWeight*treeIn.muIsoWeight
      #              if options.topPt:
      #                tmp_event_weight  = treeWeight*treeIn.normGenWeight*treeIn.puWeight*treeIn.topWeight*treeIn.eventWeightLumi*lumi*SF
      #              else:             
      #                tmp_event_weight  = treeWeight*treeIn.normGenWeight*treeIn.puWeight*treeIn.eventWeightLumi*lumi*SF # no topPt
      #              
      #              # tmp_event_weight4fit = treeWeight*treeIn.normGenWeight*treeIn.puWeight*treeIn.topWeight*SF#*treeIn.muTrigWeight*treeIn.muIsoWeight
      #              if options.topPt: 
      #                tmp_event_weight4fit = treeWeight*treeIn.normGenWeight*treeIn.puWeight*treeIn.topWeight*SF
      #              else:
      #                tmp_event_weight4fit = treeWeight*treeIn.normGenWeight*treeIn.puWeight*SF # no topPt
                    
      #              tmp_event_weight4fit = tmp_event_weight4fit*treeIn.eventWeightLumi/tmp_scale_to_lumi    
                    tmp_event_weight = tmp_scale_to_lumi
                    tmp_event_weight4fit = tmp_scale_to_lumi
                    
                else:
                  tmp_scale_to_lumi = 1.
                  tmp_event_weight = 1.
                  tmp_event_weight4fit = 1.     

                
                # if options.fitTT:
                #   tmp_event_weight4fit = 1.
                            

                #  HP category
                if discriminantCut == 2  and tmp_jet_mass > rrv_mass_j.getMin() and tmp_jet_mass < rrv_mass_j.getMax():   
                   rrv_mass_j.setVal(tmp_jet_mass)
                   
                   rdataset_mj    .add(RooArgSet(rrv_mass_j), tmp_event_weight)
                   rdataset4fit_mj.add(RooArgSet(rrv_mass_j), tmp_event_weight4fit)     

                   if tmp_jet_mass >= self.mj_sideband_lo_min and tmp_jet_mass < self.mj_sideband_lo_max:
                       hnum_4region.Fill(-1,tmp_event_weight )
                       
                   if tmp_jet_mass >= self.mj_signal_min and tmp_jet_mass < self.mj_signal_max:
                       # hnum_2region.Fill(1,tmp_event_weight)
                       hnum_4region.Fill(0,tmp_event_weight)
                       hnum_4region_error2.Fill(0,tmp_event_weight*tmp_event_weight)
                   if tmp_jet_mass >= self.mj_sideband_hi_min and tmp_jet_mass < self.mj_sideband_hi_max:
                       hnum_4region.Fill(1,tmp_event_weight)    

                   hnum_4region.Fill(2,tmp_event_weight) 
                   
                   category_p_f.setLabel("pass")
                   combData_p_f.add(RooArgSet(rrv_mass_j,category_p_f),tmp_event_weight)
                
                # TOTAL category (no Tau21 )
                if (discriminantCut == 2 or discriminantCut == 1 or discriminantCut == 0) and (rrv_mass_j.getMin() < tmp_jet_mass < rrv_mass_j.getMax()): 
                    rrv_mass_j.setVal(tmp_jet_mass)     

                    if tmp_jet_mass >= self.mj_signal_min and tmp_jet_mass <self.mj_signal_max :
                       hnum_4region_before_cut.Fill(0,tmp_event_weight)
                       hnum_4region_before_cut_error2.Fill(0,tmp_event_weight*tmp_event_weight)     

                    rdataset_beforetau2tau1cut_mj.add(RooArgSet(rrv_mass_j),tmp_event_weight)
                    rdataset4fit_beforetau2tau1cut_mj.add(RooArgSet(rrv_mass_j),tmp_event_weight4fit)
                
                # 1 minus HP category (LP)   
                if (discriminantCut==1) and (rrv_mass_j.getMin() < tmp_jet_mass < rrv_mass_j.getMax()):
        
                    rrv_mass_j.setVal(tmp_jet_mass)     

                    rdataset_failtau2tau1cut_mj     .add(RooArgSet(rrv_mass_j), tmp_event_weight)
                    rdataset4fit_failtau2tau1cut_mj .add(RooArgSet(rrv_mass_j), tmp_event_weight4fit )
          
                    category_p_f.setLabel("fail");
                    combData_p_f.add(RooArgSet(rrv_mass_j,category_p_f),tmp_event_weight)
                 #-------------------------------------------------------------------------------------------
                 # Extreme fail category (Tau21 > LP_max)   
                if discriminantCut==0 and (rrv_mass_j.getMin() < tmp_jet_mass < rrv_mass_j.getMax()):   

                  rdataset_extremefailtau2tau1cut_mj     .add(RooArgSet(rrv_mass_j), tmp_event_weight)
                  rdataset4fit_extremefailtau2tau1cut_mj .add(RooArgSet(rrv_mass_j), tmp_event_weight4fit )
            
            rrv_scale_to_lumi                        = RooRealVar("rrv_scale_to_lumi"+label+"_"                       +self.channel,"rrv_scale_to_lumi"+label+"_"                       +self.channel,tmp_scale_to_lumi*SF)
            rrv_scale_to_lumi_failtau2tau1cut        = RooRealVar("rrv_scale_to_lumi"+label+"_failtau2tau1cut_"       +self.channel,"rrv_scale_to_lumi"+label+"_failtau2tau1cut_"       +self.channel,tmp_scale_to_lumi*SF)
            rrv_scale_to_lumi_extremefailtau2tau1cut = RooRealVar("rrv_scale_to_lumi"+label+"_extremefailtau2tau1cut_"+self.channel,"rrv_scale_to_lumi"+label+"_extremefailtau2tau1cut_"+self.channel,tmp_scale_to_lumi*SF)
            
            getattr(self.workspace4fit_,"import")(rrv_scale_to_lumi)
            getattr(self.workspace4fit_,"import")(rrv_scale_to_lumi_failtau2tau1cut)
            getattr(self.workspace4fit_,"import")(rrv_scale_to_lumi_extremefailtau2tau1cut)
              
            # rrv_number_pass.setVal(rdataset_mj.sumEntries())
       #      rrv_number_pass.setError(TMath.Sqrt(rdataset_mj.sumEntries()))
       #      # rrv_number_pass.Print()
       #      rrv_number_before.setVal(rdataset_beforetau2tau1cut_mj.sumEntries())
       #      rrv_number_before.setError(TMath.Sqrt(rdataset_beforetau2tau1cut_mj.sumEntries()))
       #      # rrv_number_before.Print()
       #      rrv_number_fail.setVal(rdataset_failtau2tau1cut_mj.sumEntries())
       #      rrv_number_fail.setError(TMath.Sqrt(rdataset_failtau2tau1cut_mj.sumEntries()))
       #      # rrv_number_fail.Print()
            rrv_number_extremefail.setVal(rdataset_extremefailtau2tau1cut_mj.sumEntries())
            rrv_number_extremefail.setError(TMath.Sqrt(rdataset_extremefailtau2tau1cut_mj.sumEntries()))
            getattr(self.workspace4fit_,"import")(rrv_number_extremefail)   

      #      rrv_number_extremefail.Print()
       #
            # getattr(self.workspace4fit_,"import")(rrv_number_pass)
          #   getattr(self.workspace4fit_,"import")(rrv_number_before)
          #   getattr(self.workspace4fit_,"import")(rrv_number_fail)
                

            #prepare m_j dataset
            rrv_number_dataset_sb_lo_mj                 = RooRealVar("rrv_number_dataset_sb_lo"               +label+"_"+self.channel+"_mj","rrv_number_dataset_sb_lo"                +label+"_"+self.channel+"_mj",hnum_4region.GetBinContent(1))
            rrv_number_dataset_signal_region_mj         = RooRealVar("rrv_number_dataset_signal_region"       +label+"_"+self.channel+"_mj","rrv_number_dataset_signal_region"        +label+"_"+self.channel+"_mj",hnum_4region.GetBinContent(2))
            rrv_number_dataset_signal_region_error2_mj  = RooRealVar("rrv_number_dataset_signal_region_error2"+label+"_"+self.channel+"_mj","rrv_number_dataset_signal_region_error2" +label+"_"+self.channel+"_mj",hnum_4region_error2.GetBinContent(2))   

            rrv_number_dataset_signal_region_before_cut_mj        = RooRealVar("rrv_number_dataset_signal_region_before_cut"        +label+"_"+self.channel+"_mj","rrv_number_dataset_signal_region_before_cut"       +label+"_"+self.channel+"_mj",hnum_4region_before_cut.GetBinContent(2))
            rrv_number_dataset_signal_region_before_cut_error2_mj = RooRealVar("rrv_number_dataset_signal_region_before_cut_error2" +label+"_"+self.channel+"_mj","rrv_number_dataset_signal_region_before_cut_error2"+label+"_"+self.channel+"_mj",hnum_4region_before_cut_error2.GetBinContent(2))
            rrv_number_dataset_sb_hi_mj                           = RooRealVar("rrv_number_dataset_sb_hi"                           +label+"_"+self.channel+"_mj","rrv_number_dataset_sb_hi"                          +label+"_"+self.channel+"_mj",hnum_4region.GetBinContent(3))      

            getattr(self.workspace4fit_,"import")(rrv_number_dataset_sb_lo_mj)
            getattr(self.workspace4fit_,"import")(rrv_number_dataset_signal_region_mj)
            getattr(self.workspace4fit_,"import")(rrv_number_dataset_signal_region_error2_mj)
            getattr(self.workspace4fit_,"import")(rrv_number_dataset_signal_region_before_cut_mj)
            getattr(self.workspace4fit_,"import")(rrv_number_dataset_signal_region_before_cut_error2_mj)
            getattr(self.workspace4fit_,"import")(rrv_number_dataset_sb_hi_mj)
            getattr(self.workspace4fit_,"import")(combData_p_f)     

            print "N_rdataset_mj: "
            getattr(self.workspace4fit_,"import")(rdataset_mj)
            getattr(self.workspace4fit_,"import")(rdataset4fit_mj)
            getattr(self.workspace4fit_,"import")(rdataset_beforetau2tau1cut_mj)
            getattr(self.workspace4fit_,"import")(rdataset4fit_beforetau2tau1cut_mj)
            getattr(self.workspace4fit_,"import")(rdataset_failtau2tau1cut_mj)
            getattr(self.workspace4fit_,"import")(rdataset4fit_failtau2tau1cut_mj)
            getattr(self.workspace4fit_,"import")(rdataset_extremefailtau2tau1cut_mj)
            getattr(self.workspace4fit_,"import")(rdataset4fit_extremefailtau2tau1cut_mj)

    def CreateDataset(self, files, name, variables, cut, weightvariable): 
        print "Creating dataset {}".format(name)   

        chain = ROOT.TChain("Events")
        for file in files:
            assert(os.path.isfile(file)), "ERROR: The file: {} does not exist! You may want to update the directory/file name in Dataset.py.".format(file)
            chain.Add(file)

        print chain.GetEntries()

        print "Importing dataset '{}' from: {}".format(name, ", ".join(files))
        dataset = ROOT.RooDataSet(name, name, chain, variables, cut, weightvariable)

        return dataset



    def CreateWorkspace(self, options, filename): 
        if (self.CheckWorkspaceExistence(filename)): 
            print "Workspace already exists! "
        workspace = ROOT.RooWorkspace(WORKSPACENAME, options.workspace)

        mass = ROOT.RooRealVar(options.massvar, options.massvar, options.minX, options.maxX) #workspace.var("mass") # TODO: Do we really want to set a range here (additional cut w.r.t. tree variable)?
        weight = ROOT.RooRealVar("weight", "weight", 0., 10000000.)    # variables = ROOT.RooArgSet(x, y)
        # For importing a TTree into RooDataSet the RooRealVar names must match the branch names, see: https://root.cern.ch/root/html608/rf102__dataimport_8C_source.html

        cutPass = "{} < {}".format(options.tagger, options.cutHP)
        cutFail = "({} > {}) && ({} < {})".format(options.tagger, options.cutHP, options.tagger, options.cutLP)

        argset = ROOT.RooArgSet(mass, weight)  # TODO: Does the weight need to be included here? 

        dataset = Dataset(options.year) 
        sample = dataset.getSample("tt")

        print "HP cut:", cutPass


        roodataset = self.CreateDataset(sample, "tt", argset, "", "weight")
        getattr(workspace, "import")(roodataset) 

        print sample

        
        workspace.writeToFile(filename)

        return workspace

    def OpenWorkspace(self, options): 
        filename = options.workspace.replace(".root","")+".root"
        if (options.doWS): #create workspace if requested 
            self.workspace = self.CreateWorkspace(options, filename)
            return self.workspace

        status, message = self.CheckWorkspaceFile(filename)
        if (status == 3): 
            # The file exists and contains a valid workspace
            self.file = ROOT.TFile(filename) #TODO: close file
            self.workspace  = f.Get(WORKSPACENAME)
        
            self.workspace.SetTitle(options.workspace)
            return self.workspace
        else: 
            # Something is wrond with the workspace file
            print message


    def CheckWorkspaceExistence(self, filename): 
        status, errormessage = self.CheckWorkspaceFile(filename)
        if (status == 3): 
            return True
        else: 
            return False

    def CheckWorkspaceFile(self, filename):
        message = ""
        status = -1
        if (os.path.isfile(filename)): 
            file = ROOT.TFile.Open(filename, "READ")
            if (file.IsOpen()): 
                if (file.GetListOfKeys().Contains(WORKSPACENAME)): 
                    message = "File contains a workspace named: {}".format(WORKSPACENAME)
                    status = 3
                else: 
                    message = "File: {} does not containt a workspace named: {}".format(filename, WORKSPACENAME)
                    status = 2
            else: 
                message = "File '{}' could not be opened".format(filename)
                status = 1
        else: 
            message = "File '{}' does not exist.".format(filename)
            status = 0

        return status, message


