#!/usr/bin/env python


""" 
class SpecificYearConfig

The aim of this class is to constitute a wrapper for all selection criteria that depend on a specific year withing run 2. 
It consists of a set of methods that return the appropriate value according to the year, read from a csv config file. 
It was implemented in view of making the skimmer code independent of the year, and contain all diferences here. 


Authors: 	Marc Huwiler  	marc.huwiler@cern.ch
Created: 	21.07.2020

Versions: 
	- V1.0: First implementation with MuonTriggerSF


"""


import pandas as pd
import os
import errno
import sys


configfile = "$CMSSW_BASE/src/WTopScalefactorProducer/Skimmer/skimmerconfig.csv"
separator = ","


class SpecificYearConfig:
    def __init__(self, year, verbose = False): 
        assert(year in [2016, 2017, 2018]), "ERROR: Invalid year. Please set a year of run 2: '2016', '2017', '2018'!"
        self.year = year
        self.verbose = verbose

        try: 
            databasename = os.path.expandvars(configfile)
            if (self.verbose): print "Opening config file at:", databasename
            self.database = pd.read_csv(databasename, sep = separator, index_col=0) # 
            print "\nThe following values for SFs and triggers are going to be used, please acknowledge their accuracy:\n"
            print self.database
        except: 
            print "ERROR: Failed to open config file at: {}.".format(configfile) # raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), databasename) # python 3
            sys.exit()

        

    def MuonTriggerSF(pt, eta): 
        if (pt < self.database.loc["MuonTriggerSFPtThreshold", self.year]): 
          if (abs(eta) < self.database.loc["MuonTriggerSFEtaThreshold", self.year]): 
            return self.database.loc["MuonTriggerSFlowPtcentralEta", self.year]
          else: 
            return self.database.loc["MuonTriggerSFlowPthighEta", self.year]
        else: 
          if (abs(eta) < self.database.loc["MuonTriggerSFEtaThreshold", self.year]): 
            return self.database.loc["MuonTriggerSFhighPtcentralEta", self.year]
          else: 
            return self.database.loc["MuonTriggerSFhighPthighEta", self.year]


