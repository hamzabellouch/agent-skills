---
name: rc-circuits
description: RC Circuits in Electromagnetism (Circuits). Theoretical principles, governing equations, analytical problem-solving methodologies, and edge case analysis.
metadata:
  domain: Electromagnetism
  subdomain: Circuits
  difficulty: 3/5
---

# RC Circuits

## Overview & Theoretical Foundations
This skill establishes foundational and advanced analytical methods for **RC Circuits**, situated within **Electromagnetism** under **Circuits**.

Key focus areas include mastery of fundamental concepts, manipulation of governing differential and algebraic equations, application of rigorous problem-solving algorithms, and avoidance of common conceptual errors.

---

## Difficulty & Prerequisites
- **Difficulty Rating**: 3 / 5
- **Prerequisites**:
  - `em.circuits.kirchhoff`
  - `em.electrostatics.capacitance`
  - `math.odes`

---

## Core Theoretical Concepts
- **Time constant**: Physical principles, contextual constraints, and analytical representations.
- **Charging**: Physical principles, contextual constraints, and analytical representations.
- **Discharging**: Physical principles, contextual constraints, and analytical representations.
- **Exponential decay**: Physical principles, contextual constraints, and analytical representations.
- **Steady state**: Physical principles, contextual constraints, and analytical representations.

---

## Governing Equations & Mathematical Formulations
$$
Q(t) = Q_\infty(1 - e^{-t/RC})
$$
$$
Q(t) = Q_0 e^{-t/RC}
$$
$$
\tau = RC
$$

---

## Step-by-Step Analytical & Problem-Solving Methods
1. **Write the differential equation from Kirchhoff**
2. **Solve the first-order ODE**
3. **Identify the initial and final states**

---

## Standard Problem Archetypes & Applications
- **Charging capacitor**
- **Discharging capacitor**
- **Time to reach a certain charge**

---

## Common Pitfalls, Edge Cases & Anti-Patterns
- > [!WARNING]
  > Using final charge as initial or vice versa
- > [!WARNING]
  > Forgetting the time constant is RC

---

## Knowledge Graph & Related Skills
- `em.circuits.ac_impedance`
- `math.odes`

---

## References & Academic Bibliography
- Halliday-Resnick-Walker Ch.27
