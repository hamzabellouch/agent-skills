#!/usr/bin/env python3
"""Monte Carlo demonstrations for probability and statistics."""
import numpy as np
rng = np.random.default_rng(0)

def birthday(n=23, trials=200000):
    b = rng.integers(0, 365, size=(trials, n))
    return np.mean([len(set(r)) < n for r in b[:20000]])
def monty_hall(trials=200000, switch=True):
    car = rng.integers(0, 3, trials); pick = rng.integers(0, 3, trials)
    return np.mean((car != pick) if switch else (car == pick))
def clt_demo(n=50, trials=20000):
    means = rng.exponential(1.0, size=(trials, n)).mean(1)
    z = (means - 1.0) / (1.0 / np.sqrt(n)); return z.mean(), z.std()
def bootstrap_ci(x, stat=np.mean, B=5000, alpha=0.05):
    x = np.asarray(x); s = [stat(rng.choice(x, len(x))) for _ in range(B)]
    return np.percentile(s, [100 * alpha / 2, 100 * (1 - alpha / 2)])
def perm_test(a, b, B=10000):
    a, b = np.asarray(a), np.asarray(b); obs = abs(a.mean() - b.mean()); pool = np.r_[a, b]; c = 0
    for _ in range(B):
        rng.shuffle(pool); c += abs(pool[:len(a)].mean() - pool[len(a):].mean()) >= obs
    return (c + 1) / (B + 1)

if __name__ == "__main__":
    print("Birthday (n=23):", round(birthday(), 3), "(exact 0.507)")
    print("Monty Hall switch:", round(monty_hall(), 3), " stay:", round(monty_hall(switch=False), 3))
    print("CLT z mean/std (should be ~0/1):", np.round(clt_demo(), 3))
    d = rng.normal(5, 2, 40); print("Bootstrap 95% CI for mean:", np.round(bootstrap_ci(d), 3))
    print("Permutation p-value:", perm_test(rng.normal(0, 1, 30), rng.normal(0.8, 1, 30), 3000))
