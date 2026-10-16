---
name: semiconductor-device-physics
description: "Explain semiconductors and devices: doping, carrier statistics, p-n junctions, diodes, transistors (BJT, MOSFET), LEDs, laser diodes, solar cells, heterostructures, quantum wells, photodetectors. Use for electronics physics, chips, photovoltaics, and optoelectronics."
---

# Semiconductor & Device Physics

## Carriers
- Intrinsic n_i = sqrt(N_c N_v) exp(-E_g/2kT); Si E_g = 1.12 eV, Ge 0.67, GaAs 1.42 (direct)
- n p = n_i² (mass action); doping: donors (n-type), acceptors (p-type); Fermi level shifts
- Drift J = qnμE, diffusion J = qD dn/dx; Einstein relation D/μ = kT/q
- Recombination: SRH, radiative, Auger; lifetime τ, diffusion length L = sqrt(Dτ)

## Junctions & diodes
- Built-in potential V_bi = (kT/q) ln(N_A N_D/n_i²); depletion width W = sqrt(2ε(V_bi - V)/q × (1/N_A + 1/N_D))
- Shockley: I = I_s(e^{qV/nkT} - 1); breakdown (Zener, avalanche); capacitance C = εA/W
- Metal-semiconductor Schottky barrier; ohmic contacts

## Transistors
- BJT: β = I_C/I_B; Ebers-Moll; amplifier small-signal models (g_m = I_C/V_T)
- MOSFET: threshold V_T; saturation I_D = ½μC_ox(W/L)(V_GS - V_T)²; subthreshold swing ≥ 60 mV/dec at 300 K; short-channel effects; FinFET and gate-all-around; scaling limits and Dennard scaling breakdown
- Memory: DRAM, Flash, emerging (MRAM, RRAM, FeFET)

## Optoelectronics
- LED efficiency (IQE, EQE), laser diode threshold and population inversion in double heterostructure
- Solar cell: I = I_L - I_0(e^{qV/kT} - 1); Shockley-Queisser limit ≈ 33% for single junction (E_g ≈ 1.34 eV); tandem and perovskite cells
- Photodiodes, avalanche photodiodes, CCD/CMOS sensors

## Nanostructures
- Quantum wells, wires, dots: confinement E_n ∝ 1/L²; 2DEG in HEMT; resonant tunneling; Coulomb blockade (E_C = e²/2C); single-electron transistor
