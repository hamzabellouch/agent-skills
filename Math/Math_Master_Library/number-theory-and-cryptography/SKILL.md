---
name: number-theory-and-cryptography
description: "Solve number theory problems: divisibility, primes, gcd, modular arithmetic, congruences, CRT, Fermat/Euler theorems, quadratic residues, Diophantine equations, continued fractions, RSA and elliptic-curve cryptography basics. Includes a Python helper script. Use for integer, prime, modular and cryptography questions."
---

# Number Theory & Cryptography

## Basics
- Fundamental theorem of arithmetic; gcd via Euclid; Bezout ax + by = gcd (extended Euclid); lcm = ab/gcd.
- Modular arithmetic: a == b (mod n); inverse of a mod n exists iff gcd(a,n) = 1; solve ax == b via inverse.
- Chinese Remainder Theorem for pairwise coprime moduli.
- Fermat: a^(p-1) == 1 (mod p) for p prime, p not dividing a. Euler: a^phi(n) == 1 for gcd(a,n) = 1; phi(n) = n prod (1 - 1/p). Wilson: (p-1)! == -1 (mod p).
- Multiplicative functions: tau, sigma, mu, phi; Moebius inversion; Dirichlet convolution.
- Order of an element, primitive roots (exist mod 1, 2, 4, p^k, 2p^k).
- Quadratic residues: Legendre symbol, Euler's criterion, quadratic reciprocity, Jacobi symbol; sums of two squares (p == 1 mod 4), Lagrange four squares.
- Diophantine: linear ax + by = c solvable iff gcd | c; Pythagorean triples (m^2 - n^2, 2mn, m^2 + n^2); Pell x^2 - Dy^2 = 1 via continued fractions; Fermat's Last Theorem (Wiles); infinite descent; lifting-the-exponent lemma; Zsigmondy.
- Valuations: v_p(n!) = sum floor(n/p^k) (Legendre).

## Primes
- Sieve of Eratosthenes; primality tests: Miller-Rabin (probabilistic), AKS (deterministic polynomial); prime number theorem pi(x) ~ x/ln x; Dirichlet's theorem on primes in progressions; twin prime, Goldbach, Riemann hypothesis as open problems.

## Cryptography
- RSA: n = pq, e coprime to phi(n), d = e^{-1} mod phi(n); encrypt c = m^e mod n, decrypt m = c^d mod n. Security rests on factoring hardness; use OAEP padding and 2048+ bit keys in practice.
- Diffie-Hellman key exchange, discrete log problem; ElGamal; elliptic curves y^2 = x^3 + ax + b over F_p (group law), ECDH/ECDSA; post-quantum lattice-based (Kyber, Dilithium) as Shor-resistant alternatives; hash functions and signatures.
- Never implement your own crypto in production; use vetted libraries.

## Script
`scripts/number_theory.py`: egcd, modular inverse, CRT, Miller-Rabin, factorization (Pollard rho), phi, primitive root, RSA toy demo.
