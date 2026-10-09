---
name: conservation-angular-momentum
description: Conservation of Angular Momentum in Mechanics (Rotation). Theoretical principles, governing equations, analytical problem-solving methodologies, and edge case analysis.
metadata:
  domain: Mechanics
  subdomain: Rotation
  difficulty: 3/5
---

# Conservation of Angular Momentum

## Overview & Theoretical Foundations
This skill establishes foundational and advanced analytical methods for **Conservation of Angular Momentum**, situated within **Mechanics** under **Rotation**.

Key focus areas include mastery of fundamental concepts, manipulation of governing differential and algebraic equations, application of rigorous problem-solving algorithms, and avoidance of common conceptual errors.

---

## Difficulty & Prerequisites
- **Difficulty Rating**: 3 / 5
- **Prerequisites**:
  - `mech.rotation.ang_momentum`

---

## Core Theoretical Concepts
- **Angular momentum conservation**: Physical principles, contextual constraints, and analytical representations.
- **Spin-up**: Physical principles, contextual constraints, and analytical representations.
- **Figure skater**: Physical principles, contextual constraints, and analytical representations.
- **Kepler's second law**: Physical principles, contextual constraints, and analytical representations.

---

## Governing Equations & Mathematical Formulations
$$
L = \text{const}\ \text{if}\ \tau_{ext}=0
$$
$$
I_1\omega_1 = I_2\omega_2
$$

---

## Step-by-Step Analytical & Problem-Solving Methods
1. **Check that external torque is zero about the chosen axis**
2. **Set L_initial = L_final**
3. **Relate I and \omega**

---

## Standard Problem Archetypes & Applications
- **Skater pulling arms in**
- **Dust disk landing on a turntable**
- **Planetary orbits**

---

## Common Pitfalls, Edge Cases & Anti-Patterns
- > [!WARNING]
  > Using it when an external torque is present
- > [!WARNING]
  > Forgetting to include the new mass distribution

---

## Knowledge Graph & Related Skills
- `mech.gravitation.orbits_kepler`
- `mech.rotation.ang_momentum`

---

## References & Academic Bibliography
- Halliday-Resnick-Walker Ch.11
