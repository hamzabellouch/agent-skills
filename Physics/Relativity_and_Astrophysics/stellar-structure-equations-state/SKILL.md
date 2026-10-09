---
name: stellar-structure-equations-state
description: Stellar Structure and Equations of State in Astrophysics & Cosmology (Stars). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: ast.stellar_structure
  domain: Astrophysics & Cosmology
  subdomain: Stars
  difficulty: 4/5
---

# Stellar Structure and Equations of State

**ID:** `ast.stellar_structure`  
**Domain:** Astrophysics & Cosmology → Stars  
**Difficulty:** 4/5

## Prerequisites
- thermo.heat_transfer
- mech.gravitation.orbits_kepler

## Core Concepts
- hydrostatic equilibrium
- virial theorem
- energy transport
- stellar EOS

## Key Equations
$$
\frac{dP}{dr} = -\frac{G M(r)\rho(r)}{r^2}
$$
$$
\frac{dM}{dr} = 4\pi r^2 \rho(r)
$$

## Methods
- Set up the four stellar structure equations
- Apply boundary conditions
- Use the virial theorem to estimate central temperature

## Typical Problem Types
- Sun's central pressure
- Main-sequence lifetime estimate
- White dwarf Chandrasekhar limit

## Common Pitfalls
- Ignoring radiation pressure for massive stars
- Using a single EOS for all layers

## Related Skills
- ast.stellar_evolution
- stat.mech.fermi_dirac

## References
- Carroll & Ostlie Ch.10
- Kippenhahn & Weigert
