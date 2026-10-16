---
name: combinatorics-and-discrete-math
description: "Solve combinatorics and discrete math problems: counting principles, permutations, combinations, pigeonhole, inclusion-exclusion, recurrences, generating functions, partitions, Catalan numbers, Ramsey theory, recurrence relations, algorithms for counting. Includes script. Use for counting, enumeration, and recurrence problems."
---

# Combinatorics & Discrete Mathematics

## Counting
- Rule of sum/product; permutations P(n,k) = n!/(n-k)!; combinations C(n,k); circular arrangements (n-1)!; multiset coefficients C(n+k-1, k).
- Binomial identities: Pascal C(n,k) = C(n-1,k-1) + C(n-1,k); sum C(n,k) = 2^n; Vandermonde; hockey stick; combinatorial proofs by double counting and bijections.
- Inclusion-exclusion; derangements D_n = n! sum_{k} (-1)^k/k!; surjections via Stirling numbers S(n,k) (set partitions), Bell numbers; integer partitions p(n) (Euler's pentagonal recurrence).
- Special sequences: Catalan C_n = C(2n,n)/(n+1) (parenthesizations, Dyck paths, binary trees), Fibonacci (F_n = F_{n-1} + F_{n-2}), Stirling numbers of the first kind, Eulerian numbers.
- Burnside / Polya enumeration for counting up to symmetry.

## Extremal & existence
- Pigeonhole: n+1 objects in n boxes; Erdos-Szekeres; Dirichlet approximation.
- Ramsey: R(3,3) = 6, R(4,4) = 18. Probabilistic method: show existence by showing positive probability. Extremal graph theory: Turan's theorem; Sperner; Dilworth; Hall's marriage theorem.
- Invariants and monovariants for process problems; coloring arguments; the pigeonhole of the parity.

## Recurrences & generating functions
- Linear recurrence with constant coefficients: characteristic roots -> closed form (Binet for Fibonacci).
- Ordinary generating function G(x) = sum a_n x^n; exponential generating function for labeled structures; partial fractions to extract coefficients; Lagrange inversion; transfer-matrix method; asymptotics via singularity analysis.
- Master theorem for divide-and-conquer T(n) = aT(n/b) + f(n).

## Discrete structures
Sets, relations, equivalence classes, partial orders and lattices, Boolean algebra, functions (injective/surjective/bijective), cardinality (countable vs uncountable, Cantor diagonal).

## Method
Model as sequences/sets; decide ordered vs unordered, repetition allowed or not; count complement if easier; verify small cases by brute force with `scripts/combinatorics.py`.
