---
name: math-master
description: "Router and global conventions for all mathematics skills. Use FIRST for any mathematics, proof, calculation, statistics, or quantitative-reasoning question and decide which specialized math skill(s) to load."
---

# Math Master Router

Use this skill first for any mathematics request, then load the specialized skill(s) that match.

| If the question is about... | Load skill |
|---|---|
| Fractions, percents, mental math | arithmetic-and-number-sense |
| Equations, polynomials, functions, series | algebra |
| Triangles, circles, trig identities | trigonometry-and-geometry |
| Matrices, eigenvalues, vector spaces | linear-algebra |
| Limits, derivatives, integrals, Taylor | calculus-single-variable |
| Gradients, multiple integrals, Stokes | multivariable-vector-calculus |
| Rigorous proofs of limits, measure, Lp | real-analysis-and-measure-theory |
| Complex numbers, residues, conformal maps | complex-analysis |
| ODEs, stability, Laplace transform | ordinary-differential-equations |
| Heat, wave, Laplace equations | partial-differential-equations |
| Groups, rings, fields, Galois | abstract-algebra |
| Primes, modular arithmetic, RSA | number-theory-and-cryptography |
| Probability, distributions, Markov chains | probability-theory |
| Hypothesis tests, regression, Bayesian | statistics-and-data-science |
| Counting, recurrences, generating functions | combinatorics-and-discrete-math |
| Graphs, networks, shortest paths, NP | graph-theory-and-algorithms |
| Logic, sets, Goedel, computability | logic-set-theory-foundations |
| Topology, manifolds, curvature | topology-and-geometry-advanced |
| Hilbert spaces, Fourier, distributions | functional-analysis-and-fourier |
| LP, convex, KKT, game theory | optimization-and-operations-research |
| Floating point, quadrature, solvers | numerical-analysis-and-computation |
| Entropy, coding, capacity | information-theory-and-coding |
| Olympiad tricks, proof writing | mathematical-proof-and-competition-methods |
| Exact symbolic results, verification | symbolic-computation-sympy |
| Math behind ML and AI | machine-learning-mathematics |
| Turning real problems into equations | mathematical-modeling-and-applied-math |
| Teaching, quizzes, study plans | math-education-and-tutoring |

## Global rules
1. Restate the problem and identify its type and level of rigor required (computation, proof, explanation).
2. Show reasoning step by step; define notation; state theorems used and their hypotheses.
3. Verify: substitute back, test special cases, check dimensions/limits, and use scripts (sympy, numpy) for confirmation.
4. Give exact answers when possible and decimal approximations with stated precision.
5. Distinguish proven results, conjectures, and open problems (Riemann hypothesis, P vs NP, Navier-Stokes, Goldbach).
6. If a claim cannot be fully justified, say exactly what is missing instead of bluffing.
