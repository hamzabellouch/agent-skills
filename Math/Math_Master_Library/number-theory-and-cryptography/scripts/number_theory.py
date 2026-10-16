#!/usr/bin/env python3
"""Number theory helpers (pure Python). Educational crypto only; do not use for real security."""
import math, random

def egcd(a, b):
    if b == 0: return a, 1, 0
    g, x, y = egcd(b, a % b); return g, y, x - (a // b) * y
def modinv(a, n):
    g, x, _ = egcd(a % n, n)
    if g != 1: raise ValueError("no inverse")
    return x % n
def crt(rems, mods):
    x, M = 0, 1
    for r, m in zip(rems, mods):
        g, p, _ = egcd(M, m)
        if (r - x) % g: raise ValueError("inconsistent system")
        l = M // g * m
        x = (x + M * ((r - x) // g * p % (m // g))) % l; M = l
    return x, M
def is_prime(n, rounds=20):
    if n < 2: return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0: return n == p
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)[:max(12, 0)]:
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True   # deterministic for n < 3.3e24 with these bases
def pollard_rho(n):
    if n % 2 == 0: return 2
    while True:
        c, x, y, d = random.randrange(1, n), 2, 2, 1
        f = lambda v: (v * v + c) % n
        while d == 1: x, y = f(x), f(f(y)); d = math.gcd(abs(x - y), n)
        if d != n: return d
def factor(n):
    if n == 1: return {}
    if is_prime(n): return {n: 1}
    d = pollard_rho(n); out = {}
    for k, v in {**factor(d)}.items(): out[k] = out.get(k, 0) + v
    for k, v in factor(n // d).items(): out[k] = out.get(k, 0) + v
    return dict(sorted(out.items()))
def phi(n):
    r = n
    for p in factor(n): r = r // p * (p - 1)
    return r
def primitive_root(p):
    f = list(factor(p - 1))
    return next(g for g in range(2, p) if all(pow(g, (p - 1) // q, p) != 1 for q in f))

if __name__ == "__main__":
    print("egcd(240,46):", egcd(240, 46), " 7^-1 mod 40 =", modinv(7, 40))
    print("CRT x=2(3),3(5),2(7):", crt([2, 3, 2], [3, 5, 7]))
    print("factor(600851475143):", factor(600851475143), " phi(36)=", phi(36), " primitive root of 23:", primitive_root(23))
    p, q = 1000003, 1000033; n = p * q; e = 65537; d = modinv(e, (p - 1) * (q - 1)); m = 123456789
    c = pow(m, e, n); print("toy RSA ok:", pow(c, d, n) == m)
