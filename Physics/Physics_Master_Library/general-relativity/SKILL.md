---
name: general-relativity
description: "Work with general relativity: spacetime curvature, metrics, geodesics, Einstein field equations, Schwarzschild and Kerr black holes, gravitational waves, gravitational lensing, redshift, FLRW cosmology, tensor calculus. Use for black holes, gravity beyond Newton, or differential-geometry questions in physics."
---

# General Relativity

## Mathematical tools
- Metric g_μν; ds² = g_μν dx^μ dx^ν (signature -+++ or +---: state it!)
- Christoffel Γ^λ_μν = ½g^{λσ}(∂_μg_σν + ∂_νg_σμ - ∂_σg_μν)
- Geodesic: d²x^λ/dτ² + Γ^λ_μν (dx^μ/dτ)(dx^ν/dτ) = 0
- Riemann R^ρ_σμν, Ricci R_μν, scalar R; Bianchi identity ∇_μ G^μν = 0
- Covariant derivative, parallel transport, Killing vectors ↔ conserved quantities

## Einstein equations
G_μν + Λg_μν = (8πG/c⁴) T_μν. Vacuum: R_μν = 0 (Λ=0). Weak field: g = η + h, □h̄_μν = -(16πG/c⁴)T_μν; Newtonian limit g_00 ≈ -(1+2Φ/c²).

## Schwarzschild (non-rotating, mass M)
- r_s = 2GM/c²; ds² = -(1-r_s/r)c²dt² + dr²/(1-r_s/r) + r²dΩ²
- Gravitational redshift sqrt(1 - r_s/r); ISCO r = 3r_s; photon sphere r = 1.5r_s
- Perihelion precession Δφ = 6πGM/(c²a(1-e²)) per orbit (Mercury 43"/century)
- Light deflection α = 4GM/(c²b) (twice Newtonian); Shapiro delay; lensing Einstein radius θ_E = sqrt(4GM D_LS/(c² D_L D_S))
- Hawking temperature T = ħc³/(8πGMk_B); Bekenstein-Hawking S = k_B c³A/(4Għ)
- Kerr: spin a = J/Mc; ergosphere; frame dragging; horizons r± = (GM/c²)(1 ± sqrt(1 - a²))

## Gravitational waves
- Linearized TT gauge: two polarizations (+, ×); speed c
- Quadrupole formula: P = (G/5c⁵)⟨d³Q_ij/dt³ d³Q_ij/dt³⟩
- Compact binary: strain h ~ (G M_c)^{5/3}(π f)^{2/3}/(c⁴ d); chirp mass M_c = (m1m2)^{3/5}/(m1+m2)^{1/5}
- Detectors: LIGO/Virgo/KAGRA interferometers; pulsar timing arrays; LISA

## Method
Pick coordinates exploiting symmetry → compute metric components → find conserved quantities from Killing vectors → reduce geodesic to effective potential → interpret with proper-time vs coordinate-time care.
