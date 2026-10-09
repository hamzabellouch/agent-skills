---
name: particle-a-box
description: Particle in a Box (Infinite Potential Well) in Quantum Mechanics (Schrodinger Equation). Theoretical principles, governing equations, analytical problem-solving methodologies, and edge case analysis.
metadata:
  domain: Quantum Mechanics
  subdomain: Schrodinger Equation
  difficulty: 3/5
---

# Particle in a Box (Infinite Potential Well)

## Overview & Theoretical Foundations
This skill establishes foundational and advanced analytical methods for **Particle in a Box (Infinite Potential Well)**, situated within **Quantum Mechanics** under **Schrodinger Equation**.

Key focus areas include mastery of fundamental concepts, manipulation of governing differential and algebraic equations, application of rigorous problem-solving algorithms, and avoidance of common conceptual errors.

---

## Difficulty & Prerequisites
- **Difficulty Rating**: 3 / 5
- **Prerequisites**:
  - `qm.found.de_broglie`
  - `math.differential_equations`

---

## Core Theoretical Concepts
- **Time-independent schrodinger equation**: Physical principles, contextual constraints, and analytical representations.
- **Infinite square well**: Physical principles, contextual constraints, and analytical representations.
- **Boundary conditions**: Physical principles, contextual constraints, and analytical representations.
- **Wavefunction normalization**: Physical principles, contextual constraints, and analytical representations.
- **Zero-point energy**: Physical principles, contextual constraints, and analytical representations.
- **Orthonormality**: Physical principles, contextual constraints, and analytical representations.

---

## Governing Equations & Mathematical Formulations
$$
-\frac{\hbar^2}{2m}\frac{d^2\psi}{dx^2} = E\psi
$$
$$
\psi_n(x) = \sqrt{\frac{2}{L}}\sin\left(\frac{n\pi x}{L}\right)
$$
$$
E_n = \frac{n^2\pi^2\hbar^2}{2mL^2} = \frac{n^2 h^2}{8mL^2}
$$

---

## Step-by-Step Analytical & Problem-Solving Methods
1. **Apply boundary conditions psi(0) = psi(L) = 0**
2. **Solve second-order ODE to find sinusoidal eigenfunctions**
3. **Normalize wavefunction over interval [0, L]**
4. **Compute expectation values and position-momentum uncertainties**

---

## Standard Problem Archetypes & Applications
- **Quantum well confinement in semiconductor nanostructures**
- **Optical absorption in conjugated polyenes (particle in a box model)**
- **Calculation of ground-state energy, expectation values <x> and <p^2>**

---

## Common Pitfalls, Edge Cases & Anti-Patterns
- > [!WARNING]
  > Allowing n = 0 (which results in a trivial zero wavefunction, violating normalization)
- > [!WARNING]
  > Assuming non-zero probability at the infinite potential boundaries
- > [!WARNING]
  > Forgetting normalization factor sqrt(2/L) in inner products

---

## Knowledge Graph & Related Skills
- `qm.schrodinger.harmonic_oscillator`
- `qm.approx.perturbation_td`

---

## References & Academic Bibliography
- Griffiths Quantum Mechanics Ch.2
- Shankar Quantum Mechanics Ch.5
