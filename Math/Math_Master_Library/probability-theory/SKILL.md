---
name: probability-theory
description: "Solve probability problems: counting, conditional probability, Bayes theorem, random variables, distributions, expectation, variance, law of large numbers, central limit theorem, generating functions, Markov chains, martingales, measure-theoretic probability. Use for any chance or random-variable question."
---

# Probability Theory

## Foundations
- Axioms (Kolmogorov): P(Omega) = 1, P >= 0, countable additivity. Inclusion-exclusion; complement.
- Conditional probability P(A|B) = P(A and B)/P(B); independence; Bayes P(A|B) = P(B|A)P(A)/P(B); total probability. Beware base-rate neglect, Monty Hall (switching gives 2/3), Simpson's paradox, birthday paradox (23 people ~ 50.7%).
- Counting: permutations n!, combinations C(n,k), multinomial, stars and bars C(n+k-1, k-1), derangements n! sum (-1)^k/k!.

## Random variables
- Discrete: Bernoulli, Binomial(n,p) mean np var np(1-p), Geometric (mean 1/p), Poisson(lambda) mean = var = lambda, Hypergeometric, Negative binomial.
- Continuous: Uniform, Exponential(lambda) memoryless mean 1/lambda, Normal N(mu, sigma^2), Gamma, Beta, Chi-square, Student t, Cauchy (no mean), Pareto, Lognormal.
- Expectation is linear (even without independence) E[sum X_i] = sum E[X_i]; Var(X) = E[X^2] - (E X)^2; Var(sum) = sum Var + 2 sum Cov; indicator variable trick.
- Joint, marginal, conditional distributions; covariance and correlation; law of total expectation and variance; transformations (Jacobian).
- Moment generating function M(t) = E e^{tX}; characteristic function; probability generating function.

## Limit theorems & inequalities
- Markov P(X >= a) <= E X / a; Chebyshev P(|X - mu| >= k sigma) <= 1/k^2; Chernoff/Hoeffding bounds; Jensen E f(X) >= f(E X) for convex f.
- LLN: sample mean -> mu (weak: in probability; strong: a.s.). CLT: sqrt(n)(mean - mu)/sigma -> N(0,1). Berry-Esseen rate.
- Convergence modes: a.s., in probability, in L^p, in distribution.
- Borel-Cantelli lemmas; Kolmogorov 0-1 law.

## Stochastic processes
- Markov chains: transition matrix P, stationary distribution pi P = pi, irreducible/aperiodic -> convergence; absorbing chains; hitting times; gambler's ruin; random walks (recurrent in 1D/2D, transient in 3D, Polya).
- Poisson process (exponential inter-arrivals), birth-death, queues (M/M/1: rho = lambda/mu, L = rho/(1 - rho)), renewal theory.
- Martingales, optional stopping, Doob inequalities; Brownian motion and Ito calculus (Black-Scholes); branching processes.

## Method
Define the sample space; choose complement/conditioning/linearity of expectation; verify with simulation (see scripts/prob_sim.py in statistics-and-data-science).
