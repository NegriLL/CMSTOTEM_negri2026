#!/usr/bin/env python3

import ROOT
import sys

from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "utilities"))
from arg_handler import get_args_joint #type: ignore
from plotter import plot_joint #type: ignore

# Making sure graphs don't open and annoy me
ROOT.gROOT.SetBatch(True)


ROOT.gInterpreter.Declare("""
template <typename Tpx, typename Tpy>
ROOT::VecOps::RVec<double> KaonPts(int ntrk, const Tpx& px, const Tpy& py) {
    ROOT::VecOps::RVec<double> pts;
    for (int i = 0; i < ntrk; i++) {
        pts.push_back(sqrt(px[i]*px[i] + py[i]*py[i]));
    }
    return pts;
}
""")


def kaon_pt_together(resonant, nonresonant):
    nbins = 100
    xmin = -0.5
    xmax = 2

    def make_hist(df, histname):
        df = df.Define(
            "kaon_pts",
            "KaonPts((int)ntrk, produced_px, produced_py)"
        )
        return df.Histo1D((histname, histname, nbins, xmin, xmax), "kaon_pts")

    resonant_hist = make_hist(resonant, "pt_reson")
    nonreson_hists = {"phi": make_hist(nonresonant["phi"], "pt_nonreson")}

    return resonant_hist, nonreson_hists


def main():
    data, resonant, nonreson, save_path, title = get_args_joint(sys.argv)
    resonant_hist, nonreson_hists = kaon_pt_together(resonant, nonreson)
    plot_joint(data, resonant_hist, nonreson_hists, save_path, title, plot_data=False)


if __name__ == '__main__':
    main()