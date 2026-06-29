rule all:
    input:
        directory("plots/dimeMC/kinematics_combined")


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

# translating to root (TODO: could be improved if we used the same code)
rule exrec_to_tree_resonant:
    input:
        data="dimeMC/resonant/exrec.dat",
        script="analysis/dimeMC/exrec_to_root_resonant.py"
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
        script="analysis/combine_trees.py"
    output:
        "data/combined/TOTEM_{suffix}.root"
    shell:
        "python3 {input.script} {input.files} {output}"


rule add_glueball_mass:
    input:
        tree="data/combined/TOTEM_{suffix}.root",
        script="analysis/create_invmass_branch.py"
    output:
        "data/glueball_mass/TOTEM_{suffix}.root"
    shell:
        "python3 {input.script} {input.tree} {output}"


#----------------------------------------------//----------------------------------------------#
# Combined Analysis
