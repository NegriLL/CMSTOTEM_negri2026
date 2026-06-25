rule all:
    input:
        directory("plots/dimeMC/kinematics_combined")

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
        "dimeMC/resonant/exrec.dat"
    output:
        "data/dimeMC/exrec_resonant.root"
    log:
        "logs/exrec_to_tree_resonant.log"
    shell:
        "python3 analysis/dimeMC/exrec_to_root_resonant.py {input} {output} &> {log}"

rule exrec_to_tree_nonreson:
    input:
        "dimeMC/nonreson/exrec.dat"
    output:
        "data/dimeMC/exrec_nonreson.root"
    log:
        "logs/exrec_to_tree_nonreson.log"
    shell:
        "python3 analysis/dimeMC/exrec_to_root.py {input} {output} &> {log}"

rule kinematic_analysis:
    input:
        "data/dimeMC/exrec_resonant.root",
        "data/dimeMC/exrec_nonreson.root"
    output:
        directory("plots/dimeMC/kinematics_combined")
    log:
        "logs/kinematic_analysis.log"
    shell:
        "python3 analysis/dimeMC/kinematics.py {input} {output} &> {log}"