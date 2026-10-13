'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const QFT = require('../web/qft.js');

const tolerance = 1e-10;
const near = (a, b) => Math.abs(a - b) < tolerance;

test('QFT matches the analytic Fourier matrix on every basis vector (1–6 qubits)', () => {
  for (let n = 1; n <= 6; n++) {
    const size = 2 ** n;
    for (let input = 0; input < size; input++) {
      const state = QFT.transform(QFT.prepare(n, input), n);
      for (let output = 0; output < size; output++) {
        const angle = 2 * Math.PI * input * output / size;
        assert.ok(near(state[output][0], Math.cos(angle) / Math.sqrt(size)));
        assert.ok(near(state[output][1], Math.sin(angle) / Math.sqrt(size)));
      }
    }
  }
});

test('QFT and inverse QFT round-trip both basis and uniform states', () => {
  for (let n = 1; n <= 8; n++) {
    for (const state of [QFT.prepare(n, 2 ** n - 1), QFT.prepare(n, 0, true)]) {
      const recovered = QFT.transform(QFT.transform(state, n), n, true);
      recovered.forEach(([re, im], i) => {
        assert.ok(near(re, state[i][0]));
        assert.ok(near(im, state[i][1]));
      });
    }
  }
});

test('probability is conserved', () => {
  const state = QFT.transform(QFT.prepare(8, 67), 8);
  assert.ok(near(state.reduce((sum, a) => sum + QFT.probability(a), 0), 1));
});

test('rejects invalid input instead of allocating massive states', () => {
  for (const [n, state] of [[0, 0], [9, 0], [3, -1], [3, 8], [3, 1.5], [3.2, 1]]) {
    assert.throws(() => QFT.prepare(n, state), RangeError);
  }
  assert.throws(() => QFT.transform([], 3), TypeError);
});
