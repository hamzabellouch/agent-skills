---
name: finite-difference-finite-element-methods-pdes
description: Finite Difference and Finite Element Methods for PDEs in Computational Physics (Numerical Methods). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: comp.pde_finite
  domain: Computational Physics
  subdomain: Numerical Methods
  difficulty: 4/5
---

# Finite Difference and Finite Element Methods for PDEs

**ID:** `comp.pde_finite`  
**Domain:** Computational Physics → Numerical Methods  
**Difficulty:** 4/5

## Prerequisites
- math.pdes
- math.numerical_methods

## Core Concepts
- finite difference
- finite element
- stability
- CFL condition
- boundary conditions

## Key Equations
$$
\frac{\partial u}{\partial t} = D\frac{\partial^2 u}{\partial x^2} \Rightarrow \frac{u_i^{n+1}-u_i^n}{\Delta t} = D\frac{u_{i+1}^n - 2u_i^n + u_{i-1}^n}{\Delta x^2}
$$

## Methods
- Discretize the PDE on a grid
- Choose explicit or implicit time stepping
- Enforce boundary/initial conditions

## Typical Problem Types
- Heat equation
- Wave equation
- Schrödinger equation (split-step)

## Common Pitfalls
- Violating CFL condition
- Using too coarse a grid for the wavelength

## Related Skills
- comp.numerical_integration
- mech.fluid.reynolds

## References
- LeVeque Finite Difference Methods
- Strang & Fix
