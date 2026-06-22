#!/bin/bash

# Check if argument is correct
if [ $# -gt 1 ] || ["$1" =~ "clean"]; then
    echo "Usage: $0"
    echo "Usage: $0 clean"
    exit 1
fi

# Check for clean command
if [ "$1" = "clean" ]; then
    echo "Cleaning up exrec#.dat files..."
    cd "$(dirname "$0")/dimeMC/resonant" || exit 1
    rm -f exrex.out mxsq.out output.dat fort.40 batchjob.out a.out
    echo "Cleaned, dusted and polished."
    exit 0
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
echo

# Delete any existing exrec.dat and mxsq.out
echo "Cleaning up files exrec.dat and mxsq.out..."
rm -f exrec.dat mxsq.out

# Run simulation
echo "Running simulation..."
> log.out
./a.out >> log.out 2>&1 # move the generated histograms to log.out
if [ $? -ne 0 ]; then
    echo "Error: Run failed."
    exit 1
fi

# Run python scripts (add better checks for failure? Would involve changing python files too)
echo
echo "Running Python scripts."
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
echo