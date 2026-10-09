---
name: fermi-dirac-statistics
description: Fermi-Dirac Statistics in Statistical Mechanics (Quantum Statistics). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: stat.mech.fermi_dirac
  domain: Statistical Mechanics
  subdomain: Quantum Statistics
  difficulty: 5/5
---

# Fermi-Dirac Statistics

**ID:** `stat.mech.fermi_dirac`  
**Domain:** Statistical Mechanics → Quantum Statistics  
**Difficulty:** 5/5

## Prerequisites
- stat.mech.partition_function
- qm.many_body.pauli

## Core Concepts
- Fermi energy
- chemical potential
- degenerate electron gas
- Pauli blocking

## Key Equations
$$
\bar n(\epsilon) = \frac{1}{e^{(\epsilon-\mu)/k_BT}+1}
$$
$$
E_F = \frac{\hbar^2}{2m}(3\pi^2 n)^{2/3}
$$

## Methods
- Use the Fermi-Dirac occupation function
- Evaluate the degenerate limit T → 0
- Expand for low-T corrections

## Typical Problem Types
- Electron gas in metals
- White dwarf equation of state
- Semiconductor carrier statistics

## Common Pitfalls
- Using Maxwell-Boltzmann instead of FD
- Forgetting the factor 2 for spin

## Related Skills
- cond.band_theory
- ast.compact_objects

## References
- Kittel & Kroemer Ch.7
- Pathria Ch.8
