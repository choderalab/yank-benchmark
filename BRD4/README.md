# BRD4 public dataset from GSK

This dataset is courtesy of Eric Arnoult (GSK).
Input files were prepared by Ian Wall, and modified by Eric Arnoult for AMBER.

## Reference

This dataset comes from the [paper](http://doi.org/10.1021/acs.jctc.6b00794):
```
Wan S, Bhati AP, Zasada SJ, Wall I, Green D, Bamborough P, and Coveney PV
Rapid and Reliable Binding Affinity Prediction of Bromodomain Inhibitors: A Computational Study
JCTC 13:784, 2017
DOI: 10.1021/acs.jctc.6b00794
```
Experimental data is summarized in Table 1.

## Manifest

* `input/` - PDB structure and ligands
* `run-lsf-sams-twostage-boresch-dense.sh` - LSF batch script for SAMS with dense protocol and Boresch restraint
* `sams-twostage-boresch-dense.yaml` - SAMS with dense protocol and Boresch restraint
* `run-lsf-sams-twostage-harmonic-dense.sh` - LSF batch script for SAMS with dense protocol and harmonic restraint
* `sams-twostage-harmonic-dense.yaml` - SAMS with dense protocol and harmonic restraint
* `run-lsf-repex-twostage-harmonic-auto.sh` - LSF batch script for repex with thermodynamic path trailblazing and harmonic restraint
* `repex-twostage-harmonic-auto.yaml` - replica-exchange with thermodynamic path trailblazing and harmonic restraint
