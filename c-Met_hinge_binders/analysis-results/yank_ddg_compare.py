import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import copy

# Load data from the stored numpy file
data = np.load('free_energy_data.npz')
exp = data['experimental']
fepp = data['fepplus']
yank_explicit_fe = data['yank_explicit_fe']
yank_explicit_error = data['yank_explicit_error']
yank_implicit_fe = data['yank_implicit_fe']
yank_implicit_error = data['yank_implicit_error']

#Count number of ligands
nligands = len(exp)


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
ynames =  ['YANK implicit',     'YANK explicit',     'FEP+',             'YANK implicit',     'YANK explicit']
xnames =  ['experimental',      'experimental',      'experimental',     'FEP+',              'FEP+']
ydatas =  [yank_implicit_fe,    yank_explicit_fe,    fepp,               yank_implicit_fe,    yank_explicit_fe]
yerrors = [yank_implicit_error, yank_explicit_error, np.zeros(nligands), yank_implicit_error, yank_explicit_error]
xdatas =  [exp,                 exp,                 exp,                fepp,                fepp]
nplots = len(xdatas)

# Populate blank data holders
all_data = np.array([])
rmses_x = [None] * nplots
rmses_y = [None] * nplots

# Set figure color base, scalar base, row and column count.
sns.set()
sbn_colors = sns.color_palette("hls", nligands)
base_size = 4
nrows = 2
ncols = 3
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
# 2nd pass for formatting
# Establish min/max limits on graph
min_max = np.array([min(all_data)-.5, max(all_data)+0.5])
for index in range(nplots):
    axes = a.flatten()[index]
    rmse_x = rmses_x[index]
    rmse_y = rmses_y[index]
    xname = copy.deepcopy(xnames[index])
    yname = copy.deepcopy(ynames[index])
    # Plot the y=x line
    axes.plot(min_max, min_max, lw=1, c='k', zorder=30)
    # Set the limits and aspect ratio
    axes.set_xlim(min_max)
    axes.set_ylim(min_max)
    axes.set_aspect('equal', 'box')
    # Add labels
    axes.set_xlabel(r"$\Delta\Delta G$ {} (kcal/mol)".format(xname))
    axes.set_ylabel(r"$\Delta\Delta G$ {} (kcal/mol)".format(yname))
    title_text = []
    for name, fn in da_set:
        # Calculate RMSE or MUE, relation Y=X+0 == Y=X
        local = fn(rmse_x, rmse_y, 0)
        # Calculate CI
        ci_min, ci_max = boostrap_fn(rmse_x, rmse_y, 0, fn)
        title_text.append("{3}: {0:3.2f} [{1:3.2f}, {2:3.2f}] kcal/mol".format(local, ci_min, ci_max, name))
    axes.annotate('\n'.join(title_text),
                  xy=(0.5, 1.08),
                  xycoords='axes fraction',
                  rotation=0,
                  ha='center', va='center')
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
f.savefig("ddg_hinge_vs_fepp_exper.png", bbox_inches='tight')
f.savefig("ddg_hinge_vs_fepp_exper.pdf", bbox_inches='tight')
# plt.show()
