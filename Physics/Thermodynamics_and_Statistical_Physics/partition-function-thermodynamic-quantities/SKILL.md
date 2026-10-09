---
name: partition-function-thermodynamic-quantities
description: Partition Function and Thermodynamic Quantities in Statistical Mechanics (Foundations). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: stat.mech.partition_function
  domain: Statistical Mechanics
  subdomain: Foundations
  difficulty: 5/5
---

# Partition Function and Thermodynamic Quantities

**ID:** `stat.mech.partition_function`  
**Domain:** Statistical Mechanics → Foundations  
**Difficulty:** 5/5

## Prerequisites
- stat.mech.boltzmann
- thermo.potentials

## Core Concepts
- partition function
- free energy from Z
- classical limit
- density of states

## Key Equations
$$
F = -k_BT\ln Z
$$
$$
U = -\frac{\partial\ln Z}{\partial\beta}
$$
$$
S = k_B\ln Z + \frac{U}{T}
$$

## Methods
- Compute Z for a system
- Derive thermodynamic quantities via derivatives
- Take classical limit (large T, low density)

## Typical Problem Types
- Ideal gas thermodynamics from Z
- Vibrational and rotational partition functions
- Adsorption isotherms

## Common Pitfalls
- Using the wrong ensemble's Z
- Forgetting the N! for indistinguishable particles

## Related Skills
- stat.mech.fermi_dirac
- stat.mech.bose_einstein

## References
- Pathria Ch.3
- Reif Ch.6-7
