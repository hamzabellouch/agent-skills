---
name: gauss-s-law
description: Gauss's Law in Electromagnetism (Electrostatics). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: em.electrostatics.gauss
  domain: Electromagnetism
  subdomain: Electrostatics
  difficulty: 3/5
---

# Gauss's Law

**ID:** `em.electrostatics.gauss`  
**Domain:** Electromagnetism → Electrostatics  
**Difficulty:** 3/5

## Prerequisites
- em.electrostatics.field
- math.vector_calculus

## Core Concepts
- electric flux
- Gaussian surface
- enclosed charge
- symmetry arguments

## Key Equations
$$
\oint \vec E\cdot d\vec A = \frac{Q_{enc}}{\epsilon_0}
$$
$$
\nabla\cdot\vec E = \frac{\rho}{\epsilon_0}
$$

## Methods
- Choose a Gaussian surface matching the symmetry
- Compute enclosed charge
- Exploit planar, cylindrical, or spherical symmetry

## Typical Problem Types
- E of a charged sphere
- E of an infinite sheet
- E of a line charge

## Common Pitfalls
- Using Gauss's law without symmetry
- Forgetting that only enclosed charge counts

## Related Skills
- em.maxwell.equations
- em.electrostatics.potential

## References
- Griffiths EM Ch.2
- Purcell Ch.1
