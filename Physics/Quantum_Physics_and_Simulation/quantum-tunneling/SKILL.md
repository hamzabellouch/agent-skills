---
name: quantum-tunneling
description: Quantum Tunneling in Quantum Mechanics (Schrödinger). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: qm.schrodinger.tunneling
  domain: Quantum Mechanics
  subdomain: Schrödinger
  difficulty: 4/5
---

# Quantum Tunneling

**ID:** `qm.schrodinger.tunneling`  
**Domain:** Quantum Mechanics → Schrödinger  
**Difficulty:** 4/5

## Prerequisites
- qm.schrodinger.finite_well

## Core Concepts
- tunneling
- transmission coefficient
- barrier penetration
- exponential suppression

## Key Equations
$$
T \approx e^{-2\kappa a},\ \kappa = \sqrt{2m(V_0-E)}/\hbar
$$

## Methods
- Compute \kappa from the barrier
- Estimate T for a rectangular barrier
- Apply to alpha decay, STM, fusion

## Typical Problem Types
- Alpha decay lifetime
- Scanning tunneling microscope
- Josephson junction

## Common Pitfalls
- Forgetting that T depends exponentially on barrier width
- Classical intuition for E < V_0

## Related Skills
- nucl.radioactivity
- cond.superconductivity

## References
- Griffiths QM Ch.2
- Liboff Ch.7
