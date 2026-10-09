---
name: tension-pulleys-atwood-machines
description: Tension, Pulleys and Atwood Machines in Mechanics (Dynamics). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: mech.dynamics.pulleys
  domain: Mechanics
  subdomain: Dynamics
  difficulty: 3/5
---

# Tension, Pulleys and Atwood Machines

**ID:** `mech.dynamics.pulleys`  
**Domain:** Mechanics → Dynamics  
**Difficulty:** 3/5

## Prerequisites
- mech.dynamics.free_body
- mech.kinematics.constraints

## Core Concepts
- tension
- massless pulley
- ideal string
- Atwood machine
- acceleration constraint

## Key Equations
$$
T - m_1 g = m_1 a
$$
$$
m_2 g - T = m_2 a
$$
$$
a = \frac{(m_2-m_1)g}{m_1+m_2}
$$

## Methods
- Draw FBDs for each mass
- Apply the constraint (same |a|, opposite directions)
- Solve the coupled equations

## Typical Problem Types
- Atwood machine
- Two masses on a table over a pulley
- Moving pulley systems

## Common Pitfalls
- Ignoring pulley mass (only valid if stated)
- Wrong sign for acceleration direction

## Related Skills
- mech.kinematics.constraints
- mech.rotation.torque_dynamics

## References
- Kleppner & Kolenkow Ch.2
- Morin Ch.3
