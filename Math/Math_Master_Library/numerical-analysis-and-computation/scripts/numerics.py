#!/usr/bin/env python3
"""Numerical analysis helpers: root finding, quadrature, interpolation, convergence order."""
import numpy as np
from numpy.polynomial import chebyshev as C

def newton(f, df, x0, tol=1e-14, it=50):
    x = x0
    for _ in range(it):
        dx = f(x) / df(x); x -= dx
        if abs(dx) < tol: break
    return x
def bisect(f, a, b, tol=1e-12):
    fa = f(a)
    while b - a > tol:
        m = (a + b) / 2; fm = f(m)
        if fa * fm <= 0: b = m
        else: a, fa = m, fm
    return (a + b) / 2
def simpson(f, a, b, n=100):
    n += n % 2; x = np.linspace(a, b, n + 1); y = f(x); h = (b - a) / n
    return h / 3 * (y[0] + y[-1] + 4 * y[1:-1:2].sum() + 2 * y[2:-1:2].sum())
def gauss_legendre(f, a, b, n=10):
    t, w = np.polynomial.legendre.leggauss(n); x = 0.5 * (b - a) * t + 0.5 * (b + a)
    return 0.5 * (b - a) * np.dot(w, f(x))
def cheb_interp(f, a, b, n):
    c = C.Chebyshev.interpolate(f, n, domain=[a, b]); return c
def convergence_order(errors, hs):
    return np.polyfit(np.log(hs), np.log(errors), 1)[0]

if __name__ == "__main__":
    print("sqrt(2) via Newton:", newton(lambda x: x * x - 2, lambda x: 2 * x, 1.0))
    print("bisect cos x = x:", bisect(lambda x: np.cos(x) - x, 0, 1))
    print("Simpson int sin 0..pi:", simpson(np.sin, 0, np.pi), " Gauss-Legendre:", gauss_legendre(np.sin, 0, np.pi, 6))
    hs = np.array([0.2, 0.1, 0.05, 0.025]); errs = [abs(simpson(np.exp, 0, 1, int(1 / h)) - (np.e - 1)) for h in hs]
    print("Simpson convergence order (~4):", round(convergence_order(errs, hs), 2))
    runge = lambda x: 1 / (1 + 25 * x * x); p = cheb_interp(runge, -1, 1, 20); xs = np.linspace(-1, 1, 1001)
    print("Chebyshev interp max error on Runge function:", float(np.max(np.abs(p(xs) - runge(xs)))))
