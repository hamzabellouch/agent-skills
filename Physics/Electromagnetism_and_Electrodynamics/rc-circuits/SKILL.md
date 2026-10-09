---
name: rc-circuits
description: RC Circuits in Electromagnetism (Circuits). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: em.circuits.rc
  domain: Electromagnetism
  subdomain: Circuits
  difficulty: 3/5
---

# RC Circuits

**ID:** `em.circuits.rc`  
**Domain:** Electromagnetism → Circuits  
**Difficulty:** 3/5

## Prerequisites
- em.circuits.kirchhoff
- em.electrostatics.capacitance
- math.odes

## Core Concepts
- time constant
- charging
- discharging
- exponential decay
- steady state

## Key Equations
$$
Q(t) = Q_\infty(1 - e^{-t/RC})
$$
$$
Q(t) = Q_0 e^{-t/RC}
$$
$$
\tau = RC
$$

## Methods
- Write the differential equation from Kirchhoff
- Solve the first-order ODE
- Identify the initial and final states

## Typical Problem Types
- Charging capacitor
- Discharging capacitor
- Time to reach a certain charge

## Common Pitfalls
- Using final charge as initial or vice versa
- Forgetting the time constant is RC

## Related Skills
- em.circuits.ac_impedance
- math.odes

## References
- Halliday-Resnick-Walker Ch.27
