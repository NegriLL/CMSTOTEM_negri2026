# Load configuration
configfile: "config.yaml"

simulated_runs = config["simulated_runs"]
resonant_productions = config["resonant_production"]
nonreson_productions = config["nonreson_productions"]
fortran_files = config["fortran_files"]
suffix_map = config["suffix_map"]
title_map = config["title_map"]

# Defining basic constraints
wildcard_constraints:
    suffix="D|P|A",
    cuts_folder="cut|raw|outside",
    nonreson_production="|".join(nonreson_productions),
    resonant_production="|".join(resonant_productions)


# General rule to generate graphs. This can be edited to accomodate new stuff
rule all:
    input:
        expand(
            "plots/dimeMC/kinematics_combined/{resonant_production}/{nonreson_production}",
            resonant_production=resonant_productions,
            nonreson_production=nonreson_productions,
        ),
        expand(
            "plots/joint_{resonant_production}/{cuts_folder}/{graph}_{suffix}.png",
            resonant_production=resonant_productions,
            cuts_folder=["cut", "raw", "outside"],
            graph=["eta", "pt", "invmass", "proton_angle"],
            suffix=["D", "P", "A"],
        ),
        expand(
            "plots/kaon/{cuts_folder}/{graph}_{suffix}.png",
            cuts_folder=["cut", "raw", "outside"],
            suffix=["D", "P", "A"],
            graph=["eta", "pt"]
        )

# Simulation rules
rule simulate_resonant:
    input:
        fortran=fortran_files["resonant"],
        script="scripts/jobs/run_simulation.sh"
    params:
        num_runs=simulated_runs
    output:
        "dimeMC/resonant/{resonant_production}_exrec.dat"
    shadow: "copy-minimal"
    shell:
        "./{input.script} {input.fortran} {params.num_runs} {wildcards.resonant_production}"


rule simulate_nonreson:
    input:
        fortran=fortran_files["nonreson"],
        script="scripts/jobs/run_simulation.sh"
    params:
        num_runs=simulated_runs
    output:
        "dimeMC/nonreson/{nonreson_production}_exrec.dat"
    shadow: "copy-minimal"
    shell:
        "./{input.script} {input.fortran} {params.num_runs} {wildcards.nonreson_production}"


rule exrec_to_tree_resonant:
    input:
        data="dimeMC/resonant/{resonant_production}_exrec.dat",
        script="scripts/dimeMC/exrec_to_root.py"
    output:
        "data/dimeMC/resonant_{resonant_production}_A.root"
    log:
        "logs/exrec_to_tree_resonant_{resonant_production}_A.log"
    shell:
        "python3 {input.script} {input.data} {output} &> {log}"


rule exrec_to_tree_nonreson:
    input:
        data="dimeMC/nonreson/{nonreson_production}_exrec.dat",
        script="scripts/dimeMC/exrec_to_root.py"
    output:
        "data/dimeMC/{nonreson_production}_A.root"
    log:
        "logs/exrec_to_tree_nonreson_{nonreson_production}_A.log"
    shell:
        "python3 {input.script} {input.data} {output} &> {log}"


rule split_dimeMC_resonant:
    input:
        data="data/dimeMC/resonant_{resonant_production}_A.root",
        script="scripts/dimeMC/split.py"
    output:
        "data/dimeMC/resonant_{resonant_production}_D.root",
        "data/dimeMC/resonant_{resonant_production}_P.root"
    shell:
        "python3 {input.script} {input.data}"


rule split_dimeMC_nonreson:
    input:
        data="data/dimeMC/{nonreson_production}_A.root",
        script="scripts/dimeMC/split.py"
    output:
        "data/dimeMC/{nonreson_production}_D.root",
        "data/dimeMC/{nonreson_production}_P.root"
    shell:
        "python3 {input.script} {input.data}"


# DimeMC scripts rules
rule kinematic_scripts:
    input:
        data_reson="data/dimeMC/resonant_{resonant_production}_A.root",
        data_nonre="data/dimeMC/{nonreson_production}_A.root",
        script="scripts/dimeMC/kinematics.py"
    output:
        directory("plots/dimeMC/kinematics_combined/{resonant_production}/{nonreson_production}")
    log:
        "logs/kinematic_scripts_{resonant_production}_{nonreson_production}.log"
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
rule joint_combined:
    input:
        data="data/kinematics/TOTEM_{suffix}.root",
        dimeMC_reson="data/dimeMC/resonant_{resonant_production}_{suffix}.root",
        dimeMC_nonre=lambda wildcards: expand("data/dimeMC/{p}_{suffix}.root", p=nonreson_productions, suffix=wildcards.suffix),
        script="scripts/joint/{graph}_histogram.py",
    params:
        title=lambda wildcards: f"{title_map[wildcards.graph]} ({suffix_map[wildcards.suffix]})",
    output:
        "plots/joint_{resonant_production}/{cuts_folder}/{graph}_{suffix}.png"
    shell:
        "python3 {input.script} {input.data} {input.dimeMC_reson} {output} '{params.title}' {wildcards.cuts_folder} {input.dimeMC_nonre}"

#-----------------------------------------// Kaon plots \\-----------------------------------------#
rule kaon_graphs:
    input:
        data="data/kinematics/TOTEM_{suffix}.root",
        dimeMC_reson="data/dimeMC/resonant_phi_{suffix}.root",
        dimeMC_nonre="data/dimeMC/phi_{suffix}.root",
        script="scripts/kaon/kaon_{graph}_histogram.py",
        plotter="scripts/utilities/plotter.py",
        config_file="config.yaml"
    output:
        "plots/kaon/{cuts_folder}/{graph}_{suffix}.png"
    params:
        title=lambda wildcards: f"Kaon {title_map[wildcards.graph]} ({suffix_map[wildcards.suffix]})",
    shell:
        "python3 {input.script} {input.data} {input.dimeMC_reson} {output} '{params.title}' {wildcards.cuts_folder} {input.dimeMC_nonre}"