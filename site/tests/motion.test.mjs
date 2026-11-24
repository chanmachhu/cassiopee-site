import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';

const css = readdirSync('dist/_astro').filter((f) => f.endsWith('.css')).map((f) => readFileSync(`dist/_astro/${f}`, 'utf8')).join('\n');

test('paused animations only once the page is armed', () => {
  assert.match(css, /\.armed \.sec:not\(\.in\)/);
  assert.doesNotMatch(css, /^\s*\.sec:not\(\.in\)/m);
});
test('reduced motion turns every animation off', () => {
  assert.match(css, /@media \(prefers-reduced-motion: ?reduce\)[^}]*animation:\s*none/);
});
