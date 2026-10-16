#!/usr/bin/env python3
"""Finite-difference eigenstates of the 1D time-independent Schrodinger equation.
Units: hbar = m = 1. Demo: harmonic oscillator, E_n should be n + 1/2."""
import numpy as np
_trap = getattr(np, "trapezoid", None) or np.trapz
from scipy.linalg import eigh_tridiagonal

def solve(V, x, n_states=6):
    dx = x[1] - x[0]
    diag = 1.0/dx**2 + V(x)
    off = -0.5/dx**2 * np.ones(len(x) - 1)
    E, psi = eigh_tridiagonal(diag, off, select="i", select_range=(0, n_states-1))
    psi /= np.sqrt(_trap(psi**2, x, axis=0))
    return E, psi

if __name__ == "__main__":
    x = np.linspace(-10, 10, 4000)
    E, psi = solve(lambda x: 0.5*x**2, x)
    print("Harmonic oscillator energies:", np.round(E, 5))
    L = 1.0; xw = np.linspace(0, L, 2000)[1:-1]
    E2, _ = solve(lambda x: 0*x, xw, 4)
    print("Infinite well (exact n^2 pi^2/2):", np.round(E2, 4), np.round([(n*np.pi)**2/2 for n in range(1, 5)], 4))
