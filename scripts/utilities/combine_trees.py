#!/usr/bin/env python3

import ROOT
import sys

from pathlib import Path

def combineTrees(file_list, save_path):
    df = ROOT.RDataFrame("tree", [str(f) for f in file_list])
    # This filter is applied in all our calculations so it can be here already
    df_filtered = df.Filter("ntrk == 4")

    df_filtered.Snapshot("tree", str(save_path))


def main():
    # Iterate through all input files
    file_list = []
    for i in range(1, len(sys.argv) - 1):
        file_list.append(Path(sys.argv[i]))
    # Output in the last entry
    save_path = Path(sys.argv[-1])
    save_path.parent.mkdir(parents=True, exist_ok=True)

    combineTrees(file_list, save_path)

if __name__ == "__main__":
    main()