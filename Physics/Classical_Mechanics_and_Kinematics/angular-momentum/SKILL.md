---
name: angular-momentum
description: Angular Momentum in Mechanics (Rotation). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: mech.rotation.ang_momentum
  domain: Mechanics
  subdomain: Rotation
  difficulty: 3/5
---

# Angular Momentum

**ID:** `mech.rotation.ang_momentum`  
**Domain:** Mechanics → Rotation  
**Difficulty:** 3/5

## Prerequisites
- mech.rotation.torque_dynamics

## Core Concepts
- angular momentum
- spin
- orbital angular momentum
- angular impulse

## Key Equations
$$
\vec L = \vec r\times\vec p
$$
$$
\vec L = I\vec\omega
$$
$$
\vec\tau = \frac{d\vec L}{dt}
$$

## Methods
- Compute L about a chosen point/axis
- Use L = I\omega for rigid bodies about a principal axis
- Apply angular impulse when torque acts over time

## Typical Problem Types
- Rotating disk
- Particle moving in a straight line (L about a point)
- Spinning skater

## Common Pitfalls
- Mixing the point about which L is computed
- Forgetting that L is a vector

## Related Skills
- mech.rotation.ang_momentum_conservation
- mech.rotation.gyroscope

## References
- Taylor Ch.8
- Kleppner & Kolenkow Ch.6
