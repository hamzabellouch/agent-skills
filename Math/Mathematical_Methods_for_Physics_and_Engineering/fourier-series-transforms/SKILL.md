---
name: fourier-series-transforms
description: Fourier Series and Transforms in Mathematics (Analysis). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: math.fourier_analysis
  domain: Mathematics
  subdomain: Analysis
  difficulty: 3/5
---

# Fourier Series and Transforms

**ID:** `math.fourier_analysis`  
**Domain:** Mathematics → Analysis  
**Difficulty:** 3/5

## Prerequisites
- math.calculus.integrals

## Core Concepts
- Fourier series
- Fourier transform
- convolution
- Parseval's theorem
- Dirac delta

## Key Equations
$$
f(x) = \sum_n c_n e^{inx}
$$
$$
\hat f(k) = \int f(x)e^{-ikx}dx
$$
$$
\int |f|^2 dx = \int |\hat f|^2 dk\ \text{(Plancherel)}
$$

## Methods
- Compute coefficients/transform
- Apply convolution theorem
- Use Parseval for energy integrals

## Typical Problem Types
- Signal analysis
- Diffraction theory
- Quantum momentum-space wavefunctions

## Common Pitfalls
- Forgetting 2π factors
- Assuming pointwise convergence without conditions

## Related Skills
- optics.modern.fourier_optics
- qm.schrodinger.wavefunction

## References
- Bracewell Fourier Transform
- Arfken Ch.15
