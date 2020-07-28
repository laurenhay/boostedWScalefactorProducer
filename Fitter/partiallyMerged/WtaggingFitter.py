#!/usr/bin/env python

import ROOT
import os
import sys
from WTopScalefactorProducer.Fitter.tdrstyle import *
from Dataset import Dataset
from Fitter import Fitter



WORKSPACENAME = "WTaggingFitter"



class WTaggingFitter(Fitter):  # class WTaggingFitter(Fitter)
	def __init__(self, options):
		ROOT.gROOT.LoadMacro("PDFs/HWWLVJRooPdfs.cxx+")

		self.workspacename = WORKSPACENAME #Fixme 
		Fitter.__init__(self, options) # python 3 super().__init__(options)

		#TODO: add a mapping from Dataset name to RooDataset name (if needed, unless using RooRealVar.setRange())
		

		dataset = self.LoadDataset("HP:tt")

		print dataset

		self.fitvarname = options.massvar


		self.MakeFitModel()


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

	def MakeFitModel(self): 
		print "Making fit model"

		fitvariable = self.workspace.var(self.fitvarname)
		#self.workspace.factory("DoubleCrystalBall::HP:tt:SignalModel({}, signalMean1[80., 100.], signalMean1[-10., 10.], signalSigma[0., 50.], signalSigma[0., 50.], sign1[0.01, 5.], sign1[0.01, 10.]".format(self.fitvarname)) # TODO: check how we can use the factory syntax with custom Pdfs. 

		# Signal model in the HP category 
		signalMeanHP   = ROOT.RooRealVar("HP:tt:mean", "HP:tt:mean", 89., 80., 100.) 
		signalSigmaHP  = ROOT.RooRealVar("HP:tt:sigma", "HP:tt:sigma", 8., 5., 20.)
		signalAlpha1HP  = ROOT.RooRealVar("HP:tt:alpha1", "HP:tt:alpha1", 0.5, 0.1, 10.) 
		signalAlpha2HP  = ROOT.RooRealVar("HP:tt:alpha2", "HP:tt:alpha2", 1.0, 0.1, 10.) 
		signalSign1HP   = ROOT.RooRealVar("HP:tt:sign1", "HP:tt:sign1", 0.2, 0.01, 5.)
		signalSign2HP   = ROOT.RooRealVar("HP:tt:sign2", "HP:tt:sign2", 0.2, 0.01, 10.) 
		signalModel = ROOT.RooDoubleCrystalBall("HP:tt:signalModel","signalModel", fitvariable, signalMeanHP, signalSigmaHP, signalAlpha1HP, signalSign1HP, signalAlpha2HP, signalSign2HP)

		#getattr(self.workspace, "import")(signalModel)
		self.ImportToWorkspace(signalModel)
		#self.workspace.Write()
		self.SaveWorkspace()


	def CreateWorkspace(self, options, filename): 
		if (self.CheckWorkspaceExistence(filename)): 
			print "Workspace already exists! "
			print "A workspace with name '{}' already exists, are you sure you want to overwrite it? ".format(filename) 
			rep = self.PromptYesNo()
			if rep == 'no': 
				print "Aborting!"
				sys.exit()

		workspace = ROOT.RooWorkspace(self.workspacename, self.workspacename)

		mass = ROOT.RooRealVar(options.massvar, options.massvar, options.minX, options.maxX) #workspace.var("mass") # TODO: Do we really want to set a range here (additional cut w.r.t. tree variable)?
		tagger = ROOT.RooRealVar(options.tagger, options.tagger, 0., options.cutLP)
		tagger.setRange("HP", 0., options.cutHP)
		tagger.setRange("LP", options.cutHP, options.cutLP)
		weight = ROOT.RooRealVar("weight", "weight", 0., 10000000.)    # variables = ROOT.RooArgSet(x, y)
		# For importing a TTree into RooDataSet the RooRealVar names must match the branch names, see: https://root.cern.ch/root/html608/rf102__dataimport_8C_source.html

		cutPass = "({} <= {})".format(options.tagger, options.cutHP)
		cutFail = "({0} > {1}) && ({0} <= {2})".format(options.tagger, options.cutHP, options.cutLP)

		argset = ROOT.RooArgSet(mass, weight, tagger)  # TODO: Does the weight need to be included here? 

		weightvarname = "weight"

		dataset = Dataset(options.year) 

		# TODO: investigate usage of RooRealVar.setRange() to set HP and LP ranges 
		for sample in ["tt", "VV", "SingleTop"]: 
			getattr(workspace, "import")(self.CreateDataset(dataset.getSample(sample), "HP:"+sample, argset, cutPass, weightvarname))
			workspace.writeToFile(filename)
			getattr(workspace, "import")(self.CreateDataset(dataset.getSample(sample), "LP:"+sample, argset, cutFail, weightvarname))
			workspace.writeToFile(filename)

		# For tt we need an additional cut to separate it into gen matched merged W and unmerged
		additionalCutMerged = "&&(isW2017==1)"
		additionalCutUnmerged = "&&(isW2017==0)"
		merged = ROOT.RooRealVar("isW2017", "isW2017", 0., 1.)
		argset.add(merged)
		getattr(workspace, "import")(self.CreateDataset(dataset.getSample("tt"), "HP:ttrealW", argset, cutPass+additionalCutMerged, weightvarname))
		workspace.writeToFile(filename)
		getattr(workspace, "import")(self.CreateDataset(dataset.getSample("tt"), "HP:ttfakeW", argset, cutPass+additionalCutUnmerged, weightvarname))
		workspace.writeToFile(filename)
		getattr(workspace, "import")(self.CreateDataset(dataset.getSample("tt"), "LP:ttrealW", argset, cutFail+additionalCutMerged, weightvarname))
		workspace.writeToFile(filename)
		getattr(workspace, "import")(self.CreateDataset(dataset.getSample("tt"), "LP:ttfakeW", argset, cutFail+additionalCutUnmerged, weightvarname))


		#sample = dataset.getSample("tt")
		#roodataset = self.CreateDataset(sample, "tt", argset, cutPass, "weight")
		#getattr(workspace, "import")(roodataset) 

		# TODO: add cut values to workspace
		# TODO: uuse RooDataSet.merge or RooDataDet.append to generate the bkg dataset 
		
		workspace.writeToFile(filename)

		return workspace


