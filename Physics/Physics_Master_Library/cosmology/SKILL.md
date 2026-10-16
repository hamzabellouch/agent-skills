---
name: cosmology
description: "Explain cosmology: Big Bang, expansion, FLRW metric, Friedmann equations, dark matter, dark energy, CMB, inflation, nucleosynthesis, structure formation, Hubble tension. Use for the universe's origin, age, expansion, and composition."
---

# Cosmology

## Framework
- FLRW: ds² = -c²dt² + a(t)²[dr²/(1-kr²) + r²dΩ²]; redshift 1+z = a0/a
- Friedmann: H² = (8πG/3)ρ - kc²/a² + Λc²/3; acceleration ä/a = -(4πG/3)(ρ + 3p/c²) + Λc²/3
- Density parameters Ω_m, Ω_r, Ω_Λ, Ω_k; critical density ρ_c = 3H²/8πG ≈ 9.2e-27 kg/m³ (h=0.7)
- ΛCDM: Ω_Λ ≈ 0.69, Ω_m ≈ 0.31 (baryons ≈ 0.05, CDM ≈ 0.26), flat; H0 ≈ 67–73 km/s/Mpc (Hubble tension between CMB and local ladder); age ≈ 13.8 Gyr
- Equation of state w: matter 0, radiation 1/3, Λ -1; ρ ∝ a^{-3(1+w)}
- Distances: comoving, luminosity d_L = (1+z)d_M, angular diameter d_A = d_M/(1+z)

## Early universe
- Radiation era, matter-radiation equality z ≈ 3400, recombination z ≈ 1100 (T ≈ 3000 K), CMB T = 2.7255 K
- BBN: He-4 mass fraction ≈ 0.25, D/H ≈ 2.5e-5, Li problem; N_eff ≈ 3
- Inflation: solves horizon, flatness problems; slow-roll ε, η; scalar spectral index n_s ≈ 0.965; tensor-to-scalar r < ~0.036
- Baryogenesis, phase transitions (electroweak, QCD)

## Observables
- CMB: acoustic peaks (first peak ℓ ≈ 220 → flatness), polarization E and B modes, lensing, SZ effect
- Large-scale structure: BAO standard ruler (~150 Mpc), power spectrum P(k), growth factor, halo mass function, N-body simulations
- Supernovae Ia: discovery of acceleration (1998); weak lensing; cosmic shear
- Dark matter evidence: rotation curves, lensing, Bullet cluster, CMB; dark energy as Λ vs dynamical (DESI hints at evolving dark energy — consult recent literature)

## Computation tips
Integrate dz/E(z) with E(z) = sqrt(Ω_m(1+z)³ + Ω_r(1+z)⁴ + Ω_k(1+z)² + Ω_Λ); use numerical quadrature; use Planck or latest parameters, noting source.
