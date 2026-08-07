CERN Summer job 2026 Leonardo Negri

Instructions
1. Save the YounesNtuples to `data/YounesNtuples`. It should contain the following files
    - `TOTEM20.ROOT, TOTEM21.root, TOTEM22.root, TOTEM23.root`
    - `TOTEM40.root, TOTEM41.root, TOTEM42.root, TOTEM43.root`
2. Download DimeMC and save it to the `dimeMC/` folder.
    - `dimemc` goes in `dimeMC/nonreson`
    - `dimemc_vsm` goes in `dimeMC/resonant`
3. Create a virtual environment. Check `requirements.txt`. To install the requirements automatically, you can try running
```shell
python -m pip download -r requirements.txt
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

Possible errors:
- If you get a permission denied error when trying to run job.sh, try running
``` shell
chmod +x job.sh
```
- If you get an I/O error, try deleting and reinstalling the virtual environment.