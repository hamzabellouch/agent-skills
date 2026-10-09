---
name: partial-differential-equations
description: Partial Differential Equations in Mathematics (Differential Equations). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: math.pdes
  domain: Mathematics
  subdomain: Differential Equations
  difficulty: 4/5
---

# Partial Differential Equations

**ID:** `math.pdes`  
**Domain:** Mathematics → Differential Equations  
**Difficulty:** 4/5

## Prerequisites
- math.odes
- math.vector_calculus

## Core Concepts
- classification (elliptic/parabolic/hyperbolic)
- separation of variables
- Fourier methods
- boundary/initial conditions

## Key Equations
$$
u_t = \alpha u_{xx}\ \text{(heat)}
$$
$$
u_{tt} = c^2 u_{xx}\ \text{(wave)}
$$
$$
\nabla^2 u = 0\ \text{(Laplace)}
$$

## Methods
- Classify the equation
- Use separation of variables
- Apply BCs and ICs
- Represent as Fourier series

## Typical Problem Types
- Heat, wave, Laplace equations
- Schrödinger equation
- Electrostatics with boundaries

## Common Pitfalls
- Wrong BC count for the equation type
- Ignoring compatibility conditions

## Related Skills
- mech.waves.wave_equation
- comp.pde_finite

## References
- Haberman Applied PDEs
- Strauss PDEs
