---
name: qiskit-quantum-algorithms
metadata:
  category: Quantum Computing and Quantum AI
description: Designing and executing quantum algorithms using IBM Qiskit v1.0+. Use when constructing quantum circuits, variational quantum algorithms (VQE/QAOA), quantum machine learning (QNN), error mitigation (M3/ZNE), transpilation pass managers, or running on IBM Quantum hardware and Aer simulators.
compatibility: Qiskit v1.0+, Python 3.10+, Qiskit Aer, Qiskit IBM Runtime, NumPy, SciPy
---

# Qiskit Quantum Algorithms & Quantum AI Guidelines

This skill details quantum circuit construction, Variational Quantum Eigensolver (VQE) implementation, Quantum Approximate Optimization Algorithm (QAOA), noise mitigation strategies, and Qiskit v1.0+ transpilation workflows.

---

## 1. Qiskit v1.0+ Architecture & Primitives Paradigm

Qiskit v1.0 introduces a modular architecture centered around **Primitives** (`SamplerV2` and `EstimatorV2`):

```
+-------------------------------------------------------------------------+
|                         Quantum Circuit Definition                      |
|           (Qubit Registers, Parametric Gates, Entangled States)         |
+------------------------------------+------------------------------------+
                                     |
                                Transpilation
                                     v
+-------------------------------------------------------------------------+
|                  Target Hardware Transpilation Pass                     |
|           (Coupling Map Alignment, Gate Basis Translation, Routing)     |
+------------------------------------+------------------------------------+
                                     |
                                  Execute
                                     v
+-------------------------------------------------------------------------+
|                        Qiskit Runtime Primitives                        |
|                                                                         |
|     SamplerV2 (Quasi-probability)   |   EstimatorV2 (Expectation Values) |
+-------------------------------------------------------------------------+
```

1. **SamplerV2**: Measures individual qubit bitstrings to compute probability distributions.
2. **EstimatorV2**: Evaluates expectation values of Hermitian operators $\langle \psi | H | \psi \rangle$ directly (used in VQE / QAOA).

---

## 2. Variational Quantum Eigensolver (VQE) Implementation

Below is a production-grade Qiskit v1.0 implementation of VQE solving for the ground state energy of a molecular Hamiltonian using an efficient parametric ansatz:

```python
import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.circuit.library import EfficientSU2
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer.primitives import EstimatorV2 as AerEstimator

class VQEGroundStateSolver:
    def __init__(self, hamiltonian: SparsePauliOp, num_qubits: int):
        self.hamiltonian = hamiltonian
        self.num_qubits = num_qubits
        
        # 1. Construct Parametric Ansatz (Hardware-Efficient SU2)
        self.ansatz = EfficientSU2(
            num_qubits=num_qubits, 
            su2_gates=['ry', 'rz'], 
            entanglement='linear', 
            reps=2
        )
        self.ansatz.measure_all()
        
        # 2. Instantiate Estimator Primitive
        self.estimator = AerEstimator()

    def _cost_function(self, params: np.ndarray) -> float:
        """Evaluates expectation value <psi(params)|H|psi(params)>."""
        # Bind classical parameters to ansatz circuit
        pub = (self.ansatz, self.hamiltonian, params)
        job = self.estimator.run([pub])
        result = job.result()
        
        # Extract expectation value from primitive result array
        expectation_value = result[0].data.evs
        return float(expectation_value)

    def solve(self) -> Dict:
        # Initial random parameters
        initial_params = np.random.uniform(-np.pi, np.pi, self.ansatz.num_parameters)
        
        # Perform classical optimization (COBYLA / L-BFGS-B)
        opt_result = minimize(
            self._cost_function, 
            initial_params, 
            method='COBYLA', 
            options={'maxiter': 200, 'rhobeg': 0.1}
        )
        
        return {
            "ground_state_energy": opt_result.fun,
            "optimal_parameters": opt_result.x,
            "iterations": opt_result.nfev,
            "status": "CONVERGED" if opt_result.success else "FAILED"
        }

if __name__ == "__main__":
    # Example Molecular Hamiltonian H = 0.5 * Z0*Z1 + 0.2 * X0*X1 - 0.8 * Z0
    hamiltonian = SparsePauliOp.from_list([
        ("ZZ", 0.5),
        ("XX", 0.2),
        ("ZI", -0.8)
    ])
    
    solver = VQEGroundStateSolver(hamiltonian, num_qubits=2)
    solution = solver.solve()
    print("VQE Energy Result:", solution["ground_state_energy"])
```

---

## 3. Qiskit Transpilation & Error Mitigation

### 3.1 Custom Pass Manager Transpilation

Targeting physical quantum hardware requires transpiling high-level circuits to native hardware gate sets (`cz`, `sx`, `rz`) while optimizing circuit depth:

```python
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService

def transpile_for_ibm_backend(circuit: QuantumCircuit, backend_name: str = "ibm_brisbane"):
    # 1. Fetch real hardware target profile
    service = QiskitRuntimeService()
    backend = service.backend(backend_name)
    
    # 2. Generate Preset Pass Manager at Optimization Level 3
    pm = generate_preset_pass_manager(optimization_level=3, target=backend.target)
    
    # 3. Transpile Circuit
    transpiled_circuit = pm.run(circuit)
    
    print(f"Original Depth: {circuit.depth()} -> Transpiled Depth: {transpiled_circuit.depth()}")
    return transpiled_circuit
```

---

## 4. Anti-Patterns & Critical Pitfalls

| Anti-Pattern | Severity | Consequence | Correct Pattern |
|---|---|---|---|
| Using deprecated Qiskit 0.x methods (`execute()`, `Backend.run()`) | Critical | API breakage in Qiskit 1.0+ | Upgrade code to Qiskit 1.0 `SamplerV2` / `EstimatorV2` primitives |
| Un-transpiled execution on physical hardware | Critical | Execution error (Unsupported Gate Set) | Always run through `generate_preset_pass_manager` targeting backend |
| Unbounded ansatz depth on NISQ hardware | High | Decoherence & noise drown out quantum signal | Use shallow hardware-efficient ansätze (`EfficientSU2` reps <= 3) |
| Hardcoded measurement mapping | Medium | Faulty bitstring interpretation | Explicitly track classical register bits when sampling |
| Missing error mitigation on noisy backend | High | Inaccurate expectation values | Enable Zero-Noise Extrapolation (ZNE) or Readout Mitigation |

---

## 5. Verification & Testing Checklist

- [ ] **Statevector Simulator Verification**: Compare VQE results against exact `Statevector` diagonalization before executing on hardware.
- [ ] **Circuit Gate Count**: Verify 2-qubit gate count (`CZ`/`CNOT`) is minimized during pass manager transpilation.
- [ ] **Qiskit Version Lock**: Enforce `qiskit>=1.0.0` in `requirements.txt`.
