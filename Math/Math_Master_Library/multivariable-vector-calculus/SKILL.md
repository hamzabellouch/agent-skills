---
name: multivariable-vector-calculus
description: "Solve multivariable and vector calculus: partial derivatives, gradient, Jacobian, Lagrange multipliers, multiple integrals, change of variables, line and surface integrals, Green, Stokes, divergence theorems, differential forms. Use for 2D/3D calculus and field problems."
---

# Multivariable & Vector Calculus

## Differentiation
- Partial derivatives, gradient grad f (direction of steepest ascent, perpendicular to level sets), directional derivative D_u f = grad f . u.
- Chain rule with Jacobian; total differential; implicit function theorem; Taylor expansion with Hessian.
- Critical points: grad f = 0; classify with Hessian (D = f_xx f_yy - f_xy^2 > 0 and f_xx > 0 min; D < 0 saddle).
- Lagrange multipliers: grad f = lambda grad g with g = c; for several constraints sum of multipliers; KKT for inequalities.

## Integration
- Double/triple integrals; Fubini; order swap; polar (r dr dtheta), cylindrical (r), spherical (rho^2 sin phi); general change of variables |det J|.
- Gaussian integral integral e^{-x^2} dx = sqrt(pi).
- Surface area, volume, mass, center of mass, moments of inertia.

## Vector fields
- div F = sum dF_i/dx_i; curl F; Laplacian; identities curl grad = 0; div curl = 0; grad(fg) etc.
- Line integrals of F . dr; conservative field iff curl F = 0 on simply connected domain; potential function.
- Green: closed loop integral (P dx + Q dy) = double integral (Q_x - P_y) dA.
- Stokes: closed loop integral F . dr = surface integral curl F . dS.
- Divergence (Gauss): closed surface integral F . dS = volume integral div F dV.
- Generalized Stokes: integral over boundary of omega = integral over region of d omega (differential forms).
- Curvilinear coordinates: scale factors h_i, grad/div/curl formulas.

## Typical workflow
Sketch region -> pick coordinates fitting symmetry -> set limits carefully -> compute -> sanity-check sign/orientation and use theorem shortcuts to turn hard integrals into easy ones.
