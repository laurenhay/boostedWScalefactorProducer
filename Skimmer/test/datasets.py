#!/usr/bin/env python
### For xsec calculation: grep miniAOD datasets.py | awk '{ print $4 }' | sed "s/'//g" | sed  's/"//g' | sed 's/\,//g' > calculateXSectionAndFilterEfficiency/datasets.txt
import ROOT

dictSamples = {
        
    ####### Wtop (xsecs not available on xsdb and/or not matching between xsdb and xsec calculation script are cross-checked with an approved analysis a la CMS AN-2018/129 )
    'SingleMuon' : {
        
        '2017' :  {
            'miniAOD' : {
                'B' : '/SingleMuon/Run2017B-UL2017_MiniAODv2-v1/MINIAOD',
                'C' : '/SingleMuon/Run2017C-UL2017_MiniAODv2-v1/MINIAOD',
                'D' : '/SingleMuon/Run2017D-UL2017_MiniAODv2-v1/MINIAOD',
                'E' : '/SingleMuon/Run2017E-UL2017_MiniAODv2-v1/MINIAOD',
                'F' : '/SingleMuon/Run2017F-UL2017_MiniAODv2-v1/MINIAOD',
                },
            'nanoAOD' : {
                'B': '/SingleMuon/kadatta-Run2017B-UL2017_MiniAODv2-v1_PFNano_V2-aeb179a6519d272d4336b9926381baad/USER',
                'C': '/SingleMuon/kadatta-Run2017C-UL2017_MiniAODv2-v1_PFNanoAOD-aeb179a6519d272d4336b9926381baad/USER',
                'D': '/SingleMuon/kadatta-Run2017D-UL2017_MiniAODv2-v1_PFNanoAOD-aeb179a6519d272d4336b9926381baad/USER',
                'E': '/SingleMuon/kadatta-Run2017E-UL2017_MiniAODv2-v1_PFNanoAOD-aeb179a6519d272d4336b9926381baad/USER',
                'F': '/SingleMuon/kadatta-Run2017F-UL2017_MiniAODv2-v1_PFNanoAOD-aeb179a6519d272d4336b9926381baad/USER',
                },
            'skimmerHisto' : 'SingleMuonAll_2017UL.root',
            'lumi' : 41472.052,
            },
        '2018' :  {
            'miniAOD' : {
                'A' : '/SingleMuon/Run2018A-UL2018_MiniAODv2-v1/MINIAOD',
                'B' : '/SingleMuon/Run2018B-UL2018_MiniAODv2-v1/MINIAOD',
                'C' : '/SingleMuon/Run2018C-UL2018_MiniAODv2-v1/MINIAOD',
                'D' : '/SingleMuon/Run2018D-UL2018_MiniAODv2-v1/MINIAOD',
                },
            'nanoAOD' : {
                'A' : '/SingleMuon/kadatta-Run2018A-UL2018_MiniAODv2-v1_PFNanoV2-7c69df739076f6ca6fc3c530fd236448/USER',
                'B' : '/SingleMuon/kadatta-Run2018B-UL2018_MiniAODv2-v1_PFNanoV2-7c69df739076f6ca6fc3c530fd236448/USER',
                'C' : '/SingleMuon/kadatta-Run2018C-UL2018_MiniAODv2-v1_PFNanoAOD-690f1d1c4f2456484a2616002f2d2b6d/USER',
                'D' : '/SingleMuon/kadatta-Run2018D-UL2018_MiniAODv2-v1_PFNanoV2-7c69df739076f6ca6fc3c530fd236448/USER',
                },
            'skimmerHisto' : 'SingleMuonAll_2018UL.root',
            'lumi' : 59816.0,
            },
        'color': ROOT.kWhite,
        'selection' : 'Wtop'
    },

    'TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8' : {
        '2017' :  {
            'miniAOD' : [ '/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer19UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : 'TTJets_amcatnloFXFX-pythia8_2017UL.root',
            'nevents' : 1.,
            'nGenWeights' : 286629789811.7677,
            },
        '2018' :  {
            'miniAOD' : [ '/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer19UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmer' : [ '/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmerHisto' : 'TTJets_amcatnloFXFX-pythia8_2018UL.root',
            'nevents' : 1.,
            'nGenWeights' : 297902725633.38257,
            },
        'XS' : 7.591e+02, #some notes say 722.8 and a few say 831.76?
        'selection' : 'Wtop',
        'label' : 't#bar{t} amcatnloFXFX' ,
        'color': ROOT.kBlue
    },

    'TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8' : {
        '2017' :  {
            'miniAOD' : [ '/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : 'TTToSemileptonic_powheg_pythia8_2017UL.root',
            'nevents' : 1.,
            'nGenWeights' : 32392787477.907993,
            },
        '2018' :  {
            'miniAOD' : [ '/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmer' : [ '/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmerHisto' : 'TTToSemileptonic_powheg_pythia8_2018UL.root',
            'nevents' : 1.,
            'nGenWeights' : 31378075292.893986,
            },
        'XS' : 365.34,
        'selection' : 'Wtop',
        'label' : 't#bar{t} powheg' ,
        'color': ROOT.kMagenta
    },

    'TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8' : {
        '2017' :  {
            'miniAOD' : [ '/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : 'TTTo2L2Nu_powheg_pythia8_2017UL.root',
            'nevents' : 1.,
            'nGenWeights' :  4759777104.469413,
            },
        '2018' :  {
            'miniAOD' : [ '/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmer' : [ '/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmerHisto' : 'TTTo2L2Nu_powheg_pythia8_2018UL.root',
            'nevents' : 1.,
            'nGenWeights' : 5063754431.9676,
            },
        'selection' : 'Wtop',
        'XS' : 88.29,
        'label' : 't#bar{t} DL' ,
        'color': ROOT.kCyan+1
    },

    'WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8' : {
        '2017' :  {
            'miniAOD' : [ '/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer19UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : 'WJetsToLNu_madgraphMLM_pythia8_2017UL.root',
            'nevents' : 1.,
            'nGenWeights' : 9949891586212.455078,
            },
        '2018' :  {
            'miniAOD' : [ '/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer19UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmer' : [ '/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmerHisto' : 'WJetsToLNu_madgraphMLM_pythia8_2018UL.root',
            'nevents' : 1.,
            'nGenWeights' : 10484986870276.357422,
            },
        'selection' : 'Wtop',
        'XS' : 5.368e+04,
        'label' : 'WJets' ,
        'color': ROOT.kOrange-2
    },
    'ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8' : {
        '2017' :  {
            'miniAOD' : [ '/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8/RunIISummer19UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : 'ST_s-channel_amcatnlo_pythia8_2017UL.root',
            'nevents' : 1.,
            'nGenWeights' : 70439807.475972,
            },
        '2018' :  {
            'miniAOD' : [ '/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8/RunIISummer19UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmer' : [ '/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmerHisto' : 'ST_s-channel_amcatnlo_pythia8_2018UL.root',
            'nevents' : 1.,
            'nGenWeights' : 64014403.924644,
            },
        'selection' : 'Wtop',
        'XS' : 3.549e+00,
        'label' : 'Single top' ,
        'color': ROOT.kGreen+2,
    },
    'ST_t-channel_top_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8' : {
        '2017' :  {
            'miniAOD' : [ '/ST_t-channel_top_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/ST_t-channel_top_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/ST_t-channel_top_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : 'ST_t-channel_top_powheg_pythia8_2017UL.root',
            'nevents' : 1.,
            'nGenWeights' : 656310119.274000,
            },
        '2018' :  {
            'miniAOD' : [ '/ST_t-channel_top_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/ST_t-channel_top_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmer' : [ '/ST_t-channel_top_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmerHisto' : 'ST_t-channel_top_powheg_pythia8_2018UL.root',
            'nevents' : 1.,
            'nGenWeights' : 683747124.990000,
            },
        'selection' : 'Wtop',
        'XS' : 1.197e+02,
        'label' : 'Single top' ,
        'color': ROOT.kGreen+2,
    },
    'ST_t-channel_antitop_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8' : {
        '2017' :  {
            'miniAOD' : [ '/ST_t-channel_antitop_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/ST_t-channel_antitop_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/ST_t-channel_antitop_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : 'ST_t-channel_antitop_powheg_pythia8_2017UL.root',
            'nevents' : 1.,
            'nGenWeights' : 303960792.435600,
            },
        '2018' :  {
            'miniAOD' : [ '/ST_t-channel_antitop_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/ST_t-channel_antitop_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmer' : [ '/ST_t-channel_antitop_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmerHisto' : 'ST_t-channel_antitop_powheg_pythia8_2018UL.root',
            'nevents' : 1.,
            'nGenWeights' : 271219283.652000,
            },
        'selection' : 'Wtop',
        'XS' : 7.174e+01,
        'label' : 'Single top' ,
        'color': ROOT.kGreen+2,
    },
    'ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8' : {
        '2017' :  {
            'miniAOD' : [ '/ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : 'ST_tW_top_powheg_pythia8_2017UL.root',
            'nevents' : 1.,
            'nGenWeights' : 331239851.967700,
            },
        '2018' :  {
            'miniAOD' : [ '/ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmer' : [ '/ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmerHisto' : 'ST_tW_top_powheg_pythia8_2018UL.root',
            'nevents' : 1.,
            'nGenWeights' : 328321574.253000,
            },
        'selection' : 'Wtop',
        'XS' : 3.245e+01,
        'label' : 'Single top' ,
        'color': ROOT.kGreen+2,
    },
    'ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8' : {
        '2017' :  {
            'miniAOD' : [ '/ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : 'ST_tW_antitop_powheg_pythia8_2017UL.root',
            'nevents' : 1.,
            'nGenWeights' : 303960792.435600,
            },
        '2018' :  {
            'miniAOD' : [ '/ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/RunIISummer19UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmer' : [ '/ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmerHisto' : 'ST_tW_antitop_powheg_pythia8_2018UL.root',
            'nevents' : 1.,
            'nGenWeights' : 296655487.557600,
            },
        'selection' : 'Wtop',
        'XS' : 3.251e+01,
        'label' : 'Single top' ,
        'color': ROOT.kGreen+2,
    },
    'WW_TuneCP5_13TeV-pythia8' : {
        '2017' :  {
            'miniAOD' : [ '/WW_TuneCP5_13TeV-pythia8/RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/WW_TuneCP5_13TeV-pythia8/kadatta-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/WW_TuneCP5_13TeV-pythia8/kadatta-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : 'WW_pythia8_2017UL.root',
            'nevents' : 1.,
            'nGenWeights' : 15634116.199514,
            },
        '2018' :  {
            'miniAOD' : [ '/WW_TuneCP5_13TeV-pythia8/RunIISummer19UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/WW_TuneCP5_13TeV-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmer' : [ '/WW_TuneCP5_13TeV-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmerHisto' : 'WW_pythia8_2018UL.root',
            'nevents' : 1.,
            'nGenWeights' : 7959266.140092,
            },
        'XS' : 7.576e+01,
        'selection' : 'Wtop',
        'label' : 'Diboson' ,
        'color': ROOT.kPink-1
    },
    'ZZ_TuneCP5_13TeV-pythia8' : {
        '2017' :  {
            'miniAOD' : [ '/ZZ_TuneCP5_13TeV-pythia8/RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/ZZ_TuneCP5_13TeV-pythia8/kadatta-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/ZZ_TuneCP5_13TeV-pythia8/kadatta-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : 'ZZ_pythia8_2017UL.root',
            'nevents' : 1.,
            'nGenWeights' : 2706000.000000,
            },
        '2018' :  {
            'miniAOD' : [ '/ZZ_TuneCP5_13TeV-pythia8/RunIISummer19UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/ZZ_TuneCP5_13TeV-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmer' : [ '/ZZ_TuneCP5_13TeV-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmerHisto' : 'ZZ_pythia8_2018UL.root',
            'nevents' : 1.,
            'nGenWeights' : 2000000.000000,
            },
        #'XS' : 1.210e+01,#from xsec py script, from papers/xsdb->2.748e+00,
        'selection' : 'Wtop',
        'XS' : 2.748e+00,
        'label' : 'Diboson' ,
        'color': ROOT.kPink-1
    },
    'WZ_TuneCP5_13TeV-pythia8' : {
        '2017' :  {
            'miniAOD' : [ '/WZ_TuneCP5_13TeV-pythia8/RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/WZ_TuneCP5_13TeV-pythia8/kadatta-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/WZ_TuneCP5_13TeV-pythia8/kadatta-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : 'WZ_pythia8_2017UL.root',
            'nevents' : 1.,
            'nGenWeights' : 7889000.000000,
            },
        '2018' :  {
            'miniAOD' : [ '/WZ_TuneCP5_13TeV-pythia8/RunIISummer19UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/WZ_TuneCP5_13TeV-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmer' : [ '/WZ_TuneCP5_13TeV-pythia8/kadatta-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-754f8ab81f6f0298c5fa7c45094d30e4/USER' ],
            'skimmerHisto' : 'WZ_pythia8_2018UL.root',
            'nevents' : 1.,
            'nGenWeights' : 3976000.000000,
            },
        'XS' : 2.751e+01, #from xsec calc, and from papers->1.21e+00,
        'selection' : 'Wtop',
        #'XS' : 1.21e+00,
        'label' : 'Dibosons' ,
        'color': ROOT.kPink-1
    },
    
        'QCD_Pt-150to3000_TuneCH3_FlatPower7_13TeV-herwig7' : {
        '2017' :  {
            'miniAOD' : [ '/QCD_Pt-150to3000_TuneCH3_FlatPower7_13TeV-herwig7/RunIISummer19UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/QCD_Pt-150to3000_TuneCH3_FlatPower7_13TeV-herwig7/algomez-RunIISummer19UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/QCD_Pt-150to3000_TuneCH3_FlatPower7_13TeV-herwig7/algomez-RunIISummer19UL17PFNanoAOD_jetObservables_Skimmer_v04p3-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : 'jetObservables_histograms_QCDPt150to3000_herwig_UL2017.root',
            'nevents' : 19880000.,
            'nGenWeights' :397097.833,
            },
        '2018' :  {
            'miniAOD' : [ '/QCD_Pt-150to3000_TuneCH3_FlatPower7_13TeV-herwig7/RunIISummer19UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/QCD_Pt-150to3000_TuneCH3_FlatPower7_13TeV-herwig7/algomez-RunIISummer19UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-fff189d3e67d18da8f7301eb2c0e2940/USER' ],
            'skimmer' : [ '/QCD_Pt-150to3000_TuneCH3_FlatPower7_13TeV-herwig7/algomez-RunIISummer19UL18PFNanoAOD_jetObservables_Skimmer_v04p3-fff189d3e67d18da8f7301eb2c0e2940/USER' ],
            'skimmerHisto' : 'jetObservables_histograms_QCDPt150to3000_herwig_UL2018.root',
            'nevents' : 6649600.,
            'nGenWeights' : 28765.923,
            },
        'selection' : 'dijet',
        'XS' : 8.637e+03, ## for 2018 1.086e+04
        'label' : 'QCD Herwig7',
        'color': ROOT.kPink
    },

    'QCD_Pt_170to300_TuneCP5_13TeV_pythia8' : {
        '2017' :  {
            'miniAOD' : [ '/QCD_Pt_170to300_TuneCP5_13TeV_pythia8/RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/QCD_Pt_170to300_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/QCD_Pt_170to300_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD_jetObservables_Skimmer_v04p3-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : 'jetObservables_histograms_QCDPt170to300_UL2017.root',
            'nevents' : 27963000.0,
            'nGenWeights' : 27963000.0,
            },
        '2018' :  {
            'miniAOD' : [ '/QCD_Pt_170to300_TuneCP5_13TeV_pythia8/RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/QCD_Pt_170to300_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-fff189d3e67d18da8f7301eb2c0e2940/USER' ],
            'skimmer' : [ '/QCD_Pt_170to300_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD_jetObservables_Skimmer_v04p3-fff189d3e67d18da8f7301eb2c0e2940/USER' ],
            'skimmerHisto' : 'jetObservables_histograms_QCDPt170to300_UL2018.root',
            'nevents' : 28425000.0,
            'nGenWeights' : 28425000.0,
            },
        'selection' : 'dijet',
        'XS' : 1.035e+05,
        'label' : 'QCD Pythia8',
        'color': ROOT.kBlue
    },

    'QCD_Pt_300to470_TuneCP5_13TeV_pythia8' : {
        '2017' :  {
            'miniAOD' : [ '/QCD_Pt_300to470_TuneCP5_13TeV_pythia8/RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/QCD_Pt_300to470_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/QCD_Pt_300to470_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD_jetObservables_Skimmer_v04p3-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : 'jetObservables_histograms_QCDPt300to470_UL2017.root',
            'nevents' : 53017000.,
            'nGenWeights' : 53017008.47,
            },
        '2018' :  {
            'miniAOD' : [ '/QCD_Pt_300to470_TuneCP5_13TeV_pythia8/RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/QCD_Pt_300to470_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-fff189d3e67d18da8f7301eb2c0e2940/USER' ],
            'skimmer' : [ '/QCD_Pt_300to470_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD_jetObservables_Skimmer_v04p3-fff189d3e67d18da8f7301eb2c0e2940/USER' ],
            'skimmerHisto' : 'jetObservables_histograms_QCDPt300to470_UL2018.root',
            'nevents' : 55315000.,
            'nGenWeights' : 55315008.680,
            },
        'selection' : 'dijet',
        'XS' : 6.760e+03,
        'label' : 'QCD Pythia8',
        'color': ROOT.kBlue
    },

    'QCD_Pt_470to600_TuneCP5_13TeV_pythia8' : {
        '2017' :  {
            'miniAOD' : [ '/QCD_Pt_470to600_TuneCP5_13TeV_pythia8/RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/QCD_Pt_470to600_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/QCD_Pt_470to600_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD_jetObservables_Skimmer_v04p3-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : 'jetObservables_histograms_QCDPt470to600_UL2017.root',
            'nevents' : 46970000.,
            'nGenWeights' : 46970154.474,
            },
        '2018' :  {
            'miniAOD' : [ '/QCD_Pt_470to600_TuneCP5_13TeV_pythia8/RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/QCD_Pt_470to600_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-fff189d3e67d18da8f7301eb2c0e2940/USER' ],
            'skimmer' : [ '/QCD_Pt_470to600_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD_jetObservables_Skimmer_v04p3-fff189d3e67d18da8f7301eb2c0e2940/USER' ],
            'skimmerHisto' : 'jetObservables_histograms_QCDPt470to600_UL2018.root',
            'nevents' : 51191000.,
            'nGenWeights' : 51191166.543,
            },
        'selection' : 'dijet',
        'XS' : 5.516e+02,
        'label' : 'QCD Pythia8',
        'color': ROOT.kBlue
    },

    'QCD_Pt_600to800_TuneCP5_13TeV_pythia8' : {
        '2017' :  {
            'miniAOD' : [ '/QCD_Pt_600to800_TuneCP5_13TeV_pythia8/RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/QCD_Pt_600to800_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/QCD_Pt_600to800_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD_jetObservables_Skimmer_v04p3-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : 'jetObservables_histograms_QCDPt600to800_UL2017.root',
            'nevents' : 63458000.,
            'nGenWeights' : 63458001.544,
            },
        '2018' :  {
            'miniAOD' : [ '/QCD_Pt_600to800_TuneCP5_13TeV_pythia8/RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/QCD_Pt_600to800_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-fff189d3e67d18da8f7301eb2c0e2940/USER' ],
            'skimmer' : [ '/QCD_Pt_600to800_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD_jetObservables_Skimmer_v04p3-fff189d3e67d18da8f7301eb2c0e2940/USER' ],
            'skimmerHisto' :  'jetObservables_histograms_QCDPt600to800_UL2018.root',
            'nevents' : 65300000.,
            'nGenWeights' : 65300001.492,
            },
        'selection' : 'dijet',
        'XS' : 1.564e+02,
        'label' : 'QCD Pythia8',
        'color': ROOT.kBlue
    },

    'QCD_Pt_800to1000_TuneCP5_13TeV_pythia8' : {
        '2017' :  {
            'miniAOD' : [ '/QCD_Pt_800to1000_TuneCP5_13TeV_pythia8/RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/QCD_Pt_800to1000_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/QCD_Pt_800to1000_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD_jetObservables_Skimmer_v04p3-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : 'jetObservables_histograms_QCDPt800to1000_UL2017.root',
            'nevents' : 35696000.0,
            'nGenWeights' : 35696000.0,
            },
        '2018' :  {
            'miniAOD' : [ '/QCD_Pt_800to1000_TuneCP5_13TeV_pythia8/RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/QCD_Pt_800to1000_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-fff189d3e67d18da8f7301eb2c0e2940/USER' ],
            'skimmer' : [ '/QCD_Pt_800to1000_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD_jetObservables_Skimmer_v04p3-fff189d3e67d18da8f7301eb2c0e2940/USER' ],
            'skimmerHisto' : 'jetObservables_histograms_QCDPt800to1000_UL2018.root',
            'nevents' : 36056000.0,
            'nGenWeights' : 36056000.0,
            },
        'selection' : 'dijet',
        'XS' : 2.624e+01,
        'label' : 'QCD Pythia8',
        'color': ROOT.kBlue
    },

    'QCD_Pt_1000to1400_TuneCP5_13TeV_pythia8' : {
        '2017' :  {
            'miniAOD' : [ '/QCD_Pt_1000to1400_TuneCP5_13TeV_pythia8/RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/QCD_Pt_1000to1400_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/QCD_Pt_1000to1400_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD_jetObservables_Skimmer_v04p3-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : 'jetObservables_histograms_QCDPt1000to1400_UL2017.root',
            'nevents' : 18653000.0,
            'nGenWeights' : 18653000.0,
            },
        '2018' :  {
            'miniAOD' : [ '/QCD_Pt_1000to1400_TuneCP5_13TeV_pythia8/RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/QCD_Pt_1000to1400_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-fff189d3e67d18da8f7301eb2c0e2940/USER' ],
            'skimmer' : [ '/QCD_Pt_1000to1400_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD_jetObservables_Skimmer_v04p3-fff189d3e67d18da8f7301eb2c0e2940/USER' ],
            'skimmerHisto' : 'jetObservables_histograms_QCDPt1000to1400_UL2018.root',
            'nevents' : 19106000.0,
            'nGenWeights' : 19106000.0,
            },
        'selection' : 'dijet',
        'XS' : 7.477e+00,
        'label' : 'QCD Pythia8',
        'color': ROOT.kBlue
    },

    'QCD_Pt_1400to1800_TuneCP5_13TeV_pythia8' : {
        '2017' :  {
            'miniAOD' : [ '/QCD_Pt_1400to1800_TuneCP5_13TeV_pythia8/RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/QCD_Pt_1400to1800_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/QCD_Pt_1400to1800_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD_jetObservables_Skimmer_v04p3-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : 'jetObservables_histograms_QCDPt1400to1800_UL2017.root',
            'nevents' : 10358000.0,
            'nGenWeights' : 10358000.0,
            },
        '2018' :  {
            'miniAOD' : [ '/QCD_Pt_1400to1800_TuneCP5_13TeV_pythia8/RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/QCD_Pt_1400to1800_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-fff189d3e67d18da8f7301eb2c0e2940/USER' ],
            'skimmer' : [ '/QCD_Pt_1400to1800_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD_jetObservables_Skimmer_v04p3-fff189d3e67d18da8f7301eb2c0e2940/USER' ],
            'skimmerHisto' : 'jetObservables_histograms_QCDPt1400to1800_UL2018.root',
            'nevents' : 10550000.0,
            'nGenWeights' : 10550000.0,
            },
        'selection' : 'dijet',
        'XS' : 6.423e-01,
        'label' : 'QCD Pythia8',
        'color': ROOT.kBlue
    },

    'QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8' : {
        '2017' :  {
            'miniAOD' : [ '/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD_jetObservables_Skimmer_v04p3-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : '',
            'nevents' : 5191000.0,
            'nGenWeights' : 5191000.0,
            },
        '2018' :  {
            'miniAOD' : [ '/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-fff189d3e67d18da8f7301eb2c0e2940/USER' ],
            'skimmer' : [ '/QCD_Pt_1800to2400_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD_jetObservables_Skimmer_v04p3-fff189d3e67d18da8f7301eb2c0e2940/USER' ],
            'skimmerHisto' : 'jetObservables_histograms_QCDPt1800to2400_UL2018.root',
            'nevents' : 5152000.0,
            'nGenWeights' : 5152000.0,
            },
        'selection' : 'dijet',
        'XS' : 8.746e-02,
        'label' : 'QCD Pythia8',
        'color': ROOT.kBlue
    },

    'QCD_Pt_2400to3200_TuneCP5_13TeV_pythia8' : {
        '2017' :  {
            'miniAOD' : [ '/QCD_Pt_2400to3200_TuneCP5_13TeV_pythia8/RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/QCD_Pt_2400to3200_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/QCD_Pt_2400to3200_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD_jetObservables_Skimmer_v04p3-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : 'jetObservables_histograms_QCDPt2400to3200_UL2017.root',
            'nevents' : 2757000.0,
            'nGenWeights' : 2757000.0,
            },
        '2018' :  {
            'miniAOD' : [ '/QCD_Pt_2400to3200_TuneCP5_13TeV_pythia8/RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/QCD_Pt_2400to3200_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-fff189d3e67d18da8f7301eb2c0e2940/USER' ],
            'skimmer' : [ '/QCD_Pt_2400to3200_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD_jetObservables_Skimmer_v04p3-fff189d3e67d18da8f7301eb2c0e2940/USER' ],
            'skimmerHisto' : 'jetObservables_histograms_QCDPt2400to3200_UL2018.root',
            'nevents' : 2901000.0,
            'nGenWeights' : 2901000.0,
            },
        'selection' : 'dijet',
        'XS' : 5.233e-03,
        'label' : 'QCD Pythia8',
        'color': ROOT.kBlue
    },

    'QCD_Pt_3200toInf_TuneCP5_13TeV_pythia8' : {
        '2017' :  {
            'miniAOD' : [ '/QCD_Pt_3200toInf_TuneCP5_13TeV_pythia8/RunIISummer20UL17MiniAODv2-106X_mc2017_realistic_v9-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/QCD_Pt_3200toInf_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD-106X_mc2017_realistic_v9-v1-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmer' : [ '/QCD_Pt_3200toInf_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL17PFNanoAOD_jetObservables_Skimmer_v04p3-7a1edb72314467730e458def0bc98536/USER' ],
            'skimmerHisto' : 'jetObservables_histograms_QCDPt3200toInf_UL2017.root',
            'nevents' : 1000000.0,
            'nGenWeights' : 1000000.0,
            },
        '2018' :  {
            'miniAOD' : [ '/QCD_Pt_3200toInf_TuneCP5_13TeV_pythia8/RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM' ],
            'nanoAOD' : [ '/QCD_Pt_3200toInf_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD-106X_upgrade2018_realistic_v16_L1v1-v1-fff189d3e67d18da8f7301eb2c0e2940/USER' ],
            'skimmer' : [ '/QCD_Pt_3200toInf_TuneCP5_13TeV_pythia8/algomez-RunIISummer20UL18PFNanoAOD_jetObservables_Skimmer_v04p3-fff189d3e67d18da8f7301eb2c0e2940/USER' ],
            'skimmerHisto' : 'jetObservables_histograms_QCDPt3200toInf_UL2018.root',
            'nevents' : 934000.0,
            'nGenWeights' : 934000.0,
            },
        'selection' : 'dijet',
        'XS' : 1.351e-04,
        'label' : 'QCD Pythia8',
        'color': ROOT.kBlue
    },


    


}

def checkDict( string, dictio ):
    return next(v for k,v in dictio.items() if string.startswith(k))
