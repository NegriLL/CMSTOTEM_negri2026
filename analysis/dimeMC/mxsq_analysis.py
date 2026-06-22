import ROOT
import numpy as np

from pathlib import Path

def import_files(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    mxsq = []
    mx = []
    weight = []
    BW_weight = []
    zmat = []
    norm = []

    for i, line in enumerate(lines):
        parts = line.strip().split()

        try:
            mxsq.append(float(parts[0]))
            mx.append(np.sqrt(float(parts[0])))
        except:
            print(f"Error appending mxsq at line {i}")
            mxsq.append(0)

        try:
            weight.append(float(parts[1]))
        except:
            print(f"Error appending weight at line {i}")
            weight.append(0)

        try:
            BW_weight.append(float(parts[2]))
        except:
            print(f"Error appending BW_weight at line {i}")
            BW_weight.append(0)

        try:
            norm.append(float(parts[3]))
        except:
            print(f"Error appending zmat at line {i}")
            zmat.append(0)

        try:
            zmat.append(float(parts[4]))
        except:
            print(f"Error appending norm at line {i}")
            zmat.append(0)

    return mxsq, mx, weight, BW_weight, zmat, norm


def plot_graphs(mxsq, mx, weight, bw_weight, save_path):
    canvas = ROOT.TCanvas("canvas", "mxsq analysis", 1000, 1500)
    
    pad1 = ROOT.TPad("pad1", "pad1", 0, 0.8, 1, 1)
    pad2 = ROOT.TPad("pad2", "pad2", 0, 0.6, 1, 0.8)
    pad3 = ROOT.TPad("pad3", "pad3", 0, 0.4, 1, 0.6)
    pad4 = ROOT.TPad("pad4", "pad4", 0, 0.2, 1, 0.4)
    pad5 = ROOT.TPad("pad5", "pad5", 0, 0, 1, 0.2)
    
    pad1.Draw()
    pad2.Draw()
    pad3.Draw()
    pad4.Draw()
    pad5.Draw()
    
    mx_min = min(mxsq)
    mx_max = max(mxsq)

    nbins = 200

    hist_mxsq = ROOT.TH1F("hist_mxsq", "mxsq Distribution", nbins, mx_min - 0.5, mx_max + 0.5)
    hist_mx = ROOT.TH1F("hist_mx", "mx Distribution", nbins, np.sqrt(mx_min - 0.5), np.sqrt(mx_max + 0.5))
    hist_weight = ROOT.TH1F("hist_weight", "weight Distribution", nbins, -0.5, 10)
    hist_bw_weight = ROOT.TH1F("hist_bw_weight", "BW_weight Distribution", nbins, 0, 5)
    
    # Calculate combined weight * BW_weight distribution
    combined_weight = [w * bw for w, bw in zip(weight, bw_weight)]
    hist_combined = ROOT.TH1F("hist_combined", "weight * BW_weight Distribution", nbins, -0.5, 3)
    
    hist_mxsq.SetLineWidth(2)
    hist_mx.SetLineWidth(2)
    hist_weight.SetLineWidth(2)
    hist_bw_weight.SetLineWidth(2)
    hist_combined.SetLineWidth(2)
    
    for val in mxsq:
        hist_mxsq.Fill(val)
    for val in mx:
        hist_mx.Fill(val)
    for val in weight:
        hist_weight.Fill(val)
    for val in bw_weight:
        hist_bw_weight.Fill(val)
    for val in combined_weight:
        hist_combined.Fill(val)
    
    pad1.cd()
    pad1.SetBottomMargin(0.1)
    hist_mxsq.Draw()

    pad2.cd()
    pad2.SetBottomMargin(0.1)
    pad2.SetTopMargin(0.1)
    hist_mx.Draw()
    
    pad3.cd()
    pad3.SetBottomMargin(0.1)
    pad3.SetTopMargin(0.1)
    hist_weight.Draw()
    
    pad4.cd()
    pad4.SetBottomMargin(0.1)
    pad4.SetTopMargin(0.1)
    hist_bw_weight.Draw()
    
    pad5.cd()
    pad5.SetTopMargin(0.1)
    hist_combined.Draw()
    
    canvas.SaveAs(str(save_path / "mxsq_analysis_1D.png"))


def plot_2d_histograms(xval, yval, title, xname, yname, save_path):
    canvas = ROOT.TCanvas("canvas2d", f"{xname} vs {yname}", 1000, 800)

    x_min = min(xval)
    x_max = max(xval)
    y_min = min(yval)
    y_max = max(yval)
    
    nbins = 200
    
    hist = ROOT.TH2D("hist_2d", title, nbins, x_min - 0.1, x_max + 0.1, nbins, y_min - 0.1, y_max + 0.1)
    hist.SetXTitle(xname)
    hist.SetYTitle(yname)
    
    for x_val, y_val in zip(xval, yval):
        hist.Fill(x_val, y_val)
    
    hist.Draw("colz")
    canvas.SaveAs(str(save_path / f"{title}.png"))


def main():
    file_path = Path(__file__).parent.parent / "dimemc_vsm" / "mxsq.out"
    save_path = Path(__file__).parent.parent / "plots" / "conservation"

    mxsq, mx, weight, bw_weight, zmat, norm = import_files(file_path)
    plot_graphs(mxsq, mx, weight, bw_weight, save_path)
    plot_2d_histograms(mxsq, bw_weight, "mxsq_analysis_2D", "mxsq", "BW_weight", save_path)
    plot_2d_histograms(zmat, bw_weight, "zmat_analysis_2D", "zmat", "BW_weight", save_path)
    plot_2d_histograms(norm, bw_weight, "norm_analysis_2D", "norm", "BW_weight", save_path)


if __name__ == "__main__":
    main()