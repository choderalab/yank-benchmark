#!/usr/bin/env python

# =============================================================================
# MODULE DOCSTRING
# =============================================================================

"""Download from benchmarksets and prepare the input files for the calculations.

Requires Python 3.

"""


# =============================================================================
# GLOBAL IMPORTS
# =============================================================================

import os
import shutil
import tempfile
import urllib.request
from collections import namedtuple


# =============================================================================
# CONSTANTS
# =============================================================================

# TODO change me when CD files in nieldev branch will be merged to master.
INPUT_FILES_URL = 'https://raw.githubusercontent.com/MobleyLab/benchmarksets/nieldev/input_files/'


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
        If True, url is interpreted as relative to INPUT_FILES_URL.

    """
    # Create the directory if it doesn't exist.
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Resolve relative URL.
    if relative_url:
        url = INPUT_FILES_URL + url

    # Download and write file.
    with urllib.request.urlopen(url) as response, open(file_path, 'wb') as f:
        shutil.copyfileobj(response, f)


def merge_mol2_files(input_file_paths, output_file_path):
    """Merge all the input mol2 files into a single multi-conformer file.

    Requires OpenEye Toolkit.

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


# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

def prepare_cyclodextrin_files():
    """Download the CD mol2 files and merge all guests in a single file."""
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


if __name__ == '__main__':
    prepare_cyclodextrin_files()
