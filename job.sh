#!/bin/bash

# Set number of default runs
default_runs=5

# Check if argument is correct
if [ $# -gt 1 ]; then
    echo "Usage: $0"
    echo "Usage: $0 <number_of_runs>"
    echo "Usage: $0 clean"
    exit 1
fi

# Check for clean command
if [ "$1" = "clean" ]; then
    echo "Cleaning up exrec#.dat files..."
    cd "$(dirname "$0")/dimeMC/resonant" || exit 1
    rm -f exrec[0-9]*.dat exrec_combined.dat batchjob.out
    echo "Deleted all exrec#.dat, exrec_combined.dat, and batchjob.out files."
    exit 0
fi

# Check for valid number as argument, otherwise run default_runs
if [ $# -eq 0 ]; then
    echo "Running default: 5 runs"
    num_runs=$default_runs
elif ! [[ "$1" =~ ^[0-9]+$ ]] || [ "$1" -eq 0 ]; then
    echo "Error: Argument must be a positive integer"
    exit 1
else
    num_runs=$1
fi

# Change to the dimemc_vsm directory
echo "Changing to dimemc_vsm directory..."
cd "$(dirname "$0")/dimeMC/resonant" || exit 1

# Compile the Fortran code
echo "Compiling dimemcv1.07_vsm.f..."
gfortran dimemcv1.07_vsm.f -o a.out >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: DIME compilation failed!"
    exit 1
fi
echo "DIME compilation successful."

# Delete any existing exrec#.dat and mxsq.out
echo "Cleaning up any existing exrec#.dat files..."
rm -f exrec[0-9]*.dat exrec_combined.dat
rm -f mxsq.out

echo "Running $num_runs simulation(s)..."
# Clear previous log file
> batchjob.out

# Main loop
for ((i=1; i<=num_runs; i++)); do
    echo "Run $i of $num_runs..."
    ./a.out >> batchjob.out 2>&1 # move the generated histograms to batchjob.out
    if [ $? -ne 0 ]; then
        echo "Error: Run $i failed"
        exit 1
    fi
    
    # Rename the exrec.out
    if [ -f exrec.dat ]; then
        mv exrec.dat "exrec$i.dat"
        echo "  Renamed exrec.dat to exrec$i.dat"
    else
        echo "Error: exrec.dat not generated in run $i"
        exit 1
    fi
done

# Concatenate all exrec#.dat files
echo "Concatenating all exrec#.dat files into exrec_combined.dat..."
cat exrec[0-9]*.dat > exrec_combined.dat

if [ $? -eq 0 ]; then
    echo "  DimeMC runs completed successfully!"
    echo "  Generated file: exrec_combined.dat"
else
    echo "Error: Failed to concatenate files"
    exit 1
fi

# Run python scripts (add better checks for failure? Would involve changing python files too)
echo "Generating root files..."
cd ../..
python3 analysis/dimeMC/exrec_to_root_resonant.py > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Failed to generate exrec.root"
    exit 1
fi
echo "Generating graphs..."
python3 analysis/dimeMC/rho_plots_resonant.py > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Failed to generate graphs"
    exit 1
fi
echo "Done!"