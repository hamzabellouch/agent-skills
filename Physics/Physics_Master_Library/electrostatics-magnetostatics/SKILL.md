---
name: electrostatics-magnetostatics
description: "Solve static electric and magnetic field problems: Coulomb's law, Gauss's law, potentials, capacitance, dielectrics, Poisson/Laplace equations, image charges, multipoles, Biot-Savart, Ampere's law, magnetic materials. Use for charges, circuits fields, capacitors, magnets."
---

# Electrostatics & Magnetostatics

## Electrostatics
- Coulomb: F = q1q2/(4πε0 r²); E = F/q; V = -∫E·dl; E = -∇V
- Gauss: ∮E·dA = Q_enc/ε0; use with spherical, cylindrical, planar symmetry
- Poisson ∇²V = -ρ/ε0; Laplace ∇²V = 0 (unique solution given boundary conditions)
- Methods: separation of variables, image charges (grounded plane: -q at mirror point; grounded sphere: q' = -qR/d at R²/d), Green's functions, conformal mapping (2D)
- Multipoles: V = (1/4πε0)Σ (1/r^{l+1}) ∫ r'^l P_l(cosθ) ρ dV; dipole V = p cosθ/(4πε0 r²)
- Energy U = ½∫ε0E² dV = ½∫ρV dV; capacitor C = Q/V (parallel plate ε0A/d; sphere 4πε0R; coax 2πε0L/ln(b/a)); energy ½CV²
- Dielectrics: D = ε0E + P = εE; bound charge σ_b = P·n̂, ρ_b = -∇·P; C increases by κ

## Magnetostatics
- Biot-Savart: B = (μ0/4π)∫ I dl×r̂/r²; Ampere: ∮B·dl = μ0 I_enc
- Solenoid B = μ0 n I; toroid B = μ0NI/2πr; infinite wire B = μ0I/2πr; loop axis B = μ0IR²/2(R²+z²)^{3/2}
- Vector potential B = ∇×A, ∇²A = -μ0 J (Coulomb gauge)
- Force: F = qv×B; on wire F = IL×B; magnetic moment m = IA; torque τ = m×B
- Magnetic materials: B = μ0(H + M); dia-, para-, ferromagnetism; hysteresis; boundary conditions for B⊥, H∥
- Lorentz force trajectories: radius r = mv/qB, cyclotron ω = qB/m; E×B drift v = E/B

## Boundary conditions
E∥ continuous, E⊥ jumps by σ/ε0; B⊥ continuous, B∥ jumps by μ0K.

## Tips
Always exploit symmetry first; check by dimensional analysis (V ~ q/4πε0r) and limiting behavior (far field → point charge).
