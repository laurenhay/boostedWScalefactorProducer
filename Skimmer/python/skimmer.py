import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from collections import OrderedDict
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection,Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import *
from boostedWScalefactorProducer.Skimmer.PileupWeightTool import *
from boostedWScalefactorProducer.Skimmer.variables import recoverNeutrinoPz
from boostedWScalefactorProducer.Skimmer.SpecificYearConfig import SpecificYearConfig


import math,os,sys
import random
import array


# This is a loose selection to select events for T Tbar semileptonic events where 
# Type 1 and Type 2 events are included in the selection:

# In SF code the final cuts need to be made to choose either type 1 or type 2 selection:
# e.g. for type 1 the W leptonic Pt cut should be tightened to 200 GeV and dPhi cuts applied
# e.g. for type 2 the AK8 Pt cut should be tightened to 400 GeV and dPhi cuts applied

# Type 1 - martially merged Hadronic Top Quark (W is AK8, b is AK4) 
#(AK8 Pt > 200 GeV)

# Type 2 - fully merged Top (Top is AK8, W is most massive SD subjet, b is less massive subjet, require 1 subjet b-tag) 
#(AK8 Pt > 400 GeV): 


# selection aligned with previous SF measurement standard selection
# https://www.evernote.com/shard/s282/sh/7e5d6baa-d100-4025-8bf8-a61bf1adfbc1/f7e86fde2c2a165e


# 1 AK8 Pt > 200 GeV, |eta| < 2.5 , dR(Ak8, lep) > 1.0
# 1 AK4 Pt > 30 GeV, |eta| < 2.5
# 1 lepton , mu pt > 53 GeV or el pt > 120 GeV
# MET Pt > 40(mu) or 80(el) GeV
#Leptonic W - lepton + MET has Pt > 150 GeV # did not apply this since we are missing MET eta
         
class Skimmer(Module):
    def __init__(self, Channel, leptonSF={}, year='2018'):
        self.chan = Channel
        self.writeHistFile = True
        self.verbose = False
        self.year = year
        self.leptonSFhelper = leptonSF
        print(self.leptonSFhelper)

        ### Cuts for selections
        self.minLeadAK8JetPtW = 200.
	self.minLepWPt = 200. #to select boosted topologies in semi-leptonic ttbar
        self.minSDMassW = 60.   
        self.maxSDMassW = 125. #changing from previous

        #self.METCut = 40. #what's used in the selections of https://github.com/kaustuvdatta/jetObservables/blob/106X/Skimmer/ for muons
	    self.mindRLepJet = 1.0  #removal of any AK8 jet within dR<=1. of a lepton

        ### Kinematics Cuts AK4Jets ###
        self.minAK4JetPt = 20
        self.maxAK4JetEta = 2.4
        self.minBDisc = 0.3093  ### L: 0.0614, M: 0.3093, T: 07221, for DeepJet (ie, DeepFlavB)
        
        ### Kinematics Cuts AK8Jets ###
        self.minAK8JetPt = 170  ### this is the basic minimum, not the final
        self.maxJetAK8Eta = 2.4
        
        ### Kinenatic Cuts Muons ###
        self.minMupt = 55.
        self.maxMuEta = 2.4
        self.maxRelIso = 0.15
        self.minMuMETPt = 0.

        ### Kinenatic Cuts Electrons ###
        self.minElpt = 120.
        self.minElMETPt = 80.
     
        self.range1ElectronEta = [0,1.442]
        self.range2ElectronEta = [1.56,2.5]

        self.totalEventWeight = 1
 	
	'''
        #remove  AK8 jet within 1.0 of lepton

        self.minJetPt = 200.
        self.maxJetEta = 2.5

        self.minBDisc = 0.8484
        ### Medium https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation80XReReco

        #>= 1 CSVmedium akt4 jet
        self.minAK4Pt = 30.

        #Angular selection (to be implemented later, in fitting code):
        #dR( lepton, leading AK8 jet) > pi/2
        #dPhi(leading AK8 jet, MET) > 2
        #dPhi (leading AK8 jet, leptonic W) >2
        #self.minDPhiWJet = 2.  
        '''


    def beginJob(self, histFile, histDirName):
        Module.beginJob(self, histFile, histDirName)
        
        self.yearSpecificConfig = SpecificYearConfig(self.year, self.verbose)
   	
	### Book histograms
	self.addObject( ROOT.TH1F('nPVs',   ';number of PVs',   100, 0, 100) )
        self.addObject( ROOT.TH1F('nleps',   ';number of leptons',   20, 0, 20) )
        self.addP4Hists( 'muons', '' )
        self.addP4Hists( 'eles', '' )
        self.addObject( ROOT.TH1F('nAK8jets',   ';number of AK8 jets',   20, 0, 20) )
        self.addP4Hists( 'AK8jets', isel )
        self.addObject( ROOT.TH1F('nAK4jets',   ';number of AK4 jets',   20, 0, 20) )
        self.addP4Hists( 'AK4jets', '' )
        self.addObject( ROOT.TH1F('METPt',   ';MET (GeV)',   200, 0, 2000) )
        self.addObject( ROOT.TH1F('HT',   ';HT (GeV)',   200, 0, 2000) )
	
       
        
    def endJob(self):
        Module.endJob(self)
        print "Module ended successfully,", self.nEvent, "events analyzed"
        pass

    #############################################################################
    def addP4Hists(self, s, t ):
        self.addObject( ROOT.TH1F(s+'_pt'+t,  s+';p_{T} (GeV)',   200, 0, 2000) )
        self.addObject( ROOT.TH1F(s+'_eta'+t, s+';#eta', 100, -4.0, 4.0 ) )
        self.addObject( ROOT.TH1F(s+'_phi'+t, s+';#phi', 100, -3.14259, 3.14159) )
        self.addObject( ROOT.TH1F(s+'_mass'+t,s+';mass (GeV)', 100, 0, 1000) )
    #############################################################################


    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):         
        print "Beginning on inputFile, writing new branches"
        self.out = wrappedOutputTree
        # self.addObject( ROOT.TH1F('nGenEv',   'nGenEv',   3, 0, 3) )
        self.addObject( ROOT.TH1F('PUweight',   ';PUweight',   20, 0, 2) )
        self.addObject( ROOT.TH1F('Lepweight',   ';LepWeight',   20, 0, 2) )
        #self.puWeightTool = PileupWeightTool(yearMC=2018, yearData=2018) 

        self.out.branch('eventCategory', "I") #1 = pass, matched reco AK8; 2 = pass, unmatched reco AK8; 0 = failed to pass reco selection
        self.out.branch("SelectedJet_softDrop_mass",  "F")
        self.out.branch("SelectedJet_tau42",  "F")
        self.out.branch("SelectedJet_tau41",  "F")
        self.out.branch("SelectedJet_tau32",  "F")
        self.out.branch("SelectedJet_tau21",  "F")
        self.out.branch("SelectedJet_tau21_ddt",  "F")
        self.out.branch("SelectedJet_tau21_ddt_retune",  "F")      
        self.out.branch("SelectedJet_pt",   "F")
        self.out.branch("SelectedJet_eta",  "F")
        self.out.branch("SelectedJet_mass", "F")
        self.out.branch("SelectedLepton_pt",  "F")
        self.out.branch("SelectedLepton_iso",  "F")
        self.out.branch("Wlep_type",  "I")
        self.out.branch("W_pt",  "F")
        self.out.branch("W_mass",  "F")
        self.out.branch("dr_LepJet",  "F")
        self.out.branch("dphi_LepJet",  "F")
        self.out.branch("dphi_LepMet",  "F")
        self.out.branch("dphi_MetJet",  "F")
        self.out.branch("dphi_WJet"  ,  "F")
        self.out.branch("maxAK4CSV",  "F")
        self.out.branch("subMaxAK4CSV",  "F")
        self.out.branch("minJetMetDPhi",  "F")
        self.out.branch("HT_HEM1516",  "F")
        self.out.branch("genmatchedAK8",  "I")
        self.out.branch("genmatchedAK8Quarks",  "I")
        self.out.branch("genmatchedAK8Subjet",  "I")
        self.out.branch("genmatchedAK82017",  "I")
        self.out.branch("AK8Subjet0isMoreMassive",  "I")
        self.out.branch("passedMETfilters",  "I")
        self.out.branch("lheweight",  "F")
        self.out.branch("puweight",  "F")
        self.out.branch("topweight",  "F")
        self.out.branch("btagweight",  "F")
        self.out.branch("triggerweight",  "F")
        
        pass

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        print "File closed successfully"
        pass

    
    def leptonSF(self, lepton, leptonP4 ):

        if lepton.startswith("muon"): leptonP4eta = abs(leptonP4.eta)
        else: leptonP4eta = leptonP4.eta

        SFFileTrigger = ROOT.TFile( os.environ['CMSSW_BASE']+"/src/jetObservables/Skimmer/data/"+self.leptonSFhelper[lepton]['Trigger'][0] )
        histoSFTrigger = SFFileTrigger.Get( self.leptonSFhelper[lepton]['Trigger'][1] )
        SFTrigger = histoSFTrigger.GetBinContent( histoSFTrigger.GetXaxis().FindBin( leptonP4.pt ), histoSFTrigger.GetYaxis().FindBin( leptonP4eta ) )

        SFFileID = ROOT.TFile( os.environ['CMSSW_BASE']+"/src/jetObservables/Skimmer/data/"+self.leptonSFhelper[lepton]['ID'][0] )
        histoSFID = SFFileID.Get( self.leptonSFhelper[lepton]['ID'][1] )
        histoSFID_X = histoSFID.GetXaxis().FindBin( leptonP4.pt if self.leptonSFhelper[lepton]['ID'][2] else leptonP4eta )
        histoSFID_Y = histoSFID.GetYaxis().FindBin( leptonP4eta if self.leptonSFhelper[lepton]['ID'][2] else leptonP4.pt )
        SFID = histoSFID.GetBinContent( histoSFID_X, histoSFID_Y )
        SFID = SFID if SFID>0 else 1

        if self.year.startswith('2016') and lepton.startswith("muon"): leptonP4eta = leptonP4.eta    #### stupid fix for the stupid SF file
        SFFileISO = ROOT.TFile( os.environ['CMSSW_BASE']+"/src/jetObservables/Skimmer/data/"+self.leptonSFhelper[lepton]['ISO'][0] )
        histoSFISO = SFFileISO.Get( self.leptonSFhelper[lepton]['ISO'][1] )
        histoSFISO_X = histoSFISO.GetXaxis().FindBin( leptonP4.pt if self.leptonSFhelper[lepton]['ISO'][2] else leptonP4eta )
        histoSFISO_Y = histoSFISO.GetYaxis().FindBin( leptonP4eta if self.leptonSFhelper[lepton]['ISO'][2] else leptonP4.pt )
        SFISO = histoSFISO.GetBinContent( histoSFISO_X, histoSFISO_Y )
        SFISO = SFISO if SFISO>0 else 1

        #print (SFTrigger * SFID * SFISO), SFTrigger , SFID , SFISO, leptonP4.pt, leptonP4.eta
        return [SFTrigger , SFID , SFISO]
       
    def getSimplifiedElectronTriggerSF2018(self, pt, eta):  #TODO: remove
        # /work/pbaertsc/heavy_resonance/NanoTreeProducer/CorrectionTools/leptonEfficiencies/ElectronPOG/Run2018/Ele115orEle35_SF_2018.root
        # Ratio ELE_DATA and ELE_MC
        if pt < 120:
            if eta > -0.9: return 0.97
            else: return 0.90
        elif pt > 500 and abs(eta) > 0.9 and abs(eta) < 1.7: return 0.95
        else: return 0.98

    def getSimplifiedMuonTriggerSF2018(self, pt, eta):  #TODO: remove
        # https://gitlab.cern.ch/cms-muonPOG/MuonReferenceEfficiencies/blob/master/EfficienciesStudies/2018_trigger/theJSONfile_2018Data_AfterMuonHLTUpdate.json
        # "Mu50_OR_OldMu100_OR_TkMu100_PtEtaBins"
        if pt < 200: #"pt:[120.0,200.0]"
            if abs(eta) > 2.1: return 0.85
            else: return 0.93
        else: #"pt:[300.0,1200.0]"
            if abs(eta) > 2.1: return 0.82
            else: return 0.89

    def getBTagWeight(self, nBTagged=0, jet_SFs=[0]): 
#ported from https://github.com/ferencek/cms-MyAnalyzerDijetCode/blob/5bca32a7bb58a16abdb2c31b4c0379e6ffa27c91/MyAnalyzer_MainAnalysis_DijetBBTag_2011.cc#L1297 following recommendations on https://twiki.cern.ch/twiki/bin/viewauth/CMS/BTagSFMethods
        bTagWeight=0
        if len(jets_SFs)>2 or nBTagged>2: 
            print "Error, only leading and subleading AK4 jets are considered: # of btagged jets cannot exceed 2"
        if nBTagged>len(jet_SFs): 
            print "#b-tagged jets cannot be greater than number of them for which SFs are provided!"
            return 0
        if nBTagged==0 and len(jet_SFs)==0: return 1
        
        if len(jet_SFs)==1:
            SF = jets_SFs[0]
            
            for i in range(0,2):
                if i!=nBTagged: continue
                bTagWeight+=ROOT.TMath.pow(SF,i)*ROOT.TMath.pow(1-SF,1-i)
        
        elif len(jet_SFs)==2:
            SF1, SF2 = jet_SFs[0], jet_SFs[1]
            for i in range(0,2):
                for j in range(0,2):
                    if (i+j)!=nBTagged: continue
                    bTagWeight+=ROOT.TMath.pow(SF1,i)*ROOT.TMath.pow(1-SF,1-i)*pow(SF2,j)*pow(1-SF2,1-j)
        
        return bTagWeight

        
        
    def getSubjets(self, p4, subjets, dRmax=0.8):
        ret = []
        for subjet in subjets :
            if p4.DeltaR(subjet.p4()) < dRmax and len(ret) < 2 :
                ret.append(subjet.p4())
        return ret

    def printP4( self, c ):
        if hasattr( c, "p4"):
            s = ' %6.2f %5.2f %5.2f %6.2f ' % ( c.p4().Perp(), c.p4().Eta(), c.p4().Phi(), c.p4().M() )
        else :
            s = ' %6.2f %5.2f %5.2f %6.2f ' % ( c.Perp(), c.Eta(), c.Phi(), c.M() )
        return s
    

    def printCollection(self,coll):
        for ic,c in enumerate(coll):
            s = self.printP4( c )
            print ' %3d : %s' % ( ic, s )
            
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        
	        self.isMC = event.run == 1        

        self.dummy+=1
        if (self.dummy > 20000): return False
        if self.verbose: print ('Event : ', event.event)
        if self.dummy%500==0: print ("Analyzing events...", self.dummy)

        passRecoSel, selRecoMuons, selRecoElectrons, selRecoAK4bjets, selRecoJets, selRecoMET = self.recoSelection( event )
        recoJet = OrderedDict()
        if passRecoSel:
            self.out.fillBranch( 'eventCategory', 1 )
            #recoJet['Jet'] = self.createNsubBranches( selRecoJets[0], event, 'PFCandsAK8' )
            #WEIGHT =  self.totalEventWeight
            
        else: self.out.fillBranch('eventCategory', 0)

        
    def recoSelection(self, event):
        '''Analyzing reco-level objects'''
        '''Encapsulating selections, and objects stored/returned thereafter into one function'''
        
        AK8jets = list(Collection(event, 'FatJet' ))
        allelectrons = list(Collection(event, 'Electron'))
        allmuons = list(Collection(event, 'Muon'))
        jets = list(Collection(event, 'Jet'))
        met = Object(event, 'MET')        

        #puweight = 1.
        lheweight = 1.
        topweight = 1.
        #btagweight = 1.
        triggerweight = 1.
        isMC = (event.run == 1)
    
        if not (event.HLT_Mu50 or (event.HLT_Ele32_WPTight_Gsf or event.HLT_Ele35_WPTight_Gsf or event.HLT_Ele40_WPTight_Gsf or event.HLT_Ele115_CaloIdVT_GsfTrkIdT)): return False   #TODO: check if all those triggers are available in 2016
        if not (event.nMuon > 0 or event.nElectron > 0): return False 
        if not event.nFatJet > 0: return False                                  #?

        
        ### Find high-pT lepton, veto additional leptons, check trigger ###
        

        # Here we make some loose selections for each category; including loose pT cuts for veto
        electrons = [x for x in allelectrons if x.pt > 10. and x.cutBased >= 2 and ( abs(x.eta) < 1.44 or ( abs(x.eta) > 1.56 and abs(x.eta) < 2.5 ) )] 
        muons     = [x for x in allmuons if x.pt > 10. and x.looseId and abs(x.eta) < self.maxMuEta and x.pfIsoId >= 2] 

        # Ordering the loosely selected categories according to Pt 
        muons.sort(key=lambda x:x.pt,reverse=True)
        electrons.sort(key=lambda x:x.pt,reverse=True)

        # Check if the muon or electron with highest pT passes the tight selection (additional cuts to the loose selection)
        electronTight = len(electrons) > 0 and electrons[0].pt > 55. and electrons[0].cutBased >= 4  

        muonTight = len(muons) > 0 and muons[0].pt > 55. and abs(muons[0].eta) < self.maxMuEta and muons[0].highPtId >= 2 and muons[0].isPFcand and muons[0].pfIsoId >= 6


        possibleChannels = ["mu", "el", "elmu"]

        if self.chan not in possibleChannels : 
          print "Channel not defined! Skipping"
          print "Please select a channel in the following: "
          print possibleChannels
          return False

        
        # We require exactly one tight muon and no (loose) electron, or exactly one tight electron and no (loose) muon 
        self.Vlep_type = -1
        lepton = ROOT.TLorentzVector()
        iso = 0.

        if ("mu" in self.chan and muonTight and (len(muons) == 1) and (len(electrons) == 0)) :  # There is one tight muon and no other loose electron or muon 

          triggerEl = 0 # TODO: idem? 
          #if not triggerMu: return False
          self.Vlep_type = 0
          lepton = muons[0].p4()
          iso = muons[0].pfRelIso03_all
          if isMC: triggerweight = yearSpecificConfig.MuonTriggerSF(muons[0].pt, muons[0].eta)     #self.getSimplifiedMuonTriggerSF2018(muons[0].pt, muons[0].eta)

        elif ("el" in self.chan and electronTight and (len(electrons) == 1) and (len(muons) == 0)) :  # There is a tight electron and no other loose muon or electron
          triggerEl = (event.HLT_Ele32_WPTight_Gsf or event.HLT_Ele35_WPTight_Gsf or event.HLT_Ele40_WPTight_Gsf or event.HLT_Ele115_CaloIdVT_GsfTrkIdT)
          triggerMu = 0
          #if not triggerEl: return False
          self.Vlep_type = 1
          lepton = electrons[0].p4()
          iso = electrons[0].pfRelIso03_all
          if isMC: triggerweight = self.getSimplifiedElectronTriggerSF2018(electrons[0].pt, electrons[0].eta)  # TODO: Add this to the SpecificYearConfig (class and config file)

        else : 
          return False 


        passedMETFilters = False
        try:
          if event.Flag_goodVertices and event.Flag_globalSuperTightHalo2016Filter and event.Flag_BadPFMuonFilter and event.Flag_EcalDeadCellTriggerPrimitiveFilter and event.Flag_HBHENoiseFilter and event.Flag_HBHENoiseIsoFilter and (isMC or event.Flag_eeBadScFilter) and event.Flag_ecalBadCalibFilterV2:  # TODO: check if this makes sense 
            passedMETFilters = True
        except:
           passedMETFilters = False
          # if not passedMETFilters: return False

        if not passedMETFilters: return False
        
        # Apply MET cut    
        met = Object(event, "MET")
#        if self.Vlep_type == 0 and met.sumEt < self.minMuMETPt : return False
#        if self.Vlep_type == 1 and met.sumEt < self.minElMETPt : return False
        MET  = ROOT.TLorentzVector()
        MET.SetPtEtaPhiE(met.pt, 0., met.phi, met.pt)
        
        # Apply leptonic W cut
        WcandLep = lepton + MET
        # if WcandLep.Perp() < self.minLepWPt :
        #     return False

        pz = recoverNeutrinoPz(lepton, MET)
        neutrino  = ROOT.TLorentzVector()
        neutrino.SetPxPyPzE(MET.Px(), MET.Py(), pz, math.sqrt(MET.Px()**2 + MET.Py()**2 + pz**2))
        WcandLep = lepton + neutrino
        
        if not WcandLep.Pt() >= self.minWPt: return False   
        
        # Find fat jet
        FatJets = list(Collection(event, "FatJet"))
        recoAK8 = [ x for x in FatJets if x.p4().Perp() > self.minJetPt and  abs(x.p4().Eta()) < self.maxJetEta and x.msoftdrop > 30. and x.tau1 > 0. and x.tau2 > 0.]
#        recoAK8.sort(key=lambda x:x.msoftdrop,reverse=True)
        recoAK8.sort(key=lambda x:x.pt,reverse=True)
        if not len(recoAK8) > 0: return False

        jetAK8_4v = ROOT.TLorentzVector()
        #jetAK8_4v.SetPtEtaPhiM(recoAK8[0].pt,recoAK8[0].eta,recoAK8[0].phi,recoAK8[0].mass)
        jetAK8_4v.SetPtEtaPhiM(recoAK8[0].pt,recoAK8[0].eta,recoAK8[0].phi,recoAK8[0].mass)
        
        
        #Check for b-jet in the event, apply DeepJet later
        Jets = list(Collection(event, "Jet")) 
        recoAK4 = [ x for x in Jets if x.p4().Perp() > self.minAK4Pt and abs(x.p4().Eta()) < self.maxJetEta and jetAK8_4v.DeltaR(x.p4())>1.0 and x.btagDeepFlavB > self.minBDisc
        if len(recoAK4) < 1: return False
        
        # max and second max AK4 CSV
        #bTagValues = [ x.btagDeepFlavB for x in recoAK4]
        bTagSFs =  [x.btagSF for x in recoAK4]
        '''
        maxAK4CSV = -1.
        subMaxAK4CSV = -1.

        if len(bTagValues) >= 1 : 
          maxAK4CSV = max(bTagValues)

        if len(bTagValues) >= 2 : 
          bTagValues.remove(maxAK4CSV)
          subMaxAK4CSV = max(bTagValues) # max([ x.btagCSVV2 for x in [z for z in recoAK4 if z != maxAK4CSV]])
        '''
        
        minJetMetDPhi = min([ abs(x.p4().DeltaPhi(MET)) for x in recoAK4]) if len(recoAK4) >= 1 else -1.
        
        # No lepton overlap
        dR_jetlep = jetAK8_4v.DeltaR(lepton )
        if abs(dR_jetlep) < self.mindRLepJet : return False

        # Angular separation cuts
        if not dR_jetlep > 1.5708: return False
        if not abs(jetAK8_4v.DeltaPhi(MET)) > 1.5708: return False
        
        HT_HEM1516 = 0.
        for j in Jets:
            if j.eta > -3.0 and j.eta < -1.3 and j.phi > -1.57 and j.phi < -0.87:
                HT_HEM1516 += j.pt

        # Gen
        self.isW = 0
        self.isWqq = 0
        self.matchedJ = 0
        self.matchedSJ = 0
        
        #### Weight
        if self.isMC:
            try:
                if event.LHEWeight_originalXWGTUP < 0.: lheweight = -1.
            except:
                pass
            #puweight = self.puWeightTool.getWeight(event.Pileup_nTrueInt)
            #event.btagWeight_CSVV2 if not event.btagWeight_CSVV2==0 else 1.

        if self.isMC:
            if len(recoMuons)>0: leptonWeights= self.leptonSF( "muon", recoMuons[0] )
            else: leptonWeights = [0, 0, 0]
	    
	    if len(recoElectrons)>0: leptonWeights= self.leptonSF( "electron", recoElectrons[0] )
            else: leptonWeights = [0, 0, 0]

        else: leptonWeights = [1, 1, 1]

        if self.isMC:
            btagweight = self.getBTagWeight(nBTagged=len(recoAK4), jet_SFs=btagSFs) #obtaining btagSF's from nanoAODTools' BTagSFPRoducer 
            weight = event.puWeight * event.genWeight * np.prod(leptonWeights) * btagweight
            getattr( self, 'PUWeight' ).Fill( event.puWeight )
            getattr( self, 'LepWeight' ).Fill( np.prod(leptonWeights) )
            self.leptonWeight = np.prod(leptonWeights)
        else:
            weight = 1
            self.leptonWeight = 1
        self.out.fillBranch("leptonWeight", np.prod(leptonWeights) )  ### dummy for nanoAOD Tools
        self.totalEventWeight = weight
    
            ### Look at generator level particles
            ### find events where :
            ### a W decays to quarks (Type 1 - partially merged)
            ###    OR
            ### a Top decays to W + b (Type 2 - fully merged top quark)
            gens = Collection(event, "GenPart")
            Wdaus =  [x for x in gens if x.pt>1 and 0<abs(x.pdgId)<9]
            Ws =  [x for x in gens if x.pt>10 and abs(x.pdgId)==24]

            TWdaus =  [x for x in gens if x.pt>1 and  0<abs(x.pdgId)<4]
            Tdaus =  [x for x in gens if x.pt>1 and (abs(x.pdgId)==5  or  abs(x.pdgId)==24 )]
            Ts =  [x for x in gens if x.pt>10 and abs(x.pdgId)==6] 
            Tops =  [x for x in gens if x.pdgId==6]
            AntiTop =  [x for x in gens if x.pdgId==-6]
            
            realVs = []
            realVdaus = []

            realTs = []
            realWs = []
            realqs = []
            self.matchedJ = 0
            self.matchedSJ = 0

            if len(Ws)>0 and len(Wdaus)>0:
              for dau in Wdaus:
                for mom in Ws:
                  try:
                    if mom == gens[dau.genPartIdxMother]: 
                      realVs.append(mom)
                      realVdaus.append(dau)    
                  except:
                    continue    

            if len(Ts)>0 and len(Tdaus)>0:   # TODO: remove? 
              for gdau in TWdaus :
                for dau in Tdaus:
                  for mom in Ts:
                    try:
                      if mom == gens[dau.genPartIdxMother] and dau == gens[gdau.genPartIdxMother]: 
                        realTs.append(mom)
                        realWs.append(dau)
                        realqs.append(gdau)    
                    except:
                      continue  
            
            if len(Top)>0 and len(AntiTop)>0:
                topSF = math.exp(0.0615 - 0.0005 * Top[0].pt)
                antitopSF = math.exp(0.0615 - 0.0005 * AntiTop[0].pt)
                topweight = math.sqrt(topSF*antitopSF)
                
        
        # Check if matched to genW and genW daughters
        #for partially merged:
        self.isW = 0
        self.isWqq = 0
        self.isW2017 = 0
        # TODO: check if we want to keep all matching definitions 
        if isMC == False:
            genjets = [None] * len(recoAK8)

        else:
             
            # standard gen matching   
	    for V in realVs:
                gen_4v = ROOT.TLorentzVector()
                gen_4v.SetPtEtaPhiM(V.pt,V.eta,V.phi,V.mass)
                dR = jetAK8_4v.DeltaR(gen_4v)
                if dR < 0.8: 
                    nDau = 0
                    for v in realVdaus:
                        gen_4v = ROOT.TLorentzVector()
                	gen_4v.SetPtEtaPhiM(v.pt,v.eta,v.phi,v.mass)
                	dR = jetAK8_4v.DeltaR(gen_4v)
                	if dR < 0.6: #changed from 0.8 
                  	    nDau +=1                 
                  	    self.isWqq = 1
          
       
        #for fully merged:  # TODO: remove this part (not used anymore)
        self.SJ0isW = -1
        # List of reco subjets:
        recosubjets = list(Collection(event,"SubJet"))
        # Dictionary to hold ungroomed-->groomed for reco
        recoAK8Groomed = {}        
        # Get the groomed reco jets
        maxrecoSJmass = 1.
        WHadreco = None
        for ireco,reco in enumerate(recoAK8):
            if reco.subJetIdx2 >= len(recosubjets) or reco.subJetIdx1 >= len(recosubjets) :
                if self.verbose: print "Reco subjet indices not in Subjet list, Skipping"
                continue
            if reco.subJetIdx1 >= 0 and reco.subJetIdx2 >= 0 :
                recoAK8Groomed[reco] = recosubjets[reco.subJetIdx1].p4() + recosubjets[reco.subJetIdx2].p4()
                if recosubjets[reco.subJetIdx1].p4().M() > maxrecoSJmass and recosubjets[reco.subJetIdx1].p4().M() >  recosubjets[reco.subJetIdx2].p4().M() :
                    maxrecoSJmass = recosubjets[reco.subJetIdx1].p4().M()
                    WHadreco = recosubjets[reco.subJetIdx1].p4()
                    if recosubjets[reco.subJetIdx1].btagCSVV2 >  self.minBDisc  or recosubjets[reco.subJetIdx2].btagCSVV2 >  self.minBDisc :
                        self.SJ0isW = 1
                if recosubjets[reco.subJetIdx2].p4().M() > maxrecoSJmass and recosubjets[reco.subJetIdx2].p4().M() < recosubjets[reco.subJetIdx2].p4().M() :
                    maxrecoSJmass = recosubjets[reco.subJetIdx1].p4().M()
                    WHadreco = recosubjets[reco.subJetIdx2].p4()
                    if recosubjets[reco.subJetIdx1].btagCSVV2 >  self.minBDisc  or recosubjets[reco.subJetIdx2].btagCSVV2 >  self.minBDisc :
                        self.SJ0isW = 0
                if isMC and WHadreco != None and self.SJ0isW >= 0 :
                      
                    for q in realqs:
                        gen_4v = ROOT.TLorentzVector()
                        gen_4v.SetPtEtaPhiM(q.pt,q.eta,q.phi,q.mass)
                        dR = WHadreco.DeltaR(gen_4v)
                        if dR < 0.6: self.matchedSJ = 1
            else :
                recoAK8Groomed[reco] = None
                WHadreco = None
        
        # now fill branches
        self.out.fillBranch("genmatchedAK8",  self.isW)
        self.out.fillBranch("genmatchedAK8Quarks",  self.isWqq)
        self.out.fillBranch("genmatchedAK82017",  self.isW2017)
        self.out.fillBranch("genmatchedAK8Subjet", self.matchedSJ)
        self.out.fillBranch("AK8Subjet0isMoreMassive", self.SJ0isW )
        self.out.fillBranch("puweight", puweight )
        self.out.fillBranch("btagweight", btagweight )
        self.out.fillBranch("triggerweight", triggerweight )
        self.out.fillBranch("topweight", topweight )
        self.out.fillBranch("lheweight", lheweight )
        self.out.fillBranch("passedMETfilters", passedMETFilters)
        self.out.fillBranch("dr_LepJet"  , abs(dR_jetlep))
        self.out.fillBranch("dphi_LepJet", abs(jetAK8_4v.DeltaPhi(lepton)))
        self.out.fillBranch("dphi_LepMet", abs(lepton.DeltaPhi(MET)))
        self.out.fillBranch("dphi_MetJet", abs(jetAK8_4v.DeltaPhi(MET)))
        self.out.fillBranch("dphi_WJet"  , abs(jetAK8_4v.DeltaPhi(WcandLep)))
        self.out.fillBranch("Wlep_type",self.Vlep_type)
        self.out.fillBranch("W_pt", WcandLep.Pt() )
        self.out.fillBranch("W_mass", WcandLep.M() )
        self.out.fillBranch("maxAK4CSV", maxAK4CSV )
        self.out.fillBranch("subMaxAK4CSV", subMaxAK4CSV )
        self.out.fillBranch("minJetMetDPhi", minJetMetDPhi )
        self.out.fillBranch("HT_HEM1516", HT_HEM1516 )
        self.out.fillBranch("SelectedJet_softDrop_mass",  recoAK8[0].msoftdrop)
        self.out.fillBranch("SelectedJet_pt",   recoAK8[0].pt)
        self.out.fillBranch("SelectedJet_eta",  recoAK8[0].eta)
        self.out.fillBranch("SelectedJet_mass",  recoAK8[0].mass)
        self.out.fillBranch("SelectedLepton_pt", lepton.Pt())
        self.out.fillBranch("SelectedLepton_iso",  iso)
        if recoAK8[0].tau1 > 0.0: 
          tau21 = recoAK8[0].tau2/recoAK8[0].tau1
          tau41 = recoAK8[0].tau4/recoAK8[0].tau1
        else:
          tau21 = -1.
          tau41 = -1.
        if recoAK8[0].tau2 > 0.0: 
          tau42 = recoAK8[0].tau4/recoAK8[0].tau2
        else:
          tau42 = -1.
        self.out.fillBranch("SelectedJet_tau21",tau21)
        self.out.fillBranch("SelectedJet_tau21_ddt", tau21+0.063*ROOT.TMath.Log(recoAK8[0].msoftdrop**2/recoAK8[0].pt))
        self.out.fillBranch("SelectedJet_tau21_ddt_retune", tau21+0.082*ROOT.TMath.Log(recoAK8[0].msoftdrop**2/recoAK8[0].pt))
        if recoAK8[0].tau2 > 0.0: 
          tau32 = recoAK8[0].tau3/recoAK8[0].tau2
        else:
          tau32 = -1.     
        self.out.fillBranch("SelectedJet_tau32",tau32)
        self.out.fillBranch("SelectedJet_tau42",tau42)
        self.out.fillBranch("SelectedJet_tau41",tau41)
        
        self.nEvent += 1
        if self.nEvent % 1000 == 0: print "Filled event", self.nEvent
        
        
        return True


    ######################################################
                 ###Helper Functions###
    ######################################################
    def matchRecoGenParticle( self, event, recoJet ):

        genParticles = Collection(event, "GenPart")

        quarksFromW = GenQuarkFromW( genParticles )
        bquarksFromTop = GenBquarkFromTop( genParticles )
        allQuarksFromWtop = quarksFromW + bquarksFromTop

        listMatched = []
        for q in allQuarksFromWtop:
            #print event.event, q.pdgId, genParticles[q.genPartIdxMother].pdgId, q.p4().Pt()
            if recoJet.p4().DeltaR( q.p4() )<0.3: listMatched.append( True )
            else: listMatched.append( False )

        if (len(listMatched)==4) and all(listMatched[:2]) and not all(listMatched[2:]): boosted = 2  ## only boostedW
        elif (len(listMatched)==4) and all(listMatched[:2]) and any(listMatched[2:]): boosted = 4      ## boosted Top
        else: boosted = 0
        #print listMatched, boosted

        return boosted

###################### Different gen functions
def getDaughters(GenParticle,gp):
    ret = []
    tmpListGenParticles = list(GenParticle)
    for part in GenParticle:
        if part != gp:
            if part.genPartIdxMother == tmpListGenParticles.index(gp):
                ret.append(part)
    return ret

def GenBquarkFromTop(GenParticle):
    ret = []
    for gP in GenParticle:
        if (abs(gP.pdgId) == 5) and gP.genPartIdxMother>0:
            mom = GenParticle[gP.genPartIdxMother]
            if abs(mom.pdgId)  == 6:
                dauids = [abs(dau.pdgId) for dau in getDaughters(GenParticle,mom)]
                if 6 not in dauids:
                    ret.append(gP)
    return ret

def GenQuarkFromW(GenParticle):
    ret = []
    for gP in GenParticle:
        if gP.genPartIdxMother>0:
            if (abs(gP.pdgId) <= 5) and (abs(GenParticle[gP.genPartIdxMother].pdgId) == 24):
                ret.append(gP)
        if (abs(gP.pdgId) <= 5) and gP.genPartIdxMother>0:
            mom = GenParticle[gP.genPartIdxMother]
            if abs(mom.pdgId)  == 24:
                dauids = [abs(dau.pdgId) for dau in getDaughters(GenParticle,mom)]
                if 24 not in dauids:
                    ret.append(gP)

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
ttbar_semilep = lambda : Skimmer(Channel="elmu") 
