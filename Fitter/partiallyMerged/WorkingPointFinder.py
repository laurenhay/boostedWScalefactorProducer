#!/usr/bin/env python

import argparse
import ROOT
import sys
import os
from WtaggingFitter import WTaggingFitter
from Dataset import Dataset
import numpy as np
from rootpy.tree import Cut


overflowmargin = 20.

estimatelpstats = False


ROOT.gROOT.LoadMacro("PlotROC.C")


parser = argparse.ArgumentParser(description='WorkingPointDetermination')

parser.add_argument('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
parser.add_argument('-d','--dry', action = 'store_true', help = 'Run in dry mode (just displaying WP but not creating workspaces)')
parser.add_argument('-v', '--verbose', dest="verbose", action='store_true', default=False, help="Print out more messages.")
parser.add_argument('-y', '--year', dest="year", default = "all", help="The year for which you want to create the workspace. ")
parser.add_argument('fakerate', default=None, type=float, help="The desired fake-rate. ")
parser.add_argument('--workspace', action="store",type=str,dest="workspace",default="workspace", help="Name of workspace")
parser.add_argument('--sample', action="store",type=str,dest="sample",default="QCD", help='Which tt sample is used')
parser.add_argument('--tagger', action="store",type=str,dest="tagger",default="SelectedJet_tau21", help="Name of tagger variable (tau32/tau21/ddt)")
parser.add_argument('--massvar', action="store",type=str,dest="massvar",default="SelectedJet_softDrop_mass", help="Name of mass variable to fit")
parser.add_argument('--minX', action="store", type=float,dest="minX",default=50. , help="Lower mass cut")
parser.add_argument('--maxX', action="store", type=float,dest="maxX",default=130., help="Upper mass cut")
parser.add_argument('--weightvar', dest="weightvar", type=str, default="weight", help="The name of the event weight variable in the tree.")
parser.add_argument('--HP', action="store", type=float,dest="cutHP",default=0.35)
parser.add_argument('--LP', action="store", type=float,dest="cutLP",default=0.75)
parser.add_argument('-p', '--precision', action='store', type=int, dest="precision", default = 10000, help="The number f working points to test. ")
parser.add_argument('--min', action="store", type=float, dest="min",default=0. , help="Lower limit of the range of tagger values considered. ")
parser.add_argument('--max', action="store", type=float, dest="max",default=1., help="Upper limit of the range of tagger values considered. ")
#parser.add_argument('--ptmin', action="store", type=float,dest="pTmin",default=200., help="Lower pT cut")
#parser.add_argument('--ptmax', action="store", type=float,dest="pTmax",default=10000., help="Upper pT cut")


class DummyOptions: 
	def __init__(self, year, batchmode, verbose, filename, HP, LP, tagger, weightvar, massvar, min, max): 
		self.noX = batchmode
		self.verbose = verbose
		#self.dry = dry
		self.doBinnedFit = False # TODO: fix this hack
		self.workspace = filename
		self.year = year
		self.doWS = True
		self.cutHP = HP
		self.cutLP = LP
		self.massvar = massvar
		self.maxX = max
		self.minX = min
		self.weightvar = weightvar
		self.tagger = tagger

	def Description(): 
		print "This is a dummy options class"


def GetWorkingPoint(year, options): 

	background = GetChain(options.sample, year)

	efficiency = []
	error = []
	#increment = (options.max - options.min)/float(options.precision)

	for cutvalue in np.linspace(options.min, options.max, options.precision):
		print "Testing cut value at: {}".format(cutvalue)
		eff, err = GetEfficiency(cutvalue, background)
		efficiency.append(eff)
		error.append(err)

	return efficiency[0] #TODO: fix



def GetChain(sample, year): 
	dataset = Dataset(year)

	chain = ROOT.TChain("Events")	

	for file in dataset.getSample(sample):
		assert(os.path.isfile(file)), "ERROR: The file: {} does not exist! You may want to update the directory/file name in Dataset.py.".format(file)
		chain.Add(file)

	return chain



def GetEfficiency(cutvalue, chain): 
	
	maxVal = chain.GetMaximum(variable)+overflowmargin
	minVal = chain.GetMinimum(variable)-overflowmargin	

	passcutHP = ROOT.TH1D("passHP", "passHP", 1, minVal, maxVal) # TODO: make it one histogram, with 2 bins having the edge at the cut 
	passcutLP = ROOT.TH1D("passLP", "passLP", 1, minVal, maxVal)
	total = ROOT.TH1D("total", "total", 1, minVal, maxVal)
	passcutHP.Sumw2()
	passcutLP.Sumw2()
	total.Sumw2()	
	

	chain.Draw(variable+">>"+passcutHP.GetName(), weight*(basecut & cutHP))
	chain.Draw(variable+">>"+passcutLP.GetName(), weight*(basecut & cutLP))
	chain.Draw(variable+">>"+total.GetName(), weight*(basecut))	
	

	NpassHP = passcutHP.Integral()
	NpassLP = passcutLP.Integral()
	Ntotal = total.Integral()	

	print NpassHP, Ntotal 	

	effHP = passcutHP.Divide(total)
	effErrHP = passcutLP.Divide(total)	

	return effHP, effErrHP #TODO: fix


if __name__ == '__main__':

	options = parser.parse_args()	


	if (options.noX): 
		ROOT.gROOT.SetBatch(True)
	

	assert(options.fakerate > 0. and options.fakerate < 1.), "ERROR: Invalid fake-rate: {}. You must specify a fakerate in ]0,1[. ".format(options.fakerate)	
	

	allyears = [2016, 2017, 2018]
	if (options.year == "all"): 
		years = allyears
	else: 
		assert (int(options.year) in allyears), "ERROR: Invalid year, please specify a year parameter from the following: '2016', '2017', '2018', 'all'."
		years = [int(options.year)]	

	variable = options.tagger
	weight = Cut("eventweightlumi") #options.weightvar	
	basecut = Cut("SelectedJet_pt>300. && SelectedJet_pt<500.")
	signalcut = Cut("genmatchedAK82017")
	#cutHP = Cut("SelectedJet_tau21<0.35")
	#cutLP = Cut("SelectedJet_tau21<0.75 && SelectedJet_tau21>=0.35")

	cut = weight*basecut
	cutsignal = weight*signalcut

	years = [2020] # TODO: remove 

	fakerate = int(options.fakerate*100.)
	

	HP = {}
	LP = {}

	# Looping over all years to determie the working points 
	for year in years: 
		backgroundchain = GetChain(options.sample, year)
		signalchain = GetChain("tt", year)

		# Using a previously written C++ script hacked for the purpose (super fast)
		HP[year] = ROOT.PlotROC(signalchain, backgroundchain, options.tagger, cutsignal, cut, options.fakerate, 10000, "fakerate{}ROC.root".format(fakerate), options.verbose)

		#print HP[year]

		if  (estimatelpstats): 
			file = ROOT.TFile.Open("stats{}{}background.root".format(year, options.tagger), "UPDATE")
			histo = ROOT.TH1D("histo{}".format(fakerate), options.tagger+" distribution in background (QCD) for fakerate {}\%".format(fakerate), 200, backgroundchain.GetMinimum(options.tagger), backgroundchain.GetMaximum(options.tagger))
			backgroundchain.Draw(options.tagger+">>"+histo.GetName(), cut*Cut(options.tagger+">{}".format(WP)))
			file.Write()
			file.Close()

	print "Working points: HP: {}, LP: {}.".format(HP, LP)

	LP[2020] = 0.7 # TODO: remove

	if not options.dry: 
		print "Creating workspace: {}".format(options.workspace)

		for year in years: 
			HPcut = HP[year]
			LPcut = LP[year]
			print "Creating workspace for {} with HP cut: {} and LP cut: {}".format(year, HPcut, LPcut)

			workspacefilename = options.workspace+str(year)
			opt = DummyOptions(year, options.noX, options.verbose, workspacefilename, HPcut, LPcut, options.tagger, options.weightvar, options.massvar, options.minX, options.maxX)

			fitter = WTaggingFitter(opt)




		


	


