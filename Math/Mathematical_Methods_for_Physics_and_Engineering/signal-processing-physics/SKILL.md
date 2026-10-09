---
name: signal-processing-physics
description: Signal Processing for Physics in Mathematics (Applications). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: comp.signal_processing
  domain: Mathematics
  subdomain: Applications
  difficulty: 4/5
---

# Signal Processing for Physics

**ID:** `comp.signal_processing`  
**Domain:** Mathematics → Applications  
**Difficulty:** 4/5

## Prerequisites
- math.fourier_analysis
- math.statistics

## Core Concepts
- sampling theorem
- aliasing
- filters
- power spectral density
- windowing

## Key Equations
$$
f_s > 2 f_{max}
$$
$$
PSD(f) = |\hat x(f)|^2
$$

## Methods
- Choose sampling rate
- Apply window functions
- Estimate power spectra

## Typical Problem Types
- Analyzing experimental time series
- Lock-in detection
- Gravitational wave data analysis

## Common Pitfalls
- Undersampling causing aliasing
- Ignoring spectral leakage

## Related Skills
- math.fourier_analysis
- rel.general.gravitational_waves

## References
- Oppenheim & Schafer
- Press et al. Numerical Recipes Ch.13
