# Neutral Ligands for c-Met Hinge Data Set from Merck KGaA

This data set is a set of hinge ligands for the c-Met kinase binding in explicit solvent

This set can be found from the following paper:

```
Dorsch, D., Schadt, O., Stieber, F., Meyring, M., Grädler, U., Bladt, F., 
Friese-Hamima, M, Knühla, C., Pehla, U., and Blaukat, A. (2015). 
Identification and optimization of pyridazinones as potent and selective c-Met kinase inhibitors. 
Bioorganic & Medicinal Chemistry Letters, 25(7), 1597–1602. 
https://doi.org/10.1016/j.bmcl.2015.02.002

```

## EXPERIMENTAL: SAMS input files

* `sams-twostage-boresch-dense.yaml` - single-replica SAMS with dense alchemical protocol and Boresch restraints (experimental)
* `sams-twostage-harmonic-dense.yaml` - single-replica SAMS with dense alchemical protocol and Harmonic restraints (experimental)
* `repex-twostage-auto.yaml` - single-replica replica-exchange with thermodynamic trailblazing (for comparison)
* `sams-twostage-auto.yaml` - single-replica SAMS with thermodynamic trailblazing (not recommended)

## Manifest

* `input/c-Met_bmcl_neutral_docked.sdf`: Docked ligand structures
* `input/c-Met_bmcl_neutral_fepplus.sdf`: Provided results from FEP+ and experimental values  
* `input/met_4r1y_mae_prot.pdb`: c-Met protein used for the neutral set 
* `input/4r1y_pocket_resSeq.npy`: List of residue numbers in the PDB who have atoms within 4.5 A of the docked Ligands. 
   Used to target the centroid of the receptor for harmonic restraints since the pocket is not near the receptor 
   centroid. This is stored as a NumPy array, use `numpy.load()` to access it.
   * IMPORTANT: This list only has Residue Numbers as they appear in the PDB file
   * To get the correct residue ID's in absolute index, run the file in `input/list_sequences.py`
* `explicit-all.yaml`: YAML file to run the ligands in the SDF file
* `run-slurm-all.sh`: SLURM script to run the YAML file for all ligands (Merck KGaA GTX1080 Cluster)
* `run-lsf-all.sh`: LSF script to run the YAML file for all ligands (MSKCC *Lilac* Cluster)
* `README.md`: This document.

## Instructions
Run the appropriate cluster submission file, after you have adapted it to your cluster

## Single Simulations Manifest

The Python script here sets up a single simulation for each ligand in its own directory with its 
own YAML file and submission script.

* `populate_neutral.py`: Build script to populate individual ligand run files from YAML and SLURM skeletons  
* `run-slurm-skel.sh`: Skeletal SLURM script for running ligands (Merck KGaA GTX1080 Cluster)
* `explicit-skel.yaml`: Skeletal YAML file used as template for individual ligand setup 


### Single Simulations Instructions

Run the `populate_neutral.py` script to make a directory for each ligand in the `c-Met_bmcl_neutral_docked.sdf` file.
This will create directories containing a unique yaml and slurm script.

If you want to run all the molecules as one simulation, set the `select` in the skeletal YAML file to `all` and replace 
the `restrained_receptor_atoms` with the selection you want to restrain to or remove the entry all together. 
See the `populate_neutral.py` file for how to use the `.npy` file to tag residues near the binding site.
