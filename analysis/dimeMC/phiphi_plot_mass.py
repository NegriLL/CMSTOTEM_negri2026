#!/usr/bin/env python3

"""Before running this script, dimemc must be run with the phi flag. It will probably
work even if you don't run the correct flag but the data could be nonsense."""

import ROOT
from pathlib import Path

def main():
    # Open the ROOT file
    file_path = Path(__file__).parent.parent / "data" / "exrec.root"
    root_file = ROOT.TFile(str(file_path.resolve()))
    
    if not root_file or root_file.IsZombie():
        print(f"Error: Could not open file {file_path}")
        return
    
    # Get the TTree from the file
    tree = root_file.Get("particles")
    
    if not tree:
        print("Error: Could not find tree in file")
        root_file.Close()
        return
    
    # Get the number of entries
    num_entries = tree.GetEntries()
    print(f"Total entries: {num_entries}")
    
    # Create histogram for invariant mass
    xmin = 1.8
    xmax = 3
    bin_size = 0.02 # in GeV
    bins = int((xmax - xmin) / bin_size)
    hist_no_cuts = ROOT.TH1F("inv_mass_no_cut", "#phi #phi Production Invariant Mass", bins, xmin, xmax)
    hist_p_cut =  ROOT.TH1F("inv_mass_p_cut", "#phi #phi Production Invariant Mass (py cut)", bins, xmin, xmax)

    # Cut parameters
    proton_py_min = 0.18
    proton_py_max = 0.68
    
    # Iterate through entries
    for entry in tree:
        inv_mass = ROOT.TLorentzVector(0, 0, 0, 0)
        for i in range(entry.ntrk[0]):
            if(entry.produced_id[i] == 321 or entry.produced_id[i] == -321):
                px = entry.produced_px[i]
                py = entry.produced_py[i]
                pz = entry.produced_pz[i]
                e = entry.produced_e[i]
                inv_mass += ROOT.TLorentzVector(px, py, pz, e)

        hist_no_cuts.Fill(inv_mass.M())
        if ((proton_py_min < abs(entry.p1_out_py[0]) < proton_py_max) and (proton_py_min < abs(entry.p2_out_py[0]) < proton_py_max)):
            hist_p_cut.Fill(inv_mass.M())
    print("Done!")
    
    # Formatting
    for h in (hist_no_cuts, hist_p_cut):
        h.GetXaxis().SetTitle("Mass [GeV]")
        h.GetYaxis().SetTitle("Events")
    
    # Plot both histograms on canvas
    canvas = ROOT.TCanvas("canvas", "Invariant Mass Plot")
    hist_no_cuts.SetLineColor(ROOT.kBlue)
    hist_p_cut.SetLineColor(ROOT.kRed)
    hist_no_cuts.Draw()
    hist_p_cut.Draw("SAME")
    
    # add legend
    legend = ROOT.TLegend()
    legend.AddEntry(hist_no_cuts, "No Cuts")
    legend.AddEntry(hist_p_cut, "0.18 GeV < |pr_py| < 0.68 GeV")
    legend.Draw()
    
    # save canvas
    save_path = Path(__file__).parent.parent / "plots"
    canvas.SaveAs(str(save_path / "phiphi_decay_mass.png"))
    
    # Save histograms as ROOT file
    output_file = ROOT.TFile(str(save_path / "phiphi_decay_mass.root"), "RECREATE")
    hist_no_cuts.Write()
    hist_p_cut.Write()
    output_file.Close()
    
    canvas.Draw()
    ROOT.gApplication.Run()
    
    root_file.Close()


if __name__ == '__main__':
    main()
