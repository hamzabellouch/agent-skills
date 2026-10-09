---
name: ac-circuits-impedance
description: AC Circuits and Impedance in Electromagnetism (Circuits). Theoretical foundations, governing equations, analytical problem-solving methods, and typical archetypes.
metadata:
  id: em.circuits.ac_impedance
  domain: Electromagnetism
  subdomain: Circuits
  difficulty: 4/5
---

# AC Circuits and Impedance

**ID:** `em.circuits.ac_impedance`  
**Domain:** Electromagnetism → Circuits  
**Difficulty:** 4/5

## Prerequisites
- em.induction.inductance
- em.circuits.rc

## Core Concepts
- phasors
- impedance
- resonance
- RMS values
- RLC circuits

## Key Equations
$$
Z_R = R
$$
$$
Z_L = i\omega L
$$
$$
Z_C = \frac{1}{i\omega C}
$$
$$
Z_{RLC} = \sqrt{R^2 + (\omega L - 1/\omega C)^2}
$$

## Methods
- Convert to phasor domain
- Apply complex impedance and Ohm's law
- Analyze resonance and power factor

## Typical Problem Types
- Series RLC response
- Power factor correction
- Filter design

## Common Pitfalls
- Adding reactances as scalars without phasors
- Confusing peak and RMS values

## Related Skills
- mech.oscillations.driven_resonance
- em.maxwell.equations

## References
- Halliday-Resnick-Walker Ch.31
- Nilsson Riedel
