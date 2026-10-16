---
name: lagrangian-hamiltonian-mechanics
description: "Apply analytical mechanics: Lagrangian and Hamiltonian formalism, generalized coordinates, constraints, Euler-Lagrange equations, Noether's theorem, canonical transformations, Poisson brackets, Hamilton-Jacobi. Use for coupled systems, pendulums, constrained motion, symmetry and conservation law questions."
---

# Lagrangian & Hamiltonian Mechanics

## Procedure
1. Choose generalized coordinates q_i matching degrees of freedom (constraints eliminated).
2. Write T and V in those coordinates; L = T - V.
3. Euler-Lagrange: d/dt(∂L/∂q̇_i) - ∂L/∂q_i = Q_i (Q_i non-conservative generalized forces).
4. Conjugate momenta p_i = ∂L/∂q̇_i; Hamiltonian H = Σ p_i q̇_i - L.
5. Hamilton's equations: q̇_i = ∂H/∂p_i, ṗ_i = -∂H/∂q_i.
6. Look for cyclic coordinates (∂L/∂q = 0 → p conserved) and time-independence (H conserved).

## Concepts
- Noether: continuous symmetry ↔ conserved quantity (time→energy, space translation→momentum, rotation→angular momentum).
- Lagrange multipliers for holonomic constraints give constraint forces.
- Poisson bracket {f,g} = Σ(∂f/∂q ∂g/∂p - ∂f/∂p ∂g/∂q); df/dt = {f,H} + ∂f/∂t. Quantization: {,} → (1/iħ)[,].
- Canonical transformation preserves brackets; generating functions F1..F4.
- Hamilton-Jacobi: H(q, ∂S/∂q, t) + ∂S/∂t = 0. Action-angle variables for integrable systems.
- Liouville's theorem: phase-space volume is conserved.
- Charged particle: L = ½mv² - qφ + q v·A; p = mv + qA.
- Relativistic particle: L = -mc² sqrt(1 - v²/c²) - V.

## Classic examples
- Double pendulum (chaotic), bead on rotating hoop (bifurcation at ω² = g/R), Atwood machine, spherical pendulum, Kepler problem (reduce to effective potential U_eff = L²/2mr² - k/r).

## Pitfalls
- Check that T is quadratic in q̇ only for scleronomic systems; otherwise H ≠ E.
- Non-holonomic constraints (rolling without slipping on a surface in 3D) need multipliers, not coordinate elimination.
