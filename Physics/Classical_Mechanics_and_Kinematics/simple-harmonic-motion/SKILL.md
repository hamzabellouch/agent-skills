---
name: simple-harmonic-motion
description: Simple Harmonic Motion in Mechanics (Oscillations & Waves). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: mech.oscillations.shm
  domain: Mechanics
  subdomain: Oscillations & Waves
  difficulty: 2/5
---

# Simple Harmonic Motion

**ID:** `mech.oscillations.shm`  
**Domain:** Mechanics → Oscillations & Waves  
**Difficulty:** 2/5

## Prerequisites
- mech.dynamics.springs
- math.odes

## Core Concepts
- SHM
- amplitude
- angular frequency
- phase
- small-angle approximation

## Key Equations
$$
\ddot x + \omega^2 x = 0
$$
$$
x(t) = A\cos(\omega t + \phi)
$$
$$
\omega = \sqrt{k/m}
$$

## Methods
- Show that the restoring force is linear in displacement
- Read off \omega, then A and \phi from initial conditions
- Use energy to find speed at a given position

## Typical Problem Types
- Mass-spring
- Simple pendulum (small angle)
- LC circuit analogue

## Common Pitfalls
- Applying SHM when the force is nonlinear
- Forgetting phase from initial conditions

## Related Skills
- mech.oscillations.damped
- mech.oscillations.pendulums

## References
- Kleppner & Kolenkow Ch.7
- Taylor Ch.5
