import yaml
from pathlib import Path
 
CONFIG_PATH = Path(__file__).parent.parent.parent / "config.yaml"

def load_config(path=CONFIG_PATH):
    with open(path, "r") as f:
        return yaml.safe_load(f)

config = load_config()

proton_py_min = config["acceptance"]["py_min"]
proton_py_max = config["acceptance"]["py_max"]

rho_mass = config["mass"]["rho_mass"]
mass_interval = config["mass"]["mass_interval"]
inv_mass_min = config["mass"]["inv_mass_min"]
inv_mass_max = config["mass"]["inv_mass_max"]

px_cut = config["momentum"]["px_cut"]
py_cut = config["momentum"]["py_cut"]
p_cut = config["momentum"]["p_cut"]

mass_min = rho_mass - mass_interval
mass_max = rho_mass + mass_interval

def dime_fltr():
    fltr_acceptance = ( 
    f"(({proton_py_min} < fabs(p1_out_py)) && (fabs(p1_out_py) < {proton_py_max})) && "
    f"(({proton_py_min} < fabs(p2_out_py)) && (fabs(p2_out_py) < {proton_py_max}))"
    )
    fltr_mass = (f"(({mass_min} < primary_m[0]) && (primary_m[0] < {mass_max})) && "
                    f"(({mass_min} < primary_m[1]) && (primary_m[1] < {mass_max})) && "
                    f"{inv_mass_min} < inv_mass && inv_mass < {inv_mass_max}")
    return f"{fltr_acceptance} && {fltr_mass}"

def data_fltr():
    fltr_data = (f"fabs(px_diff) < {px_cut} && "
                    f"fabs(py_diff) < {py_cut} && "
                    f"fabs(trk_p[0]) < {p_cut} && "
                    f"fabs(trk_p[1]) < {p_cut} && "
                    f"fabs(trk_p[2]) < {p_cut} && "
                    f"fabs(trk_p[3]) < {p_cut} && "
                    f"{mass_min} < pair_masses[0][0] && pair_masses[0][0] < {mass_max} && "
                    f"{mass_min} < pair_masses[0][1] && pair_masses[0][1] < {mass_max} && "
                    f"{inv_mass_min} < inv_mass && inv_mass < {inv_mass_max}")
    return fltr_data


if __name__ == "__main__":
    print()
    print(f"CONFIG PATH   : {CONFIG_PATH}")
    print(f"proton_py_min = {proton_py_min:.3f}")
    print(f"proton_py_max = {proton_py_max:.3f}")
    print(f"rho_mass      = {rho_mass:.3f}")
    print(f"mass_interval = {mass_interval:.3f}")
    print(f"px_cut        = {px_cut:.3f}")
    print(f"py_cut        = {py_cut:.3f}")
    print(f"p_cut         = {p_cut:.3f}")
    print(f"mass_min      = {mass_min:.3f}")
    print(f"mass_max      = {mass_max:.3f}")
    print(f"inv_mass_min  = {inv_mass_min:.3f}")
    print(f"inv_mass_max  = {inv_mass_max:.3f}")
    print()
