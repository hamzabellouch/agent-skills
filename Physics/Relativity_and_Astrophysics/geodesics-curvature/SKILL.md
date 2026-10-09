---
name: geodesics-curvature
description: Geodesics and Curvature in Relativity (General). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: rel.general.geodesics
  domain: Relativity
  subdomain: General
  difficulty: 5/5
---

# Geodesics and Curvature

**ID:** `rel.general.geodesics`  
**Domain:** Relativity → General  
**Difficulty:** 5/5

## Prerequisites
- rel.special.four_vectors
- math.differential_geometry

## Core Concepts
- geodesic equation
- Christoffel symbols
- Riemann tensor
- Ricci tensor
- Einstein field equations

## Key Equations
$$
\frac{d^2x^\mu}{d\tau^2} + \Gamma^\mu_{\alpha\beta}\frac{dx^\alpha}{d\tau}\frac{dx^\beta}{d\tau} = 0
$$
$$
G_{\mu\nu} = \frac{8\pi G}{c^4}T_{\mu\nu}
$$

## Methods
- Compute Christoffel symbols from the metric
- Solve the geodesic equation
- Interpret curvature via the Riemann tensor

## Typical Problem Types
- Schwarzschild geodesics
- FRW cosmology
- Gravitational wave propagation

## Common Pitfalls
- Index errors in the geodesic equation
- Mixing conventions for curvature

## Related Skills
- rel.general.schwarzschild
- ast.cosmology

## References
- Carroll Ch.3
- Misner Thorne Wheeler
