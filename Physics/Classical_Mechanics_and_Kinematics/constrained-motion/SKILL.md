---
name: constrained-motion
description: Constrained Motion (Pulleys, Ropes, Wedges) in Mechanics (Kinematics). Theoretical principles, governing equations, analytical problem-solving methodologies, and edge case analysis.
metadata:
  domain: Mechanics
  subdomain: Kinematics
  difficulty: 3/5
---

# Constrained Motion (Pulleys, Ropes, Wedges)

## Overview & Theoretical Foundations
This skill establishes foundational and advanced analytical methods for **Constrained Motion (Pulleys, Ropes, Wedges)**, situated within **Mechanics** under **Kinematics**.

Key focus areas include mastery of fundamental concepts, manipulation of governing differential and algebraic equations, application of rigorous problem-solving algorithms, and avoidance of common conceptual errors.

---

## Difficulty & Prerequisites
- **Difficulty Rating**: 3 / 5
- **Prerequisites**:
  - `mech.kinematics.definitions`
  - `mech.dynamics.pulleys`

---

## Core Theoretical Concepts
- **Constraint equations**: Physical principles, contextual constraints, and analytical representations.
- **Inextensible string**: Physical principles, contextual constraints, and analytical representations.
- **Virtual work**: Physical principles, contextual constraints, and analytical representations.
- **Degrees of freedom**: Physical principles, contextual constraints, and analytical representations.

---

## Governing Equations & Mathematical Formulations
$$
\sum_i \vec F_i \cdot \delta\vec r_i = 0
$$
$$
L = \text{const} \Rightarrow \dot L = 0
$$

---

## Step-by-Step Analytical & Problem-Solving Methods
1. **Write the length constraint of the string**
2. **Differentiate to relate accelerations**
3. **Use the number of DOF to decide independent coordinates**

---

## Standard Problem Archetypes & Applications
- **Atwood machine with moving pulley**
- **Two blocks connected over a wedge**
- **Block sliding on a moving wedge**

---

## Common Pitfalls, Edge Cases & Anti-Patterns
- > [!WARNING]
  > Assuming both blocks have equal acceleration without checking the constraint
- > [!WARNING]
  > Ignoring the constraint direction

---

## Knowledge Graph & Related Skills
- `mech.dynamics.pulleys`
- `math.variational_lagrange`

---

## References & Academic Bibliography
- Kleppner & Kolenkow Ch.2
- Morin Ch.3
