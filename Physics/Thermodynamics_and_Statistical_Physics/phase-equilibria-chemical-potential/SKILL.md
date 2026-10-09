---
name: phase-equilibria-chemical-potential
description: Phase Equilibria and Chemical Potential in Thermodynamics (Formalism). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: thermo.phase_equilibria
  domain: Thermodynamics
  subdomain: Formalism
  difficulty: 5/5
---

# Phase Equilibria and Chemical Potential

**ID:** `thermo.phase_equilibria`  
**Domain:** Thermodynamics → Formalism  
**Difficulty:** 5/5

## Prerequisites
- thermo.potentials

## Core Concepts
- chemical potential
- Gibbs phase rule
- coexistence
- Clausius-Clapeyron
- critical exponents

## Key Equations
$$
\mu_i = \left(\frac{\partial G}{\partial N_i}\right)_{T,P}
$$
$$
\mu_{liquid} = \mu_{gas}\ \text{(coexistence)}
$$

## Methods
- Set chemical potentials equal for equilibrium
- Use Gibbs phase rule F = C - P + 2
- Apply Clausius-Clapeyron for coexistence curves

## Typical Problem Types
- Vapor pressure vs temperature
- Binary phase diagrams
- Critical phenomena

## Common Pitfalls
- Confusing chemical potential with Gibbs free energy per particle for mixtures
- Ignoring the phase rule

## Related Skills
- stat.mech.phase_transitions
- thermo.potentials

## References
- Callen Ch.9
- Landau & Lifshitz Statistical Physics
