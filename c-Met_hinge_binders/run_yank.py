#!/usr/local/bin/env python

"""
Run YANK with two restraints and starting in the noninteracting state.

The script is still in a prototype phase. We use two restraints: a harmonic
restraint that is always on and a orientational restraint that we activate
while we turn off the sterics.

Moreover, we force the SAMSSampler to start in the noninteracting state (i.e.,
the last one) to work around eventual clashes in the initial docked structure.

Notes
-----
The script assumes

"""

# =============================================================================================
# GLOBAL IMPORTS
# =============================================================================================

import copy

from simtk import openmm, unit

from yank.experiment import AlchemicalPhaseFactory, ExperimentBuilder
from yank.restraints import RMSD


# ==============================================================================
# SUPPORTING CLASS
# ==============================================================================

class TwoRestraintsPhaseFactory(AlchemicalPhaseFactory):
    """Create alchemical phases with two restraints and starting in the noninteracting state."""

    def __init__(self, alchemical_phase_factory):
        # Copy all attributes.
        self.__dict__ = copy.copy(alchemical_phase_factory.__dict__)

    def create_alchemical_phase(self):
        """Override parent method to add a second restraint and set initial thermodynamic state."""
        # Add a second RMSD restraint if this is the complex phase.
        if self.restraint is not None:
            self._add_rmsd_restraint()

        # Create the alchemical phase.
        alchemical_phase = super(TwoRestraintsPhaseFactory, self).create_alchemical_phase()

        # Set initial thermodynamic state to last one if using SAMS
        if (alchemical_phase._sampler.n_replicas == 1):
            alchemical_phase._sampler._replica_thermodynamic_states[0] = alchemical_phase._sampler.n_states - 1

        return alchemical_phase

    def initialize_alchemical_phase(self):
        """Override parent method to skip the fully interacting state minimization."""
        # Turn off general minimization.
        minimize = self.options['minimize']
        if minimize is True:
            # This hack is not compatible if we also want to randomize
            # the ligand or equilibrate after minimization.
            # DEBUG for repex auto
            #assert self.options['randomize_ligand'] is False
            #assert self.options['number_of_equilibration_iterations'] <= 0
            self.options['number_of_equilibration_iterations'] = 0
            self.options['minimize'] = False

        # Run usual method without minimization.
        alchemical_phase = super(TwoRestraintsPhaseFactory, self).initialize_alchemical_phase()

        # Skip fully interacting state minimization and minimize replicas.
        if minimize:
            tolerance = self.options['minimize_tolerance']
            max_iterations = self.options['minimize_max_iterations']
            alchemical_phase._sampler.minimize(tolerance=tolerance, max_iterations=max_iterations)

        return alchemical_phase

    def _add_rmsd_restraint(self):
        """Add a RMSD restraint to the reference ThermodynamicState.

        The restraint is controlled by lambda_restraints * (1 - lambda_restraints)
        so that it turns on only in the middle of the protocol when lambda_restraints
        goes from 0.0 to 1.0.
        """
        # Add RMSD restraint force on top of the YAML-specified restraint.
        ligand_dsl = '(element C)'
        receptor_dsl = '(resname ALA) and (name CA)'
        rmsd_restraint = RMSD(restrained_receptor_atoms=receptor_dsl, restrained_ligand_atoms=ligand_dsl, RMSD0=0.0*unit.angstroms, K_RMSD=0.6*unit.kilocalories_per_mole/unit.angstrom**2)

        # Determine automatically the parameters.
        rmsd_restraint.determine_missing_parameters(self.thermodynamic_state, self.sampler_states,
                                                    self.topography)
        rmsd_restraint.restrain_state(self.thermodynamic_state)

        # Isolate restraint Force object.
        system = self.thermodynamic_state.system
        for restraint_force in system.getForces():
            if isinstance(restraint_force, openmm.CustomCVForce):
                break

        # Modify the restraint force to be on only in the middle of the protocol.
        energy_function = restraint_force.getEnergyFunction().replace('lambda_restraints',
                                                                      '4 * 4 * lambda_restraints * (1 - lambda_restraints)')
        restraint_force.setEnergyFunction(energy_function)

        # Update reference thermodynamic state with the new definition of the force.
        self.thermodynamic_state.system = system


class TwoRestraintsBuilder(ExperimentBuilder):
    """Experiment builder using TwoRestraintsPhaseFactory instead of AlchemicalPhaseFactory."""

    def _build_experiment(self, *args, **kwargs):
        """Prepare a single experiment.

        Override parent method to build an experiment composed of two
        TwoRestraintsPhaseFactories instead of AlchemicalPhaseFactories.

        Returns
        -------
        yaml_experiment : Experiment
            A Experiment object.

        """
        experiment = super(TwoRestraintsBuilder, self)._build_experiment(*args, **kwargs)
        # Convert AlchemicalPhaseFactories to TwoRestraintsPhaseFactories.
        for phase_idx, phase in enumerate(experiment.phases):
            # Check if we're resuming or not before converting.
            if isinstance(phase, AlchemicalPhaseFactory):
                experiment.phases[phase_idx] = TwoRestraintsPhaseFactory(phase)
        return experiment


# ==============================================================================
# MAIN
# ==============================================================================

def main(yaml_script_path, job_id, n_jobs):
    experiment_builder = TwoRestraintsBuilder(yaml_script_path, job_id, n_jobs)
    experiment_builder.run_experiments()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run YANK with two restraints and starting from the decoupled state.')
    parser.add_argument('-y', '--yaml', type=str, dest='yaml_script_path',
                        help='Path to the YAML script specifying options and/or how to set up and run the experiment.')
    parser.add_argument('--jobid', type=int, dest='job_id', default=None, help='Identifier for the job: 1 <= jobid <= njobs.')
    parser.add_argument('--njobs', type=int, dest='n_jobs', default=None, help='Total number of parallel executions.')

    args = parser.parse_args()
    main(args.yaml_script_path, args.job_id, args.n_jobs)
