/* *********************************************************************************************
 
 Copyright   2018    Marc Huwiler  <marc.huwiler@cern.ch>, <marc.huwiler@windowlive.com>
 
 Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
 and associated documentation files (the "Software"), to deal in the Software without restriction, 
 including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
 and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, 
 subject to the following conditions:
 
 The above copyright notice and this permission notice shall be included in all copies or substantial 
 portions of the Software.
 
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT 
 LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
 IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
 WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
 SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 
 ************************************************************************************************ */


#include "TFile.h"
#include "TTree.h"
#include "TString.h"
#include "TChain.h"
#include "TBranch.h"
#include "TDirectory.h"
#include "TKey.h"
#include "TCut.h"
#include <vector>
#include <iostream>
#include <string>
#include <sstream>
#include "TSystem.h"

// Global definitions, might get to a more sensitive part of the code or be obtained from data
const Double_t overflowmargin = 10.; 
bool inverse = true; 
// Add here definitions for chosen variable names in trees



using std::cout, std::endl; 



double PlotROC( TChain *signal, TChain *background, const TString cutVariable, const TString signalCut = "", const TString backgroundCut = "", const Double_t threshold = 0.9, const Int_t distcretisation = 1000, const TString outname = "ROCsummary.root", bool verbose = false ) 
{

    

    if (verbose) std::cout << "Using:\tsignal cut: " << signalCut << std::endl << "\tbackground cut: " << backgroundCut << std::endl; 

    std::vector<Double_t> MVAcutvalues;
    /*std::map<Double_t, Int_t> nsignal;
    std::map<Double_t, Double_t> sigEff;
    std::map<Double_t, Double_t> sigEffErr;
    std::map<Double_t, Int_t> nbackground;
    std::map<Double_t, Double_t> bkgEff;
    std::map<Double_t, Double_t> bkgEffErr; */
    
    Double_t MVAmin = min(signal->GetMinimum(cutVariable), background->GetMinimum(cutVariable));       // <- Set this        // Maybe take the min of the mins of signal and background ...
    Double_t MVAmax = max(signal->GetMaximum(cutVariable), background->GetMaximum(cutVariable));       // <- Set this
    
    
    TH1D *signalaftercut = nullptr;
    TH1D *backgroundaftercut = nullptr;
    
    TCanvas *canvas = new TCanvas("myCanvas", "temporary Canvas", 800., 600.);
    
    const Double_t rangemin = MVAmin - overflowmargin;        // idem (as for MVAmin)
    const Double_t rangemax = MVAmax + overflowmargin;
    
    signalaftercut = new TH1D("signalwocut", "signalwocut", distcretisation, rangemin, rangemax);
    backgroundaftercut = new TH1D("backgroundwocut", "backgroundwocut", distcretisation, rangemin, rangemax); 
       
    signal->Draw(cutVariable+">>signalwocut", signalCut);
    background->Draw(cutVariable+">>backgroundwocut", backgroundCut);
    
    const Double_t Nsignal = signalaftercut->Integral();
    const Double_t Nbackground = backgroundaftercut->Integral();


    const Double_t minaxis = MVAmin; 
    MVAmin = signalaftercut->GetBinCenter(min(signalaftercut->FindFirstBinAbove(minaxis), backgroundaftercut->FindFirstBinAbove(minaxis))-1); 
    MVAmax = signalaftercut->GetBinCenter(max(signalaftercut->FindLastBinAbove(minaxis), backgroundaftercut->FindLastBinAbove(minaxis))+1); 


    if (MVAmax == MVAmin) 
    {
        std::cerr << "ERROR: The MVA variable is constant. Cannot create a ROC curve. "; 
        return -999; 
    }
    Double_t MVAit = (MVAmax-MVAmin)/static_cast<Double_t>(distcretisation); //0.02;
    
    
    
    for (double cutvalue=MVAmin; cutvalue<=MVAmax; cutvalue+=MVAit)
    {
        MVAcutvalues.push_back(cutvalue);
        //cout <<cutvalue << std::endl;
    }
    
    
    
    
    // Setting variables for reading the branches in the file
    
    //Double_t pt=0., energy=0.;
    
    //signal->SetBranchStatus("*", 0);
    //signal->SetBranchStatus(cutVariable, 1);
    //signal->SetBranchStatus(cutVariable, 1);
    
    //background->SetBranchStatus("*", 0);
    //background->SetBranchStatus(cutVariable, 1);
    //background->SetBranchStatus(cutVariable, 1);
    
    
    if (verbose) cout << std::endl << "Will scan cuts on " << cutVariable << " between " << MVAmin << " and " << MVAmax << " by steps of " << MVAit << " (total of " << distcretisation << " cuts) ... " << std::endl << std::endl;
    
    
    Double_t sigEffPlot[MVAcutvalues.size()];
    Double_t bkgEffPlot[MVAcutvalues.size()];
    Double_t sigEffErrPlot[MVAcutvalues.size()];
    Double_t bkgEffErrPlot[MVAcutvalues.size()];
    Double_t invBkgEffPlot[MVAcutvalues.size()]; 

    if (verbose) cout << "Starting loop" << std::endl;
    for (unsigned int i=0; i<MVAcutvalues.size(); i++ )
    {
        Double_t cutvalue = MVAcutvalues.at(i);
        if (verbose) cout << "Processing cut at " << cutvalue << std::endl;
        
        // Computing stuff locally
        Double_t sigEffError; // Not used yet
        Int_t maxBin = signalaftercut->GetBin(signalaftercut->GetNbinsX()); 
        Int_t minBin = signalaftercut->GetBin(0); 
        Double_t Nsignalaftercut = -999.; 
        if (inverse == false) 
        {
            Nsignalaftercut = signalaftercut->IntegralAndError(signalaftercut->FindBin(cutvalue), maxBin, sigEffError);
        }
        else 
        {
            Nsignalaftercut = signalaftercut->IntegralAndError(minBin, signalaftercut->FindBin(cutvalue), sigEffError);
        }
        sigEffPlot[i] = static_cast<Double_t>(Nsignalaftercut)/static_cast<Double_t>(Nsignal);
        sigEffErrPlot[i] = sqrt(sigEffPlot[i]*(1.-sigEffPlot[i])/static_cast<Double_t>(Nsignal)); 
        //std::cout << "histogram error: " << sigEffError << std::endl; 
        
        Double_t Nbackgroundaftercut = -999.; 
        maxBin = backgroundaftercut->GetBin(backgroundaftercut->GetNbinsX()); 
        minBin = backgroundaftercut->GetBin(0); 
        if (!inverse) 
        {
            Nbackgroundaftercut = backgroundaftercut->IntegralAndError(backgroundaftercut->FindBin(cutvalue), maxBin, sigEffError);
        }
        else 
        {
            Nbackgroundaftercut = backgroundaftercut->IntegralAndError(minBin, backgroundaftercut->FindBin(cutvalue), sigEffError);
        }
        bkgEffPlot[i] = static_cast<Double_t>(Nbackgroundaftercut)/static_cast<Double_t>(Nbackground);
        bkgEffErrPlot[i] = sqrt(bkgEffPlot[i]*(1.-bkgEffPlot[i])/static_cast<Double_t>(Nbackground));
        invBkgEffPlot[i] = 1. - bkgEffPlot[i]; 

        // Set the the results in the global maps
       
        
        
            
    
    }
    
    if (verbose) cout << "Finished loop " << std::endl;
    
#if 0
    for (unsigned int i=0; i<MVAcutvalues.size(); i++)
    {
        //cout << nsignal.at(MVAcutvalues.at(i)) << " " << sigEff.at(MVAcutvalues.at(i)) << " " << sigEffErr.at(MVAcutvalues.at(i)) << " " << nbackground.at(MVAcutvalues.at(i)) << " " << bkgEff.at(MVAcutvalues.at(i)) << " " << bkgEffErr.at(MVAcutvalues.at(i)) << std::endl;
        
    }
#endif
    
    /*Double_t sigEffPlot[MVAcutvalues.size()];
    Double_t bkgEffPlot[MVAcutvalues.size()];
    Double_t sigEffErrPlot[MVAcutvalues.size()];
    Double_t bkgEffErrPlot[MVAcutvalues.size()];
    Double_t invBkgEffPlot[MVAcutvalues.size()]; 
    //sigEffPlot.reserve(MVAcutvalues.size());
    for (unsigned int i=0; i<MVAcutvalues.size(); i++)
    {
        Double_t cut = MVAcutvalues.at(i);
        sigEffPlot[i] = sigEff.at(cut);
        bkgEffPlot[i] = bkgEff.at(cut);
        sigEffErrPlot[i] = sigEffErr.at(cut);
        bkgEffErrPlot[i] = bkgEffErr.at(cut);
        invBkgEffPlot[i] = 1. - bkgEff.at(cut); 
        
    } */

    Double_t finalcutvalue = -888.; 
    for (unsigned i = 0; i<MVAcutvalues.size(); i++) 
    {
        finalcutvalue = MVAcutvalues.at(i); 

        if (verbose) std::cout << bkgEffPlot[i] << std::endl; 
        
        if (bkgEffPlot[i] > threshold) 
        {
            if (i<1)
            {
                std::cerr << "The background efficiency is already higher than " << threshold << " at the first cut, cannot provide a cut value for background efficiency " << threshold << ". " << std::endl; 
                break; 
            }

            finalcutvalue = MVAcutvalues.at(i-1); 
            std::cout << "Closest cut for " << 100*threshold << "\% background efficiency : " << finalcutvalue << std::endl; 
            break; 

        }
    }
   
    /*canvas->cd();
    TGraphErrors *ROCcurve = new TGraphErrors(MVAcutvalues.size(), bkgEffPlot, sigEffPlot, bkgEffErrPlot, sigEffErrPlot);
    ROCcurve->SetMarkerStyle(21);
    ROCcurve->Draw("AP.");
    canvas->Draw();
    canvas->Print("output.pdf"); */



    TFile *plotFile = TFile::Open(outname, "RECREATE"); 
   
    TGraphErrors *ROCcurve = new TGraphErrors(MVAcutvalues.size(), sigEffPlot, bkgEffPlot, sigEffErrPlot, bkgEffErrPlot);
    ROCcurve->SetName("bkgEff(sigEff)");
    ROCcurve->SetMarkerStyle(21);
    //ROCcurve->Draw("AP.");
    ROCcurve->SetTitle("bkgEff(sigEff)");
    ROCcurve->GetXaxis()->SetTitle("Signal efficiency");
    ROCcurve->GetYaxis()->SetTitle("Background efficiency");

    ROCcurve->Write(); 
    

    Double_t bkgEffat90 = ROCcurve->Eval(0.9);
    
    Double_t bkgEffat80 = ROCcurve->Eval(0.8);

    
    ROCcurve = new TGraphErrors(MVAcutvalues.size(), invBkgEffPlot, sigEffPlot, bkgEffErrPlot, sigEffErrPlot);
    ROCcurve->SetName("TMVA-like_ROC");
    ROCcurve->SetMarkerStyle(21);
    //->Draw("AP.");
    ROCcurve->SetTitle("TMVA-like ROC curve");
    ROCcurve->GetXaxis()->SetTitle("Background rejection");
    ROCcurve->GetYaxis()->SetTitle("Signal efficiency");

    ROCcurve->Write(); 

    ROCcurve = new TGraphErrors(MVAcutvalues.size(), bkgEffPlot, sigEffPlot, bkgEffErrPlot, sigEffErrPlot);
    ROCcurve->SetName("scikit-like_ROC");
    ROCcurve->SetMarkerStyle(21);
    //ROCcurve->Draw("AP.");
    ROCcurve->SetTitle("scikit-like ROC curve");
    ROCcurve->GetXaxis()->SetTitle("Background efficiency");
    ROCcurve->GetYaxis()->SetTitle("Signal efficiency");


    ROCcurve->Write(); 


    Double_t signalEfficiency = ROCcurve->Eval(threshold); 

    std::cout << "Signal efficiency at background efficiency of " << threshold << ": " << signalEfficiency << std::endl; 

    

    plotFile->Close(); 

    delete canvas; 
    delete signalaftercut; 
    delete backgroundaftercut; 
    
    return finalcutvalue; 
}

double PlotROC( TChain *signal, TChain *background, const TString cutVariable, const TCut signalCut, const TCut backgroundCut, const Double_t threshold = 0.9, const Int_t distcretisation = 1000, const TString outname = "ROCsummary.root", bool verbose = false) 
{
    return PlotROC(signal, background, cutVariable, TString(signalCut.GetTitle()), TString(backgroundCut.GetTitle()), threshold, distcretisation, outname, verbose); 
    //return -1.; 
}

