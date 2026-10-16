---
name: plasma-physics
description: "Analyze plasmas: Debye shielding, plasma frequency, single particle motion, MHD, waves in plasmas, instabilities, fusion confinement, space and solar plasmas, magnetic reconnection, kinetic theory (Vlasov). Use for ionized gases, fusion devices, solar wind, auroras."
---

# Plasma Physics

## Parameters
- Debye length λ_D = sqrt(ε0 k_B T/(n e²)); plasma parameter N_D = (4π/3)nλ_D³ ≫ 1
- Plasma frequency ω_p = sqrt(ne²/(ε0 m)) ≈ 56.4 sqrt(n[m⁻³]) rad/s for electrons
- Gyrofrequency Ω = qB/m; gyroradius ρ = mv⊥/(|q|B); plasma beta β = 2μ0 nkT/B²
- Collision frequency and Coulomb logarithm; Spitzer resistivity ∝ T^{-3/2}

## Single-particle motion
- E×B drift v = E×B/B²; ∇B drift; curvature drift; polarization drift
- Adiabatic invariant μ = mv⊥²/2B; magnetic mirror (loss cone sin²θ = B_min/B_max); Van Allen belts

## Fluid & kinetic models
- Two-fluid, MHD: ρ dv/dt = J×B - ∇p; ∂B/∂t = ∇×(v×B) + η∇²B; magnetic Reynolds number R_m; frozen-in flux; Alfvén speed v_A = B/sqrt(μ0ρ)
- Magnetic pressure B²/2μ0; Z-pinch and θ-pinch; Grad-Shafranov equilibrium; safety factor q
- Vlasov equation ∂f/∂t + v·∇f + (q/m)(E + v×B)·∂f/∂v = 0; Landau damping; Bohm-Gross dispersion ω² = ω_p² + 3k²v_th²

## Waves & instabilities
- Electromagnetic waves in plasma n² = 1 - ω_p²/ω²; cutoff, resonance; whistler, Alfvén, magnetosonic, ion-acoustic waves
- Instabilities: Rayleigh-Taylor, kink, sausage, two-stream, Kelvin-Helmholtz, tearing mode; ELMs in tokamaks
- Magnetic reconnection: Sweet-Parker rate, Petschek, plasmoid; solar flares and substorms

## Applications
- Fusion: tokamak ITER (B ~ 5 T, Q = 10 goal), stellarator W7-X, ICF; triple product; heating (ohmic, NBI, ICRH); divertors
- Space & astro: solar wind, corona heating, heliosphere, auroras, pulsar magnetospheres, dynamo theory
- Industry: plasma etching, thrusters, arcs, lighting
