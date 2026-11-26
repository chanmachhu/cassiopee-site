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
// Guards the post-build rewrite of Astro's island loader.
test('every local <script src> points to a file in dist', () => {
  for (const f of htmlFiles('dist')) {
    for (const [, src] of read(f).matchAll(/<script\b[^>]*\ssrc="(\/[^"]+)"/g)) assert.ok(existsSync(join('dist', src)), `${f}: ${src}`);
  }
});
test('guide page: title and one TOC link per ## section', () => {
  const html = read('dist/preparer-son-app/index.html');
  const md = read('src/content/guide/preparer-son-app.md');
  const title = md.match(/^title: (.+)$/m)[1];
  const n = (md.match(/^## /gm) ?? []).length;
  assert.match(html, /<h1[^>]*aria-label="Préparer son app"/);
  assert.ok(html.includes(title), 'guide title');
  const ids = [...html.matchAll(/<section id="([^"]+)"/g)].map((m) => m[1]);
  assert.equal(ids.length, n);
  const toc = html.match(/<nav class="toc toc-st"[\s\S]*?<\/nav>/)[0];
  assert.deepEqual([...toc.matchAll(/href="#([^"]+)"/g)].map((m) => m[1]), ids);
  assert.match(html, /<a href="\/preparer-son-app" class="nl" aria-current="page"/);
});
