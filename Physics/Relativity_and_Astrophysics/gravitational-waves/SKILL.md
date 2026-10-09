---
name: gravitational-waves
description: Gravitational Waves in Relativity (General). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: rel.general.gravitational_waves
  domain: Relativity
  subdomain: General
  difficulty: 5/5
---

# Gravitational Waves

**ID:** `rel.general.gravitational_waves`  
**Domain:** Relativity → General  
**Difficulty:** 5/5

## Prerequisites
- rel.general.geodesics

## Core Concepts
- linearized gravity
- quadrupole radiation
- strain h
- LIGO detection
- chirp

## Key Equations
$$
h \sim \frac{2G}{c^4 r}\ddot{Q}
$$
$$
P = \frac{32}{5}\frac{G^4}{c^5}\frac{m_1^2 m_2^2(m_1+m_2)}{a^5}
$$

## Methods
- Linearize the field equations around flat space
- Compute the quadrupole moment's time derivatives
- Estimate strain at a detector

## Typical Problem Types
- Strain from a binary merger
- Chirp mass extraction
- Energy loss of a binary orbit

## Common Pitfalls
- Forgetting the 1/r falloff
- Using monopole/dipole radiation

## Related Skills
- rel.general.schwarzschild
- ast.compact_objects

## References
- Carroll Ch.7
- Maggiore Gravitational Waves
