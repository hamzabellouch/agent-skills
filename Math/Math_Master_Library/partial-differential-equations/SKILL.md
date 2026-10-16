---
name: partial-differential-equations
description: "Solve PDEs: heat, wave, Laplace, Poisson equations, separation of variables, Fourier series and transforms, characteristics, Green's functions, classification, maximum principles, Sobolev and weak solutions, numerical PDEs. Use for any PDE or boundary-value problem."
---

# Partial Differential Equations

## Classification
Second order a u_xx + 2b u_xy + c u_yy: elliptic (b^2 - ac < 0, Laplace), parabolic (= 0, heat), hyperbolic (> 0, wave). Linear vs nonlinear; well-posedness (Hadamard: existence, uniqueness, continuous dependence).

## Core equations
- Heat u_t = k u_xx: separation u = X(x)T(t) -> eigenfunctions sin(n pi x/L), decay e^{-k n^2 pi^2 t/L^2}; fundamental solution (4 pi k t)^(-1/2) exp(-x^2/4kt); maximum principle.
- Wave u_tt = c^2 u_xx: d'Alembert u = f(x - ct) + g(x + ct); energy conservation; finite speed of propagation; Duhamel's principle.
- Laplace/Poisson: harmonic functions, mean value property, maximum principle, Dirichlet and Neumann problems, Poisson kernel on a disk, Green's function G, fundamental solution -1/(2 pi) ln r (2D), 1/(4 pi r) (3D).
- Transport u_t + c u_x = 0 (characteristics); Burgers u_t + u u_x = 0 (shocks, Rankine-Hugoniot, entropy conditions).
- Schrodinger i u_t = -u_xx + V u; KdV (solitons); Navier-Stokes (open Millennium problem); Maxwell; Einstein.

## Methods
1. Separation of variables with Sturm-Liouville eigenfunctions (Fourier sine/cosine, Bessel in cylinders, Legendre in spheres).
2. Fourier/Laplace transforms for infinite domains.
3. Method of characteristics for first-order.
4. Green's functions and eigenfunction expansions; method of images.
5. Similarity solutions; dimensional analysis.
6. Variational/weak formulations: u in H^1, Lax-Milgram, Galerkin/finite elements; regularity theory.
7. Numerical: finite difference (CFL, von Neumann stability), finite element, spectral, finite volume.

## Checklist
State domain, boundary and initial conditions; compatibility; verify solution satisfies PDE and conditions; check limiting behavior.
