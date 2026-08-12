#!/usr/bin/env python3

import ROOT
import sys
import math
 
from array import array
from pathlib import Path
 
 
def parse_particle_line(line):
    parts = line.split()
    particle_id = int(parts[1])
    px = float(parts[7])
    py = float(parts[8])
    pz = float(parts[9])
    e = float(parts[10])
    m = float(parts[11])
    return particle_id, px, py, pz, e, m
 
 
def read_file(input_file, output_file):
    event_numbers = []
    p1_in_pz_list = []   # incoming proton 1 pz
    p1_in_e_list = []    # incoming proton 1 energy
    p2_in_pz_list = []   # incoming proton 2 pz
    p2_in_e_list = []    # incoming proton 2 energy
    p1_out_px_list = []  # outgoing proton 1 px
    p1_out_py_list = []
    p1_out_pz_list = []
    p1_out_e_list = []
    p2_out_px_list = []  # outgoing proton 2 px
    p2_out_py_list = []
    p2_out_pz_list = []
    p2_out_e_list = []
    ntrk_list = []       # number of produced particles
    mass_loss_list = []  # M = sqrt(xi_1 * xi_2 * s)
    invariant_mass_list = []  # invariant mass of the system of produced particles
 
    primary_particles_per_event = []  # list[(id, px, py, pz, e, m)]
    produced_particles_per_event = []  # list[(id, px, py, pz, e, m)]
 
    with open(input_file, 'r') as f:
        lines = f.readlines()
 
    n_lines = len(lines)
    line_idx = 0
 
    while line_idx < n_lines:
        line = lines[line_idx].strip()

        # skip invalid lines
        if not line:
            line_idx += 1
            continue

        # search for header
        parts = line.split()
        if len(parts) != 2:
            line_idx += 1
            continue
 
        try:
            event_num = int(parts[0])
            num_particles = int(parts[1])
            line_idx += 1
 
            # First incoming proton (pz, e)
            _, _, _, p1_in_pz, p1_in_e, _ = parse_particle_line(lines[line_idx])
            line_idx += 1
 
            # Second incoming proton (pz, e)
            _, _, _, p2_in_pz, p2_in_e, _ = parse_particle_line(lines[line_idx])
            line_idx += 1
 
            # First outgoing proton (px, py, pz, e)
            _, p1_out_px, p1_out_py, p1_out_pz, p1_out_e, _ = parse_particle_line(lines[line_idx])
            line_idx += 1
 
            # Second outgoing proton (px, py, pz, e)
            _, p2_out_px, p2_out_py, p2_out_pz, p2_out_e, _ = parse_particle_line(lines[line_idx])
            line_idx += 1
 
            # Mass loss: M = sqrt(xi_1 * xi_2 * s)
            p1_in_p = abs(p1_in_pz)
            p1_out_p = math.sqrt(p1_out_px ** 2 + p1_out_py ** 2 + p1_out_pz ** 2)
 
            p2_in_p = abs(p2_in_pz)
            p2_out_p = math.sqrt(p2_out_px ** 2 + p2_out_py ** 2 + p2_out_pz ** 2)
 
            xi_1 = abs(p1_out_p - p1_in_p) / p1_in_p
            xi_2 = abs(p2_out_p - p2_in_p) / p2_in_p
 
            s = (p1_in_p + p2_in_p) ** 2
            mass_loss = math.sqrt(xi_1 * xi_2 * s)
 
            # Primary production (2 particles)
            primary_particles = []
            for _ in range(2):
                pid, px, py, pz, e, m = parse_particle_line(lines[line_idx])
                primary_particles.append((pid, px, py, pz, e, m))
                line_idx += 1
 
            ntrk = num_particles - 6  # two incoming, two outgoing, two primary particles
 
            # Produced particles, accumulating the total 4-vector as we go
            produced_particles = []
            particle_vec = ROOT.Math.PxPyPzEVector(0, 0, 0, 0)
 
            for _ in range(ntrk):
                pid, px, py, pz, e, m = parse_particle_line(lines[line_idx])
                produced_particles.append((pid, px, py, pz, e, m))
                particle_vec += ROOT.Math.PxPyPzEVector(px, py, pz, e)
                line_idx += 1
 
            # Only commit this event once every line has parsed
            event_numbers.append(event_num)
            p1_in_pz_list.append(p1_in_pz)
            p1_in_e_list.append(p1_in_e)
            p2_in_pz_list.append(p2_in_pz)
            p2_in_e_list.append(p2_in_e)
            p1_out_px_list.append(p1_out_px)
            p1_out_py_list.append(p1_out_py)
            p1_out_pz_list.append(p1_out_pz)
            p1_out_e_list.append(p1_out_e)
            p2_out_px_list.append(p2_out_px)
            p2_out_py_list.append(p2_out_py)
            p2_out_pz_list.append(p2_out_pz)
            p2_out_e_list.append(p2_out_e)
            ntrk_list.append(ntrk)
            mass_loss_list.append(mass_loss)
            invariant_mass_list.append(particle_vec.M())
            primary_particles_per_event.append(primary_particles)
            produced_particles_per_event.append(produced_particles)

        except (ValueError, IndexError):
            # In case of formatting problems skip line
            line_idx += 1
 
    # Create ROOT file and tree
    ROOT.gROOT.SetBatch(True)
    root_file = ROOT.TFile(output_file, "RECREATE")
    tree = ROOT.TTree("particles", "Particle data from exrec.dat")
 
    event_no = array('i', [0])
    incoming_p1_pz = array('d', [0.0])
    incoming_p1_e = array('d', [0.0])
    incoming_p2_pz = array('d', [0.0])
    incoming_p2_e = array('d', [0.0])
    outgoing_p1_px = array('d', [0.0])
    outgoing_p1_py = array('d', [0.0])
    outgoing_p1_pz = array('d', [0.0])
    outgoing_p1_e = array('d', [0.0])
    outgoing_p2_px = array('d', [0.0])
    outgoing_p2_py = array('d', [0.0])
    outgoing_p2_pz = array('d', [0.0])
    outgoing_p2_e = array('d', [0.0])
    ntrk = array('i', [0])
    mass_loss_p = array('d', [0.0])
    primary_id = ROOT.std.vector('int')()
    primary_px = ROOT.std.vector('double')()
    primary_py = ROOT.std.vector('double')()
    primary_pz = ROOT.std.vector('double')()
    primary_e = ROOT.std.vector('double')()
    primary_m = ROOT.std.vector('double')()
    produced_id = ROOT.std.vector('int')()
    produced_px = ROOT.std.vector('double')()
    produced_py = ROOT.std.vector('double')()
    produced_pz = ROOT.std.vector('double')()
    produced_e = ROOT.std.vector('double')()
    produced_m = ROOT.std.vector('double')()
    invariant_mass = array('d', [0.0])
 
    tree.Branch("event_number", event_no, "event_number/I")
    tree.Branch("p1_in_pz", incoming_p1_pz, "p1_in_pz/D")
    tree.Branch("p1_in_e", incoming_p1_e, "p1_in_e/D")
    tree.Branch("p2_in_pz", incoming_p2_pz, "p2_in_pz/D")
    tree.Branch("p2_in_e", incoming_p2_e, "p2_in_e/D")
    tree.Branch("p1_out_px", outgoing_p1_px, "p1_out_px/D")
    tree.Branch("p1_out_py", outgoing_p1_py, "p1_out_py/D")
    tree.Branch("p1_out_pz", outgoing_p1_pz, "p1_out_pz/D")
    tree.Branch("p1_out_e", outgoing_p1_e, "p1_out_e/D")
    tree.Branch("p2_out_px", outgoing_p2_px, "p2_out_px/D")
    tree.Branch("p2_out_py", outgoing_p2_py, "p2_out_py/D")
    tree.Branch("p2_out_pz", outgoing_p2_pz, "p2_out_pz/D")
    tree.Branch("p2_out_e", outgoing_p2_e, "p2_out_e/D")
    tree.Branch("ntrk", ntrk, "ntrk/I")
    tree.Branch("mass_loss_p", mass_loss_p, "mass_loss_p/D")
    tree.Branch("primary_id", primary_id)
    tree.Branch("primary_px", primary_px)
    tree.Branch("primary_py", primary_py)
    tree.Branch("primary_pz", primary_pz)
    tree.Branch("primary_e", primary_e)
    tree.Branch("primary_m", primary_m)
    tree.Branch("produced_id", produced_id)
    tree.Branch("produced_px", produced_px)
    tree.Branch("produced_py", produced_py)
    tree.Branch("produced_pz", produced_pz)
    tree.Branch("produced_e", produced_e)
    tree.Branch("produced_m", produced_m)
    tree.Branch("inv_mass", invariant_mass, "inv_mass/D")
 
    # Fill Tree
    n_events = len(event_numbers)
    for i in range(n_events):
        primary_id.clear()
        primary_px.clear()
        primary_py.clear()
        primary_pz.clear()
        primary_e.clear()
        primary_m.clear()
        produced_id.clear()
        produced_px.clear()
        produced_py.clear()
        produced_pz.clear()
        produced_e.clear()
        produced_m.clear()
 
        event_no[0] = event_numbers[i]
        incoming_p1_pz[0] = p1_in_pz_list[i]
        incoming_p1_e[0] = p1_in_e_list[i]
        incoming_p2_pz[0] = p2_in_pz_list[i]
        incoming_p2_e[0] = p2_in_e_list[i]
 
        outgoing_p1_px[0] = p1_out_px_list[i]
        outgoing_p1_py[0] = p1_out_py_list[i]
        outgoing_p1_pz[0] = p1_out_pz_list[i]
        outgoing_p1_e[0] = p1_out_e_list[i]
 
        outgoing_p2_px[0] = p2_out_px_list[i]
        outgoing_p2_py[0] = p2_out_py_list[i]
        outgoing_p2_pz[0] = p2_out_pz_list[i]
        outgoing_p2_e[0] = p2_out_e_list[i]
 
        ntrk[0] = ntrk_list[i]
        mass_loss_p[0] = mass_loss_list[i]
        invariant_mass[0] = invariant_mass_list[i]
 
        for pid, px, py, pz, e, m in primary_particles_per_event[i]:
            primary_id.push_back(pid)
            primary_px.push_back(px)
            primary_py.push_back(py)
            primary_pz.push_back(pz)
            primary_e.push_back(e)
            primary_m.push_back(m)
 
        for pid, px, py, pz, e, m in produced_particles_per_event[i]:
            produced_id.push_back(pid)
            produced_px.push_back(px)
            produced_py.push_back(py)
            produced_pz.push_back(pz)
            produced_e.push_back(e)
            produced_m.push_back(m)
 
        tree.Fill()
 
    root_file.Write()
    root_file.Close()
 
    total_produced = sum(len(p) for p in produced_particles_per_event)
    print(f"Created ROOT tree with {n_events} events")
    print(f"Total produced particles: {total_produced}")
    print(f"Output file: {output_file}")
 
 
if __name__ == "__main__":
 
    if len(sys.argv) == 3:
        input_path = Path(sys.argv[1])
        output_path = Path(sys.argv[2])
    elif len(sys.argv) == 1:
        input_path = Path(__file__).parent.parent.parent / "dimeMC" / "resonant" / "exrec.dat"
        output_path = Path(__file__).parent.parent.parent / "data" / "dimeMC" / "resonant.root"
    else:
        print("Incorrect number of input values. Expected 0 or 2")
        sys.exit(1)
 
    # make sure path exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
 
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)
 
    read_file(str(input_path), str(output_path))