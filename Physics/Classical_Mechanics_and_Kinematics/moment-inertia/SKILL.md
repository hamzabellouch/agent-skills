---
name: moment-inertia
description: Moment of Inertia in Mechanics (Rotation). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: mech.rotation.moment_of_inertia
  domain: Mechanics
  subdomain: Rotation
  difficulty: 3/5
---

# Moment of Inertia

**ID:** `mech.rotation.moment_of_inertia`  
**Domain:** Mechanics → Rotation  
**Difficulty:** 3/5

## Prerequisites
- mech.rotation.angular_kinematics

## Core Concepts
- moment of inertia
- rotational inertia
- continuous bodies
- standard shapes

## Key Equations
$$
I = \sum m_i r_i^2
$$
$$
I = \int r^2\,dm
$$
$$
I_{disk} = \tfrac12 MR^2
$$
$$
I_{sphere} = \tfrac25 MR^2
$$

## Methods
- Choose the axis
- Integrate r^2 dm using symmetry
- Use standard results for common shapes

## Typical Problem Types
- I for a rod, disk, sphere, hoop
- Composite bodies

## Common Pitfalls
- Using I about the wrong axis
- Forgetting that I depends on mass distribution

## Related Skills
- mech.rotation.parallel_axis
- mech.rotation.rot_energy

## References
- Serway Ch.10
- Kleppner & Kolenkow Ch.6
