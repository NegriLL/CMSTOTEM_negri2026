import sys
from pathlib import Path
import ROOT

sys.path.append(str(Path(__file__).parent.parent / "utilities"))
from cuts_string import dime_fltr, data_fltr #type: ignore

def str_to_bool(value: str) -> bool:
    return value.strip().lower() in ("true", "1", "yes")

def get_args_joint(argv):
    if len(argv) < 7:
        print("Error: Expected 7 inputs")
        print("[data] [dime resonant] [save folder] [title] [dime nonresonant]")
        sys.exit(1)

    data_file = Path(argv[1])
    resonant_file = Path(argv[2])
    save_path = Path(argv[3])
    title = argv[4]
    filtered = str_to_bool(argv[5])

    productions = {}
    for i in range(6, len(argv)):
        p = Path(argv[i])
        # get production type at the start of filename
        production = p.stem.split('_')[0]
        productions[production] = p

    # make sure savepath exists
    save_path.parent.mkdir(parents=True, exist_ok=True)

    if filtered:
        data = ROOT.RDataFrame("tree", str(data_file)).Filter(data_fltr())
        resonant = ROOT.RDataFrame("particles", str(resonant_file)).Filter(dime_fltr())
        nonreson = {}
        for key in productions:
            nonreson[key] = ROOT.RDataFrame("particles", str(productions[key])).Filter(dime_fltr())
    else:
        data = ROOT.RDataFrame("tree", str(data_file))
        resonant = ROOT.RDataFrame("particles", str(resonant_file))
        nonreson = {}
        for key in productions:
            nonreson[key] = ROOT.RDataFrame("particles", str(productions[key]))

    return data, resonant, nonreson, save_path, title