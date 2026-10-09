---
name: schr-dinger-equation-wavefunctions
description: The Schrödinger Equation and Wavefunctions in Quantum Mechanics (Schrödinger). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: qm.schrodinger.wavefunction
  domain: Quantum Mechanics
  subdomain: Schrödinger
  difficulty: 3/5
---

# The Schrödinger Equation and Wavefunctions

**ID:** `qm.schrodinger.wavefunction`  
**Domain:** Quantum Mechanics → Schrödinger  
**Difficulty:** 3/5

## Prerequisites
- qm.found.de_broglie
- math.pdes

## Core Concepts
- wavefunction
- probability density
- normalization
- time-dependent vs time-independent
- boundary conditions

## Key Equations
$$
i\hbar\frac{\partial\psi}{\partial t} = -\frac{\hbar^2}{2m}\nabla^2\psi + V\psi
$$
$$
\int|\psi|^2 d^3r = 1
$$

## Methods
- Separate variables for time-independent problems
- Apply boundary conditions and continuity
- Normalize the wavefunction

## Typical Problem Types
- Particle in a box
- Infinite well
- Free particle

## Common Pitfalls
- Forgetting continuity of \psi and \psi'
- Non-normalizable trial functions

## Related Skills
- qm.schrodinger.particle_in_box
- qm.formalism.operators

## References
- Griffiths QM Ch.1-2
