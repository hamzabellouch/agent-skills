---
name: mathematical-modeling-and-applied-math
description: "Build and analyze mathematical models of real-world systems: population dynamics, epidemics, finance, economics, physics, engineering, networks, optimization trade-offs, sensitivity analysis, dimensionless scaling, model validation. Use for turning real problems into equations."
---

# Mathematical Modeling & Applied Mathematics

## Modeling cycle
1. Define the question and the quantity of interest. 2. Identify variables, parameters, assumptions. 3. Choose the framework (ODE, PDE, stochastic, discrete, network, agent-based, optimization). 4. Non-dimensionalize. 5. Solve/simulate. 6. Validate with data; check sensitivity. 7. Interpret, state limits of validity, iterate.

## Classic models
- Population: exponential, logistic r N (1 - N/K), Lotka-Volterra predator-prey, age-structured Leslie matrices, Allee effect.
- Epidemics: SIR dS/dt = -beta S I/N, dI/dt = beta S I/N - gamma I; R0 = beta/gamma; herd immunity threshold 1 - 1/R0; SEIR; network and stochastic versions.
- Finance: compound interest A = P e^{rt}; present value; Black-Scholes PDE, geometric Brownian motion; portfolio theory (mean-variance); Value-at-Risk.
- Economics: supply-demand equilibria, game theory, Solow growth, input-output matrices (Leontief).
- Engineering: RC/RLC circuits, spring-mass-damper, heat conduction, beams, control systems (PID, transfer functions, stability by poles), Kalman filter.
- Social/networks: PageRank (dominant eigenvector of Google matrix), diffusion on graphs, opinion dynamics, traffic flow (LWR conservation law).
- Chemistry/biology: mass-action kinetics, Michaelis-Menten, Turing patterns, Hodgkin-Huxley.

## Analysis tools
Dimensional analysis, scaling, perturbation methods (regular/singular), multiple scales, sensitivity (partial derivatives, Sobol indices), parameter estimation (least squares, MLE, Bayesian), identifiability, uncertainty quantification, cross-validation.

## Communication
State assumptions explicitly, show equations, graph results with units, give a plain-language conclusion and caveats.
