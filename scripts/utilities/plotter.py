import ROOT

def plot_joint(data_hist, resonant_hist, nonreson_hists, save_path, title):
    data_hist = data_hist.GetValue()
    resonant_hist = resonant_hist.GetValue()
    nonreson_list = [nonreson_hists[key].GetValue() for key in nonreson_hists]

    for h in (data_hist, resonant_hist, *nonreson_list):
        max_val = h.GetMaximum()
        if max_val != 0:
            h.Scale(1.0 / max_val)

    data_hist.SetLineWidth(3)
    data_hist.SetLineStyle(1)
    data_hist.SetTitle(title)

    resonant_hist.SetLineWidth(3)
    resonant_hist.SetLineStyle(9)

    for hist in nonreson_list:
        hist.SetLineWidth(3)
        hist.SetLineStyle(7)

    ymax = max(h.GetMaximum() for h in (data_hist, resonant_hist, *nonreson_list))
    data_hist.SetMaximum(ymax * 1.1)

    c = ROOT.TCanvas("c", "c", 1600, 1200)
    
    ROOT.gStyle.SetPalette(ROOT.kBlueRedYellow)
    data_hist.Draw("HIST")
    for hist in nonreson_list:
        hist.Draw("HIST PLC SAME")
    resonant_hist.Draw("HIST PLC SAME")

    legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
    legend.AddEntry(data_hist, "Data", "l")
    legend.AddEntry(resonant_hist, "DimeMC Resonant", "l")
    for key, hist in zip(nonreson_hists, nonreson_list):
        legend.AddEntry(hist, f"DimeMC {key}", "l")
    legend.Draw()

    c.Draw()
    c.SaveAs(str(save_path))