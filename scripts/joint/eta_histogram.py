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
template <typename Tpt, typename Teta, typename Tphi>
double ComputeTotalEtaPtEtaPhiM(int ntrk, const Tpt& pt, const Teta& eta, const Tphi& phi, double mass) {
    TLorentzVector total;
    for (int i = 0; i < ntrk; i++) {
        TLorentzVector track;
        track.SetPtEtaPhiM(pt[i], eta[i], phi[i], mass);
        total += track;
    }
    return total.Eta();
}

template <typename Tid, typename Tpx, typename Tpy, typename Tpz, typename Te>
double ComputeTotalEtaPxPyPzE(int ntrk, const Tid& id, const Tpx& px, const Tpy& py, const Tpz& pz, const Te& e) {
    TLorentzVector total;
    for (int i = 0; i < ntrk; i++) {
        if (std::abs(id[i]) == 211) {
            TLorentzVector particle(px[i], py[i], pz[i], e[i]);
            total += particle;
        }
    }
    return total.Eta();
}
""")


def eta_together(data, resonant, nonresonant):
    nbins = 50
    xmin = -5
    xmax = 5
    pion_mass = 0.13957

    data = data.Define(
        "eta_val",
        f"ComputeTotalEtaPtEtaPhiM((int)ntrk, trk_pt, trk_eta, trk_phi, {pion_mass})"
    )
    data_hist = data.Histo1D(("eta_data", "eta_data", nbins, xmin, xmax), "eta_val")

    def make_hist(df, histname):
        df = df.Define(
            "eta_val",
            "ComputeTotalEtaPxPyPzE((int)ntrk, produced_id, produced_px, produced_py, produced_pz, produced_e)"
        )
        return df.Histo1D((histname, histname, nbins, xmin, xmax), "eta_val")

    resonant_hist = make_hist(resonant, "eta_reson")
    nonreson_hists = {}
    for key in nonresonant:
        nonreson_hists[key] = make_hist(nonresonant[key], f"{key}_eta_nonreson")

    return data_hist, resonant_hist, nonreson_hists


def main():
    data, resonant, nonreson, save_path, title = get_args_joint(sys.argv)
    data_hist, resonant_hist, nonreson_hists = eta_together(data, resonant, nonreson)
    plot_joint(data_hist, resonant_hist, nonreson_hists, save_path, title)
    

if __name__ == '__main__':
    main()