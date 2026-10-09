---
name: band-theory-solids
description: Band Theory of Solids in Condensed Matter (Electronic Structure). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: cond.band_theory
  domain: Condensed Matter
  subdomain: Electronic Structure
  difficulty: 5/5
---

# Band Theory of Solids

**ID:** `cond.band_theory`  
**Domain:** Condensed Matter → Electronic Structure  
**Difficulty:** 5/5

## Prerequisites
- cond.crystal_structure
- stat.mech.fermi_dirac

## Core Concepts
- Bloch theorem
- energy bands
- band gap
- effective mass
- density of states

## Key Equations
$$
\psi_{n\vec k}(\vec r) = e^{i\vec k\cdot\vec r}u_{n\vec k}(\vec r)
$$
$$
E_n(\vec k)\ \text{periodic in reciprocal space}
$$

## Methods
- Apply Bloch's theorem
- Compute bands in tight-binding or nearly-free-electron models
- Determine metals vs insulators vs semiconductors

## Typical Problem Types
- Band structure of a 1D chain
- Effective mass near band edges
- Fermi surface

## Common Pitfalls
- Treating electrons as free
- Forgetting the periodic potential

## Related Skills
- cond.semiconductors
- cond.superconductivity

## References
- Ashcroft & Mermin Ch.8-9
- Kittel Ch.7
