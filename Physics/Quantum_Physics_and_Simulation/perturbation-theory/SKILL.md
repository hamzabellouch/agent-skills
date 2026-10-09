---
name: perturbation-theory
description: Perturbation Theory (Time-Independent and Time-Dependent) in Quantum Mechanics (Approximation Methods). Theoretical principles, governing equations, analytical problem-solving methodologies, and edge case analysis.
metadata:
  domain: Quantum Mechanics
  subdomain: Approximation Methods
  difficulty: 5/5
---

# Perturbation Theory (Time-Independent and Time-Dependent)

## Overview & Theoretical Foundations
This skill establishes foundational and advanced analytical methods for **Perturbation Theory (Time-Independent and Time-Dependent)**, situated within **Quantum Mechanics** under **Approximation Methods**.

Key focus areas include mastery of fundamental concepts, manipulation of governing differential and algebraic equations, application of rigorous problem-solving algorithms, and avoidance of common conceptual errors.

---

## Difficulty & Prerequisites
- **Difficulty Rating**: 5 / 5
- **Prerequisites**:
  - `qm.schrodinger.harmonic_oscillator`

---

## Core Theoretical Concepts
- **Non-degenerate perturbation theory**: Physical principles, contextual constraints, and analytical representations.
- **Degenerate perturbation theory**: Physical principles, contextual constraints, and analytical representations.
- **First-order energy correction**: Physical principles, contextual constraints, and analytical representations.
- **Fermi's golden rule**: Physical principles, contextual constraints, and analytical representations.
- **Harmonic perturbation**: Physical principles, contextual constraints, and analytical representations.
- **Transition rate**: Physical principles, contextual constraints, and analytical representations.

---

## Governing Equations & Mathematical Formulations
$$
E_n^{(1)} = \langle \psi_n^{(0)} | \hat H' | \psi_n^{(0)} \rangle
$$
$$
E_n^{(2)} = \sum_{k\neq n} \frac{|\langle \psi_k^{(0)} | \hat H' | \psi_n^{(0)} \rangle|^2}{E_n^{(0)} - E_k^{(0)}}
$$
$$
\Gamma_{i\to f} = \frac{2\pi}{\hbar}|\langle f | \hat H' | i \rangle|^2 \rho(E_f)
$$

---

## Step-by-Step Analytical & Problem-Solving Methods
1. **Identify unperturbed Hamiltonian H0 and small perturbation H'**
2. **Compute first-order energy shift by sandwiching H' between unperturbed eigenstates**
3. **Diagonalize degenerate subspace for degenerate energy levels**
4. **Apply Fermi's Golden Rule for transitions induced by time-dependent perturbations**

---

## Standard Problem Archetypes & Applications
- **Stark effect in hydrogen atom**
- **Anharmonic oscillator perturbations (x^3, x^4 terms)**
- **Radiative transition rates and absorption cross-sections**

---

## Common Pitfalls, Edge Cases & Anti-Patterns
- > [!WARNING]
  > Applying non-degenerate perturbation formulas when unperturbed states are degenerate
- > [!WARNING]
  > Neglecting higher-order terms when perturbation magnitude is not small compared to level spacing

---

## Knowledge Graph & Related Skills
- `qm.schrodinger.harmonic_oscillator`
- `qm.scattering.theory`

---

## References & Academic Bibliography
- Griffiths Quantum Mechanics Ch.6-7
- Sakurai Modern Quantum Mechanics Ch.5
