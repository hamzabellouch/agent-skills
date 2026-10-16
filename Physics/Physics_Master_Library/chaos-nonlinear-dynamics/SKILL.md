---
name: chaos-nonlinear-dynamics
description: "Study nonlinear dynamics and chaos: fixed points, stability, bifurcations, limit cycles, Lyapunov exponents, strange attractors, logistic map, Lorenz system, fractals, synchronization, pattern formation, complex systems. Use for chaotic or nonlinear systems."
---

# Chaos & Nonlinear Dynamics

## Toolkit
- Phase space; fixed points where f(x*) = 0; linear stability via Jacobian eigenvalues (negative real part → stable; imaginary → oscillation)
- 1D flows: saddle-node, transcritical, pitchfork, Hopf bifurcations; normal forms
- Limit cycles: Poincaré-Bendixson (2D no chaos), van der Pol oscillator, relaxation oscillations
- Chaos requires ≥3D continuous flow or 1D noninvertible map; sensitive dependence: δ(t) ≈ δ0 e^{λt} with Lyapunov exponent λ > 0
- Logistic map x_{n+1} = r x_n(1 - x_n): period doubling cascade, Feigenbaum δ = 4.669..., chaos at r ≈ 3.5699, windows of periodicity
- Lorenz system: σ=10, ρ=28, β=8/3; butterfly attractor; fractal dimension ≈ 2.06
- Measures: Lyapunov spectrum, correlation dimension, Kolmogorov-Sinai entropy, bifurcation diagram, Poincaré section, return map, power spectrum
- Fractals: Cantor set, Koch curve, box-counting dimension D = lim ln N(ε)/ln(1/ε)
- Hamiltonian chaos: KAM theorem, resonances, Poincaré sections, standard map, kicked rotor (quantum analog), billiards, three-body problem
- Synchronization: Kuramoto model; coupled oscillators; chimera states
- Pattern formation: Turing instability, reaction-diffusion, Rayleigh-Bénard convection, Swift-Hohenberg
- Quantum chaos: random matrix theory, level statistics (Wigner-Dyson), OTOCs, scrambling
- Time series: Takens embedding, nonlinear prediction, noise vs determinism tests

## Approach
Find fixed points → linearize → classify → vary parameter → numerically compute orbits and Lyapunov exponents; report diagrams with parameter values.
