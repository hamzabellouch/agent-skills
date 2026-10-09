---
name: numerical-methods
description: Root finding, numerical interpolation, quadrature, numerical linear algebra, and error analysis.
metadata:
  category: Optimization and Game Theory
---

# Numerical Methods

## Domain
Algorithms for approximate solutions.

## Core Concepts
- Floating point, error, stability
- Convergence rates, order of accuracy
- Conditioning of problems

## Key Methods
- Root finding: bisection, Newton, secant
- Linear systems: LU, QR, iterative (Jacobi, CG)
- Interpolation: Lagrange, splines
- Quadrature: trapezoid, Simpson, Gauss
- ODE solvers: Euler, Runge–Kutta
- PDE: finite differences, finite elements

## Canonical Examples
- Newton: x_{n+1} = x_n - f(x_n)/f'(x_n), quadratic convergence.
- Simpson's rule error O(h⁴).
- RK4 local error O(h⁵).

## Common Pitfalls
- Numerical instability (catastrophic cancellation)
- Ignoring condition number
- Wrong step size (too large/small)

## Related Skills
Linear Algebra, Calculus, Optimization
