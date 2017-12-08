# Neutral Ligands for c-Met Hinge Data Set from Merck KGaA

This data set is a set of hinge ligands for the c-Met kinase binding in explicit solvent

This is currently a crude first pass which has not been fully debugged and will 
likely need refinement

## Manifest

* `input/c-Met_bmcl_neutral_docked.sdf`: Docked ligand structures  
* `input/met_4r1y_mae_prot.pdb`: c-Met protein used for the neutral set 
* `input/4r1y_pocket_resSeq.npy`: List of residue numbers in the PDB who have atoms within 4.5 A of the docked Ligands. 
   Used to target the centroid of the receptor for harmonic restraints since the pocket is not near the receptor
   centroid. This is stored as a NumPy array, use `numpy.load()` to access it.
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
