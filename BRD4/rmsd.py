import yank.analyze as an
import numpy as np
import mdtraj as md 
import openmmtools as mmtools
import sys, os

source_directory = sys.argv[1]
experiments_directory = os.path.join(source_directory, 'experiments')
analysis_directory = os.path.join(source_directory, 'analysis')

for experiment_set_directory in os.listdir(experiments_directory):
    for experiment_directory in os.listdir(os.path.join(experiments_directory, experiment_set_directory)):
        complex_phase = os.path.join(experiments_directory, experiment_set_directory, experiment_directory, "complex.nc")
        print(complex_phase)
        print("Extracting Trajectory")
        reporter = an.multistate.MultiStateReporter(complex_phase)
        reporter.open()
        n_iterations = reporter.read_last_iteration()
        checkpoint = reporter.checkpoint_interval
        ncp = np.floor(n_iterations/checkpoint).astype(int)
        last_iter = int(ncp*checkpoint)
        tr = an.extract_trajectory(complex_phase, keep_solvent=False, replica_index=0, end_frame=last_iter-1, skip_frame=10)
        dummy_sampler_states = reporter.read_sampler_states(0, analysis_particles_only=True)
        n_atoms, n_dim = dummy_sampler_states[0].positions.shape
        n_iterations = reporter.read_last_iteration()
        print("Reading Metadata")
        metadata = reporter.read_dict('metadata')
        print("Deserializing Topology")
        top = mmtools.utils.deserialize(metadata['topography'])
        print("Calculating RMSD")
        ligand = top.select(" mass >= 1.5 and name != 'Cl-' and name != 'Na+'", subset=top.ligand_atoms)
        receptor = top.select(" mass >= 1.5 and name != 'Cl-' and name != 'Na+'", subset=top.receptor_atoms)
        backbone = top.select(" backbone", subset=top.receptor_atoms)
        tr.superpose(tr, atom_indices=backbone)
        rmsd_l = np.sqrt(3*np.mean((tr.xyz[:, ligand, :] - tr.xyz[0, ligand, :])**2, axis=(1,2)))
        rmsd_r = np.sqrt(3*np.mean((tr.xyz[:, receptor, :] - tr.xyz[0, receptor, :])**2, axis=(1,2)))
        reporter.close()

        # Write analysis file
        outdir = os.path.join(analysis_directory, experiment_set_directory)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        npz_filename = os.path.join(outdir, experiment_directory + '.npz')
        np.savez(npz_filename, ligand=rmsd_l, receptor=rmsd_r)
