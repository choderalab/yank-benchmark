#!/bin/env python

"""
Generate protocol for RMSD-based annihilation

"""

import numpy as np
from collections import OrderedDict

nelectrostatics = 80
nsterics = 80
nrestraints = 20

lambdas = OrderedDict()
lambdas['lambda_restraints'] = np.concatenate((np.linspace(0.0, 0.5, nrestraints), np.linspace(0.5, 0.5, nelectrostatics), np.linspace(0.5, 0.5, nsterics), np.linspace(0.5, 1.0, nrestraints+1)))
lambdas['lambda_electrostatics'] = np.concatenate((np.linspace(1.0, 1.0, nrestraints), np.linspace(1.0, 0.0, nelectrostatics), np.linspace(0.0, 0.0, nsterics), np.linspace(0.0, 0.0, nrestraints+1)))
lambdas['lambda_sterics'] = np.concatenate((np.linspace(1.0, 1.0, nrestraints), np.linspace(1.0, 1.0, nelectrostatics), np.linspace(1.0, 0.0, nsterics), np.linspace(0.0, 0.0, nrestraints+1)))

for name in lambdas:
    s = '%32s: [' % name
    for i, val in enumerate(lambdas[name]):
        if i > 0: s += ', '
        s += '%5.3f' % val
    s += ']'
    print(s)
