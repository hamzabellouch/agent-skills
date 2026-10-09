---
name: molecular-dynamics
description: Molecular Dynamics in Computational Physics (Simulation). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: comp.molecular_dynamics
  domain: Computational Physics
  subdomain: Simulation
  difficulty: 4/5
---

# Molecular Dynamics

**ID:** `comp.molecular_dynamics`  
**Domain:** Computational Physics → Simulation  
**Difficulty:** 4/5

## Prerequisites
- comp.numerical_integration
- stat.mech.boltzmann

## Core Concepts
- force fields
- Verlet integration
- thermostats
- periodic boundaries
- radial distribution function

## Key Equations
$$
\vec F_i = -\nabla_i U
$$
$$
\vec r_i(t+\Delta t) = 2\vec r_i(t) - \vec r_i(t-\Delta t) + \frac{\vec F_i}{m}\Delta t^2
$$

## Methods
- Build a system with periodic boundaries
- Integrate with velocity Verlet
- Couple to a thermostat/barostat

## Typical Problem Types
- Liquid argon simulation
- Protein folding (conceptual)
- Phase diagram computation

## Common Pitfalls
- Too-large time step causing instability
- Ignoring long-range electrostatics

## Related Skills
- comp.monte_carlo
- stat.mech.fluctuations

## References
- Frenkel & Smit Understanding Molecular Simulation
