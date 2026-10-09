---
name: projectile-motion
description: Projectile Motion in Mechanics (Kinematics). Theoretical principles, governing equations, analytical problem-solving methodologies, and edge case analysis.
metadata:
  domain: Mechanics
  subdomain: Kinematics
  difficulty: 2/5
---

# Projectile Motion

## Overview & Theoretical Foundations
This skill establishes foundational and advanced analytical methods for **Projectile Motion**, situated within **Mechanics** under **Kinematics**.

Key focus areas include mastery of fundamental concepts, manipulation of governing differential and algebraic equations, application of rigorous problem-solving algorithms, and avoidance of common conceptual errors.

---

## Difficulty & Prerequisites
- **Difficulty Rating**: 2 / 5
- **Prerequisites**:
  - `mech.kinematics.constant_acceleration`

---

## Core Theoretical Concepts
- **Independence of axes**: Physical principles, contextual constraints, and analytical representations.
- **Range**: Physical principles, contextual constraints, and analytical representations.
- **Max height**: Physical principles, contextual constraints, and analytical representations.
- **Time of flight**: Physical principles, contextual constraints, and analytical representations.
- **Launch angle**: Physical principles, contextual constraints, and analytical representations.
- **Parabolic trajectory**: Physical principles, contextual constraints, and analytical representations.

---

## Governing Equations & Mathematical Formulations
$$
x = v_0\cos\theta\, t
$$
$$
y = v_0\sin\theta\, t - \tfrac12 g t^2
$$
$$
R = \frac{v_0^2 \sin 2\theta}{g}
$$
$$
H = \frac{v_0^2\sin^2\theta}{2g}
$$

---

## Step-by-Step Analytical & Problem-Solving Methods
1. **Decompose velocity into horizontal and vertical components**
2. **Treat axes independently; only y has acceleration**
3. **Use energy conservation for speed at a given height**

---

## Standard Problem Archetypes & Applications
- **Find range/height/time**
- **Hit a target at distance d**
- **Projectile from a cliff or moving platform**

---

## Common Pitfalls, Edge Cases & Anti-Patterns
- > [!WARNING]
  > Applying suvat to the horizontal axis
- > [!WARNING]
  > Ignoring launch height
- > [!WARNING]
  > Assuming symmetric trajectory when launch and landing heights differ

---

## Knowledge Graph & Related Skills
- `mech.kinematics.relative`
- `mech.energy.conservation`

---

## References & Academic Bibliography
- Kleppner & Kolenkow Ch.1
- Irodov 1.1-1.30
