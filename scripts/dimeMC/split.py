#!/usr/bin/env python3

import ROOT
import sys

from pathlib import Path


def split_file(dime_file, save_path):
    df = ROOT.RDataFrame("particles", str(dime_file))

    save_path = save_path / f'{dime_file.stem.replace}_D.root'

    # Find the quadrant of the angle and get the difference between them
    df.Define("q_diff",
            "TLorentzVector p1(p1_out_px, p1_out_py, p1_out_pz, p1_out_e);"
            "TLorentzVector p2(p2_out_px, p2_out_py, p2_out_pz, p2_out_e);"
            "int q1 = int( p1.Phi()/ (M_pi/2) );"
            "int q2 = int( p2.Phi()/ (M_pi/2) );"
            "return abs(q1 - q2);")
    
    # Diagonal events happen when the quadrants differ by 2. Parallel otherwise.
    df_D = df.Filter("q_diff == 2")
    df_P = df.Filter("q_diff != 2")

    df_D.Snapshot("particles", str(save_path).replace("_A", "_D"))
    df_P.Snapshot("particles", str(save_path).replace("_A", "_D"))

def main():
    data_file = Path(sys.argv[1])

    save_path = Path("data/dimeMC")
    save_path.mkdir(parents=True, exist_ok=True)

    split_file(data_file, save_path)



if __name__ == '__main__':
    main()