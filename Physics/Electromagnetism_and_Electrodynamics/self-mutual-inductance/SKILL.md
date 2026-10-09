---
name: self-mutual-inductance
description: Self and Mutual Inductance in Electromagnetism (Induction). Theoretical principles, governing equations, analytical problem-solving methodologies, and edge case analysis.
metadata:
  domain: Electromagnetism
  subdomain: Induction
  difficulty: 4/5
---

# Self and Mutual Inductance

## Overview & Theoretical Foundations
This skill establishes foundational and advanced analytical methods for **Self and Mutual Inductance**, situated within **Electromagnetism** under **Induction**.

Key focus areas include mastery of fundamental concepts, manipulation of governing differential and algebraic equations, application of rigorous problem-solving algorithms, and avoidance of common conceptual errors.

---

## Difficulty & Prerequisites
- **Difficulty Rating**: 4 / 5
- **Prerequisites**:
  - `em.induction.faraday`
  - `em.circuits.rc`

---

## Core Theoretical Concepts
- **Inductance**: Physical principles, contextual constraints, and analytical representations.
- **Self-induced emf**: Physical principles, contextual constraints, and analytical representations.
- **Solenoid inductance**: Physical principles, contextual constraints, and analytical representations.
- **Mutual inductance**: Physical principles, contextual constraints, and analytical representations.
- **Energy in an inductor**: Physical principles, contextual constraints, and analytical representations.

---

## Governing Equations & Mathematical Formulations
$$
L = \frac{N\Phi}{I}
$$
$$
\mathcal{E} = -L\frac{dI}{dt}
$$
$$
U = \tfrac12 LI^2
$$

---

## Step-by-Step Analytical & Problem-Solving Methods
1. **Compute L from geometry**
2. **Use Kirchhoff with an inductor**
3. **Analyze RL transients**

---

## Standard Problem Archetypes & Applications
- **Solenoid inductance**
- **RL circuit response**
- **Energy stored in an inductor**

---

## Common Pitfalls, Edge Cases & Anti-Patterns
- > [!WARNING]
  > Treating inductors like resistors in DC steady state
- > [!WARNING]
  > Forgetting back-EMF direction

---

## Knowledge Graph & Related Skills
- `em.circuits.ac_impedance`
- `em.maxwell.equations`

---

## References & Academic Bibliography
- Griffiths EM Ch.7
- Halliday-Resnick-Walker Ch.30
