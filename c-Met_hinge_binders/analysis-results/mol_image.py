import openeye.oechem as oechem
from openeye import oedepict

# The input_file is the order in which the molecules are indexed
# So it is used as the main indexing sequence.
input_file = '../input/c-Met_bmcl_neutral_docked.sdf'
input_ifs = oechem.oemolistream(input_file)
# Loop through all molecules in order
width, height, scale = 800, 800, oedepict.OEScale_AutoScale
opts = oedepict.OE2DMolDisplayOptions(width, height, scale)
for index, mol in enumerate(input_ifs.GetOEGraphMols()):
    oedepict.OEPrepareDepiction(mol)
    opts.SetAromaticStyle(oedepict.OEAromaticStyle_Circle)
    disp = oedepict.OE2DMolDisplay(mol, opts)
    oedepict.OERenderMolecule("mol_images/mol_image{}.png".format(index), disp)