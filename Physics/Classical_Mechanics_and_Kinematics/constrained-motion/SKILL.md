---
name: constrained-motion
description: Constrained Motion (Pulleys, Ropes, Wedges) in Mechanics (Kinematics). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: mech.kinematics.constraints
  domain: Mechanics
  subdomain: Kinematics
  difficulty: 3/5
---

# Constrained Motion (Pulleys, Ropes, Wedges)

**ID:** `mech.kinematics.constraints`  
**Domain:** Mechanics → Kinematics  
**Difficulty:** 3/5

## Prerequisites
- mech.kinematics.definitions
- mech.dynamics.pulleys

## Core Concepts
- constraint equations
- inextensible string
- virtual work
- degrees of freedom

## Key Equations
$$
\sum_i \vec F_i \cdot \delta\vec r_i = 0
$$
$$
L = \text{const} \Rightarrow \dot L = 0
$$

## Methods
- Write the length constraint of the string
- Differentiate to relate accelerations
- Use the number of DOF to decide independent coordinates

## Typical Problem Types
- Atwood machine with moving pulley
- Two blocks connected over a wedge
- Block sliding on a moving wedge

## Common Pitfalls
- Assuming both blocks have equal acceleration without checking the constraint
- Ignoring the constraint direction

## Related Skills
- mech.dynamics.pulleys
- math.variational_lagrange

## References
- Kleppner & Kolenkow Ch.2
- Morin Ch.3
