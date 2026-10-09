---
name: maxwell-boltzmann-distribution
description: Maxwell-Boltzmann Distribution in Thermodynamics (Kinetic Theory). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: thermo.maxwell_boltzmann
  domain: Thermodynamics
  subdomain: Kinetic Theory
  difficulty: 4/5
---

# Maxwell-Boltzmann Distribution

**ID:** `thermo.maxwell_boltzmann`  
**Domain:** Thermodynamics → Kinetic Theory  
**Difficulty:** 4/5

## Prerequisites
- thermo.kinetic_theory
- stat.mech.boltzmann

## Core Concepts
- speed distribution
- most probable speed
- mean speed
- rms speed
- distribution function

## Key Equations
$$
f(v) = 4\pi n\left(\frac{m}{2\pi k_B T}\right)^{3/2} v^2 e^{-mv^2/2k_BT}
$$
$$
v_p = \sqrt{\frac{2k_BT}{m}}
$$
$$
\bar v = \sqrt{\frac{8k_BT}{\pi m}}
$$

## Methods
- Derive from Boltzmann factor and density of states
- Compute average quantities via integrals
- Compare v_p, ar v, v_{rms}

## Typical Problem Types
- Fraction of molecules above a speed
- Effusion rates
- Reaction rates in gases

## Common Pitfalls
- Confusing the three characteristic speeds
- Forgetting the v^2 factor in the distribution

## Related Skills
- stat.mech.boltzmann
- thermo.kinetic_theory

## References
- Reif Ch.7
- Kittel & Kroemer Ch.6
