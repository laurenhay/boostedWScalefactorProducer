#! /usr/bin/env python

from __future__ import division, print_function
import os, multiprocessing, math
from array import array
import ROOT
import numpy as np

import argparse

import MC_scalings

parser = argparse.ArgumentParser(description="This scripts adds a weight to account for the equivalent luminosity of the MC samples. The new weight variables needs to be multiplied by the luminosity of data before being added to the eventWeight. ")
parser.add_argument(action='store', type=str, dest='directory', default="/work/mhuwiler/data/WScaleFactors/UL2017/UL17_Wtagging_files/", help="Sample or directory of samples where the luminosity weight will be added. ")
parser.add_argument('-f', '--filter', action='store', type=str, dest='filter', default="")
parser.add_argument('-k', '--exclude', action='store', type=list, dest='excluded', default=["SingleMuon", "EGamma"], help="Provide here a list of patterns which, if contained in a sample name, will lead to this sample being ignored. ")
parser.add_argument('--singlethread', action='store_true', dest='singlecore', default=False, help="Run single threaded (use for debugging)")
parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help="More information print out (for the sequence to make sense, you may want to use option '--singlethread' as well).")

args = parser.parse_args()

filterset   = args.filter #TODO: remove 

##############################

def processFile(filename, verbose=False):
    sample = os.path.basename(filename).replace(".root", "")
    if (verbose): print("Processing file {}".format(sample))

    isMC = True
    if (np.any([pattern in sample for pattern in args.excluded])):
        isMC = False
    print(isMC) #TODO: remove

    
    #filename = args.directory + '/' + sample + '.root'
    
    file = ROOT.TFile(filename, 'UPDATE')
    file.cd()

    weight = 1.

    if isMC:
        # number of events
        rundata = file.Get('Runs')

        genH = ROOT.TH1D("genH_%s" % sample, "", 1, 0, 0)
        genH.Sumw2()
        #rundata.Draw("genEventSumw>>genH_%s" % sample, "", "goff")
        rundata.Draw("genEventCount_>>genH_%s" % sample, "", "goff")
        genEv = genH.GetMean()*genH.GetEntries()
        print(genEv)
        
        # Cross section
        #XS = getXsec(sample)
        #SF = getSF(sample)
        
        #Leq = LUMI*XS/genEv if genEv > 0 else 0.
        #print(Leq)

        lumidict = MC_scalings.dict_MCscaling_UL17

        parts = sample.split("_")

        key = sample
        number = len(parts)

        while (not key in lumidict.keys()): # Assumes the key in the dict is a truncated name of the file
            number-=1
            key = "_".join(parts[0:number])
            if (number == 0): 
                print("ERROR: Sample '{}'' not found in dictionary, not setting lumiWeight.".format(sample))
                return

        print("Sample: {}, key: {}".format(sample, key))
        crosssection = lumidict[key][0]
        numevents = lumidict[key][1]

        weight = float(crosssection)*1000./float(numevents)

        if (verbose) : print("Cross section: {}, number of events: {}, weight: {}".format(crosssection, numevents, weight))




    #else: Leq = 1.
    
    print(sample, ": lumiWeight =", weight)
    
    # Variables declaration
    lumiWeight = array('f', [1.0])  # global event weight with lumi
    
    # Looping over file content
    # Tree
    tree = file.Get('Events')
    nev = tree.GetEntriesFast()
    
    # New branches
    branch = tree.Branch('lumiWeight', lumiWeight, 'lumiWeight/F')

    # looping over events
    for event in range(0, tree.GetEntries()):
        if verbose and (event%10000==0 or event==nev-1): 
            print(' = TTree:', tree.GetName(), 'events:', nev, '\t', int(100*float(event+1)/float(nev)), '%\r')
        
        tree.GetEntry(event)

        
        lumiWeight[0] = weight 
            
        # Fill the branches
        branch.Fill()

    tree.Write("", ROOT.TObject.kOverwrite)
        
    file.Close() 



if not os.path.exists(args.directory):
    print('Origin directory', args.directory, 'does not exist, aborting...')
    exit()

jobs = []
if (os.path.isfile(args.directory)): 
    processFile(args.directory, args.verbose)
else: 
    for d in os.listdir(args.directory):
        if not '.root' in d: continue
        if len(filterset)>0 and not filterset in d: continue
        
        if args.singlecore:
            print(" -", d)
            processFile(args.directory+'/'+d, args.verbose)
        else:
            p = multiprocessing.Process(target=processFile, args=(d,args.verbose,))
            jobs.append(p)
            p.start()
        #exit()
    
print('\nDone.')

