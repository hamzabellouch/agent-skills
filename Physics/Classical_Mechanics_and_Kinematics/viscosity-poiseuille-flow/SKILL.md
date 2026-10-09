---
name: viscosity-poiseuille-flow
description: Viscosity and Poiseuille Flow in Mechanics (Fluids). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: mech.fluid.viscosity
  domain: Mechanics
  subdomain: Fluids
  difficulty: 4/5
---

# Viscosity and Poiseuille Flow

**ID:** `mech.fluid.viscosity`  
**Domain:** Mechanics → Fluids  
**Difficulty:** 4/5

## Prerequisites
- mech.fluids.bernoulli

## Core Concepts
- viscosity
- Newtonian fluid
- Poiseuille's law
- Stokes drag
- laminar flow

## Key Equations
$$
F = \eta A\frac{dv}{dy}
$$
$$
Q = \frac{\pi R^4 \Delta P}{8\eta L}
$$
$$
F_{Stokes} = 6\pi\eta r v
$$

## Methods
- Check whether flow is laminar
- Use Poiseuille for pipe flow
- Use Stokes drag for small spheres

## Typical Problem Types
- Flow rate through a pipe
- Sedimentation velocity
- Oil flow in a tube

## Common Pitfalls
- Using Bernoulli in a viscous regime
- Forgetting the R^4 dependence

## Related Skills
- mech.fluid.reynolds
- mech.dynamics.drag

## References
- Landau & Lifshitz Fluid Mechanics
- Feynman Vol. II Ch.41
