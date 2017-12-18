import matplotlib.pyplot as plt
import yaml
import numpy as np
from yank.experiment import YankLoader
import os.path as path

base_name = 'cmethingesinglehinge'
count = 12
names = ['complex', 'solvent']
solvs = ['explicit', 'implicit']

for solv in solvs:
    base_path = path.join('{}-all'.format(solv), 'experiments', base_name)
    for name in names:
        the_fig, (the_plot_percent, the_plot_index) = plt.subplots(2, 1, figsize=(8, 8))
        maxx = 0
        for i in range(count):
            with open(path.join(base_path + str(i), base_name + str(i) + '.yaml'), 'r') as f:
                yaml_load = yaml.load(f.read(), Loader=YankLoader)
            path_yaml = yaml_load['protocols']['absolute-binding'][name]['alchemical_path']
            electro_path = np.array(path_yaml['lambda_electrostatics'][::-1])
            electro_path_min = np.where(electro_path > 0)[0].min()  # Find last index of electro path
            electro_path = electro_path[electro_path_min:]
            sterics_path = np.array(path_yaml['lambda_sterics'][::-1])
            sterics_path = sterics_path[:electro_path_min]
            n_electro = len(electro_path)
            n_sterics = len(sterics_path)
            ntot = n_electro + n_sterics
            state_indices = range(ntot)
            xpercent = np.array(state_indices)/float(ntot-1)
            y = np.concatenate((sterics_path, electro_path+1))
            the_plot_percent.plot(xpercent, y, lw=0.5)
            the_plot_index.plot(state_indices, y, lw=0.5)
            if ntot > maxx:
                maxx = ntot
        for plot in [the_plot_percent, the_plot_index]:
            plot.axhline(y=1, xmin=0, xmax=1, c='k')
            plot.set_ylim([0, 2])
            nlabels = 11
            plot.set_yticks(np.linspace(0, 2, 11))
            ylabels_float = np.linspace(0, 1, 6)
            # ylabels = np.array(['{0:3.2f}'.format(lab) for lab in ylabels_float], dtype=str)
            # ylabels = np.concatenate((ylabels, ylabels[1:]))
            ylabels = ['{0:3.2f}'.format(lab) for lab in ylabels_float]
            ylabels.extend(ylabels[1:])
            ylabels[5] = '0.00\n1.00'
            plot.set_yticklabels(ylabels)
            #plot.text(0.02, 0.33, 'Sterics', fontsize=14, rotation='vertical', transform=plot.transAxes)
            #plot.text(0.02, 0.66, 'Electro.', fontsize=14, rotation='vertical')
            plot.set_ylabel("Sterics            Electro.", fontsize=14)
        the_plot_percent.set_xlim([0, 1])
        the_plot_percent.set_xlabel('% of transform\n(state_index/n_states)')
        the_plot_index.set_xlim([0, maxx - 1])
        the_plot_index.set_xlabel('index of the state')
    
        # the_fig.text(0.02, 0.33, 'Sterics', fontsize=14, rotation='vertical')
        # the_fig.text(0.02, 0.75, 'Electro.', fontsize=14, rotation='vertical')
        the_fig.suptitle('{} Path for each molecule, {}'.format(name.title(), solv.title()))
        the_fig.subplots_adjust(hspace=0.25, top=0.95, bottom=0.05, right=0.95)
    
        the_fig.savefig(name + '_' + solv + '_paths.png', bbox_inches='tight')

plt.show()
