---
name: tension-pulleys-atwood-machines
description: Tension, Pulleys and Atwood Machines in Mechanics (Dynamics). Theoretical principles, governing equations, analytical problem-solving methodologies, and edge case analysis.
metadata:
  domain: Mechanics
  subdomain: Dynamics
  difficulty: 3/5
---

# Tension, Pulleys and Atwood Machines

## Overview & Theoretical Foundations
This skill establishes foundational and advanced analytical methods for **Tension, Pulleys and Atwood Machines**, situated within **Mechanics** under **Dynamics**.

Key focus areas include mastery of fundamental concepts, manipulation of governing differential and algebraic equations, application of rigorous problem-solving algorithms, and avoidance of common conceptual errors.

---

## Difficulty & Prerequisites
- **Difficulty Rating**: 3 / 5
- **Prerequisites**:
  - `mech.dynamics.free_body`
  - `mech.kinematics.constraints`

---

## Core Theoretical Concepts
- **Tension**: Physical principles, contextual constraints, and analytical representations.
- **Massless pulley**: Physical principles, contextual constraints, and analytical representations.
- **Ideal string**: Physical principles, contextual constraints, and analytical representations.
- **Atwood machine**: Physical principles, contextual constraints, and analytical representations.
- **Acceleration constraint**: Physical principles, contextual constraints, and analytical representations.

---

## Governing Equations & Mathematical Formulations
$$
T - m_1 g = m_1 a
$$
$$
m_2 g - T = m_2 a
$$
$$
a = \frac{(m_2-m_1)g}{m_1+m_2}
$$

---

## Step-by-Step Analytical & Problem-Solving Methods
1. **Draw FBDs for each mass**
2. **Apply the constraint (same |a|, opposite directions)**
3. **Solve the coupled equations**

---

## Standard Problem Archetypes & Applications
- **Atwood machine**
- **Two masses on a table over a pulley**
- **Moving pulley systems**

---

## Common Pitfalls, Edge Cases & Anti-Patterns
- > [!WARNING]
  > Ignoring pulley mass (only valid if stated)
- > [!WARNING]
  > Wrong sign for acceleration direction

---

## Knowledge Graph & Related Skills
- `mech.kinematics.constraints`
- `mech.rotation.torque_dynamics`

---

## References & Academic Bibliography
- Kleppner & Kolenkow Ch.2
- Morin Ch.3
