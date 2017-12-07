# Neutral Ligands for c-Met Hinge Dataset from Merck KGaA

This data set is a set of hinge ligands for the c-Met kinase binding in explicit solvent

This is currently a crude first pass which has not been fully debugged and will need refinement.

## Manifest

* `c-Met_bmcl_neutral_docked.sdf`: Docked ligand structures  
* `met_4r1y_mae_prot.pdb`: c-Met protien used for the neutral set 
* `populate_neutral.py`: Build script to popultate individual ligand run files from yaml and slurm skeletons  
* `run-slurm-skel.sh`: Skeletal SLURM script for running ligands (Merck KGaA GTX1080 Cluster)
* `explicit-skel.yaml`: Skeletal YAML file used as template for individual ligand setup 
* `4r1y_pocket_resSeq.npy`: List of residue numbers in the PDB who have atoms within 4.5 A of the docked Ligands. 
   Used to target the centroid of the receptor for harmonic restraints since the pocket is not near the receptor
   centroid.

## Instructions

Run the `populate_neutral.py` script to make a directory for each ligand in the `c-Met_bmcl_neutral_docked.sdf` file.
This will create directories containing a unique yaml and slurm script.

If you want to run all the molecules as one simulation, set the `select` in the skeletal YAML file to `all` and replace 
the `restrained_receptor_atoms` with the selection you want to restrain to or remove the entry all together. 
See the `populate_neutral.py` file for how to use the `.npy` file to tag residues near the binding site.
