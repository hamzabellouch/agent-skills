---
name: functional-analysis-and-fourier
description: "Cover functional analysis and Fourier analysis: Banach and Hilbert spaces, bounded operators, spectral theorem, Hahn-Banach, open mapping, distributions, Fourier series and transform, wavelets, Sobolev spaces. Use for operator theory, Fourier methods, and infinite-dimensional analysis."
---

# Functional Analysis & Fourier Analysis

## Normed spaces
- Banach spaces (complete normed), Hilbert spaces (complete inner product). l^p, L^p, C(K) with sup norm.
- Bounded linear operators B(X,Y): norm ||T||; continuity <=> boundedness. Dual space X*, Riesz representation (Hilbert space H* = H).
- Big theorems: Hahn-Banach (extension of functionals), Uniform boundedness (Banach-Steinhaus), Open mapping, Closed graph, Banach-Alaoglu (weak-* compactness).
- Weak topologies, reflexivity, compact operators (Fredholm alternative), Fredholm index.
- Spectrum sigma(T): resolvent set; spectral theorem for compact self-adjoint operators (diagonalizable with real eigenvalues), for bounded/unbounded self-adjoint operators (projection-valued measure). Application: quantum observables.
- Banach algebras, C*-algebras, Gelfand transform; semigroups of operators (e^{tA}) for PDE evolution (Hille-Yosida).

## Distributions and Sobolev spaces
Test functions, distributions (delta, principal value), weak derivatives; Sobolev W^{k,p} and H^s; Sobolev embedding; trace theorem; Poincare inequality; Lax-Milgram for elliptic PDE.

## Fourier analysis
- Fourier series: coefficients c_n = (1/2 pi) integral f e^{-int}; Parseval sum |c_n|^2 = (1/2 pi) integral |f|^2; Gibbs phenomenon; convergence (Dirichlet, Fejer averages).
- Fourier transform f^(xi) = integral f(x) e^{-i x xi} dx; Plancherel; convolution <-> product; derivative <-> multiplication by i xi; Gaussians map to Gaussians; uncertainty principle sigma_x sigma_xi >= 1/2; Poisson summation; sampling theorem (Shannon-Nyquist).
- Discrete: DFT and FFT O(n log n); windowing; spectral leakage.
- Wavelets: multiresolution analysis, Haar and Daubechies; time-frequency analysis, Gabor transform; applications in compression and denoising.
- Harmonic analysis on groups: characters, Pontryagin duality, Peter-Weyl.

## Tip
In infinite dimensions, finite-dimensional intuition can fail: closed bounded sets need not be compact, operators may have continuous spectrum, and domains of unbounded operators matter.
