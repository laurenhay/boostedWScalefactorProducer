#!/usr/bin/env python
"""
This is a small script that submits a config over many datasets
"""
import os
from optparse import OptionParser

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
echo "python {pythonFile} --sample {datasets} "
python {pythonFile} --sample {datasets} 
fi
    '''
    open('runPostProc'+options.datasets+'.sh', 'w').write(BASH_SCRIPT.format(**options.__dict__))


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
    config.JobType.maxMemoryMB = 3000
    config.JobType.allowUndistributedCMSSW = True

    config.section_("Data")
    #config.Data.publication = True
    #config.Data.publishDBS = 'phys03'
    config.Data.inputDBS = 'global'
    #config.Data.ignoreLocality = True
    config.Data.allowNonValidInputDataset = True

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


    requestname = 'boostedWtaggingSF_Skims_'+ job + '_' +options.version
    print requestname
    config.JobType.scriptExe = 'runPostProc'+options.datasets+'.sh'
    config.JobType.inputFiles = [ options.pythonFile ,'haddnano.py', 'keep_and_drop.txt']
    config.JobType.sendPythonFolder  = True
    if job.startswith(('Single', 'EGamma')): 
	if '2016' in job: config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Final/Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON.txt'
	if '2017' in job: config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/Legacy_2017/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt'
	if '2018' in job: config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/PromptReco/Cert_314472-315801_13TeV_PromptReco_Collisions18_JSON.txt'

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

    (options, args) = parser.parse_args()


    dictSamples = {}
    
    
    
    
    ''' 
    ######## UL17 samples #######
    
    dictSamples['UL17_SingleMuon_B'] = ['/SingleMuon/Run2017B-UL2017_02Dec2019-v1/NANOAOD', 1 ]
    dictSamples['UL17_SingleMuon_C'] = ['/SingleMuon/Run2017C-UL2017_02Dec2019-v1/NANOAOD', 1 ]
    dictSamples['UL17_SingleMuon_D'] = ['/SingleMuon/Run2017D-UL2017_02Dec2019-v1/NANOAOD', 1 ]
    dictSamples['UL17_SingleMuon_E'] = ['/SingleMuon/Run2017E-UL2017_02Dec2019-v1/NANOAOD', 1 ]
    dictSamples['UL17_SingleMuon_F'] = ['/SingleMuon/Run2017F-UL2017_02Dec2019-v1/NANOAOD', 1 ]
    
    #dictSamples['UL17_TT_PFNano_Test'] = [ '/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v6-v2-830c141d7b4aa70b88c71a25d598b0f2/USER', 1 ]
    dictSamples['UL17_TTToSemiLeptonic-powheg-pythia8'] = [ '/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v2/NANOAODSIM', 1 ]
    dictSamples['UL17_TTJets-amcatnloFXFX-pythia8'] = [ '/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v1/NANOAODSIM', 1 ]
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
        dictSamples['UL17_W1JetsToLNu-madgraphMLM-pythia8'] = ['/W1JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v2/NANOAODSIM', 1 ]
    dictSamples['UL17_W2JetsToLNu-madgraphMLM-pythia8'] = ['/W2JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v2/NANOAODSIM', 1 ]
    dictSamples['UL17_W3JetsToLNu-madgraphMLM-pythia8'] = ['/W3JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v2/NANOAODSIM', 1 ]
    dictSamples['UL17_W4JetsToLNu-madgraphMLM-pythia8'] = ['/W4JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v2/NANOAODSIM', 1 ]
    
    dictSamples['UL17_ST_s-channel-madgraph-pythia8'] = ['/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21_ext1-v1/NANOAODSIM', 1 ]
    dictSamples['UL17_ST_t-channel-powheg-pythia8_antitop'] = ['/ST_t-channel_antitop_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v1/NANOAODSIM', 1 ]
    dictSamples['UL17_ST_t-channel-powheg-pythia8_top'] = ['/ST_t-channel_top_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v1/NANOAODSIM', 1 ]
    dictSamples['UL17_ST_tW_antitop-powheg-pythia8'] = ['/ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v1/NANOAODSIM', 1 ]
    dictSamples['UL17_ST_tW_top-powheg-pythia8'] = ['/ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL17NanoAOD-106X_mc2017_realistic_v6-v1/NANOAODSIM', 1 ]
    
    #dictSamples['UL17_WZ-pythia8'] = ['/WZ_TuneCP5_13TeV-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    #dictSamples['UL17_ZZ-pythia8'] = ['/ZZ_TuneCP5_13TeV-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    #dictSamples['UL17_WW-pythia8'] = ['/WW_TuneCP5_13TeV-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
   
    
    '''
    
    '''
    ###### 2018 re-reco samples ######
    dictSamples['SingleMuon2018RR_A'] = ['/SingleMuon/Run2018A-02Apr2020-v1/NANOAOD', 1 ]
    dictSamples['SingleMuon2018RR_B'] = ['/SingleMuon/Run2018B-02Apr2020-v1/NANOAOD', 1 ]
    dictSamples['SingleMuon2018RR_C'] = ['/SingleMuon/Run2018C-02Apr2020-v1/NANOAOD', 1 ]
    dictSamples['SingleMuon2018RR_D'] = ['/SingleMuon/Run2018D-02Apr2020-v1/NANOAOD', 1 ]

    dictSamples['TTToSemiLeptonic-powheg-pythia8_2018'] = [ '/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    
    dictSamples['TTTo2L2Nu-powheg-pythia8_2018'] = [ '/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['TT-powheg-herwig7_2018'] = [ '/TT_TuneCH3_13TeV-powheg-herwig7/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['TTJets-amcatnloFXFX-pythia8_2018'] = [ '/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21_ext1-v1/NANOAODSIM', 1 ]

    
    dictSamples['ST_s-channel-madgraph-pythia8_2018'] = ['/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21_ext1-v1/NANOAODSIM', 1 ]
    dictSamples['ST_t-channel-powheg-madspin-pythia8_antitop_2018'] = ['/ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['ST_t-channel-powheg-madspin-pythia8_top_2018'] = ['/ST_t-channel_top_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['ST_tW_antitop-powheg-pythia8_2018'] = ['/ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21_ext1-v1/NANOAODSIM', 1 ]
    dictSamples['ST_tW_top-powheg-pythia8_2018'] = ['/ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21_ext1-v1/NANOAODSIM', 1 ]

    dictSamples['WJetsToLNu-madgraphMLM-pythia8_inclusive_2018'] = ['/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['WJetsToLNu_HT70-madgraphMLM-pythia8_inclusive_2018'] = [ '/WJetsToLNu_HT-70To100_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['WJetsToLNu_HT100-madgraphMLM-pythia8_inclusive_2018'] = [ '/WJetsToLNu_HT-100To200_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['WJetsToLNu_HT200-madgraphMLM-pythia8_inclusive_2018'] = [ '/WJetsToLNu_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['WJetsToLNu_HT400-madgraphMLM-pythia8_inclusive_2018'] = [ '/WJetsToLNu_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['WJetsToLNu_HT600-madgraphMLM-pythia8_inclusive_2018'] = [ '/WJetsToLNu_HT-600To800_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['WJetsToLNu_HT800-madgraphMLM-pythia8_inclusive_2018'] = [ '/WJetsToLNu_HT-800To1200_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['WJetsToLNu_HT1200-madgraphMLM-pythia8_inclusive_2018'] = [ '/WJetsToLNu_HT-1200To2500_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['WJetsToLNu_HT2500-madgraphMLM-pythia8_inclusive_2018'] = [ '/WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]

    dictSamples['WZ-pythia8_2018'] = ['/WZ_TuneCP5_13TeV-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['ZZ-pythia8_2018'] = ['/ZZ_TuneCP5_13TeV-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['WW-pythia8_2018'] = ['/WW_TuneCP5_13TeV-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]

    dictSamples['QCD_HT100-madgraphMLM-pythia8_2018'] = ['/QCD_HT100to200_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['QCD_HT200-madgraphMLM-pythia8_2018'] = ['/QCD_HT200to300_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['QCD_HT300-madgraphMLM-pythia8_2018'] = ['/QCD_HT300to500_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['QCD_HT500-madgraphMLM-pythia8_2018'] = ['/QCD_HT500to700_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['QCD_HT700-madgraphMLM-pythia8_2018'] = ['/QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['QCD_HT1000-madgraphMLM-pythia8_2018'] = ['/QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['QCD_HT1500-madgraphMLM-pythia8_2018'] = ['/QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]
    dictSamples['QCD_HT2000-madgraphMLM-pythia8_2018'] = ['/QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM', 1 ]

    '''
    processingSamples = {}
    if 'all' in options.datasets:
        for sam in dictSamples: processingSamples[ sam ] = dictSamples[ sam ]
    else:
        for sam in dictSamples:
            if sam.startswith( options.datasets ): processingSamples[ sam ] = dictSamples[ sam ]

    if len(processingSamples)==0: print 'No sample found. \n Have a nice day :)'

    for isam in processingSamples:

        options.datasets = isam
        print('Creating bash file...')
        createBash()

        print ("dataset %s has %d files" % (processingSamples[isam], len(processingSamples[isam][0])))
        submitJobs( isam, processingSamples[isam][0], processingSamples[isam][1] )
