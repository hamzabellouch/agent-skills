---
name: maxwell-s-equations
description: Maxwell's Equations in Electromagnetism (Foundations). Theoretical principles, governing equations, analytical problem-solving methodologies, and edge case analysis.
metadata:
  domain: Electromagnetism
  subdomain: Foundations
  difficulty: 5/5
---

# Maxwell's Equations

## Overview & Theoretical Foundations
This skill establishes foundational and advanced analytical methods for **Maxwell's Equations**, situated within **Electromagnetism** under **Foundations**.

Key focus areas include mastery of fundamental concepts, manipulation of governing differential and algebraic equations, application of rigorous problem-solving algorithms, and avoidance of common conceptual errors.

---

## Difficulty & Prerequisites
- **Difficulty Rating**: 5 / 5
- **Prerequisites**:
  - `em.electrostatics.gauss`
  - `em.magnetostatics.ampere`
  - `em.induction.faraday`

---

## Core Theoretical Concepts
- **Displacement current**: Physical principles, contextual constraints, and analytical representations.
- **Unification**: Physical principles, contextual constraints, and analytical representations.
- **Wave equation origin**: Physical principles, contextual constraints, and analytical representations.
- **Differential vs integral form**: Physical principles, contextual constraints, and analytical representations.

---

## Governing Equations & Mathematical Formulations
$$
\nabla\cdot\vec E = \frac{\rho}{\epsilon_0}
$$
$$
\nabla\cdot\vec B = 0
$$
$$
\nabla\times\vec E = -\frac{\partial \vec B}{\partial t}
$$
$$
\nabla\times\vec B = \mu_0\vec J + \mu_0\epsilon_0\frac{\partial \vec E}{\partial t}
$$

---

## Step-by-Step Analytical & Problem-Solving Methods
1. **Choose integral or differential form based on symmetry**
2. **Use displacement current for time-varying fields**
3. **Derive the wave equation in vacuum**

---

## Standard Problem Archetypes & Applications
- **Deriving the speed of light**
- **Boundary conditions at interfaces**
- **Waveguides**

---

## Common Pitfalls, Edge Cases & Anti-Patterns
- > [!WARNING]
  > Forgetting the displacement current
- > [!WARNING]
  > Using static forms for time-varying fields

---

## Knowledge Graph & Related Skills
- `em.waves.em_waves`
- `rel.special.lorentz`

---

## References & Academic Bibliography
- Griffiths EM Ch.7
- Jackson Ch.6
