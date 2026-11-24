// Text only: every value goes through textContent, never HTML strings.
const DOWN = "Le livre d'or ne répond pas pour l'instant.";
const TOO_MANY = 'Trop de messages en ce moment, réessaie dans une minute.';
const FIELD_ERRORS = {
  auteur: 'Ton nom doit faire entre 1 et 40 caractères.',
  texte: 'Ton message doit faire entre 1 et 280 caractères.',
};

function add(parent, tag, className, text) {
  const n = document.createElement(tag);
  n.className = className;
  n.textContent = text;
  parent.appendChild(n);
  return n;
}

export function renderMessages(list, container) {
  container.replaceChildren();
  for (const m of list) {
    const item = document.createElement('li');
    add(item, 'strong', 'auteur', m.auteur);
    add(item, 'time', 'date', m.cree_le.slice(0, 10));
    add(item, 'p', 'texte', m.texte);
    container.appendChild(item);
  }
}

export function renderStats(list, container) {
  container.replaceChildren();
  for (const s of list) add(container, 'li', 'stat', `${s.jour} : ${s.messages}`);
}

export async function loadMessages(fetchImpl, container) {
  try {
    const r = await fetchImpl('/api/messages?limit=20');
    if (!r.ok) throw new Error(r.status);
    renderMessages(await r.json(), container);
  } catch {
    container.textContent = DOWN;
  }
}

// Returns null on success, otherwise the message to show.
export async function submitMessage(fetchImpl, auteur, texte) {
  try {
    const r = await fetchImpl('/api/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ auteur, texte }),
    });
    if (r.status === 201) return null;
    if (r.status === 429) return TOO_MANY;
    if (r.status === 422) {
      const { detail } = await r.json();
      const fields = detail.map((d) => d.loc[d.loc.length - 1]);
      return fields.map((f) => FIELD_ERRORS[f]).filter(Boolean).join(' ') || 'Message invalide.';
    }
    return DOWN;
  } catch {
    return DOWN;
  }
}

// Wire the page only in a browser (tests import this file under node).
if (typeof document !== 'undefined' && document.getElementById) {
  const $ = (id) => document.getElementById(id);
  const refresh = async () => {
    await loadMessages(fetch, $('messages'));
    try {
      const r = await fetch('/api/stats');
      if (r.ok) renderStats((await r.json()).slice(-30), $('stats'));
    } catch { /* the messages list already shows the outage */ }
  };
  for (const [input, counter] of [['auteur', 'auteur-n'], ['texte', 'texte-n']]) {
    const update = () => { $(counter).textContent = `${$(input).value.length}/${$(input).maxLength}`; };
    $(input).addEventListener('input', update);
    update();
  }
  $('form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const err = await submitMessage(fetch, $('auteur').value.trim(), $('texte').value.trim());
    $('erreur').textContent = err ?? '';
    if (!err) { $('texte').value = ''; $('texte-n').textContent = `0/${$('texte').maxLength}`; refresh(); }
  });
  refresh();
}
