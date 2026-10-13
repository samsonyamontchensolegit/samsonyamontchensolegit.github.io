"""Reproduces every number and curve of the paper (main.tex).
Run:  python quadrature.py     -> writes data/*.csv and table-results.tex
"""
import numpy as np
from scipy.special import erf

tests = {
    "f1": dict(f=lambda x: np.exp(-x**2), a=0.0, b=1.0, exact=np.sqrt(np.pi)/2*erf(1.0)),
    "f2": dict(f=lambda x: np.sqrt(x),    a=0.0, b=1.0, exact=2.0/3.0),
    "f3": dict(f=lambda x: 1.0/(1.0+25.0*x**2), a=-1.0, b=1.0, exact=2.0/5.0*np.arctan(5.0)),
}

def trapezoid(f, a, b, n):
    x = np.linspace(a, b, n+1); y = f(x); h = (b-a)/n
    return h*(y[0]/2 + y[1:-1].sum() + y[-1]/2)

def simpson(f, a, b, n):
    x = np.linspace(a, b, n+1); y = f(x); h = (b-a)/n
    return h/3*(y[0] + 4*y[1:-1:2].sum() + 2*y[2:-1:2].sum() + y[-1])

def gauss(f, a, b, m):
    t, w = np.polynomial.legendre.leggauss(m)
    x = 0.5*(b-a)*t + 0.5*(b+a)
    return 0.5*(b-a)*np.dot(w, f(x))

floor = 1e-17
comp_n = [2**k for k in range(1, 11)]          # n = 2 ... 1024  (N = n+1 evaluations)
gauss_m = list(range(2, 101))                  # m = 2 ... 100   (N = m evaluations)
series = {}
for name, t in tests.items():
    f, a, b, ex = t["f"], t["a"], t["b"], t["exact"]
    rows = {"trap": [], "simp": [], "gauss": []}
    for n in comp_n:
        rows["trap"].append((n+1, max(abs(trapezoid(f, a, b, n)-ex), floor)))
        rows["simp"].append((n+1, max(abs(simpson(f, a, b, n)-ex), floor)))
    for m in gauss_m:
        rows["gauss"].append((m, max(abs(gauss(f, a, b, m)-ex), floor)))
    series[name] = rows
    for meth, data in rows.items():
        with open(f"data/{name}_{meth}.csv", "w") as fh:
            fh.write("N,err\n")
            for N, e in data:
                fh.write(f"{N},{e:.6e}\n")

def sci(x):
    if x <= 1.01*floor:
        return r"$<\!10^{-16}$"
    m, e = f"{x:.1e}".split("e")
    return rf"${m}\times10^{{{int(e)}}}$"

def err_at(rows, N):
    for n, e in rows:
        if n == N:
            return e
    raise KeyError(N)

def first_N(rows, tol):
    for n, e in rows:
        if e <= tol:
            return n
    return None

# table 1: error with N = 17 evaluations (n = 16 for the composite rules, m = 17 for Gauss-Legendre)
lines = []
names = {"f1": r"$f_1$", "f2": r"$f_2$", "f3": r"$f_3$"}   # short labels, defined in Table 1 of the paper
for k in ("f1", "f2", "f3"):
    r = series[k]
    lines.append(" & ".join([names[k], sci(err_at(r["trap"], 17)), sci(err_at(r["simp"], 17)), sci(err_at(r["gauss"], 17))]) + r" \\")
HEADER = r"Integrand & Trapezoidal & Simpson & Gauss--Legendre \\"
def full_tabular(rows):
    # the whole tabular is generated, because \input inside a tabular breaks booktabs rules
    return "\n".join([r"\begin{tabular}{lccc}", r"\toprule", HEADER, r"\midrule"] + rows + [r"\bottomrule", r"\end{tabular}"]) + "\n"
open("table-results.tex", "w", newline="\n").write(full_tabular(lines))

# table 2: smallest number of evaluations reaching a tolerance of 1e-8 (searched on the grids used above)
lines = []
for k in ("f1", "f2", "f3"):
    r = series[k]
    cells = []
    for meth in ("trap", "simp", "gauss"):
        n = first_N(r[meth], 1e-8)
        cells.append(str(n) if n else r"$>\!"+str(r[meth][-1][0])+"$")
    lines.append(" & ".join([names[k]] + cells) + r" \\")
open("table-evals.tex", "w", newline="\n").write(full_tabular(lines))

# observed convergence orders (least squares on the last points of the log-log curve)
def slope(rows, last=5):
    pts = np.array(rows[-last:], dtype=float)
    return np.polyfit(np.log(pts[:, 0]), np.log(pts[:, 1]), 1)[0]
print("exact values:", {k: float(v["exact"]) for k, v in tests.items()})
for k in tests:
    print(k, "slopes (error ~ N^p):",
          "trap %.2f" % slope(series[k]["trap"]), "simp %.2f" % slope(series[k]["simp"]),
          "| gauss (m=10..20) %.2f" % slope([r for r in series[k]["gauss"] if 10 <= r[0] <= 20], last=11))
for k in tests:
    print(k, "N=17:", {m: "%.2e" % err_at(series[k][m], 17) for m in ("trap", "simp", "gauss")},
          "| N for 1e-8:", {m: first_N(series[k][m], 1e-8) for m in ("trap", "simp", "gauss")})
