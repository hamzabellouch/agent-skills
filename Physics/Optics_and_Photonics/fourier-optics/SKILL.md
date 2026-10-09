---
name: fourier-optics
description: Fourier Optics in Optics (Modern Optics). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: optics.modern.fourier_optics
  domain: Optics
  subdomain: Modern Optics
  difficulty: 5/5
---

# Fourier Optics

**ID:** `optics.modern.fourier_optics`  
**Domain:** Optics → Modern Optics  
**Difficulty:** 5/5

## Prerequisites
- math.fourier_analysis
- optics.wave.diffraction

## Core Concepts
- spatial frequency
- Fourier transform of aperture
- PSF and OTF
- 4f system
- spatial filtering

## Key Equations
$$
E(x,y) \propto \mathcal{F}\{A(\xi,\eta)\}
$$
$$
H(f_x,f_y) = \mathcal{F}\{h(x,y)\}
$$

## Methods
- Take the Fourier transform of the aperture
- Propagate to the focal plane
- Apply spatial filters in the Fourier plane

## Typical Problem Types
- Diffraction pattern as a Fourier transform
- Image filtering with a 4f system
- Resolution limit from the aperture

## Common Pitfalls
- Confusing spatial and temporal frequencies
- Forgetting the quadratic phase factors

## Related Skills
- optics.wave.diffraction
- comp.signal_processing

## References
- Goodman Introduction to Fourier Optics
