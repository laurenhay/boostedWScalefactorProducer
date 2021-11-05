import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection,Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import *
from boostedWScalefactorProducer.Skimmer.PileupWeightTool import *
from boostedWScalefactorProducer.Skimmer.variables import recoverNeutrinoPz

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

algNames = [
    "sdB0", "sdB1", "sdB0Z0p05", "sdB1Z0p05", "sdB0Z0p15", "sdB1Z0p15"
]
         
class Skimmer(Module):
    def __init__(self, channel, leptonSF={}, year='2017'):
        self.chan = channel
        self.writeHistFile = True
        self.verbose = False
        self.year = year
        self.leptonSFhelper = leptonSF

        self.minMupt = 55.
        self.maxMuEta = 2.4
        self.maxRelIso = 0.15
        self.minMuMETPt = 50.

        #remove  AK8 jet within 1.0 of lepton
        self.mindRLepJet = 1.0 
       
        self.minElpt = 120.
        self.minElMETPt = 80.
     
        self.minLepWPt = 150.

        self.minJetPt = 200.
        self.maxJetEta = 2.5
        
        self.minWPt = 150.

        self.minBDisc = 0.8838
        ### Medium https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X

        #>= 1 CSVmedium akt4 jet
        self.minAK4Pt = 30.

        #Angular selection (to be implemented later, in fitting code):
        #dR( lepton, leading AK8 jet) > pi/2
        #dPhi(leading AK8 jet, MET) > 2
        #dPhi (leading AK8 jet, leptonic W) >2
        #self.minDPhiWJet = 2.  
        
        self.totalEventWeight = 1
        self.nEventsProcessed=0
        self.nEventsPassed = 0

    def beginJob(self, histFile, histDirName):

        ROOT.gSystem.Load("libPhysicsToolsNanoAODJMARTools.so")

        self.sdB0Z0p05 = ROOT.SoftDropWrapper(0. ,0.05, 0.8, self.minJetPt)
        self.sdB0 = ROOT.SoftDropWrapper(0. ,0.1, 0.8, self.minJetPt)
        self.sdB0Z0p15 = ROOT.SoftDropWrapper(0. ,0.15, 0.8, self.minJetPt)

        self.sdB1Z0p05 = ROOT.SoftDropWrapper(1. ,0.05, 0.8, self.minJetPt)
        self.sdB1 = ROOT.SoftDropWrapper(1. ,0.1, 0.8, self.minJetPt)
        self.sdB1Z0p15 = ROOT.SoftDropWrapper(1. ,0.15, 0.8, self.minJetPt)

        self.algsToRun = [ self.sdB0, self.sdB1, self.sdB0Z0p05, self.sdB1Z0p05, self.sdB0Z0p15, self.sdB1Z0p15 ]
        self.algNames = [
            "sdB0", "sdB1", "sdB0Z0p05", "sdB1Z0p05", "sdB0Z0p15", "sdB1Z0p15"
        ]

        Module.beginJob(self, histFile, histDirName)
        self.nEventsProcessed=0
        print ('Beginning job, current nEventsProcessed=%d'%self.nEventsProcessed)

    def endJob(self):
        Module.endJob(self)
        print "Module ended successfully,", self.nEventsProcessed, "events analyzed"
        pass
        
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
         self.out = wrappedOutputTree
         self.out.branch("eventWeight", "F")
         self.out.branch("SelectedJet_softDrop_mass",  "F")
         for ialg,alg in enumerate(self.algsToRun):
            self.out.branch("SelectedJet_"+self.algNames[ialg]+"_mass", "F")
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
         #self.out.branch("HT_HEM1516",  "F")
         self.out.branch("genmatchedAK8",  "I")
         self.out.branch("genmatchedAK8Quarks",  "I")
         self.out.branch("genmatchedAK8Subjet",  "I")
         self.out.branch("genmatchedAK82017",  "I")
         self.out.branch("AK8Subjet0isMoreMassive",  "I")
         self.out.branch("lheweight",  "F")
         self.out.branch("puweight",  "F")
         self.out.branch("topweight",  "F")
         self.out.branch("btagweight",  "F")
         self.out.branch("leptonweight",  "F")

         pass

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        print "File closed successfully"
        print ("%f p.c. of %d events processed have passed the selection")%((self.nEventsPassed/(1.*self.nEventsProcessed)), self.nEventsProcessed)
        pass

    def leptonSF(self, lepton, leptonP4 ):

        leptonP4eta = abs(leptonP4.eta)
        leptonP = ROOT.TMath.Sqrt(leptonP4.p4().Px()**2 + leptonP4.p4().Py()**2 + leptonP4.p4().Pz()**2)

        SFFileTrigger = ROOT.TFile( os.environ['CMSSW_BASE']+"/src/data/"+self.leptonSFhelper[lepton]['Trigger'][0] )
        histoSFTrigger = SFFileTrigger.Get( self.leptonSFhelper[lepton]['Trigger'][1] )
        SFTrigger = histoSFTrigger.GetBinContent( histoSFTrigger.GetXaxis().FindBin( leptonP4eta ), histoSFTrigger.GetYaxis().FindBin( leptonP4.pt ) )

        SFFileID = ROOT.TFile( os.environ['CMSSW_BASE']+"/src/data/"+self.leptonSFhelper[lepton]['ID'][0] )
        histoSFID = SFFileID.Get( self.leptonSFhelper[lepton]['ID'][1] )
        histoSFID_X = histoSFID.GetXaxis().FindBin( leptonP4eta)
        histoSFID_Y = histoSFID.GetYaxis().FindBin( leptonP4.pt )
        SFID = histoSFID.GetBinContent( histoSFID_X, histoSFID_Y )
        SFID = SFID if SFID>0 else 1

        SFFileISO = ROOT.TFile( os.environ['CMSSW_BASE']+"/src/data/"+self.leptonSFhelper[lepton]['ISO'][0] )
        histoSFISO = SFFileISO.Get( self.leptonSFhelper[lepton]['ISO'][1] )
        histoSFISO_X = histoSFISO.GetXaxis().FindBin( leptonP4eta )
        histoSFISO_Y = histoSFISO.GetYaxis().FindBin( leptonP4.pt )
        SFISO = histoSFISO.GetBinContent( histoSFISO_X, histoSFISO_Y )
        SFISO = SFISO if SFISO>0 else 1

        # SFFileRecoEff = ROOT.TFile( os.environ['CMSSW_BASE']+"/src/data/"+self.leptonSFhelper[lepton]['RecoEff'][0] )
        # histoSFRecoEff = SFFileRecoEff.Get( self.leptonSFhelper[lepton]['RecoEff'][1] )      
        # histoSFRecoEff_X = histoSFRecoEff.GetXaxis().FindBin( leptonP4eta ) 
        # histoSFRecoEff_Y = histoSFRecoEff.GetYaxis().FindBin( leptonP ) 
        # SFRecoEff = histoSFRecoEff.GetBinContent( histoSFRecoEff_X, histoSFRecoEff_Y )       
        # SFRecoEff = SFRecoEff if SFRecoEff>0 else 1 
        SFRecoEff = 1.

        #print (SFTrigger * SFID * SFISO), SFTrigger , SFID , SFISO, leptonP4.pt, leptonP4.eta
        return [SFTrigger , SFID , SFISO, SFRecoEff]

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
        self.nEventsProcessed+=1
        if self.nEventsProcessed%500==0: print ("Analyzing events...", self.nEventsProcessed) 

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

        
        # Find high-pT lepton, veto additional leptons, check trigger
        allmuons = Collection(event, "Muon")
        allelectrons = Collection(event, "Electron")

        # Here we make some loose selections for each category 
        electrons = [x for x in allelectrons if x.pt > 10. and x.cutBased >= 2 and ( abs(x.eta) < 1.44 or ( abs(x.eta) > 1.56 and abs(x.eta) < 2.5 ) )] #loose pt cut for veto 
        muons     = [x for x in allmuons if x.pt > 10. and x.isPFcand and (x.isTracker or x.isGlobal) and abs(x.eta) < self.maxMuEta and x.pfIsoId >= 2] #loose pt cut for veto
        
        # Ordening the loosely selected categories according to Pt 
        muons.sort(key=lambda x:x.pt,reverse=True)
        electrons.sort(key=lambda x:x.pt,reverse=True)

        # Check if the muon or electron with highest Pt passes the tight selection (additional cuts to the loose selection)
        electronTight = len(electrons) > 0 and electrons[0].pt > 55. and electrons[0].cutBased >= 4  #and abs(electrons[0].eta) < 2.5 and not (abs(electrons[0].eta) > 1.44 and abs(electrons[0].eta) < 1.56)
        muonTight = len(muons) > 0 and muons[0].pt > 55. and abs(muons[0].eta) < self.maxMuEta and muons[0].highPtId >= 2 and muons[0].isPFcand and muons[0].pfIsoId >= 6


        possibleChannels = ["mu", "el", "elmu"]

        if self.chan not in possibleChannels : 
          print "Channel not defined! Skipping"
          print "Please select a channel in the following: "
          print possibleChannels
          return False

        
        # We require one and only one tight muon and no electron (loose) or one and only one tight electron and no (loose) muon 
        self.Vlep_type = -1
        lepton = ROOT.TLorentzVector()
        iso = 0.

        if ("mu" in self.chan and muonTight and (len(muons) == 1) and (len(electrons) == 0)) :  # There is one tight muon and no other loose electron or muon 
          triggerEl = 0
          #if not triggerMu: return False
          self.Vlep_type = 0
          lepton = muons[0].p4()
          iso = muons[0].miniPFRelIso_all

        elif ("el" in self.chan and electronTight and (len(electrons) == 1) and (len(muons) == 0)) :  # There is a tight electron and no other loose muon or electron
          triggerMu = 0
          #if not triggerEl: return False
          self.Vlep_type = 1
          lepton = electrons[0].p4()
          iso = electrons[0].pfRelIso03_all

        else : 
          return False 
        
        # Apply MET cut    
        met = Object(event, "MET")
        if self.Vlep_type == 0 and met.sumEt < self.minMuMETPt : return False
        if self.Vlep_type == 1 and met.sumEt < self.minElMETPt : return False
        
        # Apply leptonic W cut
        MET  = ROOT.TLorentzVector()
        MET.SetPtEtaPhiE(met.pt, 0., met.phi, met.pt)
        WcandLep = lepton + MET
        if WcandLep.Pt() < self.minLepWPt :
             return False

        #Get AK8 jet constituents
        allrecoparts = list(Collection(event, "PFCandsAK8"))
        recoCandsPUPPIweightedVec = ROOT.vector("TLorentzVector")()
        for p in allrecoparts :
            pw =  p.puppiWeight
            tp = ROOT.TLorentzVector(p.p4().Px(), p.p4().Py(), p.p4().Pz(), p.p4().E())
            tp = tp * pw
            recoCandsPUPPIweightedVec.push_back(tp)
     
        # Find fat jet
        FatJets = list(Collection(event, "FatJet"))
        recoAK8 = [ x for x in FatJets if x.p4().Perp() > self.minJetPt and  abs(x.p4().Eta()) < self.maxJetEta and x.tau1 > 0. and x.tau2 > 0. and (x.jetId>=2) and abs(x.p4().DeltaPhi(lepton.p4()))>2.]
        if not len(recoAK8) > 0: return False
        recoAK8.sort(key=lambda x:x.pt,reverse=True)

        jetAK8_4v = ROOT.TLorentzVector()
        jetAK8_4v.SetPtEtaPhiM(recoAK8[0].pt,recoAK8[0].eta,recoAK8[0].phi,recoAK8[0].mass)
        
        # #Recluster jets with alternate softdrop settings
        # # Cluster only the particles near the appropriate jet to save time
        recojetsGroomedAK8_4v = {}
        constituents = ROOT.vector("TLorentzVector")()

        jecNomVal = recoAK8[0].corr_JEC
           
        for x_cands in recoCandsPUPPIweightedVec:
            if recoAK8[0].p4().DeltaR( x_cands ) < 0.8:
                constituents.push_back(x_cands)
        for ialg,alg in enumerate(self.algsToRun):
            groomedjetsFJ = alg.result( constituents )
            groomedjets = [ ROOT.TLorentzVector( x.px(), x.py(), x.pz(), x.e() ) for x in groomedjetsFJ]
            if len(groomedjets) > 0 :
                recojetsGroomedAK8_4v[ialg] = groomedjets[0]*jecNomVal
            else:
                print 'Grooming failed. Inputs are:'
                self.printCollection( constituents )
                recojetsGroomedAK8_4v[ialg] = None
        
        #Check for additional b-jet in the event, apply CSV later!
        Jets = list(Collection(event, "Jet")) 
        recoAK4 = [ x for x in Jets if x.p4().Perp() > self.minAK4Pt and abs(x.p4().Eta()) < self.maxJetEta and jetAK8_4v.DeltaR(x.p4())>1.0] #x.btagCSVV2 > self.minBDisc
#        if len(recoAK4) < 1: return False
        
        # max and second max AK4 CSV
        bTagValues = [ x.btagCSVV2 for x in recoAK4]
        maxAK4CSV = -1.
        subMaxAK4CSV = -1.

        if len(bTagValues) >= 1 : 
          maxAK4CSV = max(bTagValues)

        if len(bTagValues) >= 2 : 
          bTagValues.remove(maxAK4CSV)
          subMaxAK4CSV = max(bTagValues) # max([ x.btagCSVV2 for x in [z for z in recoAK4 if z != maxAK4CSV]])
          
        
        minJetMetDPhi = min([ abs(x.p4().DeltaPhi(MET)) for x in recoAK4]) if len(recoAK4) >= 1 else -1.
        

        # HT_HEM1516 = 0.
        # for j in Jets:
        #     if j.eta > -3.0 and j.eta < -1.3 and j.phi > -1.57 and j.phi < -0.87:
        #         HT_HEM1516 += j.pt

        if self.isMC:
            try:
                if event.LHEWeight_originalXWGTUP < 0.: lheweight = -1.
            except:
                pass

            if len(muons)>0:
                leptonweight = self.leptonSF( "muon", muons[0] )
            elif len(electrons)>0:
                leptonweight = self.leptonSF( "electron", electrons[0] )
            else: leptonweight = np.array([0., 0., 0., 0.])
            btagweight = event.btagWeight_CSVV2
            weight =  np.prod(leptonweight) * btagweight * puweight *  genweight

        else:
            leptonweight = np.array([1., 1., 1., 1.])
            weight = 1.
        self.totalEventWeight = weight
        
        # Gen
        self.isW = 0
        self.isWqq = 0
        self.matchedJ = 0
        self.matchedSJ = 0
        
        if self.isMC:
            ### Look at generator level particles
            ### find events where :
            ### a W decays to quarks (Type 1 - partially merged)
            ###    OR
            ### a Top decays to W + b (Type 2 - fully merged top quark)
            gens = Collection(event, "GenPart")
            Wdaus =  [x for x in gens if x.pt>1 and 0<abs(x.pdgId)<9]
            Wmoms =  [x for x in gens if x.pt>10 and abs(x.pdgId)==24]

            TWdaus =  [x for x in gens if x.pt>1 and  0<abs(x.pdgId)<4]
            Tdaus =  [x for x in gens if x.pt>1 and (abs(x.pdgId)==5  or  abs(x.pdgId)==24 )]
            Tmoms =  [x for x in gens if x.pt>10 and abs(x.pdgId)==6] 
            Top =  [x for x in gens if x.pdgId==6]
            AntiTop =  [x for x in gens if x.pdgId==-6]
            
            realVs = []
            realVdaus = []

            realTs = []
            realWs = []
            realqs = []
            self.matchedJ = 0
            self.matchedSJ = 0

            if len(Wmoms)>0 and len(Wdaus)>0:
              for dau in Wdaus:
                for mom in Wmoms:
                  try:
                    if mom == gens[dau.genPartIdxMother]: 
                      realVs.append(mom)
                      realVdaus.append(dau)    
                  except:
                    continue    
            
            if len(Top)>0 and len(AntiTop)>0:
                topSF = math.exp(0.0615 - 0.0005 * Top[0].pt)
                antitopSF = math.exp(0.0615 - 0.0005 * AntiTop[0].pt)
                topweight = math.sqrt(topSF*antitopSF)
                
        
        # Check if matched to genW and genW daughters
        #for partially merged:
        self.isW = 0
        if self.isMC == False:
            genjets = [None] * len(recoAK8)

        else :
          # legacy 2017 gen matching 
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
                if dR < 0.8: 
                  nDau +=1                 
              if nDau >1: self.isW = 1
              else: self.isW = 0
       
        #for fully merged:
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
                if self.isMC and WHadreco != None and self.SJ0isW >= 0 :
                      
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
        self.out.fillBranch("genmatchedAK8Subjet", self.matchedSJ)
        self.out.fillBranch("AK8Subjet0isMoreMassive", self.SJ0isW )
        self.out.fillBranch("puweight", puweight )
        self.out.fillBranch("btagweight", btagweight )
        self.out.fillBranch("triggerweight", triggerweight )
        self.out.fillBranch("topweight", topweight )
        self.out.fillBranch("lheweight", lheweight )
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
        #self.out.fillBranch("HT_HEM1516", HT_HEM1516 )
        self.out.fillBranch("SelectedJet_softDrop_mass",  recoAK8[0].msoftdrop)
        for ialg,alg in enumerate(self.algsToRun):
            if recojetsGroomedAK8_4v[ialg] != None : self.out.fillBranch("SelectedJet_"+self.algNames[ialg]+"_mass", recojetsGroomedAK8_4v[ialg].M())
        else : self.out.fillBranch("SelectedJet_"+self.algNames[ialg]+"_mass", -1.0)
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
        
        self.nEventsPassed += 1
        if self.nEventsPassed % 1000 == 0: print "Filled event", self.nEventsPassed
        
        
        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
ttbar_semilep = lambda : Skimmer(Channel="elmu") 
