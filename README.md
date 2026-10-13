# Quantum Fourier Transform (QFT)

A dependency-free state-vector implementation of the quantum Fourier transform and its inverse, with a browser demonstration, Python functions, and a command-line interface.

## Interactive browser simulator

Open [web/index.html](web/index.html) in a browser, or serve this repository locally:

```bash
python -m http.server 8000
# Open http://localhost:8000/ (redirects to /web/)
```

The static application supports 1–8 qubits, basis states and uniform superpositions, forward/inverse QFT, complex amplitudes, measurement probabilities, round-trip error, and JSON export. All computations run locally in JavaScript. No account, API, external script, or server computation is required. The root `index.html` makes the application suitable for GitHub Pages published from the repository root.

## Mathematical convention

For `n` qubits and `N = 2ⁿ`, the forward transform is

```text
QFT |j⟩ = (1/√N) Σₖ exp(2πijk/N) |k⟩
```

Qubit 0 is the most significant bit. The circuit uses Hadamard gates, controlled phase rotations, and final bit reversal. The inverse uses conjugate phases in reverse gate order.

## Python usage

Requires Python 3.9 or later. The core mathematical engine uses only the standard library; the installed CLI also uses Pydantic.

```bash
python -m pip install -e .
quantum-fourier-transform-qft qft -n 3 -s 5 --verify
quantum-fourier-transform-qft matrix -n 3 --verify
quantum-fourier-transform-qft period -r 4 -n 6
quantum-fourier-transform-qft phase-est --phases "0.25,0.5" --ancilla-qubits 4
```

Equivalent direct entry point: `python cli.py qft -n 3 -s 5 --verify`.

```python
from qft_engine.engine import basis_state, apply_qft, apply_inverse_qft, fidelity

source = basis_state(3, 5)
spectrum = apply_qft(source, 3)
recovered = apply_inverse_qft(spectrum, 3)
assert fidelity(source, recovered) > 1 - 1e-10
```

State-vector transforms are limited to 12 qubits to bound memory and work; explicit dense QFT matrices are limited to 6 qubits. Period finding constructs an idealized periodic state. The phase-estimation example assumes known eigenphases and estimates each independently; it does **not** simulate controlled-unitary evolution or quantum hardware.

## Tests

```bash
python -m pip install -e ".[test,server]"
AUDIT_SECRET_KEY=ci-local-test-key-not-for-production python -m pytest -q
node --check web/qft.js
node --check web/app.js
node --test tests/test_browser_qft.cjs
```

The Python suite covers QFT matrix/circuit agreement, unitarity, inverse round trips, input bounds, CLI operations, and the optional audit subsystem. The Node tests compare the browser implementation with the analytic Fourier matrix and verify inverse round trips. GitHub Actions runs Python 3.10–3.12 and Node 22.

## Optional API and audit subsystem

The repository also contains a legacy mock supervisor/audit subsystem, independent of the QFT state-vector simulator. It is not a quantum hardware controller, validated clinical decision tool, or post-quantum cryptographic implementation.

Install the optional server dependencies and set a unique audit signing key:

```bash
python -m pip install -e ".[server]"
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
python cli.py serve
# Local API: http://127.0.0.1:8000/health
```

Alternatively, use Docker Compose after exporting `AUDIT_SECRET_KEY`:

```bash
docker compose up --build
```

The container binds port 8000. The audit logger retains its HMAC chain **in memory only**; it is not a persistent or independently anchored audit store. The optional API is unauthenticated and should only be exposed in a trusted environment until proper authentication, TLS, durable audit storage, and operational safeguards are implemented. Its identifier filtering is pattern-based and **does not guarantee de-identification**. Do not submit real patient information or secrets to this demonstration.

## Technology and privacy

- Python 3.9+, standard-library QFT math; Pydantic for the CLI's ancillary audit features
- HTML, CSS, dependency-free modern JavaScript for the static browser simulator
- Optional FastAPI/Uvicorn server; Docker Compose
- MIT license: see [LICENSE](LICENSE)

The browser simulator does not call a backend or send entered states to a service; JSON exports are generated locally. The static UI targets current evergreen browsers with modern JavaScript support. The API is separate and should not be used as a public production service without further hardening.
