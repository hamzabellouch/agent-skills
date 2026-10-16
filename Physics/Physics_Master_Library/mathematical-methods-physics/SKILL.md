---
name: mathematical-methods-physics
description: "Apply math tools to physics: vector calculus, ODE/PDE, Fourier and Laplace transforms, special functions, complex analysis, linear algebra, tensors, group theory, Green's functions, variational calculus, perturbation methods. Use when a physics derivation needs a mathematical technique."
---

# Mathematical Methods for Physics

## Toolbox
- Vector calculus: grad, div, curl, Laplacian in cartesian/cylindrical/spherical; Gauss/Stokes theorems; Helmholtz decomposition; delta functions
- ODEs: linear constant coefficient (characteristic equation), Green's functions, Frobenius series, Sturm-Liouville theory (orthogonal eigenfunctions), phase plane analysis
- PDE: separation of variables for Laplace, heat, wave, Schrödinger; method of characteristics; Green's function for Poisson; eigenfunction expansions
- Special functions: Legendre P_l, spherical harmonics Y_lm, Bessel J_n, Hermite, Laguerre, Gamma Γ(n+1) = n!, error function, elliptic integrals, delta distribution
- Transforms: Fourier (convolution theorem, Parseval), Laplace (initial-value ODEs), Z-transform, Mellin
- Complex analysis: residue theorem ∮f dz = 2πi Σ Res; contour integrals for real integrals; Kramers-Kronig; branch cuts; analytic continuation; steepest descent
- Linear algebra: eigenproblems, diagonalization, Hermitian/unitary matrices, SVD, matrix exponentials, tensor products
- Tensors: index notation, Einstein summation, metric raising/lowering, Levi-Civita ε_ijk identity ε_ijk ε_ilm = δ_jl δ_km - δ_jm δ_kl
- Groups: SO(3), SU(2), SU(3), Lorentz group, Lie algebras, representations; Young tableaux
- Calculus of variations: Euler-Lagrange for functionals, constraints
- Asymptotics: Taylor/Laurent, Stirling n! ≈ √(2πn)(n/e)ⁿ, WKB, boundary layer, multiple scales, dimensional regularization
- Probability: Gaussian integrals ∫e^{-ax²} = √(π/a); central limit theorem; Bayes

## Practice
Always verify with a symbolic or numeric tool (see scripts in numerical-simulation-physics) before presenting a final closed-form result. Present assumptions about convergence and branch choices.
