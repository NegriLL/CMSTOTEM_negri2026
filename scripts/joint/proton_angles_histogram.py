#!/usr/bin/env python3

import ROOT
import sys
import math

from pathlib import Path
import numpy as np

sys.path.append(str(Path(__file__).parent.parent / "utilities"))
from cuts_string import dime_fltr, data_fltr #type: ignore

# Making sure graphs don't open and annoy me
ROOT.gROOT.SetBatch(True)


def proton_angle_together(data, resonant, nonresonant, save_path, title):
    nbins = 100
    xmin = 0
    xmax = math.pi

    data = data.Define("diff",
        "double phi1 = atan2(ThyR, ThxR);"
        "double phi2 = atan2(ThyL, ThxL);"
        "double d = fabs(phi1 - phi2);"
        "return d > M_PI ? 2*M_PI - d : d;")
    data_hist = data.Histo1D(("proton_angle_data", "proton_angle_data", nbins, xmin, xmax), "diff")

    def make_hist(df, histname):
        df = df.Define("diff",
            "TLorentzVector p1(p1_out_px, p1_out_py, p1_out_pz, p1_out_e);"
            "TLorentzVector p2(p2_out_px, p2_out_py, p2_out_pz, p2_out_e);"
            "double d = fabs(p1.Phi() - p2.Phi());"
            "return d > M_PI ? 2*M_PI - d : d;")
        return df.Histo1D((histname, histname, nbins, xmin, xmax), "diff")

    resonant_hist = make_hist(resonant, "proton_angle_reson")
    nonreson_hist = make_hist(nonresonant, "proton_angle_nonreson")

    data_hist = data_hist.GetValue()
    resonant_hist = resonant_hist.GetValue()
    nonreson_hist = nonreson_hist.GetValue()

    for h in (data_hist, resonant_hist, nonreson_hist):
        max_val = h.GetMaximum()
        if max_val != 0:
            h.Scale(1.0 / max_val)

    data_hist.SetLineColor(ROOT.kBlue)
    data_hist.SetLineWidth(2)
    data_hist.SetTitle(title)
    data_hist.SetLineWidth(3)

    resonant_hist.SetLineColor(ROOT.kGreen + 2)
    resonant_hist.SetLineWidth(2)
    resonant_hist.SetLineWidth(3)

    nonreson_hist.SetLineColor(ROOT.kRed)
    nonreson_hist.SetLineWidth(2)
    nonreson_hist.SetLineWidth(3)

    c = ROOT.TCanvas("c", "c", 1600, 1200)
    nonreson_hist.Draw("HIST")
    resonant_hist.Draw("HIST SAME")
    data_hist.Draw("HIST SAME")

    ymax = max(h.GetMaximum() for h in (data_hist, resonant_hist, nonreson_hist))
    data_hist.SetMaximum(ymax * 1.1)

    legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
    legend.AddEntry(data_hist, "Data", "l")
    legend.AddEntry(resonant_hist, "DimeMC Resonant", "l")
    legend.AddEntry(nonreson_hist, "DimeMC Nonresonant", "l")
    legend.Draw()

    c.Draw()
    c.SaveAs(str(save_path))



def main():
    if len(sys.argv) < 6:
        print("Error: Expected inputs")
        print("[data] [dime resonant] [dime nonresonant] [save folder] [title]")
        sys.exit(1)

    data_file = Path(sys.argv[1])
    resonant_file = Path(sys.argv[2])
    nonresonant_file = Path(sys.argv[3])
    save_path = Path(sys.argv[4])
    title = sys.argv[5]

    save_path.parent.mkdir(parents=True, exist_ok=True)

    # Opening the files and filtering
    proton_py_min = 0.18
    proton_py_max = 0.68
    rho_mass = 0.770
    mass_interval = 0.062

    px_cut = 0.130
    py_cut = 0.060
    p_cut = 1
    mass_min = rho_mass - mass_interval
    mass_max = rho_mass + mass_interval

    data = ROOT.RDataFrame("tree", str(data_file)).Filter(data_fltr())
    resonant = ROOT.RDataFrame("particles", str(resonant_file)).Filter(dime_fltr())
    nonreson = ROOT.RDataFrame("particles", str(nonresonant_file)).Filter(dime_fltr())
    
    proton_angle_together(data, resonant, nonreson, save_path, title)
    

if __name__ == '__main__':
    main()