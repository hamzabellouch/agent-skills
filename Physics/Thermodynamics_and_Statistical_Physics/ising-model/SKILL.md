---
name: ising-model
description: The Ising Model in Statistical Mechanics (Models). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: stat.mech.ising
  domain: Statistical Mechanics
  subdomain: Models
  difficulty: 5/5
---

# The Ising Model

**ID:** `stat.mech.ising`  
**Domain:** Statistical Mechanics → Models  
**Difficulty:** 5/5

## Prerequisites
- stat.mech.phase_transitions
- comp.monte_carlo

## Core Concepts
- spin lattice
- exchange coupling
- 1D/2D Ising
- mean-field theory
- transfer matrix

## Key Equations
$$
H = -J\sum_{\langle ij\rangle} s_i s_j - h\sum_i s_i
$$
$$
Z = \sum_{\{s\}} e^{-\beta H}
$$

## Methods
- Compute Z for 1D via transfer matrix
- Use mean-field for higher dimensions
- Simulate via Monte Carlo

## Typical Problem Types
- 1D Ising (no phase transition)
- 2D Onsager solution (conceptually)
- Magnetization vs temperature

## Common Pitfalls
- Expecting a transition in 1D with finite J
- Confusing T_c with J/k_B

## Related Skills
- comp.monte_carlo
- cond.magnetism

## References
- Kardar Ch.5
- Goldenfeld Ch.3
