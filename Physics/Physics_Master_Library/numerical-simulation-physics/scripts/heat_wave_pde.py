#!/usr/bin/env python3
"""1D heat equation (FTCS) and wave equation (leapfrog) with stability checks."""
import numpy as np
_trap = getattr(np, "trapezoid", None) or np.trapz

def heat_ftcs(u0, D, dx, dt, steps):
    r = D*dt/dx**2
    if r > 0.5: raise ValueError(f"Unstable: D dt/dx^2 = {r:.3f} > 0.5")
    u = u0.copy()
    for _ in range(steps):
        u[1:-1] += r*(u[2:] - 2*u[1:-1] + u[:-2]); u[0] = u[-1] = 0.0
    return u

def wave_leapfrog(u0, c, dx, dt, steps):
    s = c*dt/dx
    if s > 1: raise ValueError(f"CFL violated: c dt/dx = {s:.3f} > 1")
    up = u0.copy(); u = u0.copy()
    u[1:-1] = up[1:-1] + 0.5*s**2*(up[2:] - 2*up[1:-1] + up[:-2])
    for _ in range(steps - 1):
        un = np.zeros_like(u)
        un[1:-1] = 2*u[1:-1] - up[1:-1] + s**2*(u[2:] - 2*u[1:-1] + u[:-2])
        up, u = u, un
    return u

if __name__ == "__main__":
    x = np.linspace(0, 1, 201); dx = x[1]-x[0]
    u0 = np.sin(np.pi*x)
    D, dt, steps = 0.01, 0.4*dx**2/0.01, 500
    u = heat_ftcs(u0, D, dx, dt, steps); t = dt*steps
    print("Heat: numeric vs exact peak:", u.max(), np.exp(-D*np.pi**2*t))
    c = 1.0; dtw = 0.5*dx/c; n = int(round(1.0/(c*dtw)))*2  # two transit times
    uw = wave_leapfrog(u0, c, dx, dtw, n)
    print("Wave: max error after full period:", np.abs(uw - u0).max())
