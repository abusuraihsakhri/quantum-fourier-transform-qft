/* Dependency-free QFT state-vector simulator. Qubit 0 is the most significant bit. */
(function (root) {
  'use strict';
  const MAX_QUBITS = 8;

  function validate(n, index) {
    if (!Number.isInteger(n) || n < 1 || n > MAX_QUBITS) {
      throw new RangeError(`Qubits must be an integer between 1 and ${MAX_QUBITS}.`);
    }
    if (!Number.isInteger(index) || index < 0 || index >= 2 ** n) {
      throw new RangeError(`Basis state must be an integer between 0 and ${2 ** n - 1}.`);
    }
  }

  function prepare(n, index, uniform = false) {
    validate(n, index);
    const size = 2 ** n;
    const state = Array.from({ length: size }, () => [0, 0]);
    if (uniform) {
      const amplitude = 1 / Math.sqrt(size);
      for (const value of state) value[0] = amplitude;
    } else {
      state[index][0] = 1;
    }
    return state;
  }

  function hadamard(state, n, target) {
    const mask = 1 << (n - 1 - target);
    const scale = 1 / Math.sqrt(2);
    for (let i = 0; i < state.length; i++) {
      if (i & mask) continue;
      const j = i | mask;
      const a = state[i];
      const b = state[j];
      state[i] = [(a[0] + b[0]) * scale, (a[1] + b[1]) * scale];
      state[j] = [(a[0] - b[0]) * scale, (a[1] - b[1]) * scale];
    }
  }

  function controlledPhase(state, n, control, target, order, inverse) {
    const angle = (inverse ? -1 : 1) * 2 * Math.PI / (2 ** order);
    const c = Math.cos(angle);
    const s = Math.sin(angle);
    const mask = (1 << (n - control - 1)) | (1 << (n - target - 1));
    for (let i = 0; i < state.length; i++) {
      if ((i & mask) !== mask) continue;
      const [re, im] = state[i];
      state[i] = [re * c - im * s, re * s + im * c];
    }
  }

  function reverseBits(value, n) {
    let reversed = 0;
    for (let bit = 0; bit < n; bit++) {
      reversed = (reversed << 1) | (value & 1);
      value >>= 1;
    }
    return reversed;
  }

  function reverseQubits(state, n) {
    const result = new Array(state.length);
    for (let i = 0; i < state.length; i++) result[reverseBits(i, n)] = state[i];
    return result;
  }

  function transform(input, n, inverse = false) {
    validate(n, 0);
    if (!Array.isArray(input) || input.length !== 2 ** n ||
        input.some(v => !Array.isArray(v) || v.length !== 2 || !v.every(Number.isFinite))) {
      throw new TypeError('State must contain 2^n finite complex amplitudes.');
    }
    let state = input.map(v => [...v]);
    if (inverse) {
      state = reverseQubits(state, n);
      for (let j = n - 1; j >= 0; j--) {
        for (let k = n - 1; k > j; k--) {
          controlledPhase(state, n, k, j, k - j + 1, true);
        }
        hadamard(state, n, j);
      }
    } else {
      for (let j = 0; j < n; j++) {
        hadamard(state, n, j);
        for (let k = j + 1; k < n; k++) {
          controlledPhase(state, n, k, j, k - j + 1, false);
        }
      }
      state = reverseQubits(state, n);
    }
    return state;
  }

  function probability(amplitude) {
    return amplitude[0] ** 2 + amplitude[1] ** 2;
  }

  const QFT = Object.freeze({ MAX_QUBITS, validate, prepare, transform, probability });
  if (typeof module !== 'undefined' && module.exports) module.exports = QFT;
  root.QFT = QFT;
})(typeof window !== 'undefined' ? window : globalThis);
