import ROOT
import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent.parent / "config.yaml"

def load_config(path=CONFIG_PATH):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def plot_joint(data_hist, resonant_hist, nonreson_hists, save_path, title):
    data_hist = data_hist.GetValue()
    resonant_hist = resonant_hist.GetValue()
    nonreson_list = [nonreson_hists[key].GetValue() for key in nonreson_hists]

    for h in (data_hist, resonant_hist, *nonreson_list):
        max_val = h.GetMaximum()
        if max_val != 0:
            h.Scale(1.0 / max_val)

    config = load_config()
    line_width = config["line_width"]
    line_style_data = config["line_style_data"]
    line_style_resonant = config["line_style_resonant"]
    line_style_nonresonant = config["line_style_nonresonant"]
    image_size_x = config["image_size"]["x"]
    image_size_y = config["image_size"]["y"]
    legend_x1 = config["legend"]["x1"]
    legend_y1 = config["legend"]["y1"]
    legend_x2 = config["legend"]["x2"]
    legend_y2 = config["legend"]["y2"]

    data_hist.SetTitle(title)
    data_hist.SetLineWidth(line_width)
    data_hist.SetLineStyle(line_style_data)

    resonant_hist.SetLineWidth(line_width)
    resonant_hist.SetLineStyle(line_style_resonant)

    for hist in nonreson_list:
        hist.SetLineWidth(line_width)
        hist.SetLineStyle(line_style_nonresonant)

    ymax = max(h.GetMaximum() for h in (data_hist, resonant_hist, *nonreson_list))
    data_hist.SetMaximum(ymax * 1.1)

    c = ROOT.TCanvas("c", "c", image_size_x, image_size_y)
    
    ROOT.gStyle.SetPalette(ROOT.kBlueRedYellow)
    data_hist.Draw("HIST")
    for hist in nonreson_list:
        hist.Draw("HIST PLC SAME")
    resonant_hist.Draw("HIST PLC SAME")

    legend = ROOT.TLegend(legend_x1,
                          legend_y1,
                          legend_x2,
                          legend_y2)
    
    legend.AddEntry(data_hist, "Data", "l")
    legend.AddEntry(resonant_hist, "DimeMC Resonant", "l")
    for key, hist in zip(nonreson_hists, nonreson_list):
        legend.AddEntry(hist, f"DimeMC {key}", "l")
    legend.Draw()

    c.Draw()
    c.SaveAs(str(save_path))