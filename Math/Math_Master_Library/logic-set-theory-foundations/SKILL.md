---
name: logic-set-theory-foundations
description: "Explain mathematical logic, set theory, proof techniques, and foundations: propositional and predicate logic, axioms (ZFC), cardinality, ordinals, axiom of choice, Goedel incompleteness, computability, Turing machines, model theory, type theory. Use for logic puzzles, proofs by induction, and foundational questions."
---

# Logic, Set Theory & Foundations

## Logic
- Propositional: connectives, truth tables, equivalences (De Morgan, contrapositive), normal forms (CNF/DNF), SAT, resolution, completeness theorem.
- Predicate logic: quantifiers, negating (not forall = exists not), free vs bound variables; models, satisfiability, Goedel completeness, compactness, Lowenheim-Skolem.
- Proof techniques: direct, contrapositive, contradiction, induction (weak, strong, structural), well-ordering, pigeonhole, cases, constructive vs non-constructive, double counting, extremal principle, invariants, probabilistic method.

## Set theory
- ZFC axioms: extensionality, pairing, union, power set, infinity, separation, replacement, foundation, choice. Russell's paradox motivates restricted comprehension.
- Cardinality: |N| = aleph_0, |R| = 2^aleph_0 > aleph_0 (Cantor diagonal); Cantor's theorem |P(A)| > |A|; Schroeder-Bernstein; cardinal arithmetic.
- Ordinals and transfinite induction; well-ordering theorem; Zorn's lemma; equivalence of AC with these.
- Continuum hypothesis independent of ZFC (Goedel, Cohen forcing). Large cardinals.

## Computability & incompleteness
- Turing machines, Church-Turing thesis, halting problem undecidable, Rice's theorem, decidable vs semi-decidable, lambda calculus, primitive recursive vs recursive functions.
- Goedel's incompleteness: any consistent, effectively axiomatized theory containing arithmetic is incomplete and cannot prove its own consistency. Tarski undefinability, Chaitin's Omega, Kolmogorov complexity.
- Complexity theory classes P, NP, PSPACE, EXP, BPP, BQP; oracle/diagonal arguments.

## Alternative foundations
Type theory (Curry-Howard: proofs as programs), category theory, homotopy type theory, intuitionistic logic, proof assistants (Lean, Coq, Isabelle) and formal verification.

## Writing a proof
State claim precisely, list assumptions, structure the argument (base case/inductive step), cite lemmas, end with the conclusion, and double-check edge cases.
