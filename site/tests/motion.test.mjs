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
test('a section reveals at 20 % visible, or at first sight when taller than 5 roots', async () => {
  const { shouldReveal } = await import('../src/scripts/reveal.ts');
  const entry = (ratio, height, root = 800) => ({ isIntersecting: true, intersectionRatio: ratio, boundingClientRect: { height }, rootBounds: { height: root } });
  assert.equal(shouldReveal(entry(0.25, 900)), true);
  assert.equal(shouldReveal(entry(0.1, 900)), false);
  assert.equal(shouldReveal(entry(0.15, 5 * 800)), true);
});
