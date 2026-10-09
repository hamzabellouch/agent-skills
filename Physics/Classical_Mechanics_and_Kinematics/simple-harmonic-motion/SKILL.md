---
name: simple-harmonic-motion
description: Simple Harmonic Motion in Mechanics (Oscillations & Waves). Theoretical principles, governing equations, analytical problem-solving methodologies, and edge case analysis.
metadata:
  domain: Mechanics
  subdomain: Oscillations & Waves
  difficulty: 2/5
---

# Simple Harmonic Motion

## Overview & Theoretical Foundations
This skill establishes foundational and advanced analytical methods for **Simple Harmonic Motion**, situated within **Mechanics** under **Oscillations & Waves**.

Key focus areas include mastery of fundamental concepts, manipulation of governing differential and algebraic equations, application of rigorous problem-solving algorithms, and avoidance of common conceptual errors.

---

## Difficulty & Prerequisites
- **Difficulty Rating**: 2 / 5
- **Prerequisites**:
  - `mech.dynamics.springs`
  - `math.odes`

---

## Core Theoretical Concepts
- **Shm**: Physical principles, contextual constraints, and analytical representations.
- **Amplitude**: Physical principles, contextual constraints, and analytical representations.
- **Angular frequency**: Physical principles, contextual constraints, and analytical representations.
- **Phase**: Physical principles, contextual constraints, and analytical representations.
- **Small-angle approximation**: Physical principles, contextual constraints, and analytical representations.

---

## Governing Equations & Mathematical Formulations
$$
\ddot x + \omega^2 x = 0
$$
$$
x(t) = A\cos(\omega t + \phi)
$$
$$
\omega = \sqrt{k/m}
$$

---

## Step-by-Step Analytical & Problem-Solving Methods
1. **Show that the restoring force is linear in displacement**
2. **Read off \omega, then A and \phi from initial conditions**
3. **Use energy to find speed at a given position**

---

## Standard Problem Archetypes & Applications
- **Mass-spring**
- **Simple pendulum (small angle)**
- **LC circuit analogue**

---

## Common Pitfalls, Edge Cases & Anti-Patterns
- > [!WARNING]
  > Applying SHM when the force is nonlinear
- > [!WARNING]
  > Forgetting phase from initial conditions

---

## Knowledge Graph & Related Skills
- `mech.oscillations.damped`
- `mech.oscillations.pendulums`

---

## References & Academic Bibliography
- Kleppner & Kolenkow Ch.7
- Taylor Ch.5
