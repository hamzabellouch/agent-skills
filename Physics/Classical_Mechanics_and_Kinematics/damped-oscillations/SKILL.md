---
name: damped-oscillations
description: Damped Oscillations in Mechanics (Oscillations & Waves). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: mech.oscillations.damped
  domain: Mechanics
  subdomain: Oscillations & Waves
  difficulty: 3/5
---

# Damped Oscillations

**ID:** `mech.oscillations.damped`  
**Domain:** Mechanics → Oscillations & Waves  
**Difficulty:** 3/5

## Prerequisites
- mech.oscillations.shm
- math.odes

## Core Concepts
- damping coefficient
- underdamped
- critically damped
- overdamped
- quality factor

## Key Equations
$$
\ddot x + 2\gamma\dot x + \omega_0^2 x = 0
$$
$$
x(t) = A e^{-\gamma t}\cos(\omega_d t + \phi)
$$
$$
\omega_d = \sqrt{\omega_0^2 - \gamma^2}
$$

## Methods
- Classify by comparing \gamma to \omega_0
- Use the damped frequency for underdamped case
- Compute Q for weak damping

## Typical Problem Types
- Oscillator with air resistance
- RLC circuit
- Shock absorber

## Common Pitfalls
- Ignoring damping when it is significant
- Using \omega_0 instead of \omega_d

## Related Skills
- mech.oscillations.driven_resonance
- em.circuits.ac_impedance

## References
- Taylor Ch.5
- Morin Ch.4
