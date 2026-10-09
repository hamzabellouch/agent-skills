---
name: time-independent-perturbation-theory
description: Time-Independent Perturbation Theory in Quantum Mechanics (Approximations). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: qm.approx.perturbation_ti
  domain: Quantum Mechanics
  subdomain: Approximations
  difficulty: 5/5
---

# Time-Independent Perturbation Theory

**ID:** `qm.approx.perturbation_ti`  
**Domain:** Quantum Mechanics → Approximations  
**Difficulty:** 5/5

## Prerequisites
- qm.formalism.operators

## Core Concepts
- non-degenerate PT
- degenerate PT
- first/second-order corrections
- matrix elements

## Key Equations
$$
E_n^{(1)} = \langle n^{(0)}|H'|n^{(0)}\rangle
$$
$$
E_n^{(2)} = \sum_{m\ne n}\frac{|\langle m^{(0)}|H'|n^{(0)}\rangle|^2}{E_n^{(0)}-E_m^{(0)}}
$$

## Methods
- Compute matrix elements of H' in the unperturbed basis
- Decide whether degeneracy requires special treatment
- Sum over intermediate states

## Typical Problem Types
- Stark effect in hydrogen
- Anharmonic oscillator
- Fine structure

## Common Pitfalls
- Dividing by zero energy denominators (degenerate case)
- Using only first order when it vanishes

## Related Skills
- qm.approx.variational
- qm.approx.perturbation_td

## References
- Griffiths QM Ch.6
- Sakurai Ch.5
