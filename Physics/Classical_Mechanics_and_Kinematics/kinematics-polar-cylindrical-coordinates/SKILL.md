---
name: kinematics-polar-cylindrical-coordinates
description: Kinematics in Polar and Cylindrical Coordinates in Mechanics (Kinematics). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: mech.kinematics.curvilinear_coordinates
  domain: Mechanics
  subdomain: Kinematics
  difficulty: 3/5
---

# Kinematics in Polar and Cylindrical Coordinates

**ID:** `mech.kinematics.curvilinear_coordinates`  
**Domain:** Mechanics → Kinematics  
**Difficulty:** 3/5

## Prerequisites
- mech.kinematics.definitions
- math.vector_calculus

## Core Concepts
- radial and tangential unit vectors
- polar basis
- centripetal term
- Coriolis term
- coordinate basis change

## Key Equations
$$
\vec v = \dot r\,\hat r + r\dot\theta\,\hat\theta
$$
$$
\vec a = (\ddot r - r\dot\theta^2)\hat r + (r\ddot\theta + 2\dot r\dot\theta)\hat\theta
$$

## Methods
- Express position in polar basis, then differentiate
- Identify radial and transverse components
- Use cylindrical/spherical symmetry when appropriate

## Typical Problem Types
- Particle on a rotating arm
- Spiral trajectory
- Central force motion

## Common Pitfalls
- Differentiating unit vectors as if constant
- Dropping the 2\dot r\dot	heta Coriolis term

## Related Skills
- mech.dynamics.noninertial
- mech.gravitation.field_potential

## References
- Goldstein Ch.1
- Taylor Classical Mechanics Ch.1
