"""Regression tests for QFT input validation and independent phase estimates."""
import pytest

from qft_engine.engine import (
    apply_qft, apply_inverse_qft, basis_state, zero_state,
    qft_matrix, phase_estimation_simple, period_finding_qft,
)


@pytest.mark.parametrize("qubits,index", [(0, 0), (-1, 0), (3, -1), (3, 8), (13, 0)])
def test_basis_state_rejects_invalid_dimensions(qubits, index):
    with pytest.raises(ValueError):
        basis_state(qubits, index)


@pytest.mark.parametrize("qubits", [0, -1, 13])
def test_zero_state_rejects_invalid_dimensions(qubits):
    with pytest.raises(ValueError):
        zero_state(qubits)


def test_qft_rejects_mismatched_state_dimensions():
    with pytest.raises(ValueError):
        apply_qft([1 + 0j, 0j], 3)
    with pytest.raises(ValueError):
        apply_inverse_qft([1 + 0j, 0j], 3)


@pytest.mark.parametrize("qubits", [0, -1, 7])
def test_matrix_allocation_has_explicit_limit(qubits):
    with pytest.raises(ValueError):
        qft_matrix(qubits)


@pytest.mark.parametrize("period", [0, -2, 65])
def test_period_finding_rejects_invalid_period(period):
    with pytest.raises(ValueError):
        period_finding_qft(period, 6)


def test_phase_estimation_eigenphases_are_independent():
    estimates = phase_estimation_simple([0.25, 0.5], 4)
    assert estimates == pytest.approx([0.25, 0.5])


def test_phase_estimation_wraps_phases_into_unit_interval():
    assert phase_estimation_simple([-0.25, 1.25], 4) == pytest.approx([0.25, 0.75])


@pytest.mark.parametrize("phases", [[], [float("nan")], [float("inf")]])
def test_phase_estimation_rejects_nonfinite_or_empty_phases(phases):
    with pytest.raises(ValueError):
        phase_estimation_simple(phases, 4)


@pytest.mark.parametrize("args", [
    ["qft", "-n", "3", "-s", "-1"],
    ["qft", "-n", "0"],
    ["matrix", "-n", "9"],
    ["period", "-r", "0"],
    ["phase-est", "--phases", "nan"],
])
def test_cli_handles_invalid_input_without_tracebacks(args):
    from cli import main
    assert main(args) == 1


def test_legacy_agent_module_and_api_can_initialize():
    from qft_engine.agents import QFTCoordinator
    from qft_engine.models import FrontierPayload
    from qft_engine.server import create_app
    coordinator = QFTCoordinator()
    output = coordinator.process(FrontierPayload(
        task_id="SYNTHETIC-1",
        target_identifier="QFT-TEST",
        primary_metric=0.5,
        secondary_metric=0.1,
        status_descriptor="NOMINAL",
    ))
    assert output["total_alerts"] == 0
    assert create_app() is not None
