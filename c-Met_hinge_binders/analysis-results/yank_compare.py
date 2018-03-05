import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

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


def boostrap_rmse(x, y, b, nreplicates=1000):
    replicate_rmse = np.zeros([nreplicates])
    for replicate in range(nreplicates):
        # sample with replacement
        bootstrap_indices = np.random.choice(range(nligands), nligands)
        # compute statistics on this sample
        replicate_rmse[replicate] = rmse(x[bootstrap_indices], y[bootstrap_indices], b)
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

all_data = np.concatenate((exp, fepp, yank_explicit_fe, yank_implicit_fe))

# Establish min/max limits on graph
min_max = np.array([min(all_data)-.5, max(all_data)+0.5])

sns.set()
base_size = 4
nrows = 2
ncols = 3
f, a = plt.subplots(nrows, ncols, figsize=(base_size*ncols, base_size*nrows))
color_wraps = ['orange', 'g']
decoy_artists = []
# Calculate plot min/max limits
for index in range(nplots):
    axes = a.flatten()[index]
    xname = xnames[index]
    xdata = xdatas[index]
    yname = ynames[index]
    ydata = ydatas[index]
    yerror = yerrors[index]
    # Plot the scatter
    axes.errorbar(xdata, ydata, yerr=2*yerror, fmt='o')  # Plot scatter
    # Plot the y=x line
    axes.plot(min_max, min_max, lw=1, c='k')
    # Calculate the local best fit line
    local_fit = fit(xdata, ydata)
    # Plot the local best fit line
    axes.plot(min_max, min_max + local_fit)
    local_rmse = rmse(xdata, ydata, local_fit)
    # Calculate CI
    ci_min, ci_max = boostrap_rmse(xdata, ydata, local_fit)
    # Set the limits and aspect ratio
    axes.set_xlim(min_max)
    axes.set_ylim(min_max)
    axes.set_aspect('equal', 'box')
    # Add labels
    axes.set_xlabel(r"$\Delta G$ {} (kcal/mol)".format(xname))
    axes.set_ylabel(r"$\Delta G$ {} (kcal/mol)".format(yname))
    axes.annotate("RMSE: {0:3.2f} [{1:3.2f}, {2:3.2f}] kcal/mol".format(local_rmse, ci_min, ci_max),
                  xy=(0.5, 1.05),
                  xycoords='axes fraction',
                  rotation=0,
                  ha='center', va='center')
    # Equalize ticks
    xticks = axes.get_xticks()
    yticks = axes.get_yticks()
    # import pdb; pdb.set_trace()
    if len(xticks) < len(yticks):
        equalize_ticks(axes, 'x')
    else:
        equalize_ticks(axes, 'y')
# Delete unused plots
for index in range(nplots, a.size):
    f.delaxes(a.flatten()[index])
# Adjust spacing
f.subplots_adjust(hspace=0.00, wspace=0.4, top=0.99, bottom=0.05, left=0.1, right=0.95)
f.savefig("dg_hinge_vs_fepp_exper.png", bbox_inches='tight')
f.savefig("dg_hinge_vs_fepp_exper.pdf", bbox_inches='tight')
plt.show()
