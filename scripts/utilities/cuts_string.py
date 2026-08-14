#!/usr/bin/env python3

import sys
from pathlib import Path
 
sys.path.append(str(Path(__file__).parent.parent / "utilities"))
from load_config import load_config #type: ignore

config = load_config()

proton_py_min = config["acceptance"]["py_min"]
proton_py_max = config["acceptance"]["py_max"]

# mass intervals
mass_cuts = config["mass_cuts"]
inv_mass_min = mass_cuts["inv_mass_min"]
inv_mass_max = mass_cuts["inv_mass_max"]

px_cut = config["momentum"]["px_cut"]
py_cut = config["momentum"]["py_cut"]
p_cut = config["momentum"]["p_cut"]

momentum_cuts = config["momentum"]["momentum_cuts"]

def dime_fltr(production, inside = True):
    fltr_acceptance = ( 
    f"(({proton_py_min} < fabs(p1_out_py)) && (fabs(p1_out_py) < {proton_py_max})) && "
    f"(({proton_py_min} < fabs(p2_out_py)) && (fabs(p2_out_py) < {proton_py_max}))"
    )

    if inside:
        fltr_mass = f"{inv_mass_min} < inv_mass && inv_mass < {inv_mass_max}"
    else:
        fltr_mass = "(2.000 < inv_mass && inv_mass < 2.180) || (2.260 < inv_mass && inv_mass < 2.500)"

    try:
        particle = mass_cuts[production]
        mass_min = particle["mass"] - particle["interval"]
        mass_max = particle["mass"] + particle["interval"]
        fltr_mass = (f"({fltr_mass}) && "
                     f"(({mass_min} < primary_m[0]) && (primary_m[0] < {mass_max})) && "
                     f"(({mass_min} < primary_m[1]) && (primary_m[1] < {mass_max}))")
    except KeyError:
        print()
        print(f"Mass boundaries for {production} not found in config file. Skipping.")
        print()

    return f"{fltr_acceptance} && {fltr_mass}"

def data_fltr(inside = True):
    try:
        mass_min = mass_cuts["rho"]["mass"] - mass_cuts["rho"]["interval"]
        mass_max = mass_cuts["rho"]["mass"] + mass_cuts["rho"]["interval"]
    except KeyError:
        rho_mass = 0.770
        interval = 0.062
        mass_min = rho_mass - interval
        mass_max = rho_mass + interval

    if inside:
        fltr_mass = f"{inv_mass_min} < inv_mass && inv_mass < {inv_mass_max}"
    else:
        fltr_mass = "(2.000 < inv_mass && inv_mass < 2.180) || (2.260 < inv_mass && inv_mass < 2.500)"

    fltr_data = (f"fabs(px_diff) < {px_cut} && "
                 f"fabs(py_diff) < {py_cut} && "
                 f"{mass_min} < pair_masses[0][0] && pair_masses[0][0] < {mass_max} && "
                 f"{mass_min} < pair_masses[0][1] && pair_masses[0][1] < {mass_max} && "
                 f"({fltr_mass})")
    
    fltr_p = (f"fabs(trk_p[0]) < {p_cut} && "
              f"fabs(trk_p[1]) < {p_cut} && "
              f"fabs(trk_p[2]) < {p_cut} && "
              f"fabs(trk_p[3]) < {p_cut}")

    return f"{fltr_data} && {fltr_p}" if momentum_cuts else fltr_data


if __name__ == "__main__":
    print()
    print(f"{'proton_py_min':<18}= {proton_py_min:.3f}")
    print(f"{'proton_py_max':<18}= {proton_py_max:.3f}")
    print(f"{'px_cut':<18}= {px_cut:.3f}")
    print(f"{'py_cut':<18}= {py_cut:.3f}")
    print(f"{'p_cut':<18}= {p_cut:.3f}")
    print(f"{'inv_mass_min':<18}= {inv_mass_min:.3f}")
    print(f"{'inv_mass_max':<18}= {inv_mass_max:.3f}")
    print()
    print(f"Nonresonant masses")
    for key in config["nonreson_productions"]:
        print(f"  {key + ":":<7}{'mass':<8} = {mass_cuts[key]['mass']:.3f}")
        print(f"  {key + ":":<7}{'interval':<8} = {mass_cuts[key]['interval']:.3f}")
        print()
    print()
    # ToDo: add the particle production here dynamically
