---
name: calculus-variations-lagrangian-mechanics
description: Calculus of Variations and Lagrangian Mechanics in Mathematics (Analytical Mechanics). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: math.variational_lagrange
  domain: Mathematics
  subdomain: Analytical Mechanics
  difficulty: 4/5
---

# Calculus of Variations and Lagrangian Mechanics

**ID:** `math.variational_lagrange`  
**Domain:** Mathematics → Analytical Mechanics  
**Difficulty:** 4/5

## Prerequisites
- math.odes
- math.vector_calculus

## Core Concepts
- functional
- Euler-Lagrange equation
- action principle
- constraints
- generalized coordinates

## Key Equations
$$
S = \int L(q,\dot q,t)\, dt
$$
$$
\frac{d}{dt}\frac{\partial L}{\partial\dot q_i} - \frac{\partial L}{\partial q_i} = 0
$$

## Methods
- Write the Lagrangian in generalized coordinates
- Apply the Euler-Lagrange equations
- Include constraints via multipliers

## Typical Problem Types
- Simple pendulum via Lagrangian
- Double pendulum
- Geodesics as shortest paths

## Common Pitfalls
- Forgetting velocity dependence of kinetic energy
- Wrong sign in potential term

## Related Skills
- mech.kinematics.constraints
- math.tensor_calculus

## References
- Goldstein Ch.2
- Landau & Lifshitz Mechanics
