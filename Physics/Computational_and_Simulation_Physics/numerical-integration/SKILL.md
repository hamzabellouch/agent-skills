---
name: numerical-integration
description: Numerical Integration in Computational Physics (Numerical Methods). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: comp.numerical_integration
  domain: Computational Physics
  subdomain: Numerical Methods
  difficulty: 3/5
---

# Numerical Integration

**ID:** `comp.numerical_integration`  
**Domain:** Computational Physics → Numerical Methods  
**Difficulty:** 3/5

## Prerequisites
- math.calculus.integrals

## Core Concepts
- trapezoid rule
- Simpson's rule
- Gaussian quadrature
- error scaling
- adaptive methods

## Key Equations
$$
\int_a^b f\, dx \approx h\left[\tfrac12 f_0 + f_1 + \dots + \tfrac12 f_N\right]
$$

## Methods
- Choose the method based on smoothness
- Control the step size
- Estimate error

## Typical Problem Types
- Integrals of smooth functions
- Oscillatory integrals
- Multi-dimensional integrals

## Common Pitfalls
- Using too coarse a grid
- Ignoring endpoint singularities

## Related Skills
- comp.monte_carlo
- math.numerical_methods

## References
- Numerical Recipes Ch.4
- Press et al.
