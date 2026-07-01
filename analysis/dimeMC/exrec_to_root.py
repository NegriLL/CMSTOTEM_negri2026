#!/usr/bin/env python3

import ROOT
import sys
import numpy as np

from array import array
from pathlib import Path


def read_file(input_file, output_file):    
    # Parameters
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
    produced_particles = []  # list of [event_num, id, px, py, pz, e] for each produced particle
    invariant_mass_list = []  # invariant mass of the system of produced particles
    
    # Read exrec.dat file
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    current_event = None
    line_idx = 0
    
    while line_idx < len(lines):
        line = lines[line_idx].strip()
        
        if not line:
            line_idx += 1
            continue
        
        # Try to parse as header line
        parts = line.split()
        if len(parts) == 2:
            try:
                event_num = int(parts[0])
                num_particles = int(parts[1])
                current_event = event_num
                line_idx += 1

                # Read first incoming proton (pz and e only)
                particle_line = lines[line_idx].strip()
                particle_parts = particle_line.split()
                p1_in_pz = float(particle_parts[9])
                p1_in_pz_list.append(p1_in_pz)
                p1_in_e = float(particle_parts[10])
                p1_in_e_list.append(p1_in_e)
                line_idx += 1

                # Read second incoming proton (pz only)
                particle_line = lines[line_idx].strip()
                particle_parts = particle_line.split()
                p2_in_pz = float(particle_parts[9])
                p2_in_pz_list.append(p2_in_pz)
                p2_in_e = float(particle_parts[10])
                p2_in_e_list.append(p2_in_e)
                line_idx += 1

                # Read first outgoing proton (px, py, pz, e)
                particle_line = lines[line_idx].strip()
                particle_parts = particle_line.split()
                p1_out_px = float(particle_parts[7])
                p1_out_py = float(particle_parts[8])
                p1_out_pz = float(particle_parts[9])
                p1_out_e = float(particle_parts[10])
                p1_out_px_list.append(p1_out_px)
                p1_out_py_list.append(p1_out_py)
                p1_out_pz_list.append(p1_out_pz)
                p1_out_e_list.append(p1_out_e)
                line_idx += 1

                # Read second outgoing proton (px, py, pz, e)
                particle_line = lines[line_idx].strip()
                particle_parts = particle_line.split()
                p2_out_px = float(particle_parts[7])
                p2_out_py = float(particle_parts[8])
                p2_out_pz = float(particle_parts[9])
                p2_out_e = float(particle_parts[10])
                p2_out_px_list.append(p2_out_px)
                p2_out_py_list.append(p2_out_py)
                p2_out_pz_list.append(p2_out_pz)
                p2_out_e_list.append(p2_out_e)
                line_idx += 1

                # Claculate mass loss
                p1_in_p = abs(p1_in_pz)
                p1_out_p = np.sqrt(p1_out_px**2 + p1_out_py**2 + p1_out_pz**2)

                p2_in_p = abs(p2_in_pz)
                p2_out_p = np.sqrt(p2_out_px**2 + p2_out_py**2 + p2_out_pz**2)

                xi_1 = abs(p1_out_p - p1_in_p) / p1_in_p
                xi_2 = abs(p2_out_p - p2_in_p) / p2_in_p
                
                s = (p1_in_p + p2_in_p)**2
                mass_loss = np.sqrt(xi_1 * xi_2 * s)
                mass_loss_list.append(mass_loss)

                # Count remaining particles (produced particles)
                ntrk = num_particles - 4
                ntrk_list.append(ntrk)
                event_numbers.append(current_event)

                # Read produced particles (px, py, pz, e)
                particle_vec = ROOT.Math.PxPyPzEVector(0, 0, 0, 0)

                for _ in range(ntrk):
                    particle_line = lines[line_idx].strip()
                    particle_parts = particle_line.split()
                    
                    particle_id = int(particle_parts[1])
                    px = float(particle_parts[7])
                    py = float(particle_parts[8])
                    pz = float(particle_parts[9])
                    e = float(particle_parts[10])
                    m = float(particle_parts[11])
                    
                    # Store produced particle data with event number and id
                    produced_particles.append([current_event, particle_id, px, py, pz, e, m])

                    if abs(particle_id) == 211:
                        temp_vec = ROOT.Math.PxPyPzEVector(px, py, pz, e)
                        particle_vec = particle_vec + temp_vec

                    line_idx += 1
                
                invariant_mass_list.append(particle_vec.M())

            except (ValueError, IndexError):
                # In case of formatting problems skip line
                line_idx += 1
        else:
            line_idx += 1
    
    # Create ROOT file and tree
    ROOT.gROOT.SetBatch(True)
    root_file = ROOT.TFile(output_file, "RECREATE")
    tree = ROOT.TTree("particles", "Particle data from exrec.dat")
    
    # Create branches for event-level data
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
    tree.Branch("produced_id", produced_id)
    tree.Branch("produced_px", produced_px)
    tree.Branch("produced_py", produced_py)
    tree.Branch("produced_pz", produced_pz)
    tree.Branch("produced_e", produced_e)
    tree.Branch("produced_m", produced_m)
    tree.Branch("inv_mass", invariant_mass, "inv_mass/D")
    
    # Fill tree with event data
    for i in range(len(event_numbers)):
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
        
        # Add produced particles for this event
        for particle in produced_particles:
            if particle[0] == event_numbers[i]:
                produced_id.push_back(particle[1])
                produced_px.push_back(particle[2])
                produced_py.push_back(particle[3])
                produced_pz.push_back(particle[4])
                produced_e.push_back(particle[5])
                produced_m.push_back(particle[6])
        
        tree.Fill()
    
    root_file.Write()
    root_file.Close()
    
    print(f"Created ROOT tree with {len(event_numbers)} events")
    print(f"Total produced particles: {len(produced_particles)}")
    print(f"Output file: {output_file}")


if __name__ == "__main__":

    if len(sys.argv) == 3:
        input_path = Path(sys.argv[1])
        output_path = Path(sys.argv[2])
    elif len(sys.argv) == 1:
        input_path = Path(__file__).parent.parent.parent / "dimeMC" / "resonant" / "exrec.dat"
        output_path = Path(__file__).parent.parent.parent / "data" / "dimeMC" / "exrec_resonant.root"
    else:
        print("Incorrect number of input values. Expected 0 or 2")
        sys.exit(1)

    # make sure path exists
    input_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)
    
    read_file(str(input_path), str(output_path))
