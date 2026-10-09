---
name: amp-re-s-law
description: Ampère's Law in Electromagnetism (Magnetostatics). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: em.magnetostatics.ampere
  domain: Electromagnetism
  subdomain: Magnetostatics
  difficulty: 4/5
---

# Ampère's Law

**ID:** `em.magnetostatics.ampere`  
**Domain:** Electromagnetism → Magnetostatics  
**Difficulty:** 4/5

## Prerequisites
- em.magnetostatics.biot_savart
- em.electrostatics.gauss

## Core Concepts
- Ampère's law
- Amperian loop
- enclosed current
- symmetry
- solenoid field

## Key Equations
$$
\oint \vec B\cdot d\vec l = \mu_0 I_{enc}
$$
$$
\nabla\times\vec B = \mu_0\vec J\ \text{(static)}
$$

## Methods
- Choose an Amperian loop matching the symmetry
- Compute the enclosed current
- Exploit translational/rotational symmetry

## Typical Problem Types
- Field inside a solenoid
- Field of a coaxial cable
- Field of a toroid

## Common Pitfalls
- Using Ampère's law without symmetry
- Forgetting that only enclosed current contributes

## Related Skills
- em.maxwell.equations
- em.induction.faraday

## References
- Griffiths EM Ch.5
- Purcell Ch.5
