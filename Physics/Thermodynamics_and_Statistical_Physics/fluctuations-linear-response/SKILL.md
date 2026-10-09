---
name: fluctuations-linear-response
description: Fluctuations and Linear Response in Statistical Mechanics (Advanced). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: stat.mech.fluctuations
  domain: Statistical Mechanics
  subdomain: Advanced
  difficulty: 5/5
---

# Fluctuations and Linear Response

**ID:** `stat.mech.fluctuations`  
**Domain:** Statistical Mechanics → Advanced  
**Difficulty:** 5/5

## Prerequisites
- stat.mech.partition_function

## Core Concepts
- variance of observables
- fluctuation-dissipation
- correlation functions
- Kubo formula

## Key Equations
$$
\langle(\Delta E)^2\rangle = k_BT^2 C_V
$$
$$
\langle x(t)x(0)\rangle \sim e^{-t/\tau}
$$

## Methods
- Compute fluctuations from derivatives of Z
- Relate response to correlation functions
- Apply to diffusion and transport

## Typical Problem Types
- Energy fluctuations in the canonical ensemble
- Brownian motion
- Electrical conductivity

## Common Pitfalls
- Assuming fluctuations are negligible without justification
- Confusing correlation time and relaxation time

## Related Skills
- comp.molecular_dynamics
- cond.band_theory

## References
- Kubo Statistical Mechanics
- Pathria Ch.14
