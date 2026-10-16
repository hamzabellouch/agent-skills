---
name: dimensional-analysis-estimation
description: "Use dimensional analysis, scaling laws, order-of-magnitude and Fermi estimation to solve or sanity-check physics problems: Buckingham Pi theorem, natural units, similarity, back-of-envelope calculation. Use whenever the user wants a quick estimate or a check of units and scaling."
---

# Dimensional Analysis & Estimation

## Dimensional analysis
1. List all relevant variables and their dimensions [M, L, T, Θ, I].
2. Buckingham Pi: n variables, k independent dimensions → n - k dimensionless groups.
3. Express the answer as Π1 = f(Π2, ...); determine f by theory, limit, or experiment.
Examples: pendulum T ∝ sqrt(L/g); Taylor blast radius R ≈ (E t²/ρ)^{1/5}; drag via Re; pipe flow via friction factor.

## Natural scales
- Planck: l_P = sqrt(ħG/c³) = 1.6e-35 m; t_P = 5.4e-44 s; m_P = 2.2e-8 kg; E_P = 1.2e19 GeV
- Atomic: Bohr radius a0 = 0.529 Å, Hartree 27.2 eV, fine structure α ≈ 1/137
- Nuclear: fm, MeV; QCD scale ≈ 200 MeV
- Useful: ħc = 197.3 eV·nm; k_BT at 300 K = 25.9 meV; 1 eV = 11,600 K; λ[nm] = 1240/E[eV]; GM☉/c² = 1.48 km

## Fermi estimation
- Break the problem into factors known to within a factor ~3; multiply; errors partly cancel (log-normal).
- Anchor numbers: Earth R = 6.4e6 m, g = 9.8, atmosphere 1e5 Pa, human power ≈ 100 W, global energy use ≈ 18 TW, sun's flux 1361 W/m², c = 3e8 m/s, N_A = 6e23.
- Report as order of magnitude with a stated uncertainty; cross-check by a second route.

## Scaling
Square-cube law (strength ∝ L², weight ∝ L³), Kleiber's law (metabolic rate ∝ M^{3/4}), scaling of waves, stars (L ∝ M^{3.5}).

## Checks
Every final formula: confirm units; test limits (zero, infinity); compare with a known special case.
