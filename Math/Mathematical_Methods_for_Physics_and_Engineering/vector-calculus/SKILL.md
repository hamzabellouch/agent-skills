---
name: vector-calculus
description: Vector Calculus in Mathematics (Calculus). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: math.vector_calculus
  domain: Mathematics
  subdomain: Calculus
  difficulty: 3/5
---

# Vector Calculus

**ID:** `math.vector_calculus`  
**Domain:** Mathematics → Calculus  
**Difficulty:** 3/5

## Prerequisites
- math.calculus.derivatives
- math.vectors.basics

## Core Concepts
- gradient
- divergence
- curl
- Laplacian
- line/surface/volume integrals
- divergence and Stokes theorems

## Key Equations
$$
\nabla f = (\partial_x f, \partial_y f, \partial_z f)
$$
$$
\nabla\cdot\vec F = \partial_x F_x + \partial_y F_y + \partial_z F_z
$$
$$
(\nabla\times\vec F)_i = \epsilon_{ijk}\partial_j F_k
$$

## Methods
- Choose the appropriate operator
- Apply the divergence/Stokes theorem to convert integrals
- Interpret geometrically

## Typical Problem Types
- Computing grad/div/curl of given fields
- Flux through a surface
- Circulation of a field

## Common Pitfalls
- Mixing up divergence and curl
- Wrong orientation for surface normals

## Related Skills
- em.electrostatics.gauss
- mech.energy.conservative_potential

## References
- Boas Ch.6
- Marsden & Tromba Vector Calculus
