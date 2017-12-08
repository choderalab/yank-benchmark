#!/usr/bin/env python
"""
Populate the directories to run the neutral ligands individually
"""

import openeye.oechem as oechem
import mdtraj as md
import os
import numpy as np

# Read in the data:
with open('explicit-skel.yaml', 'r') as f:
    raw_yaml = f.read()
with open('run-slurm-skel.sh', 'r') as f:
    raw_slurm  = f.read()
pocket = np.load('../input/4r1y_pocket_resSeq.npy')
ligands = '../input/c-Met_bmcl_neutral_docked.sdf'
receptor = '../input/met_4r1y_mae_prot.pdb'
t = md.load(receptor).topology
pocket_indices = [residue.index for residue in t.residues if residue.resSeq in pocket]
ifs = oechem.oemolistream(ligands)
for i, mol in enumerate(ifs.GetOEGraphMols()):
    replaced_select = raw_yaml.replace('REPLACE_SELECT', str(i))
    pocket_string = '('
    pocket_string += ' or '.join(['resid {}'.format(pocket_index) for pocket_index in pocket_indices])
    pocket_string += ') and (mass > 1.5)'
    final_raw_yaml = replaced_select.replace('REPLACE_RESTRAINED', pocket_string)
    molname = mol.GetTitle()
    os.makedirs(molname, exist_ok=True)
    with open(os.path.join(molname, 'explicit.yaml'), 'w') as explicit:
        explicit.write(final_raw_yaml)
    with open(os.path.join(molname, 'run-slurm.sh'),  'w') as slurm:
        slurm.write(raw_slurm.replace('XXX', str(i)))
