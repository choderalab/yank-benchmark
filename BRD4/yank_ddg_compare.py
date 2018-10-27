import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import copy
import pickle
from simtk import unit

import openeye.oechem as oechem
from openeye import oedepict

# The input_file is the order in which the molecules are indexed
# So it is used as the main indexing sequence.
input_file = 'input/ligands_am1-bcc_DGfromIC50.sdf'

# Count molecules
input_ifs = oechem.oemolistream(input_file)
nligands = 0
for index, mol in enumerate(input_ifs.GetOEGraphMols()):
    nligands += 1
input_ifs.close()


# Loop through all molecules in order
exp_fe = np.zeros([nligands], np.float64)
fepplus_fe = np.zeros([nligands], np.float64)
fepplus_error = np.zeros([nligands], np.float64)
input_ifs = oechem.oemolistream(input_file)
for index, mol in enumerate(input_ifs.GetOEGraphMols()):
    exp_string = oechem.OEGetSDData(mol, 'Calc DG')
    if exp_string[0] == '>':
        exp_fe[index] = 0.0
    else:
        exp_fe[index] = float(exp_string) 
    fepplus_fe[index] = 0.0
    fepplus_error[index] = 0.0
input_ifs.close()
print(exp_fe)
print(fepplus_fe)
print(fepplus_error)

# Count number of ligands
nligands = len(exp_fe)

# Load data from analysis pickle
analysis_filename = 'analysis-BRD4-sams-2.pkl'
with open(analysis_filename, 'rb') as f:
    data = pickle.load(f)
print(data.keys())
#prefix = 'Harmonic_cmethingesinglehinge'
#prefix = 'cmethingesinglehinge'
prefix = 'BRD4complexligands'
#prefix = 'PeriodicTorsionBoresch_cmethingesinglehinge'
yank_explicit_fe = np.zeros([nligands], np.float64)
yank_explicit_error = np.zeros([nligands], np.float64)
yank_implicit_fe = None
yank_implicit_error = None
energy_unit = unit.kilocalories_per_mole
for index in range(nligands):
    name = '%s%d' % (prefix, index)
    try:
        yank_explicit_fe[index] = data[name]['free_energy']['free_energy_diff_unit'] / energy_unit
        yank_explicit_error[index] = data[name]['free_energy']['free_energy_diff_error_unit'] / energy_unit
    except Exception as e:
        print('%s : %s' % (name, str(e)))

def fit(x, y):
    # Find Y = X + B function (shift the y=x line, not used for DDG)
    return np.mean(y - 1*x)


def rmse(x, y, b):
    # RMSE evaluation of an expected X and measured Y with the desired relation Y = X + B curve
    f = 1*x + b
    rmse = np.sqrt(np.mean((f-y)**2))
    return rmse


def mue(x, y, b):
    # Mean Unsigned Error, see RMSE for args
    f = 1*x + b
    return np.mean(np.abs(f-y))


def ci(xtrace, width=0.95):
    """
    Compute confidence interval
    """
    x = np.array(xtrace)
    x.sort()
    n = len(xtrace)
    low = int(n * (1-width)/2.0)
    high = int(n * (1 - (1-width)/2.0))
    return x[low], x[high]


def boostrap_fn(x, y, b, function=rmse, nreplicates=1000):
    replicate_rmse = np.zeros([nreplicates])
    n_data = len(x)
    assert len(x) == len(y)
    for replicate in range(nreplicates):
        # sample with replacement
        bootstrap_indices = np.random.choice(range(n_data), n_data)
        # compute statistics on this sample
        replicate_rmse[replicate] = function(x[bootstrap_indices], y[bootstrap_indices], b)
    # report 95% CI
    xlow, xhigh = ci(replicate_rmse)
    return xlow, xhigh


def equalize_ticks(axes, small_ax):
    # Plotting helper function to set the tick labels to be identical relative to which small_ax(es) is provided
    if small_ax == "x":
        large_ax = "y"
    else:
        large_ax = "x"
    small_ticks = getattr(axes, "get_{}ticks".format(small_ax))()
    lims = getattr(axes, "get_{}lim".format(small_ax))()
    real_ticks = np.array([
        tick for tick in small_ticks if lims[0] <= tick <= lims[1]
    ])
    getattr(axes, "set_{}ticks".format(large_ax))(real_ticks)


# Flatten names, X data, and Y data to loop over for plotting
ynames =  ['YANK explicit',     'YANK explicit',     'FEP+',             'FEP+',              'YANK explicit',     'YANK explicit']
xnames =  ['experimental',      'experimental',      'experimental',     'experimental',      'FEP+',              'FEP+']
ydatas =  [yank_explicit_fe,    yank_explicit_fe,    fepplus_fe,         fepplus_fe,          yank_explicit_fe,    yank_explicit_fe]
yerrors = [yank_explicit_error, yank_explicit_error, fepplus_error,      fepplus_error,       yank_explicit_error, yank_explicit_error]
xdatas =  [exp_fe,              exp_fe,              exp_fe,             exp_fe,             fepplus_fe,          fepplus_fe]
types  =  ['DG',                'DDG',               'DG',               'DDG' ,             'DG',                'DDG']
nplots = len(xdatas)

# Populate blank data holders
all_data = np.array([])
rmses_x = [None] * nplots
rmses_y = [None] * nplots

# Set figure color base, scalar base, row and column count.
sns.set()
sbn_colors = sns.color_palette("hls", nligands)
base_size = 4
nrows = 3
ncols = 2
da_set = [('RMSE', rmse), ('MUE', mue)]

f, a = plt.subplots(nrows, ncols, figsize=(base_size*ncols, base_size*nrows))
# First pass: plot data
for index in range(nplots):
    axes = a.flatten()[index]  # Get plot we are working with
    # Copy data so modifications dont change original
    xname = copy.deepcopy(xnames[index])
    xdata = copy.deepcopy(xdatas[index])
    yname = copy.deepcopy(ynames[index])
    ydata = copy.deepcopy(ydatas[index])
    yerror = copy.deepcopy(yerrors[index])
    plottype = types[index]

    if plottype == 'DDG':
        # Empty place holder
        rmse_x = np.array([])
        rmse_y = np.array([])
        # Loop through each relative ligand
        for ref_id in range(nligands):
            color = sbn_colors[ref_id]
            # Shift data local to the reference ligand
            xlocal = np.delete(xdata - xdata[ref_id], ref_id)
            ylocal = np.delete(ydata - ydata[ref_id], ref_id)
            yerror_local = np.delete(np.sqrt(yerror**2 + yerror[ref_id]**2), ref_id)
            # Plot the scatter
            axes.scatter(xlocal, ylocal, marker='o', edgecolors='k',
                         c=color, zorder=20)
            # Plot the error bars under the scatter
            # Cant use marker here because less control on the marker colors
            axes.errorbar(xlocal, ylocal, yerr=2*yerror_local, ecolor=color,
                          elinewidth=0, mec='none', mew=0, linestyle='None',
                          zorder=10)
            # Add all data together for min/max determination, redundancy does no harm her
            all_data = np.concatenate((all_data, xlocal, ylocal))
            # Combine all data for this plot to be analyzed for RMSE/MUE later
            rmse_x = np.concatenate((rmse_x, xlocal))
            rmse_y = np.concatenate((rmse_y, ylocal))
            # Store combined data from this plot for 2nd pass
            rmses_x[index] = rmse_x
            rmses_y[index] = rmse_y
    elif plottype == 'DG':        
        # Plot the scatter
        color = sbn_colors
        axes.scatter(xdata, ydata, marker='o', edgecolors='k',
                         c=color, zorder=20)
        for i in range(nligands):
            axes.text(xdata[i], ydata[i], '%d' % i) # DEBUG
        # Plot the error bars under the scatter
        # Cant use marker here because less control on the marker colors
        axes.errorbar(xdata, ydata, yerr=2*yerror, ecolor=color,
                          elinewidth=0, mec='none', mew=0, linestyle='None',
                          zorder=10)

# 2nd pass for formatting
# Establish min/max limits on graph
min_max = np.array([min(all_data)-.5, max(all_data)+0.5])
min_max = np.array([-25, +25]) # DEBUG
#min_max = np.array([-17, -5]) # DEBUG ZOOM

for index in range(nplots):
    axes = a.flatten()[index]
    rmse_x = rmses_x[index]
    rmse_y = rmses_y[index]
    xname = copy.deepcopy(xnames[index])
    yname = copy.deepcopy(ynames[index])
    plottype = types[index]

    # Plot the y=x line
    axes.plot(min_max, min_max, lw=1, c='k', zorder=30)
    # Set the limits and aspect ratio
    axes.set_xlim(min_max)
    axes.set_ylim(min_max)
    axes.set_aspect('equal', 'box')
    # Add labels
    if plottype == 'DDG':
        axes.set_xlabel(r"$\Delta\Delta G$ {} (kcal/mol)".format(xname))
        axes.set_ylabel(r"$\Delta\Delta G$ {} (kcal/mol)".format(yname))
        title_text = []
        for name, fn in da_set:
            # Calculate RMSE or MUE, relation Y=X+0 == Y=X
            local = fn(rmse_x, rmse_y, 0)
            # Calculate CI
            ci_min, ci_max = boostrap_fn(rmse_x, rmse_y, 0, fn)
            title_text.append("{3}: {0:3.2f} [{1:3.2f}, {2:3.2f}] kcal/mol".format(local, ci_min, ci_max, name))
            axes.annotate('\n\n'.join(title_text),
                          xy=(0.5, 1.08),
                          xycoords='axes fraction',
                          rotation=0,
                          ha='center', va='center', fontsize=6)

    elif plottype == 'DG':
        axes.set_xlabel(r"$\Delta G$ {} (kcal/mol)".format(xname))
        axes.set_ylabel(r"$\Delta G$ {} (kcal/mol)".format(yname))

    # Equalize ticks
    xticks = axes.get_xticks()
    yticks = axes.get_yticks()
    if len(xticks) < len(yticks):
        equalize_ticks(axes, 'x')
    else:
        equalize_ticks(axes, 'y')
# Delete unused plots
for index in range(nplots, a.size):
    f.delaxes(a.flatten()[index])
# Adjust spacing
f.subplots_adjust(hspace=0.00, wspace=0.4, top=0.99, bottom=0.05, left=0.1, right=0.95)
txt = r"$\Delta\Delta G$ relative to first molecule" + "\nwhich is also on 0,0" + "\n\n"
txt += "$\Delta\Delta G$ is taken separately on each axis\n" \
       "e.g. Experiment is relative to Experiment,\n   and FEP+ is relative to FEP+\n\n"
txt += "Dot color between figures is the same\nreference molecule"
# f.text((ncols*3-3)/(ncols*3), (1)/(nrows*2), txt, wrap=True,)
f.savefig("BRD4-yank.png", bbox_inches='tight')
f.savefig("BRD4-yank.pdf", bbox_inches='tight')
# plt.show()
