---
name: numerical-simulation-physics
description: "Simulate physical systems numerically: ODE integrators (Euler, RK4, Verlet, symplectic), PDE solvers (finite difference, spectral), N-body, molecular dynamics, Schrodinger solvers, stability and error analysis. Includes ready-to-run Python scripts. Use whenever the user wants a physics simulation, numeric solution, or code for physics."
---

# Numerical Simulation in Physics

## Choose the method
| Problem | Method |
|---|---|
| Generic ODE | RK4 or adaptive RK45 (scipy.integrate.solve_ivp) |
| Long-time Hamiltonian (orbits, MD) | Velocity-Verlet / leapfrog / Yoshida (symplectic, energy error bounded) |
| Stiff ODE | Implicit methods (Radau, BDF) |
| Heat/diffusion | FTCS (r = DΔt/Δx² ≤ 1/2) or Crank-Nicolson |
| Wave equation | Leapfrog; CFL: cΔt/Δx ≤ 1 |
| Schrödinger 1D | Split-operator FFT, Crank-Nicolson, or matrix diagonalization |
| Poisson/Laplace | Gauss-Seidel/SOR, multigrid, FFT |
| Many-body ground states | Exact diagonalization, DMRG, QMC |

## Workflow
1. Non-dimensionalize equations. 2. Pick Δt/Δx from stability and accuracy needs. 3. Validate on an analytic case. 4. Run convergence study (halve step, error should drop by 2^order). 5. Monitor conserved quantities. 6. Plot and interpret.

## Scripts in this skill
- `scripts/integrators.py` — Euler, RK4, velocity-Verlet, with a demo (pendulum energy drift).
- `scripts/schrodinger1d.py` — finite-difference eigenstates of arbitrary 1D potential.
- `scripts/nbody.py` — gravitational N-body with leapfrog and energy diagnostics.
- `scripts/heat_wave_pde.py` — 1D heat and wave equation solvers.
Run: `python scripts/<name>.py` (requires numpy; matplotlib optional).

## Pitfalls
Euler is unstable for oscillators (energy grows). Time-step too large breaks CFL. Floating point: avoid subtracting near-equal numbers; use compensated sums for long runs. Always state the integrator and step size with results.
