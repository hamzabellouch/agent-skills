---
name: projectile-motion
description: Projectile Motion in Mechanics (Kinematics). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: mech.kinematics.projectile
  domain: Mechanics
  subdomain: Kinematics
  difficulty: 2/5
---

# Projectile Motion

**ID:** `mech.kinematics.projectile`  
**Domain:** Mechanics → Kinematics  
**Difficulty:** 2/5

## Prerequisites
- mech.kinematics.constant_acceleration

## Core Concepts
- independence of axes
- range
- max height
- time of flight
- launch angle
- parabolic trajectory

## Key Equations
$$
x = v_0\cos\theta\, t
$$
$$
y = v_0\sin\theta\, t - \tfrac12 g t^2
$$
$$
R = \frac{v_0^2 \sin 2\theta}{g}
$$
$$
H = \frac{v_0^2\sin^2\theta}{2g}
$$

## Methods
- Decompose velocity into horizontal and vertical components
- Treat axes independently; only y has acceleration
- Use energy conservation for speed at a given height

## Typical Problem Types
- Find range/height/time
- Hit a target at distance d
- Projectile from a cliff or moving platform

## Common Pitfalls
- Applying suvat to the horizontal axis
- Ignoring launch height
- Assuming symmetric trajectory when launch and landing heights differ

## Related Skills
- mech.kinematics.relative
- mech.energy.conservation

## References
- Kleppner & Kolenkow Ch.1
- Irodov 1.1-1.30
