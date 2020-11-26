import ROOT,sys
from WTopScalefactorProducer.Fitter.tdrstyle import *
import  WTopScalefactorProducer.Fitter.CMS_lumi as CMS_lumi
from WTopScalefactorProducer.Skimmer.getGenEv import getGenEv
setTDRStyle()
from time import sleep
import os
import numpy as np
import MC_scalings

ROOT.gROOT.SetBatch(True)
lumi = 43.024 #*0.024

ttbarSF = 1.
wjetsSF = 1.

CMS_lumi.lumi_13TeV = "%.1f fb^{-1} (2018)" % lumi
CMS_lumi.writeExtraText = 1
CMS_lumi.extraText = "Preliminary"
CMS_lumi.lumi_sqrtS = "13 TeV"
iPos = 11
if( iPos==0 ): CMS_lumi.relPosX = 0.12
iPeriod = 4 #iPeriod = 0 for simulation-only plots


#cut = "(SelectedJet_tau21_ddt_retune<0.57)"
#cut = "(abs(dr_LepJet)>1.5708&&abs(dphi_MetJet)>2.&&abs(dphi_WJet)>2&&Wlep_type==0&&SelectedJet_tau21<0.40)"
#cut = "(1==1)"
#cut = "(passedMETfilters&&abs(dr_LepJet)>1.5708&&abs(dphi_MetJet)>1.5708&&Muon_highPtId[0]>=2&&Muon_isPFcand[0]&&Muon_pfIsoId[0]>=6&&W_pt>150.&&maxAK4CSV<0.8484)"
cut = "Wlep_type==0" # && SelectedJet_softDrop_mass > 50. && SelectedJet_softDrop_mass < 130. && SelectedJet_pt > 200. && SelectedJet_pt < 10000.)"
#vars = ["SelectedJet_softDrop_mass","SelectedJet_tau21", "SelectedJet_tau21_ddt", "SelectedJet_tau21_ddt_retune", "FatJet_pt[0]","FatJet_eta[0]","FatJet_phi[0]","FatJet_tau1[0]","FatJet_tau2[0]","FatJet_tau3[0]","FatJet_mass[0]","FatJet_msoftdrop[0]","SelectedLepton_pt","SelectedLepton_iso","maxAK4CSV","nFatJet", "nJet", "nMuon","PV_npvs","W_pt","MET_pt","fabs(dphi_WJet)","fabs(dphi_MetJet)","fabs(dphi_LepJet)","dr_LepJet"]
vars = ["SelectedJet_tau21"] #"SelectedJet_softDrop_mass"
#vars = ["SelectedJet_tau21", "FatJet_pt[0]", "W_pt", "SelectedJet_softDrop_mass","SelectedJet_tau21", "SelectedJet_tau21_ddt", "SelectedJet_tau21_ddt_retune"] 
#vars += [ "Muon_pt[0]", "Muon_pfRelIso03_all[0]" ]
#vars += ["Electron_eta[0]", "Electron_phi[0]", "Electron_pt[0]", "Electron_pfRelIso03_all[0]"]


#Data infile
datas   = ["SingleMuon_B_2017UL.root", 
"SingleMuon_C_2017UL.root", 
"SingleMuon_D_2017UL.root", 
"SingleMuon_E_2017UL.root", 
"SingleMuon_F_2017UL.root"]

#MC infiles
bkgs = []
STs   = [#"ST_s-channel_madgraph_pythia8_2017UL.root", 
"ST_s-channel_amcatnlo_pythia8_2017UL.root", 
"ST_t-channel_antitop_powheg_pythia8_2017UL.root", 
"ST_t-channel_top_powheg_pythia8_2017UL.root", 
"ST_tW_antitop_powheg_pythia8_2017UL.root", 
"ST_tW_top_powheg_pythia8_2017UL.root"]
#VVs   = ["WW_TuneCP5_13TeV-pythia8.root", "WZ_TuneCP5_13TeV-pythia8.root", "ZZ_TuneCP5_13TeV-pythia8.root"]
TTs   = [ #"TTJets_amcatnloFXFX-_pythia88_2017UL.root", 
"TTTo2L2Nu_powheg_pythia8_2017UL.root", 
"TTToSemileptonic_powheg_pythia8_2017UL.root"] #["TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8.root", "TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8.root"]
#TTs   = ["TT_TuneCH3_13TeV-powheg-herwig7.root"]
#WJs   = ["WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8.root"]
WJs   = [#"W1JetsToLNu_madgraphMLM_pythia8_2017UL.root", 
#"W2JetsToLNu_madgraphMLM_pythia8_2017UL.root", 
#"W3JetsToLNu_madgraphMLM_pythia8_2017UL.root", 
#"W4JetsToLNu_madgraphMLM_pythia8_2017UL.root", 
"WJetsToLNu_madgraphMLM_pythia8_2017UL.root"
]
#QCDs = ["QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8.root", "QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8.root", "QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8.root", "QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8.root"]
QCDs = [
#"QCD_Pt-15to7000_Flat2018_pythia8_2017UL.root", 
#"QCD_Pt-15to7000_Flat_herwig7_2017UL.root", 
"QCD_Pt_170to300_pythia8_2017UL.root", 
"QCD_Pt_300to470_pythia8_2017UL.root", 
"QCD_Pt_470to600_pythia8_2017UL.root", 
"QCD_Pt_600to800_pythia8_2017UL.root", 
"QCD_Pt_800to1000_pythia8_2017UL.root", 
"QCD_Pt_1000to1400_pythia8_2017UL.root", 
"QCD_Pt_1400to1800_pythia8_2017UL.root", 
"QCD_Pt_1800to2400_pythia8_2017UL.root", 
"QCD_Pt_2400to3200_pythia8_2017UL.root", 
"QCD_Pt_3200toInf_pythia8_2017UL.root", 
]

bkgs.append(QCDs)
bkgs.append(WJs)
#bkgs.append(VVs) # TODO: reenable this 
bkgs.append(STs)
bkgs.append(TTs)
#TTscompletion = ["oldprod/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8.root", "oldprod/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8.root"]
bkgs.append(TTs)

dir = "/work/mhuwiler/data/WScaleFactors/UL2017/UL17_Wtagging_files/" #"/eos/cms/store/group/phys_jetmet/mhuwiler/WSFnanoAODtuples/" #"/work/mhuwiler/data/WScaleFactors/added/"

plotdir = "plots/"
if "maxAK4CSV<" in cut: plotdir = "plots/WCR/"
if 'herwig' in TTs[0]: plotdir = "plots/Herwig/"
if not os.path.isdir(plotdir) : os.system('mkdir -p '+plotdir)

#For drawing
legs=["QCD multijets", "W+jets","Single top", "t#bar{t} unmerged W", "t#bar{t} merged W"] #if not 'herwig' in TTs[0] else 'TT Herwig'] #"WW/WZ/ZZ"
fillcolor = [797, 633, 613, 434, 415, 414] #[921,432,600,632,417]


def getTreeWeight(filename):
  xSec = getXsec(filename)
  xSF  = getSF(filename)
  genEv = getNev(filename)
  LEQ = float(xSec)*float(xSF)*lumi/float(genEv)
  return LEQ

#def setTreeWeight(filename):
#  print "For = ", filename
#  file = ROOT.TFile(dir+filename, 'UPDATE')
#  treeE = file.Get('Events')
#  event = treeE.GetEntry(0)
#  xSec = treeE.crossection
#  genEv = getGenEv(file.GetName())
#  LEQ = float(xSec*lumi/genEv)
#  print "xs  = " , xSec; print "N   =" ,genEv; print "Rescaling tree by = ", LEQ
#  treeE.SetWeight(LEQ)
#  treeE.AutoSave()
#  print "Tree weight is now: " ,treeE.GetWeight()

def setTreeWeight(filename):
  print "For = ", filename
  file = ROOT.TFile(dir+filename, 'UPDATE')
  treeE = file.Get('Events')
  event = treeE.GetEntry(0)
  weight = getTreeWeight(filename)
  treeE.SetWeight(weight)
  treeE.AutoSave()
  print "Tree weight is now: " ,treeE.GetWeight()

def debugPad(pad): 
  print "Pad dimensions (W, H): ", pad.GetWw(), pad.GetWh()
  print "Pad margins: ", pad.GetTopMargin(), pad.GetRightMargin(), pad.GetBottomMargin(), pad.GetLeftMargin()
  
def getCanvas():
  H_ref = 800 #600
  W_ref = 800
  W = W_ref
  H  = H_ref
  T = 0.08 #*H_ref
  B = 0.2 #*H_ref 
  L = 0.12 #*W_ref
  R = 0.04 #*W_ref

  leftMargin = 0.15
  rightMargin = 0.04
  topMargin = 0.08
  bottomMargin = 0.11

  padDelimitation = 0.27
  middleMargin = 0.04

  correctionFactorUpperPad = 1./(1.-padDelimitation)
  correctionFactorLowerPad = 1./padDelimitation

  # Setting the positions
  blPlotx = leftMargin
  blPloty = padDelimitation + middleMargin/2. 
  trPlotx, trPloty = 1.-rightMargin, 1.-topMargin

  blRatiox, blRatioy = leftMargin, bottomMargin
  trRatiox = 1. - rightMargin
  trRatioy = padDelimitation - middleMargin/2.


  #Other numbers

  #oldstyle = ROOT.gStyle
  #stylePad1 = ROOT.TStyle("stylePad1", "stylePad1")
  #stylePad1.Copy(ROOT.gStyle)
  #stylePad1.SetLabelSize(ROOT.gStyle.GetLabelSize("Y")*correctionFactorUpperPad, "XYZ")
  #stylePad1.SetTitleSize(ROOT.gStyle.GetTitleSize("Y")*correctionFactorUpperPad, "XYZ")
  #stylePad1.cd()

 
  #canvas = ROOT.TCanvas("c1","c1",50,50,W,H)
  canvas = ROOT.TCanvas("c1", "c1", W, H)
  canvas.SetLeftMargin( 0. ) #Not affected
  canvas.SetRightMargin( 0. )
  canvas.SetTopMargin( 0.)
  canvas.SetBottomMargin( 0. )
  canvas.Draw()
  # Upper histogram plot is pad1
  # Here we use a hack. Instead of making the pads non-overlapping, we make them both fully transparent and fill the canvas and exclude the area of the other in the margins in order not to disrupt the title and label size settings from the style
  pad1 = ROOT.TPad("pad1", "pad1", 0., padDelimitation, 1., 1.,)
  ROOT.SetOwnership(pad1, 0)
  pad1.SetLeftMargin(leftMargin) 
  pad1.SetRightMargin(rightMargin)
  pad1.SetTopMargin(topMargin) #no correcting factor here, prefer not to mess around with the top margin, as it would interfer wiht the legend and text 
  pad1.SetBottomMargin((middleMargin/2.)*correctionFactorUpperPad)
  #pad1.SetBottomMargin(0)  # joins upper and lower plot
  #pad1.SetGridx()
  pad1.Draw()
  #frame1 = pad1.DrawFrame(0., 0.5, 100., 1.5)
  #frame1.SetTitleSize(ROOT.gStyle.GetTitleSize("Y")*correctionFactorUpperPad, "Y")
  #frame1.SetTitleSize(ROOT.gStyle.GetTitleSize("X")*correctionFactorUpperPad, "X")

  #ROOT.gROOT.SetStyle("tdrStyle")#

#  stylePad2 = ROOT.TStyle("stylePad2", "stylePad2")
#  stylePad2.Copy(ROOT.gStyle)
#  stylePad2.SetLabelSize(ROOT.gStyle.GetLabelSize("Y")*correctionFactorUpperPad, "XYZ")
#  stylePad2.SetTitleSize(ROOT.gStyle.GetTitleSize("Y")*correctionFactorUpperPad, "XYZ")
#  stylePad2.cd()

  # Lower ratio plot is pad2
  canvas.cd()  # returns to main canvas before defining pad2
  pad2 = ROOT.TPad("pad2", "pad2", 0., 0., 1., 1.-padDelimitation)
  ROOT.SetOwnership(pad2, 0)
  pad2.SetLeftMargin(leftMargin) 
  pad2.SetRightMargin(rightMargin)
  pad2.SetTopMargin(((1.-(2.*padDelimitation))+middleMargin/2.)*correctionFactorUpperPad)
  pad2.SetBottomMargin(bottomMargin*correctionFactorUpperPad)
  pad2.Draw()
  print ((1.-(2.*padDelimitation))+middleMargin/2.)
#  frame2 = pad2.DrawFrame(0., 0.5, 100., 1.5)
#  frame2.SetTitleSize(ROOT.gStyle.GetTitleSize("Y")*correctionFactorLowerPad, "Y")
#  frame2.SetTitleSize(ROOT.gStyle.GetTitleSize("X")*correctionFactorLowerPad, "X")
#  frame2.SetLabelSize(ROOT.gStyle.GetLabelSize("Y")*correctionFactorLowerPad, "Y")
#  frame2.SetLabelSize(ROOT.gStyle.GetLabelSize("X")*correctionFactorLowerPad, "X")
  #pad2.SetTopMargin(0)  # joins upper and lower plot
  #pad2.SetBottomMargin(0.2)
  #pad2.SetGridx()
  #pad1.SetLeftMargin( L/W )
  #pad1.SetRightMargin( R/W )
  #pad1.SetTopMargin( T/H )
  #pad1.SetBottomMargin( B/H )

  #ROOT.gROOT.SetStyle("tdrStyle")

  for pad in [pad1, pad2]: 
    pad.SetFillColor(0)
    pad.SetFillColorAlpha(ROOT.kWhite, 0)
    pad.SetBorderMode(0)
    pad.SetFrameFillStyle(0)
    pad.SetFrameBorderMode(0)
    pad.SetBorderSize(0)
    pad.SetTickx(0)
    pad.SetTicky(0)
  ROOT.gStyle.SetOptStat(0)
  ROOT.gStyle.SetOptTitle(0)
  pad1.cd()
  legend = ROOT.TLegend(0.62,0.58,0.92,0.9,"","brNDC")
  legend.SetBorderSize(0)
  legend.SetLineColor(1)
  legend.SetLineStyle(1)
  legend.SetLineWidth(1)
  legend.SetFillColor(0)
  legend.SetFillStyle(0)
  legend.SetTextFont(42)
  addInfo = ROOT.TPaveText(0.2,0.6,0.52,0.72,"NDC")
  addInfo.SetFillColor(0)
  addInfo.SetLineColor(0)
  addInfo.SetFillStyle(0)
  addInfo.SetBorderSize(0)
  addInfo.SetTextFont(42)
  addInfo.SetTextSize(0.040)
  addInfo.SetTextAlign(12)
  #pad1.cd()
  return canvas, legend, addInfo, pad1, pad2

def GetRatioPlot(stack, histo, legend): 
  canvas = ROOT.TCanvas("canvas", "canvas", 800, 600)
  ROOT.TRatioPlot(stack, histo)

  legend = ROOT.TLegend(0.62,0.7,0.92,0.9,"","brNDC")
  legend.SetBorderSize(0)
  legend.SetLineColor(1)
  legend.SetLineStyle(1)
  legend.SetLineWidth(1)
  legend.SetFillColor(0)
  legend.SetFillStyle(0)
  legend.SetTextFont(42)
  addInfo = ROOT.TPaveText(0.73010112,0.2566292,0.8202143,0.5523546,"NDC")
  addInfo.SetFillColor(0)
  addInfo.SetLineColor(0)
  addInfo.SetFillStyle(0)
  addInfo.SetBorderSize(0)
  addInfo.SetTextFont(42)
  addInfo.SetTextSize(0.040)
  addInfo.SetTextAlign(12)

  return canvas, legend, addInfo

  	
def drawTH1(id,tree,var,cuts,bins,min,max,fillcolor,titlex = "",units = "",drawStyle = "HIST",lumi="%s"%lumi):
  h = ROOT.TH1D("tmpTH1_%s" % id,"",bins,min,max)
  h.Sumw2()
  h.SetFillColor(fillcolor)
  if units=="": h.GetXaxis().SetTitle(titlex)
  else: h.GetXaxis().SetTitle(titlex+ " ["+units+"]")
  tree.Draw(var+">>tmpTH1_%s" % id,cuts,"goff")
  print cuts
  
  if not "data" in id:
      if "W+jets" in legs[int(id)]: h.Scale(wjetsSF)
      if "TT" in legs[int(id)]: h.Scale(ttbarSF)
#  corrString='1'
#  if id.find("data")==-1:
#    corrString = corrString+"*(genWeight)"
#  else:
#    lumi = "1"
#  tree.Draw(var+">>tmpTH1","("+cuts+")*"+lumi+"*("+corrString+")","goff")
#  if id.find("data")==-1:
#      tree.Draw(var+">>tmpTH1","("+cuts+")","goff")
#  else:
#      tree.Draw(var+">>tmpTH1","("+cuts+")*"+lumi+"*(genWeight)","goff")
  return h

def doCP(cutL,postfix=""):
  for var in vars:
    name = var
    canvas,legend,pave, plot, ratio = getCanvas()
    minx = 200.
    maxx = 2000.
    bins = 36
    unit = "GeV"
    if var.find("MET")!=-1: minx=40.; maxx=3000.; bins=60; 
    if var.find("softdrop")!=-1 or var.find("mass")!=-1: minx=0.; maxx=130.; bins=16; 
    if var.find("eta")!=-1: minx=-3; maxx=3; bins=25; unit = "";
    if var.find("phi")!=-1: minx=-3.15; maxx=3.15; bins=50; unit = "";
    if var.find("tau")!=-1: minx=0.; maxx=1.0; bins=20; unit = "";
    if var.find("ddt")!=-1: minx=-0.2; maxx=1.2; bins=20; unit = "";
    if var.find("Muon_pt")!=-1: minx=50.; maxx=1000.0; bins=100; unit = "GeV";
    if var.find("RelIso")!=-1: minx=0.; maxx=0.15; bins=100; unit = "";
    if var.find("CSV")!=-1: minx=0.; maxx=1.; bins=100; unit = "";
    if var.find("nJet")!=-1: minx=-0.5; maxx=19.5; bins=20; unit = "";
    if var.find("nFatJet")!=-1: minx=-0.5; maxx=9.5; bins=10; unit = "";
    if var.find("nMuon")!=-1: minx=-0.5; maxx=4.5; bins=5; unit = "";
    if var.find("W_pt")!=-1: minx=0.; maxx=2000.; bins=100; unit = "";
    if var.find("W_mass")!=-1: minx=0.; maxx=200.; bins=200; unit = "";
    if var.find("dphi_")!=-1: minx=0; maxx=3.15; bins=30; unit = "";
    if var.find("dr_")!=-1: minx=0; maxx=5; bins=25; unit = "";
    if var.find("npvs")!=-1: minx=0; maxx=80; bins=80; unit = "";
    if var.find("MET_pt")!=-1: minx=0; maxx=500; bins=25; unit = "";
    if var.find("Electron_pt")!=-1: minx=0; maxx=600; bins=25; unit = "";
    if var.find("Electron_pfRelIso")!=-1: minx=0.; maxx=0.06; bins=100; unit = "";
    treeD = ROOT.TChain("Events")
    for file in datas:
      print "Using file: ", ROOT.TString(dir+file)
      fileIn_name = ROOT.TString(dir+file)  
      treeD.Add(fileIn_name.Data())
    cutT = cutL if not var in cutL else ()
    
    cutsData = "("+cutL+")*eventWeight"
    datahist = drawTH1("data",treeD,var,cutsData,bins,minx,maxx,1,var.replace("_", " ").replace("[0]", "").replace("FatJet", "AK8 jet").replace("pt", "p_{T}"),unit,"HIST","1")
    datahist.SetName("data")
    legend.AddEntry(datahist,"Data (2017UL)","LEP")
    tmpfile={}
    tmphist={}
    hists=[]
    stack = ROOT.THStack("stack","")
    totalmc = ROOT.TH1D("totalmc", "totalmc", bins, minx, maxx)
    totalmc.Sumw2()
    dataint		= datahist.Integral(0, datahist.GetNbinsX()+1)
    backint 	= [None]*len(bkgs)
    for i,bg in enumerate(bkgs):
      tree = ROOT.TChain("Events")
      name = bg[0]
      hist = None
      if legs[i] == "t#bar{t} merged W" : MCcut = cutL+"&&genmatchedAK8==1"
      elif legs[i] == "t#bar{t} unmerged W" : MCcut = cutL+"&&genmatchedAK8==0"
      else: MCcut = cutL
      totalcut = "("+MCcut+")*(eventWeight*lumiWeight*"+str(lumi)+")"
      print "Name is: ", name
      for j, file in enumerate(bg):
        print "Using file: ", ROOT.TString(dir+file)
        #setTreeWeight(file)
        fileIn_name = ROOT.TString(dir+file)  
        tree.Add(fileIn_name.Data())
#        tmpfile[file] = ROOT.TFile(fileIn_name.Data(), 'READ')
#        tmptree = tmpfile[file].Get("Events")
#        tmphist[file] = drawTH1(str(i),tmptree,var,cutL,bins,minx,maxx,fillcolor[i],var.replace("_", " ").replace("[0]", "").replace("FatJet", "AK8 jet"),unit,"HIST")
#        tmphist[file].Scale(getTreeWeight(fileIn_name.Data()))
#        if hist==None: hist = tmphist[file]
#        else: hist.Add(tmphist[file])
        
        
      hist = drawTH1(str(i),tree,var,totalcut,bins,minx,maxx,fillcolor[i],var.replace("_", " ").replace("[0]", "").replace("FatJet", "AK8 jet").replace("pt", "p_{T}"),unit,"HIST")
      # Adding the old samples with mass cut msoftdrop<30. to compensate for selection difference
      #if legs[i].find("unmerged")!=-1:
      #  chain = ROOT.TChain("Events")
      #  for file in TTscompletion: 
      #    chain.Add(dir+file)
      #  newhisto = ROOT.TH1D("newhisto", "newhisto", bins, minx, maxx)
      #  chain.Draw(var+">>newhisto","("+cutL+"&&SelectedJet_softDrop_mass<30.)*eventweightlumi","goff")
      #  hist.Add(newhisto)
      
      hist.SetFillColor(fillcolor[i])
      backint[i] = hist.Integral(0, hist.GetNbinsX()+1)
#      if name.find("TT")!=-1:
#        ttint = hist.Integral()
#        scale = (datahist.Integral()-totalMinoInt)/ttint
#        hist.Scale(scale)
#      else: totalMinoInt += hist.Integral()
      stack.Add(hist)
      totalmc.Add(hist)
      hists.append(hist)

    for i in range(len(hists)-1, -1, -1): 
      legend.AddEntry(hists[i],legs[i],"F")
    
    
#    print "DATA/MC" ,scale
    plot.cd()
    print plot.GetWw(), plot.GetWh(), plot.GetTopMargin(), plot.GetRightMargin(), plot.GetBottomMargin(), plot.GetLeftMargin()

    debugPad(canvas)
    debugPad(plot)
    debugPad(ratio)

    datahist.GetYaxis().SetRangeUser(0, datahist.GetMaximum()*1.8);
    datahist.GetYaxis().SetTitle("Events")
    datahist.GetYaxis().SetTitleOffset(1.3)
    if var in ["FatJet_pt[0]","Muon_pt[0]","W_pt","Muon_pfRelIso03_chg[0]","Muon_pfRelIso03_all[0]"]:
    	datahist.GetYaxis().SetRangeUser(0.1, datahist.GetMaximum()*1000);
    	canvas.SetLogy()
    #datahist.GetXaxis().SetTitleSize(0.05)
    datahist.GetXaxis().SetTitleOffset(1.1)
    datahist.GetXaxis().SetTitle("Probe jet #tau_{21}")
    dataratio = datahist.Clone()
    datahist.GetXaxis().SetTitleSize(0.)
    datahist.GetXaxis().SetTitleOffset(-999.)
    datahist.GetXaxis().SetLabelSize(0.)
    datahist.GetXaxis().SetLabelOffset(-999.)
    datahist.Draw("ME")
    stack.Draw("HIST SAME")
    datahist.GetYaxis().SetRangeUser(0, stack.GetMaximum()*1.2) #TODO: remove
    totalmc.SetFillColor(ROOT.kGray+2)
    totalmc.SetMarkerStyle(8)
    totalmc.SetMarkerSize(0)
    uncertaintyband = totalmc.Clone()
    uncertaintyband.SetFillColor(ROOT.kGray)
    totalmc.SetFillStyle(3001)
    totalmc.SetLineWidth(1)
    legend.AddEntry(uncertaintyband, "Stat. unc. from MC", "F")
    totalmc.Draw("E2 SAME")
    datahist.Draw("ME same")
    legend.Draw("SAME")
    pave.AddText("p_{T} > 200 GeV")
    pave.AddText("|#eta| < 2.5")
    #pave.AddText("maxAK4CSV > 0.8484")
    #pave.AddText("#Delta r(jet, lepton) > 1.5708")
    #pave.AddText("#Delta r(jet, MET) > 1.5708")
    pave.Draw("SAME")
    factor = 1.0
    CMS_lumi.writeExtraText = True
    CMS_lumi.lumiTextSize     = 0.45*factor
    CMS_lumi.lumiTextOffset   = 0.2*factor
    CMS_lumi.cmsTextSize      = 0.75*factor
    CMS_lumi.lumi_13TeV = "59.7 fb^{-1}"
    #CMS_lumi(canvas, 4, 11)
    CMS_lumi.CMS_lumi(plot, iPeriod, iPos)
    plot.Update()
    ratio.cd()
    #stack.Draw()
    uncertaintyband.Sumw2()
    uncertaintyband.Divide(totalmc)
    dataratio.Draw()
    uncertaintyband.Draw("E2 SAME")
    dataratio.Draw("SAME")
    dataratio.Divide(totalmc)
    dataratio.GetYaxis().SetRangeUser(0.4, 1.6)
    dataratio.GetYaxis().SetTitle("Data/MC")
    dataratio.GetYaxis().SetTitleOffset(1.3)
    dataratio.GetYaxis().SetNdivisions(3)
    dataratio.GetYaxis().Set(3, np.asarray([0.8, 1., 1.2], 'd'))
    dataratio.GetXaxis().SetTitle(datahist.GetXaxis().GetTitle())
    line = ROOT.TLine(0., 1., 1., 1.)
    upperline = ROOT.TLine(0., 1.2, 1., 1.2)
    lowerline = ROOT.TLine(0., 0.8, 1., 0.8)
    upperline.SetLineStyle(9) # dashed
    lowerline.SetLineStyle(9)
    line.Draw("SAME")
    #upperline.Draw("SAME")
    #lowerline.Draw("SAME")
    #dataratio.GetYaxis().SetTitleSize(datahist.GetYaxis().GetTitleSize())
    ratio.Update()

    canvas.Update()
    canvas.SaveAs(plotdir+var.replace("[0]","").replace("abs(","").replace("(","").replace(")","")+postfix+".png")
    canvas.SaveAs(plotdir+var.replace("[0]","").replace("abs(","").replace("(","").replace(")","")+postfix+".pdf")

    
    
    print "--- Summary ----"
    print "Data (2018)", "\t", dataint
    print "-"*20
    for i,bg in enumerate(bkgs):
      print legs[i], "\t", backint[i]
    print "-"*20
    print "Ratio data/bkg", "\t", dataint/sum(backint)
    print "\n"
    b = 4
    print "Scale factor for", legs[b], (dataint - sum([x for i, x in enumerate(backint) if not i==b] )) / backint[b]
    
    sleep(10)

if __name__ == "__main__":
	doCP(cut)
