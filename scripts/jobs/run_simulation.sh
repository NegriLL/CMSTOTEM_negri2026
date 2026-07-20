#!/bin/bash
 
# set how many runs here. This can be improved in the future but for now it works
num_runs=500
 
# $1 = path to the fortran source file
# $2 = production rho/phi. Ignored by resonant file
fortran_path="$1"
num_runs="$2"
production="$3"
 
# change into dime folder
folder="$(dirname "$fortran_path")"
file="$(basename "$fortran_path")"
cd "$folder"
 
gfortran "$file" -o a.out >/dev/null 2>&1 || { echo "Compilation failed"; exit 1; }
 
# save output to log.out
./a.out "$num_runs" "$production" > log.out 2>&1 || { echo "Run failed, see log.out"; exit 1; }
 
# rename exrec.dat only if the argument for production was given
if [ -n "$production" ]; then
    mv exrec.dat "${production}_exrec.dat"
fi