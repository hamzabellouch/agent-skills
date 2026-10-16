#!/usr/bin/env python3
"""Optimization helpers: LP, gradient descent, Newton, knapsack DP."""
import numpy as np
from scipy.optimize import linprog

def solve_lp(c, A_ub, b_ub, maximize=True):
    c = np.asarray(c, float); r = linprog(-c if maximize else c, A_ub=A_ub, b_ub=b_ub, bounds=(0, None), method="highs")
    return (r.x, -r.fun if maximize else r.fun) if r.success else (None, r.message)
def gradient_descent(grad, x0, lr=0.1, iters=2000, tol=1e-10):
    x = np.asarray(x0, float)
    for _ in range(iters):
        g = grad(x)
        if np.linalg.norm(g) < tol: break
        x = x - lr * g
    return x
def newton(grad, hess, x0, iters=50, tol=1e-12):
    x = np.asarray(x0, float)
    for _ in range(iters):
        g = grad(x)
        if np.linalg.norm(g) < tol: break
        x = x - np.linalg.solve(hess(x), g)
    return x
def knapsack(values, weights, cap):
    dp = [0] * (cap + 1)
    for v, w in zip(values, weights):
        for c in range(cap, w - 1, -1): dp[c] = max(dp[c], dp[c - w] + v)
    return dp[cap]

if __name__ == "__main__":
    print("LP max 3x+2y s.t. x+y<=4, x+3y<=6:", solve_lp([3, 2], [[1, 1], [1, 3]], [4, 6]))
    f_grad = lambda x: np.array([2 * (x[0] - 1), 4 * (x[1] + 2)])
    print("GD minimizer (expect 1,-2):", np.round(gradient_descent(f_grad, [0, 0], 0.2), 5))
    print("Newton on Rosenbrock:", np.round(newton(lambda x: np.array([-400*x[0]*(x[1]-x[0]**2)-2*(1-x[0]), 200*(x[1]-x[0]**2)]),
          lambda x: np.array([[1200*x[0]**2-400*x[1]+2, -400*x[0]], [-400*x[0], 200]]), [-1.2, 1.0]), 5))
    print("Knapsack:", knapsack([60, 100, 120], [10, 20, 30], 50), "(expect 220)")
