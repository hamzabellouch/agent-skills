---
name: statistical-mechanics
description: "Use statistical mechanics: microstates, ensembles, partition functions, Boltzmann/Fermi-Dirac/Bose-Einstein distributions, Ising model, phase transitions, blackbody, Bose-Einstein condensation, fluctuations, renormalization group. Use to connect microscopic physics to thermodynamics."
---

# Statistical Mechanics

## Foundations
- Boltzmann entropy S = k_B ln Ω; Gibbs S = -k_B Σ p_i ln p_i
- Ensembles: microcanonical (E,V,N), canonical (T,V,N) with Z = Σ e^{-βE_i}, grand canonical (T,V,μ) with Ξ = Σ e^{-β(E-μN)}
- Canonical: F = -k_B T ln Z; ⟨E⟩ = -∂lnZ/∂β; C_V = k_B β² ∂²lnZ/∂β²; Var(E) = k_B T² C_V
- Equipartition: ½k_BT per quadratic degree of freedom (fails when quantum effects freeze modes)
- Maxwell-Boltzmann speed: f(v) = 4π(m/2πk_BT)^{3/2} v² e^{-mv²/2k_BT}; v_mp = sqrt(2k_BT/m), ⟨v⟩ = sqrt(8k_BT/πm)

## Quantum statistics
- Occupancy ⟨n⟩ = 1/(e^{β(ε-μ)} ± 1) (+ fermions, - bosons)
- Fermi gas: E_F = ħ²(3π²n)^{2/3}/2m; degeneracy pressure; Sommerfeld C ∝ T
- Bose gas: T_c = (2πħ²/mk_B)(n/ζ(3/2))^{2/3}; condensate below T_c
- Photon gas: u = (π²/15)(k_BT)⁴/(ħc)³; Planck: B(ν) ∝ ν³/(e^{hν/kT}-1)
- Debye model: C_V ∝ T³ at low T; Einstein model for optical modes; Dulong-Petit 3Nk at high T

## Models and phase transitions
- Two-level system: Z = 1 + e^{-βΔ}; Schottky anomaly
- Ising model: 1D exact, no transition at T>0; 2D Onsager T_c = 2J/(k_B ln(1+√2)); mean-field T_c = zJ/k_B
- Landau theory: F = a(T-T_c)m² + b m⁴; critical exponents; universality
- Renormalization group: fixed points, relevant/irrelevant operators, scaling relations
- Fluctuation-dissipation theorem; Brownian motion D = k_BT/γ (Einstein); Langevin and Fokker-Planck equations
- Boltzmann equation, H-theorem, kinetic theory; Onsager reciprocal relations

## Workflow
Enumerate states → write Z → derive thermodynamics by derivatives → check high/low-T limits.
