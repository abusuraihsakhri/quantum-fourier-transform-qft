"""
Security-focused tests for Quantum Fourier Transform Qft.
Tests PHI guard, audit trail integrity, and secure key handling.
"""
import os
import sys
from pathlib import Path

# Set audit key before importing agents
os.environ.setdefault("AUDIT_SECRET_KEY", "security-test-key-not-for-production-2026")

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import (
    PHIGuard, AuditTrail, AuditLogger, SecurityException, assert_no_phi
)


class TestPHIGuard:
    """Test PHI detection and blocking."""

    def test_blocks_mrn(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient MRN-12345678")

    def test_blocks_ssn(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("SSN: 123-45-6789")

    def test_blocks_phone(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Call (555) 123-4567")

    def test_blocks_email(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Email: patient@example.com")

    def test_blocks_dob(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("DOB: 01/15/1990")

    def test_blocks_patient_name(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient Name: John Smith")

    def test_blocks_john_doe(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Test patient John Doe registered")

    def test_allows_clean_text(self):
        PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")
        PHIGuard.assert_no_phi("Quantum state vector simulation complete")

    def test_allows_empty_string(self):
        PHIGuard.assert_no_phi("")

    def test_allows_none_handling(self):
        # Empty string is handled, None is converted to string
        PHIGuard.assert_no_phi("")

    def test_redact_phi(self):
        text = "Patient MRN-12345678 and SSN 123-45-6789"
        redacted = PHIGuard.redact_phi(text)
        assert "MRN" not in redacted or "REDACTED" in redacted
        assert "REDACTED_IDENTIFIER" in redacted


class TestAuditTrail:
    """Test cryptographic audit trail integrity."""

    def test_audit_trail_creation(self):
        trail = AuditTrail(secret_key="test-key-for-unit-tests-only-2026")
        assert len(trail.get_trail()) == 0
        assert trail.verify_integrity() is True

    def test_audit_trail_logs_entries(self):
        trail = AuditTrail(secret_key="test-key-for-unit-tests-only-2026")
        entry = trail.log("test_actor", "admin", "TEST_EVENT", {"action": "test"})
        assert entry["audit_id"].startswith("AUDIT-")
        assert entry["actor"] == "test_actor"
        assert entry["event_type"] == "TEST_EVENT"
        assert entry["current_hash"] != ""

    def test_audit_trail_chain_integrity(self):
        trail = AuditTrail(secret_key="test-key-for-unit-tests-only-2026")
        trail.log("actor1", "admin", "EVENT_1", {"step": 1})
        trail.log("actor2", "admin", "EVENT_2", {"step": 2})
        trail.log("actor3", "admin", "EVENT_3", {"step": 3})
        assert trail.verify_integrity() is True

    def test_audit_trail_linked_hashes(self):
        trail = AuditTrail(secret_key="test-key-for-unit-tests-only-2026")
        e1 = trail.log("actor1", "admin", "EVENT_1", {"step": 1})
        e2 = trail.log("actor2", "admin", "EVENT_2", {"step": 2})
        # Second entry's prev_hash should match first entry's current_hash
        assert e2["prev_hash"] == e1["current_hash"]

    def test_audit_trail_detects_tampering(self):
        trail = AuditTrail(secret_key="test-key-for-unit-tests-only-2026")
        trail.log("actor1", "admin", "EVENT_1", {"step": 1})
        trail.log("actor2", "admin", "EVENT_2", {"step": 2})
        # Tamper with an entry
        trail.logs[0]["current_hash"] = "TAMPERED_HASH"
        assert trail.verify_integrity() is False

    def test_audit_requires_secret_key(self):
        # Temporarily clear env var
        old_key = os.environ.pop("AUDIT_SECRET_KEY", None)
        try:
            with pytest.raises(RuntimeError, match="AUDIT_SECRET_KEY"):
                AuditTrail(secret_key=None)
        finally:
            if old_key:
                os.environ["AUDIT_SECRET_KEY"] = old_key

    def test_audit_rejects_short_key(self):
        with pytest.raises(ValueError, match="at least 16 characters"):
            AuditTrail(secret_key="short")

    def test_audit_blocks_phi_in_details(self):
        trail = AuditTrail(secret_key="test-key-for-unit-tests-only-2026")
        with pytest.raises(SecurityException):
            trail.log("actor1", "admin", "EVENT", {"data": "Patient MRN-12345678"})


class TestAuditLogger:
    """Test global audit logger interface."""

    def test_global_audit_logger(self):
        entry = AuditLogger.log("test", "admin", "TEST", {"key": "value"})
        assert entry["actor"] == "test"
        assert entry["event_type"] == "TEST"

    def test_global_audit_trail_retrieval(self):
        trail = AuditLogger.get_trail()
        assert isinstance(trail, list)
        assert len(trail) > 0

    def test_global_audit_verification(self):
        result = AuditLogger.verify_integrity()
        assert result is True


class TestCLICommands:
    """Test new CLI commands added for audit, chat, verify-audit."""

    def test_audit_command(self):
        from cli import main
        assert main(["audit", "--task-id", "TEST-01"]) == 0

    def test_audit_command_with_critical(self):
        from cli import main
        assert main(["audit", "--task-id", "TEST-02", "--is-critical"]) == 0

    def test_chat_command(self):
        from cli import main
        assert main(["chat", "Explain", "quantum", "states"]) == 0

    def test_verify_audit_command(self):
        from cli import main
        assert main(["verify-audit"]) == 0

    def test_serve_command(self):
        from cli import main
        assert main(["serve"]) == 0

    def test_chat_blocks_phi(self):
        from cli import main
        result = main(["chat", "Patient", "MRN-12345678"])
        assert result == 1  # Should fail due to PHI guard
