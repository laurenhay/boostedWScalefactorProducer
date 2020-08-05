#!/usr/bin/env python

import ROOT
import os
import sys
from WTopScalefactorProducer.Fitter.tdrstyle import *
from Dataset import Dataset
from Fitter import Fitter



WORKSPACENAME = "WTaggingFitter"

simplemodel = True



class WTaggingFitter(Fitter):  # class WTaggingFitter(Fitter)
	def __init__(self, options):
		# Loading custom Roofit PDFs 
		ROOT.gROOT.LoadMacro("PDFs/HWWLVJRooPdfs.cxx+")

		self.workspacename = WORKSPACENAME #Fixme 
		Fitter.__init__(self, options) # python 3 super().__init__(options)

		#TODO: add a mapping from Dataset name to RooDataset name (if needed, unless using RooRealVar.setRange())
		

		#dataset = self.LoadDataset("HP:tt")

		#print dataset

		self.fitvarname = options.massvar

		# Defining the samples
		self.background = ["tt", "VV", "SingleTop"] # TODO: define a class "sample" with a chain and cut on it 

		# Defining the fit options to be used 
		roofitoptions = ROOT.RooLinkedList()
		roofitoptions.Add(ROOT.RooFit.Save(1)) # Produce the fit result
		roofitoptions.Add(ROOT.RooFit.SumW2Error(ROOT.kTRUE)) # Interpret errors as errors on MC (see https://root.cern.ch/doc/master/classRooAbsPdf.html#af43c48c044f954b0e0e9d4fe38347551)
		roofitoptions.Add(ROOT.RooFit.Extended(ROOT.kTRUE)) # Add extended likelihood term 
		roofitoptions.Add(ROOT.RooFit.Minimizer("Minuit2")) # Use the Minuit2 minimizer (possible options: OldMinuit, Minuit (default), Minuit2, GSLMultiMin, GSLSimAn)
		#roofitoptions.Add(ROOT.RooFit.Verbose(ROOT.kFALSE)) # Disable verbosity 
		self.fitoptions = roofitoptions


		self.MakeFitModel()



	def FitMC(self, options, fitoptions = ""): 
		print "Fitting MC... "

		massvar = self.workspace.var(options.massvar)

		roofitoptions = ROOT.RooLinkedList()
		roofitoptions.Add(ROOT.RooFit.Save(1)) # Produce the fit result
		roofitoptions.Add(ROOT.RooFit.SumW2Error(ROOT.kTRUE)) # Interpret errors as errors on MC (see https://root.cern.ch/doc/master/classRooAbsPdf.html#af43c48c044f954b0e0e9d4fe38347551)
		roofitoptions.Add(ROOT.RooFit.Extended(ROOT.kTRUE)) # Add extended likelihood term 
		roofitoptions.Add(ROOT.RooFit.Minimizer("Minuit2")) # Use the Minuit2 minimizer (possible options: OldMinuit, Minuit (default), Minuit2, GSLMultiMin, GSLSimAn)
		#roofitoptions.Add(ROOT.RooFit.Verbose(ROOT.kFALSE)) # Disable verbosity 

		ttsample = self.workspace.data("HP:ttrealW")

		signalmodel = self.workspace.pdf("HP:tt:signalModel")

		self.FitSample({signalmodel:ttsample}, massvar, "SignalHP.pdf", roofitoptions)

		VVsample = self.workspace.data("HP:VV")
		VVmodel = self.workspace.pdf("HP:VV:model")

		self.FitSample({VVmodel:VVsample}, massvar, "VVbackgroundHP.pdf", roofitoptions)

		STsample = self.workspace.data("HP:st")
		STmodel = self.workspace.pdf("HP:st:model")
		self.FitSample({STmodel:STsample}, massvar, "STbackgroundHP.pdf", roofitoptions)


		#fitstuff = {
		#	signalmodel:ttsample, 
		#	VVmodel:VVsample, 
		#	STmodel:STsample,
		#}

		#plot, results = self.FitSample(fitstuff, massvar) # Working 

		

		#canvas = ROOT.TCanvas("canvas", "Fit to tt realW", 800, 600)
		#plot.Draw()

		#canvas.Print("fittest.pdf")

	def FitControlRegion(slef, options): 
		print "Fitting data and MC... "



	def FitSample(self, samplelist, variable, saveas="", fitoptions=None): 
		if (fitoptions==None): # TODO: fix! 
			if hasattr(self, "fitoptions"): 
				fitoptions = self.fitoptions
			else: 
				fitoptions = ROOT.RooLinkedList()

		print fitoptions

		plot = variable.frame()

		fitresult = []
		for model, dataset in samplelist.items():
			result = model.fitTo(dataset) 
			fitresult.append(result)
			model.plotOn(plot)
			dataset.plotOn(plot)

		if not saveas == "":
			canvas = ROOT.TCanvas("canvas", "Fit", 800, 600)
			plot.Draw()

			canvas.Print(saveas)

		return plot, fitresult


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
		signalShape = ROOT.RooDoubleCrystalBall("HP:tt:signalShape","HP:tt:signalShape", fitvariable, signalMeanHP, signalSigmaHP, signalAlpha1HP, signalSign1HP, signalAlpha2HP, signalSign2HP)
		signalNumber = ROOT.RooRealVar("HP:tt:signalNumber", "HP:tt:signalNumber", 0., 1e15)
		signalModel = ROOT.RooExtendPdf("HP:tt:signalModel", "HP:tt:signalModel", signalShape, signalNumber)
		if (simplemodel): signalModel = signalShape

		#getattr(self.workspace, "import")(signalModel)
		self.ImportToWorkspace(signalModel)
		#params = signalModel.getParameters(fitvariable)
		#self.workspace.defineSet("signalParams", params)
		#self.workspace.saveSnapshot("buildmodel", params, ROOT.kTRUE)

		# Background unmerged tt model
		backgroundOffset = ROOT.RooRealVar("HP:tt:fake:offset" ,"HP:tt:fake:offset", 90, 10, 200) # 90, 10, 200
		backgroundWidth  = ROOT.RooRealVar("HP:tt:fake:width" ,"HP:tt:fake:width", 40, 25, 300) # 40, 25, 100
		backgroundCoefficient  = ROOT.RooRealVar("HP:tt:fake:coefficient" ,"HP:tt:fake:coefficient", -0.03, -1., 0.) # -0.04, -1, 0.
		backgroundShape     = ROOT.RooErfExpPdf("HP:tt:fake:shape", "HP:tt:fake:shape" ,fitvariable, backgroundCoefficient, backgroundOffset, backgroundWidth)
		backgroundNumber = ROOT.RooRealVar("HP:tt:fake:number", "HP:tt:fake:number", 0., 1e15)
		backgroundModel = ROOT.RooExtendPdf("HP:tt:fake:model", "HP:tt:fake:model", backgroundShape, backgroundNumber)
		if (simplemodel): backgroundModel = backgroundShape
		self.ImportToWorkspace(backgroundModel)

		# Background VV model
		VValpha       = ROOT.RooRealVar("HP:VV:alpha","HP:VV:alpha",-0.01 ,-1., 0.)
		gaus_means  = 8.2653e+01 # Constraining the gaussian part to the mass of the W (well actually 80)
		gaussigmas   = 7.
		VVmean  = ROOT.RooRealVar("HP:VV:mean", "HP:VV:mean", gaus_means, gaus_means*.8, gaus_means*1.2) 
		VVsigma = ROOT.RooRealVar("HP:VV:sigma", "HP:VV:sigma", gaussigmas, gaussigmas*.5, gaussigmas*1.5)
		VVfactor        = ROOT.RooRealVar("HP:VV:factor", "GP:VV:factor", 0.7, 0., 1.)
		VVExp = ROOT.RooExponential("HP:VV:Exponential", "HP:VV:exponential", fitvariable, VValpha)
		VVGauss = ROOT.RooGaussian("HP:VV:Gaussian", "HP:VV:gaussian", fitvariable ,VVmean, VVsigma)
		VVshape = ROOT.RooAddPdf("HP:VV:shape","HP:VV:shape", ROOT.RooArgList(VVExp, VVGauss), ROOT.RooArgList(VVfactor))
		VVnumber = ROOT.RooRealVar("HP:VV:number", "HP:VV:number", 0., 1e15)
		VVmodel = ROOT.RooExtendPdf("HP:VV:model", "HP:VV:model", VVshape, VVnumber)
		if (simplemodel): VVmodel = VVshape
		self.ImportToWorkspace(VVmodel)

		# Background single top model
		STcoeff = ROOT.RooRealVar("HP:st:coefficient", "HP:st:coefficient", -0.04, -1., 1.)
		STwidth = ROOT.RooRealVar("HP:st:width","HP:st:width", 30., 0., 400.)
		SToffset = ROOT.RooRealVar("HP:st:offset", "HP:st:offset", 60., 50., 100.)
		STmean = ROOT.RooRealVar("HP:st:mean", "HP:st:mean", gaus_means, gaus_means*.8, gaus_means*1.2)
		STsigma = ROOT.RooRealVar("HP:st:sigma", "HP:st:sigma", gaussigmas, gaussigmas*.5, gaussigmas*1.5)
		STErfExp = ROOT.RooErfExpPdf("HP:st:ErfExp", "HP:st:ErfExp", fitvariable, STcoeff, SToffset, STwidth)
		STGauss = ROOT.RooGaussian ("HP:st:Gaussian" ,"HP:st:Gaussian" , fitvariable, STmean, STsigma)
		STfactor = ROOT.RooRealVar("HP:st:factor", "HP:st:factor", 0.3, 0.0, 0.99)
		STshape = ROOT.RooAddPdf("HP:st:shape", "HP:st:shape", STErfExp, STGauss, STfactor)
		STnumber = ROOT.RooRealVar("HP:st:number", "HP:st:number", 0., 1e15)
		STmodel = ROOT.RooExtendPdf("HP:st:model", "HP:st:model", STshape, STnumber)
		if (simplemodel): STmodel = STshape
		self.ImportToWorkspace(STmodel)

		# Backgound W+Jets model
		WJetscoeff  = ROOT.RooRealVar("HP:WJets:coefficient", "HP:WJets:coefficient", -0.026, -0.05, 0.05)
		WJetsoffset = ROOT.RooRealVar("HP:WJets:offset", "HP:WJets:offset" ,41. ,0., 100)
		WJetswidth  = ROOT.RooRealVar("HP:WJets:width", "HP:WJets:width", 30., 1., 100.)
		WJetsshape  = ROOT.RooErfExpPdf("HP:WJets:shape", "HP:WJets:shape", fitvariable, WJetscoeff, WJetsoffset, WJetswidth)
		WJetsnumber = ROOT.RooRealVar("HP:WJets:number", "HP:WJets:number", 0., 1e15)
		WJetsmodel = ROOT.RooExtendPdf("HP:WJets:model", "HP:WJets:model", WJetsshape, WJetsnumber)
		if (simplemodel): WJetsmodel = WJetsshape
		self.ImportToWorkspace(WJetsmodel, True)

		self.workspace.saveSnapshot("buildmodel", ROOT.RooArgSet(STcoeff, STwidth, SToffset, STmean, STsigma, STfactor), ROOT.kTRUE) # works! 
		self.workspace.saveSnapshot("buildmodel", VVmodel.getParameters(ROOT.RooArgSet(fitvariable)), ROOT.kTRUE) # works too

		

		#self.SaveWorkspace()


		#getattr(self.workspace, "import")(signalModel)
		#self.ImportToWorkspace(signalModel, True)
		#self.workspace.Write()
		#self.SaveWorkspace()


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
		for sample in ["VV", "st", "WJets"]: # "tt", 
			getattr(workspace, "import")(self.CreateDataset(dataset.getSample(sample), "HP:"+sample, argset, cutPass, weightvarname))
			workspace.writeToFile(filename)
			getattr(workspace, "import")(self.CreateDataset(dataset.getSample(sample), "LP:"+sample, argset, cutFail, weightvarname))
			workspace.writeToFile(filename)

		# For tt we need an additional cut to separate it into gen matched merged W and unmerged
		additionalCutMerged = "&&(genmatchedAK82017==1)"
		additionalCutUnmerged = "&&(genmatchedAK82017==0)"
		merged = ROOT.RooRealVar("genmatchedAK82017", "genmatchedAK82017", 0., 1.)
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
		# TODO: use RooDataSet.merge or RooDataDet.append to generate the bkg dataset 
		
		workspace.writeToFile(filename)

		return workspace


