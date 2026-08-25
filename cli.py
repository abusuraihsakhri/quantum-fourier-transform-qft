"""
CLI for Quantum Fourier Transform (QFT) Engine.
Provides commands for QFT computation, inverse QFT, period finding, and matrix display.
"""
import argparse
import cmath
import json
import math
import sys

from qft_engine.engine import (
    apply_qft, apply_inverse_qft, apply_matrix,
    qft_matrix, inverse_qft_matrix,
    basis_state, zero_state, normalize_state,
    state_probabilities, state_info, fidelity,
    period_finding_qft, phase_estimation_simple,
    reverse_qubits, tensor_product,
)


def cmd_qft(args):
    """Apply QFT to a computational basis state |j⟩."""
    n = args.qubits
    N = 2 ** n
    if args.state >= N:
        print(f"Error: state index {args.state} out of range for {n} qubits (max {N-1})")
        return 1
    state = basis_state(n, args.state)
    result = apply_qft(state, n)
    info = state_info(result, n, threshold=1e-8)
    print(f"QFT of |{args.state}⟩ ({n} qubits, {N}D Hilbert space):")
    print(f"  Total probability: {info['total_probability']:.10f}")
    for comp in info['nonzero_components']:
        amp = comp['amplitude']
        print(f"  |{comp['label']}⟩: amplitude = {amp.real:+.6f}{amp.imag:+.6f}i  "
              f"prob = {comp['probability']:.6f}  phase = {comp['phase_deg']:.1f}°")
    if args.verify:
        recovered = apply_inverse_qft(result, n)
        fid = fidelity(state, recovered)
        print(f"\n  Round-trip fidelity (QFT → IQFT): {fid:.10f}")
    return 0


def cmd_iqft(args):
    """Apply inverse QFT to a state."""
    n = args.qubits
    N = 2 ** n
    if args.state >= N:
        print(f"Error: state index {args.state} out of range for {n} qubits (max {N-1})")
        return 1
    # Apply QFT first, then inverse QFT to verify
    state = basis_state(n, args.state)
    qft_state = apply_qft(state, n)
    recovered = apply_inverse_qft(qft_state, n)
    fid = fidelity(state, recovered)
    print(f"Inverse QFT verification ({n} qubits):")
    print(f"  Original state: |{args.state}⟩")
    print(f"  After QFT → IQFT round-trip fidelity: {fid:.10f}")
    info = state_info(recovered, n, threshold=1e-6)
    for comp in info['nonzero_components']:
        print(f"  |{comp['label']}⟩: prob = {comp['probability']:.6f}")
    return 0


def cmd_matrix(args):
    """Display the QFT or inverse QFT matrix."""
    n = args.qubits
    if n > 5:
        print(f"Warning: displaying {2**n}×{2**n} matrix. Consider n≤5.")
    N = 2 ** n
    if args.inverse:
        mat = inverse_qft_matrix(n)
        label = "Inverse QFT"
    else:
        mat = qft_matrix(n)
        label = "QFT"
    print(f"{label} matrix F_{N} ({n} qubits):")
    print(f"  F[j][k] = 1/√{N} × ω^(jk), ω = e^(2πi/{N})")
    print()
    for j in range(min(N, 16)):  # Limit display
        row_str = "  [" + "  ".join(
            f"{mat[j][k].real:+.3f}{mat[j][k].imag:+.3f}i" for k in range(min(N, 8))
        )
        if N > 8:
            row_str += "  ..."
        row_str += "]"
        print(row_str)
    if N > 16:
        print(f"  ... ({N - 16} more rows)")
    # Verify unitarity: F†F = I
    if args.verify:
        # F† = conjugate transpose
        F_dag = [[mat[k][j].conjugate() for k in range(N)] for j in range(N)]
        product = [[sum(F_dag[i][k] * mat[k][j] for k in range(N)) for j in range(N)] for i in range(N)]
        max_off_diag = 0
        for i in range(N):
            for j in range(N):
                expected = 1.0 if i == j else 0.0
                diff = abs(product[i][j] - expected)
                max_off_diag = max(max_off_diag, diff)
        print(f"\n  Unitarity check (max |F†F - I| entry): {max_off_diag:.2e}")
    return 0


def cmd_period(args):
    """Demonstrate period finding using QFT."""
    result = period_finding_qft(args.period, args.qubits)
    print(f"Period finding with QFT:")
    print(f"  Period r = {result['period']}, Qubits = {result['n_qubits']}")
    print(f"  State dimension = {result['state_size']}")
    print(f"  Expected peak spacing: N/r = {result['expected_peak_spacing']}")
    print(f"\n  Peaks in QFT output (probability > 50% of max):")
    for idx, prob in result['peaks']:
        print(f"    |{idx}⟩: prob = {prob:.6f}")
    if args.show_probs:
        print(f"\n  Full probability distribution:")
        probs = result['probabilities']
        for i, p in enumerate(probs):
            if p > 0.001:
                print(f"    |{i}⟩: {'█' * int(p * 50):50s} {p:.6f}")
    return 0


def cmd_superposition(args):
    """Apply QFT to a uniform superposition state."""
    n = args.qubits
    N = 2 ** n
    # Create uniform superposition: H⊗n|0⟩
    state = [complex(1.0 / math.sqrt(N), 0)] * N
    result = apply_qft(state, n)
    print(f"QFT of uniform superposition ({n} qubits):")
    info = state_info(result, n, threshold=1e-6)
    print(f"  Total probability: {info['total_probability']:.10f}")
    for comp in info['nonzero_components']:
        print(f"  |{comp['label']}⟩: prob = {comp['probability']:.6f}")
    # QFT of uniform superposition should give |0⟩
    fid = fidelity(basis_state(n, 0), result)
    print(f"\n  Fidelity with |0⟩: {fid:.10f}")
    return 0


def cmd_phase_est(args):
    """Run simple phase estimation demo."""
    phases = [float(x) for x in args.phases.split(',')]
    n = args.ancilla_qubits
    estimated = phase_estimation_simple(phases, n)
    print(f"Phase estimation ({n} ancilla qubits):")
    print(f"  Input phases: {phases}")
    print(f"  Estimated phases: {estimated}")
    for phi in phases:
        best_est = min(estimated, key=lambda e: min(abs(e - phi), abs(e - phi - 1), abs(e - phi + 1)))
        error = min(abs(best_est - phi), abs(best_est - phi - 1), abs(best_est - phi + 1))
        print(f"  Phase {phi:.6f} → estimated {best_est:.6f}, error = {error:.6f}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="quantum-fourier-transform-qft",
        description="Quantum Fourier Transform (QFT) — real quantum state vector simulation"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # qft
    p = sub.add_parser("qft", help="Apply QFT to basis state |j⟩")
    p.add_argument("-n", "--qubits", type=int, default=3, help="Number of qubits (default: 3)")
    p.add_argument("-s", "--state", type=int, default=0, help="Basis state index (default: 0)")
    p.add_argument("--verify", action="store_true", help="Verify round-trip QFT→IQFT")

    # iqft
    p = sub.add_parser("iqft", help="Verify inverse QFT round-trip")
    p.add_argument("-n", "--qubits", type=int, default=3, help="Number of qubits")
    p.add_argument("-s", "--state", type=int, default=0, help="Basis state index")

    # matrix
    p = sub.add_parser("matrix", help="Display QFT matrix")
    p.add_argument("-n", "--qubits", type=int, default=3, help="Number of qubits")
    p.add_argument("--inverse", action="store_true", help="Show inverse QFT matrix")
    p.add_argument("--verify", action="store_true", help="Verify unitarity")

    # period
    p = sub.add_parser("period", help="Period finding with QFT")
    p.add_argument("-r", "--period", type=int, default=4, help="Period to find")
    p.add_argument("-n", "--qubits", type=int, default=6, help="Number of qubits")
    p.add_argument("--show-probs", action="store_true", help="Show full probability distribution")

    # superposition
    p = sub.add_parser("superposition", help="QFT of uniform superposition")
    p.add_argument("-n", "--qubits", type=int, default=3, help="Number of qubits")

    # phase-est
    p = sub.add_parser("phase-est", help="Simple phase estimation demo")
    p.add_argument("--phases", type=str, default="0.25,0.5", help="Comma-separated phases")
    p.add_argument("--ancilla-qubits", type=int, default=4, help="Number of ancilla qubits")

    args = parser.parse_args(argv)

    handlers = {
        'qft': cmd_qft,
        'iqft': cmd_iqft,
        'matrix': cmd_matrix,
        'period': cmd_period,
        'superposition': cmd_superposition,
        'phase-est': cmd_phase_est,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
