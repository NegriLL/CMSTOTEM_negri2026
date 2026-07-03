rule all:
    input:
        directory("plots/dimeMC/kinematics_combined"),
        expand(
            "plots/joint/{graph}_{config}.png",
            graph=["eta", "pt", "invmass", "proton_angle"],
            config=["D", "P", "A"],
        )


# Simulation rules
rule simulate_resonant:
    input:
        fortran="dimeMC/resonant/dimemcv1.07_vsm.f",
        script="jobs/run_simulation.sh"
    output:
        "dimeMC/resonant/exrec.dat"
    shell:
        "./{input.script} {input.fortran}"

rule simulate_nonreson:
    input:
        fortran="dimeMC/nonreson/dimemcv1.07.f",
        script="jobs/run_simulation.sh"
    output:
        "dimeMC/nonreson/exrec.dat"
    shell:
        "./{input.script} {input.fortran}"

rule exrec_to_tree_resonant:
    input:
        data="dimeMC/resonant/exrec.dat",
        script="analysis/dimeMC/exrec_to_root.py"
    output:
        "data/dimeMC/exrec_resonant.root"
    log:
        "logs/exrec_to_tree_resonant.log"
    shell:
        "python3 {input.script} {input.data} {output} &> {log}"
        
rule exrec_to_tree_nonreson:
    input:
        data="dimeMC/nonreson/exrec.dat",
        script="analysis/dimeMC/exrec_to_root.py"
    output:
        "data/dimeMC/exrec_nonreson.root"
    log:
        "logs/exrec_to_tree_nonreson.log"
    shell:
        "python3 {input.script} {input.data} {output} &> {log}"


# DimeMC analysis rules
rule kinematic_analysis:
    input:
        data_reson="data/dimeMC/exrec_resonant.root",
        data_nonre="data/dimeMC/exrec_nonreson.root",
        script="analysis/dimeMC/kinematics.py"
    output:
        directory("plots/dimeMC/kinematics_combined")
    log:
        "logs/kinematic_analysis.log"
    shell:
        "python3 {input.script} {input.data_reson} {input.data_nonre} {output} &> {log}"


#----------------------------------------------//----------------------------------------------#
# Data analysis rules
# Rules for combining trees for [D]iagonal [P]arallel and [A]ll
rule combine_trees:
    input:
        files=lambda wildcards: expand(
            "data/YounesNtuples/TOTEM{p}{n}.root",
            p={"D": ["2"], "P": ["4"], "A": ["2", "4"]}[wildcards.suffix],
            n=range(0, 4)
        ),
        script="analysis/utilities/combine_trees.py"
    output:
        "data/combined/TOTEM_{suffix}.root"
    shell:
        "python3 {input.script} {input.files} {output}"


rule add_glueball_mass:
    input:
        tree="data/combined/TOTEM_{suffix}.root",
        script="analysis/utilities/create_invmass_branch.py"
    output:
        "data/glueball_mass/TOTEM_{suffix}.root"
    shell:
        "python3 {input.script} {input.tree} {output}"

rule add_kinematics:
    input:
        tree="data/glueball_mass/TOTEM_{suffix}.root",
        script="analysis/utilities/create_kinematic_branch.py"
    output:
        "data/kinematics/TOTEM_{suffix}.root"
    shell:
        "python3 {input.script} {input.tree} {output}"

#----------------------------------------------//----------------------------------------------#
# Combined Analysis

suffix_map = {
    "D": "Diagonal",
    "A": "All",
    "P": "Parallel",
}

rule inv_mass_combined:
    input:
        data="data/kinematics/TOTEM_{suffix}.root",
        dimeMC_reson="data/dimeMC/exrec_resonant.root",
        dimeMC_nonre="data/dimeMC/exrec_nonreson.root",
        script="analysis/joint/invariant_mass_histogram.py"
    output:
        "plots/joint/invmass_{suffix}.png"
    params:
        title=lambda wildcards: f"Combined Invariant Mass ({suffix_map[wildcards.suffix]})"
    shell:
        "python3 {input.script} {input.data} {input.dimeMC_reson} {input.dimeMC_nonre} {output} '{params.title}'"


rule pt_combined:
    input:
        data="data/kinematics/TOTEM_{suffix}.root",
        dimeMC_reson="data/dimeMC/exrec_resonant.root",
        dimeMC_nonre="data/dimeMC/exrec_nonreson.root",
        script="analysis/joint/pt_histogram.py"
    output:
        "plots/joint/pt_{suffix}.png"
    params:
        title=lambda wildcards: f"Combined Transverse Momentum ({suffix_map[wildcards.suffix]})"
    shell:
        "python3 {input.script} {input.data} {input.dimeMC_reson} {input.dimeMC_nonre} {output} '{params.title}'"


rule eta_combined:
    input:
        data="data/kinematics/TOTEM_{suffix}.root",
        dimeMC_reson="data/dimeMC/exrec_resonant.root",
        dimeMC_nonre="data/dimeMC/exrec_nonreson.root",
        script="analysis/joint/eta_histogram.py"
    output:
        "plots/joint/eta_{suffix}.png"
    params:
        title=lambda wildcards: f"Combined Rapidity ({suffix_map[wildcards.suffix]})"
    shell:
        "python3 {input.script} {input.data} {input.dimeMC_reson} {input.dimeMC_nonre} {output} '{params.title}'"


rule angles_combined:
    input:
        data="data/kinematics/TOTEM_{suffix}.root",
        dimeMC_reson="data/dimeMC/exrec_resonant.root",
        dimeMC_nonre="data/dimeMC/exrec_nonreson.root",
        script="analysis/joint/proton_angles_histogram.py"
    output:
        "plots/joint/proton_angle_{suffix}.png"
    params:
        title=lambda wildcards: f"Proton Angle Difference ({suffix_map[wildcards.suffix]})"
    shell:
        "python3 {input.script} {input.data} {input.dimeMC_reson} {input.dimeMC_nonre} {output} '{params.title}'"
