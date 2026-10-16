---
name: fluid-mechanics
description: "Solve fluid statics and dynamics: pressure, buoyancy, Bernoulli, continuity, viscosity, Reynolds number, Navier-Stokes, boundary layers, drag, turbulence, surface tension. Use for pipes, flow, lift, drag, hydrostatics."
---

# Fluid Mechanics

## Statics
- Hydrostatic p = p0 + ρgh; Pascal's principle; Archimedes: F_b = ρ_fluid V_disp g
- Surface tension: Laplace ΔP = 2γ/R (drop), 4γ/R (bubble); capillary rise h = 2γcosθ/(ρgr)

## Dynamics
- Continuity: ∇·(ρv) + ∂ρ/∂t = 0; incompressible A1v1 = A2v2
- Bernoulli (steady, inviscid, incompressible along a streamline): p + ½ρv² + ρgz = const
- Navier-Stokes (incompressible): ρ(∂v/∂t + v·∇v) = -∇p + μ∇²v + ρg
- Reynolds number Re = ρvL/μ; laminar pipe flow Re < ~2300
- Poiseuille: Q = πR⁴ΔP/(8μL)
- Stokes drag on sphere (low Re): F = 6πμRv; terminal velocity v = 2R²(ρ_s-ρ_f)g/(9μ)
- Drag: F = ½ρC_d A v²; lift F = ½ρC_L A v²
- Vorticity ω = ∇×v; Kelvin's circulation theorem; potential flow with stream function ψ
- Compressible flow: Mach M = v/c; isentropic relations; shock waves for M>1; choked flow at M=1 in nozzles
- Dimensionless numbers: Froude, Mach, Prandtl, Rayleigh (convection onset Ra ≈ 1708), Strouhal, Weber

## Approach
1. Decide regime: Re, Ma, viscous or inviscid, steady or unsteady.
2. Select conservation law (mass, momentum, energy) in integral form for control volumes.
3. Non-dimensionalize to find controlling parameters; use scaling to estimate.
4. For numerics: finite volume/difference; check CFL condition.
