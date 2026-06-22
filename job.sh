#!/bin/bash

# Folders
resonant_folder="$(dirname "$0")/dimeMC/resonant"
nonreson_folder="$(dirname "$0")/dimeMC/nonreson"

# fortran number of runs
num_runs=1

# check options
clean=false
nosim=false

while getopts "cnh" opt; do
    case $opt in
        c) clean=true ;;
        n) nosim=true ;;
        h) echo "Usage: $0 [-c] [-n] [-h]"
           echo "  -c  Clean dime files"
           echo "  -n  Skip simulation"
           echo "  -h  Show this help message"
           exit 0 ;;
        ?) echo "Usage: $0 [-c] [-n] [-h]"
           exit 1 ;;
    esac
done

# Check for clean command
if [ "$clean" == true ]; then
    echo "Cleaning up files..."
    to_delete="exrec.dat mxsq.dat output.dat fort.40 batchjob.out a.out"
    cd $resonant_folder || exit 1
    rm -f $to_delete
    cd ../..
    cd $nonreson_folder || exit 1
    rm -f $to_delete
    echo "Cleaned, dusted and polished."
    echo
    exit 0
fi

# simulation run code
function compile_and_run() {
    echo "Compiling $1"
    cd "$1" || exit 1
    gfortran *.f -o a.out >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "Error: $1 compilation failed!"
        exit 1
    fi
    echo "$1 compilation successful."
    > log.out
    ./a.out "$2" > log.out 2>&1
    if [ $? -ne 0 ]; then
        echo "Error: $1 Run failed."
        exit 1
    fi
}

if [ "$nosim" = true ]; then
    echo Skipping dime simulation
else
    compile_and_run "$resonant_folder" "$num_runs" &
    pid1=$!
    compile_and_run "$nonreson_folder" "$num_runs" &
    pid2=$!
    echo
fi

wait $pid1
status1=$?
wait $pid2
status2=$?

if [ $status1 -ne 0 ] || [ $status2 -ne 0 ]; then
    exit 1
fi


# Run python scripts (add better checks for failure? Would involve changing python files too)
function run_python() {
    echo "Running $1"
    python3 "$1" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "Error: Run failed!"
        echo
        exit 1
    fi
}

echo
echo "Running Python scripts."
if [ "$nosim" = true ]; then
    echo Skipping exrec to tree file creation.
else
    run_python "analysis/dimeMC/exrec_to_root_resonant.py"
    run_python "analysis/dimeMC/exrec_to_root.py"
fi
run_python "analysis/dimeMC/rho_plots_resonant.py"
run_python "analysis/dimeMC/kinematics.py"

echo "Done!"
echo