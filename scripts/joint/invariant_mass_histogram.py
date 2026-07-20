#!/usr/bin/env python3

import ROOT
import sys

from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "utilities"))
from arg_handler import get_args_joint #type: ignore
from plotter import plot_joint #type: ignore

# Making sure graphs don't open and annoy me
ROOT.gROOT.SetBatch(True)


def invariant_mass_together(data, resonant, nonreson):
    nbins = 100
    xmin = 1.9
    xmax = 2.6

    model = ("h", "Normalized Data and DimeMC Invmass Comparison", nbins, xmin, xmax)

    data_hist = data.Histo1D(("data",) + model[1:], "inv_mass")
    resonant_hist = resonant.Histo1D(("reson",) + model[1:], "inv_mass")
    nonreson_hists = {}
    for key in nonreson:
        nonreson_hists[key] = nonreson[key].Histo1D(("nonreson",) + model[1:], "inv_mass")

    return data_hist, resonant_hist, nonreson_hists


def main():
    data, resonant, nonreson, save_path, title = get_args_joint(sys.argv)
    data_hist, resonant_hist, nonreson_hists = invariant_mass_together(data, resonant, nonreson)
    plot_joint(data_hist, resonant_hist, nonreson_hists, save_path, title)
    

if __name__ == '__main__':
    main()