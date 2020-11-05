#####################################
##### This script sum the genWeights from nanoAOD
##### To run: python computeGenWeights.py -d NAMEOFDATASET
#####################################

#!/usr/bin/env python
import argparse, os, shutil, sys
import numpy as np
import ROOT
import uproot
from root_numpy import root2array, tree2array
from dbs.apis.dbsClient import DbsApi  ## talk to DBS to get list of files in this dataset
dbsGlobal = DbsApi('https://cmsweb.cern.ch/dbs/prod/global/DBSReader')
dbsPhys03 = DbsApi('https://cmsweb.cern.ch/dbs/prod/phys03/DBSReader')


#####################################
def computeGenWeights( inputFiles, outputName ):
    """docstring for computeGenWeights"""

#    ### Open root files
#    intree = ROOT.TChain("Runs")
#    intree2 = ROOT.TChain("Events")
#    if isinstance(inputFiles, list):
#        for iFile in inputFiles:
#            intree.Add(iFile)
#            intree2.Add(iFile)
#    else:
#        intree.Add(inputFiles)
#        intree2.Add(inputFiles)
#    print intree.GetEntries()
#
#    ### Convert root tree to numpy array, applying cuts
#    arrays = tree2array( intree,
#                            branches=['genEventCount_', 'genEventSumw_', 'genEventSumw2_'],
#                            selection='',
#                            #stop=1000,  #### to test only, run only 1000 events
#                            )
#    arrays2 = tree2array( intree2,
#                            branches=['genWeight'],
#                            selection='',
#                            #stop=1000,  #### to test only, run only 1000 events
#                            )
#
#    #tmp = arrays['genWeight']/arrays['genWeight'][0]
#    #print 'Total number of events in sample: ', intree.GetEntries()
#    #print 'Event weights per file: ', arrays['genEventSumw']
#    print 'Total number of genEventCount in sample: ', sum(arrays['genEventCount_'])
#    print 'Total number of genEventSumw in sample: ', sum(arrays['genEventSumw_'])
#    print 'Total number of genEventSumw2 in sample: ', sum(arrays['genEventSumw2_'])
#    print 'Total sum of genWeights in sample: ', sum(arrays2['genWeight'])
#    print 'Total sum of sign(genWeights) in sample: ', sum(np.sign(arrays2['genWeight']))

    genEventSumw = 0
    genEventSumw2 = 0
    genEventCount = 0
    genWeight = 0
    for fi in inputFiles:
        ff = uproot.open(fi)
        bl = ff.get("Runs")
        try:
            genEventSumw += bl.array("genEventSumw").sum()
            genEventSumw2 += bl.array("genEventSumw2").sum()
            genEventCount += bl.array("genEventCount").sum()
        except:
            genEventSumw += bl.array("genEventSumw_").sum()
            genEventSumw2 += bl.array("genEventSumw2_").sum()
            genEventCount += bl.array("genEventCount_").sum()
        bl = ff.get("Events")
        genWeight += bl.array("genWeight").sum()

    print 'Total number of genEventCount in sample: ', genEventCount
    print 'Total number of genEventSumw in sample: ', genEventSumw
    print 'Total number of genEventSumw2 in sample: ', genEventSumw2
    print 'Total sum of genWeights in sample: ', genWeight


#####################################
if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--datasets", action='store', dest="datasets", default="ttHTobb", help="Name of dataset to process" )
    parser.add_argument("-v", "--version", action='store', dest="version", default="v00", help="Version" )
    parser.add_argument("-y", "--year", action='store', choices=[ '2016', '2017', '2018' ],  default="2017", help="Version" )

    try: args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)

    dictSamples = {}
    ####### UL 2017 samples #######
    dictSamples['UL17_TTToSemiLeptonic-powheg-pythia8'] = '/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/kadatta-boostedWtaggingSF_Skims_UL17_TTToSemiLeptonic-powheg-pythia8_newSel_SF-300f5d580f69b452436b7b3806acb636/USER'
    dictSamples['UL17_TTJets-amcatnloFXFX-pythia8'] = '/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/kadatta-boostedWtaggingSF_Skims_UL17_TTJets-amcatnloFXFX-pythia8_newSel_SF-b8e5db6dc58e02fa065eca4e059912ff/USER'
    dictSamples['UL17_TTTo2L2Nu-powheg-pythia8'] = '/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/kadatta-boostedWtaggingSF_Skims_UL17_TTTo2L2Nu-powheg-pythia8_newSel_SF-300f5d580f69b452436b7b3806acb636/USER'
    
    dictSamples['UL17_QCD_Pt-170to300-pythia8'] = '/QCD_Pt_170to300_TuneCP5_13TeV_pythia8/kadatta-boostedWtaggingSF_Skims_UL17_QCD_Pt-170to300-pythia8_newSel_SF-b8e5db6dc58e02fa065eca4e059912ff/USER'
    dictSamples['UL17_QCD_Pt-300to470-pythia8'] = '/QCD_Pt_300to470_TuneCP5_13TeV_pythia8/kadatta-boostedWtaggingSF_Skims_UL17_QCD_Pt-300to470-pythia8_newSel_SF-b8e5db6dc58e02fa065eca4e059912ff/USER'
    dictSamples['UL17_QCD_Pt-470to600-pythia8'] = '/QCD_Pt_470to600_TuneCP5_13TeV_pythia8/kadatta-boostedWtaggingSF_Skims_UL17_QCD_Pt-470to600-pythia8_newSel_SF-b8e5db6dc58e02fa065eca4e059912ff/USER'
    dictSamples['UL17_QCD_Pt-600to800-pythia8'] = '/QCD_Pt_600to800_TuneCP5_13TeV_pythia8/kadatta-boostedWtaggingSF_Skims_UL17_QCD_Pt-600to800-pythia8_newSel_SF-b8e5db6dc58e02fa065eca4e059912ff/USER'
    dictSamples['UL17_QCD_Pt-800to1000-pythia8'] = '/QCD_Pt_800to1000_TuneCP5_13TeV_pythia8/kadatta-boostedWtaggingSF_Skims_UL17_QCD_Pt-800to1000-pythia8_newSel_SF-b8e5db6dc58e02fa065eca4e059912ff/USER'
    dictSamples['UL17_QCD_Pt-1000to1400-pythia8'] = '/QCD_Pt_1000to1400_TuneCP5_13TeV_pythia8/kadatta-boostedWtaggingSF_Skims_UL17_QCD_Pt-1000to1400-pythia8_newSel_SF-b8e5db6dc58e02fa065eca4e059912ff/USER'
    dictSamples['UL17_QCD_Pt-1400to1800-pythia8'] = '/QCD_Pt_1400to1800_TuneCP5_13TeV_pythia8/kadatta-boostedWtaggingSF_Skims_UL17_QCD_Pt-1400to1800-pythia8_newSel_SF-b8e5db6dc58e02fa065eca4e059912ff/USER'
    dictSamples['UL17_QCD_Pt-1800to2400-pythia8'] = '/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/kadatta-boostedWtaggingSF_Skims_UL17_QCD_Pt-1800to2400-pythia8_newSel_SF-b8e5db6dc58e02fa065eca4e059912ff/USER'
    dictSamples['UL17_QCD_Pt-2400to3200-pythia8'] = '/QCD_Pt_2400to3200_TuneCP5_13TeV_pythia8/kadatta-boostedWtaggingSF_Skims_UL17_QCD_Pt-2400to3200-pythia8_newSel_SF-b8e5db6dc58e02fa065eca4e059912ff/USER'
    dictSamples['UL17_QCD_Pt-3200toInf-pythia8'] =  '/QCD_Pt_3200toInf_TuneCP5_13TeV_pythia8/kadatta-boostedWtaggingSF_Skims_UL17_QCD_Pt-3200toInf-pythia8_newSel_SF-b8e5db6dc58e02fa065eca4e059912ff/USER'
    dictSamples['UL17_QCD_Pt-15to7000_Flat_herwig7'] = '/QCD_Pt-15to7000_TuneCH3_Flat_13TeV_herwig7/kadatta-boostedWtaggingSF_Skims_UL17_QCD_Pt-15to7000_Flat_herwig7_newSel_SF-300f5d580f69b452436b7b3806acb636/USER'
    dictSamples['UL17_QCD_Pt-15to7000_Flat2018_pythia8'] = '/QCD_Pt-15to7000_TuneCP5_Flat2018_13TeV_pythia8/kadatta-boostedWtaggingSF_Skims_UL17_QCD_Pt-15to7000_Flat2018_pythia8_newSel_SF-300f5d580f69b452436b7b3806acb636/USER'
    
    dictSamples['UL17_WJetsToLNu-madgraphMLM-pythia8'] = '/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/kadatta-boostedWtaggingSF_Skims_UL17_WJetsToLNu-madgraphMLM-pythia8_newSel_SF-300f5d580f69b452436b7b3806acb636/USER'
    dictSamples['UL17_W1JetsToLNu-madgraphMLM-pythia8'] = '/W1JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/kadatta-boostedWtaggingSF_Skims_UL17_W1JetsToLNu-madgraphMLM-pythia8_newSel_SF-300f5d580f69b452436b7b3806acb636/USER'
    dictSamples['UL17_W2JetsToLNu-madgraphMLM-pythia8'] = '/W2JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/kadatta-boostedWtaggingSF_Skims_UL17_W2JetsToLNu-madgraphMLM-pythia8_newSel_SF-300f5d580f69b452436b7b3806acb636/USER'
    dictSamples['UL17_W3JetsToLNu-madgraphMLM-pythia8'] = '/W3JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/kadatta-boostedWtaggingSF_Skims_UL17_W3JetsToLNu-madgraphMLM-pythia8_newSel_SF-300f5d580f69b452436b7b3806acb636/USER'
    dictSamples['UL17_W4JetsToLNu-madgraphMLM-pythia8'] = '/W4JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/kadatta-boostedWtaggingSF_Skims_UL17_W4JetsToLNu-madgraphMLM-pythia8_newSel_SF-300f5d580f69b452436b7b3806acb636/USER'
    
    dictSamples['UL17_ST_s-channel-madgraph-pythia8'] = '/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8/kadatta-boostedWtaggingSF_Skims_UL17_ST_s-channel-amcatnlo-pythia8_newSel_SF-300f5d580f69b452436b7b3806acb636/USER'
    dictSamples['UL17_ST_t-channel-powheg-pythia8_antitop'] = '/ST_t-channel_antitop_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-boostedWtaggingSF_Skims_UL17_ST_t-channel-powheg-pythia8_antitop_newSel_SF-300f5d580f69b452436b7b3806acb636/USER'
    dictSamples['UL17_ST_t-channel-powheg-pythia8_top'] = '/ST_t-channel_top_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-boostedWtaggingSF_Skims_UL17_ST_t-channel-powheg-pythia8_top_newSel_SF-300f5d580f69b452436b7b3806acb636/USER'
    #dictSamples['UL17_ST_tW_antitop-powheg-pythia8'] = ['/ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v1/NANOAODSIM', 1 ]
    #dictSamples['UL17_ST_tW_top-powheg-pythia8'] = ['/ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v1/NANOAODSIM', 1 ]
    
    
    
    ### To choose dataset from dictSamples
    processingSamples = {}
    for sam in dictSamples:
        if 'all' in args.datasets:
            processingSamples[ sam ] = dictSamples[ sam ]
        elif sam.startswith( args.datasets ):
            processingSamples[ sam ] = dictSamples[ sam ]
    if len(processingSamples)==0: print 'No sample found. \n Have a nice day :)'

    print(processingSamples)
    for isample, jsample  in processingSamples.items():

        ### Create a list from the dataset
        if isinstance( jsample, list ):
            allfiles = []
            for jsam in jsample:
                fileDictList = ( dbsPhys03 if jsam.endswith('USER') else dbsGlobal).listFiles(dataset=jsam,validFileOnly=1)
                tmpfiles = [ "root://xrootd-cms.infn.it/"+dic['logical_file_name'] for dic in fileDictList ]
                #print tmpfiles
                allfiles = allfiles + tmpfiles
            #print allfiles
        else:
            fileDictList = ( dbsPhys03 if jsample.endswith('USER') else dbsGlobal).listFiles(dataset=jsample,validFileOnly=1)
            # DBS client returns a list of dictionaries, but we want a list of Logical File Names
            #allfiles = [ "root://cms-xrd-global.cern.ch/"+dic['logical_file_name'] for dic in fileDictList ]
            allfiles = [ "root://xrootd-cms.infn.it/"+dic['logical_file_name'] for dic in fileDictList ]
        print ("dataset %s has %d files" % (jsample, len(allfiles)))

        #for i in range (0, len(allfiles),20):
        #    print i
        #    computeGenWeights( allfiles[i:i+20], isample )
        computeGenWeights( allfiles, isample )
