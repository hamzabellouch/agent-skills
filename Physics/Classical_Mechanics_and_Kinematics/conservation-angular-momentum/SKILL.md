---
name: conservation-angular-momentum
description: Conservation of Angular Momentum in Mechanics (Rotation). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: mech.rotation.ang_momentum_conservation
  domain: Mechanics
  subdomain: Rotation
  difficulty: 3/5
---

# Conservation of Angular Momentum

**ID:** `mech.rotation.ang_momentum_conservation`  
**Domain:** Mechanics → Rotation  
**Difficulty:** 3/5

## Prerequisites
- mech.rotation.ang_momentum

## Core Concepts
- angular momentum conservation
- spin-up
- figure skater
- Kepler's second law

## Key Equations
$$
L = \text{const}\ \text{if}\ \tau_{ext}=0
$$
$$
I_1\omega_1 = I_2\omega_2
$$

## Methods
- Check that external torque is zero about the chosen axis
- Set L_initial = L_final
- Relate I and \omega

## Typical Problem Types
- Skater pulling arms in
- Dust disk landing on a turntable
- Planetary orbits

## Common Pitfalls
- Using it when an external torque is present
- Forgetting to include the new mass distribution

## Related Skills
- mech.gravitation.orbits_kepler
- mech.rotation.ang_momentum

## References
- Halliday-Resnick-Walker Ch.11
