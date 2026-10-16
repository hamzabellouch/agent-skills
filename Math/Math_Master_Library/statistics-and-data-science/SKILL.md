---
name: statistics-and-data-science
description: "Perform statistics: descriptive statistics, estimation, confidence intervals, hypothesis tests, regression, ANOVA, Bayesian inference, bootstrapping, experimental design, model selection, causal inference basics. Includes a Python simulation script. Use for data analysis, p-values, A/B tests, and regression."
---

# Statistics & Data Science

## Descriptive
Mean, median, mode, variance s^2 (n-1), IQR, skewness, kurtosis, correlation (Pearson, Spearman), outliers, visualization (histogram, box plot, scatter, QQ plot).

## Estimation & inference
- Estimators: bias, variance, MSE, consistency, efficiency; MLE (maximize log-likelihood; asymptotically normal, Fisher information, Cramer-Rao bound); method of moments.
- Confidence interval for a mean: x-bar +- t_{n-1,a/2} s/sqrt(n); proportion p-hat +- z sqrt(p-hat(1-p-hat)/n) (use Wilson interval for small n). A 95% CI means the procedure covers the true value 95% of the time, not a 95% probability for this interval.
- Hypothesis testing: null/alternative, test statistic, p-value = P(data at least as extreme | H0), alpha, Type I/II errors, power. Tests: z, t (one-sample, two-sample Welch, paired), chi-square (goodness of fit, independence), F-test, ANOVA, Mann-Whitney, Wilcoxon, Kolmogorov-Smirnov, permutation tests.
- Multiple testing: Bonferroni, Holm, Benjamini-Hochberg FDR. Effect sizes (Cohen d) and practical significance; p-hacking and pre-registration; sample-size planning.
- Bayesian: posterior ~ likelihood x prior; conjugate pairs (Beta-Binomial, Normal-Normal, Gamma-Poisson); credible intervals; Bayes factors; MCMC (Metropolis, Gibbs, HMC); posterior predictive checks.
- Bootstrap and jackknife for uncertainty without formulas.

## Regression & modeling
- OLS: beta = (X^T X)^{-1} X^T y; R^2; residual diagnostics (linearity, homoscedasticity, normality, independence); multicollinearity (VIF); leverage and Cook's distance.
- GLMs: logistic (odds ratio), Poisson regression; regularization (ridge, lasso, elastic net); cross-validation; bias-variance tradeoff; AIC/BIC.
- Time series: stationarity, ACF/PACF, ARIMA, exponential smoothing, state-space models.
- Machine learning basics: train/validation/test split, overfitting, ensemble methods, calibration. Correlation is not causation: confounders, randomized trials, instrumental variables, difference-in-differences, DAGs.

## Practice
State assumptions, check them, report effect size with interval, and avoid over-claiming. Warn about selection bias, survivorship bias, and data leakage.

## Script
`scripts/prob_sim.py`: Monte Carlo helpers (birthday paradox, Monty Hall, CLT demo, bootstrap CI, t-test via permutation).
