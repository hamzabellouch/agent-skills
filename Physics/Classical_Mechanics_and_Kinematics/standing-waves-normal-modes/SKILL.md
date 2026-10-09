---
name: standing-waves-normal-modes
description: Standing Waves and Normal Modes in Mechanics (Oscillations & Waves). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: mech.waves.standing
  domain: Mechanics
  subdomain: Oscillations & Waves
  difficulty: 3/5
---

# Standing Waves and Normal Modes

**ID:** `mech.waves.standing`  
**Domain:** Mechanics → Oscillations & Waves  
**Difficulty:** 3/5

## Prerequisites
- mech.waves.superposition

## Core Concepts
- standing wave
- nodes and antinodes
- harmonics
- boundary conditions
- resonance in strings/pipes

## Key Equations
$$
y = 2A\sin(kx)\cos(\omega t)
$$
$$
\lambda_n = \frac{2L}{n}
$$
$$
f_n = \frac{nv}{2L}\ \text{(string fixed at both ends)}
$$

## Methods
- Apply boundary conditions to get allowed wavelengths
- Identify node/antinode pattern
- Use f = v/\lambda

## Typical Problem Types
- Vibrating string
- Open and closed pipes
- Cavity resonances

## Common Pitfalls
- Using the string formula for a pipe (different BCs)
- Forgetting the factor of 2 in \lambda_n

## Related Skills
- mech.waves.superposition
- qm.schrodinger.particle_in_box

## References
- Halliday-Resnick-Walker Ch.17
