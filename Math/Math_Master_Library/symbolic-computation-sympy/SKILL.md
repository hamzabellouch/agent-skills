---
name: symbolic-computation-sympy
description: "Use computer algebra for mathematics: SymPy symbolic algebra, calculus, equation solving, series, matrices, ODEs, simplification, LaTeX output, and verification of hand derivations. Includes a Python helper script. Use whenever exact symbolic results or verification of algebra is needed."
---

# Symbolic Computation with SymPy

## When to use
Exact simplification, factoring, limits, derivatives, integrals, series, equation systems, ODE solutions, matrix operations; verifying human derivations; generating LaTeX.

## Quick reference
```python
import sympy as sp
x, y, t = sp.symbols('x y t', real=True)
sp.simplify(expr); sp.expand(expr); sp.factor(expr); sp.apart(expr); sp.together(expr)
sp.diff(f, x, 2); sp.integrate(f, (x, 0, sp.oo)); sp.limit(f, x, 0)
sp.series(f, x, 0, 6); sp.solve(sp.Eq(a, b), x); sp.nsolve(eq, x, 1.0)
sp.dsolve(sp.Eq(y(t).diff(t, 2) + y(t), 0), y(t))
M = sp.Matrix([[1, 2], [3, 4]]); M.eigenvects(); M.det(); M.inv(); M.jordan_form()
sp.latex(expr); sp.lambdify(x, f, 'numpy')
```
- Declare assumptions (positive=True, integer=True) for correct simplification.
- Use rational numbers (sp.Rational(1,3)) not floats for exact results.
- Cross-check symbolic results numerically with random inputs.

## Script
`scripts/sympy_tools.py` includes: verify_identity (random-point testing + simplify), solve_and_check, taylor_error_bound, and a demo.

## Pitfalls
simplify may not reach the form you want (try trigsimp, radsimp, powsimp); integrate can fail or return piecewise results; sqrt branch and absolute value issues for complex inputs; timeouts on huge expressions (use series, numerical fallback).
