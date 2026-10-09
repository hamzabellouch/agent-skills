---
name: bose-einstein-statistics-condensation
description: Bose-Einstein Statistics and Condensation in Statistical Mechanics (Quantum Statistics). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: stat.mech.bose_einstein
  domain: Statistical Mechanics
  subdomain: Quantum Statistics
  difficulty: 5/5
---

# Bose-Einstein Statistics and Condensation

**ID:** `stat.mech.bose_einstein`  
**Domain:** Statistical Mechanics → Quantum Statistics  
**Difficulty:** 5/5

## Prerequisites
- stat.mech.partition_function

## Core Concepts
- Bose-Einstein distribution
- photon gas
- BEC
- critical temperature
- chemical potential

## Key Equations
$$
\bar n(\epsilon) = \frac{1}{e^{(\epsilon-\mu)/k_BT}-1}
$$
$$
T_c = \frac{2\pi\hbar^2}{mk_B}\left(\frac{n}{\zeta(3/2)}\right)^{2/3}
$$

## Methods
- Use the BE distribution
- Evaluate photon and phonon gases
- Find BEC critical temperature

## Typical Problem Types
- Planck spectrum from BE
- Phonon heat capacity
- BEC experiments

## Common Pitfalls
- Allowing \mu > 0 for bosons
- Forgetting the ground state at T < T_c

## Related Skills
- qm.many_body.phonons
- qm.found.blackbody_planck

## References
- Pathria Ch.7
- Kittel & Kroemer Ch.7
