---
name: physical-constants-and-units
description: "Look up physical constants, unit conversions, and derived scales (CODATA values) for any physics calculation; includes a Python helper and JSON data file. Use whenever a calculation needs fundamental constants, SI/CGS/natural-unit conversions, astronomical data, or energy-wavelength-temperature equivalences."
---


# Physical Constants & Units

## Use
- Prefer `references/constants.json` (CODATA 2022; exact SI defining constants flagged) and `scripts/constants.py` helpers instead of recalling digits from memory.
- Run `python scripts/constants.py` to list everything, or `python scripts/constants.py G hbar` for specific values.

## Unit systems
- SI base: m, kg, s, A, K, mol, cd. Since 2019 h, e, k_B, N_A, c are exact.
- CGS (Gaussian) ↔ SI for EM: Coulomb law F = q1q2/r² (Gaussian) vs q1q2/4πε0r² (SI); B in gauss (1 T = 1e4 G); e²/ħc = α in Gaussian.
- Natural units ħ = c = 1: [E] = [mass] = [1/length] = [1/time]; ħc = 197.327 MeV·fm; 1 GeV⁻¹ = 0.1973 fm = 6.58e-25 s.
- Atomic units ħ = m_e = e = 4πε0 = 1: length a0, energy Hartree (27.211 eV), time 2.42e-17 s.
- Astronomical: AU, pc (3.26 ly), M☉, solar luminosity; Jansky 1e-26 W m⁻² Hz⁻¹.

## Handy equivalences
- 1 eV ≙ 11604.5 K ≙ 241.8 THz ≙ 1239.84 nm ≙ 8065.5 cm⁻¹
- Photon energy E[eV] = 1239.84/λ[nm]
- 1 u = 931.494 MeV/c²; m_e c² = 0.511 MeV; m_p c² = 938.272 MeV
- 1 Gauss = 1e-4 T; 1 atm = 101325 Pa; 1 cal = 4.184 J; 1 Å = 0.1 nm; 1 barn = 1e-28 m²

## Rules
Convert everything to a single system before calculating; keep units in the working; report with appropriate significant figures; cite the constant set (CODATA year).

