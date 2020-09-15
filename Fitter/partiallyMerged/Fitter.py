#!/usr/bin/env python

"""
class Fitter

The Fitter class is a virtual super class containing boilerplate code for file handling, workspace
creation and handling, and plotting. It can and should be used as super class for an application
specific Fitter (inheriting) class, which reimplements the task specific methods: CreateWorkspace, 
MakeFitModel, Fit, and any number of additional relevant methods. 


Copyright   2020    Marc Huwiler  <marc.huwiler@cern.ch>, <marc.huwiler@windowlive.com>


Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
and associated documentation files (the "Software"), to deal in the Software without restriction, 
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, 
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial 
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT 
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import ROOT
import os
import sys
import atexit


class Fitter: 
	def __init__(self, options):
		print "Initialising Fitter"

		self.verbose = options.verbose
		self.binned = options.doBinnedFit
		#atexit.register(self.Cleanup)

		# Setting the verbosity of RooFit
		# TODO: set verbosity levels in options (enable self.verbosity (True) if greater than 0 and add dictionary to map int to RooFit level)
		if self.verbose: 
			ROOT.RooMsgService.instance().setSilentMode(False)
		else: 
			ROOT.RooMsgService.instance().setSilentMode(True)
			ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING)

		ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.DEBUG) #DEBUG,INFO,PROGRESS,WARNING,ERROR or FATAL
		
		# --- Open the workspace
		self.workspace = self.OpenWorkspace(options)

		# --- Attributes used in this class's methods, shoud be overriden in daughter class
		self.saveconstraints = False
		self.savemodel = False


	def Cleanup(self):
		if hasattr(self, "file"): 
			self.file.Close()

	def CreateWorkspace(self, options, filename): 
		raise NotImplementedError()

	def MakeFitModel(self): 
		raise NotImplementedError()

	def ImportToWorkspace(self, stuff, autosave=False, options=ROOT.RooFit.Silence()): 
		# TODO: check if an object with given name already exists in workspace
		assert(getattr(self, "workspace")), "ERROR: The class has no member 'workspace' yet, cannot import to workspace."
		errorDuringImport = getattr(self.workspace, "import")(stuff, options)
		assert(not errorDuringImport), "ERROR: There was an error during the import of '{}' into the workspace! Check if the pdf or some components already exist in the workspace and set a conflict strategy.".format(stuff.GetName())
		if (autosave): 
			if (getattr(self, "filename")): 
				self.SaveWorkspace()
			else: 
				print "WARNING: The fitter has no attribute 'filename', cannot save workspace to file. "
		return

	def SaveWorkspace(self, filename=""): 
		assert(getattr(self, "workspace")), "ERROR: The class has no member 'workspace' yet, unable to save it to file." 
		if (filename == ""): 
			assert(getattr(self, "filename")), "ERROR: No filename was provided and the class has no member 'filename', cannot save workspace." 
			filename = self.filename
		self.workspace.writeToFile(filename)
		#ROOT.gDirectory.Add(self.workspace) # Also works
		# Thanks to Bruno Lenzi for this hack
		ROOT.SetOwnership(self.workspace, 0) # Discard the workspace from python's garbage collector to avoid double deletion (is owned by the TFile)
		return

	def GetComponent(self, model, component): 
		comp = model.pdfList().find(component)
		assert(comp), "ERROR: The model '{}' does not contain a component named '{}'!".format(model.GetName(), component)
		return comp

	def AddConstraint(self, variablename, mean, sigma):
		variable = self.LoadVariable(variablename)
		return self.AddConstraintBase(variable, mean, sigma)

	def AddConstraintBase(self, variable, mean, sigma):
		mean = ROOT.RooRealVar(variable.GetName()+"_mean", variable.GetName()+"_mean", mean)
		sigma = ROOT.RooRealVar(variable.GetName()+"_sigma", variable.GetName()+"_sigma", sigma)
		constraintpdf = ROOT.RooGaussian("constraintpdf_"+variable.GetName(), "constraintpdf_"+variable.GetName(), variable, mean, sigma)
		self.constraintlist.append(constraintpdf.GetName())
		self.ImportToWorkspace(constraintpdf, self.saveconstraints)
		if (self.verbose): 
			print "Added Gaussian constraint to parameter '{}', with mean '{}': {}, and sigma '{}': {}. ".format(variable.GetName(), mean.GetName(), mean.getVal(), sigma.GetName(), sigma.getVal())
		return constraintpdf

	def FixAllParameters(self, modelname, datasetname, variables, binned = False):
		variableset = self.ComposeRooArgSet(variables)
		model = self.LoadPdf(modelname)
		dataset = self.LoadDataset(datasetname, variableset, binned)
		return self.FixAllParametersBase(model, dataset)

	def FixAllParametersBase(self, model, dataset):
		parameters = model.getParameters(dataset) # TODO: Make also accept string as model 
		paramIter = parameters.createIterator()
		paramIter.Reset()
		param=paramIter.Next()
		while (param):
			param.setConstant(True)
			param=paramIter.Next()
		if (self.verbose): 
			print "Fixed all parameters of model '{}'.".format(model.GetName())

	def FixParameter(self, modelname, datasetname, variables, parametername, binned = False):
		variableset = self.ComposeRooArgSet(variables)
		model = self.LoadPdf(modelname)
		dataset = self.LoadDataset(datasetname, variableset, binned)
		return self.FixParameterBase(model, dataset, parametername)

	def FixParameterBase(self, model, dataset, parametername):
		parameters = model.getParameters(dataset)
		param = parameters.find(parametername)
		assert(param), "ERROR: The model '{}' does  not contain any parameter named '{}'. Check if the parameter name and dataset provided are correct!".format(model.GetName(), parametername)
		param.setConstant(True)
		if (self.verbose): 
			print "Fixed parameter '{}' in model '{}'.".format(parametername, model.GetName())

	# python style overload of methods
	def ComposeRooArgSet(self, variables): 
		variableset = ROOT.RooArgSet()

		if isinstance(variables, str):
			variableset = ROOT.RooArgSet(self.LoadVariable(variables))

		elif isinstance(variables, list): 
			for variable in variables: 
				assert(isinstance(variable, str)), "ERROR: The variable is not a list of 'str', please make sure to provide a list of 'str', or another supported type!"
				variableset.add(self.LoadVariable(variable))

		elif isinstance(variables, ROOT.RooRealVar): 
			assert(variables.InheritsFrom("RooRealVar")), "ERROR: The variable does not inherit from class 'RooRealVar', case resolution seems odd!"
			variableset = ROOT.RooArgSet(variables)

		elif isinstance(variables, ROOT.RooArgSet): 
			assert(variables.InheritsFrom("RooArgSet")), "ERROR: The variable does not inherit from class 'RooArgSet', case resolution seems odd!"
			variableset = variables 
		else: 
			print "ERROR: The parameter 'variable' is of unsupported type: {}. Please provide the argument 'variables' as 'str', 'list', 'RooRealVar' or 'RooArgSet'!".format(type(variables))
			raise TypeError()

		return variableset

	def GetCurrentValue(self, name): 
		variable = self.LoadVariable(name)
		return variable.getVal()

	def SetValue(self, name, value): 
		variable = self.LoadVariable(name)
		#TODO: check if value is valid
		variable.setVal(value)

	def LoadSnapshot(self, snapshotname): 
		if (self.verbose): 
			print "Loading snapshot: '{}'.".format(snapshotname)
		# TODO: Check if the snapshot exists in the workspace 
		#params = model.getParameters(dataset)
		self.workspace.loadSnapshot(snapshotname)

	def SaveSnapshot(self, model, dataset, snapshotname): 
		#self.workspace.saveSnapshot(snapshotname, model.getParameters(dataset), True)
		self.SaveSnapshotParams(model.getParameters(dataset), snapshotname) # TODO: check if we could use the fit variable instead of the dataset

	def SaveSnapshotParams(self, params, snapshotname): 
		if (self.verbose): 
			print "Saving a snapshot of the following parameters:"
			params.Print()
		self.workspace.saveSnapshot(snapshotname, params, True)

	def SnapShot(self, model, dataset): 
		params = model.getParameters(dataset)
		snap = params.snapshot()
		return snap

	def LoadVariable(self, name): 
		assert(self.workspace.var(name)), "ERROR: The workspace does not contain any variable named '{}'!".format(name)
		return self.workspace.var(name)

	# Wrapper function to display an error message if the pdf does not exist in the workspace
	def LoadPdf(self, name): 
		assert(self.workspace.pdf(name)), "ERROR: The workspace does not contain any pdf named '{}'!".format(name)
		return self.workspace.pdf(name) 

	def LoadDataset1D(self, name, variable, cutrange = None, binned = None): 
		if (cutrange != None): 
			assert(isinstance(cutrange, str)), "ERROR: The arguemet 'cutrange' provided: {} is of wrong type. Should be a 'str'!".format(cutrange) # TODO: make it possible to also provide char cuts 
			cutrange = ROOT.RooFit.CutRange(cutrange) # Also use cut for string expression 
		return self.LoadDataset(name, ROOT.RooArgSet(variable), cutrange, binned)

	def LoadDataset(self, name, variables, cut = None, binned = None): 
		assert(self.workspace.data(name)), "ERROR: The workspace does not contain any dataset named '{}'!".format(name)
		# TODO: check if the dataset depends on the variables given in the RooArgSet
		dataset = self.workspace.data(name)
		if (cut != None): 
			dataset = dataset.reduce(cut)
		dataset = dataset.reduce(variables)
		if (binned == None): 
			binned = self.binned
		assert(binned in [0, 1]), "ERROR: The parameter 'binned' provided: {}, is invalid, should be a boolean.".format(binned)
		if (binned): 
			dataset = dataset.binnedClone()
		return dataset

	def CreateDataset(self, files, name, variables, cut, weightvariable): 
		print "Creating dataset {}".format(name)   

		chain = ROOT.TChain("Events")
		for file in files:
			assert(os.path.isfile(file)), "ERROR: The file: {} does not exist! You may want to update the directory/file name in Dataset.py.".format(file)
			chain.Add(file)

		if (self.verbose): print "Tree with {} entries.".format(chain.GetEntries())

		if (self.verbose): print "Importing dataset '{}' with cut '{}' from: {}".format(name, cut, ", ".join(files))
		dataset = ROOT.RooDataSet(name, name, chain, variables, cut, weightvariable)

		return dataset


	def OpenWorkspace(self, options): 
		filename = options.workspace.replace(".root","")+".root"
		self.filename = filename
		if (options.doWS): #create workspace if requested 
			workspace = self.CreateWorkspace(options, filename)
			return workspace # TODO: fix this (crash at destruction)

		status, message = self.CheckWorkspaceFile(filename)
		if (status == 3): 
			# The file exists and contains a valid workspace
			self.file = ROOT.TFile(filename) #TODO: close file
			workspace  = self.file.Get(self.workspacename)
		
			workspace.SetTitle(options.workspace)
			return workspace
		else: 
			# Something is wrong with the workspace file
			print message
			print "\nDo you want to create (overwrite) the file? " # TODO: is the method writeToFile really overwriting? 
			if (self.PromptYesNo() == 'yes'):
				workspace = self.CreateWorkspace(options, filename)
				return workspace
			else: 
				print "Aborting!" 
				sys.exit()



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
				if (file.GetListOfKeys().Contains(self.workspacename)): 
					message = "File contains a workspace named: {}".format(self.workspacename)
					status = 3
				else: 
					message = "File: {} does not containt a workspace named: {}".format(filename, self.workspacename)
					status = 2
			else: 
				message = "File '{}' could not be opened".format(filename)
				status = 1
		else: 
			message = "File '{}' does not exist.".format(filename)
			status = 0

		return status, message

	def PromptYesNo(self, answerasbool=False): 
		# Inspired from Fabrice Couderc 
		rep = ''
		while not rep in [ 'yes', 'no' ]:
			rep = raw_input( "(type 'yes' or 'no'): " ).lower()
		if (answerasbool): 
			if (rep == 'yes'): 
				return True
			else: 
				return False
		return rep


