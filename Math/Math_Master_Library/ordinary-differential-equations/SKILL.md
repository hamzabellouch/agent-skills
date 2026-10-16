---
name: ordinary-differential-equations
description: "Solve ODEs: first-order (separable, linear, exact), second-order linear with constant coefficients, variation of parameters, Laplace transforms, series solutions, systems, phase plane, stability, existence and uniqueness, boundary value problems. Use for any differential equation."
---

# Ordinary Differential Equations

## First order
- Separable: dy/dx = f(x)g(y) -> integral dy/g = integral f dx.
- Linear: y' + p(x)y = q(x); integrating factor mu = e^{integral p}; (mu y)' = mu q.
- Exact: M dx + N dy = 0 with M_y = N_x; find potential F. Otherwise seek integrating factor.
- Bernoulli y' + p y = q y^n -> v = y^(1-n). Homogeneous dy/dx = F(y/x) -> v = y/x. Riccati with known solution.
- Autonomous: phase line, equilibria and stability; logistic y' = ry(1 - y/K).

## Higher order linear
- Constant coefficients: characteristic polynomial; real distinct roots e^{r x}; repeated x e^{r x}; complex a +- bi -> e^{ax}(cos bx, sin bx).
- Nonhomogeneous: undetermined coefficients (modify by x^k for resonance); variation of parameters with Wronskian W: y_p = -y1 integral y2 g/W + y2 integral y1 g/W.
- Euler-Cauchy x^2 y'' + a x y' + b y = 0 -> y = x^r.
- Reduction of order; Green's function; Laplace transforms: L{y'} = sY - y(0); L{e^{at}} = 1/(s-a); shift theorems; convolution; Dirac delta and Heaviside for forcing.
- Series (Frobenius): regular singular points, indicial equation; Bessel, Legendre, Airy equations.

## Systems & dynamics
- x' = Ax: eigenvalues determine solutions e^{At}; classification: node, saddle, spiral, center, degenerate; trace-determinant plane.
- Nonlinear: linearization at fixed points (Hartman-Grobman), Lyapunov functions, limit cycles, Poincare-Bendixson, bifurcations (see physics skill chaos-nonlinear-dynamics).
- Theory: Picard-Lindelof existence-uniqueness (f Lipschitz in y); Gronwall inequality; continuous dependence.
- BVP and Sturm-Liouville: eigenvalues, orthogonal eigenfunctions, Fourier expansions.

## Numerical
Euler, RK4, adaptive methods, stiff solvers (see numerical-analysis-and-computation).

## Verification
Substitute solution back; check initial conditions; compare with numerics.
