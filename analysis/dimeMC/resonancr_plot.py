import ROOT
import numpy as np
from pathlib import Path

def read_data(filename):
    x_values = []
    y_values = []
    
    with open(filename, 'r') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if line:
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        x = float(parts[0])
                        y = float(parts[1])
                        x_values.append(x)
                        y_values.append(y)
                    except ValueError:
                        print(f"Invalid value in line {i}")
    
    return np.array(x_values), np.array(y_values)

def create_histogram(x_values, y_values, hist_name="hist", title="Distribution from output.dat"):
    if len(x_values) > 1:
        bin_width = x_values[1] - x_values[0]
        bin_edges = [x_values[0] - bin_width/2]
        for i in range(len(x_values) - 1):
            bin_edges.append(x_values[i] + bin_width/2)
        bin_edges.append(x_values[-1] + bin_width/2)
    else:
        bin_edges = [x_values[0] - 0.1, x_values[0] + 0.1]
    
    hist = ROOT.TH1F(hist_name, title, len(x_values), np.array(bin_edges))
    
    for i, y in enumerate(y_values):
        hist.SetBinContent(i + 1, y)
    
    return hist

def main():
    input_file = Path(__file__).parent.parent / "dimemc_vsm" / "output.dat"

    x_values, y_values = read_data(input_file)
    
    hist = create_histogram(x_values, y_values, 
                            hist_name="output_histogram",
                            title="Distribution from output.dat")
    
    canvas = ROOT.TCanvas("c1", "Histogram from output.dat", 800, 600)
    hist.Draw("HIST")
    hist.GetXaxis().SetTitle("Value")
    hist.GetYaxis().SetTitle("Frequency")
    
    canvas.Update()
    canvas.SaveAs("output_histogram.pdf")
    canvas.SaveAs("output_histogram.png")
    canvas.SaveAs("output_histogram.root")
    
    ROOT.gApplication.Run()

if __name__ == "__main__":
    main()
