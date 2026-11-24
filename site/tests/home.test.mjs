import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { exemples } from '../src/data/exemples.ts';

const html = readFileSync('dist/index.html', 'utf8');
const count = (s, sub) => s.split(sub).length - 1;

test('home keeps the mockup copy', () => {
  // The title is checked through its label: its words get split into spans.
  assert.match(html, /<h1[^>]*aria-label="Mets ton API parmi les étoiles"/);
  for (const s of ['Les trois piliers', 'Le rituel, en trois étapes', 'Trois exemples, en ligne', "Consulte l'oracle", "Ton temple t'attend"]) assert.match(html, new RegExp(s));
});
test('no "Voir en ligne" without an address', () => {
  assert.equal(count(html, 'Voir en ligne'), exemples.filter((e) => e.enLigne).length);
});
test('main call to action opens the intranet Cassiopée page', () => {
  const ctas = [...html.matchAll(/<a\b[^>]*href="([^"]*)"[^>]*>(?:(?!<\/a>).)*Déployer depuis l'intranet/gs)].map((m) => m[1]);
  assert.deepEqual(ctas, ['https://intranet.sigl.epita.fr/cassiopee', 'https://intranet.sigl.epita.fr/cassiopee']);
});
test('recipe buttons point to the examples page', () => {
  for (const s of ['livre-dor', 'stats', 'bot']) assert.match(html, new RegExp(`href="/exemples#${s}"`));
});
test('hero shows the "En ligne" pill only with the guestbook address', () => {
  const live = exemples.find((e) => e.slug === 'livre-dor').enLigne;
  assert.equal(html.includes('En ligne</span>'), Boolean(live));
  if (live) assert.ok(html.includes(`>${live}</span>`));
});
