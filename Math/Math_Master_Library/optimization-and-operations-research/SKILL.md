---
name: optimization-and-operations-research
description: "Solve optimization problems: linear programming, simplex, duality, convex optimization, gradient descent, Lagrange and KKT conditions, integer programming, dynamic programming, game theory, network flow, calculus of variations, stochastic optimization. Includes a Python script. Use for any maximize/minimize or decision problem."
---

# Optimization & Operations Research

## Formulation
Decision variables -> objective -> constraints; classify: LP, QP, convex, nonconvex, integer, stochastic.

## Linear programming
- Standard form max c^T x s.t. Ax <= b, x >= 0; optimum at a vertex; simplex method; interior-point methods (polynomial time).
- Duality: min b^T y s.t. A^T y >= c; strong duality (equal optimal values); complementary slackness; shadow prices; sensitivity analysis.
- Special cases: transportation, assignment, shortest path, max flow as LPs.

## Convex & nonlinear
- Convex set/function; local min = global min; first-order condition f(y) >= f(x) + grad f(x)^T (y - x).
- KKT conditions: stationarity, primal/dual feasibility, complementary slackness; Slater's condition gives strong duality.
- Algorithms: gradient descent (step 1/L, rate O(1/k), strongly convex linear rate), accelerated (Nesterov), Newton (quadratic local), quasi-Newton (BFGS), conjugate gradient, proximal methods, ADMM, SGD and Adam for ML, trust regions.
- Nonconvex: local minima, saddle points, random restarts, simulated annealing, genetic algorithms, Bayesian optimization.

## Discrete & dynamic
- Integer programming: branch and bound, cutting planes, total unimodularity; knapsack, TSP, scheduling.
- Dynamic programming: Bellman principle, optimal substructure (knapsack, edit distance, shortest paths); Markov decision processes, value iteration, reinforcement learning basics.
- Calculus of variations: Euler-Lagrange equation d/dx(F_y') = F_y; brachistochrone, geodesics, isoperimetric problem; optimal control (Pontryagin).
- Game theory: Nash equilibrium (existence by Nash/Brouwer), zero-sum minimax (von Neumann), prisoner's dilemma, mixed strategies, auctions, mechanism design.
- Queueing, inventory (EOQ = sqrt(2DS/H)), scheduling.

## Script
`scripts/optim_tools.py` has a simplex-free LP via scipy, gradient descent with line search, Newton, and knapsack DP examples.

## Answer format
State model, solver or method, optimal value and solution, check feasibility and optimality (duality gap or gradient norm).
