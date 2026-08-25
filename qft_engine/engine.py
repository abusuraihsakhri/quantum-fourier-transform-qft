"""
Quantum Fourier Transform (QFT) Engine
Real implementation using state vector simulation with Python stdlib only.

QFT transforms computational basis states to Fourier basis:
|j⟩ → 1/√N Σ_k ω^(jk) |k⟩  where ω = e^(2πi/N), N = 2^n

Gate definitions:
- Hadamard: H = 1/√2 × [[1, 1], [1, -1]]
- Controlled rotation: R_k = [[1, 0], [0, e^(2πi/2^k)]]
- QFT matrix: F_N = 1/√N × [ω^(jk)]_{j,k=0}^{N-1}
"""
import cmath
import math
from typing import List, Tuple, Optional


# ─── Gate Matrices ───────────────────────────────────────────────────────────

SQRT2_INV = 1.0 / math.sqrt(2.0)

# Hadamard gate: H = 1/√2 [[1, 1], [1, -1]]
H_MATRIX = [
    [complex(SQRT2_INV, 0), complex(SQRT2_INV, 0)],
    [complex(SQRT2_INV, 0), complex(-SQRT2_INV, 0)],
]

# Pauli-X gate
X_MATRIX = [
    [complex(0, 0), complex(1, 0)],
    [complex(1, 0), complex(0, 0)],
]

# Identity gate
I_MATRIX = [
    [complex(1, 0), complex(0, 0)],
    [complex(0, 0), complex(1, 0)],
]


def rotation_gate(k: int) -> List[List[complex]]:
    """R_k = [[1, 0], [0, e^(2πi/2^k)]]."""
    phase = cmath.exp(2j * cmath.pi / (2 ** k))
    return [[complex(1, 0), complex(0, 0)],
            [complex(0, 0), phase]]


def controlled_rotation_gate(k: int) -> List[List[complex]]:
    """Controlled-R_k as 4×4 matrix on 2 qubits (control, target).
    |00⟩→|00⟩, |01⟩→|01⟩, |10⟩→|10⟩, |11⟩→e^(2πi/2^k)|11⟩
    """
    phase = cmath.exp(2j * cmath.pi / (2 ** k))
    m = [[complex(0) for _ in range(4)] for _ in range(4)]
    m[0][0] = complex(1, 0)  # |00⟩
    m[1][1] = complex(1, 0)  # |01⟩
    m[2][2] = complex(1, 0)  # |10⟩
    m[3][3] = phase           # |11⟩
    return m


# ─── State Vector Operations ────────────────────────────────────────────────

def zero_state(n: int) -> List[complex]:
    """Return |0...0⟩ state vector for n qubits (length 2^n)."""
    N = 2 ** n
    state = [complex(0, 0)] * N
    state[0] = complex(1, 0)
    return state


def basis_state(n: int, index: int) -> List[complex]:
    """Return |index⟩ computational basis state for n qubits."""
    N = 2 ** n
    state = [complex(0, 0)] * N
    state[index] = complex(1, 0)
    return state


def normalize_state(state: List[complex]) -> List[complex]:
    """Normalize a state vector to unit length."""
    norm = math.sqrt(sum(abs(a) ** 2 for a in state))
    if norm < 1e-15:
        raise ValueError("Cannot normalize zero vector")
    return [a / norm for a in state]


def state_probabilities(state: List[complex]) -> List[float]:
    """Return measurement probabilities |α_i|^2 for each basis state."""
    return [abs(a) ** 2 for a in state]


def apply_single_qubit_gate(state: List[complex], gate: List[List[complex]],
                             target: int, n: int) -> List[complex]:
    """Apply a single-qubit gate to qubit `target` (0-indexed, MSB=0) in an n-qubit state."""
    N = 2 ** n
    new_state = [complex(0, 0)] * N
    t_mask = 1 << (n - 1 - target)
    for i in range(N):
        bit = (i >> (n - 1 - target)) & 1
        for new_bit in range(2):
            coeff = gate[new_bit][bit]
            if abs(coeff) < 1e-15:
                continue
            j = (i & ~t_mask) | (new_bit << (n - 1 - target))
            new_state[j] += coeff * state[i]
    return new_state


def apply_controlled_gate(state: List[complex], gate2: List[List[complex]],
                           control: int, target: int, n: int) -> List[complex]:
    """Apply a controlled 2-qubit gate (4×4 matrix) with given control and target qubits."""
    N = 2 ** n
    new_state = [complex(0, 0)] * N
    c_shift = n - 1 - control
    t_shift = n - 1 - target
    for i in range(N):
        c_bit = (i >> c_shift) & 1
        t_bit = (i >> t_shift) & 1
        if c_bit == 0:
            # Control is 0: identity on target
            new_state[i] += state[i]
        else:
            # Control is 1: apply gate to target
            for new_t_bit in range(2):
                coeff = gate2[new_t_bit][t_bit]
                if abs(coeff) < 1e-15:
                    continue
                j = (i & ~(1 << t_shift)) | (new_t_bit << t_shift)
                new_state[j] += coeff * state[i]
    return new_state


# ─── QFT Circuit Construction ───────────────────────────────────────────────

def qft_circuit(n: int) -> List[Tuple[str, dict]]:
    """Return the QFT circuit as a list of (gate_name, params) for n qubits.
    
    Circuit for n qubits (q0 is MSB):
    For each qubit j from 0 to n-1:
        1. Apply H to qubit j
        2. For each qubit k > j: apply controlled-R_{k-j+1} with control=k, target=j
    Then swap qubits to reverse bit order (optional, handled in apply_qft)
    """
    gates = []
    for j in range(n):
        gates.append(('H', {'target': j}))
        for k in range(j + 1, n):
            rotation_order = k - j + 1
            gates.append(('CR', {'control': k, 'target': j, 'k': rotation_order}))
    return gates


def apply_qft(state: List[complex], n: int) -> List[complex]:
    """Apply QFT to an n-qubit state vector using the standard circuit."""
    gates = qft_circuit(n)
    for gate_name, params in gates:
        if gate_name == 'H':
            state = apply_single_qubit_gate(state, H_MATRIX, params['target'], n)
        elif gate_name == 'CR':
            k = params['k']
            cr_gate = [[complex(1, 0), complex(0, 0)],
                       [complex(0, 0), cmath.exp(2j * cmath.pi / (2 ** k))]]
            state = apply_controlled_gate(state, cr_gate, params['control'], params['target'], n)
    # Reverse qubit order (swap qubit i with qubit n-1-i)
    state = reverse_qubits(state, n)
    return state


def apply_inverse_qft(state: List[complex], n: int) -> List[complex]:
    """Apply inverse QFT (QFT†) by reversing and conjugating the QFT circuit."""
    # First reverse qubits (undo the swap at end of QFT)
    state = reverse_qubits(state, n)
    # Apply gates in reverse order, with conjugate transpose
    gates = qft_circuit(n)
    for gate_name, params in reversed(gates):
        if gate_name == 'H':
            # H is self-adjoint: H† = H
            state = apply_single_qubit_gate(state, H_MATRIX, params['target'], n)
        elif gate_name == 'CR':
            k = params['k']
            # Conjugate transpose: e^(-2πi/2^k)
            cr_gate_dag = [[complex(1, 0), complex(0, 0)],
                           [complex(0, 0), cmath.exp(-2j * cmath.pi / (2 ** k))]]
            state = apply_controlled_gate(state, cr_gate_dag, params['control'], params['target'], n)
    return state


def reverse_qubits(state: List[complex], n: int) -> List[complex]:
    """Reverse the qubit ordering in a state vector."""
    N = 2 ** n
    new_state = [complex(0, 0)] * N
    for i in range(N):
        # Reverse bits of i in n-bit representation
        j = int(format(i, f'0{n}b')[::-1], 2)
        new_state[j] = state[i]
    return new_state


# ─── QFT Matrix (Direct) ────────────────────────────────────────────────────

def qft_matrix(n: int) -> List[List[complex]]:
    """Construct the full QFT matrix F_N where N=2^n.
    F_N[j][k] = 1/√N × ω^(jk) where ω = e^(2πi/N)
    """
    N = 2 ** n
    omega = cmath.exp(2j * cmath.pi / N)
    norm = 1.0 / math.sqrt(N)
    matrix = []
    for j in range(N):
        row = []
        for k in range(N):
            row.append(norm * omega ** (j * k))
        matrix.append(row)
    return matrix


def inverse_qft_matrix(n: int) -> List[List[complex]]:
    """Construct the inverse QFT matrix F_N†.
    F_N†[j][k] = 1/√N × ω^(-jk)
    """
    N = 2 ** n
    omega = cmath.exp(-2j * cmath.pi / N)
    norm = 1.0 / math.sqrt(N)
    matrix = []
    for j in range(N):
        row = []
        for k in range(N):
            row.append(norm * omega ** (j * k))
        matrix.append(row)
    return matrix


def apply_matrix(state: List[complex], matrix: List[List[complex]]) -> List[complex]:
    """Apply a matrix to a state vector: |ψ'⟩ = M|ψ⟩."""
    N = len(state)
    result = [complex(0, 0)] * N
    for i in range(N):
        for j in range(N):
            result[i] += matrix[i][j] * state[j]
    return result


# ─── Applications ────────────────────────────────────────────────────────────

def phase_estimation_simple(unitary_phases: List[float], n_ancilla: int) -> List[float]:
    """Simple phase estimation using QFT.
    Given eigenvalue phases φ (where eigenvalue = e^(2πiφ)), 
    estimate them using n_ancilla qubits.
    Returns estimated phases.
    """
    # For a diagonal unitary with known eigenphases, QPE reduces to
    # preparing the state and applying inverse QFT
    N = 2 ** n_ancilla
    # Create superposition state encoding the phases
    state = [complex(0, 0)] * N
    for k in range(N):
        phase_sum = 0.0
        for phi in unitary_phases:
            phase_sum += 2 * cmath.pi * phi * k
        state[k] = cmath.exp(1j * phase_sum) / math.sqrt(N)
    
    # Apply inverse QFT
    state = apply_inverse_qft(state, n_ancilla)
    
    # Get probabilities
    probs = state_probabilities(state)
    
    # Find dominant phases
    phases = []
    for i, p in enumerate(probs):
        if p > 0.01:  # threshold
            phases.append(i / N)
    return sorted(phases)


def period_finding_qft(period: int, n_qubits: int) -> dict:
    """Demonstrate period finding using QFT.
    Creates a periodic state with given period, applies QFT,
    and extracts the period from the frequency spectrum.
    """
    N = 2 ** n_qubits
    # Create periodic state: equal superposition of |0⟩, |r⟩, |2r⟩, ...
    state = [complex(0, 0)] * N
    count = 0
    for k in range(0, N, period):
        state[k] = complex(1, 0)
        count += 1
    # Normalize
    norm = math.sqrt(count)
    state = [s / norm for s in state]
    
    # Apply QFT
    qft_state = apply_qft(state, n_qubits)
    
    # Get probabilities
    probs = state_probabilities(qft_state)
    
    # Find peaks (should be at multiples of N/period)
    peaks = []
    threshold = max(probs) * 0.5
    for i, p in enumerate(probs):
        if p > threshold:
            peaks.append((i, p))
    
    return {
        'period': period,
        'n_qubits': n_qubits,
        'state_size': N,
        'peaks': peaks,
        'probabilities': probs,
        'expected_peak_spacing': N // period if period > 0 else 0,
    }


def fidelity(state1: List[complex], state2: List[complex]) -> float:
    """Calculate fidelity F = |⟨ψ1|ψ2⟩|^2 between two pure states."""
    if len(state1) != len(state2):
        raise ValueError("States must have same dimension")
    inner = sum(a.conjugate() * b for a, b in zip(state1, state2))
    return abs(inner) ** 2


def inner_product(state1: List[complex], state2: List[complex]) -> complex:
    """Calculate inner product ⟨ψ1|ψ2⟩."""
    if len(state1) != len(state2):
        raise ValueError("States must have same dimension")
    return sum(a.conjugate() * b for a, b in zip(state1, state2))


def tensor_product(state1: List[complex], state2: List[complex]) -> List[complex]:
    """Compute tensor product |ψ1⟩ ⊗ |ψ2⟩."""
    result = []
    for a in state1:
        for b in state2:
            result.append(a * b)
    return result


def state_info(state: List[complex], n: int, threshold: float = 1e-6) -> dict:
    """Return human-readable info about a quantum state."""
    probs = state_probabilities(state)
    nonzero = []
    for i, (amp, p) in enumerate(zip(state, probs)):
        if p > threshold:
            label = format(i, f'0{n}b')
            nonzero.append({
                'index': i,
                'label': label,
                'amplitude': complex(amp),
                'probability': p,
                'phase_deg': math.degrees(cmath.phase(amp)),
            })
    total_prob = sum(probs)
    return {
        'n_qubits': n,
        'dimension': 2 ** n,
        'total_probability': total_prob,
        'nonzero_components': nonzero,
    }
