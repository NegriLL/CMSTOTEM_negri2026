CERN Summer job 2026 Leonardo Negri

Set up:
1. Save the YounesNtuples to data/YounesNtuples. It should contain the following files
    - TOTEM20.ROOT, TOTEM21.root, TOTEM22.root, TOTEM23.root
    - TOTEM40.root, TOTEM41.root, TOTEM42.root, TOTEM43.root
2. Download dimeMC and save it to the dimeMC folder.
    - dimemc goes in nonreson
    - dimemc_vsm goes in resonant
3. It's a good idea to increase the precision of DimeMC output. Go into the code and change the format lines around ~1260 to E25.16
4. If you get a permission denied error when trying to run job.sh, try running "chmod +x job.sh" first