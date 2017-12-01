#!/usr/bin/env python

# =============================================================================
# MODULE DOCSTRING
# =============================================================================

"""Download and prepare the input files for the calculations.

See the docs of ``prepare_cyclodextrin_files()`` and ``prepare_t4lysozyme_files()``
for an exact description of the preparation.

Requires Python 3 and OpenEye.

"""


# =============================================================================
# GLOBAL IMPORTS
# =============================================================================

import os
import json
import shutil
import tempfile
import urllib.request
from collections import namedtuple

import mdtraj
import numpy as np
import openmoltools as moltools
from pdbfixer import PDBFixer
from simtk import unit
from simtk.openmm.app import PDBFile

from mcce import protonatePDB
from docking import create_receptor, dock_molecule


# =============================================================================
# CONSTANTS
# =============================================================================

# TODO change me when CD files in nieldev branch will be merged to master.
CD_INPUT_FILES_URL = 'https://raw.githubusercontent.com/MobleyLab/benchmarksets/nieldev/input_files/'
MCCE_PATH = '/home/andrrizzi/mcce'


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def download_and_save_file(url, file_path, relative_url=True):
    """Download and save a file.

    Parameters
    ----------
    url : str
        The URL of the file to download.
    file_path : str
        The path of the file to save.
    relative_url : bool
        If True, url is interpreted as relative to CD_INPUT_FILES_URL.

    """
    # Create the directory if it doesn't exist.
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Resolve relative URL.
    if relative_url:
        url = CD_INPUT_FILES_URL + url

    # Download and write file.
    with urllib.request.urlopen(url) as response, open(file_path, 'wb') as f:
        shutil.copyfileobj(response, f)


def merge_mol2_files(input_file_paths, output_file_path):
    """Merge all the input mol2 files into a single multi-conformer file.

    Atom names are standardized. Requires OpenEye Toolkit.

    Parameters
    ----------
    input_file_path : list of str
        Paths to the files to merge.
    output_file_path : str
        Path to the output mol2 file.

    Returns
    -------
    molecule : list of openeye.chem.OEMol
        The OpenEye Molecule found in the file.

    """
    from openeye import oechem

    # Load all files as OpenEye molecules.
    molecules = []
    for input_file_path in input_file_paths:
        ifs = oechem.oemolistream()
        if not ifs.open(input_file_path):
            oechem.OEThrow.Fatal('Unable to open {}'.format(input_file_path))

        for mol in ifs.GetOEMols():
            molecules.append(oechem.OEMol(mol))
        ifs.close()

    # Save multi-conformer mol2 file.
    ofs = oechem.oemolostream(output_file_path)
    ofs.SetFormat(oechem.OEFormat_MOL2H)

    for mol in molecules:
        # Write all molecules and standardize atom names.
        oechem.OEWriteMolecule(ofs, mol)
    ofs.close()

    # Fix residue name.
    with open(output_file_path, 'r') as f:
        output_lines = f.readlines()
    with open(output_file_path, 'w') as f:
        for line in output_lines:
            f.write(line.replace('<0>', 'MOL'))

    return molecules


def pdbfix_protein(input_pdb_path, output_pdb_path, find_missing_residues=True,
                   keep_water=False, ph=None):
    """Run PDBFixer on the input PDB file.

    Heterogen atoms are always removed.

    Parameters
    ----------
    input_pdb_path : str
        The PDB to fix.
    output_pdb_path : str
        The path to the output PDB file.
    find_missing_residues : bool, optional
        If True, PDBFixer will try to model the unresolved residues
        that appear in the amino acid sequence (default is True).
    keep_water : bool, optional
        If True, water molecules are not stripped (default is False).
    ph : float or None, optional
        If not None, hydrogen atoms will be added at this pH.

    """
    fixer = PDBFixer(filename=input_pdb_path)
    if find_missing_residues:
        fixer.findMissingResidues()
    else:
        fixer.missingResidues = {}
    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()
    fixer.removeHeterogens(keep_water)
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    if ph is not None:
        fixer.addMissingHydrogens(ph)

    # print(fixer.nonstandardResidues)
    # print(fixer.missingAtoms)
    # print(fixer.missingTerminals)

    with open(output_pdb_path, 'w') as f:
        PDBFile.writeFile(fixer.topology, fixer.positions, f)


# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

def prepare_cyclodextrin_files():
    """Download the CD mol2 files and merge all guests in a single file.

    The function downloads the alpha and beta cyclodextrin host and their
    guests as mol2 files from benchmarksets. The guest files of each host
    are merged into a single multi-molecule mol2 file. The atom names are
    standardized with OpenEye.

    The files are saved in ../cyclodextrin/input/.

    """
    input_file_dir_path = os.path.join('..', 'cyclodextrin', 'input')

    # Data to download all cyclodextrin molecules.
    # Some of the mol2 guest files are numbered with an extra 's'.
    # n_s_guests is the number of guests file named this way.
    CDSet = namedtuple('CDSet', ['url', 'host_type', 'n_s_guests', 'tot_n_guests'])
    cd_sets = [
        CDSet(url='cd-set1/mol2/', host_type='a', n_s_guests=14, tot_n_guests=22),
        CDSet(url='cd-set2/mol2/', host_type='b', n_s_guests=9, tot_n_guests=21)
    ]

    for cd_set_url, host_type, n_s_guests, tot_n_guests in cd_sets:
        n_p_guests = tot_n_guests - n_s_guests

        # Determine all paths.
        host_file_name = 'host-{}cd.mol2'.format(host_type)
        merged_guest_file_name = 'guests-{}cd.mol2'.format(host_type)
        host_file_path = os.path.join(input_file_dir_path, host_file_name)
        merged_guest_file_path = os.path.join(input_file_dir_path, merged_guest_file_name)

        # Determine all URL to downloads
        host_url = cd_set_url + host_file_name
        guest_urls = [cd_set_url + 'guest-{}.mol2'.format(i+1) for i in range(n_p_guests)]
        guest_urls += [cd_set_url + 'guest-s{}.mol2'.format(n_p_guests+i+1) for i in range(n_s_guests)]

        # Download host file first. This should be ready to go.
        download_and_save_file(host_url, host_file_path)

        with tempfile.TemporaryDirectory() as tmp_dir:
            # Download and save all the guests in a temporary directory.
            guest_file_paths = [os.path.join(tmp_dir, guest_url) for guest_url in guest_urls]
            for guest_url, guest_file_path in zip(guest_urls, guest_file_paths):
                download_and_save_file(guest_url, guest_file_path)

            # Merge all files in a single mol2 file.
            merge_mol2_files(guest_file_paths, merged_guest_file_path)


def prepare_t4lysozyme_files():
    """Prepare the input files for T4 Lysozyme calculations.

    The function download two crystal structures from the RCSB protein
    data bank for T4 L99A (181L, bound to benzene) and T4 L99A/M102Q
    (1LI2, bound to phenol). The protein is run through PDBFixer to
    remove waters and heterogen atoms and the protonation state of the
    protein is found with MCCE2.

    The ligands are generated

    """
    # Configuration.
    docking_box_side = 19.0  # In angstroms.

    # File paths.
    t4lysozyme_dir_path = os.path.join('..', 't4lysozyme', 'input')
    t4ligands_file_path = os.path.join('..', 't4lysozyme', 't4ligands.json')  # Input file.

    # Load all molecules to dock.
    with open(t4ligands_file_path, 'r') as f:
        t4ligands_set = json.load(f)

    # Benchmark sets. The name field is the key of t4ligands_set.
    T4Set = namedtuple('T4Set', ['name', 'pdb_code', 'ligand_dsl', 'phs'])
    t4_sets = [
        T4Set(name='l99a', pdb_code='181L', ligand_dsl='resname BNZ', phs=[5.5, 6.8, 5.45]),
        T4Set(name='l99a-m102q', pdb_code='1LI2', ligand_dsl='resname IPH', phs=[6.8])
    ]

    for t4_name, pdb_code, ligand_dsl, phs in t4_sets:
        with tempfile.TemporaryDirectory() as tmp_dir:
            for ph in phs:
                full_name = t4_name + '-' + str(ph).replace('.', '')

                # Temporary file paths.
                crystal_pdb_file_path = os.path.join(tmp_dir, full_name + '.pdb')
                pdbfixed_pdb_file_path = os.path.join(tmp_dir, full_name + '.pdbfixer.pdb')

                # Output file path for MCCE.
                mcce_pdb_file_path = os.path.join(t4lysozyme_dir_path, full_name + '.mcce.pdb')

                # Download crystal structure from RCSB.
                pdb_traj = mdtraj.load_pdb('http://files.rcsb.org/view/' + pdb_code + '.pdb')

                # Remove ligand and crystal waters to prepare for MCCE protonation.
                pdb_traj.save(crystal_pdb_file_path)
                pdbfix_protein(crystal_pdb_file_path, pdbfixed_pdb_file_path,
                               find_missing_residues=False, keep_water=False, ph=None)

                # Find protonation state MCCE. The reference experiments pH is 5.5.
                print('Find protonation state of {}'.format(full_name))
                protonatePDB(pdbfixed_pdb_file_path, outfile=mcce_pdb_file_path,
                             pH=5.5, mccepath=MCCE_PATH)

                # Set the docking box center to the ligand centroid.
                ligand_atoms = pdb_traj.topology.select(ligand_dsl)
                ligand_positions = np.array(pdb_traj.openmm_positions(0) / unit.angstrom)[ligand_atoms]
                box_center = np.mean(ligand_positions, axis=0)  # In angstroms.

                # Prepare receptor for docking.
                box_docking = np.concatenate((box_center + docking_box_side/2,
                                              box_center - docking_box_side/2))
                receptor = create_receptor(mcce_pdb_file_path, box_docking)

                # Dock and store docked positions.
                print('Docking ligands for {}'.format(full_name))
                docked_molecule_file_paths = {}
                for molecule_name, molecule_data in t4ligands_set[t4_name].items():
                    if molecule_data['pH'] == ph:
                        docked_molecule_file_path = os.path.join(tmp_dir, molecule_name + '.mol2')
                        docked_oemol = dock_molecule(receptor, molecule_data['smiles'])
                        moltools.openeye.molecule_to_mol2(docked_oemol, docked_molecule_file_path, residue_name='MOL')

                        # Be sure to keep ligands that were assayed in different buffers separated.
                        # We also isolate the numeric part of the ligand id to name the output file.
                        reference_doi = molecule_data['doi']
                        molecule_idx = int(molecule_name.split('-')[-1])
                        try:
                            docked_molecule_file_paths[reference_doi][0].append(molecule_idx)
                            docked_molecule_file_paths[reference_doi][1].append(docked_molecule_file_path)
                        except KeyError:
                            docked_molecule_file_paths[reference_doi] = [[molecule_idx],
                                                                         [docked_molecule_file_path]]

                # Merge docked positions into a multi-molecule mol2 file.
                for reference_doi, (molecule_indices, file_paths) in docked_molecule_file_paths.items():
                    # Determine output file name.
                    suffix = '{}-{}'.format(min(molecule_indices), max(molecule_indices))
                    ligands_mol2_file_name = 'ligands-{}-{}.mol2'.format(t4_name, suffix)
                    ligands_mol2_file_path = os.path.join(t4lysozyme_dir_path, ligands_mol2_file_name)
                    # Merge docked molecules into a single mol2 file.
                    merge_mol2_files(file_paths, ligands_mol2_file_path)


if __name__ == '__main__':
    prepare_cyclodextrin_files()
    prepare_t4lysozyme_files()
