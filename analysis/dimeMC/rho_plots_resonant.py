#!/usr/bin/env python3

"""Before running this script, dimemc must be run with the rho flag. It will probably
work even if you don't run the correct flag but the data could be nonsense."""

import ROOT
import math
from pathlib import Path

# Set ROOT to batch mode to avoid GUI issues
ROOT.gROOT.SetBatch(True)

def main():
    # Open the ROOT file
    file_path = Path(__file__).parent.parent.parent / "data" / "dimeMC" / "exrec_resonant.root"
    root_file = ROOT.TFile(str(file_path))
    
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
    
    # Create histograms
    # Pion momentum for each track (raw)
    pion_p_hist_raw = [ROOT.TH1F(f"pion_track{i}_p_raw", f"Track {i+1} Momentum (Raw)", 100, 0, 2) for i in range(4)]
    
    # Pion momentum for each track (with proton acceptance cut)
    pion_p_hist_cut = [ROOT.TH1F(f"pion_track{i}_p_cut", f"Track {i+1} Momentum (Cut)", 100, 0, 2) for i in range(4)]
    
    # Pion pseudorapidity
    pion_eta_hist_raw = [ROOT.TH1F(f"pion_track{i}_eta_raw", f"Track {i+1} Pseudorapidity (Raw)", 100, -3, 3) for i in range(4)]
    pion_eta_hist_cut = [ROOT.TH1F(f"pion_track{i}_eta_cut", f"Track {i+1} Pseudorapidity (Cut)", 100, -3, 3) for i in range(4)]
    
    # "glueball" pseudorapidity
    glue_eta_hist_raw = ROOT.TH1F("glue_eta_raw", "Two Rho Invariant Mass Pseudorapidity (Raw)", 100, -5, 5)
    glue_eta_hist_cut = ROOT.TH1F("glue_eta_cut", "Two Rho Invariant Mass Pseudorapidity (Cut)", 100, -5, 5)
    
    # pion pairs equivalent
    rho_mass_2d_raw = ROOT.TH2F("rho_mass_2d_raw", "#rho Mass Distribution (Raw)", 100, 0.5, 1.0, 100, 0.5, 1.0)
    rho_mass_2d_cut = ROOT.TH2F("rho_mass_2d_cut", "#rho Mass Mass Distribution (Acceptance)", 100, 0.5, 1.0, 100, 0.5, 1.0)
    
    # Two Rho Invariant Mass inv mass reconstruction
    two_rho_mass_hist_raw = ROOT.TH1F("two_rho_mass_raw", "Two Rho Invariant Mass (Raw)", 100, 1.0, 5.0)
    two_rho_mass_hist_cut = ROOT.TH1F("two_rho_mass_cut", "Two Rho Invariant Mass (Acceptance)", 100, 1.0, 5.0)
    
    # Angle between outgoing protons (raw and cut)
    proton_angle_hist_raw = ROOT.TH1F("proton_angle_raw", "Angle Between Outgoing Protons (Raw)", 200, 0, 2*math.pi)
    proton_angle_hist_cut = ROOT.TH1F("proton_angle_cut", "Angle Between Outgoing Protons (Cut)", 200, 0, 2*math.pi)
    
    # 2D histogram: Glueball Mass vs Proton Angle
    glue_mass_vs_proton_angle_raw = ROOT.TH2F("glue_mass_vs_proton_angle_raw", "Glueball Mass vs Proton Angle (Raw)", 100, 1.0, 5.0, 100, 0, 2*math.pi)
    glue_mass_vs_proton_angle_cut = ROOT.TH2F("glue_mass_vs_proton_angle_cut", "Glueball Mass vs Proton Angle (Acceptance)", 100, 1.0, 5.0, 100, 0, 2*math.pi)
    
    # Total rapidity distribution
    total_rapidity_hist_raw = ROOT.TH1F("total_rapidity_raw", "Total Rapidity (Raw)", 100, -5, 5)
    total_rapidity_hist_cut = ROOT.TH1F("total_rapidity_cut", "Total Rapidity (Acceptance)", 100, -5, 5)
    
    # Mass loss - two rho mass (collecting individual entries for bar plot)
    mass_loss_hist = ROOT.TH1F("mass_loss_hist", "Mass Loss (M - M_{#rho#rho})", 200, -2, 2)

    mass_loss_diff_raw = []
    mass_loss_diff_cut = []
    
    # Proton acceptance
    proton_py_min = 0.18
    proton_py_max = 0.68
    
    # Iterate through entries
    for entry in tree:
        pions = []
        rhos = []
        for i in range(entry.ntrk[0]):
            if abs(entry.produced_id[i]) == 211:  # Pion
                px = entry.produced_px[i]
                py = entry.produced_py[i]
                pz = entry.produced_pz[i]
                e = entry.produced_e[i]
                vec = ROOT.TLorentzVector(px, py, pz, e)
                pions.append(vec)
            if abs(entry.produced_id[i]) == 113:
                px = entry.produced_px[i]
                py = entry.produced_py[i]
                pz = entry.produced_pz[i]
                e = entry.produced_e[i]
                vec = ROOT.TLorentzVector(px, py, pz, e)
                rhos.append(vec)     
        
        # Check acceptance
        proton_cut_passed = ((proton_py_min < abs(entry.p1_out_py[0]) < proton_py_max) and 
                             (proton_py_min < abs(entry.p2_out_py[0]) < proton_py_max))
        
        # Check conservation of momentum
        rho1 = rhos[0]
        rho2 = rhos[1]
        px_tot = entry.p1_out_px[0] + rho1.Px() + rho2.Px() + entry.p2_out_px[0]
        py_tot = entry.p1_out_py[0] + rho1.Py() + rho2.Py() + entry.p2_out_py[0]
        pz_tot = entry.p1_out_pz[0] + rho1.Pz() + rho2.Pz() + entry.p2_out_pz[0]
        pe_tot = entry.p1_out_e[0] + rho1.E() + rho2.E() + entry.p2_out_e[0] 
        #print(f"{px_tot}\t\t\t{py_tot}\t\t\t{pz_tot}\t\t{pe_tot}")


        # Calculate angle between outgoing protons
        p1 = ROOT.TLorentzVector(entry.p1_out_px[0], entry.p1_out_py[0], entry.p1_out_pz[0], entry.p1_out_e[0])
        p2 = ROOT.TLorentzVector(entry.p2_out_px[0], entry.p2_out_py[0], entry.p2_out_pz[0], entry.p2_out_e[0])
        angle = abs(p1.Phi() - p2.Phi())
        # Normalize angle to be between 0 and 2pi
        if angle > 2 * math.pi:
            angle = angle - 2 * math.pi
        if angle < 0:
            angle = 2 * math.pi + angle
        
        proton_angle_hist_raw.Fill(angle)
        if proton_cut_passed:
            proton_angle_hist_cut.Fill(angle)
        
        
        # Fill pion momentum and pseudorapidity for each track
        for idx, pion in enumerate(pions[:4]):
            pion_p_hist_raw[idx].Fill(pion.P())
            pion_eta_hist_raw[idx].Fill(pion.Eta())
            if proton_cut_passed:
                pion_p_hist_cut[idx].Fill(pion.P())
                pion_eta_hist_cut[idx].Fill(pion.Eta())
        
        # We always have 4 pions but just to be sure
        if len(pions) == 4:
            #rho1 = pions[0] + pions[1]
            #rho2 = pions[2] + pions[3]
            m1 = rho1.M()
            m2 = rho2.M()
            # Fill histograms
            rho_mass_2d_raw.Fill(m1, m2)
            if proton_cut_passed:
                rho_mass_2d_cut.Fill(m1, m2)
            # Fill "glueball" histogram
            total = rho1 + rho2
            two_rho_mass = total.M()
            two_rho_mass_hist_raw.Fill(two_rho_mass)
            glue_eta_hist_raw.Fill(total.Eta())
            glue_mass_vs_proton_angle_raw.Fill(two_rho_mass, angle)
            total_rapidity_hist_raw.Fill(total.Rapidity())
            
            # Calculate mass_loss - two_rho_mass
            mass_loss = entry.mass_loss_p[0]
            mass_loss_diff = mass_loss - total.M()
            mass_loss_diff_raw.append(mass_loss_diff)
            mass_loss_hist.Fill(mass_loss_diff)
            
            if proton_cut_passed:
                two_rho_mass_hist_cut.Fill(two_rho_mass)
                glue_eta_hist_cut.Fill(total.Eta())
                glue_mass_vs_proton_angle_cut.Fill(two_rho_mass, angle)
                total_rapidity_hist_cut.Fill(total.Rapidity())
                mass_loss_diff_cut.append(two_rho_mass)
            else:
                mass_loss_diff_cut.append(two_rho_mass)
    
    print("Done!")
    
    # Formatting pion momentum
    for h in pion_p_hist_raw + pion_p_hist_cut:
        h.GetXaxis().SetTitle("Momentum [GeV]")
        h.GetYaxis().SetTitle("Events")
    
    # Formatting pion pseudorapidity
    for h in pion_eta_hist_raw + pion_eta_hist_cut:
        h.GetXaxis().SetTitle("Pseudorapidity")
        h.GetYaxis().SetTitle("Events")
    
    # Formatting Two Rho Invariant Mass pseudorapidity
    for h in (glue_eta_hist_raw, glue_eta_hist_cut):
        h.GetXaxis().SetTitle("Pseudorapidity")
        h.GetYaxis().SetTitle("Events")
    
    # Formatting proton angle
    for h in (proton_angle_hist_raw, proton_angle_hist_cut):
        h.GetXaxis().SetTitle("Angle [rad]")
        h.GetYaxis().SetTitle("Events")
    
    # Formatting rho 2D histograms
    for h in (rho_mass_2d_raw, rho_mass_2d_cut):
        h.GetXaxis().SetTitle("#rho_1 Mass [GeV]")
        h.GetYaxis().SetTitle("#rho_2 Mass [GeV]")
    
    # Formatting "glueball"
    for h in (two_rho_mass_hist_raw, two_rho_mass_hist_cut):
        h.GetXaxis().SetTitle("Mass [GeV]")
        h.GetYaxis().SetTitle("Events")
    
    # Formatting glueball mass vs proton angle
    for h in (glue_mass_vs_proton_angle_raw, glue_mass_vs_proton_angle_cut):
        h.GetXaxis().SetTitle("Glueball Mass [GeV]")
        h.GetYaxis().SetTitle("Proton Angle [rad]")
    
    # Formatting total rapidity
    for h in (total_rapidity_hist_raw, total_rapidity_hist_cut):
        h.GetXaxis().SetTitle("Rapidity")
        h.GetYaxis().SetTitle("Events")
    
    save_path = Path(__file__).parent.parent.parent / "plots" / "dimeMC" / "resonant"
    
    # plot pion momentum for each track
    canvas_pion = ROOT.TCanvas("canvas_pion", "Pion Track Momentum Distribution", 1400, 600)
    canvas_pion.Divide(2, 1)
    
    colors = [ROOT.kBlue, ROOT.kRed, ROOT.kGreen, ROOT.kMagenta]
    
    # Raw
    canvas_pion.cd(1)
    for i in range(4):
        pion_p_hist_raw[i].SetLineColor(colors[i])
    
    pion_p_hist_raw[0].Draw()
    for i in range(1, 4):
        pion_p_hist_raw[i].Draw("SAME")
    
    legend_raw = ROOT.TLegend(0.7, 0.7, 0.95, 0.95)
    for i in range(4):
        legend_raw.AddEntry(pion_p_hist_raw[i], f"Track {i+1}")
    legend_raw.Draw()
    
    # Proton Acceptance
    canvas_pion.cd(2)
    for i in range(4):
        pion_p_hist_cut[i].SetLineColor(colors[i])
    
    pion_p_hist_cut[0].Draw()
    for i in range(1, 4):
        pion_p_hist_cut[i].Draw("SAME")
    
    legend_cut = ROOT.TLegend(0.7, 0.7, 0.95, 0.95)
    for i in range(4):
        legend_cut.AddEntry(pion_p_hist_cut[i], f"Track {i+1}")
    legend_cut.Draw()
    
    canvas_pion.SaveAs(str(save_path / "pion_momentum.png"))
    
    # pion pairs
    canvas_rho_2d = ROOT.TCanvas("canvas_rho_2d", "Rho Mass 2D", 1200, 500)
    canvas_rho_2d.Divide(2, 1)
    
    # no cut
    canvas_rho_2d.cd(1)
    rho_mass_2d_raw.Draw("COLZ")
    ROOT.gPad.SetTitle("No Cut")
    
    # acceptance
    canvas_rho_2d.cd(2)
    rho_mass_2d_cut.Draw("COLZ")
    ROOT.gPad.SetTitle("Acceptance")
    
    canvas_rho_2d.SaveAs(str(save_path / "rho_mass_2d.png"))
    
    # "glueball"
    canvas_two_rho = ROOT.TCanvas("canvas_two_rho", "Two Rho Invariant Mass", 1200, 500)
    canvas_two_rho.Divide(2, 1)
    two_rho_mass_hist_raw.Fit('gaus', "", "", 2, 3)
    canvas_two_rho.SaveAs(str(save_path / "two_rho_mass.png"))

    # no cut
    canvas_two_rho.cd(1)
    two_rho_mass_hist_raw.SetLineColor(ROOT.kBlue)
    two_rho_mass_hist_raw.Draw()
    ROOT.gPad.SetTitle("Raw")
    
    # acceptance
    canvas_two_rho.cd(2)
    two_rho_mass_hist_cut.SetLineColor(ROOT.kRed)
    two_rho_mass_hist_cut.Draw()
    ROOT.gPad.SetTitle("Proton Cut")
    
    
    # Pseudorapidity
    canvas_eta = ROOT.TCanvas("canvas_eta", "Pseudorapidity Distribution", 1400, 1200)
    canvas_eta.Divide(2, 2)

    # Mass loss
    canvas_mass_loss = ROOT.TCanvas("canvas_mass_loss", "Mass Loss", 800, 600)
    
    # Top left: pion pseudorapidity (raw)
    canvas_eta.cd(1)
    for i in range(4):
        pion_eta_hist_raw[i].SetLineColor(colors[i])
    
    pion_eta_hist_raw[0].Draw()
    for i in range(1, 4):
        pion_eta_hist_raw[i].Draw("SAME")
    
    legend_eta_pion_raw = ROOT.TLegend(0.7, 0.7, 0.95, 0.95)
    for i in range(4):
        legend_eta_pion_raw.AddEntry(pion_eta_hist_raw[i], f"Track {i+1}")
    legend_eta_pion_raw.Draw()
    ROOT.gPad.SetTitle("Pion Tracks (Raw)")
    
    # Top right: Two Rho Invariant Mass pseudorapidity (raw)
    canvas_eta.cd(2)
    glue_eta_hist_raw.SetLineColor(ROOT.kBlue)
    glue_eta_hist_raw.Draw()
    ROOT.gPad.SetTitle("Two Rho Invariant Mass (Raw)")
    
    # Bottom left: pion pseudorapidity (acceptance cut)
    canvas_eta.cd(3)
    for i in range(4):
        pion_eta_hist_cut[i].SetLineColor(colors[i])
    
    pion_eta_hist_cut[0].Draw()
    for i in range(1, 4):
        pion_eta_hist_cut[i].Draw("SAME")
    
    legend_eta_pion_cut = ROOT.TLegend(0.7, 0.7, 0.95, 0.95)
    for i in range(4):
        legend_eta_pion_cut.AddEntry(pion_eta_hist_cut[i], f"Track {i+1}")
    legend_eta_pion_cut.Draw()
    ROOT.gPad.SetTitle("Pion Tracks (Acceptance)")
    
    # Bottom right: Two Rho Invariant Mass pseudorapidity (acceptance cut)
    canvas_eta.cd(4)
    glue_eta_hist_cut.SetLineColor(ROOT.kRed)
    glue_eta_hist_cut.Draw()
    ROOT.gPad.SetTitle("Two Rho Invariant Mass (Acceptance)")
    
    canvas_eta.SaveAs(str(save_path / "pseudorapidity.png"))
    
    # Angle between outgoing protons - raw and cut on same canvas
    canvas_angle = ROOT.TCanvas("canvas_angle", "Angle Between Outgoing Protons", 800, 600)
    
    proton_angle_hist_raw.SetLineColor(ROOT.kBlue)
    proton_angle_hist_cut.SetLineColor(ROOT.kRed)
    
    proton_angle_hist_raw.Draw()
    proton_angle_hist_cut.Draw("SAME")
    
    legend_angle = ROOT.TLegend(0.7, 0.7, 0.95, 0.95)
    legend_angle.AddEntry(proton_angle_hist_raw, "Raw")
    legend_angle.AddEntry(proton_angle_hist_cut, "Acceptance Cut")
    legend_angle.Draw()
    
    canvas_angle.SaveAs(str(save_path / "proton_angle.png"))
    
    # Glueball mass vs proton angle
    canvas_glue_angle = ROOT.TCanvas("canvas_glue_angle", "Glueball Mass vs Proton Angle", 1200, 500)
    canvas_glue_angle.Divide(2, 1)
    
    # no cut
    canvas_glue_angle.cd(1)
    glue_mass_vs_proton_angle_raw.Draw("COLZ")
    ROOT.gPad.SetTitle("Raw")
    
    # acceptance
    canvas_glue_angle.cd(2)
    glue_mass_vs_proton_angle_cut.Draw("COLZ")
    ROOT.gPad.SetTitle("Acceptance")
    
    canvas_glue_angle.SaveAs(str(save_path / "glue_mass_vs_proton_angle.png"))
    
    # Total rapidity distribution
    canvas_rapidity = ROOT.TCanvas("canvas_rapidity", "Total Rapidity Distribution", 800, 600)
    canvas_rapidity.Divide(2, 1)
    
    # Raw
    canvas_rapidity.cd(1)
    total_rapidity_hist_raw.SetLineColor(ROOT.kBlue)
    total_rapidity_hist_raw.Draw()
    ROOT.gPad.SetTitle("Raw")
    
    # Acceptance
    canvas_rapidity.cd(2)
    total_rapidity_hist_cut.SetLineColor(ROOT.kRed)
    total_rapidity_hist_cut.Draw()
    ROOT.gPad.SetTitle("Proton Acceptance")
    
    canvas_rapidity.SaveAs(str(save_path / "total_rapidity.png"))
    
    # Mass loss - two rho mass
    import matplotlib.pyplot as plt
    import numpy as np
    
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Mass loss
    ax1 = axes[0]
    entry_indices_raw = np.arange(len(mass_loss_diff_raw))
    colors_raw = [ROOT.kBlue if val >= 0 else ROOT.kRed for val in mass_loss_diff_raw]
    ax1.bar(entry_indices_raw, mass_loss_diff_raw, color=['blue' if val >= 0 else 'red' for val in mass_loss_diff_raw], alpha=0.7)
    ax1.set_xlabel("Entry Number")
    ax1.set_ylabel("[GeV]")
    ax1.set_title(r'$M - M_{\rho\rho}$')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
    #ax1.set_yscale('log')
    
    # Glueball mass/other values for comparison
    ax2 = axes[1]
    entry_indices_cut = np.arange(len(mass_loss_diff_cut))
    ax2.bar(entry_indices_cut, mass_loss_diff_cut, color=['blue' if val >= 0 else 'red' for val in mass_loss_diff_cut], alpha=0.7)
    ax2.set_xlabel("Entry Number")
    ax2.set_ylabel("[GeV]")
    ax2.set_title("Glueball Mass")
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
    
    plt.tight_layout()
    plt.savefig(str(save_path / "mass_loss_diff_barplot.png"), dpi=150)
    plt.close()

    # Mass loss hist
    canvas_mass_loss.cd()
    mass_loss_hist.SetLineColor(ROOT.kBlue)
    mass_loss_hist.GetXaxis().SetTitle("Mass Difference [GeV]")
    mass_loss_hist.GetYaxis().SetTitle("Events")
    mass_loss_hist.Draw()
    canvas_mass_loss.SaveAs(str(save_path / "mass_loss_hist.png"))
    
    # saving
    output_file = ROOT.TFile(str(save_path / "rho_plots.root"), "RECREATE")
    for i in range(4):
        pion_p_hist_raw[i].Write()
        pion_p_hist_cut[i].Write()
        pion_eta_hist_raw[i].Write()
        pion_eta_hist_cut[i].Write()
    rho_mass_2d_raw.Write()
    rho_mass_2d_cut.Write()
    two_rho_mass_hist_raw.Write()
    two_rho_mass_hist_cut.Write()
    glue_eta_hist_raw.Write()
    glue_eta_hist_cut.Write()
    proton_angle_hist_raw.Write()
    proton_angle_hist_cut.Write()
    glue_mass_vs_proton_angle_raw.Write()
    glue_mass_vs_proton_angle_cut.Write()
    total_rapidity_hist_raw.Write()
    total_rapidity_hist_cut.Write()
    canvas_mass_loss.Write()
    output_file.Close()
    
    root_file.Close()

if __name__ == '__main__':
    main()