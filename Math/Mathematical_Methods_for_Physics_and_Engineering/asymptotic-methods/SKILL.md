---
name: asymptotic-methods
description: Asymptotic Methods in Mathematics (Analysis). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: math.asymptotics
  domain: Mathematics
  subdomain: Analysis
  difficulty: 5/5
---

# Asymptotic Methods

**ID:** `math.asymptotics`  
**Domain:** Mathematics → Analysis  
**Difficulty:** 5/5

## Prerequisites
- math.special_functions
- math.complex_analysis

## Core Concepts
- asymptotic series
- Laplace method
- stationary phase
- steepest descent
- dominant balance

## Key Equations
$$
\int_a^b g(x)e^{\lambda f(x)}dx \sim g(x_0)e^{\lambda f(x_0)}\sqrt{\frac{2\pi}{\lambda|f''(x_0)|}}
$$

## Methods
- Identify large/small parameter
- Apply Laplace/stationary-phase method
- Match asymptotic regions

## Typical Problem Types
- Saddle-point approximations
- WKB connection formulas
- Large-N expansions

## Common Pitfalls
- Confusing convergent and asymptotic series
- Ignoring endpoint contributions

## Related Skills
- qm.approx.wkb
- math.special_functions

## References
- Bender & Orszag Advanced Mathematical Methods
