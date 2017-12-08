"""
List the residues near the binding pocket
"""
import numpy as np

pocket = np.load('4r1y_pocket_resSeq.npy')
print(pocket)
pocket_string = '('
pocket_string += ' or '.join(['residue {}'.format(pocket_id) for pocket_id in pocket])
pocket_string += ') and (mass > 1.5)'
print(pocket_string)
