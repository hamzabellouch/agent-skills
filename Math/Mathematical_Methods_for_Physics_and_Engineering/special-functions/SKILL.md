---
name: special-functions
description: Special Functions in Mathematics (Analysis). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: math.special_functions
  domain: Mathematics
  subdomain: Analysis
  difficulty: 4/5
---

# Special Functions

**ID:** `math.special_functions`  
**Domain:** Mathematics → Analysis  
**Difficulty:** 4/5

## Prerequisites
- math.odes
- math.complex_analysis

## Core Concepts
- Bessel functions
- Legendre polynomials
- Hermite polynomials
- Laguerre polynomials
- Gamma function

## Key Equations
$$
x^2 y'' + xy' + (x^2-n^2)y = 0\ \text{(Bessel)}
$$
$$
(1-x^2)y'' - 2xy' + l(l+1)y = 0\ \text{(Legendre)}
$$

## Methods
- Recognize the differential equation
- Use generating functions and recurrences
- Apply orthogonality

## Typical Problem Types
- Separation of variables in cylindrical/spherical geometry
- Quantum harmonic oscillator
- Hydrogen radial functions

## Common Pitfalls
- Forgetting the orthogonality weights
- Using the wrong branch

## Related Skills
- qm.formalism.hydrogen_atom
- qm.schrodinger.harmonic_oscillator

## References
- Arfken Ch.11-13
- Abramowitz & Stegun
