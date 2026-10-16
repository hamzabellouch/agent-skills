---
name: quantum-field-theory
description: "Teach quantum field theory: canonical quantization, path integrals, Feynman rules, renormalization, QED, gauge theories, spontaneous symmetry breaking, effective field theory, Dirac equation, anomalies, CFT. Use for field-theoretic calculations and conceptual questions."
---

# Quantum Field Theory

## Foundations
- Natural units ħ=c=1; metric (+,-,-,-); action S = ∫d⁴x L
- Free scalar: L = ½(∂φ)² - ½m²φ²; Klein-Gordon; φ = ∫d³p/((2π)³ 2E)(a e^{-ipx} + a† e^{ipx}); [a_p, a†_q] = (2π)³2E δ³
- Dirac field: (iγ·∂ - m)ψ = 0; spinors u, v; Weyl and Majorana fermions; spin-statistics
- Propagators: scalar i/(p²-m²+iε); fermion i(p̸+m)/(p²-m²+iε); photon -ig_μν/(k²+iε) (Feynman gauge)

## Interactions
- Interaction picture, Dyson series, Wick's theorem; LSZ reduction relates S-matrix to correlators
- Path integral Z[J] = ∫Dφ e^{i(S+Jφ)}; generating functionals; Euclidean continuation
- Feynman rules: vertices, propagators, loop integrals, symmetry factors
- QED: L = ψ̄(iD̸ - m)ψ - ¼F², D = ∂ + ieA; Compton scattering, Møller, e⁺e⁻ → μ⁺μ⁻ (σ = 4πα²/3s); anomalous magnetic moment a_e = α/2π + ... (match experiment to ~12 digits)
- Yang-Mills theories: non-abelian L = -¼F^a F^a; ghosts; BRST symmetry

## Renormalization
- UV divergences; regularization (cutoff, dimensional d = 4-ε, Pauli-Villars); counterterms; renormalization conditions
- Running couplings: β(g) = μ dg/dμ; QED β>0 (Landau pole), QCD β<0 (asymptotic freedom); Callan-Symanzik equation
- Wilsonian EFT: integrate out heavy modes; relevant, marginal, irrelevant operators; naturalness

## Symmetry
- Noether currents; spontaneous symmetry breaking and Goldstone theorem; Higgs mechanism; Ward-Takahashi identities; chiral symmetry and anomalies (ABJ, π⁰→γγ)
- Instantons, solitons (kinks, monopoles, skyrmions), thermal field theory, curved-space QFT (Unruh, Hawking effects), AdS/CFT, conformal field theory (primary operators, central charge)
