#!/usr/bin/env python

import argparse
import os

#custom imports
import Dataset
import DASTools
#import Config as cf


def WriteJobConfigFile(filename, workdir, dataset, year, template, multiplicity, maxtime, localoutput, sepath, scratchpath="/scratch"): 
    name = "./etc/"+template+".conf"
    if not os.path.isfile(name): 
      print "ERROR: The template:", name, "does not exist. Please make sure you select or create one in ./etc/ . "
      return False

    with open(name, "r") as template: 
        configfile = open(filename, 'w')
        
        datasettext=""
        for line in dataset: 
        	datasettext+=("\t"+line+"\n")

        #if architecture in cf.config: 
        #  backend = cf.config[architecture]["backend"]
        #  queue = cf.config[architecture]["queue"]
        #else : 
        #  print "ERROR: The configuration \"", architecture, "\" is not known. Please add it to the file: Config.py. "
        #  return False

        filecontent = template.read()
        filecontent = filecontent.replace("$workdir$", workdir)
        filecontent = filecontent.replace("$maxtime$", str(maxtime))
        filecontent = filecontent.replace("$multiplicity$", str(multiplicity))
        filecontent = filecontent.replace("$dataset$", datasettext)
        filecontent = filecontent.replace("$year$", str(year))
        #filecontent = filecontent.replace("$queue$", queue)
        #filecontent = filecontent.replace("$scratchpath$", scratchpath)
        #filecontent = filecontent.replace("$sepath$", "srm://t3se01.psi.ch:8443/srm/managerv2?SFN=/pnfs/psi.ch/cms/trivcat/store/user/$USER/production/Wtagging")
        #filecontent = filecontent.replace("$backend$", backend)
        #filecontent = filecontent.replace("$localoutput$", localoutput)

        configfile.write(filecontent)
        configfile.close()

        return True
  	


if __name__ == "__main__":

   parser = argparse.ArgumentParser(description='GC: makeJobConfig') 

   parser.add_argument('descriptor', default = None, help="Which dataset to produce [mandatory]")
   parser.add_argument('-d','--dry', action = 'store_true', help = 'Run in dry mode (create but do not submit jobs)')
   parser.add_argument('-b','--batch', action = 'store_true', help = 'run in batch mode (no printout) ')
   parser.add_argument('-o', '--output', action = 'store', type=str, dest='outdir', default="catalogue", help = 'Where to store the config dataset files')
   parser.add_argument('-v', '--verbose', action='store_true', help = 'Give a lot of output (verbose)')
   parser.add_argument('-f', '--force', action='store_true', help="Force overwriting (the catalogue or job config file)")
   parser.add_argument('-m', '--multiplicity', action='store', type=int, default=10, help="Number of files per job") 
   #parser.add_argument('-g', '--backend', action='store', type=str, dest='backend', default="lxplus", help = "Which environment (job scheduler) from Config.py to use")
   parser.add_argument('-t', '--template', action='store', type=str, dest='template', default="t3psiSlurmMH", help = "Which Grid-Control template to start with (from etc/). ")
   parser.add_argument('-y', '--year', action='store', type=int, dest='year', help = "Which year the samples should be produced from.")

   args = parser.parse_args()  
 

   datasetfiles = []

   #args.descriptor = "TT" # choose in [TT, ST, VV, WJets, QCD, mc, data, all]

   datasetdir = args.outdir+"_dataset"
   configfile = args.outdir+".conf"
   workdir = args.outdir+"_GCwork"

   for dataset in Dataset.getDataset(args.descriptor): 
        datasetfiles.append(DASTools.GenerateGCDatasetFiles(dataset, datasetdir))

   # print datasetfiles

   os.system(". ./makeEnv.sh")	# Droping the environment variables into a file for GC 


   maxtime = args.multiplicity*4.

   if WriteJobConfigFile(configfile, workdir, datasetfiles, args.year, args.template, args.multiplicity, int(maxtime), "/work/mhuwiler/data/WScaleFactors/production", "srm://t3se01.psi.ch:8443/srm/managerv2?SFN=/pnfs/psi.ch/cms/trivcat/store/user/$USER/production/Wtagging", "/scratch"): 

    cmd = "go.py {} -cG".format(configfile)
    if not args.dry: os.system(cmd)

    print cmd





