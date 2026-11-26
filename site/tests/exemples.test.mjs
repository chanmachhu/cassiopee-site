import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const html = readFileSync('dist/exemples/index.html', 'utf8');
// One section per example: <section id="slug" …> up to the next section or the footer.
const section = (slug) => html.match(new RegExp(`<section id="${slug}"[\\s\\S]*?(?=<section id=|<footer)`))?.[0] ?? '';
const text = (s) => s.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
const VARS = { 'livre-dor': ['DATABASE_URL', 'ADMIN_TOKEN', 'API_URL'], stats: ['DATABASE_URL'], bot: ['API_URL', 'DISCORD_TOKEN'] };
const SECRETS = ['ADMIN_TOKEN', 'DISCORD_TOKEN'];

test('examples page: h1, header link, one anchored section per example', () => {
  assert.match(html, /<h1[^>]*aria-label="Trois exemples, en ligne"/);
  assert.match(html, /<a href="\/exemples" class="nl" aria-current="page"/);
  for (const slug of Object.keys(VARS)) assert.match(html, new RegExp(`<section id="${slug}"`));
});
test('each example lists the variables of its recipe', () => {
  for (const [slug, names] of Object.entries(VARS)) {
    const s = section(slug);
    assert.ok(s, slug);
    for (const n of names) assert.ok(s.includes(n), `${slug}: ${n}`);
  }
  assert.ok(!section('stats').includes('ADMIN_TOKEN'));
});
// A secret row must read exactly "NAME Secret •••• saisi dans Cassiopée": nothing else can follow the mask.
test('secrets show the mask and no value', () => {
  for (const name of SECRETS) {
    const row = [...html.matchAll(/<li>(?:(?!<\/li>)[\s\S])*<\/li>/g)].map((m) => text(m[0])).find((t) => t.startsWith(name));
    assert.equal(row, `${name} Secret •••• saisi dans Cassiopée`);
  }
  assert.doesNotMatch(html, /\b[0-9a-f]{32,}\b/);
  assert.doesNotMatch(html, /[\w-]{24}\.[\w-]{6}\.[\w-]{27}/);
});
test('code links open in a new tab; no live button without an address', () => {
  assert.equal((html.match(/aria-label="Code de livre-dor-[a-z]+"/g) ?? []).length, 5);
  assert.equal((html.match(/Voir le code/g) ?? []).length, 3);
  assert.doesNotMatch(html, /Voir en ligne/);
  assert.match(section('bot'), /Bientôt en ligne/);
});
