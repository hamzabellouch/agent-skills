---
name: non-inertial-frames-pseudo-forces
description: Non-Inertial Frames and Pseudo-Forces in Mechanics (Dynamics). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: mech.dynamics.noninertial
  domain: Mechanics
  subdomain: Dynamics
  difficulty: 4/5
---

# Non-Inertial Frames and Pseudo-Forces

**ID:** `mech.dynamics.noninertial`  
**Domain:** Mechanics → Dynamics  
**Difficulty:** 4/5

## Prerequisites
- mech.kinematics.relative
- mech.dynamics.newton_laws

## Core Concepts
- accelerating frame
- fictitious force
- centrifugal force
- Coriolis force
- Euler force

## Key Equations
$$
\vec F_{eff} = \vec F_{real} - m\vec a_{frame}
$$
$$
\vec F_{Cor} = -2m\,\vec\omega\times\vec v'
$$
$$
\vec F_{cent} = -m\,\vec\omega\times(\vec\omega\times\vec r')
$$

## Methods
- Add pseudo-forces when working in an accelerating frame
- Choose between inertial and non-inertial description

## Typical Problem Types
- Rotating platform
- Weather patterns and Coriolis
- Accelerating elevator

## Common Pitfalls
- Treating pseudo-forces as real interactions
- Forgetting the Coriolis term for rotating frames

## Related Skills
- mech.rotation.gyroscope
- mech.fluid.reynolds

## References
- Goldstein Ch.4
- Taylor Ch.9
