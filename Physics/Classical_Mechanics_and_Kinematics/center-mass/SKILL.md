---
name: center-mass
description: Center of Mass in Mechanics (Momentum). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: mech.momentum.center_of_mass
  domain: Mechanics
  subdomain: Momentum
  difficulty: 2/5
---

# Center of Mass

**ID:** `mech.momentum.center_of_mass`  
**Domain:** Mechanics → Momentum  
**Difficulty:** 2/5

## Prerequisites
- mech.momentum.conservation

## Core Concepts
- center of mass
- CM frame
- reduced mass
- CM motion

## Key Equations
$$
\vec R_{CM} = \frac{1}{M}\sum_i m_i\vec r_i
$$
$$
\vec F_{ext} = M\ddot{\vec R}_{CM}
$$
$$
\mu = \frac{m_1 m_2}{m_1+m_2}
$$

## Methods
- Compute CM for discrete and continuous systems
- Switch to CM frame to simplify collisions
- Use reduced mass for two-body problems

## Typical Problem Types
- CM of a composite body
- Two-body collision in CM frame
- Rocket staging

## Common Pitfalls
- Confusing CM with geometric centroid
- Forgetting reduced mass in two-body problems

## Related Skills
- mech.momentum.conservation
- rel.general.two_body

## References
- Kleppner & Kolenkow Ch.4
- Goldstein Ch.1
