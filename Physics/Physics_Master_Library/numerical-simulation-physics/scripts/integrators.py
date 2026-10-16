#!/usr/bin/env python3
"""ODE integrators for physics: Euler, RK4, velocity-Verlet. Demo: pendulum energy drift."""
import numpy as np
_trap = getattr(np, "trapezoid", None) or np.trapz

def euler(f, y, t, dt):
    return y + dt * f(t, y)

def rk4(f, y, t, dt):
    k1 = f(t, y); k2 = f(t + dt/2, y + dt/2*k1)
    k3 = f(t + dt/2, y + dt/2*k2); k4 = f(t + dt, y + dt*k3)
    return y + dt/6*(k1 + 2*k2 + 2*k3 + k4)

def verlet(acc, x, v, dt):
    """Velocity-Verlet for x'' = acc(x). Returns new (x, v)."""
    a = acc(x)
    x_new = x + v*dt + 0.5*a*dt**2
    v_new = v + 0.5*(a + acc(x_new))*dt
    return x_new, v_new

def integrate(step, f, y0, t_end, dt):
    n = int(round(t_end/dt)); ys = np.empty((n+1, len(y0))); ys[0] = y0; t = 0.0
    for i in range(n):
        ys[i+1] = step(f, ys[i], t, dt); t += dt
    return ys

if __name__ == "__main__":
    g_over_L = 9.81
    f = lambda t, y: np.array([y[1], -g_over_L*np.sin(y[0])])
    energy = lambda y: 0.5*y[1]**2 - g_over_L*np.cos(y[0])
    y0 = np.array([1.0, 0.0]); dt, T = 0.01, 50.0
    for name, step in [("Euler", euler), ("RK4", rk4)]:
        ys = integrate(step, f, y0, T, dt)
        print(f"{name:6s} energy drift after {T}s: {energy(ys[-1]) - energy(y0):+.3e}")
    x, v = 1.0, 0.0; E0 = energy([x, v])
    for _ in range(int(T/dt)):
        x, v = verlet(lambda q: -g_over_L*np.sin(q), x, v, dt)
    print(f"Verlet energy drift after {T}s: {energy([x, v]) - E0:+.3e}")
