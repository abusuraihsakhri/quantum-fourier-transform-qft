# Quantum Fourier Transform (QFT)

Real implementation of the Quantum Fourier Transform using state vector simulation in pure Python (stdlib only).

## What This Actually Does

This is a functional quantum computing simulator that implements:

- **QFT circuit construction** for n qubits using Hadamard and controlled rotation gates
- **State vector simulation** — full 2^n-dimensional complex state vectors
- **Gate operations** — H, controlled-R_k, applied via matrix multiplication on state vectors
- **QFT matrix** — direct construction of F_N = 1/√N × [ω^(jk)] where ω = e^(2πi/N)
- **Inverse QFT** — via conjugate transpose circuit
- **Period finding** — demonstrates QFT's application to finding periodicity
- **Phase estimation** — simplified QPE using QFT

### Gate Definitions

| Gate | Matrix |
|------|--------|
| Hadamard H | 1/√2 × [[1, 1], [1, -1]] |
| Controlled-R_k | diag(1, 1, 1, e^(2πi/2^k)) |
| QFT F_N | 1/√N × [ω^(jk)], ω = e^(2πi/N) |

## Usage

```bash
# Apply QFT to |010⟩ (3 qubits)
python cli.py qft -n 3 -s 2

# Verify QFT → IQFT round-trip
python cli.py qft -n 4 -s 5 --verify

# Display QFT matrix
python cli.py matrix -n 3 --verify

# Period finding demo
python cli.py period -r 4 -n 6 --show-probs

# QFT of uniform superposition (should give |0⟩)
python cli.py superposition -n 3

# Phase estimation
python cli.py phase-est --phases 0.25,0.5 --ancilla-qubits 4
```

## API

```python
from qft_engine.engine import (
    apply_qft, apply_inverse_qft, qft_matrix,
    basis_state, state_probabilities, fidelity,
    period_finding_qft, phase_estimation_simple,
)

# Apply QFT to |3⟩ in 3-qubit system
state = basis_state(3, 3)
qft_result = apply_qft(state, 3)
probs = state_probabilities(qft_result)

# Verify round-trip
recovered = apply_inverse_qft(qft_result, 3)
print(fidelity(state, recovered))  # Should be ~1.0
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Limitations

- State vector simulation: exponential memory (2^n complex numbers), practical for n ≤ ~20
- No noise model — ideal quantum gates only
- Period finding demo is simplified (not full Shor's algorithm)
- Phase estimation assumes known eigenvalue structure
