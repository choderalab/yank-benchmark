import numpy as np
import matplotlib.pyplot as plt
from pymbar import timeseries

y = np.load('explicit0_timeseries.npy')
[n_equilibration, g_t, n_effective_max] = timeseries.detectEquilibration(y)
[n_short, g_t_short, n_eff_max_short] = timeseries.detectEquilibration(y[1:])

print("Full Trajectory -- Equilibration {0:d}, Subsample Rate {1:3.2f}, Num Effective {2:d}".format(
    n_equilibration, g_t, int(np.floor(n_effective_max))
))
print("Trajectory w/o initial sample -- Equilibration {0:d}, Subsample Rate {1:3.2f}, Num Effective {2:d}".format(
    n_short, g_t_short, int(np.floor(n_eff_max_short))
))

f, (a,b) = plt.subplots(2, 1)
x = np.arange(y.size)
a.plot(x, y, 'k-', label='Timeseries')
b.plot(x[1:], y[1:], '-k')
for p in [a, b]:
    ylim = p.get_ylim()
    xlim = p.get_xlim()
    p.set_xlabel('Iteration')
    p.set_ylabel(r'$\sum_k u_{k,k,n}$')
    p.vlines(n_equilibration, *ylim,
             colors='b', linewidth=1,
             label='Full Timeseries: Num Samples={}'.format(int(np.floor(n_effective_max))))
    p.vlines(n_short, *ylim,
             colors='r', linewidth=1,
             label='Timeseries[1:]: Num Samples={}'.format(int(np.floor(n_eff_max_short))))
    p.set_ylim(ylim)
    p.set_xlim(xlim)
a.legend()
f.savefig('bad_series.png', bbox_inches='tight')
