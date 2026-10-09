---
name: elastic-collisions
description: Elastic Collisions in Mechanics (Momentum). Theoretical principles, governing equations, analytical problem-solving methodologies, and edge case analysis.
metadata:
  domain: Mechanics
  subdomain: Momentum
  difficulty: 3/5
---

# Elastic Collisions

## Overview & Theoretical Foundations
This skill establishes foundational and advanced analytical methods for **Elastic Collisions**, situated within **Mechanics** under **Momentum**.

Key focus areas include mastery of fundamental concepts, manipulation of governing differential and algebraic equations, application of rigorous problem-solving algorithms, and avoidance of common conceptual errors.

---

## Difficulty & Prerequisites
- **Difficulty Rating**: 3 / 5
- **Prerequisites**:
  - `mech.momentum.conservation`
  - `mech.energy.conservation`

---

## Core Theoretical Concepts
- **Elastic collision**: Physical principles, contextual constraints, and analytical representations.
- **Coefficient of restitution**: Physical principles, contextual constraints, and analytical representations.
- **Equal-mass exchange**: Physical principles, contextual constraints, and analytical representations.
- **Cm frame**: Physical principles, contextual constraints, and analytical representations.

---

## Governing Equations & Mathematical Formulations
$$
e = \frac{v_2'-v_1'}{v_1-v_2} = 1
$$
$$
v_1' = \frac{m_1-m_2}{m_1+m_2}v_1
$$

---

## Step-by-Step Analytical & Problem-Solving Methods
1. **Use momentum conservation plus KE conservation**
2. **Work in the CM frame for simplicity**
3. **Solve the coupled equations**

---

## Standard Problem Archetypes & Applications
- **1D elastic collision**
- **Equal masses exchanging velocities**
- **2D elastic scattering**

---

## Common Pitfalls, Edge Cases & Anti-Patterns
- > [!WARNING]
  > Using KE conservation for inelastic collisions
- > [!WARNING]
  > Wrong sign of relative velocity

---

## Knowledge Graph & Related Skills
- `mech.momentum.inelastic`
- `mech.momentum.center_of_mass`

---

## References & Academic Bibliography
- Taylor Ch.3
- Kleppner & Kolenkow Ch.4
