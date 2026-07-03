#!/usr/bin/env python3

import ROOT
import sys
import math

from pathlib import Path
import numpy as np

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


def eta_together(data, resonant, nonresonant, save_path, title):
    nbins = 100
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
    nonreson_hist = make_hist(nonresonant, "eta_nonreson")

    data_hist = data_hist.GetValue()
    resonant_hist = resonant_hist.GetValue()
    nonreson_hist = nonreson_hist.GetValue()

    for h in (data_hist, resonant_hist, nonreson_hist):
        max_val = h.GetMaximum()
        if max_val != 0:
            h.Scale(1.0 / max_val)

    data_hist.SetLineColor(ROOT.kBlue)
    data_hist.SetLineWidth(3)
    data_hist.SetTitle(title)

    resonant_hist.SetLineColor(ROOT.kGreen + 2)
    resonant_hist.SetLineWidth(3)

    nonreson_hist.SetLineColor(ROOT.kRed)
    nonreson_hist.SetLineWidth(3)

    ymax = max(h.GetMaximum() for h in (data_hist, resonant_hist, nonreson_hist))
    data_hist.SetMaximum(ymax * 1.1)

    c = ROOT.TCanvas("c", "c", 1600, 1200)
    data_hist.Draw("HIST")
    resonant_hist.Draw("HIST SAME")
    nonreson_hist.Draw("HIST SAME")

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
    
    fltr_acceptance = ( 
    f"(({proton_py_min} < fabs(p1_out_py)) && (fabs(p1_out_py) < {proton_py_max})) && "
    f"(({proton_py_min} < fabs(p2_out_py)) && (fabs(p2_out_py) < {proton_py_max}))"
    )
    fltr_mass = (f"(({mass_min} < primary_m[0]) && (primary_m[0] < {mass_max})) && "
                 f"(({mass_min} < primary_m[1]) && (primary_m[1] < {mass_max}))")

    fltr_data = (f"fabs(px_diff) < {px_cut} && "
                 f"fabs(py_diff) < {py_cut} && "
                 f"fabs(trk_p[0]) < {p_cut} && "
                 f"fabs(trk_p[1]) < {p_cut} && "
                 f"fabs(trk_p[2]) < {p_cut} && "
                 f"fabs(trk_p[3]) < {p_cut} && "
                 f"{mass_min} < pair_masses[0][0] && pair_masses[0][0] < {mass_max} && "
                 f"{mass_min} < pair_masses[0][1] && pair_masses[0][1] < {mass_max}")

    data = ROOT.RDataFrame("tree", str(data_file)).Filter(fltr_data)
    resonant = ROOT.RDataFrame("particles", str(resonant_file)).Filter(f'{fltr_acceptance} && {fltr_mass}')
    nonreson = ROOT.RDataFrame("particles", str(nonresonant_file)).Filter(f'{fltr_acceptance} && {fltr_mass}')
    
    eta_together(data, resonant, nonreson, save_path, title)
    

if __name__ == '__main__':
    main()