---
name: thermodynamic-potentials
description: Thermodynamic Potentials in Thermodynamics (Formalism). Theoretical principles, governing equations, analytical problem-solving methodologies, and edge case analysis.
metadata:
  domain: Thermodynamics
  subdomain: Formalism
  difficulty: 4/5
---

# Thermodynamic Potentials

## Overview & Theoretical Foundations
This skill establishes foundational and advanced analytical methods for **Thermodynamic Potentials**, situated within **Thermodynamics** under **Formalism**.

Key focus areas include mastery of fundamental concepts, manipulation of governing differential and algebraic equations, application of rigorous problem-solving algorithms, and avoidance of common conceptual errors.

---

## Difficulty & Prerequisites
- **Difficulty Rating**: 4 / 5
- **Prerequisites**:
  - `thermo.entropy`

---

## Core Theoretical Concepts
- **Helmholtz free energy**: Physical principles, contextual constraints, and analytical representations.
- **Gibbs free energy**: Physical principles, contextual constraints, and analytical representations.
- **Enthalpy**: Physical principles, contextual constraints, and analytical representations.
- **Maxwell relations**: Physical principles, contextual constraints, and analytical representations.
- **Legendre transform**: Physical principles, contextual constraints, and analytical representations.

---

## Governing Equations & Mathematical Formulations
$$
F = U - TS
$$
$$
G = H - TS = U - TS + PV
$$
$$
H = U + PV
$$
$$
dF = -S\,dT - P\,dV
$$

---

## Step-by-Step Analytical & Problem-Solving Methods
1. **Choose the potential whose natural variables match the constraints**
2. **Use Maxwell relations to swap derivatives**
3. **Use Gibbs for phase equilibrium**

---

## Standard Problem Archetypes & Applications
- **Free energy change in reactions**
- **Work from a thermodynamic system**
- **Phase equilibria**

---

## Common Pitfalls, Edge Cases & Anti-Patterns
- > [!WARNING]
  > Using U when T or P is the controlled variable
- > [!WARNING]
  > Sign errors in Legendre transforms

---

## Knowledge Graph & Related Skills
- `thermo.phase_equilibria`
- `stat.mech.partition_function`

---

## References & Academic Bibliography
- Callen Thermodynamics
- Kittel & Kroemer Ch.5
