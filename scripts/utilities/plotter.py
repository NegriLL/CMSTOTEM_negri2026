import ROOT

def plot_joint(data_hist, resonant_hist, nonreson_hists, title, save_path):
    data_hist = data_hist.GetValue()
    resonant_hist = resonant_hist.GetValue()
    nonreson_hists = [hist.GetValue() for hist in nonreson_hists]

    for h in (data_hist, resonant_hist, *nonreson_hists):
        max_val = h.GetMaximum()
        if max_val != 0:
            h.Scale(1.0 / max_val)

    ROOT.gStyle.SetPalette(ROOT.kRainbow)

    data_hist.SetLineWidth(3)
    data_hist.SetTitle(title)

    resonant_hist.SetLineWidth(3)

    nonreson_list = [nonreson_hists[key] for key in nonreson_hists]

    for hist in nonreson_list:
        hist.SetLineWidth(3)

    ymax = max(h.GetMaximum() for h in (data_hist, resonant_hist, *nonreson_list))
    data_hist.SetMaximum(ymax * 1.1)

    c = ROOT.TCanvas("c", "c", 1600, 1200)
    for hist in nonreson_list:
        hist.Draw("HIST PLC SAME")
    resonant_hist.Draw("HIST PLC SAME")
    data_hist.Draw("HIST PLC SAME")

    legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
    legend.AddEntry(data_hist, "Data", "l")
    legend.AddEntry(resonant_hist, "DimeMC Resonant", "l")
    for key in nonreson_hists:
        legend.AddEntry(hist, f"DimeMC {key}", "l")
    legend.Draw()

    c.Draw()
    c.SaveAs(str(save_path))