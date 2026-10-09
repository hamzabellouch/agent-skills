---
name: tensor-calculus-differential-forms
description: Tensor Calculus and Differential Forms in Mathematics (Geometry). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: math.tensor_calculus
  domain: Mathematics
  subdomain: Geometry
  difficulty: 5/5
---

# Tensor Calculus and Differential Forms

**ID:** `math.tensor_calculus`  
**Domain:** Mathematics → Geometry  
**Difficulty:** 5/5

## Prerequisites
- math.vector_calculus
- math.linear_algebra

## Core Concepts
- tensors
- index notation
- covariant/contravariant
- metric tensor
- connection

## Key Equations
$$
T^{\mu\nu} = \Lambda^\mu_{\ \alpha}\Lambda^\nu_{\ \beta}T^{\alpha\beta}
$$
$$
\Gamma^\lambda_{\mu\nu} = \tfrac12 g^{\lambda\sigma}(\partial_\mu g_{\sigma\nu} + \partial_\nu g_{\sigma\mu} - \partial_\sigma g_{\mu\nu})
$$

## Methods
- Manipulate indices carefully
- Raise/lower with the metric
- Compute covariant derivatives

## Typical Problem Types
- Stress-energy tensor
- Curvature computation
- Relativistic kinematics

## Common Pitfalls
- Summing over the wrong pair of indices
- Mixing up upper/lower indices

## Related Skills
- rel.general.geodesics
- rel.special.four_vectors

## References
- Schutz Geometrical Methods
- Misner Thorne Wheeler Ch.3
