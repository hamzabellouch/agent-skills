---
name: boltzmann-distribution
description: Boltzmann Distribution in Statistical Mechanics (Foundations). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: stat.mech.boltzmann
  domain: Statistical Mechanics
  subdomain: Foundations
  difficulty: 4/5
---

# Boltzmann Distribution

**ID:** `stat.mech.boltzmann`  
**Domain:** Statistical Mechanics → Foundations  
**Difficulty:** 4/5

## Prerequisites
- stat.mech.microstates_ensembles

## Core Concepts
- Boltzmann factor
- canonical distribution
- temperature interpretation
- detailed balance

## Key Equations
$$
p_i = \frac{e^{-\beta E_i}}{Z}
$$
$$
Z = \sum_i e^{-\beta E_i}
$$

## Methods
- Write the partition function
- Compute probabilities and expectation values
- Take derivatives of lnZ

## Typical Problem Types
- Two-level system population
- Paramagnet
- Harmonic oscillator thermodynamics

## Common Pitfalls
- Forgetting normalization by Z
- Mixing eta = 1/k_B T

## Related Skills
- stat.mech.partition_function
- thermo.kinetic_theory

## References
- Reif Ch.6
- Kittel & Kroemer Ch.3
