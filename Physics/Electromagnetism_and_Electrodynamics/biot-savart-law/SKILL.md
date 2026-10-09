---
name: biot-savart-law
description: Biot-Savart Law in Electromagnetism (Magnetostatics). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: em.magnetostatics.biot_savart
  domain: Electromagnetism
  subdomain: Magnetostatics
  difficulty: 4/5
---

# Biot-Savart Law

**ID:** `em.magnetostatics.biot_savart`  
**Domain:** Electromagnetism → Magnetostatics  
**Difficulty:** 4/5

## Prerequisites
- em.magnetostatics.force
- math.vector_calculus

## Core Concepts
- Biot-Savart law
- magnetic field of a current element
- superposition
- field of a loop/wire

## Key Equations
$$
d\vec B = \frac{\mu_0 I}{4\pi}\frac{d\vec l\times\hat r}{r^2}
$$

## Methods
- Set up the integral over the current path
- Use symmetry to reduce the integral
- Evaluate for standard geometries

## Typical Problem Types
- Field of a straight wire
- Field on the axis of a loop
- Field of a solenoid

## Common Pitfalls
- Direction errors from cross product
- Forgetting the geometry factor

## Related Skills
- em.magnetostatics.ampere
- em.maxwell.equations

## References
- Griffiths EM Ch.5
- Purcell Ch.5
