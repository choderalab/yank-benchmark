import numpy as np
import re
import openeye.oechem as oechem

# The input_file is the order in which the molecules are indexed
# So it is used as the main indexing sequence.
# tbe exp_data_file is the FEP+ and experimental data
input_file = '../input/c-Met_bmcl_neutral_docked.sdf'
exp_data_file = '../input/c-Met_bmcl_neutral_fepplus.sdf'
input_ifs = oechem.oemolistream(input_file)
# Create the data holders
exper_data = []
fepp = []
yank_imp_fe = []
yank_imp_err = []
yank_exp_fe = []
yank_exp_err = []
# Loop through all molecules in order
for index, mol in enumerate(input_ifs.GetOEGraphMols()):
    name = mol.GetTitle()
    exp_data_ifs = oechem.oemolistream(exp_data_file)
    for exper_mol in exp_data_ifs.GetOEGraphMols():
        # Ensure the molecule is the same name
        if exper_mol.GetTitle() == name:
            for pair in oechem.OEGetSDDataPairs(exper_mol):
                # Assign experimental and FEP+ free energy
                if pair.GetTag() == 'r_fepplus_exp_dG':
                    exper_data.append(float(pair.GetValue()))
                elif pair.GetTag() == 'r_fepplus_pred_dG':
                    fepp.append(float(pair.GetValue()))
    # Go through the implicit and explicit YANK calculations
    for solv, fe, err in zip(['imp', 'exp'], [yank_imp_fe, yank_exp_fe], [yank_imp_err, yank_exp_err]):
        with open('{0}licit/cmet-{1}-{0}.ipynb'.format(solv, index), 'r') as notebook:
            for line in notebook.readlines():
                # Grab only the free energy line
                if "Free energy of binding" in line:
                    fe_block = re.search('\((.*)\)', line).group(1)
                    # Order of group should be...
                    # free_energy, +-, error, kcal/mol
                    splits = fe_block.split()
                    free_energy = float(splits[0])
                    error = float(splits[2])
                    fe.append(free_energy)
                    err.append(error)
# Write out to multi-array NumPy File
np.savez('free_energy_data.npz',
         experimental=np.array(exper_data),
         fepplus=np.array(fepp),
         yank_explicit_fe=yank_exp_fe,
         yank_explicit_error=yank_exp_err,
         yank_implicit_fe=yank_imp_fe,
         yank_implicit_error=yank_imp_err)