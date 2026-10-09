---
name: variable-mass-systems-rockets
description: Variable-Mass Systems and Rockets in Mechanics (Momentum). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: mech.momentum.variable_mass
  domain: Mechanics
  subdomain: Momentum
  difficulty: 4/5
---

# Variable-Mass Systems and Rockets

**ID:** `mech.momentum.variable_mass`  
**Domain:** Mechanics → Momentum  
**Difficulty:** 4/5

## Prerequisites
- mech.momentum.impulse
- mech.momentum.conservation

## Core Concepts
- rocket equation
- thrust
- mass flow rate
- Tsiolkovsky

## Key Equations
$$
F_{thrust} = v_{ex}\frac{dm}{dt}
$$
$$
\Delta v = v_{ex}\ln\frac{m_0}{m_f}
$$

## Methods
- Apply momentum conservation to the system + exhaust
- Derive and use the rocket equation
- Include gravity when needed

## Typical Problem Types
- Rocket in free space
- Rocket under gravity
- Rain falling into a moving cart

## Common Pitfalls
- Using F = ma with constant m
- Wrong sign for mass loss

## Related Skills
- mech.momentum.center_of_mass
- math.odes

## References
- Taylor Ch.3
- Kleppner & Kolenkow Ch.4
