---
name: spring-forces-hooke-s-law
description: Spring Forces and Hooke's Law in Mechanics (Dynamics). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: mech.dynamics.springs
  domain: Mechanics
  subdomain: Dynamics
  difficulty: 2/5
---

# Spring Forces and Hooke's Law

**ID:** `mech.dynamics.springs`  
**Domain:** Mechanics → Dynamics  
**Difficulty:** 2/5

## Prerequisites
- mech.dynamics.newton_laws

## Core Concepts
- Hooke's law
- spring constant
- restoring force
- series/parallel springs
- effective k

## Key Equations
$$
F = -kx
$$
$$
\frac{1}{k_{eff}} = \sum_i \frac{1}{k_i}\ \text{(series)}
$$
$$
k_{eff} = \sum_i k_i\ \text{(parallel)}
$$

## Methods
- Set x = 0 at the equilibrium position
- Write ma = -kx
- Combine springs when needed

## Typical Problem Types
- Mass on a spring
- Springs in series/parallel
- Coupled oscillators

## Common Pitfalls
- Forgetting the minus sign in Hooke's law
- Using the wrong effective k

## Related Skills
- mech.oscillations.shm
- mech.energy.conservative_potential

## References
- Halliday-Resnick-Walker Ch.7,15
