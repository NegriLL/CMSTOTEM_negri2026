#!/usr/bin/env python3

import ROOT
from pathlib import Path
from numpy import arctanh, linalg

# Calculate pseudorapidity
def pseudorapidity(px, py, pz):
    P = linalg.norm([px, py, pz])
    return arctanh(pz/P)

def main():
    prod = "rho"
    # Open the ROOT file
    file_path = Path(__file__).parent.parent / "data" / "exrec.root"
    root_file = ROOT.TFile(str(file_path.resolve()))

    # Making sure tree and files exist
    if not root_file or root_file.IsZombie():
        print(f"Error: Could not open file {file_path}")
        return
    
    tree = root_file.Get("particles")

    if not tree:
        print("Error: Could not find tree in file")
        root_file.Close()
        return
    
    # Get the number of entries
    num_entries = tree.GetEntries()
    print(f"Total entries: {num_entries}")
    
    # Cut parameters
    proton_py_min = 0.18
    proton_py_max = 0.68
    
    # Create histograms
    bins = 100
    xmin = -4
    xmax = 4
    # K distributions
    hist_K_mass_dist = ROOT.TH1F("hist_K_mass_dist", f"{prod} Generated Mass Distribution", bins, 0.6, 1.2)
    hist_Kbar_mass_dist = ROOT.TH1F("hist_Kbar_mass_dist", f"{prod} Generated Mass Distribution", bins, 0.6, 1.2)
    # p distributions K
    hist_Kpx_dist =  ROOT.TH1F("hist_Kpx_dist", f"{prod} px", bins, xmin, xmax)
    hist_Kpy_dist =  ROOT.TH1F("hist_Kpy_dist", f"{prod} py", bins, xmin, xmax)
    hist_Kpz_dist =  ROOT.TH1F("hist_Kpz_dist", f"{prod} pz", bins, xmin, xmax)
    hist_Ke_dist =  ROOT.TH1F("hist_Ke_dist", f"{prod} pe", bins, xmin, xmax)

    hist_Kbarpx_dist =  ROOT.TH1F("hist_Kbarpx_dist", f"{prod}bar px", bins, xmin, xmax)
    hist_Kbarpy_dist =  ROOT.TH1F("hist_Kbarpy_dist", f"{prod}bar py", bins, xmin, xmax)
    hist_Kbarpz_dist =  ROOT.TH1F("hist_Kbarpz_dist", f"{prod}bar pz", bins, xmin, xmax)
    hist_Kbare_dist =  ROOT.TH1F("hist_Kbare_dist", f"{prod}bar pe", bins, xmin, xmax)
    # eta rapidity distis
    hist_Keta_dist = ROOT.TH1F("hist_Keta_dist", f"{prod} Pseudorapidity Distribution", bins, -4, 4)
    hist_Kbareta_dist = ROOT.TH1F("hist_Kbareta_dist", f"{prod}bar Pseudorapidity Distribution", 100, -4, 4)

    # Now same but with cuts
    hist_K_mass_dist_cut =  ROOT.TH1F("hist_K_mass_dist_cut", f"{prod} Generated Mass Distribution (py cut)", bins, 0.6, 1.2)
    hist_Kbar_mass_dist_cut = ROOT.TH1F("hist_Kbar_mass_dist_cut", f"{prod}bar Generated Mass Distribution (py cut)", bins, 0.6, 1.2)

    hist_Kpx_dist_cut =  ROOT.TH1F("hist_Kpx_dist_cut", f"{prod} px", bins, xmin, xmax)
    hist_Kpy_dist_cut =  ROOT.TH1F("hist_Kpy_dist_cut", f"{prod} py", bins, xmin, xmax)
    hist_Kpz_dist_cut =  ROOT.TH1F("hist_Kpz_dist_cut", f"{prod} pz", bins, xmin, xmax)
    hist_Ke_dist_cut =  ROOT.TH1F("hist_Ke_dist_cut", f"{prod} pe", bins, xmin, xmax)

    hist_Kbarpx_dist_cut =  ROOT.TH1F("hist_Kbarpx_dist_cut", f"{prod}bar px", bins, xmin, xmax)
    hist_Kbarpy_dist_cut =  ROOT.TH1F("hist_Kbarpy_dist_cut", f"{prod}bar py", bins, xmin, xmax)
    hist_Kbarpz_dist_cut =  ROOT.TH1F("hist_Kbarpz_dist_cut", f"{prod}bar pz", bins, xmin, xmax)
    hist_Kbare_dist_cut =  ROOT.TH1F("hist_Kbare_dist_cut", f"{prod}bar pe", bins, xmin, xmax)

    hist_Keta_dist_cut = ROOT.TH1F("hist_Keta_dist_cut", f"{prod} Pseudorapidity Distribution", bins, -4, 4)
    hist_Kbareta_dist_cut = ROOT.TH1F("hist_Kbareta_dist_cut", f"{prod}bar Pseudorapidity Distribution", bins, -4, 4)

    # Iterate through entries
    for entry in tree:
        # First two particles are K* and K*bar in this generation
        # Fill K* first
        Km = entry.produced_m[0]
        Kpx = entry.produced_px[0]
        Kpy = entry.produced_py[0]
        Kpz = entry.produced_pz[0]
        Ke = entry.produced_e[0]
        Keta = pseudorapidity(Kpx, Kpy, Kpz)

        hist_K_mass_dist.Fill(Km)
        hist_Kpx_dist.Fill(Kpx)
        hist_Kpy_dist.Fill(Kpy)
        hist_Kpz_dist.Fill(Kpz)
        hist_Ke_dist.Fill(Ke)
        hist_Keta_dist.Fill(Keta)

        # Now K*bar
        Kbarm = entry.produced_m[1]
        Kbarpx = entry.produced_px[1]
        Kbarpy = entry.produced_py[1]
        Kbarpz = entry.produced_pz[1]
        Kbare = entry.produced_e[1]
        Kbareta = pseudorapidity(Kbarpx, Kbarpy, Kbarpz)

        hist_Kbar_mass_dist.Fill(Kbarm)
        hist_Kbarpx_dist.Fill(Kbarpx)
        hist_Kbarpy_dist.Fill(Kbarpy)
        hist_Kbarpz_dist.Fill(Kbarpz)
        hist_Kbare_dist.Fill(Kbare)
        hist_Kbareta_dist.Fill(Kbareta)

        # Now with cuts
        if ((proton_py_min < abs(entry.p1_out_py[0]) < proton_py_max) and (proton_py_min < abs(entry.p2_out_py[0]) < proton_py_max)):
            hist_K_mass_dist_cut.Fill(Km)
            hist_Kpx_dist_cut.Fill(Kpx)
            hist_Kpy_dist_cut.Fill(Kpy)
            hist_Kpz_dist_cut.Fill(Kpz)
            hist_Ke_dist_cut.Fill(Ke)
            hist_Keta_dist_cut.Fill(Keta)
            hist_Kbar_mass_dist_cut.Fill(Kbarm)
            hist_Kbarpx_dist_cut.Fill(Kbarpx)
            hist_Kbarpy_dist_cut.Fill(Kbarpy)
            hist_Kbarpz_dist_cut.Fill(Kbarpz)
            hist_Kbare_dist_cut.Fill(Kbare)
            hist_Kbareta_dist_cut.Fill(Kbareta)


    print("Done!")

    # Mass distributions
    c1 = ROOT.TCanvas("c1", "Mass Distributions", 1600, 1200)
    c1.Divide(1, 2)
    c1.cd(1)
    hist_K_mass_dist.SetLineColor(ROOT.kRed)
    hist_K_mass_dist.Draw()
    hist_Kbar_mass_dist.SetLineColor(ROOT.kBlue)
    hist_Kbar_mass_dist.Draw("same")
    legend1 = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
    legend1.AddEntry(hist_K_mass_dist, f"{prod}", "l")
    legend1.AddEntry(hist_Kbar_mass_dist, f"{prod}bar", "l")
    legend1.Draw()
    c1.cd(2)
    hist_K_mass_dist_cut.SetLineColor(ROOT.kRed)
    hist_K_mass_dist_cut.Draw()
    hist_Kbar_mass_dist_cut.SetLineColor(ROOT.kBlue)
    hist_Kbar_mass_dist_cut.Draw("same")
    legend2 = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
    legend2.AddEntry(hist_K_mass_dist_cut, f"{prod}", "l")
    legend2.AddEntry(hist_Kbar_mass_dist_cut, f"{prod}bar", "l")
    legend2.Draw()
    
    # Momentum distributions
    c2 = ROOT.TCanvas("c2", "Momentum Distributions", 1600, 1200)
    c2.Divide(2, 2)
    legend_p = ROOT.TLegend(0.7, 0.6, 0.9, 0.9)
    legend_p.AddEntry(hist_Kpx_dist, f"{prod} no cut", "l")
    legend_p.AddEntry(hist_Kbarpx_dist, f"{prod}bar no cut", "l")
    legend_p.AddEntry(hist_Kpx_dist_cut, f"{prod} cut", "l")
    legend_p.AddEntry(hist_Kbarpx_dist_cut, f"{prod} cut", "l")
    c2.cd(1)
    hist_Kpx_dist.SetLineColor(ROOT.kRed)
    hist_Kpx_dist.Draw()
    hist_Kbarpx_dist.SetLineColor(ROOT.kBlue)
    hist_Kbarpx_dist.Draw("same")
    hist_Kpx_dist_cut.SetLineColor(ROOT.kGreen)
    hist_Kpx_dist_cut.Draw("same")
    hist_Kbarpx_dist_cut.SetLineColor(ROOT.kMagenta)
    hist_Kbarpx_dist_cut.Draw("same")
    legend_p.Draw()
    c2.cd(2)
    hist_Kpy_dist.SetLineColor(ROOT.kRed)
    hist_Kpy_dist.Draw()
    hist_Kbarpy_dist.SetLineColor(ROOT.kBlue)
    hist_Kbarpy_dist.Draw("same")
    hist_Kpy_dist_cut.SetLineColor(ROOT.kGreen)
    hist_Kpy_dist_cut.Draw("same")
    hist_Kbarpy_dist_cut.SetLineColor(ROOT.kMagenta)
    hist_Kbarpy_dist_cut.Draw("same")
    legend_p.Draw()
    c2.cd(3)
    hist_Kpz_dist.SetLineColor(ROOT.kRed)
    hist_Kpz_dist.Draw()
    hist_Kbarpz_dist.SetLineColor(ROOT.kBlue)
    hist_Kbarpz_dist.Draw("same")
    hist_Kpz_dist_cut.SetLineColor(ROOT.kGreen)
    hist_Kpz_dist_cut.Draw("same")
    hist_Kbarpz_dist_cut.SetLineColor(ROOT.kMagenta)
    hist_Kbarpz_dist_cut.Draw("same")
    legend_p.Draw()
    c2.cd(4)
    hist_Ke_dist.SetLineColor(ROOT.kRed)
    hist_Ke_dist.Draw()
    hist_Kbare_dist.SetLineColor(ROOT.kBlue)
    hist_Kbare_dist.Draw("same")
    hist_Ke_dist_cut.SetLineColor(ROOT.kGreen)
    hist_Ke_dist_cut.Draw("same")
    hist_Kbare_dist_cut.SetLineColor(ROOT.kMagenta)
    hist_Kbare_dist_cut.Draw("same")
    legend_p.Draw()

    # Pseudorapidities
    c3 = ROOT.TCanvas("c3", "Pseudorapidities", 1600, 1200)
    c3.Divide(1, 2)
    c3.cd(1)
    hist_Keta_dist.SetLineColor(ROOT.kRed)
    hist_Keta_dist.Draw()
    hist_Kbareta_dist.SetLineColor(ROOT.kBlue)
    hist_Kbareta_dist.Draw("same")
    legend3 = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
    legend3.AddEntry(hist_Keta_dist, f"{prod}".format(prod), "l")
    legend3.AddEntry(hist_Kbareta_dist, f"{prod}bar".format(prod), "l")
    legend3.Draw()
    c3.cd(2)
    hist_Keta_dist_cut.SetLineColor(ROOT.kRed)
    hist_Keta_dist_cut.Draw("same")
    hist_Kbareta_dist_cut.SetLineColor(ROOT.kBlue)
    hist_Kbareta_dist_cut.Draw("same")
    legend4 = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
    legend4.AddEntry(hist_Keta_dist_cut, f"{prod}", "l")
    legend4.AddEntry(hist_Kbareta_dist_cut, f"{prod}bar", "l")
    legend4.Draw()

    # Save canvases
    save_path = Path(__file__).parent.parent / "plots"
    
    c1.SaveAs(str(save_path / f"{prod}_mass_dist.png"))
    c1.SaveAs(str(save_path / f"{prod}_mass_dist.root"))
    c2.SaveAs(str(save_path / f"{prod}_momentum_dist.png"))
    c2.SaveAs(str(save_path / f"{prod}_momentum_dist.root"))
    c3.SaveAs(str(save_path / f"{prod}_pseudorapidity_dist.png"))
    c3.SaveAs(str(save_path / f"{prod}_pseudorapidity_dist.root"))

    root_file.Close()



if __name__ == "__main__":
    main()