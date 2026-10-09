---
name: driven-oscillations-resonance
description: Driven Oscillations and Resonance in Mechanics (Oscillations & Waves). Theoretical principles, governing equations, analytical problem-solving methodologies, and edge case analysis.
metadata:
  domain: Mechanics
  subdomain: Oscillations & Waves
  difficulty: 4/5
---

# Driven Oscillations and Resonance

## Overview & Theoretical Foundations
This skill establishes foundational and advanced analytical methods for **Driven Oscillations and Resonance**, situated within **Mechanics** under **Oscillations & Waves**.

Key focus areas include mastery of fundamental concepts, manipulation of governing differential and algebraic equations, application of rigorous problem-solving algorithms, and avoidance of common conceptual errors.

---

## Difficulty & Prerequisites
- **Difficulty Rating**: 4 / 5
- **Prerequisites**:
  - `mech.oscillations.damped`

---

## Core Theoretical Concepts
- **Driving frequency**: Physical principles, contextual constraints, and analytical representations.
- **Resonance**: Physical principles, contextual constraints, and analytical representations.
- **Amplitude response**: Physical principles, contextual constraints, and analytical representations.
- **Phase lag**: Physical principles, contextual constraints, and analytical representations.
- **Steady state**: Physical principles, contextual constraints, and analytical representations.

---

## Governing Equations & Mathematical Formulations
$$
\ddot x + 2\gamma\dot x + \omega_0^2 x = F_0\cos(\omega t)/m
$$
$$
A(\omega) = \frac{F_0/m}{\sqrt{(\omega_0^2-\omega^2)^2 + (2\gamma\omega)^2}}
$$

---

## Step-by-Step Analytical & Problem-Solving Methods
1. **Solve for the steady-state particular solution**
2. **Analyze A(\omega) near resonance**
3. **Include the transient if initial conditions matter**

---

## Standard Problem Archetypes & Applications
- **Resonance in a driven pendulum**
- **Tacoma Narrows analogy**
- **RLC resonance**

---

## Common Pitfalls, Edge Cases & Anti-Patterns
- > [!WARNING]
  > Forgetting the transient term
- > [!WARNING]
  > Assuming resonance is always at \omega_0 (it shifts with damping)

---

## Knowledge Graph & Related Skills
- `mech.oscillations.damped`
- `mech.waves.wave_equation`

---

## References & Academic Bibliography
- Taylor Ch.5
- Feynman Vol. I Ch.23
