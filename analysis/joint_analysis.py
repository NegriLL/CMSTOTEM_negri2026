#!/usr/bin/env python3

import ROOT
import sys

from pathlib import Path
import numpy as np

# Making sure graphs don't open and annoy me
ROOT.gROOT.SetBatch(True)

def invariant_mass_together(data_file, resonant_file, nonresonant_file, save_path, title):
    proton_py_min = 0.18
    proton_py_max = 0.68

    acceptance = ( 
    f"(({proton_py_min} < fabs(p1_out_py)) && (fabs(p1_out_py) < {proton_py_max})) && "
    f"(({proton_py_min} < fabs(p2_out_py)) && (fabs(p2_out_py) < {proton_py_max}))"
    )

    data = ROOT.RDataFrame("tree", str(data_file)).Filter("ntrk == 4")
    resonant = ROOT.RDataFrame("particles", str(resonant_file)).Filter(acceptance)
    nonreson = ROOT.RDataFrame("particles", str(nonresonant_file)).Filter(acceptance)

    nbins = 200
    xmin = 0
    xmax = 5

    model = ("h", "Normalized Data and DimeMC Invmass Comparison", nbins, xmin, xmax)

    data_hist = data.Histo1D(("data",) + model[1:], "inv_mass")
    resonant_hist = resonant.Histo1D(("reson",) + model[1:], "inv_mass")
    nonreson_hist = nonreson.Histo1D(("nonreson",) + model[1:], "inv_mass")

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

    # Draw
    c = ROOT.TCanvas("c", "c", 1600, 1200)
    data_hist.Draw("HIST")
    resonant_hist.Draw("HIST SAME")
    nonreson_hist.Draw("HIST SAME")

    # Make sure y-axis fits all three
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
        print("Error: Expeted inputs")
        print("[data] [dime resonant] [dime nonresonant] [save folder] [title]")
        sys.exit(1)

    data_file = Path(sys.argv[1])
    dime_resonant_file = Path(sys.argv[2])
    dime_nonresonant_file = Path(sys.argv[3])
    save_path = Path(sys.argv[4])
    title = sys.argv[5]

    save_path.parent.mkdir(parents=True, exist_ok=True)

    invariant_mass_together(data_file, dime_resonant_file, dime_nonresonant_file, save_path, title)

if __name__ == '__main__':
    main()