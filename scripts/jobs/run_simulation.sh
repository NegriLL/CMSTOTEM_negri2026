#!/bin/bash

# set how many runs here. This can be improved in the future but for now it works
num_runs=40000
# change into dime folder
folder="$(dirname "$1")"
file="$(basename "$1")"
cd "$folder"
gfortran "$file" -o a.out >/dev/null 2>&1 || { echo "Compilation failed"; exit 1; }
# save output to log.out
./a.out "$num_runs" > log.out 2>&1 || { echo "Run failed, see log.out"; exit 1; }