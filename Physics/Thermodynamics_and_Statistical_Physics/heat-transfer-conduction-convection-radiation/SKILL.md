---
name: heat-transfer-conduction-convection-radiation
description: Heat Transfer: Conduction, Convection, Radiation in Thermodynamics (Heat Transfer). Theoretical principles, governing equations, analytical problem-solving methodologies, and edge case analysis.
metadata:
  domain: Thermodynamics
  subdomain: Heat Transfer
  difficulty: 3/5
---

# Heat Transfer: Conduction, Convection, Radiation

## Overview & Theoretical Foundations
This skill establishes foundational and advanced analytical methods for **Heat Transfer: Conduction, Convection, Radiation**, situated within **Thermodynamics** under **Heat Transfer**.

Key focus areas include mastery of fundamental concepts, manipulation of governing differential and algebraic equations, application of rigorous problem-solving algorithms, and avoidance of common conceptual errors.

---

## Difficulty & Prerequisites
- **Difficulty Rating**: 3 / 5
- **Prerequisites**:
  - `thermo.first_law`

---

## Core Theoretical Concepts
- **Thermal conductivity**: Physical principles, contextual constraints, and analytical representations.
- **Fourier's law**: Physical principles, contextual constraints, and analytical representations.
- **Newton cooling**: Physical principles, contextual constraints, and analytical representations.
- **Stefan-boltzmann**: Physical principles, contextual constraints, and analytical representations.
- **Emissivity**: Physical principles, contextual constraints, and analytical representations.

---

## Governing Equations & Mathematical Formulations
$$
\frac{dQ}{dt} = -kA\frac{dT}{dx}
$$
$$
\frac{dQ}{dt} = hA(T_s - T_\infty)
$$
$$
\frac{dQ}{dt} = \epsilon\sigma A T^4
$$

---

## Step-by-Step Analytical & Problem-Solving Methods
1. **Identify the dominant transfer mode**
2. **Use steady-state flux for layered walls**
3. **Combine modes when they act in parallel/series**

---

## Standard Problem Archetypes & Applications
- **Heat through a composite wall**
- **Cooling of a hot object**
- **Solar constant and Earth temperature**

---

## Common Pitfalls, Edge Cases & Anti-Patterns
- > [!WARNING]
  > Forgetting emissivity for real surfaces
- > [!WARNING]
  > Mixing steady-state and transient problems

---

## Knowledge Graph & Related Skills
- `stat.mech.boltzmann`
- `ast.stellar_structure`

---

## References & Academic Bibliography
- Incropera & DeWitt
- Halliday-Resnick-Walker Ch.18
