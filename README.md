# Quantum Fourier Transform (QFT)

> **Domain:** Quantum Computing Simulation & Post-Quantum Cryptography  
> **Standards:** NIST FIPS 203/204/205, NIST SP 800-90B

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg?logo=python&logoColor=white)
![QFT Engine](https://img.shields.io/badge/QFT-Circuit%20%2B%20Matrix-brightgreen.svg)

</div>

---

## Overview

A real Quantum Fourier Transform (QFT) implementation using state vector simulation with Python stdlib only. Provides both circuit-based and matrix-based QFT computation, inverse QFT, period finding, and phase estimation.

The QFT transforms computational basis states to Fourier basis:
```
|j⟩ → 1/√N Σ_k ω^(jk) |k⟩  where ω = e^(2πi/N), N = 2^n
```

---

## Features

- **Circuit-based QFT**: Standard gate decomposition with Hadamard and controlled rotation gates
- **Matrix-based QFT**: Direct matrix construction for verification
- **Inverse QFT**: QFT† for round-trip verification
- **Period Finding**: QFT-based period extraction demonstration
- **Phase Estimation**: Simple quantum phase estimation
- **CLI Interface**: Full command-line interface for all operations
- **Enterprise Agents**: Supervisor orchestrator with multi-worker evaluation
- **PHI Guard**: Outbound PHI detection and blocking
- **Audit Trail**: HMAC-SHA256 tamper-evident logging

---

## Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/quantum-fourier-transform-qft.git
cd quantum-fourier-transform-qft

# Install dependencies
pip install -e .

# Optional: Install FastAPI for REST API server
pip install fastapi uvicorn pydantic
```

---

## Quickstart

### CLI Commands

```bash
# Apply QFT to basis state |5⟩ with 3 qubits
python cli.py qft -n 3 -s 5 --verify

# Display QFT matrix for 3 qubits with unitarity check
python cli.py matrix -n 3 --verify

# Demonstrate period finding with QFT
python cli.py period -r 4 -n 6 --show-probs

# QFT of uniform superposition (should give |0⟩)
python cli.py superposition -n 3

# Phase estimation demo
python cli.py phase-est --phases "0.25,0.5" --ancilla-qubits 4

# Run audit task evaluation
python cli.py audit --task-id TASK-01 --primary-metric 15.0

# Chat with supervisor
python cli.py chat "Explain quantum Fourier transform"

# Verify audit trail integrity
python cli.py verify-audit
```

### Python API

```python
from qft_engine.engine import apply_qft, basis_state, fidelity, state_info

# Create |3⟩ state for 3 qubits
state = basis_state(3, 3)

# Apply QFT
result = apply_qft(state, 3)

# Check result info
info = state_info(result, 3)
for comp in info['nonzero_components']:
    print(f"|{comp['label']}⟩: prob = {comp['probability']:.4f}")
```

---

## Testing

```bash
# Set audit key (required for tests)
export AUDIT_SECRET_KEY="test-key-for-development-only"

# Run all tests
pytest -v

# Run specific test suites
pytest tests/test_qft_engine.py -v
pytest tests/test_security.py -v
pytest tests/test_enrichment.py -v
```

**Test Results:** 70+ tests covering:
- State vector operations
- Gate matrix unitarity
- QFT circuit vs matrix consistency
- Round-trip fidelity (QFT → IQFT)
- QFT mathematical properties (unitarity, norm preservation)
- Period finding accuracy
- PHI guard enforcement
- Audit trail integrity and tamper detection
- CLI command execution

---

## Architecture

```
quantum-fourier-transform-qft/
├── cli.py                    # Main CLI entry point
├── simulator.py              # High-throughput simulation
├── enrichment.py             # Feature enrichment engines
├── qft_engine/
│   └── engine.py             # Core QFT implementation
├── agents/
│   ├── base.py               # Security, PHI guard, audit trail
│   ├── models.py             # Pydantic data models
│   ├── workers.py            # Domain worker agents
│   ├── supervisor.py         # Master orchestrator
│   ├── api.py                # FastAPI REST server
│   ├── metrics.py            # Prometheus telemetry
│   ├── learning.py           # Bayesian calibration
│   ├── llm_factory.py        # LLM provider abstraction
│   └── streamer.py           # WebSocket telemetry
├── tests/                    # Test suite
├── web/index.html            # Operations console
├── Dockerfile                # Container build
└── docker-compose.yml        # Container orchestration
```

---

## Security

- **PHI Guard**: Active regex inspection blocking SSNs, MRNs, phone numbers, emails, DOBs, and patient names
- **Audit Trail**: HMAC-SHA256 chained, cryptographically signed logs with tamper detection
- **Secure Key Management**: `AUDIT_SECRET_KEY` environment variable required (no hardcoded defaults)

### Setting the Audit Key

```bash
# Generate a secure key
python -c "import secrets; print(secrets.token_hex(32))"

# Set environment variable
export AUDIT_SECRET_KEY="your-generated-key-here"
```

---

## Docker Deployment

```bash
docker build -t quantum-fourier-transform-qft .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY="your-key" quantum-fourier-transform-qft
```

Or with docker-compose:

```bash
AUDIT_SECRET_KEY="your-key" docker-compose up
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.
