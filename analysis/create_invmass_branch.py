#!/usr/bin/env python3

import ROOT
import sys

from pathlib import Path

def create_invmass_branch(file, save_path, mass_pion = 0.13957):
    df = ROOT.RDataFrame("tree", str(file)) 

    invmass = f"ROOT::VecOps::InvariantMass(trk_pt, trk_eta, trk_phi, ROOT::RVecF(ntrk, {mass_pion}))"
    df = df.Define("inv_mass", invmass)

    df.Snapshot("tree", str(save_path))


def main():
    if len(sys.argv) != 3:
        print("Error: Incorrect number of arguments. Need 2 files.")
        sys.exit(1)

    file = Path(sys.argv[1])
    save_path = Path(sys.argv[2])
    save_path.parent.mkdir(parents=True, exist_ok=True)

    create_invmass_branch(file, save_path)


if __name__ == "__main__":
    main()