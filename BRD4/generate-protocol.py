#!/bin/env python

"""
Generate protocol for RMSD-based annihilation

"""

import numpy as np
from collections import OrderedDict

nelectrostatics = 80
nsterics = 80
nrestraints = nsterics + nelectrostatics
nlambda = nrestraints

lambdas = OrderedDict()
lambdas['lambda_restraints'] = np.append(np.linspace(0.0, 0.0, nelectrostatics), np.linspace(0.0, 1.0, nsterics+1))
lambdas['lambda_electrostatics'] = np.append(np.linspace(1.0, 0.0, nelectrostatics), np.linspace(0.0, 0.0, nsterics+1))
lambdas['lambda_sterics'] = np.append(np.linspace(1.0, 1.0, nelectrostatics), np.linspace(1.0, 0.0, nsterics+1))

for name in lambdas:
    s = '%32s: [' % name
    for i, val in enumerate(lambdas[name]):
        if i > 0: s += ', '
        s += '%5.3f' % val
    s += ']'
    print(s)
