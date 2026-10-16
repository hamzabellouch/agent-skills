#!/usr/bin/env python3
"""Combinatorics helpers: counting numbers, partitions, brute-force checks."""
import math, itertools
from functools import lru_cache

def catalan(n): return math.comb(2 * n, n) // (n + 1)
def derangements(n):
    a, b = 1, 0
    for k in range(2, n + 1): a, b = b, (k - 1) * (a + b)
    return b if n >= 1 else 1
@lru_cache(None)
def stirling2(n, k):
    if n == k: return 1
    if k == 0 or k > n: return 0
    return k * stirling2(n - 1, k) + stirling2(n - 1, k - 1)
def bell(n): return sum(stirling2(n, k) for k in range(n + 1))
@lru_cache(None)
def partitions(n, m=None):
    m = n if m is None else m
    if n == 0: return 1
    return sum(partitions(n - k, k) for k in range(1, min(n, m) + 1))
def fib(n):
    a, b = 0, 1
    for _ in range(n): a, b = b, a + b
    return a
def count_derangements_bruteforce(n):
    return sum(all(p[i] != i for i in range(n)) for p in itertools.permutations(range(n)))
def burnside_necklaces(n, colors):
    return sum(colors ** math.gcd(n, k) for k in range(n)) // n

if __name__ == "__main__":
    print("Catalan 0..8:", [catalan(i) for i in range(9)])
    print("Derangements 0..7:", [derangements(i) for i in range(8)], " brute n=6:", count_derangements_bruteforce(6))
    print("Stirling2(5,*):", [stirling2(5, k) for k in range(6)], " Bell(6):", bell(6))
    print("p(10) =", partitions(10), " Fibonacci(30) =", fib(30))
    print("Necklaces n=6, 3 colors:", burnside_necklaces(6, 3))
