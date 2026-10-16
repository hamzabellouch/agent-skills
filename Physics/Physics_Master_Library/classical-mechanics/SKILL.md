---
name: classical-mechanics
description: "Solve Newtonian mechanics problems: kinematics, forces, work-energy, momentum, collisions, friction, projectile motion, constraints, non-inertial frames. Use whenever the user asks about forces, motion, energy conservation, or momentum, even if they just say 'physics problem' about masses, ramps, pulleys, or projectiles."
---

# Classical (Newtonian) Mechanics

## Workflow
1. Draw/describe the system, choose a coordinate system aligned with the motion or constraint.
2. Identify all forces (gravity, normal, tension, friction, drag, spring, applied). Write a free-body diagram in words.
3. Apply Newton's 2nd law per axis: ΣF = m a (or dp/dt = F for variable mass).
4. If forces are complex but energies are simple, prefer work-energy: W_net = ΔK; with conservative forces E = K + U is constant.
5. For short interactions (collisions) use momentum: Σp_before = Σp_after; check energy to classify elastic/inelastic.
6. Sanity check: units, limiting cases (g→0, m→∞, θ→0), sign and magnitude.

## Key equations
- Kinematics (const. a): v = v0 + at; x = x0 + v0 t + ½at²; v² = v0² + 2aΔx
- Projectile: range R = v0² sin2θ / g; max height H = v0² sin²θ / 2g; time of flight T = 2 v0 sinθ / g
- Friction: f_s ≤ μ_s N; f_k = μ_k N
- Work: W = ∫F·dr; Power P = F·v
- Spring: F = -kx, U = ½kx²; Gravity: U = mgh (near surface)
- Elastic 1D: v1' = ((m1-m2)v1 + 2 m2 v2)/(m1+m2)
- Center of mass: R = Σ m_i r_i / M; external forces alone move the COM
- Drag: linear F = -bv (terminal v = mg/b); quadratic F = -½ρC_dAv² (terminal v = sqrt(2mg/ρC_dA))
- Variable mass (rocket): Δv = v_e ln(m0/m_f)
- Non-inertial frames: F_fict = -ma_frame - 2m Ω×v - mΩ×(Ω×r) - m dΩ/dt × r

## Pitfalls
- Never mix friction direction with motion direction (kinetic friction opposes relative sliding).
- Tension is uniform only for massless string over frictionless pulley.
- Energy is not conserved in inelastic collisions; momentum still is (if no external impulse).
- Use SI units throughout; convert km/h and g/cm³ early.
