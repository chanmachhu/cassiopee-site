// Turns the guide's flat Markdown into the mockup's structure: one <section> per `##`, numbered rings,
// warning box, checklist tablet, verdict pills, kind badges and compose arrows.
// Uses Satteri (Astro's Markdown engine) directly: Astro 7 only accepts rehype plugins with an extra package.
import { hastToHtml, markdownToHast } from 'satteri';
import { sectionMeta } from './guide';

type N = any;

const h = (tagName: string, properties: N = {}, ...children: N[]): N => ({ type: 'element', tagName, properties, children });
const t = (value: string): N => ({ type: 'text', value });
const text = (n: N): string => (n.type === 'text' ? n.value : (n.children ?? []).map(text).join(''));
const kids = (n: N, tag?: string): N[] => (n.children ?? []).filter((c: N) => c.type === 'element' && (!tag || c.tagName === tag));
const rows = (table: N) => kids(kids(table, 'tbody')[0], 'tr');

const VERDICT: Record<string, string> = { Oui: 'v-oui', 'À adapter': 'v-adapt', Non: 'v-non' };
const KIND: Record<string, string> = { Valeur: 'k-val', Secret: 'k-sec', Base: 'k-base' };
const ARROW = () => h('td', { className: ['arr'] }, h('svg', { width: 22, height: 10, viewBox: '0 0 22 10', 'aria-hidden': 'true' },
  h('path', { d: 'M1,5 H19 M15,1.5 L20,5 L15,8.5', fill: 'none', stroke: '#3F5E37', strokeWidth: 1.6, strokeLinecap: 'round', strokeLinejoin: 'round' })));
const CHECK = () => h('svg', { className: ['ck'], width: 22, height: 22, viewBox: '0 0 22 22', 'aria-hidden': 'true' },
  h('circle', { cx: 11, cy: 11, r: 9.6, fill: 'none', stroke: '#A8842F', strokeWidth: 1, opacity: '.55' }),
  h('path', { d: 'M6.4,11.6 L9.8,15 L15.8,7.4', fill: 'none', stroke: 'url(#gGold)', strokeWidth: 2.3, strokeLinecap: 'round', strokeLinejoin: 'round' }));
const TEX = () => h('svg', { className: ['tex'], 'aria-hidden': 'true' },
  h('rect', { width: '100%', height: '100%', fill: '#fff', filter: 'url(#fVeinsBig)', opacity: '.6' }),
  h('rect', { width: '100%', height: '100%', fill: '#fff', filter: 'url(#fGrain)', opacity: '.4' }));

// A cell that is only "Oui" / "À adapter" / "Non" (or Valeur / Secret / Base) becomes a pill.
function badge(td: N) {
  const label = text(td).trim();
  const cls = VERDICT[label] ? ['v', VERDICT[label]] : KIND[label] ? ['kind', KIND[label]] : null;
  if (cls) td.children = [h('span', { className: cls }, t(label))];
}

// "| # | Règle | Si tu l'oublies |" becomes the numbered tablet.
function tablet(table: N) {
  const miss = text(kids(kids(kids(table, 'thead')[0], 'tr')[0], 'th')[2]).trim();
  const items = rows(table).map((tr: N) => {
    const [n, rule, why] = kids(tr, 'td');
    return h('li', {}, CHECK(), h('span', { className: ['tnum', 'engraved'] }, t(text(n))), h('span', {}, ...rule.children),
      h('span', { className: ['miss'] }, h('span', {}, t(`${miss} :`)), t(' '), ...why.children));
  });
  return h('div', { className: ['tablet'] }, TEX(), h('h3', { className: ['engraved'] }, t('LES DIX RÈGLES')), h('ol', {}, ...items));
}

// "**Title.** body" as a paragraph: the first strong ends with a full stop.
function warn(p: N) {
  const [first, ...rest] = p.children;
  if (first?.tagName !== 'strong' || !text(first).endsWith('.')) return p;
  const title = text(first).slice(0, -1);
  rest[0] = { ...rest[0], value: rest[0].value?.replace(/^\s+/, '') };
  return h('div', { className: ['warn'], role: 'note' },
    h('p', { className: ['warn-t'] }, h('svg', { width: 16, height: 16, viewBox: '-6 -6 12 12', 'aria-hidden': 'true' }, h('use', { href: '#rosette' })), t(title)),
    h('p', {}, ...rest));
}

function block(node: N, id: string) {
  if (node.tagName === 'p') return warn(node);
  if (node.tagName !== 'table') return node;
  const head = kids(kids(node, 'thead')[0], 'tr')[0];
  if (text(kids(head, 'th')[0]).trim() === '#') return tablet(node);
  rows(node).forEach((tr: N) => kids(tr, 'td').forEach(badge));
  if (id === 'compose') {
    head.children.splice(1, 0, h('th'));
    rows(node).forEach((tr: N) => tr.children.splice(1, 0, ARROW()));
  }
  return h('div', { className: ['mt'] }, node);
}

export function renderGuide(markdown: string) {
  const tree: N = markdownToHast(markdown);
  const sections: N[] = [];
  const toc: ReturnType<typeof sectionMeta>[] = [];
  for (const node of tree.children) {
    if (node.type !== 'element') continue;
    if (node.tagName === 'h2') {
      const meta = sectionMeta(text(node));
      toc.push(meta);
      if (meta.n) node.children[0].value = node.children[0].value.replace(/^\d+\.\s+/, '');
      node.children = [...(meta.n ? [h('span', { className: ['ring'] }, t(meta.n))] : []), h('span', {}, ...node.children)];
      sections.push(h('section', { id: meta.id, 'data-reveal': meta.id, className: ['sec', 'rv'] }, node));
    } else {
      const cur = sections.at(-1);
      cur?.children.push(block(node, cur.properties.id));
    }
  }
  return { toc, html: hastToHtml(sections) };
}
