---
name: electrodynamics-maxwell
description: "Work with Maxwell's equations and electromagnetic radiation: induction, Faraday's law, EM waves, Poynting vector, radiation from accelerating charges, waveguides, transmission lines, AC circuits, gauge theory, retarded potentials. Use for time-varying fields, antennas, EM waves in media."
---

# Electrodynamics

## Maxwell's equations (SI)
∇·E = ρ/ε0; ∇·B = 0; ∇×E = -∂B/∂t; ∇×B = μ0J + μ0ε0 ∂E/∂t. Lorentz force F = q(E + v×B). c = 1/sqrt(μ0ε0).

## Key results
- Faraday EMF = -dΦ/dt; Lenz's law; inductance L, energy ½LI²; mutual inductance M
- Potentials: E = -∇φ - ∂A/∂t; gauges (Lorenz: ∇·A + (1/c²)∂φ/∂t = 0); retarded solution φ(r,t) = (1/4πε0)∫ρ(r',t_r)/|r-r'| dV'
- Plane wave: E = E0 cos(k·r - ωt), B = k̂×E/c; ω = ck; energy density u = ε0E²; Poynting S = E×B/μ0; intensity I = ½cε0E0²; radiation pressure I/c (absorb), 2I/c (reflect)
- In matter: v = c/n, n = sqrt(εrμr); Fresnel: normal incidence R = ((n1-n2)/(n1+n2))²; Brewster tan θ_B = n2/n1; total internal reflection sinθ_c = n2/n1
- Conductors: skin depth δ = sqrt(2/μσω); plasma frequency ω_p = sqrt(ne²/mε0)
- Larmor radiation: P = q²a²/(6πε0c³); dipole radiation angular pattern sin²θ; Liénard for relativistic charges; synchrotron radiation
- Waveguides: cutoff frequency, TE/TM modes; rectangular f_c = (c/2)sqrt((m/a)²+(n/b)²)
- Transmission lines: Z0 = sqrt(L/C); reflection coefficient Γ = (Z_L - Z0)/(Z_L + Z0); VSWR
- AC circuits: Z_R = R, Z_L = iωL, Z_C = 1/iωC; resonance ω0 = 1/sqrt(LC); power P = V_rms I_rms cosφ
- Covariant formulation: F^{μν}, ∂_μF^{μν} = μ0J^ν; invariants E²-c²B², E·B

## Workflow
Specify sources and media → choose potentials or fields → solve wave equation with boundary conditions → compute energy flux and check conservation (Poynting theorem).
