---
name: maxwell-s-equations
description: Maxwell's Equations in Electromagnetism (Foundations). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: em.maxwell.equations
  domain: Electromagnetism
  subdomain: Foundations
  difficulty: 5/5
---

# Maxwell's Equations

**ID:** `em.maxwell.equations`  
**Domain:** Electromagnetism → Foundations  
**Difficulty:** 5/5

## Prerequisites
- em.electrostatics.gauss
- em.magnetostatics.ampere
- em.induction.faraday

## Core Concepts
- displacement current
- unification
- wave equation origin
- differential vs integral form

## Key Equations
$$
\nabla\cdot\vec E = \frac{\rho}{\epsilon_0}
$$
$$
\nabla\cdot\vec B = 0
$$
$$
\nabla\times\vec E = -\frac{\partial \vec B}{\partial t}
$$
$$
\nabla\times\vec B = \mu_0\vec J + \mu_0\epsilon_0\frac{\partial \vec E}{\partial t}
$$

## Methods
- Choose integral or differential form based on symmetry
- Use displacement current for time-varying fields
- Derive the wave equation in vacuum

## Typical Problem Types
- Deriving the speed of light
- Boundary conditions at interfaces
- Waveguides

## Common Pitfalls
- Forgetting the displacement current
- Using static forms for time-varying fields

## Related Skills
- em.waves.em_waves
- rel.special.lorentz

## References
- Griffiths EM Ch.7
- Jackson Ch.6
