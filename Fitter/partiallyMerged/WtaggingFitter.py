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

		# Defining the samples
		self.background = ["tt", "VV", "SingleTop"] # TODO: define a class "sample" with a chain and cut on it 


		self.MakeFitModel()



	def FitMC(self, options): 
		print "Fitting MC... "

		ttsample = self.workspace.data("HP:ttrealW")

		massvar = self.workspace.var(options.massvar)

		model = self.workspace.pdf("HP:tt:signalModel")



		fitresult = model.fitTo(ttsample)

		print fitresult

		plot = massvar.frame()

		model.plotOn(plot)
		ttsample.plotOn(plot)

		canvas = ROOT.TCanvas("canvas", "Fit to tt realW", 800, 600)
		plot.Draw()

		canvas.Print("fittest.pdf")


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
		self.ImportToWorkspace(signalModel, True)
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


