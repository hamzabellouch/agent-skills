---
name: thermodynamic-potentials
description: Thermodynamic Potentials in Thermodynamics (Formalism). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: thermo.potentials
  domain: Thermodynamics
  subdomain: Formalism
  difficulty: 4/5
---

# Thermodynamic Potentials

**ID:** `thermo.potentials`  
**Domain:** Thermodynamics → Formalism  
**Difficulty:** 4/5

## Prerequisites
- thermo.entropy

## Core Concepts
- Helmholtz free energy
- Gibbs free energy
- enthalpy
- Maxwell relations
- Legendre transform

## Key Equations
$$
F = U - TS
$$
$$
G = H - TS = U - TS + PV
$$
$$
H = U + PV
$$
$$
dF = -S\,dT - P\,dV
$$

## Methods
- Choose the potential whose natural variables match the constraints
- Use Maxwell relations to swap derivatives
- Use Gibbs for phase equilibrium

## Typical Problem Types
- Free energy change in reactions
- Work from a thermodynamic system
- Phase equilibria

## Common Pitfalls
- Using U when T or P is the controlled variable
- Sign errors in Legendre transforms

## Related Skills
- thermo.phase_equilibria
- stat.mech.partition_function

## References
- Callen Thermodynamics
- Kittel & Kroemer Ch.5
