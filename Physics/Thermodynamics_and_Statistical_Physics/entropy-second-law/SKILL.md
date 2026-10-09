---
name: entropy-second-law
description: Entropy and the Second Law in Thermodynamics (Entropy). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: thermo.entropy
  domain: Thermodynamics
  subdomain: Entropy
  difficulty: 3/5
---

# Entropy and the Second Law

**ID:** `thermo.entropy`  
**Domain:** Thermodynamics → Entropy  
**Difficulty:** 3/5

## Prerequisites
- thermo.second_law
- stat.mech.microstates_ensembles

## Core Concepts
- entropy
- statistical definition
- irreversibility
- free expansion
- entropy of mixing

## Key Equations
$$
dS = \frac{dQ_{rev}}{T}
$$
$$
S = k_B \ln\Omega
$$
$$
\Delta S_{mix} = -nR\sum x_i \ln x_i
$$

## Methods
- Choose a reversible path between the same states
- Use statistical definition for microstates
- Compute \Delta S_{universe}

## Typical Problem Types
- Free expansion of a gas
- Mixing of two gases
- Heat conduction between reservoirs

## Common Pitfalls
- Using irreversible path in dS = dQ/T
- Forgetting the reservoir entropy contribution

## Related Skills
- stat.mech.boltzmann
- thermo.potentials

## References
- Kittel & Kroemer Ch.3
- Reif Ch.3
