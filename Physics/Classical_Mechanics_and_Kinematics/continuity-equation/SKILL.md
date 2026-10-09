---
name: continuity-equation
description: Continuity Equation in Mechanics (Fluids). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: mech.fluids.continuity
  domain: Mechanics
  subdomain: Fluids
  difficulty: 2/5
---

# Continuity Equation

**ID:** `mech.fluids.continuity`  
**Domain:** Mechanics → Fluids  
**Difficulty:** 2/5

## Prerequisites
- mech.fluids.statics

## Core Concepts
- mass conservation
- flow rate
- incompressible flow
- cross-sectional area

## Key Equations
$$
A_1 v_1 = A_2 v_2
$$
$$
\nabla\cdot\vec v = 0\ \text{(incompressible)}
$$

## Methods
- Apply mass conservation between two sections
- Assume incompressible if density is constant
- Combine with Bernoulli when pressure matters

## Typical Problem Types
- Flow through a narrowing pipe
- Blood flow in arteries
- Water from a tap

## Common Pitfalls
- Forgetting that flow rate is conserved, not velocity
- Applying to compressible flow

## Related Skills
- mech.fluids.bernoulli
- mech.fluids.viscosity

## References
- Halliday-Resnick-Walker Ch.14
