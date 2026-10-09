---
name: angular-momentum
description: Angular Momentum in Mechanics (Rotation). Theoretical principles, governing equations, analytical problem-solving methodologies, and edge case analysis.
metadata:
  domain: Mechanics
  subdomain: Rotation
  difficulty: 3/5
---

# Angular Momentum

## Overview & Theoretical Foundations
This skill establishes foundational and advanced analytical methods for **Angular Momentum**, situated within **Mechanics** under **Rotation**.

Key focus areas include mastery of fundamental concepts, manipulation of governing differential and algebraic equations, application of rigorous problem-solving algorithms, and avoidance of common conceptual errors.

---

## Difficulty & Prerequisites
- **Difficulty Rating**: 3 / 5
- **Prerequisites**:
  - `mech.rotation.torque_dynamics`

---

## Core Theoretical Concepts
- **Angular momentum**: Physical principles, contextual constraints, and analytical representations.
- **Spin**: Physical principles, contextual constraints, and analytical representations.
- **Orbital angular momentum**: Physical principles, contextual constraints, and analytical representations.
- **Angular impulse**: Physical principles, contextual constraints, and analytical representations.

---

## Governing Equations & Mathematical Formulations
$$
\vec L = \vec r\times\vec p
$$
$$
\vec L = I\vec\omega
$$
$$
\vec\tau = \frac{d\vec L}{dt}
$$

---

## Step-by-Step Analytical & Problem-Solving Methods
1. **Compute L about a chosen point/axis**
2. **Use L = I\omega for rigid bodies about a principal axis**
3. **Apply angular impulse when torque acts over time**

---

## Standard Problem Archetypes & Applications
- **Rotating disk**
- **Particle moving in a straight line (L about a point)**
- **Spinning skater**

---

## Common Pitfalls, Edge Cases & Anti-Patterns
- > [!WARNING]
  > Mixing the point about which L is computed
- > [!WARNING]
  > Forgetting that L is a vector

---

## Knowledge Graph & Related Skills
- `mech.rotation.ang_momentum_conservation`
- `mech.rotation.gyroscope`

---

## References & Academic Bibliography
- Taylor Ch.8
- Kleppner & Kolenkow Ch.6
