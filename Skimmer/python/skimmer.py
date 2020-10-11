import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
#from ROOT import TMath
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
import numpy as np


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
    def __init__(self, channel='elmu', leptonSF={}, year='2017'):
        self.chan = channel
        self.writeHistFile = True
        self.verbose = False
        self.year = year
        self.leptonSFhelper = leptonSF
        #print(self.leptonSFhelper)

        ### Cuts for selections (mostly aligned with CMS-JME-18-002)
        #self.minLeadAK8JetPtW = 200.
	self.minLepWPt = 250. #to select boosted topologies in semi-leptonic ttbar
        self.minSDMassW = 50.   
        self.maxSDMassW = 130. #changing from previous
	#self.mindRLepJet = 1.0  #removal of any AK8 jet within dR<=1. of a lepton

        ### Kinematics Cuts AK4Jets ###
        self.minAK4JetPt = 30.
        self.maxAK4JetEta = 2.4
        self.minBDisc = 0.3093  ### L: 0.0614, M: 0.3093, T: 07221, for DeepJet (ie, DeepFlavB)


        ### Kinematics Cuts AK8Jets ###
        self.minAK8JetPt = 200  
        self.maxAK8JetEta = 2.4
        
        ### Kinenatic Cuts Muons ###
        self.minMupt = 55. 
        self.maxMuEta = 2.5
        self.maxRelIso = 0.15
        self.minMuMETPt = 50. #this was previously 0 for 2018 re-reco! Why?

        ### Kinenatic Cuts Electrons ###
        self.minElpt = 120. 
        self.minElMETPt = 80.
     
        #self.range1ElectronEta = [0,1.442]
        #self.range2ElectronEta = [1.56,2.5]

        self.totalEventWeight = 1
	self.nEventsProcessed=0
	self.nEventsPassed = 0 	
	'''	
	#Angular selection (to be implemented later, in fitting code):
        #dR( lepton, leading AK8 jet) > pi/2
        #dPhi(leading AK8 jet, MET) > 2
        #dPhi (leading AK8 jet, leptonic W) >2
        #self.minDPhiWJet = 2.  
        '''


    def beginJob(self, histFile, histDirName):
            
        Module.beginJob(self, histFile, histDirName)
        # For debugging the pT_rel and dR selections
        self.addObject(ROOT.TH2F('pT_rel_dR_lepAK4_OG_TLV', ';p_{T}^{rel}; #Delta R(lep, AK4)', 1000, 0, 500, 1000, 0., 6.28) )
        self.addObject(ROOT.TH2F('pT_rel_dR_lepAK4_nanostyle', ';p_{T}^{rel}; #Delta R(lep, AK4)', 1000, 0, 500, 1000, 0., 6.28) )
        self.addObject(ROOT.TH2F('pT_rel_dR_lepAK4nano', ';p_{T}^{rel}; #Delta R(lep, AK4)', 1000, 0, 500, 1000, 0., 6.28) )
        #self.addObject(ROOT.TH2F('mindRlepAK4_etas', ';min #Delta R lep_{#eta}; min #Delta R AK4_{#eta}', 100, -3., 3., 100, -3., 3.) )
        
        
        #self.yearSpecificConfig = SpecificYearConfig(self.year, self.verbose)
   	self.nEventsProcessed=0
	print ('Beginning job, current nEventsProcessed=%d'%self.nEventsProcessed)
       
        
    def endJob(self):
        Module.endJob(self)
        print "Module ended successfully,", self.nEventsProcessed, "events analyzed"
        pass

    #############################################################################
    def addP4Hists(self, s, t ):
        self.addObject( ROOT.TH1F(s+'_pt',  s+';p_{T} (GeV)',   200, 0, 2000) )
        self.addObject( ROOT.TH1F(s+'_eta', s+';#eta', 100, -4.0, 4.0 ) )
        self.addObject( ROOT.TH1F(s+'_phi', s+';#phi', 100, -3.14259, 3.14159) )
        self.addObject( ROOT.TH1F(s+'_mass',s+';mass (GeV)', 100, 0, 1000) )
    #############################################################################


    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):         
        print "Beginning on inputFile, writing new branches"
        self.out = wrappedOutputTree

        self.out.branch("eventWeight", "F")
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
        self.out.branch("SelectedLepton_eta",  "F")
        self.out.branch("SelectedLepton_iso",  "F")
        self.out.branch("mindRAK4_eta", "F")
        self.out.branch("mindRAK4_pT", "F")
        self.out.branch("Wlep_type",  "I")
        self.out.branch("Wlep_pt",  "F")
        self.out.branch("Wlep_mass",  "F")
        self.out.branch("dr_LepAK8",  "F")
        self.out.branch("dphi_LepAK8",  "F")
        self.out.branch("dphi_LepMet",  "F")
        self.out.branch("dphi_MetAK8",  "F")
        self.out.branch("dphi_WAK8"  ,  "F")
        self.out.branch("minAK4MetDPhi",  "F")
        
        
        self.out.branch("mindR_Lep_ClosestAK4nano",  "F")
        self.out.branch("pT_rel_Lep_AK4nano",  "F")
        
        self.out.branch("mindR_Lep_ClosestAK4",  "F")
        self.out.branch("pT_rel_Lep_AK4_nanostyle",  "F")
        self.out.branch("pT_rel_Lep_AK4_OG_TLV",  "F")
        
        
        self.out.branch("passingAK4_HT",  "F")
	self.out.branch("nSelectedAK4", "I")        
	self.out.branch("genmatchedAK8",  "I")
        self.out.branch("lheweight",  "F")
        self.out.branch("puweight",  "F")
        self.out.branch("topweight",  "F")
        self.out.branch("btagweight",  "F")
        self.out.branch("leptonweight",  "F")
        

        pass

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        print ("File closed successfully")
	print ("%f p.c. of %d events processed have passed the selection")%((self.nEventsPassed/(1.*self.nEventsProcessed)), self.nEventsProcessed)
        pass

    
    def leptonSF(self, lepton, leptonP4 ):

        if lepton.startswith("muon"): leptonP4eta = abs(leptonP4.eta)
        else: leptonP4eta = leptonP4.eta

        SFFileTrigger = ROOT.TFile( os.environ['CMSSW_BASE']+"/src/boostedWScalefactorProducer/Skimmer/data/leptonSF/"+self.leptonSFhelper[lepton]['Trigger'][0] )
        histoSFTrigger = SFFileTrigger.Get( self.leptonSFhelper[lepton]['Trigger'][1] )
        SFTrigger = histoSFTrigger.GetBinContent( histoSFTrigger.GetXaxis().FindBin( leptonP4.pt ), histoSFTrigger.GetYaxis().FindBin( leptonP4eta ) )

        SFFileID = ROOT.TFile( os.environ['CMSSW_BASE']+"/src/boostedWScalefactorProducer/Skimmer/data/leptonSF/"+self.leptonSFhelper[lepton]['ID'][0] )
        histoSFID = SFFileID.Get( self.leptonSFhelper[lepton]['ID'][1] )
        histoSFID_X = histoSFID.GetXaxis().FindBin( leptonP4.pt if self.leptonSFhelper[lepton]['ID'][2] else leptonP4eta )
        histoSFID_Y = histoSFID.GetYaxis().FindBin( leptonP4eta if self.leptonSFhelper[lepton]['ID'][2] else leptonP4.pt )
        SFID = histoSFID.GetBinContent( histoSFID_X, histoSFID_Y )
        SFID = SFID if SFID>0 else 1

        if self.year.startswith('2016') and lepton.startswith("muon"): leptonP4eta = leptonP4.eta   
        SFFileISO = ROOT.TFile( os.environ['CMSSW_BASE']+"/src/boostedWScalefactorProducer/Skimmer/data/leptonSF/"+self.leptonSFhelper[lepton]['ISO'][0] )
        histoSFISO = SFFileISO.Get( self.leptonSFhelper[lepton]['ISO'][1] )
        histoSFISO_X = histoSFISO.GetXaxis().FindBin( leptonP4.pt if self.leptonSFhelper[lepton]['ISO'][2] else leptonP4eta )
        histoSFISO_Y = histoSFISO.GetYaxis().FindBin( leptonP4eta if self.leptonSFhelper[lepton]['ISO'][2] else leptonP4.pt )
        SFISO = histoSFISO.GetBinContent( histoSFISO_X, histoSFISO_Y )
        SFISO = SFISO if SFISO>0 else 1

        return np.array([SFTrigger , SFID , SFISO])
    
    # Implementing https://github.com/ferencek/cms-MyAnalyzerDijetCode/blob/5bca32a7bb58a16abdb2c31b4c0379e6ffa27c91/MyAnalyzer_MainAnalysis_DijetBBTag_2011.cc#L1297 following recommendations on https://twiki.cern.ch/twiki/bin/viewauth/CMS/BTagSFMethods
    def getBTagWeight(self, nBTagged=0, jet_SFs=[0]): 
        bTagWeight=0
        if len(jet_SFs)>2 or nBTagged>2: 
            print "Error, only leading and subleading AK4 jets are considered: # of btagged jets cannot exceed 2"
        if nBTagged>len(jet_SFs): 
            print "Number of b-tagged jets cannot be greater than number of them for which SFs are provided!"
            return 0
        if nBTagged==0 and len(jet_SFs)==0: return 1
        
        if len(jet_SFs)==1:
            SF = jet_SFs[0]
            
            for i in range(0,2):
                if i!=nBTagged: continue
                bTagWeight+=pow(SF,i)*pow(1-SF,1-i)
        
        elif len(jet_SFs)==2:
            SF1, SF2 = jet_SFs[0], jet_SFs[1]
            for i in range(0,2):
                for j in range(0,2):
                    if (i+j)!=nBTagged: continue
                    bTagWeight+=pow(SF1,i)*pow(1-SF1,1-i)*pow(SF2,j)*pow(1-SF2,1-j)
        
        return bTagWeight
    
       
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        
        self.isMC = event.run == 1        
        #if self.nEventsProcessed%500==0: #print ("Analyzing events...", self.nEventsProcessed)
        self.nEventsProcessed+=1
        #if (self.nEventsProcessed > 20000): return False
        
        passRecoSel = self.boostedWSelection( event )
        
        #### Debugging block (TODO: remove)
        '''
        if passRecoSel==True:
            #self.out.fillBranch( 'eventCategory', 1 )
	    #if (self.nEventsProcessed < 20000): 
                #print ("Event %d passed the selection!"%self.nEventsProcessed)
		if not self.nEventsProcessed == 0: print ("So far %f events have passed selection")%(self.nEventsPassed/(1.*self.nEventsProcessed))
            #WEIGHT =  self.totalEventWeight
            return True
        else: 
	    #self.out.fillBranch('eventCategory', 0)
	    #if (self.nEventsProcessed < 20000 and self.nEventsProcessed%100==0): 
            #print ("Event %d failed the selection!"%self.nEventsProcessed)
	    return False
        '''
        return passRecoSel
        
    def boostedWSelection(self, event):
        '''Analyzing reco-level objects'''
        '''Encapsulating selections, and objects stored/returned thereafter into one function'''
        #passSelection = False
	
        FatJets = list(Collection(event, "FatJet"))
        allelectrons = list(Collection(event, 'Electron'))
        allmuons = list(Collection(event, 'Muon'))
	Jets = list(Collection(event, "Jet")) #AK4 
        met = Object(event, 'MET')        

        if self.isMC: 
	    puweight = event.puWeight
            genweight = event.genWeight
	else: 
	    puweight = 1.
            genweight = 1.

        lheweight = 1.
	topweight = 1.
        btagweight = 1.
        leptonweight = 1.

   
	if not (event.nMuon > 0 or event.nElectron > 0): return False 
        if not event.nFatJet > 0: return False                               

        
        ### Find high-pT lepton, veto additional leptons, check trigger ###

        # Make some loose lepton selections; including loose pT cuts for veto
        electrons = [x for x in allelectrons if x.pt > 40. and x.cutBased >= 2 and ( abs(x.eta) < 1.44 or ( abs(x.eta) > 1.56 and abs(x.eta) < 2.5 ) )] 
        muons     = [x for x in allmuons if x.pt > 40. and x.looseId and abs(x.eta) < self.maxMuEta]# and x.pfIsoId >= 2] 

        # Ordering the loosely selected categories according to Pt 
        muons.sort(key=lambda x:x.pt,reverse=True)
        electrons.sort(key=lambda x:x.pt,reverse=True)

        # Check if the muon or electron with highest pT passes the tight selection (additional cuts to the loose selection)
        electronTight = len(electrons) > 0 and electrons[0].pt > self.minElpt and electrons[0].cutBased >= 4  

        muonTight = len(muons) > 0 and muons[0].pt > self.minMupt and abs(muons[0].eta) < self.maxMuEta and muons[0].highPtId >= 2 and muons[0].isPFcand# and muons[0].pfIsoId >= 6


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

        if ("mu" in self.chan and muonTight and (len(muons) == 1) and (len(electrons) == 0)) :  
	# There is one tight muon and no other loose electron or muon 

       	    triggerEl = 0 
            #if not triggerMu: return False
            self.Vlep_type = 0
            lepton = muons[0]#.p4()
            iso = muons[0].pfRelIso03_all
            
        elif ("el" in self.chan and electronTight and (len(electrons) == 1) and (len(muons) == 0)) :  
	# There is a tight electron and no other loose muon or electron
          
	    triggerMu = 0
            #if not triggerEl: return False
            self.Vlep_type = 1
            lepton = electrons[0]#.p4()
            iso = electrons[0].pfRelIso03_all
	    # TODO: Add this to the SpecificYearConfig (class and config file)

        else : 
          return False 


        # Apply MET cut; METFilter check now done in job submission script w/ pre-filtering of events
        met = Object(event, "MET")
	if self.Vlep_type == 0 and met.sumEt < self.minMuMETPt : return False # Muons = 0
	if self.Vlep_type == 1 and met.sumEt < self.minElMETPt : return False # Electrons = 1
        
	MET  = ROOT.TLorentzVector()
        MET.SetPtEtaPhiE(met.pt, 0., met.phi, met.sumEt)
        
        # Apply leptonic W cut
        WcandLep = lepton.p4() + MET
        
	'''
	## TODO: Check why this was being done explicitly?
        pz = recoverNeutrinoPz(lepton, MET)
        neutrino  = ROOT.TLorentzVector()
        neutrino.SetPxPyPzE(MET.Px(), MET.Py(), pz, math.sqrt(MET.Px()**2 + MET.Py()**2 + pz**2))
        WcandLep = lepton + neutrino
        '''

        if not WcandLep.Pt() > self.minLepWPt: return False   
	
        # Find fat jet
        recoAK8 = [ x for x in FatJets if x.p4().Perp() >=self.minAK8JetPt and  abs(x.p4().Eta()) < self.maxAK8JetEta and x.msoftdrop > self.minSDMassW and x.msoftdrop<self.maxSDMassW and x.tau1 > 0. and x.tau2 > 0.]
        if not len(recoAK8) > 0: return False
        recoAK8.sort(key=lambda x:x.pt,reverse=True)
	
	jetAK8_4v = ROOT.TLorentzVector()
	jetAK8_4v.SetPtEtaPhiM(recoAK8[0].pt,recoAK8[0].eta,recoAK8[0].phi,recoAK8[0].mass)
        
	# Require at least 2 AK4 jets in event and at least one b-tagged one that passes the DeepJet/DeepFlavB medium working point; before b-tagging and removing non-b-tagged jets, check if the HT of all AK4's passing the minimal pT/eta selection is greater than 250 GeV
        # Check if the custom isolation requirement ofthe nearest AK4 to the lepton:  dR(lep, jet) > 0.4 or pT_rel (lep, AK4)>25 (implemented here for el/mu/elmu channels) [all selections as per CMS-JME-18-002]
        recoAK4 = [ x for x in Jets if x.p4().Perp() > self.minAK4JetPt and abs(x.p4().Eta()) < self.maxAK4JetEta]# and jetAK8_4v.DeltaR(x.p4())>1.0]
        if not len(recoAK4) > 1: return False 
        
	# Require scalar sum of pT of all AK4 jets in the event(i.e., H_T) to be greater than 250 GeV 
	recoAK4_HT = 0. 
	for x in recoAK4: recoAK4_HT+=x.p4().Perp()
	if not recoAK4_HT > 250.: return False

	minAK4MetDPhi = min([ abs(x.p4().DeltaPhi(MET)) for x in recoAK4]) if len(recoAK4) >= 1 else -1.
	        

        #To progress further, keeping the non-btagged AK4 jet(s) is not necessary; so we drop them requiring that at least one of the AK4 jets remaining is b-tagged 
	recoAK4 = [ x for x in recoAK4 if x.btagDeepFlavB > self.minBDisc]
	if not len(recoAK4) > 0: return False
	
	
        #Custom isolation for single muon samples as per CMS-JME-18-002, but extending to prompt electrons as well since FS topology is the same
	#lep4D = convMathLV(lepton)
	
	mindRLepAK4nano = min([lepton.p4().DeltaR(x.p4()) for x in recoAK4])
       	pT_relnano = lepton.jetPtRelv2 
       	
       	#Custom isolation for single muon samples as per CMS-JME-18-002, but extending to prompt electrons as well since FS topology is the same
	mindRLepAK4 = lepton.p4().DeltaR(recoAK4[0].p4())
        pT_rel = 0.
        
        mindRLepAK4_TLV = lepton.p4().DeltaR(recoAK4[0].p4())
        pT_rel_TLV = 0.
       

        for x in recoAK4:
            jetAK4_4v = ROOT.TLorentzVector()
            jetAK4_4v.SetPtEtaPhiM(x.pt,x.eta,x.phi,x.mass)
            #jetAK4_4v = convMathLV(x)
        
            if lepton.p4().DeltaR(x.p4()) < mindRLepAK4:
                mindRLepAK4 = lepton.p4().DeltaR(x.p4())
                #pT_rel = lep4D.Vect().Cross((jetAK4_4v - lep4D).Vect().Unit()).R() 
                pT_rel = lepton.p4().Vect().Cross((x.p4() - lepton.p4()).Vect().Unit()).Mag() #DOES NOT WORK
                pT_rel_TLV = (lepton.p4()).Perp(jetAK4_4v.Vect())
		
	#################################################################
        	#also include calc by hand to compare pt_rels# 
	#################################################################
        #2D custom isolation cut: dr_min(lep,AK4) > 0.4 OR pT_rel(lep,jet)>25. for AK4 closest to lepton 	
	
	
	#if not (mindRLepAK4 > 0.4 or pT_rel > 25.): 
	#    return False        
	
	# to prevent angular overlap between leptons and the AK8
        if not abs(jetAK8_4v.DeltaPhi(lepton.p4())>2.): 
            return False 
        
	#print (mindRLepAK4nano, pT_relnano)
	#print (mindRLepAK4, pT_rel)
        #print (mindRLepAK4, pT_rel_TLV, "\n")
	
	
		
      	# Obtain btag SFs for calculating b-tagging event weights
	# Jet_btagSF_ALGO_shape -> relevant naming convention for SF branch added to the 'Jet' collection from NanoAODTools::BTagSFProducer module [https://github.com/cms-nanoAOD/nanoAOD-tools/blob/master/python/postprocessing/modules/btv/btagSFProducer.py]
	if len(recoAK4)>2: return False # b-tag weight calculator can handle at most two b-jets, for now (more shouldn't be required to be handled in this decay mode anyway...)
	if self.isMC: bTagSFs =  [x.btagSF_deepjet_shape for x in recoAK4]         

	#### Weight calculation from genweights, lepton wt., b-tagging event wt., PU wt.
        if self.isMC: 
            if len(muons)>0: leptonweight = self.leptonSF( "muon", muons[0] )
	    elif len(electrons)>0: leptonweight = self.leptonSF( "electron", electrons[0] )
            else: leptonweight = np.array([0., 0., 0.])
        else: leptonweight = np.array([1., 1., 1.])

        if self.isMC:
	    #obtain b-tagging event weight from per jet SFs
            btagweight = self.getBTagWeight(nBTagged=len(recoAK4), jet_SFs=bTagSFs) 
	    #combining all weights
            weight =  np.prod(leptonweight) * btagweight * puweight *  genweight 
            
        else:
            weight = 1.
        self.totalEventWeight = weight
    
        if self.isMC:
            try:
                if event.LHEWeight_originalXWGTUP < 0.: lheweight = -1.
            except:
                pass
	
        # Gen
        self.isW = 0
        if self.isMC:

       	    #### Matching AK8 to gen-level hadronically decaying, boosted W
            ### Look at generator level particles
            ### find events where a W decays to two partons 
            
            gens = Collection(event, "GenPart")
            Wdaus =  [x for x in gens if x.pt>1 and 0<abs(x.pdgId)<9]
            Ws =  [x for x in gens if x.pt>10 and abs(x.pdgId)==24]

            TWdaus =  [x for x in gens if x.pt>1 and  0<abs(x.pdgId)<4]
            Tdaus =  [x for x in gens if x.pt>1 and (abs(x.pdgId)==5  or  abs(x.pdgId)==24 )]
            Top =  [x for x in gens if x.pdgId==6]
            AntiTop =  [x for x in gens if x.pdgId==-6]
            
            realVs = []
            realVdaus = []

            realTs = []
            realWs = []
            realqs = []
            self.matchedJ = 0
            #self.matchedSJ = 0

            if len(Ws)>0 and len(Wdaus)>0:
              for dau in Wdaus:
                for mom in Ws:
                  try:
                    if mom == gens[dau.genPartIdxMother]: 
                      realVs.append(mom)
                      realVdaus.append(dau)    
                  except:
                    continue    
            

            if len(Top)>0 and len(AntiTop)>0:
                topSF = math.exp(0.0615 - 0.0005 * Top[0].pt) #where are these numbers coming from?
                antitopSF = math.exp(0.0615 - 0.0005 * AntiTop[0].pt)
                topweight = math.sqrt(topSF*antitopSF)
                
        
        # Check if matched to genW and genW daughters
        self.isW = 0

        if self.isMC == False:
            genjets = [None] * len(recoAK8)

        else:
             
            # standard gen matching   
	    for V in realVs:
            	gen_4v = ROOT.TLorentzVector()
                gen_4v.SetPtEtaPhiM(V.pt,V.eta,V.phi,V.mass)
                dR = jetAK8_4v.DeltaR(gen_4v)
                if dR < 0.6: # changed from 0.8 for tighter matching criterion (as per CMS-JME-18-002)
                    nDau = 0
                    for v in realVdaus:
                        gen_4v = ROOT.TLorentzVector()
                	gen_4v.SetPtEtaPhiM(v.pt,v.eta,v.phi,v.mass)
                	dR = jetAK8_4v.DeltaR(gen_4v)
                	if dR < 0.6: # changed from 0.8 for tighter matching criterion (as per CMS-JME-18-002)
                  	    nDau +=1                 
                  	    self.isW = 1
        
        #Fill output branches
	#getattr(self, 'mindRlepAK4_etas').Fill(lepton.p4().Eta(), jetAK4_4v.Eta() )
	getattr(self, 'pT_rel_dR_lepAK4_nanostyle').Fill(pT_rel, mindRLepAK4)
	getattr(self, 'pT_rel_dR_lepAK4_OG_TLV').Fill(pT_rel_TLV, mindRLepAK4)
	getattr(self, 'pT_rel_dR_lepAK4nano').Fill(pT_relnano, mindRLepAK4nano)
	#self.out.fillBranch("mindRAK4_eta", jetAK4_4v.Eta())
        #self.out.fillBranch("mindRAK4_pT", jetAK4_4v.Pt())
     
	self.out.fillBranch("mindR_Lep_ClosestAK4nano",  mindRLepAK4nano)
        self.out.fillBranch("pT_rel_Lep_AK4nano",  pT_relnano)
        
        self.out.fillBranch("mindR_Lep_ClosestAK4",  mindRLepAK4)
        self.out.fillBranch("pT_rel_Lep_AK4_nanostyle",  pT_rel)
        self.out.fillBranch("pT_rel_Lep_AK4_OG_TLV",  pT_rel_TLV)
        
        self.out.fillBranch("passingAK4_HT",  recoAK4_HT)
        self.out.fillBranch("genmatchedAK8",  self.isW)
	self.out.fillBranch("eventWeight", self.totalEventWeight)
        self.out.fillBranch("puweight", puweight )
        self.out.fillBranch("btagweight", btagweight )
        self.out.fillBranch("leptonweight", np.prod(leptonweight) )
        self.out.fillBranch("topweight", topweight )
        self.out.fillBranch("lheweight", lheweight )
	self.out.fillBranch("nSelectedAK4", len(recoAK4))        
        #self.out.fillBranch("passedMETfilters", passedMETFilters)
        self.out.fillBranch("dr_LepAK8"  , lepton.p4().DeltaR(jetAK8_4v))
        self.out.fillBranch("dphi_LepAK8", abs(jetAK8_4v.DeltaPhi(lepton.p4())))
        self.out.fillBranch("dphi_LepMet", abs(lepton.p4().DeltaPhi(MET)))
        self.out.fillBranch("dphi_MetAK8", abs(jetAK8_4v.DeltaPhi(MET)))
        self.out.fillBranch("dphi_WAK8"  , abs(jetAK8_4v.DeltaPhi(WcandLep)))
        self.out.fillBranch("minAK4MetDPhi", minAK4MetDPhi )
        self.out.fillBranch("Wlep_type",self.Vlep_type)
        self.out.fillBranch("Wlep_pt", WcandLep.Pt() )
        self.out.fillBranch("Wlep_mass", WcandLep.M() )
        
        self.out.fillBranch("SelectedJet_softDrop_mass",  recoAK8[0].msoftdrop)
        self.out.fillBranch("SelectedJet_pt",   recoAK8[0].pt)
        self.out.fillBranch("SelectedJet_eta",  recoAK8[0].eta)
        self.out.fillBranch("SelectedJet_mass",  recoAK8[0].mass)
        self.out.fillBranch("SelectedLepton_pt", lepton.pt)
        self.out.fillBranch("SelectedLepton_eta", lepton.eta)
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
        
	
	self.nEventsPassed+=1
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
            ##print event.event, q.pdgId, genParticles[q.genPartIdxMother].pdgId, q.p4().Pt()
            if recoJet.p4().DeltaR( q.p4() )<0.3: listMatched.append( True )
            else: listMatched.append( False )

        if (len(listMatched)==4) and all(listMatched[:2]) and not all(listMatched[2:]): boosted = 2  ## only boostedW
        elif (len(listMatched)==4) and all(listMatched[:2]) and any(listMatched[2:]): boosted = 4      ## boosted Top
        else: boosted = 0
        ##print listMatched, boosted

        return boosted
    
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
            #print ' %3d : %s' % ( ic, s )
            

###################### Different gen functions

def convMathLV(particleTLV):
    particle4D = ROOT.Math.LorentzVector()
    particle4D.SetPt(particleTLV.pt)
    particle4D.SetEta(particleTLV.eta)
    particle4D.SetPhi(particleTLV.phi)
    particle4D.SetM(particleTLV.mass)
    return particle4D

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
