---
name: quantum-information-computing
description: "Handle quantum information and computing: qubits, gates, circuits, entanglement, Bell inequalities, teleportation, Grover and Shor algorithms, error correction, quantum cryptography, hardware platforms. Use for any qubit, quantum circuit, or entanglement question."
---

# Quantum Information & Computing

## Basics
- Qubit |ψ⟩ = α|0⟩ + β|1⟩; Bloch sphere (θ,φ); n qubits live in 2ⁿ dimensions
- Gates: X, Y, Z (Paulis), H = (X+Z)/√2, S, T (π/8), Rx/Ry/Rz(θ) = exp(-iθσ/2), CNOT, CZ, SWAP, Toffoli. Universal set: {H, T, CNOT}
- Entanglement: Bell states (|00⟩±|11⟩)/√2, (|01⟩±|10⟩)/√2; GHZ, W; entropy of entanglement; concurrence
- CHSH inequality: classical ≤ 2, quantum ≤ 2√2 (Tsirelson)
- No-cloning theorem; teleportation (1 entangled pair + 2 classical bits); superdense coding

## Algorithms
- Deutsch-Jozsa, Bernstein-Vazirani, Simon
- Quantum Fourier transform: O(n²) gates; phase estimation
- Shor: factoring via period finding, polynomial in log N
- Grover: O(√N) search; ≈ (π/4)√N iterations
- VQE and QAOA (variational hybrid); quantum simulation (Trotterization: e^{-i(A+B)t} ≈ (e^{-iAt/n}e^{-iBt/n})ⁿ)
- HHL linear systems (with caveats on input/output)

## Error correction
- Bit-flip and phase-flip codes; Shor 9-qubit code; Steane [[7,1,3]]; surface code threshold ≈ 1%
- Stabilizer formalism; logical qubits; magic-state distillation; fault-tolerance theorem

## Hardware & cryptography
- Superconducting transmons, trapped ions, neutral atoms, photonic, spin qubits, topological (Majorana) proposals
- Metrics: T1, T2, gate fidelity, two-qubit error, readout fidelity, quantum volume
- BB84, E91 key distribution; post-quantum cryptography as classical countermeasure

## Practical tip
Give circuits in OpenQASM or Qiskit/Cirq-style pseudocode, state vector results explicitly, and verify normalization and unitarity.
