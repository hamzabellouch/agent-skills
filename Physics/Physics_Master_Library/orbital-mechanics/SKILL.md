---
name: orbital-mechanics
description: "Compute orbits and trajectories: Kepler's laws, vis-viva, orbital elements, Hohmann and bi-elliptic transfers, escape velocity, three-body problem, Lagrange points, tidal forces. Use for satellites, planets, spacecraft, and gravitational two-body questions."
---

# Orbital Mechanics

## Core results
- Gravity: F = GMm/r²; μ = GM (Earth 3.986e14 m³/s², Sun 1.327e20 m³/s²)
- Circular speed v_c = sqrt(μ/r); period T = 2π sqrt(a³/μ) (Kepler III)
- Vis-viva: v² = μ(2/r - 1/a)
- Specific energy ε = -μ/2a; angular momentum h = r×v; eccentricity e = sqrt(1 + 2εh²/μ²)
- Conic: r = a(1-e²)/(1 + e cosν). e=0 circle, 0<e<1 ellipse, e=1 parabola, e>1 hyperbola
- Escape speed v_esc = sqrt(2μ/r) = √2 v_c
- Kepler's equation: M = E - e sin E (solve by Newton iteration)
- Six orbital elements: a, e, i, Ω (RAAN), ω (arg. periapsis), ν (or M)

## Maneuvers
- Hohmann transfer: Δv1 = sqrt(μ/r1)(sqrt(2r2/(r1+r2)) - 1); Δv2 = sqrt(μ/r2)(1 - sqrt(2r1/(r1+r2))); transfer time = π sqrt((r1+r2)³/8μ)
- Plane change: Δv = 2v sin(Δi/2) (cheapest at apoapsis)
- Tsiolkovsky: Δv = I_sp g0 ln(m0/mf)
- Gravity assist: speed change in the planet frame is zero; heliocentric gain comes from vector rotation.

## Perturbations & many-body
- J2 oblateness: nodal regression dΩ/dt = -3/2 J2 (R/p)² n cos i (sun-synchronous orbits)
- Hill sphere r_H ≈ a (m/3M)^{1/3}; Roche limit d ≈ 2.44 R (ρ_M/ρ_m)^{1/3}
- Lagrange points L1–L5 in circular restricted 3-body problem; L4/L5 stable if M1/M2 > 24.96
- Tidal acceleration ≈ 2GMr/d³

## Method
Compute energy and angular momentum first; they fix the orbit. Use numerical integration (see numerical-simulation-physics) for perturbed or N-body cases, with symplectic integrators for long runs.
