---
name: abstract-algebra
description: "Teach and solve abstract algebra: groups, subgroups, homomorphisms, quotient groups, Sylow theorems, rings, ideals, fields, Galois theory, modules, polynomial rings, classification theorems. Use for group/ring/field proofs and structure questions."
---

# Abstract Algebra

## Groups
- Axioms: closure, associativity, identity, inverses. Examples: Z_n, S_n, D_n, GL_n(F), SO(3), Q_8, A_n.
- Lagrange: |H| divides |G|; order of element divides |G|; cyclic groups (every subgroup cyclic; generators = units mod n).
- Homomorphisms, kernel (normal subgroup), isomorphism theorems: G/ker phi ~ im phi.
- Normal subgroups, quotient groups, simple groups (A_n n >= 5), classification of finite simple groups (Monster).
- Actions: orbit-stabilizer |orbit| = |G|/|Stab|; Burnside counting orbits = (1/|G|) sum fix(g); class equation; conjugacy classes.
- Sylow theorems: p-subgroups exist, all conjugate, number n_p == 1 mod p and divides index.
- Structure: fundamental theorem of finite abelian groups; semidirect products; solvable, nilpotent groups; free groups, presentations.

## Rings & fields
- Rings, integral domains, fields; ideals and quotient rings R/I; prime ideals (R/P domain), maximal ideals (R/M field).
- Hierarchy: Euclidean domain => PID => UFD => integral domain. Z, F[x] are Euclidean; Z[x] is UFD not PID; Z[sqrt(-5)] not UFD.
- Polynomials: Gauss lemma, Eisenstein criterion, irreducibility over Q, F_p; Chinese Remainder Theorem Z/mn = Z/m x Z/n for coprime.
- Finite fields F_q exist iff q = p^n, unique up to isomorphism, multiplicative group cyclic.
- Field extensions: degree [K:F], tower law, algebraic/transcendental, splitting fields, constructible numbers (impossibility of doubling the cube, trisecting angles, squaring the circle).

## Galois theory
Galois group Gal(K/F) of automorphisms; Fundamental Theorem: subgroups <-> intermediate fields; solvability by radicals iff Galois group solvable; general quintic unsolvable (S_5 not solvable); cyclotomic fields.

## Further
Modules over PID (structure theorem -> Jordan/rational canonical forms), tensor products, representation theory (characters, Maschke, orthogonality), Lie algebras, category-theoretic view.

## Proof tips
Define the map, check well-definedness, check homomorphism, injective/surjective; use first isomorphism theorem; count elements; look for counterexamples in small groups (S_3, Q_8).
