#!/usr/bin/env python

"""
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
		atexit.register(self.Cleanup)
		
		# --- Open the workspace
		self.workspace = self.OpenWorkspace(options)


	def Cleanup(self):
		if hasattr(self, "file"): 
			self.file.Close()

	def CreateWorkspace(self, options, filename): 
		raise NotImplementedError()

	def MakeFitModel(self): 
		raise NotImplementedError()

	def ImportToWorkspace(self, stuff): 
		assert(getattr(self, "workspace")), "ERROR: The class has no member 'workspace' yet, cannot import to workspace."
		getattr(self.workspace, "import")(stuff)
		return

	def SaveWorkspace(self, filename=""): 
		assert(getattr(self, "workspace")), "ERROR: The class has no member 'workspace' yet, save it to file." 
		if (filename == ""): 
			assert(getattr(self, "filename")), "ERROR: No filename was provided and the class has no member 'filename', cannot save workspace." 
			filename = self.filename
		self.workspace.writeToFile(filename)
		return


	def LoadDataset(self, name): 
		dataset = self.workspace.data(name)
		if (self.binned): 
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
			return workspace

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


