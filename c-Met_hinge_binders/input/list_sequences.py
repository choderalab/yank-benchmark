"""
List the residues near the binding pocket
"""
import numpy as np
import mdtraj as md


def make_mdtraj_string(input, keyword):
    pocket_string = '('
    pocket_string += ' or '.join([keyword + ' {}'.format(id) for id in input])
    pocket_string += ') and (mass > 1.5)'
    return pocket_string

pocket = np.load('4r1y_pocket_resSeq.npy')
print("Residue ID's: {}".format(pocket))
residue_id_md_select = make_mdtraj_string(pocket, 'residue')
print("Residue ID Select:\n"
      "{}".format(residue_id_md_select))
t = md.load('met_4r1y_mae_prot.pdb').topology
indices = [residue.index for residue in t.residues if residue.resSeq in pocket]
residue_index_md_select = make_mdtraj_string(indices, 'resid')

id_select = t.select(residue_id_md_select)
index_select = t.select(residue_index_md_select)
assert np.array_equal(id_select, index_select)
print("Residue Indices: {}".format(indices))
print("Residue Indices Select:\n"
      "{}".format(residue_index_md_select))
