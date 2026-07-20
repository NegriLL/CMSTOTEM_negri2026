#!/usr/bin/env python3

import ROOT
import sys

from pathlib import Path

# Making sure graphs don't open and annoy me
ROOT.gROOT.SetBatch(True)

sys.path.append(str(Path(__file__).parent.parent / "utilities"))
from arg_handler import get_args_joint #type: ignore
from plotter import plot_joint #type: ignore


def pt_together(data, resonant, nonreson):
    nbins = 100
    xmin = -0.5
    xmax = 2

    model = ("h", "Normalized Data and DimeMC pT Comparison", nbins, xmin, xmax)
    pt_calc = "sqrt(pow(Sum(produced_px[abs(produced_id) == 211]), 2) + pow(Sum(produced_py[abs(produced_id) == 211]), 2))"

    resonant = resonant.Define("pt", pt_calc)
    for key in nonreson:
        nonreson[key] = nonreson[key].Define("pt", pt_calc)
    data_hist = data.Histo1D(("data",) + model[1:], "alltrk_pt")
    resonant_hist = resonant.Histo1D(("reson",) + model[1:], "pt")
    nonreson_hists = {}
    for key in nonreson:
        nonreson_hists[key] = nonreson[key].Histo1D(("nonreson",) + model[1:], "pt")

    return data_hist, resonant_hist, nonreson_hists


def main():
    data, resonant, nonreson, save_path, title = get_args_joint(sys.argv)
    data_hist, resonant_hist, nonreson_hists = pt_together(data, resonant, nonreson)
    plot_joint(data_hist, resonant_hist, nonreson_hists, save_path, title)
    
    

if __name__ == '__main__':
    main()