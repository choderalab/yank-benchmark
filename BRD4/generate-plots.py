#!/bin/env python

import matplotlib
matplotlib.use('agg')
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pylab as plt
import seaborn as sns
import numpy as np
import os
from netCDF4 import Dataset

#from yank.multistate import MultiStateReporter

def generate_plots(prefix):
    filename = '%s/experiments/%s/complex.nc' % (experiment, prefix)
    print(filename)
    if not os.path.exists(filename):
        return
    with Dataset(filename, 'r') as ncfile:
        logZ = np.array(ncfile.groups['online_analysis'].variables['logZ_history'])
        logZ = logZ[:-1,:]
        n_iterations, n_states = logZ.shape
        print(n_iterations, n_states)

        states = ncfile.variables['states']

        gamma = ncfile.groups['online_analysis'].variables['gamma_history']

        pdf_filename = '%s/analysis/%s.pdf' % (experiment, prefix)
        with PdfPages(pdf_filename) as pdf:
            fig = plt.figure(figsize=(10,5));
            plt.plot(logZ[:,:],'-')
            plt.xlabel('iteration');
            plt.ylabel('logZ / kT');
            pdf.savefig()  # saves the current figure into a pdf page
            plt.close()

            fig = plt.figure(figsize=(10,5));
            plt.plot(logZ[:,0] - logZ[:,-1],'.');
            plt.xlabel('iteration');
            plt.ylabel('$\Delta G_\mathrm{complex}$ / kT');
            pdf.savefig()  # saves the current figure into a pdf page
            plt.close()

            fig = plt.figure(figsize=(10,5));
            plt.plot(states,'.');
            plt.xlabel('iteration');
            plt.ylabel('thermodynamic state');
            plt.axis([0, n_iterations, 0, n_states]);
            pdf.savefig()  # saves the current figure into a pdf page
            plt.close()

            fig = plt.figure(figsize=(10,5));
            plt.plot(gamma,'.');
            plt.xlabel('iteration');
            plt.ylabel('gamma');
            pdf.savefig()  # saves the current figure into a pdf page
            plt.close()


#experiment = 'sams-twostage-harmonic-dense'
#experiment = 'sams-twostage-harmonic-auto'
#experiment = 'sams-twostage-rmsd-dense'
#experiment = 'sams-twostage-rmsd-mcligand-dense'
experiment = 'sams-twostage-boresch-dense'

prefix = 'BRD4complexligands'

for index in range(12):
    generate_plots('%s%d' % (prefix, index))

