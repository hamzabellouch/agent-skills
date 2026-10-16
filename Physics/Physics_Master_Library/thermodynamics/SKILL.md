---
name: thermodynamics
description: "Apply classical thermodynamics: laws of thermodynamics, ideal and real gases, heat engines, entropy, free energies, phase transitions, Carnot cycle, Maxwell relations, heat transfer. Use for heat, temperature, efficiency, entropy, or equations of state."
---

# Thermodynamics

## Laws
0. Thermal equilibrium is transitive → temperature.
1. dU = δQ - δW (W by system); for gas δW = p dV.
2. dS ≥ δQ/T; isolated system entropy never decreases; Clausius, Kelvin-Planck statements.
3. S → const (0 for perfect crystal) as T → 0; unattainability of absolute zero.

## Essentials
- Ideal gas pV = nRT = N k_B T; U = (f/2) N k_B T; C_V = (f/2)R; C_p - C_V = R; γ = C_p/C_V
- Adiabatic reversible: pV^γ = const; TV^{γ-1} = const
- Isothermal work W = nRT ln(V2/V1)
- Carnot efficiency η = 1 - T_c/T_h; COP refrigerator = T_c/(T_h - T_c)
- Entropy change ideal gas ΔS = nC_V ln(T2/T1) + nR ln(V2/V1)
- Potentials: U, H = U+pV, F = U-TS, G = H-TS; dG = -SdT + Vdp + μdN
- Maxwell relations e.g. (∂S/∂V)_T = (∂p/∂T)_V
- Clausius-Clapeyron: dp/dT = L/(TΔv)
- van der Waals: (p + a n²/V²)(V - nb) = nRT; critical T_c = 8a/27Rb
- Heat transfer: conduction q = -k∇T; convection q = hAΔT; radiation P = εσAT⁴ (σ = 5.670e-8 W m⁻² K⁻⁴); Wien λ_max T = 2.898e-3 m·K
- Cycles: Otto η = 1 - r^{1-γ}; Diesel, Brayton, Rankine; each has T-S and p-V description.
- Phase transitions: first order (latent heat) vs second order (continuous); Gibbs phase rule F = C - P + 2.

## Method
Identify system, process path (isothermal, adiabatic, isobaric, isochoric), state variables at each point; compute Q, W, ΔU, ΔS; verify second law with total entropy change ≥ 0.
