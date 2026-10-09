---
name: wave-equation-traveling-waves
description: The Wave Equation and Traveling Waves in Mechanics (Oscillations & Waves). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: mech.waves.wave_equation
  domain: Mechanics
  subdomain: Oscillations & Waves
  difficulty: 3/5
---

# The Wave Equation and Traveling Waves

**ID:** `mech.waves.wave_equation`  
**Domain:** Mechanics → Oscillations & Waves  
**Difficulty:** 3/5

## Prerequisites
- mech.oscillations.shm
- math.pdes

## Core Concepts
- wave equation
- wave speed
- traveling wave
- transverse vs longitudinal
- phase velocity

## Key Equations
$$
\frac{\partial^2 y}{\partial x^2} = \frac{1}{v^2}\frac{\partial^2 y}{\partial t^2}
$$
$$
y(x,t) = f(x \mp vt)
$$
$$
v = \sqrt{T/\mu}\ \text{(string)}
$$

## Methods
- Verify that f(x-vt) solves the wave equation
- Use boundary conditions to fix the form
- Compute v from medium properties

## Typical Problem Types
- String waves
- Sound waves
- Wave speed from tension and density

## Common Pitfalls
- Confusing phase velocity with particle velocity
- Mixing signs for direction of propagation

## Related Skills
- mech.waves.superposition
- em.waves.em_waves

## References
- Morin Ch.4
- Halliday-Resnick-Walker Ch.16
