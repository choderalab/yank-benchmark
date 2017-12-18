# Analysis for Dec 18th 2017

The files in this directory are the analysis from December 18th, 2017.

The data were generated on the MSKCC Cluster. Explicit and Implicit calculations 
were run with 12 GPUs each

## Explicit Calculations

After some cluster issues, the total wall clock time of the simulation comes in at 4 days and 45 min.
Due to cluster problems, after the 1 day and 45 min, the initial simulations crashed and were resumed, 
so there was a small amount of overhead incurred with rebooting it.

Auto Protocol took just over 7 hours to complete

After the reported simulation time, 700 iterations per phase per molecule, this makes about 23% of the 
scheduled 3000 iterations complete

## Implicit Calculations 

These were started post discussion with Daniel the week before and ran for 
2 days, 15 hours, and 23 minutes. This completed all 3000 iterations per phase per molecule.

Auto Protocol took just over 1 hour to compute

## Common to both Explicit and Implicit

* In each folder is the static `yank analyze report` files in HTML format
* In each folder is the `*scatter.py` script which makes the FEP+ vs YANK free energy comparison
    * The Python script makes the `*hinge_vs_fepp.png` images
    * Data for these images drawn from the HTML files
* In each folder is the `auto` protocol path breakdown outputs in the `{phase}_{solvent}_paths.png` files
    * In the top level `analysis-results` folder is the `path_plot_script.py` script which makes these images
    * The individual `.yaml` files are not included in this analysis for path output.
