---
name: quantum-mechanics-fundamentals
description: "Solve foundational quantum mechanics: Schrodinger equation, wavefunctions, operators, uncertainty principle, infinite well, harmonic oscillator, hydrogen atom, angular momentum, spin, tunneling, Dirac notation. Use for any question about quantum states, energy levels, or measurement."
---

# Quantum Mechanics: Fundamentals

## Postulates
State |ψ⟩ in Hilbert space; observables = Hermitian operators; outcomes are eigenvalues with Born probability |⟨a|ψ⟩|²; time evolution iħ ∂_t|ψ⟩ = H|ψ⟩; collapse on measurement.

## Essentials
- TDSE iħ∂ψ/∂t = -ħ²/2m ∇²ψ + Vψ; TISE Hψ = Eψ; ψ(t) = Σ c_n e^{-iE_n t/ħ}φ_n
- Commutators: [x,p] = iħ; Heisenberg ΔAΔB ≥ ½|⟨[A,B]⟩|; ΔxΔp ≥ ħ/2; ΔEΔt heuristic
- Probability current j = (ħ/2mi)(ψ*∇ψ - ψ∇ψ*)
- Infinite well width L: E_n = n²π²ħ²/2mL², ψ_n = sqrt(2/L) sin(nπx/L)
- Harmonic oscillator: E_n = ħω(n+½); ladder a, a†; [a,a†]=1; x = sqrt(ħ/2mω)(a+a†); ψ_n via Hermite polynomials
- Finite barrier tunneling: T ≈ exp(-2∫κ dx), κ = sqrt(2m(V-E))/ħ
- Delta potential bound state E = -mα²/2ħ²
- Angular momentum: [L_i,L_j] = iħε_ijk L_k; L²|l,m⟩ = ħ²l(l+1), L_z = ħm; spherical harmonics Y_lm
- Spin-½: Pauli matrices σ_x,σ_y,σ_z; S = ħσ/2; rotation operator exp(-iσ·nθ/2); Stern-Gerlach
- Hydrogen: E_n = -13.6 eV/n²; degeneracy n²; a0 = 0.529 Å; radial R_nl with Laguerre polynomials; selection rules Δl = ±1, Δm = 0,±1
- Addition of angular momentum: Clebsch-Gordan; two spin-½ → triplet and singlet
- Identical particles: bosons symmetric, fermions antisymmetric (Pauli exclusion); exchange interaction
- Free particle wave packet spreads: σ(t) = σ0 sqrt(1 + (ħt/2mσ0²)²)
- Ehrenfest theorem: d⟨x⟩/dt = ⟨p⟩/m; d⟨p⟩/dt = -⟨∇V⟩

## Method
1. Write H. 2. Solve TISE (analytic, ladder operators, or numerically via finite differences/shooting). 3. Normalize. 4. Compute expectation values and probabilities. 5. Check against limits (ħ→0 classical; large n correspondence principle).
