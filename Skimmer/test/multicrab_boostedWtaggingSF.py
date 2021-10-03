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
            crabCommand('submit', config = config, 'dryrun')
        except HTTPException, hte:
            print 'Cannot execute command'
            print hte.headers


    requestname = 'boostedWtaggingSF_Skims_'+ job +options.year+'_'+options.version
    print requestname
    config.JobType.scriptExe = 'runPostProc'+options.datasets+options.year+'.sh'
    config.JobType.inputFiles = [ options.pythonFile ,'haddnano.py', 'keep_and_drop.txt',
'/uscms/home/camclean/nobackup/ZPlusJetsXS/QJM/CMSSW_9_4_4/src/data/EfficienciesAndSF_RunBtoF_Nov17Nov2017.root',
'/uscms/home/camclean/nobackup/ZPlusJetsXS/QJM/CMSSW_9_4_4/src/data/RunBCDEF_SF_ID.root',
'/uscms/home/camclean/nobackup/ZPlusJetsXS/QJM/CMSSW_9_4_4/src/data/RunBCDEF_SF_ISO.root',
]
    config.JobType.sendPythonFolder  = True
    
    if job.startswith(('18_Single','17_Single', 'SingleMuon','Single')):
        if options.year.startswith('2017'): config.Data.lumiMask = 'afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/Final/Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt'
        elif options.year.startswith('2018'): config.Data.lumiMask = ''
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
            dest="storageSite", default="T3_US_FNALLPC",
            help=("Storage Site"),
            )
    parser.add_option(
            "-v", "--version",
            dest="version", default="v00",
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
    parser.add_option(
        '--dryrun',
        dest='DRYRUN',
        action="store_true",
        default=False
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
        #createBash()

        print ("dataset %s has %d files" % (processingSamples[isam], len(processingSamples[isam][0])))
        submitJobs( isam, processingSamples[isam][0], processingSamples[isam][1] )

