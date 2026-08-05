#!/bin/bash
 
# $1 = path to the fortran source file
# $2 = number of runs
# $3 = production rho/phi. Ignored by resonant file
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
 
# rename exrec.dat
mv exrec.dat "${production}_exrec.dat"