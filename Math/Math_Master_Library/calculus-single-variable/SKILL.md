---
name: calculus-single-variable
description: "Do single-variable calculus: limits, continuity, derivatives, optimization, related rates, integrals, techniques of integration, improper integrals, series, Taylor expansions, applications. Use for derivative/integral/limit/series problems."
---

# Single-Variable Calculus

## Limits
- Algebraic simplification, conjugates, squeeze theorem; lim sin x / x = 1; lim (1 + 1/n)^n = e; (1 - cos x)/x^2 -> 1/2.
- L'Hopital for 0/0 or inf/inf; rewrite 0*inf, inf - inf, 1^inf, 0^0 via logs.
- Epsilon-delta definition: for all eps > 0 exists delta > 0 with 0 < |x - a| < delta => |f(x) - L| < eps.
- Continuity, IVT, EVT.

## Derivatives
- Rules: product, quotient, chain; (x^n)' = n x^(n-1); (e^x)' = e^x; (ln x)' = 1/x; (a^x)' = a^x ln a; (sin)' = cos; (tan)' = sec^2; (arcsin)' = 1/sqrt(1-x^2); (arctan)' = 1/(1+x^2).
- Implicit and logarithmic differentiation; inverse functions (f^{-1})' = 1/f'(f^{-1}).
- Mean value theorem, Rolle; monotonicity and concavity; critical points, second derivative test.
- Optimization: set derivative to zero, check endpoints and nature. Related rates: differentiate the relation in time.
- Linearization f(x) ~ f(a) + f'(a)(x - a); Newton's method x_{n+1} = x_n - f/f'.

## Integrals
- FTC: d/dx integral_a^x f = f(x); integral_a^b f = F(b) - F(a).
- Techniques: substitution; integration by parts (LIATE) integral u dv = uv - integral v du; partial fractions; trig substitution (sqrt(a^2 - x^2): x = a sin t; sqrt(x^2 + a^2): x = a tan t; sqrt(x^2 - a^2): x = a sec t); Weierstrass t = tan(x/2); reduction formulas; symmetry of even/odd functions.
- Improper integrals: integral_1^inf x^-p converges iff p > 1; comparison and limit comparison.
- Applications: area, volumes (disk/shell), arc length integral sqrt(1 + f'^2), surface of revolution, average value, work, probability densities.

## Sequences & series
- Tests: divergence, geometric, p-series, integral, comparison, limit comparison, ratio, root, alternating series (Leibniz), absolute vs conditional convergence.
- Power series: radius via ratio test; differentiate/integrate termwise within the radius.
- Taylor: e^x = sum x^n/n!; sin x = x - x^3/3! + ...; cos x = 1 - x^2/2! + ...; ln(1 + x) = x - x^2/2 + ...; 1/(1-x) = sum x^n; (1+x)^a binomial series. Remainder (Lagrange) bounds error.

## Checks
Differentiate your antiderivative; verify numerically with quadrature (see numerical-analysis-and-computation).
