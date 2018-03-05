import numpy as np
import os
import yank.analyze as analyze
import yaml
import sys
import simtk.unit as unit

T = 300*unit.kelvin
kB = unit.BOLTZMANN_CONSTANT_kB * unit.AVOGADRO_CONSTANT_NA
kT = T * kB / unit.kilocalories_per_mole

spacing = 100


def prepare_mbar_input_data(sampled_energy_matrix, unsampled_energy_matrix):
    """Convert the sampled and unsampled energy matrices into MBAR ready data"""
    nstates, _, niterations = sampled_energy_matrix.shape
    _, nunsampled, _ = unsampled_energy_matrix.shape
    # Subsample data to obtain uncorrelated samples
    N_k = np.zeros(nstates, np.int32)
    N = niterations  # number of uncorrelated samples
    N_k[:] = N
    mbar_ready_energy_matrix = sampled_energy_matrix
    if nunsampled > 0:
        fully_interacting_u_ln = unsampled_energy_matrix[:, 0, :]
        noninteracting_u_ln = unsampled_energy_matrix[:, 1, :]
        # Augment u_kln to accept the new state
        new_energy_matrix = np.zeros([nstates + 2, nstates + 2, N], np.float64)
        N_k_new = np.zeros(nstates + 2, np.int32)
        # Insert energies
        new_energy_matrix[1:-1, 0, :] = fully_interacting_u_ln
        new_energy_matrix[1:-1, -1, :] = noninteracting_u_ln
        # Fill in other energies
        new_energy_matrix[1:-1, 1:-1, :] = sampled_energy_matrix
        N_k_new[1:-1] = N_k
        # Notify users
        # Reset values, last step in case something went wrong so we don't overwrite u_kln on accident
        mbar_ready_energy_matrix = new_energy_matrix
        N_k = N_k_new
    return mbar_ready_energy_matrix, N_k


# Create the data holders
index = sys.argv[2]
solvent = sys.argv[1]
source_directory = "../{1}licit-all/experiments/cmethingesinglehinge{0}/".format(index, solvent)

analysis_script_path = os.path.join(source_directory, 'analysis.yaml')
with open(analysis_script_path, 'r') as f:
    analysis = yaml.load(f)
phases = dict()
max_analysis_iteration = np.inf
phase_names = [phase_name for phase_name, _ in analysis]
# Populate placeholders
for phase_name, sign in analysis:
    phase_path = os.path.join(source_directory, phase_name + '.nc')
    print("Loading {} analyzer".format(phase_name))
    analyzer = analyze.get_analyzer(phase_path)
    phases[phase_name] = {}
    phases[phase_name]['sign'] = sign
    phases[phase_name]['analyzer'] = analyzer
    # phases[phase_name]['kT'] = analyzer.kT  # This is slow
    phases[phase_name]['kT'] = kT
    print("Loading {} energy".format(phase_name))
    kln, un_kln = analyzer.get_states_energies()
    if kln.shape[-1] < max_analysis_iteration:
        max_analysis_iteration = kln.shape[-1]
    phases[phase_name]['energy'] = kln
    phases[phase_name]['unsampled'] = un_kln
    phases[phase_name]['standard_state'] = analyzer.get_standard_state_correction()
    phases[phase_name]['f_k'] = np.zeros(kln.shape[1] + un_kln.shape[1])
# Now do free energy
x_values = np.arange(1, max_analysis_iteration, step=spacing, dtype=int)
if max_analysis_iteration not in x_values:
    x_values = np.append(x_values, max_analysis_iteration)
nx = x_values.size
free_energy = np.zeros([nx, 2], dtype=float)
for idx, n in enumerate(x_values):
    print("Working on Iteration {}/{} of spacing {}".format(n, max_analysis_iteration, spacing))
    fe = 0.0
    dfe = 0.0
    for phase_name in phase_names:
        phase = phases[phase_name]
        analyzer = phase['analyzer']
        kln = phase['energy'][:, :, :n]
        unsampled = phase['unsampled'][:, :, :n]
        u_n = analyzer.get_timeseries(kln)
        # Discard equilibration samples.
        number_equilibrated, g_t, Neff_max = analyze.get_equilibration_data(u_n)
        kln = analyze.remove_unequilibrated_data(kln, number_equilibrated, -1)
        unsampled = analyze.remove_unequilibrated_data(unsampled, number_equilibrated, -1)
        u_kln = analyze.subsample_data_along_axis(kln, g_t, -1)
        unsampled_u_kln = analyze.subsample_data_along_axis(unsampled, g_t, -1)
        mbar_ukln, mbar_N_k = prepare_mbar_input_data(u_kln, unsampled_u_kln)
        f_k = phase['f_k']
        mbar = analyze.MBAR(mbar_ukln, mbar_N_k, initial_f_k=f_k)
        phase['f_k'] = mbar.f_k
        fe_data = mbar.getFreeEnergyDifferences(compute_uncertainty=True, return_theta=False)
        try:
            phase_fes, phase_dfes = fe_data
        except ValueError:
            phase_fes, phase_dfes, _ = fe_data
        i, j = analyzer.reference_states
        phase_fe = phase_fes[i, j]
        phase_dfe = phase_dfes[i, j]
        fe -= phase['sign'] * (phase_fe + phase['standard_state']) * phase['kT']
        dfe += (phase_dfe * phase['kT'])**2
    free_energy[idx, :] = fe, dfe
free_energy[:, 1] = np.sqrt(free_energy[:, 1])

np.savez('{0}licit/{0}licit{1}_fe_by_iteration.npz'.format(solvent, index), free_energy=free_energy, x=x_values)
