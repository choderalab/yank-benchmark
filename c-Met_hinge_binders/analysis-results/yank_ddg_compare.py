import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import copy

data = np.load('free_energy_data.npz')
exp = data['experimental']
fepp = data['fepplus']
yank_explicit_fe = data['yank_explicit_fe']
yank_explicit_error = data['yank_explicit_error']
yank_implicit_fe = data['yank_implicit_fe']
yank_implicit_error = data['yank_implicit_error']

nligands = len(exp)


def fit(x, y):
    return np.mean(y - 1*x)


def rmse(x, y, b):
    f = 1*x + b
    rmse = np.sqrt(np.mean((f-y)**2))
    return rmse


def mue(x, y, b):
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


ynames =  ['YANK implicit',     'YANK explicit',     'FEP+',             'YANK implicit',     'YANK explicit']
xnames =  ['experimental',      'experimental',      'experimental',     'FEP+',              'FEP+']
ydatas =  [yank_implicit_fe,    yank_explicit_fe,    fepp,               yank_implicit_fe,    yank_explicit_fe]
yerrors = [yank_implicit_error, yank_explicit_error, np.zeros(nligands), yank_implicit_error, yank_explicit_error]
xdatas =  [exp,                 exp,                 exp,                fepp,                fepp]
nplots = len(xdatas)

# all_data = np.concatenate((exp, fepp, yank_explicit_fe, yank_implicit_fe))
all_data = np.array([])
rmses_x = [None] * nplots
rmses_y = [None] * nplots

sns.set()
base_size = 4
nrows = 2
ncols = 3
da_set = [('RMSE', rmse), ('MUE', mue)]

f, a = plt.subplots(nrows, ncols, figsize=(base_size*ncols, base_size*nrows))
color_wraps = ['orange', 'g']
decoy_artists = []
# Calculate plot min/max limits
# First pass: plot data
sbn_colors = sns.color_palette("hls", nligands)
for index in range(nplots):
    axes = a.flatten()[index]
    xname = copy.deepcopy(xnames[index])
    xdata = copy.deepcopy(xdatas[index])
    yname = copy.deepcopy(ynames[index])
    ydata = copy.deepcopy(ydatas[index])
    yerror = copy.deepcopy(yerrors[index])
    rmse_x = np.array([])
    rmse_y = np.array([])
    for ref_id in range(nligands):
        color = sbn_colors[ref_id]
        xlocal = xdata - xdata[ref_id]
        ylocal = ydata - ydata[ref_id]
        yerror_local = np.sqrt(yerror**2 + yerror[ref_id]**2)
        # Plot the scatter
        axes.scatter(xlocal, ylocal, marker='o', edgecolors='k',
                     c=color, zorder=20)
        axes.errorbar(xlocal, ylocal, yerr=2*yerror_local, ecolor=color,
                      elinewidth=0, mec='none', mew=0, linestyle='None',
                      zorder=10)
        all_data = np.concatenate((all_data, xlocal, ylocal))
        rmse_x = np.concatenate((rmse_x, xlocal))
        rmse_y = np.concatenate((rmse_y, ylocal))
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
    # Calculate the local best fit line
    local_fit = fit(rmse_x, rmse_y)
    # Plot the local best fit line
    axes.plot(min_max, min_max + local_fit, zorder=30)
    # Set the limits and aspect ratio
    axes.set_xlim(min_max)
    axes.set_ylim(min_max)
    axes.set_aspect('equal', 'box')
    # Add labels
    axes.set_xlabel(r"$\Delta\Delta G$ {} (kcal/mol)".format(xname))
    axes.set_ylabel(r"$\Delta\Delta G$ {} (kcal/mol)".format(yname))
    title_text = []
    for name, fn in da_set:
        local = fn(rmse_x, rmse_y, local_fit)
        # Calculate CI
        ci_min, ci_max = boostrap_fn(rmse_x, rmse_y, local_fit, fn)
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
f.savefig("mue_hinge_vs_fepp_exper.png", bbox_inches='tight')
# f.savefig("mue_hinge_vs_fepp_exper.pdf", bbox_inches='tight')
# plt.show()
