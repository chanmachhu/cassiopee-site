import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { renderMessages, renderStats, loadMessages, submitMessage } from '../app.js';

// Minimal fake DOM: just what app.js uses.
function el(tag = 'div') {
  const n = {
    tag, children: [], _text: '', className: '',
    appendChild(c) { n.children.push(c); return c; },
    replaceChildren(...c) { n.children = c; n._text = ''; },
    set textContent(v) { n._text = String(v); n.children = []; },
    get textContent() { return n._text + n.children.map((c) => c.textContent).join(''); },
  };
  return n;
}
globalThis.document = { createElement: el };
const reply = (status, body) => () => Promise.resolve({ ok: status < 400, status, json: async () => body });

test('messages are rendered as text', () => {
  const c = el();
  renderMessages([{ auteur: '<b>x</b>', texte: '<img src=x onerror=alert(1)>', cree_le: '2026-11-23T10:00:00Z' }], c);
  assert.equal(c.textContent.includes('<img src=x onerror=alert(1)>'), true);
});

test('stats are rendered per day', () => {
  const c = el();
  renderStats([{ jour: '2026-11-23', messages: 4 }], c);
  assert.match(c.textContent, /2026-11-23/);
  assert.match(c.textContent, /4/);
});

test('the source never uses innerHTML', () => {
  assert.doesNotMatch(readFileSync(new URL('../app.js', import.meta.url), 'utf8'), /innerHTML|insertAdjacentHTML|outerHTML/);
});

test('an unreachable API shows a clear message', async () => {
  const c = el();
  await loadMessages(() => Promise.reject(new TypeError('Failed to fetch')), c);
  assert.equal(c.textContent, "Le livre d'or ne répond pas pour l'instant.");
});

test('a 429 shows the rate-limit message', async () => {
  assert.equal(await submitMessage(reply(429, {}), 'a', 'b'), 'Trop de messages en ce moment, réessaie dans une minute.');
});

test('a 422 shows French details', async () => {
  const body = { detail: [{ loc: ['body', 'auteur'], type: 'string_too_long' }] };
  assert.equal(await submitMessage(reply(422, body), 'a', 'b'), 'Ton nom doit faire entre 1 et 40 caractères.');
});

test('a 201 returns no error', async () => {
  assert.equal(await submitMessage(reply(201, {}), 'a', 'b'), null);
});
