import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const read = (f) => readFileSync(f, 'utf8');
const htmlFiles = (d) =>
  readdirSync(d).flatMap((n) => {
    const p = join(d, n);
    return statSync(p).isDirectory() ? htmlFiles(p) : p.endsWith('.html') ? [p] : [];
  });

test('every page exists', () => {
  for (const p of ['index.html', '404.html']) assert.ok(existsSync(`dist/${p}`), p);
});
test('no inline script in any page', () => {
  for (const f of htmlFiles('dist')) assert.doesNotMatch(read(f), /<script(?![^>]*\bsrc=)[^>]*>/, f);
});
// <a href> is navigation (GitHub, intranet), not a request
test('no third-party request', () => {
  for (const f of htmlFiles('dist')) {
    const html = read(f);
    assert.doesNotMatch(html, /\ssrc="https?:\/\//, f);
    assert.doesNotMatch(html, /<link\b[^>]*\shref="https?:\/\//, f);
  }
});
