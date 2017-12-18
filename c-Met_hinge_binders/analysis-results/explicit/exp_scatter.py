import numpy as np
import matplotlib.pyplot as plt

yankfe = [
-20.526,
-24.326,
-23.486,
-19.293,
-18.701,
-17.449,
-18.121,
-17.548,
-22.969,
-22.231,
-21.358,
-22.199,
]
yankerr = [
0.36,
0.444,
0.413,
0.353,
0.37,
0.526,
0.431,
0.456,
0.414,
0.336,
0.411,
0.527,
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
a.plot(mm, mm, lw=1, c='k')
ylim = [mm[0], max(yankfe) + 0.5]
a.set_xlim(mm)
a.set_ylim(mm)
a.set_aspect('equal', 'box')

a.set_xlabel("FEP+, kcal/mol")
a.set_ylabel("Yank (Exp), kcal/mol")
f.suptitle("Exp. Solv. Yank compared to Exp. Solv. FEP+\n"
           "FF14SB+GAFF vs OPLS, units of kcal/mol")
f.savefig("exphinge_vs_fepp.png", bbox_inches='tight')
plt.show()
