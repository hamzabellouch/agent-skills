---
name: thermodynamic-processes
description: Thermodynamic Processes (Isothermal, Adiabatic, etc.) in Thermodynamics (Processes). Theoretical principles, governing equations, analytical problem-solving methodologies, and edge case analysis.
metadata:
  domain: Thermodynamics
  subdomain: Processes
  difficulty: 3/5
---

# Thermodynamic Processes (Isothermal, Adiabatic, etc.)

## Overview & Theoretical Foundations
This skill establishes foundational and advanced analytical methods for **Thermodynamic Processes (Isothermal, Adiabatic, etc.)**, situated within **Thermodynamics** under **Processes**.

Key focus areas include mastery of fundamental concepts, manipulation of governing differential and algebraic equations, application of rigorous problem-solving algorithms, and avoidance of common conceptual errors.

---

## Difficulty & Prerequisites
- **Difficulty Rating**: 3 / 5
- **Prerequisites**:
  - `thermo.first_law`

---

## Core Theoretical Concepts
- **Isothermal**: Physical principles, contextual constraints, and analytical representations.
- **Isobaric**: Physical principles, contextual constraints, and analytical representations.
- **Isochoric**: Physical principles, contextual constraints, and analytical representations.
- **Adiabatic**: Physical principles, contextual constraints, and analytical representations.
- **Polytropic process**: Physical principles, contextual constraints, and analytical representations.

---

## Governing Equations & Mathematical Formulations
$$
PV^\gamma = \text{const}\ \text{(adiabatic)}
$$
$$
PV = \text{const}\ \text{(isothermal)}
$$
$$
TV^{\gamma-1} = \text{const}\ \text{(adiabatic)}
$$

---

## Step-by-Step Analytical & Problem-Solving Methods
1. **Identify the process from what is held constant**
2. **Use the appropriate equation of state path**
3. **Compute work, heat, and \Delta U separately**

---

## Standard Problem Archetypes & Applications
- **Adiabatic compression**
- **Isothermal expansion**
- **Cyclic process like Otto cycle**

---

## Common Pitfalls, Edge Cases & Anti-Patterns
- > [!WARNING]
  > Using isothermal equations for adiabatic processes
- > [!WARNING]
  > Forgetting that Q=0 for adiabatic (not \Delta T=0)

---

## Knowledge Graph & Related Skills
- `thermo.second_law`
- `thermo.heat_engines_carnot`

---

## References & Academic Bibliography
- Zemansky & Dittman Ch.3
- Kittel & Kroemer Ch.2
