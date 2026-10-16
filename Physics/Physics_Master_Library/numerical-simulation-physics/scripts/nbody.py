#!/usr/bin/env python3
"""Gravitational N-body with leapfrog (kick-drift-kick). G = 1 units by default.
Demo: figure-eight three-body choreography, prints energy conservation."""
import numpy as np
_trap = getattr(np, "trapezoid", None) or np.trapz

def accel(pos, mass, G=1.0, eps=1e-9):
    d = pos[None, :, :] - pos[:, None, :]
    r2 = (d**2).sum(-1) + eps
    inv3 = r2**-1.5; np.fill_diagonal(inv3, 0.0)
    return G * (d * (mass[None, :, None] * inv3[:, :, None])).sum(1)

def energy(pos, vel, mass, G=1.0):
    K = 0.5*(mass*(vel**2).sum(1)).sum()
    U = 0.0
    for i in range(len(mass)):
        for j in range(i+1, len(mass)):
            U -= G*mass[i]*mass[j]/np.linalg.norm(pos[i]-pos[j])
    return K + U

def leapfrog(pos, vel, mass, dt, steps, G=1.0):
    a = accel(pos, mass, G)
    for _ in range(steps):
        vel = vel + 0.5*dt*a; pos = pos + dt*vel
        a = accel(pos, mass, G); vel = vel + 0.5*dt*a
    return pos, vel

if __name__ == "__main__":
    pos = np.array([[-0.97000436, 0.24308753], [0.97000436, -0.24308753], [0.0, 0.0]])
    v3 = np.array([-0.93240737, -0.86473146])
    vel = np.array([-v3/2, -v3/2, v3]); mass = np.ones(3)
    E0 = energy(pos, vel, mass)
    pos, vel = leapfrog(pos, vel, mass, 1e-3, 6325)  # about one period (T ~ 6.3259)
    print("Relative energy error:", abs((energy(pos, vel, mass) - E0)/E0))
    print("Final positions:\n", np.round(pos, 4))
