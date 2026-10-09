---
name: machine-learning-physics
description: Machine Learning for Physics in Computational Physics (Modern Methods). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: comp.ml_physics
  domain: Computational Physics
  subdomain: Modern Methods
  difficulty: 5/5
---

# Machine Learning for Physics

**ID:** `comp.ml_physics`  
**Domain:** Computational Physics → Modern Methods  
**Difficulty:** 5/5

## Prerequisites
- math.probability
- math.linear_algebra

## Core Concepts
- neural networks
- differentiable simulations
- surrogate models
- symbolic regression
- PINNs

## Key Equations
$$
\mathcal{L} = \mathcal{L}_{data} + \lambda\mathcal{L}_{physics}
$$

## Methods
- Choose an architecture matching the physics
- Encode physical constraints (symmetries, conservation laws)
- Validate against known limits

## Typical Problem Types
- Learning potentials from DFT
- Solving PDEs with PINNs
- Discovering equations from data

## Common Pitfalls
- Ignoring physical constraints
- Overfitting without cross-validation

## Related Skills
- comp.molecular_dynamics
- math.statistics

## References
- Carleo et al. Rev. Mod. Phys. 91, 045002 (2019)
