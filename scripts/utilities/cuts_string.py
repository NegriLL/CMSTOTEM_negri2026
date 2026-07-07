proton_py_min = 0.18
proton_py_max = 0.68
rho_mass = 0.770
mass_interval = 0.062

px_cut = 0.130
py_cut = 0.060
p_cut = 1
mass_min = rho_mass - mass_interval
mass_max = rho_mass + mass_interval

def dime_fltr():
    fltr_acceptance = ( 
    f"(({proton_py_min} < fabs(p1_out_py)) && (fabs(p1_out_py) < {proton_py_max})) && "
    f"(({proton_py_min} < fabs(p2_out_py)) && (fabs(p2_out_py) < {proton_py_max}))"
    )
    fltr_mass = (f"(({mass_min} < primary_m[0]) && (primary_m[0] < {mass_max})) && "
                    f"(({mass_min} < primary_m[1]) && (primary_m[1] < {mass_max})) && "
                    f"2.0 < inv_mass && inv_mass < 2.5")
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
                    f"2.0 < inv_mass && inv_mass < 2.5")
    return fltr_data