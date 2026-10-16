---
name: error-analysis-experimental-physics
description: "Perform experimental physics data analysis: uncertainty propagation, statistics, least-squares fitting, chi-square, systematic vs random error, significant figures, calibration, Fourier analysis of signals, noise. Includes Python scripts. Use for lab reports, data fits, and measurement uncertainty."
---

# Error Analysis & Experimental Physics

## Basics
- Mean x̄, standard deviation s = sqrt(Σ(x-x̄)²/(N-1)); standard error s/√N
- Quote result as value ± uncertainty with 1–2 significant figures of uncertainty; state coverage (1σ).
- Systematic errors do not average away: calibrate, vary conditions, cross-check with a different method.

## Propagation
- General: σ_f² = Σ(∂f/∂x_i)² σ_i² (uncorrelated); add covariance terms if correlated
- Sums/differences: add absolute errors in quadrature; products/quotients: add relative errors in quadrature; f = x^n: σ_f/f = |n|σ_x/x
- Monte Carlo propagation for nonlinear cases (see scripts/error_tools.py)

## Fitting
- Weighted least squares: minimize χ² = Σ((y_i - f(x_i))/σ_i)²; reduced χ²/ndof ≈ 1 for good fit
- Linear fit slope/intercept with uncertainties; use orthogonal distance regression if x has errors
- Nonlinear: scipy.optimize.curve_fit; check covariance matrix, residual plots
- Linearize with logs when sensible (e.g., decay: ln N vs t)
- Model comparison: AIC/BIC, F-test; Bayesian posterior (MCMC) for rich problems

## Statistics for discovery
- Gaussian, Poisson (σ = √N), binomial; confidence intervals; p-values; 5σ convention in particle physics; Bayesian credible intervals
- Bootstrapping for non-Gaussian uncertainties

## Signals & noise
- Johnson noise V² = 4k_BTRΔf; shot noise I² = 2eIΔf; 1/f noise; lock-in detection; signal averaging improves S/N by √N; Nyquist sampling f_s ≥ 2 f_max; windowing for FFT

## Scripts
`scripts/error_tools.py` — propagation (analytic via sympy-free numeric derivative, Monte Carlo), weighted linear fit, chi-square helper. Run it for a demo.

## Report structure
Objective → Setup → Data table with units and uncertainties → Analysis with sample calculation → Result vs accepted value (σ-distance) → Discussion of systematics → Improvements.
