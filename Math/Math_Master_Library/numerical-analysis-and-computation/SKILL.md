---
name: numerical-analysis-and-computation
description: "Do numerical analysis: floating point, root finding, interpolation, numerical integration, linear solvers, eigenvalue algorithms, ODE and PDE solvers, error analysis, stability, convergence, Fast Fourier Transform. Includes Python scripts. Use for any numerical computation or algorithm accuracy question."
---

# Numerical Analysis & Computation

## Floating point
IEEE 754 double: 53-bit mantissa, machine epsilon 2.2e-16; catastrophic cancellation (rewrite sqrt(x+1) - sqrt(x) = 1/(sqrt(x+1) + sqrt(x))); overflow/underflow; summation with Kahan; relative vs absolute error; condition number of a problem vs stability of an algorithm.

## Root finding
Bisection (linear, guaranteed), Newton (quadratic, needs derivative), secant (order 1.618), Brent (robust default), fixed-point iteration (converges if |g'| < 1), polynomial roots via companion matrix eigenvalues.

## Interpolation & approximation
Lagrange/Newton interpolation (Runge phenomenon -> use Chebyshev nodes), splines (cubic), least squares, minimax (Remez), Pade approximants, Chebyshev series.

## Integration & differentiation
Trapezoid O(h^2), Simpson O(h^4), Gauss-Legendre (exact to degree 2n-1), Romberg, adaptive quadrature, Monte Carlo (1/sqrt(N)) and quasi-MC for high dimensions; finite differences (central O(h^2); choose h ~ eps^{1/3}), automatic differentiation (exact derivatives to machine precision).

## Linear algebra numerics
LU with partial pivoting, Cholesky, QR (Householder), SVD; iterative: Jacobi, Gauss-Seidel, conjugate gradient, GMRES; eigen: power iteration, QR algorithm, Lanczos; sparse storage; preconditioning.

## Differential equations
Euler, Heun, RK4, adaptive RK45, multistep, stiff solvers (BDF, implicit RK), symplectic integrators; global error ~ h^p; stability regions; PDE: FD/FE/FV, CFL.

## FFT & signal
FFT O(n log n); convolution via FFT; spectral methods for smooth periodic problems.

## Workflow
Choose the method by smoothness and size, estimate error, run convergence tests (halve h), compare against a known solution. Scripts: `scripts/numerics.py` (Brent/Newton, Gauss quadrature, Chebyshev interpolation, convergence-order estimator).
