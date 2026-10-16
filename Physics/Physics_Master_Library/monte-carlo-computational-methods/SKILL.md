---
name: monte-carlo-computational-methods
description: "Use stochastic and advanced computational methods in physics: Monte Carlo integration, Metropolis algorithm, Ising simulation, molecular dynamics, path-integral MC, lattice gauge theory, DFT, tensor networks, machine learning for physics. Use for sampling, simulations of many-body and statistical systems."
---

# Monte Carlo & Computational Methods

## Monte Carlo
- Integration error ∝ 1/√N regardless of dimension; importance sampling and variance reduction; quasi-random (Sobol)
- Metropolis-Hastings: accept with min(1, e^{-βΔE}); detailed balance; thermalize, then measure; autocorrelation time τ affects error (σ ≈ sqrt(2τ var/N))
- Ising model: single-spin flip near T_c suffers critical slowing; use Wolff/Swendsen-Wang cluster updates; finite-size scaling to extract T_c and exponents
- Other: Gillespie algorithm for stochastic kinetics; kinetic Monte Carlo; diffusion and variational QMC for electron systems; path-integral MC for quantum bosons; sign problem for fermions
- Particle transport: Geant4 / MCNP-style radiation transport

## Molecular dynamics
- Integrate Newton's equations with velocity-Verlet; Lennard-Jones potential V = 4ε[(σ/r)¹² - (σ/r)⁶]; periodic boundary conditions; neighbor lists; thermostats (Nosé-Hoover, Langevin), barostats
- Observables: radial distribution function g(r), diffusion via mean-square displacement, Green-Kubo relations, pressure via virial
- Force fields vs ab initio MD, machine-learned potentials

## Electronic structure & quantum many-body
- Hartree-Fock, DFT (Kohn-Sham, LDA/GGA/hybrid functionals), GW, DMFT, coupled cluster
- Exact diagonalization (Lanczos), DMRG for 1D, tensor networks (MPS, PEPS), quantum Monte Carlo
- Lattice QCD: Wilson action, hybrid Monte Carlo
- Machine learning: neural network quantum states, symbolic regression for laws, PINNs, surrogate models, uncertainty quantification

## Good practice
Reproducibility (seed, version), convergence in N, system size, time step; error bars from blocking/jackknife; compare with exact solvable cases (2D Ising Onsager).
