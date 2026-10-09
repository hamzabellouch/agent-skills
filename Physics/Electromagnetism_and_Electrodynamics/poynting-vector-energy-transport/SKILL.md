---
name: poynting-vector-energy-transport
description: Poynting Vector and Energy Transport in Electromagnetism (Waves). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: em.waves.poynting
  domain: Electromagnetism
  subdomain: Waves
  difficulty: 4/5
---

# Poynting Vector and Energy Transport

**ID:** `em.waves.poynting`  
**Domain:** Electromagnetism → Waves  
**Difficulty:** 4/5

## Prerequisites
- em.waves.em_waves

## Core Concepts
- Poynting vector
- intensity
- radiation pressure
- energy flux

## Key Equations
$$
\vec S = \frac{1}{\mu_0}\vec E\times\vec B
$$
$$
I = \langle S\rangle
$$
$$
P_{rad} = I/c\ \text{(absorbing)}
$$

## Methods
- Compute ec S for a given wave
- Time-average for intensity
- Use radiation pressure for momentum transfer

## Typical Problem Types
- Intensity of an EM wave
- Radiation pressure on a solar sail
- Laser intensity

## Common Pitfalls
- Forgetting the time average for intensity
- Using 2I/c vs I/c for reflecting vs absorbing

## Related Skills
- em.radiation.accelerating_charges
- optics.modern.coherence_lasers

## References
- Griffiths EM Ch.9
- Jackson Ch.7
