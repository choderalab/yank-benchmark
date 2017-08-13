#!/usr/local/bin/env python

import os

import openmoltools as moltools
from openeye import oechem, oedocking


def create_receptor(protein_pdb_path, box):
    """Create an OpenEye receptor from a PDB file.

    Parameters
    ----------
    protein_pdb_path : str
        Path to the receptor PDB file.
    box : 1x6 array of float
        The minimum and maximum values of the coordinates of the box
        representing the binding site [xmin, ymin, zmin, xmax, ymax, zmax].

    Returns
    -------
    receptor : openeye.oedocking.OEReceptor
        The OpenEye receptor object.

    """
    input_mol_stream = oechem.oemolistream(protein_pdb_path)
    protein_oemol = oechem.OEGraphMol()
    oechem.OEReadMolecule(input_mol_stream, protein_oemol)

    box = oedocking.OEBox(*box)
    receptor = oechem.OEGraphMol()
    oedocking.OEMakeReceptor(receptor, protein_oemol, box)

    return receptor


def load_receptor(receptor_oeb_path):
    """Load an OpenEye receptor file in oeb format."""
    if not os.path.exists(receptor_oeb_path):
        raise FileNotFoundError('Could not find ', receptor_oeb_path)
    receptor = oechem.OEGraphMol()
    oedocking.OEReadReceptorFile(receptor, receptor_oeb_path)
    return receptor


def dock_molecule(receptor, molecule_smiles, n_conformations=10, n_poses=1):
    """Run the multi-conformer docker.

    Parameters
    ----------
    receptor : openeye.oedocking.OEReceptor
        The openeye receptor.
    molecule_smiles : str
        The SMILES string of the molecule.
    n_conformations : int, optional
        The number of omega conformations to pass to the multi-conformer
        docker (default is 10).
    n_poses : int, optional
        Number of binding poses to return.

    Returns
    -------
    docked_oemol : openeye.oechem.OEMol
        The docked multi-conformer OpenEye molecule.

    """
    dock = oedocking.OEDock()
    dock.Initialize(receptor)

    molecule_oemol = moltools.openeye.smiles_to_oemol(molecule_smiles)
    molecule_oemol = moltools.openeye.get_charges(molecule_oemol, keep_confs=n_conformations)

    docked_oemol = oechem.OEMol()
    dock.DockMultiConformerMolecule(docked_oemol, molecule_oemol, n_poses)

    return docked_oemol
