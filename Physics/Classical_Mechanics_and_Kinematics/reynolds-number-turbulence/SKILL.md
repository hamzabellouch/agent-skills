---
name: reynolds-number-turbulence
description: Reynolds Number and Turbulence in Mechanics (Fluids). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: mech.fluid.reynolds
  domain: Mechanics
  subdomain: Fluids
  difficulty: 4/5
---

# Reynolds Number and Turbulence

**ID:** `mech.fluid.reynolds`  
**Domain:** Mechanics → Fluids  
**Difficulty:** 4/5

## Prerequisites
- mech.fluid.viscosity

## Core Concepts
- Reynolds number
- laminar-turbulent transition
- similarity
- drag crisis

## Key Equations
$$
Re = \frac{\rho v L}{\eta}
$$

## Methods
- Compute Re for the geometry
- Compare to critical Re (~2300 for pipe flow)
- Use similarity arguments

## Typical Problem Types
- Pipe flow regime
- Flow around a sphere
- Scaling model experiments

## Common Pitfalls
- Using the wrong length scale
- Treating turbulence as deterministic

## Related Skills
- mech.fluid.viscosity
- comp.pde_finite

## References
- Tritton Physical Fluid Dynamics
