#!/usr/bin/env python3
"""Uncertainty propagation (numeric & Monte Carlo) and weighted fitting."""
import numpy as np
_trap = getattr(np, "trapezoid", None) or np.trapz

def propagate(f, x, sx, h=1e-6):
    """First-order propagation for uncorrelated inputs. x, sx: arrays."""
    x = np.asarray(x, float); sx = np.asarray(sx, float)
    grads = np.empty_like(x)
    for i in range(len(x)):
        d = np.zeros_like(x); d[i] = h*max(1.0, abs(x[i]))
        grads[i] = (f(x + d) - f(x - d)) / (2*d[i])
    return f(x), np.sqrt(np.sum((grads*sx)**2))

def monte_carlo(f, x, sx, n=200000, seed=0):
    rng = np.random.default_rng(seed)
    s = rng.normal(x, sx, size=(n, len(x)))
    v = np.apply_along_axis(f, 1, s)
    return v.mean(), v.std(ddof=1)

def weighted_linear_fit(x, y, sy):
    """Fit y = a + b x. Returns (a, sa, b, sb, chi2, ndof)."""
    x, y, sy = map(np.asarray, (x, y, sy)); w = 1/sy**2
    S, Sx, Sy = w.sum(), (w*x).sum(), (w*y).sum()
    Sxx, Sxy = (w*x*x).sum(), (w*x*y).sum(); D = S*Sxx - Sx**2
    a, b = (Sxx*Sy - Sx*Sxy)/D, (S*Sxy - Sx*Sy)/D
    chi2 = (((y - a - b*x)/sy)**2).sum()
    return a, np.sqrt(Sxx/D), b, np.sqrt(S/D), chi2, len(x) - 2

if __name__ == "__main__":
    # g from pendulum: g = 4 pi^2 L / T^2
    g = lambda p: 4*np.pi**2*p[0]/p[1]**2
    print("Analytic:", propagate(g, [1.000, 2.007], [0.002, 0.005]))
    print("Monte Carlo:", monte_carlo(g, [1.000, 2.007], [0.002, 0.005]))
    x = np.arange(1, 8); y = 2.0 + 0.5*x + np.random.default_rng(1).normal(0, 0.1, 7)
    a, sa, b, sb, chi2, nd = weighted_linear_fit(x, y, np.full(7, 0.1))
    print(f"Fit: a={a:.3f}+-{sa:.3f}  b={b:.3f}+-{sb:.3f}  chi2/ndof={chi2:.2f}/{nd}")
