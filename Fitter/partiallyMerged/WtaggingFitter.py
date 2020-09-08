#!/usr/bin/env python

import ROOT
import os
import sys
from WTopScalefactorProducer.Fitter.tdrstyle import *
from Dataset import Dataset
from Fitter import Fitter



WORKSPACENAME = "WTaggingFitter"

simplemodel = False



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
		self.background = ["tt", "VV", "SingleTop", ] # TODO: define a class "sample" with a chain and cut on it 

		# TODO: fix directroy handling
		self.directory = {} 
		self.directory["fitMC"] = "plots/{}/fitMC/".format(options.year)
		self.directory["fitMClogs"] = "logs/{}/fitMC/".format(options.year)

		# Creatring the output directories if they don't exist 
		for directory in self.directory.values(): 
			if not os.path.isdir(directory): 
				assert(not os.path.isfile(directory)), "ERROR: The path '{}' is a file, cannot create directory with such name!" 
				os.system("mkdir -p "+directory)

		# Defining the fit options to be used 
		#ROOT.Math:MinimizerOptions.SetDefaultTolerance()
		#self.fitoptions = roofitoptions

		self.constraintlist = []

		self.savemodel = False


		#self.MakeFitModel(True)



	def FitMC(self, options, fitoptions = ""): 
		# TODO: might remove options and set massvar as attribute 
		print "Fitting MC... "

		#self.MakeFitModel(True)

		

		massvar = self.LoadVariable(options.massvar)

		#roofitoptions = ROOT.RooLinkedList()
		#roofitoptions.Add(ROOT.RooFit.Save(1)) # Produce the fit result
		#roofitoptions.Add(ROOT.RooFit.SumW2Error(ROOT.kTRUE)) # Interpret errors as errors on MC (see https://root.cern.ch/doc/master/classRooAbsPdf.html#af43c48c044f954b0e0e9d4fe38347551)
		#roofitoptions.Add(ROOT.RooFit.Extended(ROOT.kTRUE)) # Add extended likelihood term 
		#roofitoptions.Add(ROOT.RooFit.Minimizer("Minuit2")) # Use the Minuit2 minimizer (possible options: OldMinuit, Minuit (default), Minuit2, GSLMultiMin, GSLSimAn)
		##roofitoptions.Add(ROOT.RooFit.Verbose(ROOT.kFALSE)) # Disable verbosity 

		self.FitSampleStr("HP:tt:real:model", "HP:ttrealW", massvar, self.directory["fitMC"]+"SignalHP.pdf") # TODO: give "fitMC" and name as arguments and create everything within FitSample (plot, stream, snapshoot)


		self.FitSampleStr("HP:VV:model", "HP:VV", massvar, self.directory["fitMC"]+"VVbackgroundHP.pdf")


		self.FitSampleStr("HP:st:model", "HP:st", massvar, self.directory["fitMC"]+"STbackgroundHP.pdf")

		
		self.FitSampleStr("HP:tt:fake:model", "HP:ttfakeW", massvar, self.directory["fitMC"]+"TTfakeWHP.pdf")


		#fitstuff = {
		#	signalmodel:ttsample, 
		#	VVmodel:VVsample, 
		#	STmodel:STsample,
		#}

		#plot, results = self.FitSample(fitstuff, massvar) # Working 

		

		#canvas = ROOT.TCanvas("canvas", "Fit to tt realW", 800, 600)
		#plot.Draw()

		#canvas.Print("fittest.pdf")

	def FitControlRegion(self, options): 
		print "Fitting data and MC... "
		#self.FitMC(options)

		massvar = self.LoadVariable(options.massvar)

		fullMC = ROOT.RooDataSet(self.LoadDataset1D("HP:WJets", massvar), "HP:fullMC")
		fullMC.append(self.LoadDataset1D("HP:st", massvar))
		fullMC.append(self.LoadDataset1D("HP:VV", massvar))
		fullMC.append(self.LoadDataset1D("HP:ttfakeW", massvar))
		fullMC.append(self.LoadDataset1D("HP:ttrealW", massvar))

		fullMC.Print()


		modelMC = self.LoadPdf("HP:fullMC:model")

		modelWJets = modelMC.pdfList().find("HP:WJets:model") 

		print "Parameters:", modelMC.getParameters(fullMC).find("HP:WJets:offset") # works! 

		self.AddConstraint(modelMC.getParameters(fullMC).find("HP:WJets:offset"), 61., 10.)

		self.FixAllParameters(self.LoadPdf("HP:fullMC:model").pdfList().find("HP:WJets:shape"), fullMC)

		self.FixParameter(self.LoadPdf("HP:fullMC:model").pdfList().find("HP:st:shape"), fullMC, "HP:st:mean")

		STshape = self.GetComponent(self.LoadPdf("HP:fullMC:model"), "HP:st:shape")

		self.FixParameter(self.LoadPdf("HP:fullMC:model"), fullMC, "HP:st:sigma") # also works 



		modelMC.Print()

		MCfitresult, MCplot = self.FitSample({modelMC:fullMC}, massvar, self.directory["fitMC"]+"FullMCFit.pdf")

		#data = self.workspace.data("HP:data")
		modelData = self.LoadPdf("HP:data:model")
			





	def FitSampleStr(self, modelname, samplename, variable, saveas="", fitoptions=None): 
		sample = self.LoadDataset1D(samplename, variable)
		model = self.LoadPdf(modelname)
		return self.FitSample({model:sample}, variable, saveas, fitoptions)

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
			result = model.fitTo(dataset, ROOT.RooFit.Save(1), ROOT.RooFit.SumW2Error(ROOT.kTRUE), ROOT.RooFit.Extended(ROOT.kTRUE), ROOT.RooFit.Minimizer("Minuit2")) 
			fitresult.append(result)
			dataset.plotOn(plot, ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
			model.plotOn(plot)

			if (self.verbose): 
				result.Print()
			

		if not (saveas == ""):
			canvas = ROOT.TCanvas("canvas", "Fit", 800, 600)
			plot.Draw()

			canvas.Print(saveas)

		return plot, fitresult

	def TestFit(self): 
		self.MakeFitModel(True)

		variable = self.workspace.var(self.fitvarname)

		dataset = self.LoadDataset1D("HP:ttrealW", variable)
		dataset.Print()


		model = self.workspace.pdf("HP:tt:real:model")
		#ttrealWmean   = ROOT.RooRealVar("HP:tt:mean", "HP:tt:mean", 89., 80., 95.) 
		#ttrealWsigma  = ROOT.RooRealVar("HP:tt:sigma", "HP:tt:sigma", 8., 2.5, 50.)
		#ttrealWalpha1  = ROOT.RooRealVar("HP:tt:alpha1", "HP:tt:alpha1", 0.5, 0.1, 10.) 
		#ttrealWalpha2  = ROOT.RooRealVar("HP:tt:alpha2", "HP:tt:alpha2", 1.0, 0.1, 10.) 
		#ttrealWsign1   = ROOT.RooRealVar("HP:tt:sign1", "HP:tt:sign1", 0.2, 0.01, 5.)
		#ttrealWsign2   = ROOT.RooRealVar("HP:tt:sign2", "HP:tt:sign2", 0.2, 0.01, 10.) 
		#ttrealWshape = ROOT.RooDoubleCrystalBall("HP:tt:real:shape","HP:tt:real:shape", variable, ttrealWmean, ttrealWsigma, ttrealWalpha1, ttrealWsign1, ttrealWalpha2, ttrealWsign2)
		#ttrealWnumber = ROOT.RooRealVar("HP:tt:real:number", "HP:tt:real:number", 500., 100., 1e20)
		#model = ROOT.RooExtendPdf("HP:tt:real:model", "HP:tt:real:model", ttrealWshape, ttrealWnumber)

		#mean = ROOT.RooRealVar("HP:tt:mean", "HP:tt:mean", 89., 50., 130.) 
		#sigma = ROOT.RooRealVar("HP:tt:sigma", "HP:tt:sigma", 8., 2.5, 100.)
		#shape = ROOT.RooGaussian("HP:tt:Gaussian", "HP:tt:Gaussian", variable, mean, sigma)

		#model = shape 

		snapshot = self.workspace.getSnapshot("ttinitial")
		params = model.getParameters(ROOT.RooArgSet(variable))
		#params = snapshot

		roofitoptions = ROOT.RooLinkedList()
		roofitoptions.Add(ROOT.RooFit.Save(1)) # Produce the fit result
		roofitoptions.Add(ROOT.RooFit.SumW2Error(ROOT.kTRUE)) # Interpret errors as errors on MC (see https://root.cern.ch/doc/master/classRooAbsPdf.html#af43c48c044f954b0e0e9d4fe38347551)
		roofitoptions.Add(ROOT.RooFit.Extended(ROOT.kTRUE)) # Add extended likelihood term 
		roofitoptions.Add(ROOT.RooFit.Minimizer("Minuit2")) # Use the Minuit2 minimizer (possible options: OldMinuit, Minuit (default), Minuit2, GSLMultiMin, GSLSimAn)


		plot = variable.frame()
		result = model.fitTo(dataset, ROOT.RooFit.Save(1), ROOT.RooFit.SumW2Error(ROOT.kTRUE), ROOT.RooFit.Extended(ROOT.kTRUE), ROOT.RooFit.Minimizer("Minuit2")) 
		result.Print()
		dataset.plotOn(plot, ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
		model.plotOn(plot)
		canvas = ROOT.TCanvas("canvas", "Fit", 800, 600)
		plot.Draw()
		canvas.Update()

		savename = "testfit.pdf"
		print "Do you want to save the plot as '{}' ?".format(savename)
		if(self.PromptYesNo(True)): 

			canvas.Print(savename)

		self.workspace.saveSnapshot(model.GetName()+"fitMC", model.getParameters(ROOT.RooArgSet(variable)), ROOT.kTRUE)



	def MakeFitModel(self, importmodel=False): 
		print "Making fit model"

		fitvariable = self.workspace.var(self.fitvarname)
		#self.workspace.factory("DoubleCrystalBall::HP:tt:SignalModel({}, signalMean1[80., 100.], signalMean1[-10., 10.], signalSigma[0., 50.], signalSigma[0., 50.], sign1[0.01, 5.], sign1[0.01, 10.]".format(self.fitvarname)) # TODO: check how we can use the factory syntax with custom Pdfs. 

		# Signal model in the HP category 
		ttrealWmean   = ROOT.RooRealVar("HP:tt:mean", "HP:tt:mean", 89., 80., 95.) 
		ttrealWsigma  = ROOT.RooRealVar("HP:tt:sigma", "HP:tt:sigma", 8., 2.5, 50.)
		ttrealWalpha1  = ROOT.RooRealVar("HP:tt:alpha1", "HP:tt:alpha1", 0.5, 0.1, 10.) 
		ttrealWalpha2  = ROOT.RooRealVar("HP:tt:alpha2", "HP:tt:alpha2", 1.0, 0.1, 10.) 
		ttrealWsign1   = ROOT.RooRealVar("HP:tt:sign1", "HP:tt:sign1", 0.2, 0.01, 5.)
		ttrealWsign2   = ROOT.RooRealVar("HP:tt:sign2", "HP:tt:sign2", 0.2, 0.01, 10.) 
		ttrealWshape = ROOT.RooDoubleCrystalBall("HP:tt:real:shape","HP:tt:real:shape", fitvariable, ttrealWmean, ttrealWsigma, ttrealWalpha1, ttrealWsign1, ttrealWalpha2, ttrealWsign2)
		ttrealWnumber = ROOT.RooRealVar("HP:tt:real:number", "HP:tt:real:number", 500., 0., 1e20)
		ttrealWmodel = ROOT.RooExtendPdf("HP:tt:real:model", "HP:tt:real:model", ttrealWshape, ttrealWnumber)
		if (simplemodel): ttrealWmodel = ttrealWshape

		#getattr(self.workspace, "import")(signalModel)
		if (importmodel): 
			self.ImportToWorkspace(ttrealWmodel, True)

		#self.workspace.saveSnapshot("ttinitial", ttrealWmodel.getParameters(ROOT.RooArgSet(fitvariable)), ROOT.kTRUE)
		#params = signalModel.getParameters(fitvariable)
		#self.workspace.defineSet("signalParams", params)
		#self.workspace.saveSnapshot("buildmodel", params, ROOT.kTRUE)

		# Background unmerged tt model
		ttfakeWoffset = ROOT.RooRealVar("HP:tt:fake:offset" ,"HP:tt:fake:offset", 90, 10, 200) # 90, 10, 200
		ttfakeWwidth  = ROOT.RooRealVar("HP:tt:fake:width" ,"HP:tt:fake:width", 40, 25, 300) # 40, 25, 100
		ttfakeWcoefficient  = ROOT.RooRealVar("HP:tt:fake:coefficient" ,"HP:tt:fake:coefficient", -0.03, -1., 0.) # -0.04, -1, 0.
		ttfakeWshape     = ROOT.RooErfExpPdf("HP:tt:fake:shape", "HP:tt:fake:shape" ,fitvariable, ttfakeWcoefficient, ttfakeWoffset, ttfakeWwidth)
		ttfakeWnumber = ROOT.RooRealVar("HP:tt:fake:number", "HP:tt:fake:number", 0., 1e15)
		ttfakeWmodel = ROOT.RooExtendPdf("HP:tt:fake:model", "HP:tt:fake:model", ttfakeWshape, ttfakeWnumber)
		if (simplemodel): ttfakeWmodel = ttfakeWshape
		if (importmodel): 
			self.ImportToWorkspace(ttfakeWmodel)

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
		if (importmodel): 
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
		if (importmodel): 
			self.ImportToWorkspace(STmodel)

		# Backgound W+Jets model
		WJetscoeff  = ROOT.RooRealVar("HP:WJets:coefficient", "HP:WJets:coefficient", -0.026, -0.05, 0.05)
		WJetsoffset = ROOT.RooRealVar("HP:WJets:offset", "HP:WJets:offset" ,41. ,0., 100)
		WJetswidth  = ROOT.RooRealVar("HP:WJets:width", "HP:WJets:width", 30., 1., 100.)
		WJetsshape  = ROOT.RooErfExpPdf("HP:WJets:shape", "HP:WJets:shape", fitvariable, WJetscoeff, WJetsoffset, WJetswidth)
		WJetsnumber = ROOT.RooRealVar("HP:WJets:number", "HP:WJets:number", 0., 1e15)
		WJetsmodel = ROOT.RooExtendPdf("HP:WJets:model", "HP:WJets:model", WJetsshape, WJetsnumber)
		if (simplemodel): WJetsmodel = WJetsshape
		if (importmodel): 
			self.ImportToWorkspace(WJetsmodel, True)

		if (importmodel): 
			self.workspace.saveSnapshot("buildmodel", ROOT.RooArgSet(STcoeff, STwidth, SToffset, STmean, STsigma, STfactor), ROOT.kTRUE) # works! 
			#self.workspace.saveSnapshot("buildmodel", VVmodel.getParameters(ROOT.RooArgSet(fitvariable)), ROOT.kTRUE) # works too - recommended! 

		# Full background model (MC)
		fullbackgroundMCnumber = ROOT.RooRealVar("HP:background:MC:number", "HP:background:MC:number", 0., 1e15)
		fullbackgroundMCmodel = ROOT.RooExtendPdf("HP:background:MC:model", "HP:background:MC:model", ttfakeWshape, fullbackgroundMCnumber)
		#self.ImportToWorkspace(fullbackgroundMCmodel)

		# Full signal model (MC)
		fullsignalMCnumber = ROOT.RooRealVar("HP:signal:MC:number", "HP:signal:MC:number", 0., 1e15)
		fullsignalMCmodel = ROOT.RooExtendPdf("HP:signal:MC:model", "HP:signal:MC:model", ttrealWshape, fullsignalMCnumber)

		mcTTnumber = ROOT.RooRealVar("HP:MC:number", "HP:MC:number", 500., 0., 1e20)

		fullMCmodel = ROOT.RooAddPdf("HP:fullMC:model", "HP:fullMC:model", ROOT.RooArgList(WJetsshape, VVshape, STshape, ttfakeWshape, ttrealWshape), ROOT.RooArgList(WJetsnumber, VVnumber, STnumber, ttfakeWnumber, mcTTnumber))
		print fullMCmodel

		if (importmodel): 
			self.ImportToWorkspace(fullMCmodel, True, ROOT.RooFit.RecycleConflictNodes())

		# Full background model in for data
		fullbackgrounddatanumber = ROOT.RooRealVar("HP:background:data:number", "HP:background:data:number", 0., 1e15)
		fullbackgrounddatamodel = ROOT.RooExtendPdf("HP:background:data:model", "HP:background:data:model", ttrealWshape, fullbackgrounddatanumber)
		#if (importmodel): 
			#self.ImportToWorkspace(fullbackgrounddatamodel)

		# Full signal model for data
		fullsignaldatanumber = ROOT.RooRealVar("HP:signal:data:number", "HP:signal:data:number", 0., 1e15)
		fullsignaldatamodel = ROOT.RooExtendPdf("HP:signal:data:model", "HP:signal:data:model", ttrealWshape, fullsignaldatanumber)

		fulldatamodel = ROOT.RooAddPdf("HP:data:model", "HP:data:model", ROOT.RooArgList(fullsignaldatamodel, fullbackgrounddatamodel))
		if (importmodel): 
			self.ImportToWorkspace(fulldatamodel, True, ROOT.RooFit.RecycleConflictNodes())

		#self.workspace.saveSnapshot("buildmodel", ROOT.RooArgSet(fullMCmodel.getParameters(ROOT.RooArgSet(fitvariable)), fulldatamodel.getParameters(ROOT.RooArgSet(fitvariable))), ROOT.kTRUE) # works too - recommended! 




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


