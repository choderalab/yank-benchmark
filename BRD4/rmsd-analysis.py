import numpy as np
# import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import interpolate
import os, sys

source_directory = sys.argv[1]
experiments_directory = os.path.join(source_directory, 'experiments')
analysis_directory = os.path.join(source_directory, 'analysis')

def moving_average(a, n=20):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def smooth(x, y):
    N = y.size
    tck = interpolate.splrep(x, y, k=5, s=N * 1E7)
    smoothed = interpolate.splev(x, tck, der=0)
    return smoothed




# Set figure color base, scalar base, row and column count.
sns.set()
sbn_colors = sns.color_palette("hls", nmax)
base_size = 4
nrows = nmax
ncols = nmode
plot_min = 0
plot_max = 0

nrows = 0
ncols = 0
for experiment_set_directory in os.listdir(experiments_directory):
     path = os.path.join(experiments_directory, experiment_set_directory)
     ligands = os.listdir(path)
     nligands = len(ligands)
     ncols = 2
     nrows = int(nligands / 2.0 + 0.5)
     
     f, a = plt.subplots(nrows, ncols, figsize=(base_size*ncols, base_size*nrows/3))
     g, b = plt.subplots(1, ncols, figsize=(base_size*ncols, base_size*1))
for index, mode in enumerate(modes):
    q = b[index]
    nligand = ns[index]
    lig = 0
    for lig in range(nligand):
        p = a[lig, index]
        if lig == 0:
            p.set_title("{}".format(mode).title())
        c = sbn_colors[lig]
        data = np.load("analysis-results-{0}/rmsds/rmsd-{0}-{1}.npz".format(mode, lig))
        rmsd_r = data['receptor']
        rmsd_l = data['ligand']
        ma_l = moving_average(rmsd_l*10)
        ma_r = moving_average(rmsd_r*10)
        x = np.arange(rmsd_l.size)
        mx = np.arange(ma_l.size)
        #p.plot(x, rmsd_l, linestyle='-', color=c)
        #p.plot(x, rmsd_r, linestyle='--', color=c)
        p.plot(mx, ma_l, linestyle='-', color='k')
        p.plot(mx, ma_r, linestyle='-', color='b')
        q.plot(x, smooth(x, rmsd_l*10), linestyle='-', color=c)
        q.plot(x, smooth(x, rmsd_r*10), linestyle='--', color=c)
        p.set_xlabel("Iteration x 10")
        p.set_ylabel("RMSD (A)")
        xlim = p.get_xlim()
        p.set_xlim([0, xlim[-1]])
        ylim = p.get_ylim()
        plot_max = max(max(ylim), plot_max)
        print("{}.{} - Mean: {}  -- Max: {}".format(mode, lig, rmsd_l.mean(), rmsd_l.max()))
    if lig < nmax - 1:
        # Delete unused plots
        for d in range(nmax - 1, lig, -1):
            f.delaxes(a[d, index])
    q.set_xlabel("Iteration")
    q.set_ylabel("RMSD (A)")
    xlim = q.get_xlim()
    q.set_xlim([0, xlim[-1]])
    q.set_title("{}".format(mode).title())

for z in [a, b]:
    for plot in z.flatten():
        plot.set_ylim([plot_min, plot_max])

f.subplots_adjust(top=.97, wspace=0.25, hspace=0.25)
# Create decoys
curves = [plt.Line2D((0,1), (0,1), linestyle='-', color='k'), plt.Line2D((0,1), (0,1), linestyle='--', color='k')]
curves_split = [plt.Line2D((0,1), (0,1), linestyle='-', color='k'), plt.Line2D((0,1), (0,1), linestyle='-', color='b')]
labels = ["Ligand", "Receptor"]
f.legend(curves_split, labels)
g.legend(curves, labels)
g.subplots_adjust(wspace=0.25)
g.savefig("RMSD_stacked.pdf")
f.savefig("RMSD_by_system.pdf")
# plt.show()
