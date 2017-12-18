import numpy as np
import matplotlib.pyplot as plt

yankfe = [-16.806,
-25.432,
-18.143,
-15.014,
-15.05,
-16.302,
-16.723,
-15.487,
-16.923,
-17.472,
-19.044,
-15.921
]
yankerr = [0.154,
0.0176,
0.092,
0.16,
0.097,
0.137,
0.13,
0.085,
0.143,
0.140,
0.136,
0.156
]

fepp = [-7.33521551,
-12.27822214,
-10.09261675,
-8.898817134,
-7.460412958,
-6.170323326,
-7.745894749,
-7.197390312,
-8.596160664,
-9.139049089,
-8.72836985,
-9.139049089,
]

f,a = plt.subplots(1,1)
a.errorbar(fepp, yankfe, yerr=yankerr, fmt='o')
mm = [min([min(fepp), min(yankfe)])-0.5, max([max(fepp), max(yankfe)])+0.5]
print(mm)
print([max(fepp), max(yankfe)])
a.plot(mm, mm, lw=1, c='k')
ylim = [mm[0], max(yankfe) + 0.5]
a.set_xlim(mm)
a.set_ylim(mm)
a.set_aspect('equal', 'box')

a.set_xlabel("FEP+, kcal/mol")
a.set_ylabel("Yank (Imp), kcal/mol")
f.suptitle("Imp. Solv. Yank compared to Exp. Solv. FEP+\n"
           "FF14SB+GAFF vs OPLS, units of kcal/mol")
f.savefig("imphinge_vs_fepp.png", bbox_inches='tight')
plt.show()
