---
name: numerical-methods-odes-pdes
description: Numerical Methods for ODEs/PDEs in Mathematics (Numerical Analysis). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: math.numerical_methods
  domain: Mathematics
  subdomain: Numerical Analysis
  difficulty: 3/5
---

# Numerical Methods for ODEs/PDEs

**ID:** `math.numerical_methods`  
**Domain:** Mathematics → Numerical Analysis  
**Difficulty:** 3/5

## Prerequisites
- math.odes
- math.linear_algebra

## Core Concepts
- Euler method
- Runge-Kutta
- stability
- implicit methods
- root finding

## Key Equations
$$
y_{n+1} = y_n + h f(t_n,y_n)\ \text{(Euler)}
$$
$$
y_{n+1} = y_n + \tfrac{h}{6}(k_1 + 2k_2 + 2k_3 + k_4)\ \text{(RK4)}
$$

## Methods
- Choose explicit vs implicit based on stiffness
- Control step size
- Check stability and convergence

## Typical Problem Types
- Projectile with drag
- N-body simulation
- Stiff chemical kinetics

## Common Pitfalls
- Too-large step size causing divergence
- Ignoring stiffness

## Related Skills
- comp.numerical_integration
- comp.pde_finite

## References
- Numerical Recipes Ch.16-17
- Hairer et al.
