---
name: heat-transfer-conduction-convection-radiation
description: Heat Transfer: Conduction, Convection, Radiation in Thermodynamics (Heat Transfer). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: thermo.heat_transfer
  domain: Thermodynamics
  subdomain: Heat Transfer
  difficulty: 3/5
---

# Heat Transfer: Conduction, Convection, Radiation

**ID:** `thermo.heat_transfer`  
**Domain:** Thermodynamics → Heat Transfer  
**Difficulty:** 3/5

## Prerequisites
- thermo.first_law

## Core Concepts
- thermal conductivity
- Fourier's law
- Newton cooling
- Stefan-Boltzmann
- emissivity

## Key Equations
$$
\frac{dQ}{dt} = -kA\frac{dT}{dx}
$$
$$
\frac{dQ}{dt} = hA(T_s - T_\infty)
$$
$$
\frac{dQ}{dt} = \epsilon\sigma A T^4
$$

## Methods
- Identify the dominant transfer mode
- Use steady-state flux for layered walls
- Combine modes when they act in parallel/series

## Typical Problem Types
- Heat through a composite wall
- Cooling of a hot object
- Solar constant and Earth temperature

## Common Pitfalls
- Forgetting emissivity for real surfaces
- Mixing steady-state and transient problems

## Related Skills
- stat.mech.boltzmann
- ast.stellar_structure

## References
- Incropera & DeWitt
- Halliday-Resnick-Walker Ch.18
