"""
Tests for Quantum Fourier Transform Engine.
Real quantum computing verification using mathematical properties.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import math
import cmath
import pytest
from qft_engine.engine import (
    zero_state, basis_state, normalize_state, state_probabilities,
    apply_single_qubit_gate, apply_controlled_gate,
    H_MATRIX, X_MATRIX, I_MATRIX, rotation_gate, controlled_rotation_gate,
    qft_matrix, inverse_qft_matrix, apply_matrix,
    apply_qft, apply_inverse_qft, reverse_qubits,
    fidelity, inner_product, tensor_product, state_info,
    period_finding_qft, phase_estimation_simple,
    qft_circuit,
)


# ─── State Vector Basics ────────────────────────────────────────────────────

class TestStateVectors:
    def test_zero_state_length(self):
        state = zero_state(3)
        assert len(state) == 8

    def test_zero_state_is_normalized(self):
        state = zero_state(4)
        norm_sq = sum(abs(a) ** 2 for a in state)
        assert abs(norm_sq - 1.0) < 1e-12

    def test_zero_state_first_element(self):
        state = zero_state(3)
        assert abs(state[0] - 1.0) < 1e-12
        for i in range(1, 8):
            assert abs(state[i]) < 1e-12

    def test_basis_state(self):
        state = basis_state(3, 5)
        assert len(state) == 8
        assert abs(state[5] - 1.0) < 1e-12
        assert abs(state[0]) < 1e-12

    def test_normalize_state(self):
        state = [complex(3, 0), complex(4, 0)]
        normed = normalize_state(state)
        assert abs(normed[0] - 0.6) < 1e-10
        assert abs(normed[1] - 0.8) < 1e-10

    def test_normalize_zero_raises(self):
        with pytest.raises(ValueError):
            normalize_state([complex(0, 0), complex(0, 0)])

    def test_state_probabilities(self):
        state = [complex(1 / math.sqrt(2)), complex(1 / math.sqrt(2))]
        probs = state_probabilities(state)
        assert abs(probs[0] - 0.5) < 1e-10
        assert abs(probs[1] - 0.5) < 1e-10


# ─── Gate Matrices ───────────────────────────────────────────────────────────

class TestGates:
    def test_hadamard_is_unitary(self):
        # H†H = I
        H_dag = [[H_MATRIX[j][i].conjugate() for j in range(2)] for i in range(2)]
        product = [[sum(H_dag[i][k] * H_MATRIX[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
        for i in range(2):
            for j in range(2):
                expected = 1.0 if i == j else 0.0
                assert abs(product[i][j] - expected) < 1e-10

    def test_hadamard_squared_is_identity(self):
        # H^2 = I
        H2 = [[sum(H_MATRIX[i][k] * H_MATRIX[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
        for i in range(2):
            for j in range(2):
                expected = 1.0 if i == j else 0.0
                assert abs(H2[i][j] - expected) < 1e-10

    def test_hadamard_on_zero(self):
        # H|0⟩ = |+⟩ = 1/√2(|0⟩ + |1⟩)
        state = [complex(1, 0), complex(0, 0)]
        result = apply_single_qubit_gate(state, H_MATRIX, 0, 1)
        assert abs(result[0] - 1 / math.sqrt(2)) < 1e-10
        assert abs(result[1] - 1 / math.sqrt(2)) < 1e-10

    def test_hadamard_on_one(self):
        # H|1⟩ = |−⟩ = 1/√2(|0⟩ - |1⟩)
        state = [complex(0, 0), complex(1, 0)]
        result = apply_single_qubit_gate(state, H_MATRIX, 0, 1)
        assert abs(result[0] - 1 / math.sqrt(2)) < 1e-10
        assert abs(result[1] + 1 / math.sqrt(2)) < 1e-10

    def test_rotation_gate_k1(self):
        # R_1 = [[1,0],[0,e^(πi)]] = [[1,0],[0,-1]] = Z gate
        R1 = rotation_gate(1)
        assert abs(R1[0][0] - 1.0) < 1e-10
        assert abs(R1[1][1] + 1.0) < 1e-10

    def test_rotation_gate_k2(self):
        # R_2 = [[1,0],[0,e^(πi/2)]] = [[1,0],[0,i]] = S gate
        R2 = rotation_gate(2)
        assert abs(R2[1][1] - 1j) < 1e-10

    def test_controlled_rotation_is_unitary(self):
        cr = controlled_rotation_gate(2)
        cr_dag = [[cr[j][i].conjugate() for j in range(4)] for i in range(4)]
        product = [[sum(cr_dag[i][k] * cr[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
        for i in range(4):
            for j in range(4):
                expected = 1.0 if i == j else 0.0
                assert abs(product[i][j] - expected) < 1e-10


# ─── Single Qubit Gate Application ──────────────────────────────────────────

class TestSingleQubitGates:
    def test_identity_preserves_state(self):
        state = basis_state(2, 3)
        result = apply_single_qubit_gate(state, I_MATRIX, 0, 2)
        for i in range(4):
            assert abs(result[i] - state[i]) < 1e-10

    def test_x_gate_flips_bit(self):
        # X|0⟩ = |1⟩
        state = [complex(1, 0), complex(0, 0)]
        result = apply_single_qubit_gate(state, X_MATRIX, 0, 1)
        assert abs(result[0]) < 1e-10
        assert abs(result[1] - 1.0) < 1e-10

    def test_hadamard_on_qubit1_of_2(self):
        # Apply H to qubit 1 (LSB) of |00⟩ → |0⟩⊗|+⟩ = 1/√2(|00⟩ + |01⟩)
        state = basis_state(2, 0)  # |00⟩
        result = apply_single_qubit_gate(state, H_MATRIX, 1, 2)
        assert abs(result[0] - 1 / math.sqrt(2)) < 1e-10
        assert abs(result[1] - 1 / math.sqrt(2)) < 1e-10
        assert abs(result[2]) < 1e-10
        assert abs(result[3]) < 1e-10

    def test_hadamard_on_qubit0_of_2(self):
        # Apply H to qubit 0 (MSB) of |00⟩ → |+⟩⊗|0⟩ = 1/√2(|00⟩ + |10⟩)
        state = basis_state(2, 0)  # |00⟩
        result = apply_single_qubit_gate(state, H_MATRIX, 0, 2)
        assert abs(result[0] - 1 / math.sqrt(2)) < 1e-10
        assert abs(result[2] - 1 / math.sqrt(2)) < 1e-10
        assert abs(result[1]) < 1e-10
        assert abs(result[3]) < 1e-10


# ─── QFT Matrix ─────────────────────────────────────────────────────────────

class TestQFTMatrix:
    def test_qft_matrix_1qubit(self):
        # 1-qubit QFT = Hadamard
        F = qft_matrix(1)
        assert abs(F[0][0] - 1 / math.sqrt(2)) < 1e-10
        assert abs(F[0][1] - 1 / math.sqrt(2)) < 1e-10
        assert abs(F[1][0] - 1 / math.sqrt(2)) < 1e-10
        assert abs(F[1][1] + 1 / math.sqrt(2)) < 1e-10

    def test_qft_matrix_is_unitary(self):
        for n in range(1, 5):
            F = qft_matrix(n)
            N = 2 ** n
            F_dag = [[F[k][j].conjugate() for k in range(N)] for j in range(N)]
            product = [[sum(F_dag[i][k] * F[k][j] for k in range(N)) for j in range(N)] for i in range(N)]
            for i in range(N):
                for j in range(N):
                    expected = 1.0 if i == j else 0.0
                    assert abs(product[i][j] - expected) < 1e-8, f"Failed for n={n}, i={i}, j={j}"

    def test_qft_matrix_diagonal_entries(self):
        # F_N[0][0] = 1/√N
        for n in range(1, 5):
            F = qft_matrix(n)
            N = 2 ** n
            assert abs(F[0][0] - 1 / math.sqrt(N)) < 1e-10

    def test_inverse_qft_matrix(self):
        # F†F = I
        for n in range(1, 4):
            F = qft_matrix(n)
            F_inv = inverse_qft_matrix(n)
            N = 2 ** n
            product = [[sum(F_inv[i][k] * F[k][j] for k in range(N)) for j in range(N)] for i in range(N)]
            for i in range(N):
                for j in range(N):
                    expected = 1.0 if i == j else 0.0
                    assert abs(product[i][j] - expected) < 1e-8


# ─── QFT Circuit vs Matrix ──────────────────────────────────────────────────

class TestQFTCircuitVsMatrix:
    """Verify that the circuit-based QFT matches the matrix QFT exactly."""

    def test_circuit_matches_matrix_1qubit(self):
        F = qft_matrix(1)
        for s in range(2):
            state = basis_state(1, s)
            circuit_result = apply_qft(state, 1)
            matrix_result = apply_matrix(state, F)
            for i in range(2):
                assert abs(circuit_result[i] - matrix_result[i]) < 1e-10

    def test_circuit_matches_matrix_2qubits(self):
        F = qft_matrix(2)
        for s in range(4):
            state = basis_state(2, s)
            circuit_result = apply_qft(state, 2)
            matrix_result = apply_matrix(state, F)
            for i in range(4):
                assert abs(circuit_result[i] - matrix_result[i]) < 1e-10

    def test_circuit_matches_matrix_3qubits(self):
        F = qft_matrix(3)
        for s in range(8):
            state = basis_state(3, s)
            circuit_result = apply_qft(state, 3)
            matrix_result = apply_matrix(state, F)
            for i in range(8):
                assert abs(circuit_result[i] - matrix_result[i]) < 1e-10


# ─── QFT Round-Trip (QFT → IQFT) ───────────────────────────────────────────

class TestQFTRoundTrip:
    def test_roundtrip_basis_states_3qubit(self):
        for s in range(8):
            state = basis_state(3, s)
            result = apply_inverse_qft(apply_qft(state, 3), 3)
            assert fidelity(state, result) > 1 - 1e-10

    def test_roundtrip_basis_states_4qubit(self):
        for s in range(16):
            state = basis_state(4, s)
            result = apply_inverse_qft(apply_qft(state, 4), 4)
            assert fidelity(state, result) > 1 - 1e-10

    def test_roundtrip_superposition(self):
        # Create arbitrary superposition
        n = 3
        N = 8
        state = [complex(1 / math.sqrt(N))] * N
        result = apply_inverse_qft(apply_qft(state, n), n)
        assert fidelity(state, result) > 1 - 1e-10


# ─── QFT Properties ─────────────────────────────────────────────────────────

class TestQFTProperties:
    def test_qft_of_zero_gives_uniform(self):
        # QFT|0⟩ = uniform superposition
        n = 3
        state = basis_state(n, 0)
        result = apply_qft(state, n)
        expected_prob = 1.0 / (2 ** n)
        for p in state_probabilities(result):
            assert abs(p - expected_prob) < 1e-10

    def test_qft_of_uniform_gives_zero(self):
        # QFT of uniform superposition = |0⟩
        n = 3
        N = 8
        state = [complex(1 / math.sqrt(N))] * N
        result = apply_qft(state, n)
        assert abs(abs(result[0]) ** 2 - 1.0) < 1e-10
        for i in range(1, N):
            assert abs(result[i]) ** 2 < 1e-10

    def test_qft_preserves_norm(self):
        for n in range(1, 5):
            for s in range(2 ** n):
                state = basis_state(n, s)
                result = apply_qft(state, n)
                norm_sq = sum(abs(a) ** 2 for a in result)
                assert abs(norm_sq - 1.0) < 1e-10

    def test_qft_is_unitary(self):
        # QFT applied to all basis states should give orthonormal outputs
        n = 3
        N = 8
        outputs = [apply_qft(basis_state(n, s), n) for s in range(N)]
        for i in range(N):
            for j in range(N):
                ip = inner_product(outputs[i], outputs[j])
                expected = 1.0 if i == j else 0.0
                assert abs(ip - expected) < 1e-10


# ─── Reverse Qubits ─────────────────────────────────────────────────────────

class TestReverseQubits:
    def test_reverse_preserves_norm(self):
        state = basis_state(3, 5)  # |101⟩
        reversed_state = reverse_qubits(state, 3)
        norm_sq = sum(abs(a) ** 2 for a in reversed_state)
        assert abs(norm_sq - 1.0) < 1e-10

    def test_reverse_bit_order(self):
        # |101⟩ (index 5) → |101⟩ (index 5) for 3 qubits
        state = basis_state(3, 5)
        result = reverse_qubits(state, 3)
        assert abs(result[5] - 1.0) < 1e-10

    def test_reverse_non_symmetric(self):
        # |001⟩ (index 1) → |100⟩ (index 4) for 3 qubits
        state = basis_state(3, 1)
        result = reverse_qubits(state, 3)
        assert abs(result[4] - 1.0) < 1e-10


# ─── Period Finding ─────────────────────────────────────────────────────────

class TestPeriodFinding:
    def test_period_finding_basic(self):
        result = period_finding_qft(4, 6)
        assert result['period'] == 4
        assert result['n_qubits'] == 6
        assert len(result['peaks']) > 0

    def test_period_finding_peak_spacing(self):
        # For period r, peaks should appear at multiples of N/r
        r = 4
        n = 6
        result = period_finding_qft(r, n)
        N = 2 ** n
        expected_spacing = N // r
        peak_indices = [idx for idx, _ in result['peaks']]
        if len(peak_indices) >= 2:
            spacing = peak_indices[1] - peak_indices[0]
            assert abs(spacing - expected_spacing) <= 1

    def test_period_finding_probabilities_sum_to_one(self):
        result = period_finding_qft(3, 6)
        total = sum(result['probabilities'])
        assert abs(total - 1.0) < 1e-10


# ─── Fidelity and Inner Product ─────────────────────────────────────────────

class TestFidelityAndInnerProduct:
    def test_fidelity_same_state(self):
        state = basis_state(3, 5)
        assert abs(fidelity(state, state) - 1.0) < 1e-10

    def test_fidelity_orthogonal_states(self):
        s1 = basis_state(3, 0)
        s2 = basis_state(3, 1)
        assert abs(fidelity(s1, s2)) < 1e-10

    def test_fidelity_partial_overlap(self):
        # |+⟩ and |0⟩: F = |⟨0|+⟩|^2 = 1/2
        s1 = [complex(1, 0), complex(0, 0)]
        s2 = [complex(1 / math.sqrt(2)), complex(1 / math.sqrt(2))]
        assert abs(fidelity(s1, s2) - 0.5) < 1e-10

    def test_inner_product_conjugate_symmetry(self):
        s1 = [complex(1, 1), complex(0, 1)]
        s2 = [complex(0, 1), complex(1, 0)]
        ip12 = inner_product(s1, s2)
        ip21 = inner_product(s2, s1)
        assert abs(ip12 - ip21.conjugate()) < 1e-10

    def test_tensor_product_length(self):
        s1 = [complex(1, 0), complex(0, 0)]
        s2 = [complex(1, 0), complex(0, 0)]
        result = tensor_product(s1, s2)
        assert len(result) == 4
        assert abs(result[0] - 1.0) < 1e-10


# ─── State Info ──────────────────────────────────────────────────────────────

class TestStateInfo:
    def test_state_info_basis_state(self):
        state = basis_state(3, 5)
        info = state_info(state, 3)
        assert info['n_qubits'] == 3
        assert info['dimension'] == 8
        assert len(info['nonzero_components']) == 1
        assert info['nonzero_components'][0]['index'] == 5
        assert info['nonzero_components'][0]['label'] == '101'

    def test_state_info_uniform_superposition(self):
        n = 3
        N = 8
        state = [complex(1 / math.sqrt(N))] * N
        info = state_info(state, n)
        assert len(info['nonzero_components']) == 8
        assert abs(info['total_probability'] - 1.0) < 1e-10


# ─── CLI ─────────────────────────────────────────────────────────────────────

class TestCLI:
    def test_qft_command(self):
        from cli import main
        assert main(["qft", "-n", "3", "-s", "0"]) == 0

    def test_qft_verify_command(self):
        from cli import main
        assert main(["qft", "-n", "3", "-s", "5", "--verify"]) == 0

    def test_iqft_command(self):
        from cli import main
        assert main(["iqft", "-n", "3", "-s", "2"]) == 0

    def test_matrix_command(self):
        from cli import main
        assert main(["matrix", "-n", "3"]) == 0

    def test_matrix_verify_command(self):
        from cli import main
        assert main(["matrix", "-n", "3", "--verify"]) == 0

    def test_period_command(self):
        from cli import main
        assert main(["period", "-r", "4", "-n", "6"]) == 0

    def test_superposition_command(self):
        from cli import main
        assert main(["superposition", "-n", "3"]) == 0

    def test_phase_est_command(self):
        from cli import main
        assert main(["phase-est", "--phases", "0.25,0.5", "--ancilla-qubits", "4"]) == 0

    def test_qft_invalid_state(self):
        from cli import main
        assert main(["qft", "-n", "2", "-s", "5"]) == 1
