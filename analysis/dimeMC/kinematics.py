#!/usr/bin/env python3

import ROOT
import math
import sys
from pathlib import Path


def get_particles(file_path):
    # Open root file
    root_file = ROOT.TFile(str(file_path))
    if not root_file or root_file.IsZombie():
        sys.exit(f"Error: Could not open file {file_path}")
        return
    
    # Get the TTree from the file
    tree = root_file.Get("particles")
    
    if not tree:
        sys.exit("Error: Could not find tree in file")
        root_file.Close()
        return
    
    # Get the number of entries
    num_entries = tree.GetEntries()
    print(f"Total entries: {num_entries}")

    pions = []
    rhos = []
    glues = []

    # Acceptance
    proton_cut_passed = []
    mass_cut_passed = []
    proton_py_min = 0.18
    proton_py_max = 0.68

    # proton angles
    proton_angles = []

    # Iterate through entries
    for entry in tree:
        event_pions = []
        for i in range(entry.ntrk[0]):
            if abs(entry.produced_id[i]) == 211:  # Pion
                px = entry.produced_px[i]
                py = entry.produced_py[i]
                pz = entry.produced_pz[i]
                e = entry.produced_e[i]
                vec = ROOT.TLorentzVector(px, py, pz, e)
                event_pions.append(vec)
                pions.append(vec)
        # could cause problems if there aren't 4 pions but that should never be the case for the resonant production
        rhos.append(event_pions[0] + event_pions[1])
        rhos.append(event_pions[2] + event_pions[3])
        glue = event_pions[0] + event_pions[1] + event_pions[2] + event_pions[3]
        glues.append(glue)

        proton_cut_passed.append(((proton_py_min < abs(entry.p1_out_py[0]) < proton_py_max)
                                  and (proton_py_min < abs(entry.p2_out_py[0]) < proton_py_max)))
        mass_cut_passed.append(2.1 < glue.M() < 2.4)

        # Calculate angle between outgoing protons
        p1 = ROOT.TLorentzVector(entry.p1_out_px[0], entry.p1_out_py[0], entry.p1_out_pz[0], entry.p1_out_e[0])
        p2 = ROOT.TLorentzVector(entry.p2_out_px[0], entry.p2_out_py[0], entry.p2_out_pz[0], entry.p2_out_e[0])
        angles = [p1.Phi(), p2.Phi()]

        proton_angles.append(angles)
        

    return pions, rhos, glues, proton_cut_passed, mass_cut_passed, proton_angles


def plot_kinematics(particles, particles_nonreson,
                    proton_cut_passed_resonant,proton_cut_passed_nonreson, mass_cut,
                    particle_name, save_path):
    nbins = 100

    eta_resonant_hist = ROOT.TH1F(f"{particle_name}_eta_res", f"{particle_name} #eta", nbins, -5, 5)
    phi_resonant_hist = ROOT.TH1F(f"{particle_name}_phi_res", f"{particle_name} #varphi", nbins, -4, 4)
    pt_resonant_hist = ROOT.TH1F(f"{particle_name}_pt_res", f"{particle_name} pt", nbins, -1, 4)

    eta_nonreson_hist = ROOT.TH1F(f"{particle_name}_eta_nonres", f"{particle_name} #eta", nbins, -5, 5)
    phi_nonreson_hist = ROOT.TH1F(f"{particle_name}_phi_nonres", f"{particle_name} #varphi", nbins, -4, 4)
    pt_nonreson_hist = ROOT.TH1F(f"{particle_name}_pt_nonres", f"{particle_name} pt", nbins, -1, 4)

    # Resonant histograms styling
    eta_resonant_hist.SetLineWidth(3)
    eta_resonant_hist.SetLineColor(ROOT.kBlue)
    phi_resonant_hist.SetLineWidth(3)
    phi_resonant_hist.SetLineColor(ROOT.kBlue)
    pt_resonant_hist.SetLineWidth(3)
    pt_resonant_hist.SetLineColor(ROOT.kBlue)

    # Non-resonant histograms styling
    eta_nonreson_hist.SetLineWidth(3)
    eta_nonreson_hist.SetLineColor(ROOT.kGreen)
    phi_nonreson_hist.SetLineWidth(3)
    phi_nonreson_hist.SetLineColor(ROOT.kGreen)
    pt_nonreson_hist.SetLineWidth(3)
    pt_nonreson_hist.SetLineColor(ROOT.kGreen)

    # Fill resonant histograms
    for particle, accepted in zip(particles, proton_cut_passed_resonant):
        if accepted:
            eta_resonant_hist.Fill(particle.Eta())
            phi_resonant_hist.Fill(particle.Phi())
            pt_resonant_hist.Fill(particle.Pt())
    
    # Fill non-resonant histograms
    for particle, accepted, mass_pass in zip(particles_nonreson, proton_cut_passed_nonreson, mass_cut):
        if accepted and mass_pass:
            eta_nonreson_hist.Fill(particle.Eta())
            phi_nonreson_hist.Fill(particle.Phi())
            pt_nonreson_hist.Fill(particle.Pt())
    
    canvas = ROOT.TCanvas(f"{particle_name}_kinematics", f"{particle_name} Kinematics", 600, 1800)
    canvas.Divide(1, 3)
    
    # Draw eta distributions
    canvas.cd(1)
    eta_resonant_hist.Draw()
    eta_nonreson_hist.Draw("SAME")
    
    # Draw phi distributions
    canvas.cd(2)
    phi_resonant_hist.Draw()
    phi_nonreson_hist.Draw("SAME")
    
    # Draw pt distributions
    canvas.cd(3)
    pt_resonant_hist.Draw()
    pt_nonreson_hist.Draw("SAME")
    
    canvas.cd(1)
    legend = ROOT.TLegend(1, 0.5, 0.8, 0.3)
    legend.AddEntry(eta_resonant_hist, "Resonant", "l")
    legend.AddEntry(eta_nonreson_hist, "Non-resonant", "l")
    legend.Draw()
    
    canvas.cd(2)
    legend2 = ROOT.TLegend(1, 0.5, 0.8, 0.3)
    legend2.AddEntry(phi_resonant_hist, "Resonant", "l")
    legend2.AddEntry(phi_nonreson_hist, "Non-resonant", "l")
    legend2.Draw()
    
    canvas.cd(3)
    legend3 = ROOT.TLegend(1, 0.5, 0.8, 0.3)
    legend3.AddEntry(pt_resonant_hist, "Resonant", "l")
    legend3.AddEntry(pt_nonreson_hist, "Non-resonant", "l")
    legend3.Draw()
    
    particle_title = particle_name.replace('#', "").replace('{', "").replace('}', "")
    canvas.SaveAs(str(save_path / f"{particle_title}_kinematics.png"))


def plot_angle_vs_mass(glues_resonant, glues_nonreson, proton_angles_resonant, proton_angles_nonreson,
                proton_cut_passed_resonant, proton_cut_passed_nonreson, mass_cut,
                save_path):
    nbins = 100
    mass_min = 2
    mass_max = 2.5
    resonant = ROOT.TH2F("resonant", "Glueball Mass vs Proton Angle Resonant", nbins, mass_min, mass_max, nbins, 0, 2*math.pi)
    nonreson = ROOT.TH2F("nonreson", "Glueball Mass vs Proton Angle Nonresonant", nbins, mass_min, mass_max, nbins, 0, 2*math.pi)

    angles_resonant = []
    for p1, p2 in proton_angles_resonant:
        angle = abs(p1 - p2)
        if angle > 2 * math.pi:
            angle = angle - 2 * math.pi
        if angle < 0:
            angle = 2 * math.pi + angle
        angles_resonant.append(angle)

    angles_nonreson = []
    for p1, p2 in proton_angles_nonreson:
        angle = abs(p1 - p2)
        if angle > 2 * math.pi:
            angle = angle - 2 * math.pi
        if angle < 0:
            angle = 2 * math.pi + angle
        angles_nonreson.append(angle)


    for glue, angle, cut1 in zip(glues_resonant, angles_resonant, proton_cut_passed_resonant):
        if cut1:
            resonant.Fill(glue.M(), angle)
    for glue, angle, cut1, cut2 in zip(glues_nonreson, angles_nonreson, proton_cut_passed_nonreson, mass_cut):
        if cut1 and cut2:
            nonreson.Fill(glue.M(), angle)

    for h in (resonant, nonreson):
        h.GetXaxis().SetTitle("Glueball Mass [GeV]")
        h.GetYaxis().SetTitle("Proton Angle [rad]")

    # Glueball mass vs proton angle
    canvas_glue_angle = ROOT.TCanvas("canvas_glue_angle", "Glueball Mass vs Proton Angle", 1200, 500)
    canvas_glue_angle.Divide(2, 1)
    
    canvas_glue_angle.cd(1)
    resonant.Draw("COLZ")
    ROOT.gPad.SetTitle("Resonant")
    canvas_glue_angle.cd(2)
    nonreson.Draw("COLZ")
    ROOT.gPad.SetTitle("Non-resonant")
    
    canvas_glue_angle.SaveAs(str(save_path / "glue_mass_vs_proton_angle.png"))


def plot_angle_vs_angle(proton_angles_resonant, proton_angles_nonreson,
                        proton_cut_passed_resonant, proton_cut_passed_nonreson, mass_cut,
                        save_path):
    nbins = 100
    resonant = ROOT.TH2F("resonant", "Proton Angles Resonant", nbins, 0, 2*math.pi, nbins, 0, 2*math.pi)
    nonreson = ROOT.TH2F("nonreson", "Proton Angles Nonresonant", nbins, 0, 2*math.pi, nbins, 0, 2*math.pi)

    for angle, cut1 in zip(proton_angles_resonant, proton_cut_passed_resonant):
        if cut1:
            resonant.Fill(angle[0], angle[1])
    for angle, cut1, cut2 in zip(proton_angles_nonreson, proton_cut_passed_nonreson, mass_cut):
        if cut1 and cut2:
            nonreson.Fill(angle[0], angle[1])

    for h in (resonant, nonreson):
        h.GetXaxis().SetTitle("Proton 1 Angle [rad]")
        h.GetYaxis().SetTitle("Proton 2 Angle [rad]")

    # Glueball mass vs proton angle
    canvas_proton_angle = ROOT.TCanvas("canvas_proton_angle", "Outgoing Proton Anglese", 1200, 500)
    canvas_proton_angle.Divide(2, 1)
    
    canvas_proton_angle.cd(1)
    resonant.Draw("COLZ")
    ROOT.gPad.SetTitle("Resonant")
    canvas_proton_angle.cd(2)
    nonreson.Draw("COLZ")
    ROOT.gPad.SetTitle("Non-resonant")
    
    canvas_proton_angle.SaveAs(str(save_path / "proton_angle_vs_angle.png"))
    

def main():
    root_folder = Path(__file__).parent.parent.parent
    root_path_resonant = root_folder / "data" / "dimeMC" / "exrec_resonant.root"
    root_path_nonreson = root_folder / "data" / "dimeMC" / "exrec_nonreson.root"
    save_path = root_folder / "plots" / "dimeMC" / "kinematics_combined"

    # make sure path exists
    save_path.mkdir(parents=True, exist_ok=True)

    pions_resonant, rhos_resonant, glues_resonant, \
        proton_cut_passed_resonant, _, proton_angles_resonant = get_particles(root_path_resonant)
    pions_nonreson, rhos_nonreson, glues_nonreson, \
        proton_cut_passed_nonreson, mass_cut, proton_angles_nonreson = get_particles(root_path_nonreson)

    plot_kinematics(pions_resonant, pions_nonreson,
                    proton_cut_passed_resonant, proton_cut_passed_nonreson, mass_cut,
                    "#pi^{+} and #pi^{-}", save_path)
    plot_kinematics(rhos_resonant, rhos_nonreson,
                    proton_cut_passed_resonant, proton_cut_passed_nonreson, mass_cut,
                    "#rho-meson", save_path)
    plot_kinematics(glues_resonant, glues_nonreson,
                    proton_cut_passed_resonant, proton_cut_passed_nonreson, mass_cut,
                    "Glueball", save_path)
    
    plot_angle_vs_mass(glues_resonant, glues_nonreson, proton_angles_resonant, proton_angles_nonreson,
                proton_cut_passed_resonant, proton_cut_passed_nonreson, mass_cut,
                save_path)
    
    plot_angle_vs_angle(proton_angles_resonant, proton_angles_nonreson,
                        proton_cut_passed_resonant, proton_cut_passed_nonreson, mass_cut,
                        save_path)


if __name__ == '__main__':
    main()