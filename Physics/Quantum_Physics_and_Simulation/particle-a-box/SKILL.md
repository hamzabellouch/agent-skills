---
name: particle-a-box
description: Particle in a Box in Quantum Mechanics (Schrödinger). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: qm.schrodinger.particle_in_box
  domain: Quantum Mechanics
  subdomain: Schrödinger
  difficulty: 3/5
---

# Particle in a Box

**ID:** `qm.schrodinger.particle_in_box`  
**Domain:** Quantum Mechanics → Schrödinger  
**Difficulty:** 3/5

## Prerequisites
- qm.schrodinger.wavefunction

## Core Concepts
- infinite well
- quantized energies
- nodes
- orthogonality
- expectation values

## Key Equations
$$
\psi_n(x) = \sqrt{\frac{2}{L}}\sin\!\left(\frac{n\pi x}{L}\right)
$$
$$
E_n = \frac{n^2\pi^2\hbar^2}{2mL^2}
$$

## Methods
- Solve the TISE with hard-wall boundary conditions
- Quantize n via the boundary conditions
- Compute expectation values

## Typical Problem Types
- Energy levels of a quantum well
- Probability of finding particle in a region
- 3D box degeneracies

## Common Pitfalls
- Forgetting the boundary conditions
- Off-by-one in the quantum number

## Related Skills
- qm.schrodinger.finite_well
- mech.waves.standing

## References
- Griffiths QM Ch.2
