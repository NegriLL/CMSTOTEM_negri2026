# CERN Summer job 2026 Leonardo Negri

The objective of this repo is to combine data collected by CMS-TOTEM with synthetic data from DimeMC. We want to find kinetic differences in resonant and non-resonant productions of Glueball decay products. This way, we hope to be able to find a signal in the data.

I've set up this repository to work as easily as possible with the data. I am not a software developer, so I am sure I am not following best practices with the way I arranged the workflow and implemented some of the code. Regardless, as long as the data files and dime are set up correctly, the rest of the code should work easily through snakemake. Instructions are found below.

As the code grew in complexity, I had to go back and add a few hacks to the previous logic. These should be fixed at some point to make sure the codebase is more modular and the types of graphs are easier to customise. I added a ToDo at the end of the readme in case I (or someone else) has free time and drive to make these alterations.

If you have any questions, email me. I'm happy to try to help you understand my spaghetti.

## Instructions
1. Save the YounesNtuples to `data/YounesNtuples`. It should contain the following files
    - `TOTEM20.root, TOTEM21.root, TOTEM22.root, TOTEM23.root`
    - `TOTEM40.root, TOTEM41.root, TOTEM42.root, TOTEM43.root`
2. Download DimeMC and save it to the `dimeMC/` folder.
    - `dimemc` goes in `dimeMC/nonreson`
    - `dimemc_vsm` goes in `dimeMC/resonant`
3. Create a virtual environment. Check `requirements.txt`. You will still need to install root manually (I was using version 6.40.02). To install the other requirements automatically, you can try running
```shell
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
```
4. Run `scripts/utilities/dime_patcher.py` to update dimeMC for compatibility. This only has to be done once. The changes are as follows:
    - Accept `nev` (number of events) from commmand line arguments
    - Accept `pflag` (particle production type) from command line
    - Increase precision of output
5. Data pipeline is done through snakemake. You can try running the following to get all the graphs:
```shell
snakemake --cores all
```
6. Cuts can be edited in the config.yaml file for convenience.
7. If there are problems (and there will be), email me.

# Possible errors:
- If you get a permission denied error when trying to run job.sh, try running
``` shell
chmod +x job.sh
```
- If you get an I/O error, try deleting and reinstalling the virtual environment.

## ToDo
Some changes that would be nice to add.

- arg_handler should create a dictionary of the arguments dynamically. This way everything else can access the values dyncamically.
- plotter should be standardised so all functions can use the same plotter and customise how the plots are done through arguments.
- convert the filters to a class