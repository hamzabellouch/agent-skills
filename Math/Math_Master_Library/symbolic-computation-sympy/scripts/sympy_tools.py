#!/usr/bin/env python3
"""SymPy helpers for verification of derivations."""
import random, sympy as sp

def verify_identity(lhs, rhs, symbols, trials=20):
    """Numerically test lhs == rhs at random points, then try symbolic simplify."""
    ok = True
    for _ in range(trials):
        sub = {s: random.uniform(0.2, 2.0) for s in symbols}
        if abs(complex(lhs.subs(sub).evalf() - rhs.subs(sub).evalf())) > 1e-9: ok = False; break
    return ok, sp.simplify(lhs - rhs) == 0
def solve_and_check(eqs, vars_):
    sols = sp.solve(eqs, vars_, dict=True)
    checks = [all(sp.simplify(e.subs(s)) == 0 for e in eqs) for s in sols]
    return sols, checks
def taylor_remainder_bound(f, x, a, n, xval):
    """Lagrange remainder bound at xval for degree-n Taylor polynomial about a (numeric, sampled)."""
    d = sp.diff(f, x, n + 1); pts = [a + (xval - a) * k / 200 for k in range(201)]
    M = max(abs(float(d.subs(x, p))) for p in pts)
    return M * abs(xval - a) ** (n + 1) / sp.factorial(n + 1)

if __name__ == "__main__":
    x = sp.symbols("x", real=True)
    print("sin^2+cos^2=1:", verify_identity(sp.sin(x) ** 2 + sp.cos(x) ** 2, sp.Integer(1), [x]))
    print("integral e^{-x^2}:", sp.integrate(sp.exp(-x ** 2), (x, -sp.oo, sp.oo)))
    print("limit sin(x)/x:", sp.limit(sp.sin(x) / x, x, 0), " series e^x:", sp.series(sp.exp(x), x, 0, 5))
    print("ODE y''+y=0:", sp.dsolve(sp.Eq(sp.Function("y")(x).diff(x, 2) + sp.Function("y")(x), 0)))
    print("solve:", solve_and_check([x ** 2 - 5 * x + 6], [x]))
    print("Taylor bound sin deg 5 at 1:", float(taylor_remainder_bound(sp.sin(x), x, 0, 5, 1)))
