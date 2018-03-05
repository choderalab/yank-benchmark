import numpy as np
import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import copy
import pdb
import matplotlib.colors as colors
import simtk.unit as unit

nsteps_per_iteration = 500
timestep = 2*unit.femtosecond
iteration_time = nsteps_per_iteration * timestep / unit.nanosecond


# Load data from the stored numpy file
data = np.load('free_energy_data.npz')
exp = data['experimental']
fepp = data['fepplus']
yank_explict_fe = ()
yank_explicit_fe = data['yank_explicit_fe']
yank_explicit_error = data['yank_explicit_error']
yank_implicit_fe = data['yank_implicit_fe']
yank_implicit_error = data['yank_implicit_error']

#Count number of ligands
nligands = len(exp)


def get_yank_fe_with_time(solvent, molecule):
    yank_data = np.load('{0}/{0}{1}_fe_by_iteration.npz'.format(solvent, molecule))
    yank_fe = yank_data['free_energy']
    yank_x = yank_data['x']
    return yank_fe, yank_x


def time_index_calc(current_time_index, max_index):
    output = np.zeros(nligands, dtype=int)
    for idx in range(nligands):
        if current_time_index >= max_index[idx]:
            output[idx] = max_index[idx]
        else:
            output[idx] = current_time_index
    return output


def fit(x, y):
    # Find Y = X + B function (shift the y=x line, not used for DDG)
    return np.mean(y - 1*x)


def nofit(*_):
    return 0


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
ynames =  ['YANK implicit',     'YANK explicit',     'YANK implicit',     'YANK explicit']
snames =  ['implicit',          'explicit',          'implicit',          'explicit']
xnames =  ['experimental',      'experimental',      'FEP+',              'FEP+']
ydatas =  [yank_implicit_fe,    yank_explicit_fe,    fepp,               yank_implicit_fe,    yank_explicit_fe]
yerrors = [yank_implicit_error, yank_explicit_error, yank_implicit_error, yank_explicit_error]
xdatas =  [exp,                 exp,                 fepp,                fepp]
nplots = len(xdatas)

# Populate blank data holders
all_data = np.array([])
rmses_x = [None] * nplots
rmses_y = [None] * nplots

# Set figure color base, scalar base, row and column count.
sns.set()
sbn_colors = sns.color_palette("hls", 2)
base_size = 4
nrows = 2
ncols = 2
da_set = [('RMSE', rmse), ('MUE', mue)]

for statistic, stat_fn in da_set:
    true_ylim = np.array([])
    f, a = plt.subplots(nrows, ncols, figsize=(base_size*ncols, base_size*nrows))
    for index in range(nplots):
        print("Stat {}, plot {}".format(statistic, index))
        axes = a.flatten()[index]  # Get plot we are working with
        # Get the X data
        xdata = copy.deepcopy(xdatas[index])
        xname = xnames[index]
        yname = ynames[index]
        sname = snames[index]
        data = [get_yank_fe_with_time(sname, idx) for idx in range(nligands)]
        max_time = 0
        # Number of points per ligand
        n_times = np.zeros(nligands, dtype=int)
        for j, (_, times) in enumerate(data):
            size = times.size
            n_times[j] = size
            if size > max_time:
                max_time = size
        # Ydata: nmolecule, free_energy
        ydata = np.zeros([nligands, max_time])
        times = np.zeros([nligands, max_time])
        for j, subdata in enumerate(data):
            sub_fe = subdata[0][:, 0]
            sub_time = subdata[1]
            max_fll = sub_time.size
            ydata[j, :max_fll] = sub_fe
            times[j, :max_fll] = sub_time
        observable_dg = np.zeros(max_time)
        observable_dg_ci = np.zeros([max_time, 2])
        observable_ddg = np.zeros(max_time)
        observable_ddg_ci = np.zeros([max_time, 2])
        # Now loop through all times
        true_x = times[np.argmax(n_times), :]
        for time_idx, time in enumerate(true_x):
            # Get current free energy, or our last best estimate of it
            # -1 because time_index_calc operates on time indices
            time_slice = time_index_calc(time_idx, n_times-1)
            # Fancy slice, cant just do [:, list]
            current_free_energy = ydata[np.arange(nligands), time_slice]
            local_fit = fit(xdata, current_free_energy)
            observable_dg[time_idx] = stat_fn(xdata, current_free_energy, local_fit)
            observable_dg_ci[time_idx, :] = boostrap_fn(xdata, current_free_energy, local_fit, function=stat_fn)
            # Now do Delta Delta G
            collected_ddg_x = np.array([])
            collected_ddg_y = np.array([])
            for lig_idx in range(nligands):
                # Local data copy, shifted for ddg
                x_ddg_local = np.delete(xdata - xdata[lig_idx], lig_idx)
                y_ddg_local = np.delete(current_free_energy - current_free_energy[lig_idx], lig_idx)
                collected_ddg_x = np.concatenate((collected_ddg_x, x_ddg_local))
                collected_ddg_y = np.concatenate((collected_ddg_y, y_ddg_local))
            observable_ddg[time_idx] = stat_fn(collected_ddg_x, collected_ddg_y, 0)
            observable_ddg_ci[time_idx, :] = boostrap_fn(collected_ddg_x, collected_ddg_y, 0, function=stat_fn)
        if np.allclose(xdata, exp):
            fep_dg_y = np.zeros(max_time)
            fep_dg_y[:] = [stat_fn(xdata, fepp, 0)] * max_time
            fep_dg_y_ci = np.array([boostrap_fn(xdata, fepp, 0, function=stat_fn)] * max_time)
            collected_ddg_fep_y = np.array([])
            collected_ddg_x = np.array([])
            for lig_idx in range(nligands):
                x_ddg_local = np.delete(xdata - xdata[lig_idx], lig_idx)
                fep_ddg_local = np.delete(fepp - fepp[lig_idx], lig_idx)
                collected_ddg_x = np.concatenate((collected_ddg_x, x_ddg_local))
                collected_ddg_fep_y = np.concatenate((collected_ddg_fep_y, fep_ddg_local))
            fep_ddg_y = np.array([stat_fn(collected_ddg_x, collected_ddg_fep_y, 0)] * max_time)
            fep_dg_y_ci = np.array([boostrap_fn(collected_ddg_x, collected_ddg_fep_y, 0, function=stat_fn)] * max_time)

        # FINALLY Plot something
        drop = 1  # Samples to drop
        dg_color = sbn_colors[0]
        dg_color_t = (*dg_color, 0.5)
        ddg_color = sbn_colors[1]
        ddg_color_t = (*ddg_color, 0.5)
        # Convert iterations to time
        true_x *= iteration_time
        axes.plot(true_x[drop:], observable_dg[drop:],
                  linestyle='-',
                  color=dg_color,
                  zorder=20,
                  label=r"$\Delta G$")
        axes.fill_between(true_x[drop:], observable_dg_ci[drop:, 0], observable_dg_ci[drop:, 1],
                          color=dg_color_t,
                          linewidth=0, zorder=10)
        axes.plot(true_x[drop:], observable_ddg[drop:],
                  linestyle='-',
                  color=ddg_color,
                  zorder=20,
                  label=r"$\Delta\Delta G$")
        axes.fill_between(true_x[drop:], observable_ddg_ci[drop:, 0], observable_ddg_ci[drop:, 1],
                          color=ddg_color_t,
                          linewidth=0,
                          zorder=10)
        if np.allclose(xdata, exp):
            axes.plot(true_x[drop:], fep_dg_y[drop:],
                      linestyle='--',
                      color='k',
                      zorder=20,
                      label=r"FEP+")
        # Now do formatting
        axes.set_xlabel("Simulation Time (ns)")
        axes.set_ylabel("{}".format(statistic))
        axes.set_title("{} vs. {}".format(yname, xname))
        axes.legend()
        axes.set_xlim([true_x[drop:].min(), true_x[drop:].max()])
        true_ylim = np.concatenate((true_ylim, np.array(axes.get_ylim())))
    true_ylim = (0, np.ceil(true_ylim.max()))
    for ax in a.flatten():
        ax.set_ylim(true_ylim)
    f.suptitle(statistic)
    f.subplots_adjust(top=0.9, bottom=0.05, left=0.1, right=0.95, hspace=0.25, wspace=0.25)
    f.savefig("{}_vs_time.png".format(statistic), bbox_inches='tight')
    f.savefig("{}_vs_time.pdf".format(statistic), bbox_inches='tight')

#plt.show()
