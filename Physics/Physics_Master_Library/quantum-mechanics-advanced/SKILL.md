---
name: quantum-mechanics-advanced
description: "Apply advanced quantum methods: perturbation theory, variational method, WKB, scattering theory, density matrices, path integrals, Berry phase, time-dependent perturbation, Fermi's golden rule, open quantum systems. Use for approximations, fine structure, Stark/Zeeman, transitions, decoherence."
---

# Quantum Mechanics: Advanced Methods

## Approximation methods
- Non-degenerate perturbation: E_n^(1) = ⟨n|H'|n⟩; E_n^(2) = Σ_{m≠n}|⟨m|H'|n⟩|²/(E_n - E_m); |n^(1)⟩ = Σ ⟨m|H'|n⟩/(E_n - E_m)|m⟩
- Degenerate: diagonalize H' in the degenerate subspace (good basis)
- Variational: E_0 ≤ ⟨ψ_trial|H|ψ_trial⟩/⟨ψ|ψ⟩; minimize over parameters (He ground state ≈ -77.5 eV with Z_eff = 27/16)
- WKB: ∮ p dx = (n+½)2πħ; tunneling exp(-(2/ħ)∫|p|dx)
- Hydrogen corrections: fine structure (relativistic + spin-orbit ∝ α² E_n), Lamb shift, hyperfine (21 cm line, 1420 MHz), Zeeman (weak: g_J μ_B B m_J; strong: Paschen-Back), Stark (linear for n=2)

## Time dependence
- Interaction picture; first-order amplitude c_f = -(i/ħ)∫⟨f|H'|i⟩e^{iω_fi t}dt
- Fermi's golden rule: Γ = (2π/ħ)|⟨f|H'|i⟩|² ρ(E_f)
- Rabi oscillations: P(t) = (Ω²/Ω_eff²) sin²(Ω_eff t/2); rotating-wave approximation
- Adiabatic theorem; Berry phase γ = i∮⟨n|∇_R n⟩·dR; Aharonov-Bohm effect (phase q∮A·dl/ħ)
- Sudden approximation

## Scattering
- Cross section dσ/dΩ = |f(θ)|²; Born: f = -(m/2πħ²)∫e^{-iq·r}V(r)dr; Rutherford dσ/dΩ = (Z1Z2e²/4E sin²(θ/2))²/(4πε0)²
- Partial waves: f(θ) = Σ(2l+1)(e^{2iδ_l}-1)/(2ik) P_l(cosθ); σ = (4π/k²)Σ(2l+1)sin²δ_l; optical theorem σ = (4π/k) Im f(0)
- Low energy: scattering length a, σ = 4πa²; resonances Breit-Wigner

## Density matrix & open systems
- ρ = Σ p_i|ψ_i⟩⟨ψ_i|; purity Trρ²; von Neumann S = -Tr ρ lnρ; partial trace for subsystems
- Lindblad: dρ/dt = -i[H,ρ]/ħ + Σ γ(LρL† - ½{L†L,ρ}); decoherence, T1/T2
- Path integral: K = ∫Dx exp(iS/ħ); free propagator; Wick rotation to statistical mechanics
- Symmetries: parity, time reversal, Wigner-Eckart theorem, selection rules
