# Defining basic constraints

wildcard_constraints:
    dime_suffix="resonant|nonreson",
    suffix="D|P|A"

fortran_files = {
    "resonant": "dimeMC/resonant/dimemcv1.07_vsm.f",
    "nonreson": "dimeMC/nonreson/dimemcv1.07.f",
}

suffix_map = {
    "D": "Diagonal",
    "A": "All",
    "P": "Parallel",
}

# General rule to generate graphs. This can be edited to accomodate new stuff
rule all:
    input:
        directory("plots/dimeMC/kinematics_combined"),
        expand(
            "plots/joint/{graph}_{config}.png",
            graph=["eta", "pt", "invmass", "proton_angle"],
            config=["D", "P", "A"],
        )


# Simulation rules
rule simulate:
    input:
        fortran=lambda wildcards: fortran_files[wildcards.dime_suffix],
        script="scripts/jobs/run_simulation.sh"
    output:
        "dimeMC/{dime_suffix}/exrec.dat"
    shell:
        "./{input.script} {input.fortran}"


rule exrec_to_tree:
    input:
        data="dimeMC/{dime_suffix}/exrec.dat",
        script="scripts/dimeMC/exrec_to_root.py"
    output:
        "data/dimeMC/exrec_{dime_suffix}_A.root"
    log:
        "logs/exrec_to_tree_{dime_suffix}_A.log"
    shell:
        "python3 {input.script} {input.data} {output} &> {log}"


rule split_dimeMC:
    input:
        data="data/dimeMC/exrec_{dime_suffix}_A.root",
        script="scripts/dimeMC/split.py"
    output:
        "data/dimeMC/exrec_{dime_suffix}_D.root",
        "data/dimeMC/exrec_{dime_suffix}_P.root"
    shell:
        "python3 {input.script} {input.data}"


# DimeMC scripts rules
rule kinematic_scripts:
    input:
        data_reson="data/dimeMC/exrec_resonant_A.root",
        data_nonre="data/dimeMC/exrec_nonreson_A.root",
        script="scripts/dimeMC/kinematics.py"
    output:
        directory("plots/dimeMC/kinematics_combined")
    log:
        "logs/kinematic_scripts.log"
    shell:
        "python3 {input.script} {input.data_reson} {input.data_nonre} {output} &> {log}"


#-----------------------------------------// Data scripts rules \\-----------------------------------------#
# Rules for combining trees for [D]iagonal [P]arallel and [A]ll
rule combine_trees:
    input:
        files=lambda wildcards: expand(
            "data/YounesNtuples/TOTEM{p}{n}.root",
            p={"D": ["2"], "P": ["4"], "A": ["2", "4"]}[wildcards.suffix],
            n=range(0, 4)
        ),
        script="scripts/utilities/combine_trees.py"
    output:
        "data/combined/TOTEM_{suffix}.root"
    shell:
        "python3 {input.script} {input.files} {output}"


# Add invariant mass
rule add_glueball_mass:
    input:
        tree="data/combined/TOTEM_{suffix}.root",
        script="scripts/utilities/create_invmass_branch.py"
    output:
        "data/glueball_mass/TOTEM_{suffix}.root"
    shell:
        "python3 {input.script} {input.tree} {output}"


# Add kinematic variables to make .Filter easier to handle
rule add_kinematics:
    input:
        tree="data/glueball_mass/TOTEM_{suffix}.root",
        script="scripts/utilities/create_kinematic_branch.py"
    output:
        "data/kinematics/TOTEM_{suffix}.root"
    shell:
        "python3 {input.script} {input.tree} {output}"

#-----------------------------------------// Combined scripts \\-----------------------------------------#
# These scripts plot data and Dime together.
rule inv_mass_combined:
    input:
        data="data/kinematics/TOTEM_{suffix}.root",
        dimeMC_reson="data/dimeMC/exrec_resonant_{suffix}.root",
        dimeMC_nonre="data/dimeMC/exrec_nonreson_{suffix}.root",
        script="scripts/joint/invariant_mass_histogram.py"
    output:
        "plots/joint/invmass_{suffix}.png"
    params:
        title=lambda wildcards: f"Combined Invariant Mass ({suffix_map[wildcards.suffix]})"
    shell:
        "python3 {input.script} {input.data} {input.dimeMC_reson} {input.dimeMC_nonre} {output} '{params.title}'"


rule pt_combined:
    input:
        data="data/kinematics/TOTEM_{suffix}.root",
        dimeMC_reson="data/dimeMC/exrec_resonant_{suffix}.root",
        dimeMC_nonre="data/dimeMC/exrec_nonreson_{suffix}.root",
        script="scripts/joint/pt_histogram.py"
    output:
        "plots/joint/pt_{suffix}.png"
    params:
        title=lambda wildcards: f"Combined Transverse Momentum ({suffix_map[wildcards.suffix]})"
    shell:
        "python3 {input.script} {input.data} {input.dimeMC_reson} {input.dimeMC_nonre} {output} '{params.title}'"


rule eta_combined:
    input:
        data="data/kinematics/TOTEM_{suffix}.root",
        dimeMC_reson="data/dimeMC/exrec_resonant_{suffix}.root",
        dimeMC_nonre="data/dimeMC/exrec_nonreson_{suffix}.root",
        script="scripts/joint/eta_histogram.py"
    output:
        "plots/joint/eta_{suffix}.png"
    params:
        title=lambda wildcards: f"Combined Rapidity ({suffix_map[wildcards.suffix]})"
    shell:
        "python3 {input.script} {input.data} {input.dimeMC_reson} {input.dimeMC_nonre} {output} '{params.title}'"


# Smallest angle between the outgoing protons
rule angles_combined:
    input:
        data="data/kinematics/TOTEM_{suffix}.root",
        dimeMC_reson="data/dimeMC/exrec_resonant_{suffix}.root",
        dimeMC_nonre="data/dimeMC/exrec_nonreson_{suffix}.root",
        script="scripts/joint/proton_angles_histogram.py"
    output:
        "plots/joint/proton_angle_{suffix}.png"
    params:
        title=lambda wildcards: f"Proton Angle Difference ({suffix_map[wildcards.suffix]})"
    shell:
        "python3 {input.script} {input.data} {input.dimeMC_reson} {input.dimeMC_nonre} {output} '{params.title}'"