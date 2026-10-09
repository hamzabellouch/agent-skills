---
name: coupled-oscillators-normal-modes
description: Coupled Oscillators and Normal Modes in Mechanics (Oscillations & Waves). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: mech.oscillations.coupled_normal_modes
  domain: Mechanics
  subdomain: Oscillations & Waves
  difficulty: 4/5
---

# Coupled Oscillators and Normal Modes

**ID:** `mech.oscillations.coupled_normal_modes`  
**Domain:** Mechanics → Oscillations & Waves  
**Difficulty:** 4/5

## Prerequisites
- mech.oscillations.shm
- math.linear_algebra

## Core Concepts
- normal modes
- eigenfrequencies
- coupling
- beats
- mode shapes

## Key Equations
$$
M\ddot{\vec x} + K\vec x = 0
$$
$$
\det(K - \omega^2 M) = 0
$$

## Methods
- Write equations of motion in matrix form
- Solve the eigenvalue problem
- Superpose modes with initial conditions

## Typical Problem Types
- Two coupled pendulums
- Masses connected by springs
- Molecular vibrations

## Common Pitfalls
- Assuming independent oscillators
- Forgetting to use both modes in the general solution

## Related Skills
- mech.waves.standing
- qm.schrodinger.harmonic_oscillator

## References
- Taylor Ch.11
- Goldstein Ch.6
