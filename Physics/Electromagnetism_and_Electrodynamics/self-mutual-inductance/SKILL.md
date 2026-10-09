---
name: self-mutual-inductance
description: Self and Mutual Inductance in Electromagnetism (Induction). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: em.induction.inductance
  domain: Electromagnetism
  subdomain: Induction
  difficulty: 4/5
---

# Self and Mutual Inductance

**ID:** `em.induction.inductance`  
**Domain:** Electromagnetism → Induction  
**Difficulty:** 4/5

## Prerequisites
- em.induction.faraday
- em.circuits.rc

## Core Concepts
- inductance
- self-induced EMF
- solenoid inductance
- mutual inductance
- energy in an inductor

## Key Equations
$$
L = \frac{N\Phi}{I}
$$
$$
\mathcal{E} = -L\frac{dI}{dt}
$$
$$
U = \tfrac12 LI^2
$$

## Methods
- Compute L from geometry
- Use Kirchhoff with an inductor
- Analyze RL transients

## Typical Problem Types
- Solenoid inductance
- RL circuit response
- Energy stored in an inductor

## Common Pitfalls
- Treating inductors like resistors in DC steady state
- Forgetting back-EMF direction

## Related Skills
- em.circuits.ac_impedance
- em.maxwell.equations

## References
- Griffiths EM Ch.7
- Halliday-Resnick-Walker Ch.30
