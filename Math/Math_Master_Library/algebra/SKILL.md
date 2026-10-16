---
name: algebra
description: "Solve algebra problems: linear and quadratic equations, systems, inequalities, polynomials, factoring, rational expressions, exponential and logarithmic equations, sequences and series, functions and graphs. Use for any equation solving, simplification, or algebraic manipulation."
---

# Algebra

## Equation solving
- Linear: isolate the variable; check solution by substitution.
- Quadratic ax^2 + bx + c = 0: x = (-b +- sqrt(b^2 - 4ac))/2a; discriminant D > 0 two real, D = 0 one, D < 0 complex pair. Vieta: sum = -b/a, product = c/a. Complete the square: a(x + b/2a)^2 + (c - b^2/4a).
- Factoring: GCF; difference of squares; sum/difference of cubes a^3 +- b^3 = (a +- b)(a^2 -+ ab + b^2); grouping; rational root theorem (p/q with p | constant, q | leading).
- Systems: substitution, elimination, matrices (Gaussian elimination); 2 lines: unique, none (parallel), infinite (same).
- Inequalities: flip the sign when multiplying/dividing by a negative; sign charts for polynomial/rational inequalities; absolute value |x| < a <=> -a < x < a.
- Rational equations: find LCD, multiply through, reject extraneous roots.
- Radicals: square both sides then check for extraneous solutions.

## Functions
- Domain/range, composition, inverse (swap x,y and solve), transformations f(x - h) + k, even/odd symmetry, piecewise.
- Exponential/log: log_b(xy) = log x + log y; log_b(x^k) = k log x; change of base log_b x = ln x / ln b; solve b^x = c by x = ln c / ln b.
- Polynomials: Remainder theorem, Factor theorem, Fundamental theorem of algebra (n roots with multiplicity), end behavior, synthetic division.

## Sequences & series
- Arithmetic a_n = a_1 + (n-1)d, S_n = n(a_1 + a_n)/2. Geometric a_n = a_1 r^(n-1), S_n = a_1(1 - r^n)/(1 - r), infinite sum a_1/(1 - r) for |r| < 1.
- Binomial theorem (a+b)^n = sum C(n,k) a^(n-k) b^k.
- Useful sums: sum k = n(n+1)/2; sum k^2 = n(n+1)(2n+1)/6; sum k^3 = [n(n+1)/2]^2.

## Inequalities for competitions
AM-GM, Cauchy-Schwarz (see competition-math-and-olympiads).

## Verification
Always substitute back, test special values, and use sympy (see symbolic-computation-sympy) to confirm.
