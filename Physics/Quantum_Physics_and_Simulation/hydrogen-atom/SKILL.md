---
name: hydrogen-atom
description: Hydrogen Atom (Full Quantum Treatment) in Quantum Mechanics (Formalism). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: qm.formalism.hydrogen_atom
  domain: Quantum Mechanics
  subdomain: Formalism
  difficulty: 5/5
---

# Hydrogen Atom (Full Quantum Treatment)

**ID:** `qm.formalism.hydrogen_atom`  
**Domain:** Quantum Mechanics → Formalism  
**Difficulty:** 5/5

## Prerequisites
- qm.formalism.operators
- qm.formalism.angular_momentum

## Core Concepts
- spherical harmonics
- radial wavefunctions
- quantum numbers n, l, m
- degeneracy
- selection rules

## Key Equations
$$
\psi_{nlm} = R_{nl}(r)Y_l^m(\theta,\phi)
$$
$$
E_n = -\frac{13.6\ \text{eV}}{n^2}
$$

## Methods
- Separate the TISE in spherical coordinates
- Solve the radial equation for R_{nl}
- Apply angular momentum eigenstates

## Typical Problem Types
- Orbital shapes and degeneracies
- Expectation values of r
- Transition selection rules

## Common Pitfalls
- Confusing n, l, m ranges
- Forgetting l ≤ n−1

## Related Skills
- qm.formalism.angular_momentum
- qm.approx.perturbation_td

## References
- Griffiths QM Ch.4
- Sakurai Ch.3
