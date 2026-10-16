---
name: oscillations-and-waves
description: "Handle oscillators and waves: simple, damped, driven harmonic motion, resonance, coupled oscillators, normal modes, wave equation, standing waves, superposition, dispersion, Doppler effect, Fourier analysis. Use for springs, pendulums, strings, sound and wave phenomena."
---

# Oscillations & Waves

## Oscillators
- SHM: ẍ + ω0² x = 0; ω0 = sqrt(k/m); pendulum ω0 = sqrt(g/L) (small angle); physical pendulum ω0 = sqrt(mgd/I)
- Damped: ẍ + 2γẋ + ω0² x = 0. Under (γ<ω0): ω_d = sqrt(ω0² - γ²); critical γ=ω0; over γ>ω0. Q = ω0/2γ
- Driven: amplitude A(ω) = (F0/m)/sqrt((ω0²-ω²)² + 4γ²ω²); resonance near ω0 (peak at sqrt(ω0² - 2γ²)); phase lag δ = atan(2γω/(ω0²-ω²))
- Coupled: solve det(K - ω²M) = 0 for normal modes; N-chain dispersion ω = 2 sqrt(k/m)|sin(ka/2)|

## Waves
- 1D wave equation: ∂²y/∂t² = v² ∂²y/∂x²; general y = f(x-vt) + g(x+vt)
- String v = sqrt(T/μ); sound in gas v = sqrt(γRT/M); phase v_p = ω/k; group v_g = dω/dk
- Standing waves: fixed-fixed f_n = n v/2L; open-closed pipe f_n = (2n-1)v/4L
- Intensity I ∝ A²; decibel β = 10 log10(I/10⁻¹² W/m²)
- Doppler: f' = f (v ± v_o)/(v ∓ v_s); relativistic version in special-relativity skill
- Interference: constructive path difference mλ; beats f_b = |f1 - f2|
- Fourier: any periodic function = sum of harmonics; use FFT for numeric spectra; uncertainty Δω Δt ≳ 1/2.
- Energy in oscillator averaged over a cycle: ½kA².

## Pitfalls
Small-angle approximation fails above ~15° for precision work; exact period T = 4 sqrt(L/g) K(sin(θ0/2)).
