---
name: monte-carlo-methods
description: Monte Carlo Methods in Computational Physics (Numerical Methods). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: comp.monte_carlo
  domain: Computational Physics
  subdomain: Numerical Methods
  difficulty: 4/5
---

# Monte Carlo Methods

**ID:** `comp.monte_carlo`  
**Domain:** Computational Physics → Numerical Methods  
**Difficulty:** 4/5

## Prerequisites
- math.probability
- comp.numerical_integration

## Core Concepts
- random sampling
- importance sampling
- Metropolis-Hastings
- Markov chains
- variance reduction

## Key Equations
$$
\langle f\rangle \approx \frac1N\sum_i f(x_i),\ \sigma \sim \frac{1}{\sqrt N}
$$

## Methods
- Choose a sampling distribution
- Run the Markov chain to equilibrium
- Estimate statistical errors

## Typical Problem Types
- High-dimensional integrals
- Ising model simulation
- Radiative transfer

## Common Pitfalls
- Forgetting autocorrelation time
- Insufficient thermalization

## Related Skills
- stat.mech.ising
- comp.molecular_dynamics

## References
- Landau & Binder Monte Carlo Simulations
