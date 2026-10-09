---
name: viscosity-poiseuille-flow
description: Viscosity and Poiseuille Flow in Mechanics (Fluids). Theoretical principles, governing equations, analytical problem-solving methodologies, and edge case analysis.
metadata:
  domain: Mechanics
  subdomain: Fluids
  difficulty: 4/5
---

# Viscosity and Poiseuille Flow

## Overview & Theoretical Foundations
This skill establishes foundational and advanced analytical methods for **Viscosity and Poiseuille Flow**, situated within **Mechanics** under **Fluids**.

Key focus areas include mastery of fundamental concepts, manipulation of governing differential and algebraic equations, application of rigorous problem-solving algorithms, and avoidance of common conceptual errors.

---

## Difficulty & Prerequisites
- **Difficulty Rating**: 4 / 5
- **Prerequisites**:
  - `mech.fluids.bernoulli`

---

## Core Theoretical Concepts
- **Viscosity**: Physical principles, contextual constraints, and analytical representations.
- **Newtonian fluid**: Physical principles, contextual constraints, and analytical representations.
- **Poiseuille's law**: Physical principles, contextual constraints, and analytical representations.
- **Stokes drag**: Physical principles, contextual constraints, and analytical representations.
- **Laminar flow**: Physical principles, contextual constraints, and analytical representations.

---

## Governing Equations & Mathematical Formulations
$$
F = \eta A\frac{dv}{dy}
$$
$$
Q = \frac{\pi R^4 \Delta P}{8\eta L}
$$
$$
F_{Stokes} = 6\pi\eta r v
$$

---

## Step-by-Step Analytical & Problem-Solving Methods
1. **Check whether flow is laminar**
2. **Use Poiseuille for pipe flow**
3. **Use Stokes drag for small spheres**

---

## Standard Problem Archetypes & Applications
- **Flow rate through a pipe**
- **Sedimentation velocity**
- **Oil flow in a tube**

---

## Common Pitfalls, Edge Cases & Anti-Patterns
- > [!WARNING]
  > Using Bernoulli in a viscous regime
- > [!WARNING]
  > Forgetting the R^4 dependence

---

## Knowledge Graph & Related Skills
- `mech.fluid.reynolds`
- `mech.dynamics.drag`

---

## References & Academic Bibliography
- Landau & Lifshitz Fluid Mechanics
- Feynman Vol. II Ch.41
