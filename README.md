CERN Summer job 2026 Leonardo Negri

Instructions
1. Save the YounesNtuples to `data/YounesNtuples`. It should contain the following files
    - `TOTEM20.ROOT, TOTEM21.root, TOTEM22.root, TOTEM23.root`
    - `TOTEM40.root, TOTEM41.root, TOTEM42.root, TOTEM43.root`
2. Download DimeMC and save it to the `dimeMC/` folder.
    - `dimemc` goes in `dimeMC/nonreson`
    - `dimemc_vsm` goes in `dimeMC/resonant`
3. It's a good idea to increase the precision of DimeMC output. Go into the code and change the format lines around ~1260 to `E25.16`. This might have already been done when you are reading this in the future.
4. You must substitute the following lines to DimeMC (both versions) so it can get arguments from the command line.
    - Where nev (run count) is declared
    ```fortran
    CALL GET_COMMAND_ARGUMENT(1, arg)
    READ(arg, *) nev        ! no. of unweighted events generated to event record
    ```
    - Where pflag is declared
    ```fortran
    CALL GET_COMMAND_ARGUMENT(2, pflag)    ! Process generated - see preamble for options
    ```
    - You must also add the following variable to the `character` declaration at the very beginning of the program
    ```fortran
    character prefix*50,fsp*10,order*10,pflag*10,fsi*10,formf*10
     &,ppbar*10,output*10,mregge*10,cuts*10,unw*10, arg*10
    ```
5. Create a virtual environment. Check `requirements.txt`. To install the requirements automatically, you can try running
```shell
python -m pip download -r requirements.txt
```
6. Everything can be run using snakemake rules. You can try running the following to get all the graphs:
```shell
snakemake --cores all
```
7. Cuts can be edited in the config.yaml file for convenience.
8. If there are problems (and there will be), email me.

Possible errors:
- If you get a permission denied error when trying to run job.sh, try running
``` shell
chmod +x job.sh
```
- If you get an I/O error, try deleting and reinstalling the virtual environment.