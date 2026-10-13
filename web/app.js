(function () {
  'use strict';
  const byId = id => document.getElementById(id);
  const form = byId('controls');
  const qubits = byId('qubits');
  const basis = byId('basis');
  const initial = byId('initial');
  const direction = byId('direction');
  const exportButton = byId('export');
  let latest = null;

  function updateControls() {
    const n = Number(qubits.value);
    if (Number.isInteger(n) && n >= 1 && n <= QFT.MAX_QUBITS) {
      basis.max = String(2 ** n - 1);
      byId('basis-help').textContent = `Valid range: 0–${basis.max}`;
    } else {
      byId('basis-help').textContent = `Enter 1–${QFT.MAX_QUBITS} qubits.`;
    }
    basis.disabled = initial.value === 'uniform';
  }

  function makeTextCell(row, value) {
    const cell = document.createElement('td');
    cell.textContent = value;
    row.appendChild(cell);
  }

  function render(n, amplitudes, error) {
    const size = 2 ** n;
    const probs = amplitudes.map(QFT.probability);
    const count = Math.min(size, 32);
    const max = Math.max(...probs);
    byId('dimension').textContent = String(size);
    byId('normalization').textContent = probs.reduce((sum, p) => sum + p, 0).toFixed(10);
    byId('error-value').textContent = error.toExponential(2);
    byId('plot-note').textContent = `Showing ${count} of ${size} basis states (bar length scaled to maximum probability).`;
    byId('table-note').textContent = `Showing ${count} of ${size} basis amplitudes.`;
    const plot = document.createDocumentFragment();
    const table = document.createDocumentFragment();
    for (let i = 0; i < count; i++) {
      const [real, imag] = amplitudes[i];
      const label = '|' + i.toString(2).padStart(n, '0') + '⟩';
      const p = probs[i];
      const row = document.createElement('div');
      row.className = 'bar-row';
      const title = document.createElement('span');
      title.textContent = label;
      const track = document.createElement('div');
      track.className = 'bar-track';
      const fill = document.createElement('div');
      fill.className = 'bar-fill';
      fill.style.width = (max === 0 ? 0 : p / max * 100).toFixed(4) + '%';
      track.appendChild(fill);
      const value = document.createElement('span');
      value.textContent = (p * 100).toFixed(2) + '%';
      row.append(title, track, value);
      plot.appendChild(row);
      const tr = document.createElement('tr');
      makeTextCell(tr, label);
      makeTextCell(tr, real.toFixed(6));
      makeTextCell(tr, imag.toFixed(6));
      makeTextCell(tr, (Math.abs(real) + Math.abs(imag) < 1e-10 ? 0 : Math.atan2(imag, real) * 180 / Math.PI).toFixed(2));
      table.appendChild(tr);
    }
    byId('probabilities').replaceChildren(plot);
    byId('amplitudes').replaceChildren(table);
  }

  function calculate(event) {
    event.preventDefault();
    byId('error').textContent = '';
    try {
      if (qubits.value.trim() === '' || (initial.value === 'basis' && basis.value.trim() === '')) {
        throw new Error('Enter a qubit count and basis index.');
      }
      const n = Number(qubits.value);
      const j = initial.value === 'uniform' ? 0 : Number(basis.value);
      QFT.validate(n, j);
      const inverse = direction.value === 'inverse';
      const input = QFT.prepare(n, j, initial.value === 'uniform');
      const output = QFT.transform(input, n, inverse);
      const recovered = QFT.transform(output, n, !inverse);
      const error = Math.max(...recovered.map((a, i) => Math.hypot(a[0] - input[i][0], a[1] - input[i][1])));
      render(n, output, error);
      latest = { qubits: n, input: initial.value, basis_index: initial.value === 'uniform' ? null : j,
        transform: direction.value, amplitudes: output.map(([real, imaginary], index) => ({
          index, real, imaginary, probability: QFT.probability([real, imaginary])
        })) };
      exportButton.disabled = false;
    } catch (error) {
      latest = null;
      exportButton.disabled = true;
      byId('dimension').textContent = '—';
      byId('normalization').textContent = '—';
      byId('error-value').textContent = '—';
      byId('probabilities').replaceChildren();
      byId('amplitudes').replaceChildren();
      byId('plot-note').textContent = 'Correct the input to view the spectrum.';
      byId('table-note').textContent = 'Amplitudes in the computational basis.';
      byId('error').textContent = error.message;
    }
  }

  function exportJson() {
    if (!latest) return;
    const url = URL.createObjectURL(new Blob([JSON.stringify(latest, null, 2)], { type: 'application/json' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = `qft-${latest.qubits}-qubits.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  qubits.addEventListener('input', updateControls);
  initial.addEventListener('change', updateControls);
  form.addEventListener('submit', calculate);
  exportButton.addEventListener('click', exportJson);
  updateControls();
  calculate({ preventDefault() {} });
})();
