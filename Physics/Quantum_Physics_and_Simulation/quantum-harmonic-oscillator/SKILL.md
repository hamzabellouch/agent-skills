---
name: quantum-harmonic-oscillator
description: Quantum Harmonic Oscillator in Quantum Mechanics (Schrödinger). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: qm.schrodinger.harmonic_oscillator
  domain: Quantum Mechanics
  subdomain: Schrödinger
  difficulty: 4/5
---

# Quantum Harmonic Oscillator

**ID:** `qm.schrodinger.harmonic_oscillator`  
**Domain:** Quantum Mechanics → Schrödinger  
**Difficulty:** 4/5

## Prerequisites
- qm.schrodinger.wavefunction
- mech.oscillations.shm

## Core Concepts
- ladder operators
- zero-point energy
- Hermite polynomials
- phonons
- creation/annihilation

## Key Equations
$$
E_n = \hbar\omega\left(n+\tfrac12\right)
$$
$$
a_\pm = \frac{1}{\sqrt{2m\hbar\omega}}(m\omega x \mp ip)
$$

## Methods
- Use ladder operators
- Apply [a_-, a_+] = 1
- Compute matrix elements

## Typical Problem Types
- Energy levels of a diatomic molecule
- Phonon spectrum
- Coherent states

## Common Pitfalls
- Forgetting zero-point energy
- Commuting a and a^† incorrectly

## Related Skills
- qm.many_body.phonons
- mech.oscillations.coupled_normal_modes

## References
- Griffiths QM Ch.2
- Sakurai Ch.2
