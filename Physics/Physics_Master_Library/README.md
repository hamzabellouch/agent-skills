# Physics Skills Library

A collection of 41 Agent Skills covering the breadth of physics, from classical mechanics to quantum field theory, cosmology, computational physics and experimental methods. Each folder contains a `SKILL.md` (YAML frontmatter + instructions); some include runnable `scripts/` and `references/`.

**Start with `physics-master`** — it routes any question to the right specialist skill.

## Structure
```
physics/
├── README.md
├── physics-master/SKILL.md
├── classical-mechanics/SKILL.md
├── ...
├── numerical-simulation-physics/{SKILL.md, scripts/}
├── error-analysis-experimental-physics/{SKILL.md, scripts/}
└── physical-constants-and-units/{SKILL.md, scripts/, references/}
```

## Skills
| Skill | Description |
|---|---|
| `acoustics` | Handle acoustics and sound physics: sound waves, decibels, resonance in pipes and rooms, room acoustics, ultra... |
| `astrophysics-stellar` | Cover astrophysics: stellar structure and evolution, nuclear burning, HR diagram, white dwarfs, neutron stars,... |
| `atomic-molecular-physics` | Explain atomic and molecular structure and spectra: multi-electron atoms, term symbols, Hund's rules, spin-orb... |
| `biophysics-medical-physics` | Apply physics to biology and medicine: molecular motors, membranes, diffusion, ion channels, nerve impulses, b... |
| `chaos-nonlinear-dynamics` | Study nonlinear dynamics and chaos: fixed points, stability, bifurcations, limit cycles, Lyapunov exponents, s... |
| `classical-mechanics` | Solve Newtonian mechanics problems: kinematics, forces, work-energy, momentum, collisions, friction, projectil... |
| `condensed-matter-physics` | Analyze solids and many-body systems: crystal structure, reciprocal lattice, phonons, band theory, Fermi surfa... |
| `cosmology` | Explain cosmology: Big Bang, expansion, FLRW metric, Friedmann equations, dark matter, dark energy, CMB, infla... |
| `dimensional-analysis-estimation` | Use dimensional analysis, scaling laws, order-of-magnitude and Fermi estimation to solve or sanity-check physi... |
| `electrodynamics-maxwell` | Work with Maxwell's equations and electromagnetic radiation: induction, Faraday's law, EM waves, Poynting vect... |
| `electrostatics-magnetostatics` | Solve static electric and magnetic field problems: Coulomb's law, Gauss's law, potentials, capacitance, dielec... |
| `energy-physics-engineering` | Analyze energy systems with physics: power generation, solar PV, wind, nuclear, batteries, fuel cells, thermal... |
| `error-analysis-experimental-physics` | Perform experimental physics data analysis: uncertainty propagation, statistics, least-squares fitting, chi-sq... |
| `fluid-mechanics` | Solve fluid statics and dynamics: pressure, buoyancy, Bernoulli, continuity, viscosity, Reynolds number, Navie... |
| `general-relativity` | Work with general relativity: spacetime curvature, metrics, geodesics, Einstein field equations, Schwarzschild... |
| `geophysics-atmospheric-climate` | Apply physics to Earth and atmosphere: seismology, plate tectonics, gravity and magnetic fields, geodynamo, at... |
| `lagrangian-hamiltonian-mechanics` | Apply analytical mechanics: Lagrangian and Hamiltonian formalism, generalized coordinates, constraints, Euler-... |
| `mathematical-methods-physics` | Apply math tools to physics: vector calculus, ODE/PDE, Fourier and Laplace transforms, special functions, comp... |
| `monte-carlo-computational-methods` | Use stochastic and advanced computational methods in physics: Monte Carlo integration, Metropolis algorithm, I... |
| `nuclear-physics` | Solve nuclear physics problems: nuclear structure, binding energy, radioactive decay, half-life, fission, fusi... |
| `numerical-simulation-physics` | Simulate physical systems numerically: ODE integrators (Euler, RK4, Verlet, symplectic), PDE solvers (finite d... |
| `optics-photonics` | Cover geometric and wave optics, lasers and photonics: lenses, mirrors, interference, diffraction, polarizatio... |
| `orbital-mechanics` | Compute orbits and trajectories: Kepler's laws, vis-viva, orbital elements, Hohmann and bi-elliptic transfers,... |
| `oscillations-and-waves` | Handle oscillators and waves: simple, damped, driven harmonic motion, resonance, coupled oscillators, normal m... |
| `particle-physics-standard-model` | Discuss particle physics and the Standard Model: quarks, leptons, gauge bosons, Higgs, Feynman diagrams, conse... |
| `physical-constants-and-units` | Look up physical constants, unit conversions, and derived scales (CODATA values) for any physics calculation; ... |
| `physics-education-and-communication` | Teach and communicate physics effectively: explain concepts at different levels, analogies, common misconcepti... |
| `physics-master` | Router and global conventions for all physics skills. Use FIRST for any physics, physical science, or engineer... |
| `physics-problem-solving-methodology` | Provide a systematic method for solving any physics problem and for explaining solutions step by step: underst... |
| `plasma-physics` | Analyze plasmas: Debye shielding, plasma frequency, single particle motion, MHD, waves in plasmas, instabiliti... |
| `quantum-field-theory` | Teach quantum field theory: canonical quantization, path integrals, Feynman rules, renormalization, QED, gauge... |
| `quantum-information-computing` | Handle quantum information and computing: qubits, gates, circuits, entanglement, Bell inequalities, teleportat... |
| `quantum-mechanics-advanced` | Apply advanced quantum methods: perturbation theory, variational method, WKB, scattering theory, density matri... |
| `quantum-mechanics-fundamentals` | Solve foundational quantum mechanics: Schrodinger equation, wavefunctions, operators, uncertainty principle, i... |
| `quantum-optics-and-atom-photon` | Explain quantum optics and light-matter interaction: photon number states, coherent and squeezed states, cavit... |
| `rigid-body-dynamics` | Analyze rotation of rigid bodies: moment of inertia, torque, angular momentum, rolling, gyroscopes, precession... |
| `semiconductor-device-physics` | Explain semiconductors and devices: doping, carrier statistics, p-n junctions, diodes, transistors (BJT, MOSFE... |
| `soft-matter-and-materials` | Explain soft matter and materials physics: polymers, colloids, liquid crystals, elasticity, stress-strain, fra... |
| `special-relativity` | Solve special relativity problems: time dilation, length contraction, Lorentz transformations, relativistic mo... |
| `statistical-mechanics` | Use statistical mechanics: microstates, ensembles, partition functions, Boltzmann/Fermi-Dirac/Bose-Einstein di... |
| `thermodynamics` | Apply classical thermodynamics: laws of thermodynamics, ideal and real gases, heat engines, entropy, free ener... |

## Notes
- Constants are CODATA 2022; verify critical values with NIST.
- Scripts need Python 3 with numpy and scipy.
- Skills are written in English, in the imperative style recommended for Agent Skills.
