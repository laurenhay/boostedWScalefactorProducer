#!/usr/bin/env python
"""
This is a small script that submits a config over many datasets
"""
import os
from optparse import OptionParser
from datasets import dictSamples, checkDict

def make_list(option, opt, value, parser):
    setattr(parser.values, option.dest, value.split(','))

def createBash():

    BASH_SCRIPT = '''
#this is not meant to be run locally
#
echo Check if TTY
if [ "`tty`" != "not a tty" ]; then
  echo "YOU SHOULD NOT RUN THIS IN INTERACTIVE, IT DELETES YOUR LOCAL FILES"
else
###ls -lR .
echo "ENV..................................."
env
echo "VOMS"
voms-proxy-info -all
echo "CMSSW BASE, python path, pwd"
echo $CMSSW_BASE
echo $PYTHON_PATH
echo $PWD
rm -rf $CMSSW_BASE/lib/
rm -rf $CMSSW_BASE/src/
rm -rf $CMSSW_BASE/module/
rm -rf $CMSSW_BASE/python/
mv lib $CMSSW_BASE/lib
mv src $CMSSW_BASE/src
mv python $CMSSW_BASE/python
echo Found Proxy in: $X509_USER_PROXY
echo "python {pythonFile} --sample {datasets} --year {year}"
python {pythonFile} --sample {datasets} --year {year} --runEra {runEra} 
fi
    '''
    open('runPostProc'+options.datasets+options.year+'.sh', 'w').write(BASH_SCRIPT.format(**options.__dict__))


def submitJobs( job, inputFiles, unitJobs ):

    from CRABAPI.RawCommand import crabCommand
    from WMCore.Configuration import Configuration
    config = Configuration()

    from httplib import HTTPException

    # We want to put all the CRAB project directories from the tasks we submit here into one common directory.                                                        =
    # That's why we need to set this parameter (here or above in the configuration file, it does not matter, we will not overwrite it).
    config.section_("General")
    config.General.workArea = options.dir
    #config.General.transferLogs = False
    #config.General.transferOutputs = True
    
    config.section_("JobType")
    config.JobType.pluginName = 'Analysis'
    config.JobType.psetName = 'PSet.py'
    config.JobType.maxMemoryMB = 2500
    config.JobType.allowUndistributedCMSSW = True

    config.section_("Data")
    #config.Data.publication = True
    #config.Data.publishDBS = 'phys03'
    config.Data.inputDBS = 'phys03'  
    #config.Data.ignoreLocality = True
    #config.Data.allowNonValidInputDataset = True

    config.section_("Site")
    config.Site.storageSite = options.storageSite
    #config.Site.whitelist = ['T1_US_FNAL','T2_CH_CSCS','T3_US_FNALLPC']
    #config.Site.blacklist = ['T2_US_Florida','T3_TW_*','T2_BR_*','T2_GR_Ioannina','T2_BR_SPRACE','T2_RU_IHEP','T2_PL_Swierk','T2_KR_KNU','T3_TW_NTU_HEP']

    def submit(config):
        try:
            crabCommand('submit', config = config)
        except HTTPException, hte:
            print 'Cannot execute command'
            print hte.headers


    requestname = 'boostedWtaggingSF_Skims_'+ job + '_UL' +options.year+'_'+options.version
    print requestname
    config.JobType.scriptExe = 'runPostProc'+options.datasets+options.year+'.sh'
    config.JobType.inputFiles = [ options.pythonFile ,'haddnano.py', 'keep_and_drop.txt']
    config.JobType.sendPythonFolder  = True
    
    if job.startswith(('UL18_Single','UL17_Single', 'SingleMuon','Single')):
        if options.year.startswith('2017'): config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/Legacy_2017/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt'
        elif options.year.startswith('2018'): config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/Legacy_2018/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt'
    else: 
        print "Cert not found for data sample"
    #config.Data.userInputFiles = inputFiles
    config.Data.inputDataset = inputFiles
    config.Data.splitting = 'FileBased'
    config.Data.unitsPerJob = unitJobs
    #config.Data.outputPrimaryDataset = job

    # since the input will have no metadata information, output can not be put in DBS
    config.JobType.outputFiles = [ 'boostedWtaggingSF_nanoskim.root']
    config.Data.outLFNDirBase = '/store/user/'+os.environ['USER']+'/boostedWtaggingSF/'

    if len(requestname) > 100: requestname = (requestname[:95-len(requestname)])
    print 'requestname = ', requestname
    config.General.requestName = requestname
    config.Data.outputDatasetTag = requestname
    print 'Submitting ' + config.General.requestName + ', dataset = ' + job
    print 'Configuration :'
    print config
    submit(config)
    #try : submit(config)
    #except : print 'Not submitted.'



if __name__ == '__main__':

    usage = ('usage: python multicrab_boostedWtaggingSF.py --datasets NAMEOFDATASET -d DIR -v VERSION')


    parser = OptionParser(usage=usage)
    parser.add_option(
            "-D", "--dir",
            dest="dir", default="crab_projects",
            help=("The crab directory you want to use "),
            )
    parser.add_option(
            "-d", "--datasets",
            dest="datasets", default='all',
            help=("File listing datasets to run over"),
            )
    parser.add_option(
            "-S", "--storageSite",
            dest="storageSite", default="T3_CH_PSI",
            help=("Storage Site"),
            )
    parser.add_option(
            "-v", "--version",
            dest="version", default="106X_v00",
            help=("Version of output"),
            )
    
    parser.add_option(
            "-p", "--pythonFile",
            dest="pythonFile", default="boostedWtaggingSF_skimNanoAOD.py",
            help=("python file to run"),
            )
    parser.add_option(
            "-y", "--year",
            dest="year", default="2017",
            help=("Version of output"),
            )
    parser.add_option(
            '--runEra',
            action="store",
            help="Run era for data",
            default="B"
    )

    (options, args) = parser.parse_args()
    
    processingSamples = {}
    for sam in dictSamples:
        if sam.startswith( options.datasets ) | options.datasets.startswith('all'):
            if 'SingleMuon' in sam or sam.startswith(('SingleMuon')):
                for iera in checkDict( sam, dictSamples )[options.year]['nanoAOD']:
                    processingSamples[ sam+'Run'+options.year+iera ] = [ checkDict( sam, dictSamples )[options.year]['nanoAOD'][iera], 1 ]
                    options.runEra = iera
                    print (iera,options.runEra)
            else:
                tmpList = checkDict( sam, dictSamples )[options.year]['nanoAOD']
                processingSamples[ sam ] = [ tmpList[0], 1 ]
                if len(tmpList)>1:
                    for iext in range(1,len(tmpList)):
                        processingSamples[ sam+'EXT'+str(iext) ] = [ tmpList[iext], 1 ]

    if len(processingSamples)==0: print 'No sample found. \n Have a nice day :)'

    for isam in processingSamples:

        if not processingSamples[isam][0]:
            print(' Sample ',isam,' does not have nanoAOD stored in datasets.py. Continuing with the next')
            continue
        #if isam.startswith('QCD') or isam.startswith('JetHT'): options.selection = 'dijet'
        #else: options.selection = 'Wtop'

        options.datasets = isam
        print('Creating bash file...')
        createBash()

        print ("dataset %s has %d files" % (processingSamples[isam], len(processingSamples[isam][0])))
        submitJobs( isam, processingSamples[isam][0], processingSamples[isam][1] )
    '''
    #dictSamples['UL17_TTJets_Summer19'] = [ '/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer19UL17NanoAODv2-106X_mc2017_realistic_v8-v1/NANOAODSIM',1]
    #dictSamples['UL17_TTJets_Summer20'] = [ '/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer20UL17NanoAODv2-106X_mc2017_realistic_v8-v1/NANOAODSIM',1]
    #dictSamples['UL17_TTToSemiLeptonic-powheg-pythia8'] = [ '/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v6-v2-8f037877c18053811b946b7194702f97/USER',1]
    #dictSamples['UL17_SingleMuon_D'] = ['/SingleMuon/Run2017D-UL2017_02Dec2019-v1/NANOAOD', 1 ]
    #dictSamples['UL17_SingleMuon_D'] = ['/SingleMuon/kadatta-Run2017D-09Aug2019_UL2017-v1_PFNanoAOD-711e27fd71aadb4a77ae7e6321a59353/USER',1]
    

    dictSamples = {}
    ######################################
    #2017 UL (PFNano MiniAODv2) samples
    ######################################

    dictSamples['UL17_SingleMuon_B'] = ['/SingleMuon/algomez-Run2017B-UL2017_MiniAODv2-v1_PFNanoAOD-aeb179a6519d272d4336b9926381baad/USER', 1 ]
    dictSamples['UL17_SingleMuon_C'] = ['/SingleMuon/kadatta-Run2017C-UL2017_MiniAODv2-v1_PFNano_V1-aeb179a6519d272d4336b9926381baad/USER', 1 ]
    dictSamples['UL17_SingleMuon_D'] = ['/SingleMuon/kadatta-Run2017D-UL2017_MiniAODv2-v1_PFNano_V1-aeb179a6519d272d4336b9926381baad/USER', 1]
    dictSamples['UL17_SingleMuon_E'] = ['/SingleMuon/kadatta-Run2017E-UL2017_MiniAODv2-v1_PFNano_V1-aeb179a6519d272d4336b9926381baad/USER', 1 ]
    dictSamples['UL17_SingleMuon_F'] = ['/SingleMuon/kadatta-Run2017F-UL2017_MiniAODv2-v1_PFNano_V1-aeb179a6519d272d4336b9926381baad/USER', 1 ]


    #dictSamples['UL17_TTbar_Pythia8'] = ['/TTbar_13TeV_TuneCP5_Pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER',1]
    dictSamples['UL17_TTJets'] = ['/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER',1]
    dictSamples['UL17_TTToSemileptonic'] = ['/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER',1]
    dictSamples['UL17_TTTo2L2Nu'] = ['/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER',1]

    dictSamples['UL17_ST_s-channel'] = ['/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER',1]
    dictSamples['UL17_ST_t-channel_antitop'] = ['/ST_t-channel_antitop_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER',1]
    dictSamples['UL17_ST_t-channel_top'] = ['/ST_t-channel_top_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER',1]
    dictSamples['UL17_ST_tW_antitop'] = ['/ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER',1]
    dictSamples['UL17_ST_tW_top'] = ['/ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER',1]

    dictSamples['UL17_WJetsToLNu'] = ['/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER',1] 

    dictSamples['UL17_WW'] = ['/WW_TuneCP5_13TeV-pythia8/kadatta-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER',1]
    dictSamples['UL17_ZZ'] = ['/ZZ_TuneCP5_13TeV-pythia8/kadatta-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER',1]
    dictSamples['UL17_WZ'] = ['/WZ_TuneCP5_13TeV-pythia8/kadatta-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER',1]

    dictSamples['UL17_QCD_Pt170to300'] = ['/QCD_Pt_170to300_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER',1]
    dictSamples['UL17_QCD_Pt300to470'] = ['/QCD_Pt_300to470_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER',1]
    dictSamples['UL17_QCD_Pt470to600'] = ['/QCD_Pt_470to600_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER',1]
    dictSamples['UL17_QCD_Pt600to800'] = ['/QCD_Pt_600to800_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER',1]
    dictSamples['UL17_QCD_Pt800to1000'] = ['/QCD_Pt_800to1000_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER',1]
    dictSamples['UL17_QCD_Pt1000to1400'] = ['/QCD_Pt_1000to1400_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER', 1 ]
    dictSamples['UL17_QCD_Pt1400to1800'] = ['/QCD_Pt_1400to1800_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER', 1 ]
    dictSamples['UL17_QCD_Pt1800to2400'] = ['/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER', 1 ]
    dictSamples['UL17_QCD_Pt2400to3200'] = ['/QCD_Pt_2400to3200_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER', 1 ]
    dictSamples['UL17_QCD_Pt3200toInf'] = ['/QCD_Pt_3200toInf_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER', 1 ]



    
    ######################################
    #2018 UL (PFNano MiniAODv2) samples
    ######################################

    dictSamples['UL18_SingleMuon_A'] = ['/SingleMuon/kadatta-Run2018A-UL2018_MiniAODv2-v1_PFNanoAOD-690f1d1c4f2456484a2616002f2d2b6d/USER', 1 ]
    dictSamples['UL18_SingleMuon_B'] = ['/SingleMuon/kadatta-Run2018B-UL2018_MiniAODv2-v1_PFNanoAOD-690f1d1c4f2456484a2616002f2d2b6d/USER', 1 ]
    dictSamples['UL18_SingleMuon_C'] = ['/SingleMuon/kadatta-Run2018C-UL2018_MiniAODv2-v1_PFNanoAOD-690f1d1c4f2456484a2616002f2d2b6d/USER', 1]
    dictSamples['UL18_SingleMuon_D'] = ['/SingleMuon/kadatta-Run2018D-UL2018_MiniAODv2-v1_PFNanoAOD-690f1d1c4f2456484a2616002f2d2b6d/USER', 1 ]

    #dictSamples['UL18_TTbar_Pythia8'] = ['/TTbar_13TeV_TuneCP5_Pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER',1]
    dictSamples['UL18_TTJets'] = ['/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER',1]
    dictSamples['UL18_TTToSemileptonic'] = ['/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER',1]
    dictSamples['UL18_TTTo2L2Nu'] = ['/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER',1]

    dictSamples['UL18_ST_s-channel'] = ['/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER',1]
    dictSamples['UL18_ST_t-channel_antitop'] = ['/ST_t-channel_antitop_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER',1]
    dictSamples['UL18_ST_t-channel_top'] = ['/ST_t-channel_top_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER',1]
    dictSamples['UL18_ST_tW_antitop'] = ['/ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER',1]
    dictSamples['UL18_ST_tW_top'] = ['/ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER',1]

    dictSamples['UL18_WJetsToLNu'] = ['/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER',1] 

    dictSamples['UL18_WW'] = ['/WW_TuneCP5_13TeV-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER',1]
    dictSamples['UL18_ZZ'] = ['/ZZ_TuneCP5_13TeV-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER',1]
    dictSamples['UL18_WZ'] = ['/WZ_TuneCP5_13TeV-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER',1]

    dictSamples['UL18_QCD_Pt170to300'] = ['/QCD_Pt_170to300_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-fff189d3e67d18da8f7301eb2c0e2940/USER',1]
    dictSamples['UL18_QCD_Pt300to470'] = ['/QCD_Pt_300to470_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-fff189d3e67d18da8f7301eb2c0e2940/USER',1]
    dictSamples['UL18_QCD_Pt470to600'] = ['/QCD_Pt_470to600_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-fff189d3e67d18da8f7301eb2c0e2940/USER',1]
    dictSamples['UL18_QCD_Pt600to800'] = ['/QCD_Pt_600to800_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-fff189d3e67d18da8f7301eb2c0e2940/USER',1]
    dictSamples['UL18_QCD_Pt800to1000'] = ['/QCD_Pt_800to1000_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-fff189d3e67d18da8f7301eb2c0e2940/USER',1]
    dictSamples['UL18_QCD_Pt1000to1400'] = ['/QCD_Pt_1000to1400_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-fff189d3e67d18da8f7301eb2c0e2940/USER', 1 ]
    dictSamples['UL18_QCD_Pt1400to1800'] = ['/QCD_Pt_1400to1800_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-fff189d3e67d18da8f7301eb2c0e2940/USER', 1 ]
    dictSamples['UL18_QCD_Pt1800to2400'] = ['/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-fff189d3e67d18da8f7301eb2c0e2940/USER', 1 ]
    dictSamples['UL18_QCD_Pt2400to3200'] = ['/QCD_Pt_2400to3200_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-fff189d3e67d18da8f7301eb2c0e2940/USER', 1 ]
    dictSamples['UL18_QCD_Pt3200toInf'] = ['/QCD_Pt_3200toInf_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-fff189d3e67d18da8f7301eb2c0e2940/USER', 1 ]



     
    ######## UL17 samples #######
    #dictSamples['UL17_W1JetsToLNu-madgraphMLM-pythia8'] = ['/W1JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v2/NANOAODSIM', 1 ]
    #dictSamples['UL17_W2JetsToLNu-madgraphMLM-pythia8'] = ['/W2JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v2/NANOAODSIM', 1 ]
    #dictSamples['UL17_W3JetsToLNu-madgraphMLM-pythia8'] = ['/W3JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v2/NANOAODSIM', 1 ]
    #dictSamples['UL17_W4JetsToLNu-madgraphMLM-pythia8'] = ['/W4JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v2/NANOAODSIM', 1 ]
    
    
    dictSamples['UL17_WZ-pythia8'] = ['/WZ_TuneCP5_13TeV-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['UL17_ZZ-pythia8'] = ['/ZZ_TuneCP5_13TeV-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['UL17_WW-pythia8'] = ['/WW_TuneCP5_13TeV-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    
    #dictSamples['UL17_TT_PFNano_Test2'] = [ '/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/algomez-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v6-v2-830c141d7b4aa70b88c71a25d598b0f2/USER', 1 ]

    dictSamples['UL17_WW-pythia8'] = ['/WW_TuneCP5_13TeV-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v6-v2-830c141d7b4aa70b88c71a25d598b0f2/USER',1]
    dictSamples['UL17_WZ-pythia8'] = ['/WZ_TuneCP5_13TeV-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v6-v2-830c141d7b4aa70b88c71a25d598b0f2/USER',1]
    dictSamples['UL17_ZZ-pythia8'] = ['/ZZ_TuneCP5_13TeV-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v6-v2-830c141d7b4aa70b88c71a25d598b0f2/USER',1]
    dictSamples['UL17_ST_s-channel-amcatnlo-pythia8'] = ['/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v1/NANOAODSIM', 1 ]
    
    dictSamples['UL17_SingleMuon_B'] = ['/SingleMuon/Run2017B-UL2017_02Dec2019-v1/NANOAOD', 1 ]
    dictSamples['UL17_SingleMuon_C'] = ['/SingleMuon/Run2017C-UL2017_02Dec2019-v1/NANOAOD', 1 ]
    dictSamples['UL17_SingleMuon_D'] = ['/SingleMuon/kadatta-Run2017D-09Aug2019_UL2017-v1_PFNanoAOD-711e27fd71aadb4a77ae7e6321a59353/USER',1]
    dictSamples['UL17_SingleMuon_E'] = ['/SingleMuon/Run2017E-UL2017_02Dec2019-v1/NANOAOD', 1 ]
    dictSamples['UL17_SingleMuon_F'] = ['/SingleMuon/Run2017F-UL2017_02Dec2019-v1/NANOAOD', 1 ]
    
    dictSamples['UL17_TTJets-amcatnloFXFX-pythia8'] = [ '/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v1/NANOAODSIM', 1 ]
    dictSamples['UL17_TTToSemiLeptonic-powheg-pythia8'] = [ '/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v2/NANOAODSIM', 1 ]
    dictSamples['UL17_TTTo2L2Nu-powheg-pythia8'] = [ '/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v2/NANOAODSIM', 1 ]
    
    dictSamples['UL17_QCD_Pt-170to300-pythia8'] = ['/QCD_Pt_170to300_TuneCP5_13TeV_pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v1/NANOAODSIM', 1 ]
    dictSamples['UL17_QCD_Pt-300to470-pythia8'] = ['/QCD_Pt_300to470_TuneCP5_13TeV_pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v1/NANOAODSIM', 1 ]
    dictSamples['UL17_QCD_Pt-470to600-pythia8'] = ['/QCD_Pt_470to600_TuneCP5_13TeV_pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v2/NANOAODSIM', 1 ]
    dictSamples['UL17_QCD_Pt-600to800-pythia8'] = ['/QCD_Pt_600to800_TuneCP5_13TeV_pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v2/NANOAODSIM', 1 ]
    dictSamples['UL17_QCD_Pt-800to1000-pythia8'] = ['/QCD_Pt_800to1000_TuneCP5_13TeV_pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v2/NANOAODSIM', 1 ]
    dictSamples['UL17_QCD_Pt-1000to1400-pythia8'] = ['/QCD_Pt_1000to1400_TuneCP5_13TeV_pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v2/NANOAODSIM', 1 ]
    dictSamples['UL17_QCD_Pt-1400to1800-pythia8'] = ['/QCD_Pt_1400to1800_TuneCP5_13TeV_pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v2/NANOAODSIM', 1 ]
    dictSamples['UL17_QCD_Pt-1800to2400-pythia8'] = ['/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v2/NANOAODSIM', 1 ]
    dictSamples['UL17_QCD_Pt-2400to3200-pythia8'] = ['/QCD_Pt_2400to3200_TuneCP5_13TeV_pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v2/NANOAODSIM', 1 ]
    dictSamples['UL17_QCD_Pt-3200toInf-pythia8'] = ['/QCD_Pt_3200toInf_TuneCP5_13TeV_pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v2/NANOAODSIM', 1 ]
    dictSamples['UL17_QCD_Pt-15to7000_Flat_herwig7'] = ['/QCD_Pt-15to7000_TuneCH3_Flat_13TeV_herwig7/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v1/NANOAODSIM', 1 ]
    dictSamples['UL17_QCD_Pt-15to7000_Flat2018_pythia8'] = ['/QCD_Pt-15to7000_TuneCP5_Flat2018_13TeV_pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v2/NANOAODSIM', 1 ]

    dictSamples['UL17_WJetsToLNu-madgraphMLM-pythia8'] = ['/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v2/NANOAODSIM', 1 ]
    
    dictSamples['UL17_ST_t-channel-powheg-pythia8_antitop'] = ['/ST_t-channel_antitop_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v1/NANOAODSIM', 1 ]
    dictSamples['UL17_ST_t-channel-powheg-pythia8_top'] = ['/ST_t-channel_top_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v1/NANOAODSIM', 1 ]
    dictSamples['UL17_ST_tW_top-powheg-pythia8'] = ['/ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v1/NANOAODSIM', 1 ]
    dictSamples['UL17_ST_tW_antitop-powheg-pythia8'] = ['/ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v1/NANOAODSIM', 1 ]
       
    
    
    
    processingSamples = {}
    if 'all' in options.datasets:
        for sam in dictSamples: processingSamples[ sam ] = dictSamples[ sam ]
    else:
        for sam in dictSamples:
            if sam.startswith( options.datasets ): processingSamples[ sam ] = dictSamples[ sam ]
            if sam.startswith('UL%s_SingleMuon_'%options.year[-2:]):
                iera = sam[-1:]
                options.runEra = iera
                print (iera)
    if len(processingSamples)==0: print 'No sample found. \n Have a nice day :)'

    for isam in processingSamples:

        options.datasets = isam
        print('Creating bash file...')
        createBash()

        print ("dataset %s has %d files" % (processingSamples[isam], len(processingSamples[isam][0])))
        submitJobs( isam, processingSamples[isam][0], processingSamples[isam][1] )
    '''
