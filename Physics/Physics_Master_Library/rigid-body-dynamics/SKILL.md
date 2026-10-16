---
name: rigid-body-dynamics
description: "Analyze rotation of rigid bodies: moment of inertia, torque, angular momentum, rolling, gyroscopes, precession, Euler's equations, inertia tensor, principal axes. Use for spinning tops, wheels, rolling objects, torque and angular acceleration problems."
---

# Rigid Body & Rotational Dynamics

## Fundamentals
- τ = dL/dt; for fixed axis τ = Iα; K_rot = ½Iω²; L = Iω
- Parallel axis: I = I_cm + Md²; Perpendicular axis (planar): I_z = I_x + I_y
- Common I about center: solid sphere (2/5)MR²; hollow sphere (2/3)MR²; solid cylinder ½MR²; ring MR²; thin rod (1/12)ML² (center), (1/3)ML² (end); rectangular plate (1/12)M(a²+b²)
- Rolling without slipping: v = ωR; K = ½Mv²(1 + I/MR²); acceleration down incline a = g sinθ/(1 + I/MR²)
- Inertia tensor I_ij = ∫ρ(r²δ_ij - x_i x_j)dV; diagonalize to find principal axes; L = Iω (not parallel to ω in general)

## Euler's equations (body frame, principal axes)
I1 ω̇1 = (I2 - I3) ω2 ω3 + τ1 (and cyclic).
- Torque-free: rotation about the max and min axes is stable, intermediate axis unstable (tennis racket theorem).
- Symmetric top: precession rate Ω_p ≈ mgl/(I_s ω_s) for fast spin.
- Gyroscope: τ = Ω_p × L.

## Checklist
1. Pick the axis (COM, fixed pivot, or instantaneous contact point).
2. Compute torque about that same point.
3. Use energy for rolling without slipping (static friction does no work).
4. Check angular momentum conservation for collisions with pivots, skaters, etc.
