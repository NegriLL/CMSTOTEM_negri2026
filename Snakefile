# Load configuration
configfile: "config.yaml"

simulated_runs = config["simulated_runs"]
productions = config["productions"]
fortran_files = config["fortran_files"]
suffix_map = config["suffix_map"]

# Defining basic constraints
wildcard_constraints:
    suffix="D|P|A",
    production="|".join(productions)


# General rule to generate graphs. This can be edited to accomodate new stuff
rule all:
    input:
        expand(
            "plots/dimeMC/kinematics_combined/{production}",
            production=productions,
        ),
        expand(
            "plots/joint/{graph}_{config}.png",
            graph=["eta", "pt", "invmass", "proton_angle"],
            config=["D", "P", "A"],
        )


# Simulation rules
rule simulate_resonant:
    input:
        fortran=fortran_files["resonant"],
        script="scripts/jobs/run_simulation.sh"
    params:
        num_runs=simulated_runs
    output:
        "dimeMC/resonant/exrec.dat"
    shadow: "copy-minimal"
    shell:
        # no production argument for the resonant simulation
        "./{input.script} {input.fortran} {params.num_runs}"


rule simulate_nonreson:
    input:
        fortran=fortran_files["nonreson"],
        script="scripts/jobs/run_simulation.sh"
    params:
        num_runs=simulated_runs
    output:
        "dimeMC/nonreson/{production}_exrec.dat"
    shadow: "copy-minimal"
    shell:
        "./{input.script} {input.fortran} {params.num_runs} {wildcards.production}"


rule exrec_to_tree_resonant:
    input:
        data="dimeMC/resonant/exrec.dat",
        script="scripts/dimeMC/exrec_to_root.py"
    output:
        "data/dimeMC/resonant_A.root"
    log:
        "logs/exrec_to_tree_resonant_A.log"
    shell:
        "python3 {input.script} {input.data} {output} &> {log}"


rule exrec_to_tree_nonreson:
    input:
        data="dimeMC/nonreson/{production}_exrec.dat",
        script="scripts/dimeMC/exrec_to_root.py"
    output:
        "data/dimeMC/{production}_A.root"
    log:
        "logs/exrec_to_tree_nonreson_{production}_A.log"
    shell:
        "python3 {input.script} {input.data} {output} &> {log}"


rule split_dimeMC_resonant:
    input:
        data="data/dimeMC/resonant_A.root",
        script="scripts/dimeMC/split.py"
    output:
        "data/dimeMC/resonant_D.root",
        "data/dimeMC/resonant_P.root"
    shell:
        "python3 {input.script} {input.data}"


rule split_dimeMC_nonreson:
    input:
        data="data/dimeMC/{production}_A.root",
        script="scripts/dimeMC/split.py"
    output:
        "data/dimeMC/{production}_D.root",
        "data/dimeMC/{production}_P.root"
    shell:
        "python3 {input.script} {input.data}"


# DimeMC scripts rules
rule kinematic_scripts:
    input:
        data_reson="data/dimeMC/resonant_A.root",
        data_nonre="data/dimeMC/{production}_A.root",
        script="scripts/dimeMC/kinematics.py"
    output:
        directory("plots/dimeMC/kinematics_combined/{production}")
    log:
        "logs/kinematic_scripts_{production}.log"
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
        dimeMC_reson="data/dimeMC/resonant_{suffix}.root",
        dimeMC_nonre=expand("data/dimeMC/{production}_{{suffix}}.root", production=productions),
        script="scripts/joint/invariant_mass_histogram.py"
        config_file="config.yaml"
    output:
        "plots/joint/invmass_{suffix}.png"
    params:
        title=lambda wildcards: f"Combined Invariant Mass ({suffix_map[wildcards.suffix]})"
    shell:
        "python3 {input.script} {input.data} {input.dimeMC_reson} {output} '{params.title}' {input.dimeMC_nonre}"


rule pt_combined:
    input:
        data="data/kinematics/TOTEM_{suffix}.root",
        dimeMC_reson="data/dimeMC/resonant_{suffix}.root",
        dimeMC_nonre=expand("data/dimeMC/{production}_{{suffix}}.root", production=productions),
        script="scripts/joint/pt_histogram.py"
        config_file="config.yaml"
    output:
        "plots/joint/pt_{suffix}.png"
    params:
        title=lambda wildcards: f"Combined Transverse Momentum ({suffix_map[wildcards.suffix]})"
    shell:
        "python3 {input.script} {input.data} {input.dimeMC_reson} {output} '{params.title}' {input.dimeMC_nonre}"


rule eta_combined:
    input:
        data="data/kinematics/TOTEM_{suffix}.root",
        dimeMC_reson="data/dimeMC/resonant_{suffix}.root",
        dimeMC_nonre=expand("data/dimeMC/{production}_{{suffix}}.root", production=productions),
        script="scripts/joint/eta_histogram.py"
        config_file="config.yaml"
    output:
        "plots/joint/eta_{suffix}.png"
    params:
        title=lambda wildcards: f"Combined Rapidity ({suffix_map[wildcards.suffix]})"
    shell:
        "python3 {input.script} {input.data} {input.dimeMC_reson} {output} '{params.title}' {input.dimeMC_nonre}"


rule angles_combined:
    input:
        data="data/kinematics/TOTEM_{suffix}.root",
        dimeMC_reson="data/dimeMC/resonant_{suffix}.root",
        dimeMC_nonre=expand("data/dimeMC/{production}_{{suffix}}.root", production=productions),
        script="scripts/joint/proton_angles_histogram.py"
        config_file="config.yaml"
    output:
        "plots/joint/proton_angle_{suffix}.png"
    params:
        title=lambda wildcards: f"Proton Angle Difference ({suffix_map[wildcards.suffix]})"
    shell:
        "python3 {input.script} {input.data} {input.dimeMC_reson} {output} '{params.title}' {input.dimeMC_nonre}"
