---
name: physics-master
description: "Router and global conventions for all physics skills. Use FIRST for any physics, physical science, or engineering-physics question, and decide which specialized physics skill(s) to load."
---

# Physics Master Router

Use this skill first for any physics request, then load the specialized skill that matches.

| If the question is about... | Load skill |
|---|---|
| Forces, motion, energy, momentum | classical-mechanics |
| Lagrangian/Hamiltonian, Noether, symmetries | lagrangian-hamiltonian-mechanics |
| Orbits, satellites, Kepler, Hohmann | orbital-mechanics |
| Spinning, torque, rolling, gyroscope | rigid-body-dynamics |
| Oscillators, waves, resonance | oscillations-and-waves |
| Fluids, flow, drag, Navier-Stokes | fluid-mechanics |
| Heat, entropy, engines, phase | thermodynamics |
| Ensembles, partition function, phase transitions | statistical-mechanics |
| Static E and B fields | electrostatics-magnetostatics |
| Maxwell, EM waves, radiation, circuits | electrodynamics-maxwell |
| Lenses, diffraction, lasers, fibers | optics-photonics |
| Light speed, Lorentz transformations | special-relativity |
| Curved spacetime, black holes, GW | general-relativity |
| Wavefunctions, spin, hydrogen atom | quantum-mechanics-fundamentals |
| Perturbation, scattering, density matrices | quantum-mechanics-advanced |
| Qubits, circuits, entanglement | quantum-information-computing |
| Atoms, molecules, spectra, cold atoms | atomic-molecular-physics |
| Solids, bands, superconductors, topology | condensed-matter-physics |
| Diodes, transistors, solar cells | semiconductor-device-physics |
| Isotopes, decay, fission/fusion | nuclear-physics |
| Quarks, Higgs, Standard Model | particle-physics-standard-model |
| Fields, Feynman diagrams, renormalization | quantum-field-theory |
| Stars, galaxies, compact objects | astrophysics-stellar |
| Universe expansion, CMB, dark energy | cosmology |
| Ionized gases, fusion plasmas | plasma-physics |
| Math techniques for derivations | mathematical-methods-physics |
| Estimates, scaling, units check | dimensional-analysis-estimation |
| Code/simulation for physics | numerical-simulation-physics |
| Lab data, uncertainty, fits | error-analysis-experimental-physics |
| Step-by-step problem method | physics-problem-solving-methodology |
| Sound and acoustics | acoustics |
| Biology/medical physics | biophysics-medical-physics |
| Chaos, bifurcations | chaos-nonlinear-dynamics |
| Earth, weather, climate | geophysics-atmospheric-climate |
| Monte Carlo, MD, DFT, ML | monte-carlo-computational-methods |
| Polymers, materials, rheology | soft-matter-and-materials |
| Energy systems and batteries | energy-physics-engineering |
| Photon states, cavity QED | quantum-optics-and-atom-photon |
| Teaching and science writing | physics-education-and-communication |
| Constants and conversions | physical-constants-and-units |

## Global rules
1. Identify the regime (classical/quantum, relativistic/non-relativistic, equilibrium/non-equilibrium) before choosing equations.
2. State assumptions, units, and sign conventions.
3. Derive symbolically, then compute numerically; check limits and dimensions.
4. Use scripts and constants from the specialized skills for numbers instead of memory.
5. For frontier or fast-changing results (dark energy, Hubble tension, new materials claims), say the data may have changed and recommend checking primary sources.
6. Be honest about uncertainty; separate established physics from speculation.
