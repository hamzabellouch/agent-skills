---
name: real-analysis-and-measure-theory
description: "Cover rigorous real analysis: sequences, limits, continuity, uniform convergence, compactness, metric spaces, Riemann and Lebesgue integration, measure theory, convergence theorems, Lp spaces, Fourier basics. Use for epsilon-delta proofs and analysis theory."
---

# Real Analysis & Measure Theory

## Foundations
- Completeness (least upper bound property), Archimedean property, density of Q.
- Sequences: Cauchy <=> convergent in R; monotone convergence; Bolzano-Weierstrass; limsup/liminf; subsequences.
- Topology of R / metric spaces: open, closed, compact (Heine-Borel: closed and bounded in R^n), connected, complete; Baire category theorem; Banach fixed point theorem (contraction -> unique fixed point).
- Continuity: epsilon-delta, sequential, preimage of open sets; uniform continuity (continuous on compact); Arzela-Ascoli.
- Differentiation: MVT, Taylor with remainder, Darboux; pathological examples: Weierstrass nowhere-differentiable function, Cantor function.
- Series: absolute convergence, rearrangement (Riemann rearrangement theorem), Cauchy product.
- Uniform convergence: preserves continuity; interchange of limit with integral/derivative requires conditions; Weierstrass M-test; Stone-Weierstrass (polynomials dense in C[a,b]).

## Integration & measure
- Riemann integrable <=> bounded and a.e. continuous; Darboux sums.
- Measure: sigma-algebra, Lebesgue outer measure, measurable sets, Vitali set (non-measurable, uses choice), Borel sets, Cantor set (measure zero but uncountable).
- Lebesgue integral: simple function approximation; Monotone Convergence, Fatou, Dominated Convergence theorems; Fubini-Tonelli; Radon-Nikodym; Lebesgue differentiation theorem.
- L^p spaces: Holder, Minkowski, completeness (Riesz-Fischer); L^2 Hilbert space; modes of convergence (a.e., in measure, L^p).
- Fourier series, Parseval, convergence (Dirichlet, Carleson), Fourier transform on L^1/L^2, Plancherel.

## Proof habits
State the definition; choose epsilon-delta/epsilon-N scheme (work backward to find delta); watch quantifier order; give counterexamples when a claim lacks hypotheses.
