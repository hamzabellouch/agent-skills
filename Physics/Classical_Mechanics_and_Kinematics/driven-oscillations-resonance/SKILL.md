---
name: driven-oscillations-resonance
description: Driven Oscillations and Resonance in Mechanics (Oscillations & Waves). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: mech.oscillations.driven_resonance
  domain: Mechanics
  subdomain: Oscillations & Waves
  difficulty: 4/5
---

# Driven Oscillations and Resonance

**ID:** `mech.oscillations.driven_resonance`  
**Domain:** Mechanics → Oscillations & Waves  
**Difficulty:** 4/5

## Prerequisites
- mech.oscillations.damped

## Core Concepts
- driving frequency
- resonance
- amplitude response
- phase lag
- steady state

## Key Equations
$$
\ddot x + 2\gamma\dot x + \omega_0^2 x = F_0\cos(\omega t)/m
$$
$$
A(\omega) = \frac{F_0/m}{\sqrt{(\omega_0^2-\omega^2)^2 + (2\gamma\omega)^2}}
$$

## Methods
- Solve for the steady-state particular solution
- Analyze A(\omega) near resonance
- Include the transient if initial conditions matter

## Typical Problem Types
- Resonance in a driven pendulum
- Tacoma Narrows analogy
- RLC resonance

## Common Pitfalls
- Forgetting the transient term
- Assuming resonance is always at \omega_0 (it shifts with damping)

## Related Skills
- mech.oscillations.damped
- mech.waves.wave_equation

## References
- Taylor Ch.5
- Feynman Vol. I Ch.23
