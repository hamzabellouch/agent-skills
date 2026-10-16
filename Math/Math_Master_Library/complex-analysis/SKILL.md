---
name: complex-analysis
description: "Handle complex numbers and complex analysis: Cauchy-Riemann, analytic functions, contour integration, residue theorem, Laurent series, conformal maps, branch cuts, harmonic functions, analytic continuation, Riemann zeta. Use for complex integrals and functions."
---

# Complex Analysis

## Complex numbers
z = x + iy = r e^{i theta}; |z|, arg z; conjugate; roots of unity z^n = 1 -> e^{2 pi i k/n}; De Moivre; Euler formula; complex log ln z = ln r + i(theta + 2 pi k) (multivalued); z^a = e^{a log z}.

## Analyticity
- Cauchy-Riemann: u_x = v_y, u_y = -v_x (necessary; with continuous partials sufficient). Analytic => infinitely differentiable, u,v harmonic.
- Elementary functions: exp (period 2 pi i), sin/cos (entire, unbounded), sinh/cosh, log, arcsin etc. via log.

## Integration
- Cauchy's theorem: integral over closed loop = 0 if analytic inside; Cauchy's integral formula f(a) = (1/2 pi i) loop f(z)/(z - a) dz; derivatives f^(n)(a) = n!/(2 pi i) loop f/(z-a)^(n+1).
- Consequences: Liouville (bounded entire => constant), Fundamental theorem of algebra, maximum modulus, Morera, mean value property.
- Series: Taylor within disk of convergence (radius = distance to nearest singularity); Laurent series in annuli; singularities: removable, pole of order m, essential (Casorati-Weierstrass, Picard).
- Residues: Res at simple pole = lim (z - a) f(z); at pole order m: (1/(m-1)!) d^(m-1)/dz^(m-1)[(z-a)^m f]; loop f dz = 2 pi i sum Res.
- Real integral recipes: trig integrals via z = e^{i theta}; improper integrals over R closing in upper half-plane (Jordan's lemma); principal values; branch cut (keyhole) for x^a/(1+x); sums via cot residues; argument principle; Rouche's theorem.

## Geometry
- Mobius transformations (az + b)/(cz + d): map circles/lines to circles/lines, determined by 3 points, cross ratio invariant. Conformal maps, Riemann mapping theorem. Schwarz lemma. Riemann sphere.

## Advanced
Analytic continuation, gamma function Gamma(z+1) = z Gamma(z), Riemann zeta function zeta(s) = sum n^-s with zeros and the Riemann hypothesis, Mittag-Leffler and Weierstrass products, elliptic functions.
