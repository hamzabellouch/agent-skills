---
name: cirq-quantum-circuits
metadata:
  category: Quantum Computing and Quantum AI
description: Designing, simulating, and optimizing quantum circuits using Google Cirq and TensorFlow Quantum. Use when building grid-qubit layouts, custom gate definitions, noisy density matrix simulations (Cirq Simulator), Sycamore hardware topologies, or quantum machine learning models.
compatibility: Cirq 1.2+, Python 3.10+, TensorFlow Quantum (TFQ), NumPy, SciPy
---

# Cirq Quantum Circuit Engineering Guidelines

This skill covers Google Cirq circuit architecture, GridQubit topology mapping, custom unitary gate definition, noisy density matrix simulation, and optimization routines for NISQ processors like Google Sycamore.

---

## 1. Cirq Fundamentals & Grid Topology

Cirq is engineered around physical hardware geometry using 2D grid placement (`cirq.GridQubit`):

```
                   cirq.GridQubit(0, 1)
                            |
   cirq.GridQubit(1, 0) -- cirq.GridQubit(1, 1) -- cirq.GridQubit(1, 2)
                            |
                   cirq.GridQubit(2, 1)
```

### 1.1 Creating Parametric Entangled Circuits

```python
import cirq
import sympy
import numpy as np

def create_sycamore_entangled_circuit(rows: int = 2, cols: int = 2) -> cirq.Circuit:
    # 1. Define Grid Qubits
    qubits = [cirq.GridQubit(r, c) for r in range(rows) for c in range(cols)]
    
    # 2. Symbolic Parameter for Variational Rotation
    theta = sympy.Symbol('theta')
    phi = sympy.Symbol('phi')
    
    circuit = cirq.Circuit()

    # Layer 1: Single Qubit Rotations
    circuit.append([cirq.H(q) for q in qubits])
    circuit.append([cirq.ry(theta).on(q) for q in qubits])

    # Layer 2: Entangling CZ Gates along adjacent Grid Neighbors
    circuit.append(cirq.CZ(qubits[0], qubits[1]))
    circuit.append(cirq.CZ(qubits[1], qubits[3]))
    circuit.append(cirq.CZ(qubits[2], qubits[3]))

    # Layer 3: Parametric Phase Rotations & Measurements
    circuit.append([cirq.rz(phi).on(q) for q in qubits])
    circuit.append([cirq.measure(q, key=f"q_{q.row}_{q.col}") for q in qubits])

    return circuit, qubits
```

---

## 2. Noisy Density Matrix Simulation (`cirq.DensityMatrixSimulator`)

Simulating real-world quantum hardware noise (depolarizing, amplitude damping) requires density matrix operations:

```python
import cirq

def simulate_noisy_circuit(circuit: cirq.Circuit, noise_probability: float = 0.02):
    """Applies depolarizing noise channel to 2-qubit operations and simulates results."""
    # 1. Define Noise Model
    noise_model = cirq.depolarize(p=noise_probability)
    
    # 2. Insert Noise Channel after 2-qubit gates
    noisy_circuit = circuit.with_noise(noise_model)
    
    # 3. Simulate using Density Matrix Simulator
    simulator = cirq.DensityMatrixSimulator()
    result = simulator.run(noisy_circuit, repetitions=1000)
    
    # Calculate Measurement Histogram
    histogram = result.histogram(key='q_0_0')
    print("Measurement Counts (q_0_0):", histogram)
    return result
```

---

## 3. Custom Gate Definition & Unitary Verification

Create domain-specific custom gates by extending `cirq.Gate`:

```python
import cirq
import numpy as np

class CustomSqrtISWAPGate(cirq.Gate):
    """Custom implementation of sqrt(iSWAP) gate."""
    def __init__(self):
        super().__init__()

    def _num_qubits_(self) -> int:
        return 2

    def _unitary_(self) -> np.ndarray:
        return np.array([
            [1, 0, 0, 0],
            [0, 1/np.sqrt(2), 1j/np.sqrt(2), 0],
            [0, 1j/np.sqrt(2), 1/np.sqrt(2), 0],
            [0, 0, 0, 1]
        ], dtype=np.complex128)

    def _circuit_diagram_info_(self, args: cirq.CircuitDiagramInfoArgs) -> str:
        return ("√iSWAP", "√iSWAP")

# Usage Example
q0, q1 = cirq.LineQubit.range(2)
custom_gate = CustomSqrtISWAPGate()
circuit = cirq.Circuit(custom_gate.on(q0, q1))
print("Custom Gate Circuit:\n", circuit)
```

---

## 4. Anti-Patterns & Critical Pitfalls

| Anti-Pattern | Severity | Consequence | Correct Pattern |
|---|---|---|---|
| Applying 2-qubit gates on non-adjacent `GridQubit`s | Critical | Hardware compilation failure on Google Sycamore | Enforce topological adjacency checks (`cirq.is_adjacent`) |
| Unbound Symbolic Variables (`sympy.Symbol`) | High | Simulator Runtime Crash during `.run()` | Resolve parameters via `cirq.ParamResolver({'theta': 0.5})` |
| Using `cirq.Simulator` for channels with noise | Medium | Noise channels silently ignored | Use `cirq.DensityMatrixSimulator()` for noisy channels |
| Over-allocating statevector simulation (>28 qubits) | High | Host system RAM exhaustion (OOM crash) | Use tensor network simulators (`qsimcirq`) for large circuits |

---

## 5. Verification Checklist

- [ ] **Grid Alignment Check**: Confirm all 2-qubit gates connect physically adjacent grid qubits.
- [ ] **Parameter Resolution**: Test parameter sweep resolution using `cirq.Sweepable`.
- [ ] **Gate Unitary Sanity**: Verify `cirq.has_unitary(gate)` returns `True` for custom gates.
