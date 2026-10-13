"""Generates every table and data file used in the book (book.tex).
Run:  python book_data.py
"""
import numpy as np
from scipy.special import erf

f1 = lambda x: np.exp(-x**2)
I1 = np.sqrt(np.pi) / 2 * erf(1.0)

def sci(x):
    if x == 0:
        return "$0$"
    m, e = f"{x:.2e}".split("e")
    return rf"${m}\times10^{{{int(e)}}}$"

def tabular(colspec, header, rows):
    out = [rf"\begin{{tabular}}{{{colspec}}}", r"\toprule", header + r" \\", r"\midrule"] + rows + [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(out) + "\n"

def write(name, text):
    with open(name, "w", newline="\n") as fh:
        fh.write(text)

# ------------------------------------------------------------ Riemann sums (Chapter 1)
def left(f, a, b, n):
    h = (b - a) / n; x = a + h * np.arange(n); return h * f(x).sum()
def right(f, a, b, n):
    h = (b - a) / n; x = a + h * np.arange(1, n + 1); return h * f(x).sum()
def mid(f, a, b, n):
    h = (b - a) / n; x = a + h * (np.arange(n) + 0.5); return h * f(x).sum()

rows = []
for n in (4, 8, 16, 32):
    rows.append(" & ".join([str(n), sci(abs(left(f1, 0, 1, n) - I1)), sci(abs(right(f1, 0, 1, n) - I1)), sci(abs(mid(f1, 0, 1, n) - I1))]) + r" \\")
write("table-riemann.tex", tabular("rccc", r"$n$ & $\lvert I-L_n\rvert$ & $\lvert I-R_n\rvert$ & $\lvert I-M_n\rvert$", rows))

# ------------------------------------------------------------ Gauss-Legendre nodes (Chapter 3)
rows = []
for m in range(2, 6):
    t, w = np.polynomial.legendre.leggauss(m)
    first = True
    for ti, wi in zip(t, w):
        if ti < -1e-12:
            continue
        label = str(m) if first else ""
        first = False
        rows.append(" & ".join([label, f"{ti:.10f}" if abs(ti) > 1e-12 else "0.0000000000", f"{wi:.10f}"]) + r" \\")
    if m < 5:
        rows.append(r"\addlinespace")
write("table-gaussnodes.tex", tabular("rrr", r"$m$ & nonnegative nodes $t_i$ & weights $w_i$", rows))

# ------------------------------------------------------------ Gauss on f1 (Chapter 3)
def gauss(f, a, b, m):
    t, w = np.polynomial.legendre.leggauss(m)
    x = 0.5 * (b - a) * t + 0.5 * (b + a)
    return 0.5 * (b - a) * np.dot(w, f(x))
rows = []
for m in range(1, 7):
    g = gauss(f1, 0, 1, m)
    rows.append(" & ".join([str(m), f"{g:.10f}", sci(abs(g - I1))]) + r" \\")
write("table-gausserr.tex", tabular("rcc", r"$m$ & $G_m$ & $\lvert I-G_m\rvert$", rows))

# ------------------------------------------------------------ adaptive Simpson (Chapter 4)
class Counter:
    def __init__(self, f):
        self.f = f; self.n = 0
    def __call__(self, x):
        self.n += 1; return self.f(x)

def adaptive_simpson(f, a, b, eps, mesh=None, maxdepth=50):
    fa, fb, fm = f(a), f(b), f((a + b) / 2)
    whole = (b - a) / 6 * (fa + 4 * fm + fb)
    def rec(a, b, eps, whole, fa, fm, fb, depth):
        m = (a + b) / 2
        lm, rm = (a + m) / 2, (m + b) / 2
        flm, frm = f(lm), f(rm)
        left_ = (m - a) / 6 * (fa + 4 * flm + fm)
        right_ = (b - m) / 6 * (fm + 4 * frm + fb)
        delta = left_ + right_ - whole
        if depth <= 0 or abs(delta) <= 15 * eps:
            if mesh is not None:
                mesh.append((a, b))
            return left_ + right_ + delta / 15
        return (rec(a, m, eps / 2, left_, fa, flm, fm, depth - 1) +
                rec(m, b, eps / 2, right_, fm, frm, fb, depth - 1))
    return rec(a, b, eps, whole, fa, fm, fb, maxdepth)

tests = [
    (r"$e^{-x^2}$ on $[0,1]$", f1, 0.0, 1.0, I1),
    (r"$\sqrt{x}$ on $[0,1]$", np.sqrt, 0.0, 1.0, 2.0 / 3.0),
    (r"$1/(1+25x^2)$ on $[-1,1]$", lambda x: 1.0 / (1.0 + 25.0 * x**2), -1.0, 1.0, 2.0 / 5.0 * np.arctan(5.0)),
]
rows = []
for name, f, a, b, ex in tests:
    c = Counter(f); mesh = []
    val = adaptive_simpson(c, a, b, 1e-8, mesh)
    rows.append(" & ".join([name, str(c.n), str(len(mesh)), sci(abs(val - ex))]) + r" \\")
    print(name, "evals", c.n, "intervals", len(mesh), "err %.2e" % abs(val - ex))
write("table-adaptive.tex", tabular("lccc", r"Integrand & evaluations & subintervals & error", rows))

# mesh for sqrt(x) with a coarser tolerance, to be drawn in Chapter 4
mesh = []
adaptive_simpson(np.sqrt, 0.0, 1.0, 1e-5, mesh)
with open("data/adaptive_mesh.csv", "w", newline="\n") as fh:
    fh.write("a,b\n")
    for a, b in sorted(mesh):
        fh.write(f"{a:.12g},{b:.12g}\n")
print("mesh intervals for sqrt(x), eps=1e-5:", len(mesh))

# error curves for the convergence figure of Chapter 2
def trap(f, a, b, n):
    h = (b - a) / n; x = np.linspace(a, b, n + 1); y = f(x); return h * (y[0] / 2 + y[1:-1].sum() + y[-1] / 2)
def simp(f, a, b, n):
    h = (b - a) / n; x = np.linspace(a, b, n + 1); y = f(x); return h / 3 * (y[0] + 4 * y[1:-1:2].sum() + 2 * y[2:-1:2].sum() + y[-1])
for name, fn in (("trap", trap), ("simp", simp)):
    with open(f"data/f1_{name}.csv", "w", newline="\n") as fh:
        fh.write("n,err\n")
        for k in range(1, 8):
            n = 2**k
            fh.write(f"{n},{max(abs(fn(f1, 0, 1, n) - I1), 1e-17):.6e}\n")

# Romberg table (Chapter 2): R[k][0] = T_(2^k), R[k][j] = (4^j R[k][j-1] - R[k-1][j-1]) / (4^j - 1)
R = []
for k in range(5):
    row = [trap(f1, 0, 1, 2**k)]
    for j in range(1, k + 1):
        row.append((4**j * row[j - 1] - R[k - 1][j - 1]) / (4**j - 1))
    R.append(row)
rows = []
for k, row in enumerate(R):
    cells = [str(2**k)] + [f"{v:.10f}" for v in row] + [""] * (5 - len(row))
    rows.append(" & ".join(cells) + r" \\")
write("table-romberg.tex", tabular("rlllll", r"$n$ & $R_{k,0}$ & $R_{k,1}$ & $R_{k,2}$ & $R_{k,3}$ & $R_{k,4}$", rows))
print("Romberg last:", R[-1])

# a few numbers quoted in the text
print("I =", repr(float(I1)))
print("T2, T4, S4:", trap(f1, 0, 1, 2), trap(f1, 0, 1, 4), simp(f1, 0, 1, 4), (4 * trap(f1, 0, 1, 4) - trap(f1, 0, 1, 2)) / 3)
print("L4,R4,M4:", left(f1, 0, 1, 4), right(f1, 0, 1, 4), mid(f1, 0, 1, 4))
print("n for trapezoid bound 1e-6, |f''|<=2:", int(np.ceil(1 / np.sqrt(6e-6))))
