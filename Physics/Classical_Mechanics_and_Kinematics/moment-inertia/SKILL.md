---
name: moment-inertia
description: Moment of Inertia in Mechanics (Rotation). Theoretical principles, governing equations, analytical problem-solving methodologies, and edge case analysis.
metadata:
  domain: Mechanics
  subdomain: Rotation
  difficulty: 3/5
---

# Moment of Inertia

## Overview & Theoretical Foundations
This skill establishes foundational and advanced analytical methods for **Moment of Inertia**, situated within **Mechanics** under **Rotation**.

Key focus areas include mastery of fundamental concepts, manipulation of governing differential and algebraic equations, application of rigorous problem-solving algorithms, and avoidance of common conceptual errors.

---

## Difficulty & Prerequisites
- **Difficulty Rating**: 3 / 5
- **Prerequisites**:
  - `mech.rotation.angular_kinematics`

---

## Core Theoretical Concepts
- **Moment of inertia**: Physical principles, contextual constraints, and analytical representations.
- **Rotational inertia**: Physical principles, contextual constraints, and analytical representations.
- **Continuous bodies**: Physical principles, contextual constraints, and analytical representations.
- **Standard shapes**: Physical principles, contextual constraints, and analytical representations.

---

## Governing Equations & Mathematical Formulations
$$
I = \sum m_i r_i^2
$$
$$
I = \int r^2\,dm
$$
$$
I_{disk} = \tfrac12 MR^2
$$
$$
I_{sphere} = \tfrac25 MR^2
$$

---

## Step-by-Step Analytical & Problem-Solving Methods
1. **Choose the axis**
2. **Integrate r^2 dm using symmetry**
3. **Use standard results for common shapes**

---

## Standard Problem Archetypes & Applications
- **I for a rod, disk, sphere, hoop**
- **Composite bodies**

---

## Common Pitfalls, Edge Cases & Anti-Patterns
- > [!WARNING]
  > Using I about the wrong axis
- > [!WARNING]
  > Forgetting that I depends on mass distribution

---

## Knowledge Graph & Related Skills
- `mech.rotation.parallel_axis`
- `mech.rotation.rot_energy`

---

## References & Academic Bibliography
- Serway Ch.10
- Kleppner & Kolenkow Ch.6
