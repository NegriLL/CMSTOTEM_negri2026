#!/usr/bin/env python3

import ROOT
import sys
import math

from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "utilities"))
from arg_handler import get_args_joint #type: ignore
from plotter import plot_joint #type: ignore

# Making sure graphs don't open and annoy me
ROOT.gROOT.SetBatch(True)


def proton_angle_together(data, resonant, nonresonant):
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
    nonreson_hists = {}
    for key in nonresonant:
        nonreson_hists[key] = make_hist(nonresonant[key], "proton_angle_nonreson")

    return data_hist, resonant_hist, nonreson_hists


def main():
    data, resonant, nonreson, save_path, title = get_args_joint(sys.argv)
    data_hist, resonant_hist, nonreson_hists = proton_angle_together(data, resonant, nonreson)
    plot_joint(data_hist, resonant_hist, nonreson_hists, save_path, title)
    

if __name__ == '__main__':
    main()