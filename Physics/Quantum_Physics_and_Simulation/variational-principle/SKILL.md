---
name: variational-principle
description: Variational Principle in Quantum Mechanics (Approximations). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: qm.approx.variational
  domain: Quantum Mechanics
  subdomain: Approximations
  difficulty: 4/5
---

# Variational Principle

**ID:** `qm.approx.variational`  
**Domain:** Quantum Mechanics → Approximations  
**Difficulty:** 4/5

## Prerequisites
- qm.formalism.operators

## Core Concepts
- trial wavefunction
- upper bound on ground state
- variational parameter
- Rayleigh-Ritz

## Key Equations
$$
E_{trial} = \frac{\langle\psi_T|H|\psi_T\rangle}{\langle\psi_T|\psi_T\rangle} \ge E_0
$$

## Methods
- Choose a physically motivated trial function
- Minimize \langle Hangle with respect to parameters
- Interpret the result as an upper bound

## Typical Problem Types
- Helium ground state
- Hydrogen in a magnetic field
- Molecules

## Common Pitfalls
- Assuming the trial energy can go below the true ground energy
- Poor trial function choices

## Related Skills
- qm.approx.perturbation_ti
- cond.band_theory

## References
- Griffiths QM Ch.7
- Sakurai Ch.5
