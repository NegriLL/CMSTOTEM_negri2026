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
template <typename Tpx, typename Tpy, typename Tpz>
ROOT::VecOps::RVec<double> KaonEtas(int ntrk, const Tpx& px, const Tpy& py, const Tpz& pz) {
    ROOT::VecOps::RVec<double> etas;
    for (int i = 0; i < ntrk; i++) {
        TVector3 p(px[i], py[i], pz[i]);
        etas.push_back(p.Eta());
    }
    return etas;
}
""")

def kaon_eta_together(resonant, nonresonant):
    nbins = 50
    xmin = -5
    xmax = 5

    def make_hist(df, histname):
        df = df.Define(
            "kaon_etas",
            "KaonEtas((int)ntrk, produced_px, produced_py, produced_pz)"
        )
        return df.Histo1D((histname, histname, nbins, xmin, xmax), "kaon_etas")

    resonant_hist = make_hist(resonant, "eta_reson")
    nonreson_hists = {"phi": make_hist(nonresonant["phi"], f"eta_nonreson")}

    return resonant_hist, nonreson_hists


def main():
    data, resonant, nonreson, save_path, title = get_args_joint(sys.argv)
    resonant_hist, nonreson_hists = kaon_eta_together(resonant, nonreson)
    plot_joint(data, resonant_hist, nonreson_hists, save_path, title, plot_data=False)


if __name__ == '__main__':
    main()
