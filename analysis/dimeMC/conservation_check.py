import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from ROOT import TLorentzVector, kBlue, kRed


def create_particle_dict(line):
    """Create a dictionary containing particle kinematic properties from a data line.
    
    Parses a space-separated line of particle data and extracts momentum components,
    energy, mass, total momentum magnitude, and creates a TLorentzVector representation.
    
    Args:
        line (str): Space-separated string containing particle data from DimeMC
    
    Returns:
        dict: Dictionary with keys:
            - 'x', 'y', 'z', 'e' (float): 4-Momentum components in GeV
            - 'm' (float): Mass in GeV
            - 'p' (float): Total momentum in GeV
            - 'vec' (TLorentzVector): 4-vector representation of the particle
    """
    parts = line.split()
    particle_dict = {}
    
    particle_dict['x'] = float(parts[7])
    particle_dict['y'] = float(parts[8])
    particle_dict['z'] = float(parts[9])
    particle_dict['e'] = float(parts[10])
    particle_dict['m'] = float(parts[11])
    particle_dict['p'] = np.sqrt(np.pow(particle_dict['x'],2)
                                 + pow(particle_dict['y'],2)
                                 + pow(particle_dict['z'],2))
    particle_dict['vec'] = TLorentzVector(particle_dict['x'],
                                          particle_dict['y'],
                                          particle_dict['z'],
                                          particle_dict['e'])

    return particle_dict



def format_value(value):
    """Colour values dynamically.
    
    Check whether value is within 1e-5 threshold and highlight it green or red
    accordingly.
    
    Args:
        value (float): Value to check against.
    
    Returns:
        string: value formatted in scientific notation and highlighted.
    """
    if abs(value) < 1e-5:
        return '\033[102m{:.3E}\033[0m'.format(value)
    else:
        return '\033[101m{:.3E}\033[0m'.format(value)
    


def check_mass_conservation(pr1_in_p, pr1_out_p, pr2_in_p, pr2_out_p, rho1_vec, rho2_vec):
    """Check mass conservation in a DimeMC event.
    
    Calculates the mass loss from the incoming protons and compares it with the
    combined mass of two output particles and outgoing PP. Prints the results and returns
    the mass difference.
    
    Args:
        pr1_in_p (float): Incoming momentum of proton 1 in GeV
        pr1_out_p (float): Outgoing momentum of proton 1 in GeV
        pr2_in_p (float): Incoming momentum of proton 2 in GeV
        pr2_out_p (float): Outgoing momentum of proton 2 in GeV
        rho1_vec (TLorentzVector): 4-vector of first rho meson
        rho2_vec (TLorentzVector): 4-vector of second rho meson
    
    Returns:
        float: Difference between calculated mass loss and sum of rho masses in GeV
    """
    # Variables for calculating mass loss
    s = np.pow((pr1_in_p + pr2_in_p), 2, dtype=np.float64)
    xi_1 = np.divide(np.abs(np.subtract(pr1_out_p, pr1_in_p, dtype=np.float64), dtype=np.float64), pr1_in_p, dtype=np.float64)
    xi_2 = np.divide(np.abs(np.subtract(pr2_out_p, pr2_in_p, dtype=np.float64), dtype=np.float64), pr2_in_p, dtype=np.float64)

    # Checking mass loss an comparing it against produced rhos
    mass_loss = np.sqrt(np.multiply(np.multiply(xi_1, xi_2, dtype=np.float64), s, dtype=np.float64), dtype=np.float64)

    rho_masses = (rho1_vec + rho2_vec).M()
    diff = mass_loss - rho_masses
    print('M_loss = {:.3E}\t\t rho_m sum = {:.3E}\t\t Delta = {}'
          .format(mass_loss, rho_masses, format_value(diff)))
    
    return diff

def check_momentum_conservation(pr1_in, pr2_in, pr1_out, pr2_out, rho1, rho2):
    """Check momentum conservation in a scattering event.
    
    Compares the total incoming momentum of two protons against the total outgoing
    momentum of two output particles and outgoing PP. Prints the momentum
    differences in each component.
    
    Args:
        pr1_in (TLorentzVector): Incoming 4-vector of proton 1
        pr2_in (TLorentzVector): Incoming 4-vector of proton 2
        pr1_out (TLorentzVector): Outgoing 4-vector of proton 1
        pr2_out (TLorentzVector): Outgoing 4-vector of proton 2
        rho1 (TLorentzVector): 4-vector of first rho meson
        rho2 (TLorentzVector): 4-vector of second rho meson
    """
    # Adding incoming protons together and comparing against outgoing protons and rhos
    p_conserved = pr1_in + pr2_in - pr1_out - pr2_out - rho1 - rho2

    print('px difference = {}\t py difference = {}\t pz difference = {}'
          .format(format_value(p_conserved.Px()), format_value(p_conserved.Py()), format_value(p_conserved.Pz())))
    
    
    
def check_energy_conservation(pr1_in_e, pr2_in_e, pr1_out_e, pr2_out_e, rho1_e, rho2_e):
    """Check energy conservation in a scattering event.
    
    Compares the total incoming energy of two protons against the total outgoing
    energy of two output particles and outgoing PP. Prints the energy difference.
    
    Args:
        pr1_in_e (float): Energy of incoming proton 1 in GeV
        pr2_in_e (float): Energy of incoming proton 2 in GeV
        pr1_out_e (float): Energy of outgoing proton 1 in GeV
        pr2_out_e (float): Energy of outgoing proton 2 in GeV
        rho1_e (float): Energy of first rho meson in GeV
        rho2_e (float): Energy of second rho meson in GeV
    """
    e_conserved = pr1_in_e + pr2_in_e - pr1_out_e - pr2_out_e - rho1_e - rho2_e
    print('Energy difference = {}'.format(format_value(e_conserved)))

    

def read_file(file_path):
    """Read and process particle scattering event data from a file.
    
    Parses an event file containing proton-proton scattering data with rho meson
    production. For each event, checks mass, momentum, and energy conservation.
    Prints conservation check results for each event.
    
    Args:
        file_path (str or Path): Path to the data file containing event records.
                                 Each event includes two incoming protons, two outgoing
                                 protons, and two rho mesons.
    
    Returns:
        list: Array of mass loss values (difference between calculated mass loss
              and sum of rho masses) for each event in GeV
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    line_idx = 0

    mass_losses = []

    while line_idx < len(lines):
        line = lines[line_idx].strip()

        # Write down event in the header
        parts = line.split()
        if len(parts) == 2:
            print(f'Event {int(parts[0]):03d}')
        line_idx += 1

        # Save relevant particles
        pr1_in = create_particle_dict(lines[line_idx].strip())
        pr2_in = create_particle_dict(lines[line_idx + 1].strip())
        pr1_out = create_particle_dict(lines[line_idx + 2].strip())
        pr2_out = create_particle_dict(lines[line_idx + 3].strip())
        rho1 = create_particle_dict(lines[line_idx + 4].strip())
        rho2 = create_particle_dict(lines[line_idx + 5].strip())

        mass_root = (rho1['vec'] + rho2['vec']).M()
        mass_manual = np.sqrt( np.pow(rho1['e'] + rho2['e'], 2) \
                              - (np.pow(rho1['x'] + rho2['x'], 2) \
                                 + np.pow(rho1['y'] + rho2['y'], 2) \
                                    + np.pow(rho1['z'] + rho2['z'], 2)))
        
        Ein = (pr1_in['vec'] + pr2_in['vec']).E()
        Eout = ((pr1_out['vec'] + pr2_out['vec']).E())
        pin = (pr1_in['vec'] + pr2_in['vec']).P()
        pout = (pr1_out['vec'] + pr2_out['vec']).P()
        mass_loss = np.sqrt(np.pow(Ein - Eout, 2) - np.pow(pin - pout, 2))
        print(mass_loss - mass_manual)

        Ein = (pr1_in['e'] + pr2_in['e'])
        Eout = (pr1_out['e'] + pr2_out['e'])
        pin = np.sqrt(np.pow(pr1_in['x'] + pr2_in['x'], 2) + np.pow(pr1_in['y'] + pr2_in['y'], 2) + np.pow(pr1_in['z'] + pr2_in['z'], 2))
        pout = np.sqrt(np.pow(pr1_out['x'] + pr2_out['x'], 2) + np.pow(pr1_out['y'] + pr2_out['y'], 2) + np.pow(pr1_out['z'] + pr2_out['z'], 2))
        mass_loss = np.sqrt(np.pow(Ein - Eout, 2) - np.pow(pin - pout, 2))
        
        print(mass_loss - mass_manual)

        # Print differences
        mass_loss = check_mass_conservation(pr1_in['p'], pr1_out['p'], pr2_in['p'], pr2_out['p'], rho1['vec'], rho2['vec'])
        mass_losses.append(mass_loss)
        check_momentum_conservation(pr1_in['vec'], pr2_in['vec'], pr1_out['vec'], pr2_out['vec'], rho1['vec'], rho2['vec'])
        check_energy_conservation(pr1_in['e'], pr2_in['e'], pr1_out['e'], pr2_out['e'], rho1['e'], rho2['e'])
        print()

        # Skip lines until we find another header
        line_idx += 6
        try:
            line = lines[line_idx].strip()
        except IndexError:
            break
        while len(line.split()) != 2:
            line_idx += 1
            try:
                line = lines[line_idx].strip()
            except IndexError:
                break

    return mass_losses


def plot_mass_losses(mass_losses, save_path):
    """Create and save a bar plot of mass loss values across events.
    
    Generates a bar chart showing the mass difference (M - M_rhorho) for each
    event, with positive differences shown in blue and negative in red.
    
    Args:
        mass_losses (array): Array of mass loss values in GeV for each event
        save_path (Path): Directory path where the plot will be saved as
                         'mass_loss_direct_calculation.png'
    """
    # Mass loss - two rho mass
    
    fig, ax1 = plt.subplots()
    entry_indices_raw = np.arange(len(mass_losses))
    ax1.bar(entry_indices_raw, mass_losses, color=['blue' if val >= 0 else 'red' for val in mass_losses], alpha=0.7)
    ax1.set_xlabel("Entry Number")
    ax1.set_ylabel("[GeV]")
    ax1.set_title(r'$M - M_{\rho\rho}$')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color='black', linestyle='--', linewidth=0.8)

    plt.tight_layout()
    plt.savefig(str(save_path / "mass_loss_direct_calculation.png"), dpi=150)
    plt.close()


def main():
    file_path = Path(__file__).parent.parent / "dimemc_vsm" / "exrec1.dat"
    file_path2 = Path(__file__).parent.parent / "dimemc_vsm" / "exrec2.dat"
    save_path = Path(__file__).parent.parent / "plots" / "conservation"

    # can extend this to save other variables easily
    mass_losses = read_file(file_path)
    mass_losses2 = read_file(file_path2)

    # only plotting mass losses for now
    plot_mass_losses(mass_losses + mass_losses2, save_path)
    

if __name__ == "__main__":
    main()