#!/usr/local/bin/env python

import os

import openmoltools as moltools
from openeye import oechem, oedocking


def create_receptor(protein_pdb_path, box, receptor_oeb_path=None):
    input_mol_stream = oechem.oemolistream(protein_pdb_path)
    protein_oemol = oechem.OEGraphMol()
    oechem.OEReadMolecule(input_mol_stream, protein_oemol)

    box = oedocking.OEBox(*box)
    receptor = oechem.OEGraphMol()
    oedocking.OEMakeReceptor(receptor, protein_oemol, box)

    if receptor_oeb_path is not None:
        oedocking.OEWriteReceptorFile(receptor, receptor_oeb_path)

    return receptor


def load_receptor(receptor_oeb_path):
    if not os.path.exists(receptor_oeb_path):
        raise FileNotFoundError('Could not find ', receptor_oeb_path)
    receptor = oechem.OEGraphMol()
    oedocking.OEReadReceptorFile(receptor, receptor_oeb_path)
    return receptor


def dock_molecule(receptor, molecule_smiles, n_conformations=10, n_poses=1):
    dock = oedocking.OEDock()
    dock.Initialize(receptor)

    molecule_oemol = moltools.openeye.smiles_to_oemol(molecule_smiles)
    molecule_oemol = moltools.openeye.get_charges(molecule_oemol, keep_confs=n_conformations)

    docked_oemol = oechem.OEMol()
    dock.DockMultiConformerMolecule(docked_oemol, molecule_oemol, n_poses)

    return docked_oemol
