import numpy as np
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.gridspec as gridspec
import matplotlib.colors as mpl_colors

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


def p_check(calc, exp, threshold):
    not_zero = np.where(calc != 0.0)
    calc = calc[not_zero]
    exp = exp[not_zero]
    #args = np.logical_and(np.sign(calc) == np.sign(exp), np.abs(calc) > threshold)
    args = np.sign(calc) == np.sign(exp)
    args_e = np.abs(exp) > threshold
    p_out = calc[args].size / calc.size
    #p_out = calc[args].size / exp[args_e].size
    return p_out


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


def bootstrap_fn(x, y, b, function=p_check, nreplicates=1000):
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

nplots = 1

# kcal range
kcal_span = np.linspace(0, 3, 401)
n_kcal = kcal_span.size

# Set figure color base, scalar base, row and column count.
sns.set()
sbn_colors = sns.color_palette("hls", 3)
base_size = 4
nrows = 1
ncols = 1
plot_grid = gridspec.GridSpec(nrows, ncols)
f, axes = plt.subplots(1, 1)  #, figsize=(base_size*ncols*3, base_size*nrows*1.05))
ddg_all_expt = np.array([])
ddg_all_yexp = np.array([])
ddg_all_yimp = np.array([])
ddg_all_fepp = np.array([])
# Build all data
for index in range(nligands):
    # Local data copy, shifted for ddg
    expt = np.delete(exp - exp[index], index)
    explicit = np.delete(yank_explicit_fe - yank_explicit_fe[index], index)
    implicit = np.delete(yank_implicit_fe - yank_implicit_fe[index], index)
    fepp_local = np.delete(fepp - fepp[index], index)
    ddg_all_expt = np.concatenate((ddg_all_expt, expt))
    ddg_all_yexp = np.concatenate((ddg_all_yexp, explicit))
    ddg_all_yimp = np.concatenate((ddg_all_yimp, implicit))
    ddg_all_fepp = np.concatenate((ddg_all_fepp, fepp_local))
# Do CI
n_data = ddg_all_expt.size
# Create the data holders
exp_p = np.zeros(n_kcal)
imp_p = np.zeros(n_kcal)
fepp_p = np.zeros(n_kcal)
exp_p_ci = np.zeros([n_kcal, 2])
imp_p_ci = np.zeros([n_kcal, 2])
fepp_p_ci = np.zeros([n_kcal, 2])
for i, kcal in enumerate(kcal_span):
    # Threshold for CI checks, the logic is already in for non-CI
    # But drawing randomly from the whole set can result in expt values not above the limit
    # Which can lead to divide by zero error
    # if kcal >=3.7: pdb.set_trace()
    threshold_args = np.abs(ddg_all_expt) > kcal
    exp_p[i] = p_check(ddg_all_yexp[threshold_args],
                       ddg_all_expt[threshold_args],
                       kcal)
    exp_p_ci[i, :] = bootstrap_fn(ddg_all_yexp[threshold_args],
                                  ddg_all_expt[threshold_args],
                                  kcal)

    imp_p[i] = p_check(ddg_all_yimp[threshold_args],
                       ddg_all_expt[threshold_args],
                       kcal)
    imp_p_ci[i, :] = bootstrap_fn(ddg_all_yimp[threshold_args],
                                  ddg_all_expt[threshold_args],
                                  kcal)

    fepp_p[i] = p_check(ddg_all_fepp[threshold_args],
                        ddg_all_expt[threshold_args],
                        kcal)
    fepp_p_ci[i, :] = bootstrap_fn(ddg_all_fepp[threshold_args],
                                   ddg_all_expt[threshold_args], kcal)

# Shift data to % scale
exp_p *= 100
exp_p_ci *= 100
imp_p *= 100
imp_p_ci *= 100
fepp_p *= 100
fepp_p_ci *= 100
exp_color = sbn_colors[0]
exp_color_t = (*exp_color, 0.5)
imp_color = sbn_colors[1]
imp_color_t = (*imp_color, 0.5)
fep_color = sbn_colors[2]
fep_color_t = (*fep_color, 0.5)
data = [exp_p, imp_p, fepp_p]
cis = [exp_p_ci, imp_p_ci, fepp_p_ci]
colors = [exp_color, imp_color, fep_color]
names = ['Yank Explicit', 'Yank Implicit', 'FEP+']
curves = []
labels = []
skip_now = False
for probs, dci, color, name in zip(data, cis, colors, names):
    if not skip_now:
        skip_now = True
    else:
        continue
    color_t = (*color, 0.5)
    # probability curves, returns a list, so the comma is required
    curve, = axes.plot(kcal_span, probs, linestyle='-', c=color, label=name)
    # CI curve
    axes.fill_between(kcal_span, dci[:, 0], dci[:, 1], color=color_t, linestyle='--')
    # Fill artists
    curves.append(curve)
    labels.append(name)
# Create final decoy artist
decoy_color = mpl_colors.to_rgba(mpl_colors.cnames['black'], alpha=0.5)
curves.append(plt.Rectangle((0, 0), 1, 1, color=decoy_color))
labels.append("95% Confidence Intervals")

axes.set_ylabel("Probability, %")
axes.set_xlabel(r"$\Delta\Delta G$ Threshold, kcal/mol", fontsize=10)
axes.legend(curves, labels, fontsize=10, loc='lower right')
axes.set_ylim([50, 100])
axes.set_xlim([kcal_span.min(), kcal_span.max()])
axes.set_title("Probability compound will have correct\nsign with threshold", fontsize=15)

#     # Equalize ticks
#     xticks = axes.get_xticks()
#     yticks = axes.get_yticks()
#     if len(xticks) < len(yticks):
#         equalize_ticks(axes, 'x')
#     else:
#         equalize_ticks(axes, 'y')
# # Delete unused plots
# for index in range(nplots, a.size):
#     f.delaxes(a.flatten()[index])
# Adjust spacing
#f.subplots_adjust(hspace=0.00, wspace=0.4, top=0.99, bottom=0.05, left=0.05, right=0.95)
txt = r"$\Delta\Delta G$ relative to first molecule" + "\nwhich is also on 0,0" + "\n\n"
txt += "$\Delta\Delta G$ is taken separately on each axis\n" \
       "e.g. Experiment is relative to Experiment,\n   and FEP+ is relative to FEP+\n\n"
txt += "Dot color between figures is the same\nreference molecule"
# f.text((ncols*3-3)/(ncols*3), (1)/(nrows*2), txt, wrap=True,)
f.savefig("sign_probability_exp.png", bbox_inches='tight')
f.savefig("sign_probability_exp.pdf", bbox_inches='tight')
#plt.show()
