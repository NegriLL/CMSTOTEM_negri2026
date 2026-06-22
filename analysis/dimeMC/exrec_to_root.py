#!/usr/bin/env python3

import ROOT
import math

from pathlib import Path


def read_file(input_file, output_file):    
    # Parameters
    event_numbers = []
    p1_in_pz_list = []   # incoming proton 1 pz
    p2_in_pz_list = []   # incoming proton 2 pz
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

                # Read first incoming proton (pz only)
                particle_line = lines[line_idx].strip()
                particle_parts = particle_line.split()
                p1_in_pz = float(particle_parts[9])
                p1_in_pz_list.append(p1_in_pz)
                line_idx += 1

                # Read second incoming proton (pz only)
                particle_line = lines[line_idx].strip()
                particle_parts = particle_line.split()
                p2_in_pz = float(particle_parts[9])
                p2_in_pz_list.append(p2_in_pz)
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
                p1_out_p = math.sqrt(p1_out_px**2 + p1_out_py**2 + p1_out_pz**2)

                p2_in_p = abs(p2_in_pz)
                p2_out_p = math.sqrt(p2_out_px**2 + p2_out_py**2 + p2_out_pz**2)

                xi_1 = abs(p1_out_p - p1_in_p) / p1_in_p
                xi_2 = abs(p2_out_p - p2_in_p) / p2_in_p
                
                s = (p1_in_pz - p2_in_pz)**2
                mass_loss = math.sqrt(xi_1 * xi_2 * s)
                mass_loss_list.append(mass_loss)

                # Count remaining particles (produced particles)
                ntrk = num_particles - 4
                ntrk_list.append(ntrk)
                event_numbers.append(current_event)

                # Read produced particles (px, py, pz, e)
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
                    
                    line_idx += 1
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
    event_no = ROOT.std.vector('int')()
    incoming_p1_pz = ROOT.std.vector('double')()
    incoming_p2_pz = ROOT.std.vector('double')()
    outgoing_p1_px = ROOT.std.vector('double')()
    outgoing_p1_py = ROOT.std.vector('double')()
    outgoing_p1_pz = ROOT.std.vector('double')()
    outgoing_p1_e = ROOT.std.vector('double')()
    outgoing_p2_px = ROOT.std.vector('double')()
    outgoing_p2_py = ROOT.std.vector('double')()
    outgoing_p2_pz = ROOT.std.vector('double')()
    outgoing_p2_e = ROOT.std.vector('double')()
    ntrk = ROOT.std.vector('int')()
    mass_loss_p = ROOT.std.vector('double')()
    produced_id = ROOT.std.vector('int')()
    produced_px = ROOT.std.vector('double')()
    produced_py = ROOT.std.vector('double')()
    produced_pz = ROOT.std.vector('double')()
    produced_e = ROOT.std.vector('double')()
    produced_m = ROOT.std.vector('double')()
    
    tree.Branch("event_number", event_no)
    tree.Branch("p1_in_pz", incoming_p1_pz)
    tree.Branch("p2_in_pz", incoming_p2_pz)
    tree.Branch("p1_out_px", outgoing_p1_px)
    tree.Branch("p1_out_py", outgoing_p1_py)
    tree.Branch("p1_out_pz", outgoing_p1_pz)
    tree.Branch("p1_out_e", outgoing_p1_e)
    tree.Branch("p2_out_px", outgoing_p2_px)
    tree.Branch("p2_out_py", outgoing_p2_py)
    tree.Branch("p2_out_pz", outgoing_p2_pz)
    tree.Branch("p2_out_e", outgoing_p2_e)
    tree.Branch("ntrk", ntrk)
    tree.Branch("mass_loss_p", mass_loss_p)
    tree.Branch("produced_id", produced_id)
    tree.Branch("produced_px", produced_px)
    tree.Branch("produced_py", produced_py)
    tree.Branch("produced_pz", produced_pz)
    tree.Branch("produced_e", produced_e)
    tree.Branch("produced_m", produced_m)
    
    # Fill tree with event data
    for i in range(len(event_numbers)):
        event_no.clear()
        incoming_p1_pz.clear()
        incoming_p2_pz.clear()
        outgoing_p1_px.clear()
        outgoing_p1_py.clear()
        outgoing_p1_pz.clear()
        outgoing_p1_e.clear()
        outgoing_p2_px.clear()
        outgoing_p2_py.clear()
        outgoing_p2_pz.clear()
        outgoing_p2_e.clear()
        ntrk.clear()
        mass_loss_p.clear()
        produced_id.clear()
        produced_px.clear()
        produced_py.clear()
        produced_pz.clear()
        produced_e.clear()
        produced_m.clear()
        
        event_no.push_back(event_numbers[i])
        
        incoming_p1_pz.push_back(p1_in_pz_list[i])
        incoming_p2_pz.push_back(p2_in_pz_list[i])

        outgoing_p1_px.push_back(p1_out_px_list[i])
        outgoing_p1_py.push_back(p1_out_py_list[i])
        outgoing_p1_pz.push_back(p1_out_pz_list[i])
        outgoing_p1_e.push_back(p1_out_e_list[i])

        outgoing_p2_px.push_back(p2_out_px_list[i])
        outgoing_p2_py.push_back(p2_out_py_list[i])
        outgoing_p2_pz.push_back(p2_out_pz_list[i])
        outgoing_p2_e.push_back(p2_out_e_list[i])

        ntrk.push_back(ntrk_list[i])
        mass_loss_p.push_back(mass_loss_list[i])
        
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
    import sys
    
    input_path = Path(__file__).parent.parent / "dimemc" / "exrec.dat"
    output_path = Path(__file__).parent.parent / "data" / "exrec.root"
    
    if len(sys.argv) > 1:
        input_path = Path(sys.argv[1])
    if len(sys.argv) > 2:
        output_path = Path(sys.argv[2])
    
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)
    
    read_file(str(input_path), str(output_path))
